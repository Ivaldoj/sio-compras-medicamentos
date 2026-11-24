"""Etapa 5 / 00 — integridade dos arquivos congelados (somente leitura).

Confere, por sha256:
  1. etapa4/ambiente_decisor  × etapa4/registro/hashes_ambiente_depois.csv
  2. etapa4/registro          × hashes declarados no LOG_ETAPA_4.md
  3. data/decision_input      × MANIFESTO.csv (pacote v1)
  4. data/decision_input_v2   × MANIFESTO.csv (pacote com errata)
  5. etapa5/PROTOCOLO_AVALIACAO.md × sha256 pré-registrado no LOG_PRE_ETAPA_5.md
  6. cópias em etapa5_avaliacao_independente/ambiente_avaliador × originais
Saída: resultados/integridade[_<rotulo>].csv  (rotulo = argv[2], ex.: antes | depois)
"""
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e5_comum import AMB, AVAL, E4, EVAL, P, RES, V1, V2, arquivos, sha256

rotulo = sys.argv[2] if len(sys.argv) > 2 else "antes"
linhas = []


def reg(grupo, arquivo, esperado, obtido):
    linhas.append({"grupo": grupo, "arquivo": arquivo, "sha256_esperado": esperado, "sha256_obtido": obtido,
                   "confere": esperado == obtido})


# 1. ambiente do decisor
with open(os.path.join(E4, "registro", "hashes_ambiente_depois.csv"), encoding="utf-8") as f:
    esperados = {r["arquivo"]: r["sha256"] for r in csv.DictReader(f)}
for rel, h in esperados.items():
    c = os.path.join(AMB, rel)
    if "__pycache__" in rel and not os.path.exists(c):
        continue  # cache de bytecode: não versionado, não é entregável
    reg("etapa4/ambiente_decisor", rel, h, sha256(c) if os.path.exists(c) else "AUSENTE")
extras = [rel for rel, _ in arquivos(AMB) if rel not in esperados and "__pycache__" not in rel]
for rel in extras:
    reg("etapa4/ambiente_decisor", rel, "NAO_LISTADO", sha256(os.path.join(AMB, rel)))

# 2. registro da etapa 4 (hashes no LOG_ETAPA_4.md)
log4 = open(P("LOG_ETAPA_4.md"), encoding="utf-8").read()
for nome, h in re.findall(r"^([\w.]+)\s+([0-9a-f]{64})\s*$", log4, flags=re.M):
    c = os.path.join(E4, "registro", nome)
    if os.path.exists(c):
        reg("etapa4/registro", nome, h, sha256(c))

# 3 e 4. pacotes
for nome, base in (("data/decision_input (v1)", V1), ("data/decision_input_v2", V2)):
    with open(os.path.join(base, "MANIFESTO.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rel = r["arquivo"].split("/", 2)[2] if r["arquivo"].startswith("data/") else r["arquivo"]
            c = os.path.join(base, rel)
            reg(nome, rel, r["sha256"], sha256(c) if os.path.exists(c) else "AUSENTE")

# 5. protocolo pré-registrado
log5 = open(P("LOG_PRE_ETAPA_5.md"), encoding="utf-8").read()
h_prot = re.search(r"([0-9a-f]{64})\s+etapa5/PROTOCOLO_AVALIACAO\.md", log5).group(1)
reg("protocolo", "etapa5/PROTOCOLO_AVALIACAO.md", h_prot, sha256(P("etapa5", "PROTOCOLO_AVALIACAO.md")))
reg("protocolo", "ambiente_avaliador/PROTOCOLO_AVALIACAO.md", h_prot, sha256(os.path.join(AVAL, "PROTOCOLO_AVALIACAO.md")))

# 6. cópias do ambiente do avaliador × originais
for nome, copia, orig in (("ambiente_avaliador/etapa4_congelada", os.path.join(AVAL, "etapa4_congelada"), E4),
                          ("ambiente_avaliador/dados_reservados", os.path.join(AVAL, "dados_reservados"), EVAL)):
    for rel, c in arquivos(copia):
        o = os.path.join(orig, rel)
        reg(nome, rel, sha256(o) if os.path.exists(o) else "AUSENTE_NO_ORIGINAL", sha256(c))

saida = os.path.join(RES, f"integridade_{rotulo}.csv")
with open(saida, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(linhas[0]))
    w.writeheader()
    w.writerows(linhas)

grupos = {}
for l in linhas:
    g = grupos.setdefault(l["grupo"], [0, 0])
    g[0] += 1
    g[1] += l["confere"]
print(f"integridade ({rotulo}):")
for g, (n, ok) in grupos.items():
    print(f"  {g}: {ok}/{n} conferem")
falhas = [l for l in linhas if not l["confere"]]
for l in falhas[:20]:
    print("  DIVERGE:", l["grupo"], l["arquivo"], l["sha256_esperado"][:12], l["sha256_obtido"][:12])
print("TOTAL:", len(linhas) - len(falhas), "/", len(linhas))
sys.exit(1 if falhas else 0)
