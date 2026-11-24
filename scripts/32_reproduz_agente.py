"""Pré-Etapa 5 — reproduz os cálculos do agente decisor em cópias, sem tocar em etapa4/ (congelado).

Uso: python -I -X utf8 scripts/32_reproduz_agente.py <raiz_projeto>
Para cada pacote (v1 = o que o agente usou; v2 = errata), monta etapa5/reproducao/<v>/ com o pacote, a consulta e os scripts do
agente, roda a ordem declarada por ele (10 → 20 → 21 → 30 → 40 → 50) e compara as saídas de v1 com as congeladas.
Saída: etapa5/avaliacao/reproducao.csv
"""
import hashlib, os, shutil, subprocess, sys
import pandas as pd

ROOT = os.path.abspath(sys.argv[1])
CONG = os.path.join(ROOT, "etapa4", "ambiente_decisor")
REP = os.path.join(ROOT, "etapa5", "reproducao")
ORDEM = ["10_referencias.py", "20_estrategias.py", "21_e2_diagnostico.py", "30_saidas.py", "40_numeros_texto.py", "50_registros.py"]
PACOTE = {"v1": os.path.join(CONG, "data", "decision_input"), "v2": os.path.join(ROOT, "data", "decision_input_v2")}
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
congelado_antes = {os.path.relpath(os.path.join(d, f), CONG): sha(os.path.join(d, f)) for d, _, fs in os.walk(CONG) for f in fs}

linhas = []
for v, pac in PACOTE.items():
    amb = os.path.join(REP, v)
    if os.path.exists(amb):
        shutil.rmtree(amb)
    os.makedirs(os.path.join(amb, "trabalho")); os.makedirs(os.path.join(amb, "saida")); os.makedirs(os.path.join(amb, "scripts"))
    shutil.copytree(pac, os.path.join(amb, "data", "decision_input"))
    shutil.copy(os.path.join(CONG, "scripts", "consulta_agente.py"), os.path.join(amb, "scripts"))
    for f in os.listdir(os.path.join(CONG, "trabalho")):
        if f.endswith(".py"):
            shutil.copy(os.path.join(CONG, "trabalho", f), os.path.join(amb, "trabalho"))
    for s in ORDEM:
        r = subprocess.run([sys.executable, "-I", "-X", "utf8", os.path.join("trabalho", s)], cwd=amb, capture_output=True, text=True, encoding="utf-8")
        open(os.path.join(amb, "trabalho", s.replace(".py", ".log")), "w", encoding="utf-8").write(r.stdout + "\n--- stderr ---\n" + r.stderr)
        linhas.append(dict(pacote=v, arquivo=f"trabalho/{s}", tipo="execução", resultado="ok" if r.returncode == 0 else f"erro (código {r.returncode})",
                           detalhe=r.stderr.strip().splitlines()[-1][:300] if r.returncode else ""))
    if v != "v1":
        continue
    # compara cada saída gerada com a versão congelada
    for d, _, fs in os.walk(amb):
        for f in fs:
            p = os.path.join(d, f); rel = os.path.relpath(p, amb).replace("\\", "/")
            if rel.startswith(("data/", "scripts/")) or rel.endswith((".py", ".log", ".pyc")):
                continue
            c = os.path.join(CONG, rel)
            if not os.path.exists(c):
                linhas.append(dict(pacote=v, arquivo=rel, tipo="comparação", resultado="sem versão congelada", detalhe="")); continue
            if sha(p) == sha(c):
                linhas.append(dict(pacote=v, arquivo=rel, tipo="comparação", resultado="idêntico", detalhe="")); continue
            det = ""
            if rel.endswith(".csv"):
                a, b = pd.read_csv(p), pd.read_csv(c)
                if a.shape != b.shape or list(a.columns) != list(b.columns):
                    det = f"formato difere: {a.shape} × {b.shape}"
                else:
                    num = a.select_dtypes("number").columns
                    dif = float((a[num] - b[num]).abs().max().max()) if len(num) else 0.0
                    txt = int((a.drop(columns=num).astype(str) != b.drop(columns=num).astype(str)).sum().sum())
                    det = f"máx. diferença numérica {dif:.6g}; células de texto diferentes {txt}"
            linhas.append(dict(pacote=v, arquivo=rel, tipo="comparação", resultado="difere", detalhe=det))
    # saídas congeladas que a reprodução não gerou (escritas à mão pelo agente)
    for d, _, fs in os.walk(os.path.join(CONG, "saida")):
        for f in fs:
            rel = "saida/" + f
            if not os.path.exists(os.path.join(amb, rel)):
                linhas.append(dict(pacote=v, arquivo=rel, tipo="comparação", resultado="não gerado pelos scripts (texto do agente)", detalhe=""))
    for f in os.listdir(os.path.join(CONG, "trabalho")):
        if not f.endswith(".py") and not os.path.exists(os.path.join(amb, "trabalho", f)):
            linhas.append(dict(pacote=v, arquivo="trabalho/" + f, tipo="comparação", resultado="não gerado pela ordem declarada", detalhe=""))

congelado_depois = {os.path.relpath(os.path.join(d, f), CONG): sha(os.path.join(d, f)) for d, _, fs in os.walk(CONG) for f in fs}
assert congelado_antes == congelado_depois, "etapa4/ foi alterado"
os.makedirs(os.path.join(ROOT, "etapa5", "avaliacao"), exist_ok=True)
R = pd.DataFrame(linhas)
R.to_csv(os.path.join(ROOT, "etapa5", "avaliacao", "reproducao.csv"), index=False, encoding="utf-8")
print(R.groupby(["pacote", "tipo", "resultado"]).size().to_string())
print(R[R.resultado.isin(["difere"]) | R.resultado.str.startswith("erro")].to_string(index=False))
