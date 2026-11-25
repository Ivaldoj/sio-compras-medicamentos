"""E1: quantidade projetada pelo decisor x dispensação SIA observada (processamento fev/2025-jan/2026).
Entradas: decisao_congelada (demanda_projecao.csv, cesta), dados_reservados/sia_dispensacao_pos_*.parquet,
          evidencias_primarias/sia_tabnet (conferência da base reservada e do pacote).
Saída: trabalho/e01_demanda.csv"""
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "trabalho")
import tabnet

PK = "decisao_congelada/ambiente/data/decision_input_nacional/problema/"
cesta = pd.read_parquet(PK + "cesta.parquet")
dem = pd.read_csv("decisao_congelada/ambiente/trabalho/demanda_projecao.csv")
pos = pd.read_parquet("dados_reservados/sia_dispensacao_pos_total.parquet").set_index("ap_id")
posuf = pd.read_parquet("dados_reservados/sia_dispensacao_pos_uf.parquet")

# conferências contra a evidência primária
raw_pos = tabnet.por_ap(tabnet.ler("evidencias_primarias/sia_tabnet/pos_qtd_proc_uf.html"), cesta, "Total")
raw_pre = tabnet.por_ap(tabnet.ler("evidencias_primarias/sia_tabnet/pre_qtd_proc_uf.html"), cesta, "Total")
raw_pre0 = tabnet.por_ap(tabnet.ler("evidencias_primarias/sia_tabnet/pre0_qtd_proc.html"), cesta, "Qtd.aprovada")
raw_val = tabnet.por_ap(tabnet.ler("evidencias_primarias/sia_tabnet/pos_valor_proc.html"), cesta, "Valor aprovado")
c = cesta.set_index("ap_id")
print("pos total reservado = TabNet bruto:", np.allclose(pos.dispensacao_fev2025_jan2026, raw_pos.reindex(pos.index).fillna(0)))
print("pos UF somado = pos total:", np.allclose(posuf.groupby("ap_id").dispensacao_fev2025_jan2026.sum().reindex(pos.index), pos.dispensacao_fev2025_jan2026))
print("valor SIA pos reservado = TabNet bruto:", np.allclose(pos.valor_aprovado_sia_pos, raw_val.reindex(pos.index).fillna(0)))
print("cesta d12 = TabNet pré:", np.allclose(c.dispensacao_12m_pre_corte, raw_pre.reindex(c.index).fillna(0)))
print("cesta d12 ano anterior = TabNet pré0:", np.allclose(c.dispensacao_12m_ano_anterior, raw_pre0.reindex(c.index).fillna(0)))

d = dem.merge(pos, left_on="ap_id", right_index=True)
d["obs"] = d.dispensacao_fev2025_jan2026
d["erro_rel_central"] = d.q_central / d.obs - 1
d["erro_rel_ingenuo_d12"] = d.d12 / d.obs - 1          # referência ingênua: repetir os 12 meses pré-corte
d["na_faixa"] = (d.obs >= d.q_baixa) & (d.obs <= d.q_alta)
d["posicao"] = np.where(d.obs < d.q_baixa, "abaixo da faixa", np.where(d.obs > d.q_alta, "acima da faixa", "na faixa"))
d["descentralizado"] = (d.grupo_financiamento != "1A") & (d.ap_id != "AP007")
d["crescimento_obs"] = d.obs / d.d12 - 1
d[["ap_id", "nome", "grupo_financiamento", "descentralizado", "d12", "q_baixa", "q_central", "q_alta", "obs", "erro_rel_central",
   "erro_rel_ingenuo_d12", "na_faixa", "posicao", "g_bruto", "crescimento_obs", "valor_aprovado_sia_pos"]].to_csv("trabalho/e01_demanda.csv", index=False)

a = d.erro_rel_central.abs(); b = d.erro_rel_ingenuo_d12.abs()
print(f"itens: {len(d)} | na faixa: {d.na_faixa.sum()} | abaixo: {(d.posicao=='abaixo da faixa').sum()} | acima: {(d.posicao=='acima da faixa').sum()}")
print(f"erro relativo central: mediana {d.erro_rel_central.median():+.3f}; MAPE mediano {a.median():.3f}; média |e| {a.mean():.3f}; p90 |e| {a.quantile(.9):.3f}")
print(f"ingênuo (d12): mediana {d.erro_rel_ingenuo_d12.median():+.3f}; MAPE mediano {b.median():.3f}; média |e| {b.mean():.3f}")
print(f"decisor melhor que ingênuo em {(a < b).sum()} de {len(d)} itens")
for k, g in d.groupby("descentralizado"):
    print("descentralizado" if k else "centralizado", "n=", len(g), "na faixa", g.na_faixa.sum(), "mediana erro", round(g.erro_rel_central.median(), 3))
pd.set_option("display.width", 250)
print(d.sort_values("erro_rel_central")[["ap_id", "grupo_financiamento", "d12", "q_baixa", "q_central", "q_alta", "obs", "erro_rel_central", "posicao"]].round(3).to_string(index=False))
