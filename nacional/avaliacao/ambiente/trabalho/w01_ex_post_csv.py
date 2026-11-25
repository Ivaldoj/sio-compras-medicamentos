"""Monta saida/04_comparacao_ex_post.csv (E1, E2 e E3 por apresentação + linhas de total) a partir de e01, e02 e e03."""
import pandas as pd

q = pd.read_csv("trabalho/e01_demanda.csv").set_index("ap_id")
p = pd.read_csv("trabalho/e02_precos.csv").set_index("ap_id")
c = pd.read_csv("trabalho/e03_custo.csv").set_index("ap_id")
o = q[["nome", "grupo_financiamento", "descentralizado", "d12", "q_baixa", "q_central", "q_alta", "obs", "erro_rel_central", "na_faixa", "posicao"]].rename(
    columns={"obs": "q_obs_sia_fev25_jan26", "erro_rel_central": "E1_erro_rel_q_central", "na_faixa": "E1_obs_na_faixa"})
o = o.join(p[["preco_decisor", "faixa_inf", "faixa_sup", "preco_obs", "fonte_obs", "razao_obs_decisor", "na_faixa_preco",
              "cg_H_E_mediana", "cg_H_M_mediana", "cg_H_F_mediana", "dlog_H_preco", "dlog_X_preco_ultima", "dlog_X_data_ultima",
              "bps_H_E_mediana", "bps_H_M_mediana"]].rename(columns={"razao_obs_decisor": "E2_razao_preco_obs_decisor", "na_faixa_preco": "E2_preco_na_faixa"}))
o = o.join(c[["preco_ref_obs", "nivel_preco", "custo_E1_p50", "custo_E2_p50", "custo_E2_p05", "custo_E2_p95", "valor_ref_obs", "desvio_E2_vs_ref", "E2_faixa_cobre_ref"]].rename(
    columns={"valor_ref_obs": "E3_valor_ref_observado_qobs_x_pobs", "desvio_E2_vs_ref": "E3_custo_E2_proj_sobre_ref_obs"}))
o["categoria_valor"] = "preços: homologado/praticado (Compras.gov; BPS só conferência); custos: valor de contratação projetado ou de referência observado; nada é pagamento"
tot = pd.read_csv("trabalho/e03_custo_totais.csv")
linhas = []
for _, t in tot.iterrows():
    linhas.append({"nome": "TOTAL " + t.bloco, "custo_E1_p50": t.custo_E1_proj_p50, "custo_E2_p50": t.custo_E2_proj_p50,
                   "E3_valor_ref_observado_qobs_x_pobs": t.valor_ref_observado, "E3_custo_E2_proj_sobre_ref_obs": t.E2_proj_sobre_ref,
                   "nivel_preco": f"parcela do valor com preço observado no horizonte = {t.parcela_valor_com_preco_observado_H:.3f}"})
o = pd.concat([o.reset_index(), pd.DataFrame(linhas)], ignore_index=True)
o.to_csv("saida/04_comparacao_ex_post.csv", index=False)
print(len(o), "linhas")
