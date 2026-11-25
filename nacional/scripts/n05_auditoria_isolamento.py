"""Auditoria de protocolo de um agente isolado (decisor ou avaliador): cada chamada de ferramenta da transcrição é conferida
contra a raiz permitida. Generaliza scripts/30_auditoria_etapa4.py (mesmas regras), com raiz, registro e domínios web parametrizados.

Uso: python -I -X utf8 nacional/scripts/n05_auditoria_isolamento.py <transcricao.jsonl> <raiz_ambiente> <dir_registro> [dominios_web_permitidos,...]
Grava em <dir_registro>: transcricao.jsonl (cópia), transcricao.md, auditoria_acessos.csv, auditoria_resumo.json
"""
import csv, json, os, re, shutil, sys

TRANS, ENV, REG = sys.argv[1], os.path.abspath(sys.argv[2]), os.path.abspath(sys.argv[3])
WEB_OK = [d for d in (sys.argv[4].split(",") if len(sys.argv) > 4 else []) if d]
ENV_N = ENV.replace("\\", "/").lower()
PROIB = re.compile(r"evaluation_only|quarentena|data[/\\]raw|[/\\]processados|LOG_|[/\\]docs\b|\breports[/\\]|etapa4|etapa5|"
                   r"\.\.[/\\]|\bcurl\b|\bwget\b|pip\s+install|Invoke-WebRequest|urllib|requests\.get", re.I)
ABS = re.compile(r"(?i)(?<![\w/])(?:[a-z]:[\\/]|/[a-z]/)[^\s\"'`;|&)<>]*")
INTERFACE = {"mcp__ccd_turn__update_plan", "SubagentHandback", "TodoWrite"}


def norm(p):
    p = p.replace("\\", "/")
    m = re.match(r"^/([a-zA-Z])/", p)
    if m:
        p = m.group(1) + ":/" + p[3:]
    return os.path.normpath(p).replace("\\", "/").lower()


def dentro(p):
    p = norm(p if os.path.isabs(norm(p)) else os.path.join(ENV, p))
    return p == ENV_N or p.startswith(ENV_N + "/")


def checar(nome, inp):
    if nome in INTERFACE:
        return "", []
    if nome in ("WebFetch", "WebSearch"):
        alvo = inp.get("url") or inp.get("query") or ""
        ok = nome == "WebFetch" and any(d in alvo for d in WEB_OK)
        return alvo, [] if ok or (nome == "WebSearch" and WEB_OK) else [f"acesso web não permitido: {nome}"]
    if nome in ("Agent", "Task", "SendMessage") or nome.startswith("mcp__"):
        return json.dumps(inp, ensure_ascii=False)[:300], [f"ferramenta não permitida: {nome}"]
    if nome in ("Read", "Write", "Edit", "NotebookEdit"):
        fp = inp.get("file_path") or inp.get("notebook_path") or ""
        probs = [] if dentro(fp) else ["arquivo fora do ambiente"]
        if nome != "Read" and dentro(fp) and not any(dentro(os.path.join(ENV, s)) and norm(fp).startswith(norm(os.path.join(ENV, s))) for s in ("trabalho", "saida")):
            probs.append("escrita fora de trabalho/ e saida/")
        return fp, probs
    if nome in ("Glob", "Grep"):
        p = inp.get("path")
        probs = ["sem 'path'"] if not p else ([] if dentro(p) else ["busca fora do ambiente"])
        return f"path={p} pattern={inp.get('pattern')}", probs
    if nome in ("Bash", "PowerShell"):
        cmd = inp.get("command", ""); probs = []
        m = PROIB.search(cmd)
        if m:
            probs.append(f"comando cita caminho/acesso proibido: {m.group(0)}")
        fora = sorted({a for a in ABS.findall(cmd) if not dentro(a)})
        if fora:
            probs.append("caminho absoluto fora do ambiente: " + "; ".join(fora)[:300])
        return cmd, probs
    return json.dumps(inp, ensure_ascii=False)[:300], []


def texto(c):
    if isinstance(c, str):
        return c
    return "\n".join((b.get("text") or (texto(b.get("content")) if b.get("type") == "tool_result" else "") or "") for b in (c or []) if isinstance(b, dict))


os.makedirs(REG, exist_ok=True)
dst = os.path.join(REG, "transcricao.jsonl")
if os.path.abspath(TRANS) != os.path.abspath(dst):
    shutil.copyfile(TRANS, dst)
L = [json.loads(l) for l in open(dst, encoding="utf-8") if l.strip()]
ch, md, primeiro, seq = {}, [], None, 0
for ln in L:
    msg = ln.get("message") or {}; role, cont, ts = msg.get("role") or ln.get("type"), msg.get("content"), ln.get("timestamp", "")
    if role == "user" and primeiro is None and texto(cont).strip():
        primeiro = texto(cont); md.append(f"## [{ts}] PROMPT\n\n{primeiro}\n"); continue
    for b in ([{"type": "text", "text": cont}] if isinstance(cont, str) else (cont or [])):
        t = b.get("type")
        if t == "text" and b.get("text", "").strip():
            md.append(f"## [{ts}] {'AGENTE' if role == 'assistant' else 'SISTEMA/RESULTADO'}\n\n{b['text']}\n")
        elif t == "tool_use" and b["id"] not in ch:
            seq += 1
            alvo, probs = checar(b["name"], b.get("input", {}))
            ch[b["id"]] = dict(seq=seq, timestamp=ts, ferramenta=b["name"], alvo=str(alvo).replace("\n", " ⏎ ")[:2000], conforme=not probs, problemas=" | ".join(probs))
            md.append(f"### [{ts}] #{seq} {b['name']}\n\n```\n{json.dumps(b.get('input', {}), ensure_ascii=False, indent=1)[:20000]}\n```\n")
        elif t == "tool_result":
            r = texto(b.get("content")); c = ch.get(b.get("tool_use_id"))
            md.append(f"<details><summary>resultado #{c['seq'] if c else '?'} ({len(r)} caracteres)</summary>\n\n```\n{r[:3000]}\n```\n</details>\n")
open(os.path.join(REG, "transcricao.md"), "w", encoding="utf-8").write("# Transcrição (íntegra em transcricao.jsonl)\n\n" + "\n".join(md))
with open(os.path.join(REG, "auditoria_acessos.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, ["seq", "timestamp", "ferramenta", "alvo", "conforme", "problemas"]); w.writeheader(); w.writerows(sorted(ch.values(), key=lambda c: c["seq"]))
res = dict(chamadas=len(ch), nao_conformes=[{k: c[k] for k in ("seq", "ferramenta", "problemas", "alvo")} for c in ch.values() if not c["conforme"]],
           ferramentas=dict(sorted({c["ferramenta"]: sum(1 for x in ch.values() if x["ferramenta"] == c["ferramenta"]) for c in ch.values()}.items())))
json.dump(res, open(os.path.join(REG, "auditoria_resumo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: (v if k != "nao_conformes" else [{**x, "alvo": x["alvo"][:160]} for x in v]) for k, v in res.items()}, ensure_ascii=False, indent=1))
