"""Etapa 5 — utilidades comuns da avaliação independente.

Todos os scripts e5_* são executados da raiz do projeto:
    python -I -X utf8 etapa5_avaliacao_independente/scripts/<script>.py .
Somente leitura sobre etapa4/, data/decision_input*/ e data/evaluation_only/.
Toda escrita vai para etapa5_avaliacao_independente/resultados/ (ou para um diretório temporário).
"""
import hashlib
import os
import sys

RAIZ = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
P = lambda *a: os.path.join(RAIZ, *a)

E4 = P("etapa4")
AMB = P("etapa4", "ambiente_decisor")
SAIDA = P("etapa4", "ambiente_decisor", "saida")
TRAB = P("etapa4", "ambiente_decisor", "trabalho")
V1 = P("data", "decision_input")
V2 = P("data", "decision_input_v2")
EVAL = P("data", "evaluation_only")
AVAL = P("etapa5_avaliacao_independente", "ambiente_avaliador")
PRIM = P("etapa5_avaliacao_independente", "ambiente_avaliador", "evidencias_primarias")
RES = P("etapa5_avaliacao_independente", "resultados")
os.makedirs(RES, exist_ok=True)

CORTE = "2025-01-29"
# horizonte de 12 meses da necessidade (ETP de 29/01/2025)
HORIZ_INI, HORIZ_FIM = "2025-01-30", "2026-01-29"


def sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def arquivos(base):
    for d, _, fs in os.walk(base):
        for f in fs:
            c = os.path.join(d, f)
            yield os.path.relpath(c, base).replace(os.sep, "/"), c


def brl(v, casas=0):
    if v is None or v != v:
        return "—"
    s = f"{v:,.{casas}f}"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")
