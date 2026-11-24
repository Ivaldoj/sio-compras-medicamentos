"""Análise exploratória/qualidade do Medicamentos Transparentes (tabelas parquet geradas pelo script 06).
Uso: python -I 07_analyze_transparencia.py <raiz_projeto> <tag>   (ex.: PB)"""
import os, sys
import pandas as pd
ROOT, tag = sys.argv[1], sys.argv[2]
P = lambda t: pd.read_parquet(os.path.join(ROOT, "data", "processed", f"mt_{t}_{tag}.parquet"))
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 70)
rel, it, lots, aw, ai, par, sup = (P(t) for t in ("releases", "ten_items", "ten_lots", "awards", "awa_items", "parties", "awa_suppliers"))

print("== releases:", len(rel), "| ocid distintos:", rel.ocid.nunique(), "| id distintos:", rel["id"].nunique())
rep = rel.groupby("ocid").coleta.nunique()
print("ocids presentes em >1 coleta mensal:", int((rep > 1).sum()), "| máx coletas por ocid:", int(rep.max()))
print("ocid duplicado dentro da mesma coleta:", int(rel.duplicated(["ocid", "coleta"]).sum()))
d = rel[rel.ocid.isin(rep[rep > 1].index)].sort_values(["ocid", "coleta"])
diffcols = [c for c in rel.columns if c not in ("arquivo", "coleta") and d.groupby("ocid")[c].nunique(dropna=False).max() > 1]
print("colunas que mudam entre coletas do mesmo ocid:", diffcols)
print("tags:", rel.tag.value_counts().to_dict())
rel["date_dt"] = pd.to_datetime(rel.date, errors="coerce", utc=True)
rel["date_mes"] = rel.date_dt.dt.strftime("%Y-%m")
print("release/date: min", rel.date_dt.min(), "max", rel.date_dt.max())
print("coleta == mês de release/date: %.1f%%" % (100 * (rel.coleta == rel.date_mes).mean()))
print("exemplos coleta x date_mes:", rel[["coleta", "date_mes"]].value_counts().head(8).to_dict())
print("releases por coleta:\n", rel.groupby("coleta").ocid.nunique().to_string())
print("\nmodalidade (procurementMethodDetails contém):")
print(rel["tender/procurementMethodDetails"].str.extract(r"modalidadeNome: ([^;]+)")[0].value_counts().to_string())
print("SRP (registro de preços):", rel["tender/procurementMethodDetails"].str.extract(r"srp: (\w+)")[0].value_counts().to_dict())
print("mainProcurementCategory:", rel["tender/mainProcurementCategory"].value_counts().to_dict())

# compradores
u = rel.drop_duplicates("ocid")
print("\ncompradores distintos (buyer/id):", u["buyer/id"].nunique())
b = u.groupby(["buyer/id", "buyer/name"]).agg(contratacoes=("ocid", "size"), valor_estimado=("tender/value/amount", lambda s: pd.to_numeric(s).sum()))
b.sort_values("contratacoes", ascending=False).to_csv(os.path.join(ROOT, "reports", f"mt_compradores_{tag}.csv"))
print(b.sort_values("contratacoes", ascending=False).head(15).round(0).to_string())
esf = P("par_det_classifications")
esf = esf[esf["parties/details/classifications/scheme"] == "BRA-ESFERA"].drop_duplicates("ocid")
print("esfera (contratações únicas):", esf["parties/details/classifications/description"].value_counts().to_dict())

# itens
it = it.drop_duplicates(["ocid", "tender/items/id"])  # remove repetição entre coletas
print("\n== itens de licitação únicos (ocid+item):", len(it))
print("classification/scheme:", it["tender/items/classification/scheme"].value_counts(dropna=False).to_dict())
print("CATMAT distintos:", it["tender/items/classification/id"].nunique())
for c in ("tender/items/quantity", "tender/items/unit/value/amount"):
    it[c + "_n"] = pd.to_numeric(it[c], errors="coerce")
print("quantidade preenchida %.1f%% | valor unitário estimado preenchido %.1f%%" % (100 * it["tender/items/quantity_n"].notna().mean(), 100 * it["tender/items/unit/value/amount_n"].notna().mean()))
print("unit/name top:", it["tender/items/unit/name"].value_counts().head(12).to_dict())
print("unit/name distintos:", it["tender/items/unit/name"].nunique())
print("dosageForm preenchido %.1f%% | administrationRoute %.1f%%" % (100 * it["tender/items/dosageForm"].notna().mean(), 100 * it["tender/items/administrationRoute"].notna().mean()))
print("valor unitário estimado = 0:", int((it["tender/items/unit/value/amount_n"] == 0).sum()))
lots = lots.drop_duplicates(["ocid", "tender/lots/id"])
print("\nstatus dos lotes/itens:", lots["tender/lots/statusDetails"].value_counts(dropna=False).to_dict())
print("orçamento sigiloso:", lots["tender/lots/lotsDetails/confidentialBudget"].value_counts(dropna=False).to_dict())

# adjudicações
ai = ai.drop_duplicates(["ocid", "awards/id", "awards/items/id"])
print("\n== itens adjudicados únicos:", len(ai), "| status:", ai["awards/items/status"].value_counts(dropna=False).to_dict())
m = it.merge(ai, left_on=["ocid", "tender/items/id"], right_on=["ocid", "awards/items/id"], how="left", indicator=True)
print("itens de licitação com adjudicação correspondente (ocid+item id): %.1f%%" % (100 * (m._merge == "both").mean()))
m["est"] = m["tender/items/unit/value/amount_n"]; m["adj"] = pd.to_numeric(m["awards/items/unit/value/amount"], errors="coerce")
mm = m[(m._merge == "both") & (m.est > 0) & (m.adj > 0)]
r = mm.adj / mm.est
print("razão unitário adjudicado/estimado: n=%d, quantis %s" % (len(r), r.quantile([.05, .25, .5, .75, .95]).round(3).to_dict()))
print("adjudicado > estimado:", int((r > 1).sum()), "| razão >10 ou <0.1:", int(((r > 10) | (r < .1)).sum()))
qd = (pd.to_numeric(mm["awards/items/quantity"], errors="coerce") != mm["tender/items/quantity_n"]).mean()
print("quantidade adjudicada ≠ quantidade licitada: %.1f%%" % (100 * qd))
print("mesmo nome de unidade (licitado x adjudicado): %.1f%%" % (100 * (mm["tender/items/unit/name"] == mm["awards/items/unit/name"]).mean()))
# medicamentos vs outros: palavra-chave no título (diagnóstico, não classificação oficial)
tit = u["tender/description"].fillna("").str.lower()
print("\ncontratações cujo objeto cita 'medicament':", int(tit.str.contains("medicament").sum()), "de", len(u))
print("objeto cita 'odontol' / 'laborat' / 'material':", int(tit.str.contains("odontol").sum()), int(tit.str.contains("laborat").sum()), int(tit.str.contains("material").sum()))
print("\nfornecedores distintos:", sup["awards/suppliers/id"].nunique())
it.to_parquet(os.path.join(ROOT, "data", "processed", f"mt_itens_unicos_{tag}.parquet"), index=False)
