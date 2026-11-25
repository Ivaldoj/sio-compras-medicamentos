"""Dimensão B: reexecuta os scripts do decisor numa CÓPIA (trabalho/repro/) e compara as saídas com as congeladas.
Não altera nada em decisao_congelada/. Saída: trabalho/b01_reproducao.csv"""
import filecmp, os, shutil, subprocess, sys
import numpy as np
import pandas as pd

ORIG = "decisao_congelada/ambiente"
REP = "trabalho/repro"
if os.path.exists(REP):
    shutil.rmtree(REP)
shutil.copytree(os.path.join(ORIG, "data"), os.path.join(REP, "data"), ignore=shutil.ignore_patterns("__pycache__"))
os.makedirs(os.path.join(REP, "trabalho")); os.makedirs(os.path.join(REP, "saida"))
for s in ["00_explorar", "01_demanda", "02_precos", "03_estrategias", "04_sensibilidade", "05_registros"]:
    shutil.copy(os.path.join(ORIG, "trabalho", s + ".py"), os.path.join(REP, "trabalho"))
log = []
for s in ["00_explorar", "01_demanda", "02_precos", "03_estrategias", "04_sensibilidade", "05_registros"]:
    r = subprocess.run([sys.executable, "-I", "-X", "utf8", f"trabalho/{s}.py"], cwd=REP, capture_output=True, text=True, encoding="utf8")
    log.append((s, r.returncode))
    print(s, "rc=", r.returncode, r.stderr[-300:] if r.returncode else "")

linhas = []
for sub in ["trabalho", "saida"]:
    for f in sorted(os.listdir(os.path.join(REP, sub))):
        a, b = os.path.join(ORIG, sub, f), os.path.join(REP, sub, f)
        if f.endswith(".py") or not os.path.exists(a):
            continue
        if filecmp.cmp(a, b, shallow=False):
            linhas.append((f"{sub}/{f}", "idêntico byte a byte", 0.0)); continue
        dif = np.nan
        if f.endswith(".csv"):
            x, y = pd.read_csv(a), pd.read_csv(b)
            num = x.select_dtypes("number").columns
            if x.shape == y.shape:
                dif = float(np.nanmax(np.abs(x[num].values - y[num].values) / np.maximum(1e-9, np.abs(x[num].values)))) if len(num) else 0.0
                txt = (x.drop(columns=num).fillna("") != y.drop(columns=num).fillna("")).sum().sum()
                linhas.append((f"{sub}/{f}", f"difere; maior desvio relativo numérico={dif:.2e}; células texto diferentes={txt}", dif)); continue
        linhas.append((f"{sub}/{f}", "difere (não tabular ou forma diferente)", dif))
out = pd.DataFrame(linhas, columns=["arquivo", "resultado", "max_desvio_rel"])
out.to_csv("trabalho/b01_reproducao.csv", index=False)
print(out.to_string())
# arquivos congelados sem contrapartida reproduzida
print("só no congelado:", [f for sub in ["trabalho", "saida"] for f in os.listdir(os.path.join(ORIG, sub))
                           if not f.endswith(".py") and not os.path.exists(os.path.join(REP, sub, f))])

# explora_*_resumo: GROUP BY ALL ... ORDER BY ap_id não fixa a ordem dentro do item; comparar como conjuntos ordenados
for f in ["explora_bps_resumo.csv", "explora_cg_resumo.csv"]:
    x, y = (pd.read_csv(os.path.join(p, "trabalho", f)) for p in (ORIG, REP))
    k = list(x.columns)
    igual = x.sort_values(k).reset_index(drop=True).equals(y.sort_values(k).reset_index(drop=True))
    print(f, "igual após ordenar linhas:", igual)
