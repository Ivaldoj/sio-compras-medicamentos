"""Etapa 2 — resume organizações candidatas a partir dos dados já processados na Etapa 1 (sem novos downloads).
Uso: python -I -X utf8 17_candidatas.py <raiz_projeto>
Saídas: reports/etapa2_candidatas_resumo.csv e reports/etapa2_contratacoes_candidatas.csv (uma linha por contratação)."""
import os, sys
import pandas as pd

ROOT = sys.argv[1]
P = lambda f: pd.read_parquet(os.path.join(ROOT, "data", "processed", f))
# grupo -> CNPJs (14 dígitos) usados no MT/PNCP e no BPS
CAND = {
    "SES-PB": ["08778268000160"],
    "Campina Grande (Município + FMS)": ["08993917000146", "24513574000121"],
    "Fundação PB Saúde": ["38111778000140"],
    "EBSERH (HUs na PB)": ["15126437000305", "15126437000143"],
    "Salgadinho (Município + FMS)": ["08881666000108"],
    "Santa Luzia (Município + FMS)": ["09090689000167"],
}
rel = P("mt_releases_PB.parquet").sort_values("coleta").drop_duplicates("ocid", keep="last")
rel["cnpj"] = rel["buyer/id"].str.replace("BR-CNPJ-", "").str.zfill(14)
det = rel["tender/procurementMethodDetails"].fillna("")
rel["modalidade"] = det.str.extract(r"modalidadeNome: ([^;]+)")[0]
rel["srp"] = det.str.extract(r"srp: (\w+)")[0]
rel["obj"] = rel["tender/description"].fillna("")
rel["so_medicamento"] = rel.obj.str.contains("medicament", case=False) & ~rel.obj.str.contains("odontol|laborat|material m[eé]dico|insumo", case=False)
it = P("mt_itens_unicos_PB.parquet")
lots = P("mt_ten_lots_PB.parquet").sort_values("coleta").drop_duplicates(["ocid", "tender/lots/id"], keep="last")
ai = P("mt_awa_items_PB.parquet").drop_duplicates(["ocid", "awards/id", "awards/items/id"])
bps = P("bps_2025_2026.parquet"); bps = bps[bps.sg_uf == "PB"]
bps_mun = {"Campina Grande (Município + FMS)": "CAMPINA GRANDE", "Salgadinho (Município + FMS)": "SALGADINHO", "Santa Luzia (Município + FMS)": "SANTA LUZIA"}

rows, lst = [], []
for g, cnpjs in CAND.items():
    r = rel[rel.cnpj.isin(cnpjs)]
    i = it[it.ocid.isin(r.ocid)]
    l = lots[lots.ocid.isin(r.ocid)]
    st = l["tender/lots/statusDetails"].value_counts().to_dict()
    b = bps[bps.cnpj_instituicao.isin(cnpjs) | (bps.no_municipio == bps_mun.get(g, "--"))]
    rows.append(dict(grupo=g, cnpjs=";".join(cnpjs), contratacoes_mt=len(r), so_medicamentos=int(r.so_medicamento.sum()),
                     srp=int((r.srp == "True").sum()), itens=len(i), catmat=i["tender/items/classification/id"].nunique(),
                     itens_homologados=st.get("Homologado", 0), itens_fracassados_desertos=st.get("Fracassado", 0) + st.get("Deserto", 0),
                     itens_em_andamento=st.get("Em andamento", 0), itens_adjudicados=int(ai.ocid.isin(r.ocid).sum()),
                     valor_estimado=round(pd.to_numeric(r["tender/value/amount"], errors="coerce").sum(), 2),
                     primeira_abertura=str(r["tender/tenderPeriod/startDate"].dropna().min())[:10], ultima_abertura=str(r["tender/tenderPeriod/startDate"].dropna().max())[:10],
                     registros_bps=len(b), bps_inicio=str(pd.to_datetime(b.dt_compra, format="%d/%m/%Y").min())[:10] if len(b) else "",
                     bps_fim=str(pd.to_datetime(b.dt_compra, format="%d/%m/%Y").max())[:10] if len(b) else ""))
    for _, x in r.iterrows():
        li = l[l.ocid == x.ocid]["tender/lots/statusDetails"].value_counts().to_dict()
        lst.append(dict(grupo=g, numeroControlePNCP=x["id"], ocid=x.ocid, abertura=str(x["tender/tenderPeriod/startDate"])[:10],
                        modalidade=x.modalidade, srp=x.srp, so_medicamento=x.so_medicamento, objeto=x.obj[:160],
                        itens=int((it.ocid == x.ocid).sum()), homologados=li.get("Homologado", 0), em_andamento=li.get("Em andamento", 0),
                        fracassados_desertos=li.get("Fracassado", 0) + li.get("Deserto", 0),
                        valor_estimado=x["tender/value/amount"]))
res = pd.DataFrame(rows); res.to_csv(os.path.join(ROOT, "reports", "etapa2_candidatas_resumo.csv"), index=False)
pd.set_option("display.width", 300); pd.set_option("display.max_columns", 30)
print(res.T.to_string())
L = pd.DataFrame(lst).sort_values(["grupo", "abertura"])
L.to_csv(os.path.join(ROOT, "reports", "etapa2_contratacoes_candidatas.csv"), index=False)
pd.set_option("display.max_colwidth", 90)
for g in CAND:
    s = L[(L.grupo == g) & L.so_medicamento]
    print(f"\n== {g}: {len(s)} contratações só de medicamentos")
    print(s[["numeroControlePNCP", "abertura", "modalidade", "srp", "itens", "homologados", "em_andamento", "fracassados_desertos", "valor_estimado", "objeto"]].head(25).to_string(index=False))
