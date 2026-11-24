"""Perfil completo do BPS (2025 e 2026) lido diretamente dos ZIPs originais (sem extrair).
Uso: python -I 04_profile_bps.py <raiz_projeto>
Saídas: reports/perfil_colunas_bps.csv, reports/bps_*.csv, data/processed/bps_2025_2026.parquet"""
import os, sys, zipfile
import pandas as pd

ROOT = sys.argv[1]
R = lambda *p: os.path.join(ROOT, *p)
frames = []
for ano in (2025, 2026):
    with zipfile.ZipFile(R("data", "raw", "bps", f"{ano}_csv.zip")) as z:
        df = pd.read_csv(z.open(f"{ano}.csv"), sep=";", dtype=str, encoding="utf-8", keep_default_na=False, na_values=[""])
    df["arquivo"] = f"{ano}_csv.zip"
    frames.append(df)
cols = [list(f.columns) for f in frames]
print("mesmas colunas 2025/2026:", cols[0] == cols[1])
bps = pd.concat(frames, ignore_index=True)
print("registros por arquivo:", bps.groupby("arquivo").size().to_dict())

# perfil de colunas
prof = []
for arq, g in bps.groupby("arquivo"):
    for c in bps.columns.drop("arquivo"):
        s = g[c]
        ex = s.dropna()
        prof.append(dict(base="BPS", arquivo=arq, coluna=c, registros=len(s), preenchidos=int(s.notna().sum()),
                         pct_preenchido=round(100 * s.notna().mean(), 2), distintos=int(s.nunique()),
                         exemplo=ex.iloc[0][:120] if len(ex) else ""))
pd.DataFrame(prof).to_csv(R("reports", "perfil_colunas_bps.csv"), index=False)

# tipagem
for c in ("qt_medicamento", "vl_preco_unitario", "vl_preco_total", "vl_capacidade", "validade_compra"):
    bps[c + "_num"] = pd.to_numeric(bps[c], errors="coerce")
for c in ("dt_compra", "dt_insercao"):
    bps[c + "_dt"] = pd.to_datetime(bps[c], format="%d/%m/%Y", errors="coerce")
print("falhas de conversão numérica:", {c: int(bps[c].notna().sum() - bps[c + "_num"].notna().sum()) for c in ("qt_medicamento", "vl_preco_unitario", "vl_preco_total")})
print("falhas de conversão de data:", {c: int(bps[c].notna().sum() - bps[c + "_dt"].notna().sum()) for c in ("dt_compra", "dt_insercao")})
print("dt_compra min/max:", bps.dt_compra_dt.min(), bps.dt_compra_dt.max())
print("dt_insercao min/max:", bps.dt_insercao_dt.min(), bps.dt_insercao_dt.max())
print("ano_compra x ano(dt_compra) divergentes:", int((bps.ano_compra.astype(float) != bps.dt_compra_dt.dt.year).sum()))
lag = (bps.dt_insercao_dt - bps.dt_compra_dt).dt.days
print("defasagem inserção-compra (dias): ", lag.describe(percentiles=[.25, .5, .75, .9]).round(1).to_dict())
print("inserção antes da compra:", int((lag < 0).sum()))

# contagens
bps["mes_compra"] = bps.dt_compra_dt.dt.to_period("M").astype(str)
bps.groupby("mes_compra").size().rename("registros").to_csv(R("reports", "bps_registros_por_mes.csv"))
uf = bps.groupby("sg_uf").agg(registros=("co_seq_bps", "size"), instituicoes=("cnpj_instituicao", "nunique"),
                               catmat=("co_catmat", "nunique"), valor_total=("vl_preco_total_num", "sum"))
uf.sort_values("registros", ascending=False).to_csv(R("reports", "bps_por_uf.csv"))
for c in ("ds_esfera", "tp_compra", "modalidade", "no_classe", "fg_generico", "sg_unidade_medida", "un_fornecimento"):
    print(f"\n{c}:\n", bps[c].value_counts(dropna=False).head(15).to_string())
print("\nclasses (co_classe) distintas:", bps.co_classe.nunique(), "| CATMAT distintos:", bps.co_catmat.nunique(), "| PDM distintos:", bps.no_pdm.nunique())
print("instituições (CNPJ) distintas:", bps.cnpj_instituicao.nunique(), "| nomes distintos:", bps.no_instituicao.nunique())

# consistência valor total = unitário × quantidade
calc = bps.vl_preco_unitario_num * bps.qt_medicamento_num
rel = (bps.vl_preco_total_num - calc).abs() / bps.vl_preco_total_num.where(bps.vl_preco_total_num > 0)
print("\ntotal vs unit*qtd: |dif| <=1%:", int((rel <= .01).sum()), "| >1%:", int((rel > .01).sum()), "| não calculável:", int(rel.isna().sum()))
print("qt<=0:", int((bps.qt_medicamento_num <= 0).sum()), "| preço unit <=0:", int((bps.vl_preco_unitario_num <= 0).sum()))
print("preço unitário (R$) quantis:", bps.vl_preco_unitario_num.quantile([0, .01, .25, .5, .75, .99, 1]).round(4).to_dict())
print("valor total (R$) soma por arquivo:", bps.groupby("arquivo").vl_preco_total_num.sum().round(2).to_dict())

# duplicidade
print("\nco_seq_bps duplicados:", int(bps.co_seq_bps.duplicated().sum()))
key = ["cnpj_instituicao", "dt_compra", "co_catmat", "cnpj_fornecedor", "qt_medicamento", "vl_preco_unitario", "nu_processo_compra"]
print("duplicados na chave de negócio", key, ":", int(bps.duplicated(key).sum()))
full = bps.columns.drop(["co_seq_bps", "arquivo", "dt_insercao", "dt_insercao_dt"]).tolist()
print("idênticos exceto co_seq_bps/dt_insercao:", int(bps.duplicated([c for c in full if not c.endswith(('_num', '_dt'))]).sum()))

# PB
pb = bps[bps.sg_uf == "PB"]
print("\nPB registros:", len(pb), "| instituições:", pb.cnpj_instituicao.nunique())
pb.groupby(["cnpj_instituicao", "no_instituicao", "no_municipio", "ds_esfera"]).agg(
    registros=("co_seq_bps", "size"), catmat=("co_catmat", "nunique"), valor_total=("vl_preco_total_num", "sum"),
    primeira=("dt_compra_dt", "min"), ultima=("dt_compra_dt", "max")).sort_values("registros", ascending=False).to_csv(
    R("reports", "bps_pb_instituicoes.csv"))

# variabilidade de preço por CATMAT+unidade de fornecimento (só como diagnóstico de dispersão)
g = bps.groupby(["co_catmat", "un_fornecimento"]).vl_preco_unitario_num
disp = pd.DataFrame({"n": g.size(), "mediana": g.median(), "p25": g.quantile(.25), "p75": g.quantile(.75), "min": g.min(), "max": g.max()})
disp["razao_max_min"] = disp["max"] / disp["min"].where(disp["min"] > 0)
disp = disp[disp.n >= 30].sort_values("n", ascending=False)
disp.to_csv(R("reports", "bps_dispersao_preco_catmat_unidade.csv"))
print("\ngrupos CATMAT+un_fornecimento com n>=30:", len(disp), "| razão max/min mediana:", round(disp.razao_max_min.median(), 1))
print("CATMATs com >1 un_fornecimento:", int((bps.groupby("co_catmat").un_fornecimento.nunique() > 1).sum()))

bps.drop(columns=[c for c in bps.columns if c.endswith("_dt")]).to_parquet(R("data", "processed", "bps_2025_2026.parquet"), index=False)
