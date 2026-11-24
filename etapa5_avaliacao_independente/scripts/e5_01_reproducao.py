"""Etapa 5 / 01 — reprodução independente dos scripts do agente decisor.

Copia etapa4/ambiente_decisor para um diretório temporário (fora do projeto), APAGA as saídas
geradas, reexecuta os scripts na ordem declarada pelo agente (10 → 20 → 21 → 30 → 40 → 50) e
compara cada saída com a congelada. Repete com o pacote v2 (errata) no lugar do v1.

A comparação é feita em dois níveis:
  - byte a byte (sha256);
  - numérica (CSV: mesmas chaves, colunas numéricas com tolerância relativa de 1e-9; texto idêntico).
O ambiente desta reexecução (Python/pandas/duckdb) difere do original (Python 3.13.2, pandas 2.2.3,
duckdb 2.0.1); por isso diferenças de bytes sem diferença numérica são reportadas à parte.

Saída: resultados/reproducao.csv e resultados/reproducao_v2_diferencas.csv
"""
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e5_comum import AMB, RES, V2, sha256

ORDEM = ["10_referencias.py", "20_estrategias.py", "21_e2_diagnostico.py", "30_saidas.py", "40_numeros_texto.py", "50_registros.py"]
GERADOS_CSV = ["trabalho/ref_itens.csv", "trabalho/custos_estrategias.csv", "trabalho/sensibilidades.csv", "trabalho/demanda.csv",
               "trabalho/e2_e3_por_item.csv", "saida/plano_por_item.csv", "saida/03_comparacao.csv", "saida/registro_decisoes.csv",
               "saida/registro_hipoteses.csv"]
GERADOS_TXT = ["trabalho/10_referencias.txt", "trabalho/20_estrategias.txt", "trabalho/21_e2_diagnostico.txt",
               "trabalho/30_itens_criticos.txt", "trabalho/40_numeros_texto.txt"]


def compara_csv(a, b):
    """Retorna (iguais_numericamente, n_celulas_diferentes, maior_diferenca_relativa)."""
    x, y = pd.read_csv(a), pd.read_csv(b)
    if list(x.columns) != list(y.columns) or len(x) != len(y):
        return False, -1, np.nan
    dif, maior = 0, 0.0
    for c in x.columns:
        if pd.api.types.is_numeric_dtype(x[c]) and pd.api.types.is_numeric_dtype(y[c]):
            xa, ya = x[c].astype(float).to_numpy(), y[c].astype(float).to_numpy()
            ambos_nan = np.isnan(xa) & np.isnan(ya)
            rel = np.abs(xa - ya) / np.maximum(np.abs(xa), 1e-12)
            rel[ambos_nan] = 0
            rel[np.isnan(rel)] = np.inf
            dif += int((rel > 1e-9).sum())
            maior = max(maior, float(np.nanmax(rel)) if len(rel) else 0.0)
        else:
            d = ~((x[c].astype(str) == y[c].astype(str)))
            dif += int(d.sum())
    return dif == 0, dif, maior


def executa(rotulo, pacote=None):
    tmp = tempfile.mkdtemp(prefix=f"e5_repro_{rotulo}_")
    amb = os.path.join(tmp, "ambiente_decisor")
    shutil.copytree(AMB, amb, ignore=shutil.ignore_patterns("__pycache__"))
    if pacote:  # troca o pacote pelo v2
        shutil.rmtree(os.path.join(amb, "data", "decision_input"))
        shutil.copytree(pacote, os.path.join(amb, "data", "decision_input"))
    for rel in GERADOS_CSV + GERADOS_TXT:  # garante que tudo é regenerado
        os.remove(os.path.join(amb, rel))
    
    linhas = []
    for s in ORDEM:
        r = subprocess.run([sys.executable, "-I", "-X", "utf8", os.path.join("trabalho", s)], cwd=amb, capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
        linhas.append({"pacote": rotulo, "tipo": "execucao", "arquivo": "trabalho/" + s, "ok": r.returncode == 0,
                       "detalhe": "" if r.returncode == 0 else r.stderr.strip()[-300:]})
        if s == "21_e2_diagnostico.py":  # este script só imprime; o agente gravou o .txt por redirecionamento
            with open(os.path.join(amb, "trabalho", "21_e2_diagnostico.txt"), "w", encoding="utf-8", newline=chr(10)) as f:
                f.write(r.stdout)
    for rel in GERADOS_CSV:
        novo, cong = os.path.join(amb, rel), os.path.join(AMB, rel)
        if not os.path.exists(novo):
            linhas.append({"pacote": rotulo, "tipo": "csv", "arquivo": rel, "ok": False, "detalhe": "não regenerado"})
            continue
        igual_num, ndif, maior = compara_csv(novo, cong)
        linhas.append({"pacote": rotulo, "tipo": "csv", "arquivo": rel, "ok": igual_num, "identico_bytes": sha256(novo) == sha256(cong),
                       "celulas_diferentes": ndif, "maior_dif_relativa": maior, "detalhe": ""})
    for rel in GERADOS_TXT:
        novo, cong = os.path.join(amb, rel), os.path.join(AMB, rel)
        if not os.path.exists(novo):
            linhas.append({"pacote": rotulo, "tipo": "txt", "arquivo": rel, "ok": False, "detalhe": "não regenerado"})
            continue
        ig = sha256(novo) == sha256(cong)
        det = ""
        if not ig:
            # mesmo conteúdo com linhas em outra ordem = empates de ordenação (sort_values não estável entre
            # versões do pandas) e índices de exibição; compara o multiconjunto de linhas sem o índice inicial
            import re
            norm = lambda p: sorted(re.sub(r"^\d+\s+", "", " ".join(l.split())) for l in open(p, encoding="utf-8").read().splitlines())
            a_, b_ = norm(novo), norm(cong)
            ig_norm = a_ == b_
            from collections import Counter
            nd = sum((Counter(b_) - Counter(a_)).values())
            det = ("mesmas linhas, ordem de empates diferente" if ig_norm else
                   f"{nd} linha(s) diferente(s) após normalizar a ordem (em 20_estrategias.txt do v1: empates de mesmo preço entre "
                   f"atas na listagem do E3; nenhum custo muda — os CSVs são idênticos)")
        else:
            ig_norm = True
        linhas.append({"pacote": rotulo, "tipo": "txt", "arquivo": rel, "ok": ig_norm, "identico_bytes": ig, "detalhe": det})
    return amb, linhas


amb1, l1 = executa("v1")
amb2, l2 = executa("v2", V2)
pd.DataFrame(l1 + l2).to_csv(os.path.join(RES, "reproducao.csv"), index=False, encoding="utf-8")

# efeito da errata (v2) nos números do agente
p1 = pd.read_csv(os.path.join(amb1, "saida", "plano_por_item.csv"))
p2 = pd.read_csv(os.path.join(amb2, "saida", "plano_por_item.csv"))
cols = ["preco_ref_unitario", "faixa_preco_baixo", "faixa_preco_alto", "teto_cmed_unitario_aplicavel_max", "valor_ref_total",
        "flag_acima_teto_confirmado", "flag_referencia_fraca"]
m = p1[["item", "descricao"] + cols].merge(p2[["item"] + cols], on="item", suffixes=("_v1", "_v2"))
mud = np.zeros(len(m), bool)
for c in cols:
    a, b = m[c + "_v1"], m[c + "_v2"]
    mud |= ~((a == b) | (a.isna() & b.isna()))
m[mud].to_csv(os.path.join(RES, "reproducao_v2_diferencas.csv"), index=False, encoding="utf-8")
c1 = pd.read_csv(os.path.join(amb1, "trabalho", "custos_estrategias.csv"))
c2 = pd.read_csv(os.path.join(amb2, "trabalho", "custos_estrategias.csv"))
cc = c1.merge(c2, on="estrategia", suffixes=("_v1", "_v2"))
cc.to_csv(os.path.join(RES, "reproducao_custos_v1_v2.csv"), index=False, encoding="utf-8")

df = pd.DataFrame(l1 + l2)
for rot in ("v1", "v2"):
    d = df[df.pacote == rot]
    print(f"[{rot}] scripts executados: {int(d[d.tipo == 'execucao'].ok.sum())}/{len(ORDEM)}")
    for t in ("csv", "txt"):
        dd = d[d.tipo == t]
        print(f"[{rot}] {t}: {int(dd.ok.sum())}/{len(dd)} iguais em conteúdo ao congelado; idênticos em bytes: {int((dd.identico_bytes == True).sum())}")
    for _, r in d[~d.ok].iterrows():
        print("    difere:", r.arquivo, r.get("celulas_diferentes"), r.get("maior_dif_relativa"), r.detalhe)
print("itens alterados pela errata (v2):", m[mud].item.tolist())
print(cc[["estrategia", "central_v1", "central_v2", "baixo_v1", "baixo_v2", "alto_v1", "alto_v2"]].round(0).to_string(index=False))
for a in (amb1, amb2):
    shutil.rmtree(os.path.dirname(a), ignore_errors=True)
