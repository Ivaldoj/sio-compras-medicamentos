"""Qualidade do pacote de decisão (07): checagens contra as evidências primárias e o código de preparação.
Saídas: trabalho/p01_pacote.txt (relato), trabalho/p01_ap052.csv (mediana corrigida de AP052)"""
import zipfile
import numpy as np
import pandas as pd

PK = "decisao_congelada/ambiente/data/decision_input_nacional/"
cesta = pd.read_parquet(PK + "problema/cesta.parquet").set_index("ap_id")
cg = pd.read_parquet(PK + "mercado/precos_comprasgov.parquet")
out = []
def say(s):
    print(s); out.append(s)

# 1) regra de compatibilidade aceita SUPOSITÓRIO para item oral (n03_pacote_nacional.py, UN_SOLIDA) -> AP052 contaminado
sol = cg.ap_id.map(cesta.forma).isin(["comprimido", "capsula"])
ret = cg.nomeUnidadeFornecimento.fillna("").str.upper().str.startswith("SUPOSIT") | cg.descricaoItem.fillna("").str.upper().str.contains("USO RETAL")
bad = cg[sol & ret & (cg.compatibilidade == "compativel")]
say(f"[1] registros pré-corte 'compativel' de supositório/uso retal em item oral: {len(bad)} -> itens {sorted(bad.ap_id.unique())}")
w = cg[(cg.ap_id == "AP052") & (cg.compatibilidade == "compativel") & ~cg.flag_preco_extremo & (cg.dataResultado >= "2023-02-01") & (cg.dataResultado <= "2025-01-29")]
e = w[w.esfera == "E"]; e2 = e[~(e.nomeUnidadeFornecimento.fillna("").str.upper().str.startswith("SUPOSIT") | e.descricaoItem.str.upper().str.contains("USO RETAL"))]
say(f"    AP052 mediana estadual 24m usada pelo decisor = {e.preco_unitario.median():.4f} (n={len(e)}); sem supositório/uso retal = {e2.preco_unitario.median():.4f} (n={len(e2)}); p25-p75 corrigido {e2.preco_unitario.quantile(.25):.3f}-{e2.preco_unitario.quantile(.75):.3f}")
pd.DataFrame([dict(ap_id="AP052", mediana_estadual_24m_decisor=e.preco_unitario.median(), mediana_estadual_24m_sem_retal=e2.preco_unitario.median(),
                   n_decisor=len(e), n_corrigido=len(e2))]).to_csv("trabalho/p01_ap052.csv", index=False)
un = cg[cg.compatibilidade == "compativel"].groupby([cg.ap_id.map(cesta.forma), "nomeUnidadeFornecimento"]).size()
say("    unidades aceitas como 'compativel' por forma:\n" + un.to_string())

# 2) grupo de financiamento: AP007 (imunoglobulina 5 g) aparece 1B no pacote; RENAME 2024 Anexo III, p. 209 do PDF, lista 5 g como 1A
say(f"[2] AP007 grupo no pacote = {cesta.loc['AP007','grupo_financiamento']} ({cesta.loc['AP007','grupo_metodo']}); RENAME 2024 Anexo III p.209: '5g ... 1A' (trabalho/d01_rename.py)")
say(f"    itens com grupo atribuído pelo '1º grupo do trecho': {list(cesta.index[cesta.grupo_metodo.str.startswith('1º')])}")

# 3) unidade de dispensação ausente/mal extraída
u = cesta.unidade_dispensacao.fillna("")
say(f"[3] unidade_dispensacao vazia: {list(cesta.index[u == ''])}; 'biossimilar': {list(cesta.index[u.str.startswith('biossimilar')])}")

# 4) flag_preco_extremo marca compras DLOG programáticas (mediana de referência dominada por compras pequenas)
dl = cg[cg.nomeUasg.str.startswith("DEPARTAMENTO DE LOG") & (cg.quantidade >= 0.1 * cg.ap_id.map(cesta.dispensacao_12m_pre_corte))]
say(f"[4] compras DLOG programáticas marcadas como preço extremo: {int(dl.flag_preco_extremo.sum())} de {len(dl)} -> {sorted(dl[dl.flag_preco_extremo].ap_id.unique())}")

# 5) recursos_federais 2024 x arquivo primário do Portal da Transparência
z = zipfile.ZipFile("evidencias_primarias/orcamento/orcamento_despesa_2024.zip")
o = pd.read_csv(z.open(z.namelist()[0]), sep=";", encoding="latin-1", dtype=str)
o = o[(o["CÓDIGO AÇÃO"] == "4705") & o["NOME ÓRGÃO SUPERIOR"].str.contains("SA[UÚ]DE", case=False, regex=True, na=False)]
v = pd.to_numeric(o["ORÇAMENTO EMPENHADO (R$)"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False)).sum()
rf = pd.read_csv(PK + "problema/recursos_federais.csv")
say(f"[5] 4705/2024 empenhado: pacote {rf[(rf['CÓDIGO AÇÃO'].astype(str)=='4705')&(rf['EXERCÍCIO']==2024)].empenhado.iloc[0]:,.2f}; arquivo primário {v:,.2f}; data do arquivo no zip {z.infolist()[0].date_time}")

# 6) teto CMED do pacote x lista primária (PMVG 0% se CAP; PF 0% caso contrário), por registro+apresentação
cm = pd.read_parquet(PK + "mercado/cmed_teto.parquet")
x = pd.read_excel("evidencias_primarias/cmed/cmed_pmvg_20250107.xls", header=52, dtype=str)
x.columns = [str(c).strip() for c in x.columns]
x["chave"] = x["REGISTRO"].str.strip() + "|" + x["APRESENTAÇÃO"].str.strip()
cm["chave"] = cm.registro.str.strip() + "|" + cm.apresentacao.str.strip()
m = cm.merge(x.drop_duplicates("chave"), on="chave", how="left")
num = lambda s: pd.to_numeric(s.astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False), errors="coerce")
num = lambda s: pd.to_numeric(s, errors="coerce").fillna(pd.to_numeric(s.astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False), errors="coerce"))
pmvg0, pf0 = num(m["PMVG 0%"]), num(m["PF 0%"])
esper = np.where(m.cap, pmvg0, pf0) / m.unidades_por_embalagem
ok = np.isclose(esper, m.teto_gov_0_unit, rtol=1e-3)
say(f"[6] teto CMED 0% por unidade: {int(m['REGISTRO'].notna().sum())}/{len(m)} apresentações localizadas na lista primária; conferem {int(ok.sum())}; divergem {int((~ok & m['REGISTRO'].notna()).sum())}")
dv = m[~ok & m["REGISTRO"].notna()][["ap_id", "registro", "apresentacao", "cap", "unidades_por_embalagem", "teto_gov_0_unit"]].assign(esperado=esper[~ok & m["REGISTRO"].notna()])
if len(dv): say(dv.head(10).to_string())
say(f"    colunas de ICMS na lista primária acima de 18%: {[c for c in x.columns if c.startswith('PMVG 2')][:6]} (o decisor aproximou o ICMS por 18%)")

# 7) SIA: mesma base 'atual com reprocessamentos' para pré e pós; pós termina em jan/2026 (notas TabNet: últimos 6 meses sujeitos a atualização)
say("[7] cesta.base_disponibilidade: " + cesta.base_disponibilidade.iloc[0])
open("trabalho/p01_pacote.txt", "w", encoding="utf8").write("\n".join(out))
