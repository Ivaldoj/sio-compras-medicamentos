"""Etapa 2 — execução da despesa com material farmacológico de Santa Luzia/PB (TCE-PB/SAGRES), 2024–2026,
e vínculo dos empenhos com os pregões de medicamentos (numero_licitacao).
Uso: python -I -X utf8 20_caso_santa_luzia_despesas.py <raiz_projeto>
Saídas: reports/caso_sl_farmaco_anual.csv, caso_sl_farmaco_mensal.csv, caso_sl_farmaco_por_licitacao.csv, caso_sl_farmaco_por_credor.csv"""
import glob, os, sys, zipfile
import pandas as pd

ROOT = sys.argv[1]
R = lambda f: os.path.join(ROOT, "reports", f)
fr = []
for zp in sorted(glob.glob(os.path.join(ROOT, "data", "raw", "complementares", "tcepb", "170_santa_luzia_despesas-*.zip"))):
    with zipfile.ZipFile(zp) as z:
        d = pd.read_csv(z.open(z.namelist()[0]), sep=";", dtype=str, encoding="utf-8-sig")
    d["ano"] = os.path.basename(zp)[-8:-4]
    fr.append(d)
d = pd.concat(fr, ignore_index=True)
for c in ("valor_empenhado", "valor_liquidado", "valor_pago"):
    d[c] = pd.to_numeric(d[c].str.replace(".", "", regex=False).str.replace(",", ".", regex=False), errors="coerce")
print("empenhos por ano:", d.groupby("ano").size().to_dict(), "| última data:", d.data_empenho.max())
f = d[(d.codigo_elemento_despesa.isin(["30", "32"])) & d.codigo_subelemento_exibicao.str.contains("FARMACOL", case=False, na=False)].copy()
print("elementos/subelementos usados:", f.groupby(["codigo_elemento_despesa", "elemento_despesa", "codigo_subelemento_exibicao"]).size().to_dict())
# o edital também cita 3390.32 (distribuição gratuita): conferir quanto vai para esse elemento com histórico de medicamentos
e32 = d[(d.codigo_elemento_despesa == "32") & d.historico.str.contains("MEDICAMENT", case=False, na=False)]
print("elemento 32 com 'medicament' no histórico: empenhos=%d, empenhado=%.2f" % (len(e32), e32.valor_empenhado.sum()))
f = pd.concat([f, e32[~e32.index.isin(f.index)]])
V = ["valor_empenhado", "valor_liquidado", "valor_pago"]
an = f.groupby("ano")[V].sum().round(2); an["empenhos"] = f.groupby("ano").size()
an.to_csv(R("caso_sl_farmaco_anual.csv")); print("\nanual:\n", an.to_string())
print("\nunidades gestoras:", f.groupby(["ano", "descricao_unidade_gestora"]).valor_empenhado.sum().round(0).to_dict())
print("fontes:", f.groupby("descricao_fonte_recurso").valor_empenhado.sum().round(0).sort_values(ascending=False).head(6).to_dict())
f.groupby(["ano", "mes"])[V].sum().round(2).to_csv(R("caso_sl_farmaco_mensal.csv"))
f["licitacao"] = f.numero_licitacao.fillna("") + " | " + f.modalidade_licitacao.fillna("")
lic = f.groupby(["ano", "licitacao"])[V].sum().round(2); lic["empenhos"] = f.groupby(["ano", "licitacao"]).size(); lic["credores"] = f.groupby(["ano", "licitacao"]).cpf_cnpj.nunique()
lic.to_csv(R("caso_sl_farmaco_por_licitacao.csv")); print("\npor licitação:\n", lic.to_string())
# credores: só CNPJ (14 dígitos) e soma; nomes de pessoas físicas não são exportados
cr = f[f.cpf_cnpj.str.len() == 14].groupby(["ano", "cpf_cnpj", "nome_credor"])["valor_empenhado"].sum().round(2)
cr.to_csv(R("caso_sl_farmaco_por_credor.csv"))
print("\ncredores PJ por ano:", f[f.cpf_cnpj.str.len() == 14].groupby("ano").cpf_cnpj.nunique().to_dict(), "| credores não-PJ:", int((f.cpf_cnpj.str.len() != 14).sum()), "empenhos")
