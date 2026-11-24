"""Etapa 2 — processa a lista CMED de PF/PMVG publicada em 06/01/2025 (arquivo de 07/01/2025, vigente na data de decisão)
e a vincula aos itens do caso Santa Luzia só com informação anterior à decisão:
item --(CATMAT identificado)--> registros Anvisa do BPS inseridos até a data --> apresentações CMED jan/2025.
Uso: python -I -X utf8 23_cmed_jan2025.py <raiz_projeto> [data_decisao=2025-01-29]
Requer xlrd (formato .xls BIFF). Saídas: data/processed/cmed_pmvg_20250107.parquet,
data/processed/caso_santa_luzia/pre_decisao/itens_cmed_jan2025.csv e reports/caso_sl_cmed_cobertura.csv.
Preços CMED são por APRESENTAÇÃO (embalagem); nenhuma conversão para unidade de fornecimento é feita aqui."""
import os, sys, zipfile
import pandas as pd

ROOT = sys.argv[1]
DEC = pd.Timestamp(sys.argv[2] if len(sys.argv) > 2 else "2025-01-29")
P = lambda *p: os.path.join(ROOT, *p)

raw = pd.read_excel(P("data", "raw", "complementares", "cmed_pmvg_20250107.xls"), engine="xlrd", header=None, dtype=str, nrows=80)
hdr = raw.index[raw[0].astype(str).str.strip().str.upper().str.startswith("SUBST")][0]
c = pd.read_excel(P("data", "raw", "complementares", "cmed_pmvg_20250107.xls"), engine="xlrd", header=hdr, dtype=str)
c.columns = [str(x).strip() for x in c.columns]
c = c[c["REGISTRO"].notna()]
c["reg"] = c["REGISTRO"].str.replace(r"\D", "", regex=True)
precos = [x for x in c.columns if x.startswith(("PF ", "PMVG "))]
for x in precos:  # decimal com vírgula ou número já convertido pelo Excel
    c[x] = pd.to_numeric(c[x].str.replace(".", "", regex=False).str.replace(",", ".", regex=False) if c[x].str.contains(",", na=False).any() else c[x], errors="coerce")
c.to_parquet(P("data", "processed", "cmed_pmvg_20250107.parquet"), index=False)
print("CMED jan/2025: linha de cabeçalho", hdr, "| apresentações:", len(c), "| colunas:", len(c.columns), "| registros distintos:", c.reg.nunique())
print("tamanho do registro:", c.reg.str.len().value_counts().head(3).to_dict())
print("regime:", c["REGIME DE PREÇO"].value_counts().to_dict(), "| CAP=Sim:", int((c.CAP.str.strip() == "Sim").sum()),
      "| restrição hospitalar=Sim:", int((c["RESTRIÇÃO HOSPITALAR"].str.strip() == "Sim").sum()))
print("PF sem impostos vazio: %d | PMVG sem impostos vazio: %d" % (c["PF Sem Impostos"].isna().sum(), c[[x for x in precos if x.startswith("PMVG Sem")][0]].isna().sum()))
n26 = pd.read_excel(P("data", "raw", "complementares", "cmed_lista_pmvg_20261109.xlsx"), sheet_name="Lista PMVG", nrows=0).columns
print("colunas só em jan/2025:", sorted(set(c.columns) - set(map(str.strip, n26)) - {"reg"}))
print("colunas só em nov/2026:", sorted(set(map(str.strip, n26)) - set(c.columns)))
assert c.reg.str.len().eq(13).mean() > 0.99, "formato de registro inesperado"

# vínculo pré-decisão
it = pd.read_csv(P("data", "processed", "caso_santa_luzia", "pre_decisao", "itens_necessidade_e_referencias.csv"), dtype={"catmat_identificado": str})
fr = []
for ano in (2024, 2025):
    with zipfile.ZipFile(P("data", "raw", "bps", f"{ano}_csv.zip")) as z:
        fr.append(pd.read_csv(z.open(z.namelist()[0]), sep=";", dtype=str, usecols=["co_catmat", "registro_anvisa", "dt_insercao", "un_fornecimento"]))
b = pd.concat(fr)
b = b[pd.to_datetime(b.dt_insercao, format="%d/%m/%Y") <= DEC].dropna(subset=["registro_anvisa"])
b["reg"] = b.registro_anvisa.str.replace(r"\D", "", regex=True)
regs = b.groupby("co_catmat").reg.agg(lambda s: sorted(set(s) - {""}))
it["registros_bps"] = it.catmat_identificado.map(regs)
lk = it.dropna(subset=["registros_bps"]).explode("registros_bps").rename(columns={"registros_bps": "reg"})
lk = lk.merge(c[["reg", "SUBSTÂNCIA", "LABORATÓRIO", "PRODUTO", "APRESENTAÇÃO", "TIPO DE PRODUTO (STATUS DO PRODUTO)", "REGIME DE PREÇO", "CAP", "RESTRIÇÃO HOSPITALAR"] + precos],
              on="reg", how="inner")
keep = ["item", "descricao", "unidade", "catmat_identificado", "reg"]
lk = lk[keep + [x for x in lk.columns if x not in keep and x not in it.columns]]
lk.to_csv(P("data", "processed", "caso_santa_luzia", "pre_decisao", "itens_cmed_jan2025.csv"), index=False)
cov = pd.DataFrame({"item": it.item, "valor_total_estimado_orgao": it.valor_total_estimado_orgao,
                    "tem_catmat": it.catmat_identificado.notna(), "tem_registro_bps": it.registros_bps.notna(),
                    "apresentacoes_cmed": it.item.map(lk.groupby("item").size()).fillna(0).astype(int)})
cov.to_csv(P("reports", "caso_sl_cmed_cobertura.csv"), index=False)
ok = cov.apresentacoes_cmed > 0
print("\nitens: %d | com CATMAT: %d | com registro Anvisa no BPS pré-decisão: %d | com ≥1 apresentação na CMED jan/2025: %d (%.1f%% do valor estimado)" % (
    len(cov), cov.tem_catmat.sum(), cov.tem_registro_bps.sum(), ok.sum(), 100 * cov.valor_total_estimado_orgao[ok].sum() / cov.valor_total_estimado_orgao.sum()))
print("apresentações por item (itens vinculados): mediana %.0f, máx %d" % (cov.apresentacoes_cmed[ok].median(), cov.apresentacoes_cmed.max()))
print("itens vinculados com CAP=Sim em alguma apresentação:", int(lk[lk.CAP.str.strip() == "Sim"].item.nunique()))
ex = lk[lk.item.isin(it.nlargest(3, "valor_total_estimado_orgao").item)].groupby("item").first()
print("\nexemplos (3 maiores itens):\n", ex[["descricao", "PRODUTO", "APRESENTAÇÃO", "PF Sem Impostos", [x for x in precos if x.startswith("PMVG Sem")][0], "CAP"]].to_string())
