"""E3: custo projetado pelo decisor x valor de referência observado (quantidade SIA observada x preço observado; homologado/praticado,
NUNCA pagamento). E4: execução federal agregada da ação 4705 em 2025 (contexto; categoria diferente, não somada a nada).
Entradas: trabalho/e01_demanda.csv, trabalho/e02_precos.csv, decisao_congelada (plano, custos_item_estrategia), dados_reservados/orcamento_*.
Saídas: trabalho/e03_custo.csv, trabalho/e04_orcamento.csv"""
import numpy as np
import pandas as pd

q = pd.read_csv("trabalho/e01_demanda.csv").set_index("ap_id")
p = pd.read_csv("trabalho/e02_precos.csv").set_index("ap_id")
it = pd.read_csv("decisao_congelada/ambiente/trabalho/custos_item_estrategia.csv").set_index("ap_id")
d = p[["grupo", "centralizado", "preco_decisor", "preco_obs", "fonte_obs", "dlog_X_preco_ultima", "dlog_X_data_ultima"]].join(
    q[["nome", "q_central", "obs"]]).join(it[["custo_E1_p50", "custo_E2_p50", "custo_E2_p05", "custo_E2_p95", "custo_E1_p05", "custo_E1_p95"]])
# preço observado com cascata explícita (nível registrado em 'nivel_preco')
d["preco_ref_obs"] = d.preco_obs
d["nivel_preco"] = np.where(d.preco_obs.notna(), "observado no horizonte", "")
m = d.preco_ref_obs.isna() & d.dlog_X_preco_ultima.notna()
d.loc[m, "preco_ref_obs"] = d.dlog_X_preco_ultima[m]; d.loc[m, "nivel_preco"] = "DLOG contratado após o horizonte (proxy)"
m = d.preco_ref_obs.isna()
d.loc[m, "preco_ref_obs"] = d.preco_decisor[m]; d.loc[m, "nivel_preco"] = "não observado: preço do decisor mantido"
d["valor_ref_obs"] = d.obs * d.preco_ref_obs                   # quantidade observada x preço observado
d["valor_qobs_pdec"] = d.obs * d.preco_decisor                  # isola o efeito quantidade
d["desvio_E2_vs_ref"] = d.custo_E2_p50 / d.valor_ref_obs - 1
d["E2_faixa_cobre_ref"] = (d.valor_ref_obs >= d.custo_E2_p05) & (d.valor_ref_obs <= d.custo_E2_p95)
d["E1_faixa_cobre_ref"] = (d.valor_ref_obs >= d.custo_E1_p05) & (d.valor_ref_obs <= d.custo_E1_p95)
d.to_csv("trabalho/e03_custo.csv")

def bloco(x, nome):
    return dict(bloco=nome, n=len(x), custo_E1_proj_p50=x.custo_E1_p50.sum(), custo_E2_proj_p50=x.custo_E2_p50.sum(),
                valor_qobs_x_pdecisor=x.valor_qobs_pdec.sum(), valor_ref_observado=x.valor_ref_obs.sum(),
                parcela_valor_com_preco_observado_H=x.loc[x.nivel_preco == "observado no horizonte", "valor_ref_obs"].sum() / x.valor_ref_obs.sum())
T = pd.DataFrame([bloco(d, "cesta (50)"), bloco(d[d.centralizado], "centralizados (39)"), bloco(d[~d.centralizado], "descentralizados (11)"),
                  bloco(d[d.nivel_preco == "observado no horizonte"], "só itens com preço observado no horizonte")])
T["E2_proj_sobre_ref"] = T.custo_E2_proj_p50 / T.valor_ref_observado - 1
T["E1_proj_sobre_ref"] = T.custo_E1_proj_p50 / T.valor_ref_observado - 1
T.to_csv("trabalho/e03_custo_totais.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 100)
print(T.round(3).to_string(index=False))
print(d.nivel_preco.value_counts().to_string())
print("faixa p05-p95 de E2 cobre o valor de referência observado em", int(d.E2_faixa_cobre_ref.sum()), "de 50 itens; E1:", int(d.E1_faixa_cobre_ref.sum()))
print(d.sort_values("valor_ref_obs", ascending=False)[["grupo", "q_central", "obs", "preco_decisor", "preco_ref_obs", "nivel_preco", "custo_E2_p50", "valor_ref_obs", "desvio_E2_vs_ref"]].head(20).round(2).to_string())

# E4: contexto orçamentário (empenhado/realizado da ação 4705) — agregado, sem item
R = []
for y in (2025, 2026):
    o = pd.read_csv(f"dados_reservados/orcamento_acoes_af_{y}.csv", dtype=str)
    cols = [c for c in o.columns if c.startswith("ORÇAMENTO")]
    for c in cols:
        o[c] = pd.to_numeric(o[c].str.replace(".", "", regex=False).str.replace(",", ".", regex=False), errors="coerce")
    g = o.groupby("CÓDIGO AÇÃO")[cols].sum().reset_index(); g.insert(0, "exercicio", y); R.append(g)
pre = pd.read_csv("decisao_congelada/ambiente/data/decision_input_nacional/problema/recursos_federais.csv")
pre = pre.rename(columns={"EXERCÍCIO": "exercicio", "orcamento_inicial": "ORÇAMENTO INICIAL (R$)", "dotacao_final_exercicio": "ORÇAMENTO ATUALIZADO (R$)",
                          "empenhado": "ORÇAMENTO EMPENHADO (R$)", "realizado_pago": "ORÇAMENTO REALIZADO (R$)"})
pre["CÓDIGO AÇÃO"] = pre["CÓDIGO AÇÃO"].astype(str)
O = pd.concat([pre[["exercicio", "CÓDIGO AÇÃO"] + cols], *R]).sort_values(["CÓDIGO AÇÃO", "exercicio"])
O["observacao"] = np.where(O.exercicio == 2026, "exercício em curso no arquivo (parcial)", "")
O.to_csv("trabalho/e04_orcamento.csv", index=False)
print(O.round(0).to_string(index=False))
a = O[(O["CÓDIGO AÇÃO"] == "4705")].set_index("exercicio")
cen = it[it.centralizado].custo_E1_p50.sum()
print(f"4705 empenhado 2025/2024 = {a.loc[2025,'ORÇAMENTO EMPENHADO (R$)']/a.loc[2024,'ORÇAMENTO EMPENHADO (R$)']-1:+.3f}; realizado/empenhado 2025 = {a.loc[2025,'ORÇAMENTO REALIZADO (R$)']/a.loc[2025,'ORÇAMENTO EMPENHADO (R$)']:.3f}")
print(f"custo projetado centralizados (p50, valor de contratação) / empenhado 4705 2025 = {cen / a.loc[2025,'ORÇAMENTO EMPENHADO (R$)']:.3f} (só ordem de grandeza)")
