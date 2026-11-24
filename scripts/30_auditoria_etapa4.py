"""Etapa 4 — auditoria de PROTOCOLO da execução do agente decisor (não avalia o mérito da decisão).

Uso: python -I -X utf8 scripts/30_auditoria_etapa4.py <raiz_projeto> <transcricao_jsonl_do_agente>

Gera em etapa4/registro/:
  transcricao_agente_decisor.jsonl   cópia integral da transcrição
  transcricao_agente_decisor.md      versão legível (texto integral; resultados de ferramentas truncados)
  auditoria_acessos.csv              uma linha por chamada de ferramenta, com alvo e verificação de isolamento
  auditoria_resumo.json              enunciado idêntico?, violações, exposição, integridade, entregáveis
  hashes_ambiente_depois.csv         sha256 de tudo no ambiente após a execução (congela os entregáveis)
"""
import csv, hashlib, json, os, re, shutil, sys

ROOT = os.path.abspath(sys.argv[1])
TRANS = sys.argv[2]
ENV = os.path.join(ROOT, "etapa4", "ambiente_decisor")
REG = os.path.join(ROOT, "etapa4", "registro")
ENV_N = ENV.replace("\\", "/").lower()

PROIB = re.compile(r"evaluation_only|quarentena|pos_corte|data[/\\]raw|data[/\\]processed|[/\\]docs\b|\breports[/\\]|LOG_ETAPA|LOG_PRE|"
                   r"\.\.[/\\]|\bcurl\b|\bwget\b|pip\s+install|https?://|Invoke-WebRequest|urllib|requests\.get", re.I)
ABS = re.compile(r"(?i)(?<![\w/])(?:[a-z]:[\\/]|/[a-z]/)[^\s\"'`;|&)<>]*")
EXPOSICAO = re.compile(r"evaluation_only|quarentena_temporal|_pos_corte", re.I)
WEB = {"WebSearch", "WebFetch", "Agent", "Task", "SendMessage"}
INTERFACE = {"mcp__ccd_turn__update_plan"}  # lista de tarefas do app: não lê nem envia dados do caso
ENTREGAVEIS = ["00_resumo_executivo.md", "01_diagnostico.md", "02_alternativas.md", "03_comparacao.md", "03_comparacao.csv",
               "04_recomendacao.md", "05_itens_criticos.md", "06_economia.md", "plano_por_item.csv", "registro_decisoes.csv",
               "registro_hipoteses.csv", "registro_acessos.md"]


def norm(p):
    p = p.replace("\\", "/")
    m = re.match(r"^/([a-zA-Z])/", p)
    if m:
        p = m.group(1) + ":/" + p[3:]
    return os.path.normpath(p).replace("\\", "/").lower()


def dentro(p, sub=""):
    p = norm(p if os.path.isabs(norm(p)) else os.path.join(ENV, p))
    return p == ENV_N + sub.rstrip("/") or p.startswith(ENV_N + sub.rstrip("/") + "/")


def checar(nome, inp):
    """-> (alvo, problemas[])"""
    probs = []
    if nome in INTERFACE:
        return json.dumps(inp, ensure_ascii=False)[:300], []
    if nome in WEB or nome.startswith("mcp__"):
        return json.dumps(inp, ensure_ascii=False)[:300], [f"ferramenta proibida/externa: {nome}"]
    if nome in ("Read", "Write", "Edit", "NotebookEdit"):
        fp = inp.get("file_path") or inp.get("notebook_path") or ""
        if not dentro(fp):
            probs.append("arquivo fora do ambiente")
        elif nome != "Read" and not (dentro(fp, "/trabalho") or dentro(fp, "/saida")):
            probs.append("escrita fora de trabalho/ e saida/")
        txt = inp.get("content") or inp.get("new_string") or ""
        if nome != "Read" and PROIB.search(txt):
            probs.append(f"conteúdo escrito cita caminho/acesso proibido: {PROIB.search(txt).group(0)}")
        return fp, probs
    if nome in ("Glob", "Grep"):
        p = inp.get("path")
        if not p:
            probs.append("sem 'path' (busca no diretório corrente)")
        elif not dentro(p):
            probs.append("busca fora do ambiente")
        alvo = f"path={p} pattern={inp.get('pattern')} glob={inp.get('glob')}"
        if PROIB.search(str(inp.get("pattern", "")) + str(inp.get("glob", ""))):
            probs.append("padrão de busca cita caminho proibido")
        return alvo, probs
    if nome in ("Bash", "PowerShell"):
        cmd = inp.get("command", "")
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
    out = []
    for b in c or []:
        if isinstance(b, dict):
            out.append(b.get("text") or (texto(b.get("content")) if b.get("type") == "tool_result" else "") or "")
    return "\n".join(out)


os.makedirs(REG, exist_ok=True)
if os.path.abspath(TRANS) != os.path.abspath(os.path.join(REG, "transcricao_agente_decisor.jsonl")):  # reexecução sobre a cópia
    shutil.copyfile(TRANS, os.path.join(REG, "transcricao_agente_decisor.jsonl"))
linhas = [json.loads(l) for l in open(TRANS, encoding="utf-8") if l.strip()]

chamadas, md, primeiro_user, exposicoes = {}, [], None, []
seq = 0
for ln in linhas:
    msg = ln.get("message") or {}
    role, cont, ts = msg.get("role") or ln.get("type"), msg.get("content"), ln.get("timestamp", "")
    if role == "user" and primeiro_user is None and texto(cont).strip():
        primeiro_user = texto(cont)
        md.append(f"## [{ts}] ENUNCIADO (prompt do agente)\n\n{primeiro_user}\n")
        continue
    blocos = [{"type": "text", "text": cont}] if isinstance(cont, str) else (cont or [])
    for b in blocos:
        t = b.get("type")
        if t == "text" and b.get("text", "").strip():
            md.append(f"## [{ts}] {'AGENTE' if role == 'assistant' else 'USUÁRIO/SISTEMA'}\n\n{b['text']}\n")
        elif t == "tool_use":
            if b["id"] in chamadas:  # a transcrição pode repetir o mesmo bloco em linhas sucessivas
                continue
            seq += 1
            alvo, probs = checar(b["name"], b.get("input", {}))
            chamadas[b["id"]] = dict(seq=seq, timestamp=ts, ferramenta=b["name"], alvo=alvo.replace("\n", " ⏎ ")[:2000],
                                     conforme=not probs, problemas=" | ".join(probs), exposicao_no_resultado="")
            md.append(f"### [{ts}] #{seq} {b['name']}\n\n```\n{json.dumps(b.get('input', {}), ensure_ascii=False, indent=1)}\n```\n")
        elif t == "tool_result":
            r = texto(b.get("content"))
            c = chamadas.get(b.get("tool_use_id"))
            m = EXPOSICAO.search(r)
            if c and m:
                c["exposicao_no_resultado"] = m.group(0); exposicoes.append(c["seq"])
            md.append(f"<details><summary>resultado #{c['seq'] if c else '?'} ({len(r)} caracteres)</summary>\n\n```\n{r[:3000]}"
                      f"{'\n[... truncado; íntegra na .jsonl]' if len(r) > 3000 else ''}\n```\n</details>\n")

open(os.path.join(REG, "transcricao_agente_decisor.md"), "w", encoding="utf-8").write(
    "# Transcrição do agente decisor — Etapa 4\n\nGerada por `scripts/30_auditoria_etapa4.py` a partir de `transcricao_agente_decisor.jsonl` (íntegra).\n\n" + "\n".join(md))
cols = ["seq", "timestamp", "ferramenta", "alvo", "conforme", "problemas", "exposicao_no_resultado"]
with open(os.path.join(REG, "auditoria_acessos.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, cols); w.writeheader(); w.writerows(sorted(chamadas.values(), key=lambda c: c["seq"]))

# scripts deixados em trabalho/ também não podem citar caminhos proibidos
scripts_prob = []
for d, _, fs in os.walk(os.path.join(ENV, "trabalho")):
    for f in fs:
        if f.endswith((".py", ".sql", ".sh", ".ps1")):
            s = open(os.path.join(d, f), encoding="utf-8", errors="replace").read()
            m = PROIB.search(s) or next((a for a in ABS.findall(s) if not dentro(a)), None)
            if m:
                scripts_prob.append((os.path.relpath(os.path.join(d, f), ENV), m if isinstance(m, str) else m.group(0)))

# integridade: entradas do ambiente iguais às de antes; pacote original igual ao manifesto
antes = {r["arquivo"]: r["sha256"] for r in csv.DictReader(open(os.path.join(REG, "hashes_ambiente_antes.csv"), encoding="utf-8"))}
depois = []
for d, _, fs in os.walk(ENV):
    for f in fs:
        p = os.path.relpath(os.path.join(d, f), ENV).replace("\\", "/")
        depois.append((p, os.path.getsize(os.path.join(ENV, p)), hashlib.sha256(open(os.path.join(ENV, p), "rb").read()).hexdigest()))
depois.sort()
with open(os.path.join(REG, "hashes_ambiente_depois.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["arquivo", "bytes", "sha256"]); w.writerows(depois)
dep = {p: h for p, _, h in depois}
entradas_alteradas = [p for p, h in antes.items() if dep.get(p) != h]
novos_fora = [p for p in dep if p not in antes and not p.startswith(("trabalho/", "saida/"))]
man = {r["arquivo"]: r["sha256"] for r in csv.DictReader(open(os.path.join(ROOT, "data", "decision_input", "MANIFESTO.csv"), encoding="utf-8"))}
pacote_original_alterado = [f for f, h in man.items() if hashlib.sha256(open(os.path.join(ROOT, f), "rb").read()).hexdigest() != h]

enun = open(os.path.join(ENV, "ENUNCIADO.md"), encoding="utf-8").read()
nz = lambda s: re.sub(r"\s+", " ", s or "").strip()
plano = os.path.join(ENV, "saida", "plano_por_item.csv")
resumo = dict(
    prompt_identico_ao_enunciado=nz(primeiro_user) == nz(enun),
    chamadas_de_ferramenta=len(chamadas),
    chamadas_nao_conformes=[{k: c[k] for k in ("seq", "ferramenta", "problemas")} for c in chamadas.values() if not c["conforme"]],
    resultados_com_exposicao_a_dados_de_avaliacao=exposicoes,
    scripts_com_caminho_proibido=scripts_prob,
    entradas_do_ambiente_alteradas=entradas_alteradas,
    arquivos_novos_fora_de_trabalho_saida=novos_fora,
    pacote_original_alterado=pacote_original_alterado,
    entregaveis_ausentes=[f for f in ENTREGAVEIS if not os.path.exists(os.path.join(ENV, "saida", f))],
    plano_por_item_linhas=(sum(1 for _ in csv.reader(open(plano, encoding="utf-8"))) - 1) if os.path.exists(plano) else None,
)
json.dump(resumo, open(os.path.join(REG, "auditoria_resumo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(resumo, ensure_ascii=False, indent=1))
