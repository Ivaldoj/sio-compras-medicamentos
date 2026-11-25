"""E2: preço de referência do decisor x preços observados depois do corte (Compras.gov.br e BPS), por apresentação e esfera.
Janela principal H = resultado/compra de 30/01/2025 a 31/01/2026 (horizonte do decisor). Janela estendida X = todo o pós-corte.
Filtros iguais aos do decisor: compatibilidade='compativel' e sem flag_preco_extremo nas medianas; compras DLOG programáticas
(q >= 10% da dispensação 12m pré-corte, regra H09 do decisor) incluem preços marcados extremos (regra D08 do decisor).
BPS pós: sem flag de compatibilidade -> filtro por unidade de fornecimento coerente com a forma; extremo = fora de [0,1x; 10x]
da mediana pré-corte (cesta.preco_pre_mediana). BPS é conferência: nunca somado ao Compras.gov.
Categoria de valor de todos os preços: preço homologado/praticado em compra pública (não é pagamento).
Saída: trabalho/e02_precos.csv"""
import numpy as np
import pandas as pd

H0, H1 = "2025-01-30", "2026-01-31"
PK = "decisao_congelada/ambiente/data/decision_input_nacional/"
cesta = pd.read_parquet(PK + "problema/cesta.parquet").set_index("ap_id")
plano = pd.read_csv("decisao_congelada/ambiente/saida/plano_por_apresentacao.csv").set_index("ap_id")
pr = pd.read_csv("decisao_congelada/ambiente/trabalho/precos_referencia.csv").set_index("ap_id")
cg = pd.read_parquet("dados_reservados/precos_comprasgov_pos.parquet")
cg = cg[(cg.quantidade > 0) & (cg.preco_unitario > 0)]
# correção do avaliador (falha do pacote, ver 07): em itens sólidos orais, descartar supositório / uso retal vinculados por CATMAT
sol_cg = cg.ap_id.map(cesta.forma).isin(["comprimido", "capsula"])
retal = (cg.nomeUnidadeFornecimento.fillna("").str.upper().str.startswith("SUPOSIT")) | cg.descricaoItem.fillna("").str.upper().str.contains("USO RETAL")
print("registros pós descartados por supositório/uso retal em item oral:", int((sol_cg & retal).sum()), sorted(cg[sol_cg & retal].ap_id.unique()))
cg = cg[~(sol_cg & retal)]
cg["H"] = (cg.dataResultado >= H0) & (cg.dataResultado <= H1)
ok = cg[(cg.compatibilidade == "compativel") & ~cg.flag_preco_extremo]
dl = cg[(cg.compatibilidade == "compativel") & cg.nomeUasg.str.startswith("DEPARTAMENTO DE LOG")].copy()
dl = dl[dl.quantidade >= 0.10 * dl.ap_id.map(cesta.dispensacao_12m_pre_corte)]

bps = pd.read_parquet("dados_reservados/precos_bps_2025_2026.parquet")
bps["dt"] = pd.to_datetime(bps.dt_compra, format="%d/%m/%Y")
bps["H"] = (bps.dt >= H0) & (bps.dt <= H1)
SOL = {"COMPRIMIDO", "CÁPSULA", "DRÁGEA"}; INJ = {"FRASCO-AMPOLA", "FRASCO", "AMPOLA", "SERINGA"}
solido = bps.ap_id.map(cesta.forma).isin(["comprimido", "capsula"])
bps["compat"] = np.where(solido, bps.un_fornecimento.isin(SOL), bps.un_fornecimento.isin(INJ))
r = bps.vl_preco_unitario_num / bps.ap_id.map(cesta.preco_pre_mediana)
bps = bps[bps.compat & (r <= 10) & (r >= 0.1) & (bps.vl_preco_unitario_num > 0)]

def wavg(d):
    return np.average(d.preco_unitario, weights=d.quantidade) if len(d) else np.nan

L = []
for a, c in cesta.iterrows():
    p = plano.loc[a]
    cen = not str(p.tratamento_E2).startswith("SRP nacional")
    o, oh = ok[ok.ap_id == a], ok[(ok.ap_id == a) & ok.H]
    eh = oh[oh.esfera == "E"]
    d, dh = dl[dl.ap_id == a], dl[(dl.ap_id == a) & dl.H]
    b = bps[(bps.ap_id == a) & bps.H]
    L.append(dict(
        ap_id=a, grupo=c.grupo_financiamento, centralizado=cen,
        preco_decisor=p.preco_referencia_unit, faixa_inf=p.preco_ref_faixa_inf, faixa_sup=p.preco_ref_faixa_sup,
        preco_alvo_E2=p.preco_alvo_E2_unit, fonte_decisor=p.fonte_preco,
        mediana_estadual_pre24m=pr.loc[a, "mediana_estadual_24m"], dlog_pre=pr.loc[a, "dlog_prog_preco"],
        cg_H_n=len(oh), cg_H_mediana=oh.preco_unitario.median(), cg_H_p25=oh.preco_unitario.quantile(.25), cg_H_p75=oh.preco_unitario.quantile(.75),
        cg_H_E_n=len(eh), cg_H_E_mediana=eh.preco_unitario.median(), cg_H_E_p25=eh.preco_unitario.quantile(.25), cg_H_E_p75=eh.preco_unitario.quantile(.75),
        cg_H_M_mediana=oh[oh.esfera == "M"].preco_unitario.median(), cg_H_F_mediana=oh[oh.esfera == "F"].preco_unitario.median(),
        cg_H_E_ponderada=wavg(eh),
        dlog_H_n=len(dh), dlog_H_qtd=dh.quantidade.sum(), dlog_H_preco=wavg(dh), dlog_H_datas="|".join(sorted(dh.dataResultado.unique())),
        dlog_X_n=len(d), dlog_X_preco_ultima=wavg(d[d.dataResultado == d.dataResultado.max()]) if len(d) else np.nan,
        dlog_X_data_ultima=d.dataResultado.max() if len(d) else "",
        cg_X_E_mediana=o[o.esfera == "E"].preco_unitario.median(),
        bps_H_n=len(b), bps_H_mediana=b.vl_preco_unitario_num.median(),
        bps_H_E_mediana=b[b.ds_esfera == "ESTADUAL"].vl_preco_unitario_num.median(),
        bps_H_M_mediana=b[b.ds_esfera == "MUNICIPAL"].vl_preco_unitario_num.median()))
e = pd.DataFrame(L)
# preço observado de referência (mesma lógica de categoria do decisor): centralizado -> DLOG programático em H;
# descentralizado -> mediana estadual em H (>=3 registros), senão mediana de todas as esferas em H
e["preco_obs"] = np.where(e.centralizado, e.dlog_H_preco, np.where(e.cg_H_E_n >= 3, e.cg_H_E_mediana, e.cg_H_mediana))
e["fonte_obs"] = np.where(e.centralizado, np.where(e.dlog_H_preco.notna(), "DLOG programático H", "sem DLOG programático em H"),
                          np.where(e.cg_H_E_n >= 3, "mediana estadual CG H", "mediana todas as esferas CG H"))
e["razao_obs_decisor"] = e.preco_obs / e.preco_decisor
e["na_faixa_preco"] = (e.preco_obs >= e.faixa_inf) & (e.preco_obs <= e.faixa_sup)
e["razao_bps_cg_H"] = e.bps_H_mediana / e.cg_H_mediana
e.to_csv("trabalho/e02_precos.csv", index=False)
pd.set_option("display.width", 300); pd.set_option("display.max_rows", 100)
print(e[["ap_id", "grupo", "centralizado", "preco_decisor", "faixa_inf", "faixa_sup", "preco_obs", "fonte_obs", "razao_obs_decisor", "na_faixa_preco",
         "cg_H_n", "cg_H_E_n", "dlog_X_preco_ultima", "dlog_X_data_ultima", "bps_H_n", "bps_H_mediana"]].round(3).to_string(index=False))
v = e[e.preco_obs.notna()]
print(f"\ncom preço observado: {len(v)}/50; razão obs/decisor mediana {v.razao_obs_decisor.median():.3f} (p25 {v.razao_obs_decisor.quantile(.25):.3f}; p75 {v.razao_obs_decisor.quantile(.75):.3f}); na faixa {v.na_faixa_preco.sum()}")
for k, g in v.groupby("centralizado"):
    print("centralizado" if k else "descentralizado", len(g), "razão mediana", round(g.razao_obs_decisor.median(), 3), "na faixa", g.na_faixa_preco.sum())
x = e.razao_bps_cg_H.dropna(); print(f"BPS/CG H: n={len(x)} mediana {x.median():.2f} p10 {x.quantile(.1):.2f} p90 {x.quantile(.9):.2f}")
