"""Inspeção de ref_itens.csv: itens sem referência externa, PNCP estimado, razão estimativa do órgão / mediana praticada."""
import pandas as pd
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40); pd.set_option("display.max_colwidth", 70)
r = pd.read_csv("trabalho/ref_itens.csv")
m = r.prat_n >= 5
ratio = r.loc[m, "p_org"] / r.loc[m, "prat_med"]
print("razão p_org/prat_med (itens com >=5 praticados):", ratio.describe(percentiles=[.1,.25,.5,.75,.9]).round(3).to_dict())
print("ponderada por valor: soma v_org / soma q*prat_med =", round(r.loc[m, "v_org"].sum() / (r.loc[m, "q"] * r.loc[m, "prat_med"]).sum(), 3))
print("itens com p_org < p25:", int((r.loc[m,'p_org'] < r.loc[m,'prat_p25']).sum()), "| > p75:", int((r.loc[m,'p_org'] > r.loc[m,'prat_p75']).sum()), "de", int(m.sum()))
cols = ["item", "descricao", "unidade", "q", "p_org", "v_org", "status_preco_praticado", "status_teto_cmed", "cmed_melhor_classe", "conf_n", "conf_med", "conf_motivos", "pncp_n_est", "pncp_med_est", "teto_max"]
print("\n== sem referência externa (estimativa do órgão)")
print(r.loc[r.flag_sem_referencia_externa, cols].sort_values("v_org", ascending=False).to_string())
print("\n== PNCP estimado / homologado")
print(r.loc[r.fonte_ref.str.startswith("PNCP"), cols + ["p_ref", "fonte_ref"]].sort_values("v_org", ascending=False).to_string())
print("\n== a conferir")
print(r.loc[r.flag_a_conferir, cols + ["p_ref", "p_se_conferir_compativel"]].sort_values("v_org", ascending=False).to_string())
print("\n== sem praticado e com teto:", int((r.prat_n.isna() & r.teto_max.notna()).sum()))
# números citados no diagnóstico (rastreabilidade)
print("\n== registros por item (praticado): mediana n =", r.prat_n.median(), "| mediana UFs =", r.prat_ufs.median(), "| janela:", r.prat_janela.value_counts().to_dict())
mm = r.prat_n.notna() & r.teto_min.notna()
print("teto_min / mediana praticada:", (r.teto_min / r.prat_med)[mm].describe(percentiles=[.05, .1, .25, .5, .75, .9, .95]).round(3).to_dict())
print("status_identificacao:", r.status_identificacao.value_counts().to_dict())
print("item 268: v_org =", float(r.loc[r.item == 268, "v_org"].iloc[0]), "| referência E1 =", float((r.q * r.p_ref)[r.item == 268].iloc[0]))
