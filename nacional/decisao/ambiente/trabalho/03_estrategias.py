"""Custos por estratégia (Monte Carlo), economia potencial vs. linha de base e plano por apresentação.

Entradas: trabalho/demanda_projecao.csv, trabalho/precos_referencia.csv, trabalho/elasticidade.csv, cesta, recursos_federais.
Saídas:   trabalho/custos_item_estrategia.csv, trabalho/mc_resumo.txt, saida/03_comparacao.csv, saida/plano_por_apresentacao.csv

Todos os custos são "valor estimado de contratação" = quantidade planejada x preço unitário estimado
(categoria: preço homologado/praticado projetado). NÃO é pagamento, NÃO é orçamento, NÃO é valor financiado SIA.

Estratégias (detalhe em saida/02_estrategias.md):
 E1 status quo federativo: itens centralizados pelo MS (1A + AP007) ao preço DLOG; 1B/2 compra por cada SES.
 E2 compra nacional compartilhada (SRP nacional, MS gerenciador, 27 SES participantes) para 1B/2.
 E3 blocos/consórcios regionais (5 macrorregiões) para 1B/2.
 E4 federalização: reclassificar 1B/2 para 1A (MS compra tudo).
 Itens centralizados têm o mesmo custo em todas as estratégias.
"""
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.join("data", "decision_input_nacional"))
import consulta as q

N = 4000
rng = np.random.default_rng(20250129)
con = q.conectar()
cesta = con.sql("SELECT ap_id, nome, unidade_dispensacao, grupo_financiamento, valor_aprovado_sia_12m FROM cesta").df()
dem = pd.read_csv("trabalho/demanda_projecao.csv")
pr = pd.read_csv("trabalho/precos_referencia.csv")
el = pd.read_csv("trabalho/elasticidade.csv").set_index("segmento")
df = cesta.merge(dem[["ap_id", "q_baixa", "q_central", "q_alta"]], on="ap_id").merge(pr, on="ap_id")
assert len(df) == 50

# AP007: formalmente 1B, mas compra observada centralizada no MS (DLOG ~750 mil frascos em 2024) e SIA 1B quase nulo
CENTRALIZADO_OBSERVADO = {"AP007"}
df["centralizado"] = (df.grupo_financiamento == "1A") | df.ap_id.isin(CENTRALIZADO_OBSERVADO)

# Preço base de E1 (nível 2024): centralizados -> DLOG programático; sem DLOG -> mediana 24m x efeito volume nacional
usa_est = df.n_estadual_24m >= 3
df["p_e1_med"] = np.where(usa_est, df.mediana_estadual_24m, df.mediana_24m)
df["p_e1_p25"] = np.where(usa_est, df.p25_estadual_24m, df.p25_24m)
df["p_e1_p75"] = np.where(usa_est, df.p75_estadual_24m, df.p75_24m)
df["fonte_e1"] = np.where(usa_est, "Compras.gov estadual 24m (mediana; p25-p75)", "Compras.gov todas as esferas 24m (mediana; p25-p75)")
beta_c = df.segmento.map(el.beta)
lvmax = np.log(df.lq_max_obs)


def fator(v, beta):
    """Efeito volume relativo a q_ref: exp(beta*(log v - log q_ref)), v limitado ao máximo observado; nunca > 1."""
    lv = np.minimum(np.log(v), lvmax)
    return np.minimum(1.0, np.exp(beta * (lv - np.log(df.q_ref_mediana))))


df["f_nac"] = fator(df.v_nacional, beta_c)
df["f_reg"] = fator(df.v_regiao_mediana, beta_c)
tem_dlog = df.centralizado & df.dlog_prog_preco.notna()
df["p_central"] = np.where(df.centralizado,
                           np.where(tem_dlog, df.dlog_prog_preco, df.p_e1_med * df.f_nac), df.p_e1_med)
df["fonte_preco"] = np.where(tem_dlog, "Compras.gov DLOG/MS compra programática (média ponderada da última; " + df.dlog_prog_data.astype(str) + ")",
                     np.where(df.centralizado, "HIPÓTESE: mediana Compras.gov 24m x efeito volume nacional (sem compra DLOG programática)", df.fonte_e1))
assert (df.p_central > 0).all() and df.p_central.notna().all()

# ---------------- Monte Carlo (números aleatórios comuns entre estratégias) ----------------
def tri(lo, mo, hi, u):
    lo, mo, hi = np.minimum(lo, mo), mo, np.maximum(hi, mo)
    c = np.where(hi > lo, (mo - lo) / np.where(hi > lo, hi - lo, 1), 0.5)
    return np.where(u < c, lo + np.sqrt(u * (hi - lo) * (mo - lo)), hi - np.sqrt((1 - u) * (hi - lo) * (hi - mo)))

I = len(df)
uq = rng.random((N, 1))                                   # demanda comonotônica entre itens (conservador)
Q = tri(df.q_baixa.values, df.q_central.values, df.q_alta.values, uq)
idx = rng.uniform(1.00, 1.05, (N, 1))                     # reajuste de preços 2025 (H12)
up = rng.random((N, I))
p_e1 = tri(df.p_e1_p25.values, df.p_e1_med.values, df.p_e1_p75.values, up)
# renovação dos centralizados (H11); se o preço DLOG foi marcado extremo, o teto da faixa é o preço do modelo (D08)
hi_c = np.where(df.dlog_flag_extremo, np.maximum(1.10, df.p_e1_med * df.f_nac / df.dlog_prog_preco), 1.10)
mult_c = tri(np.full(I, 0.95), np.ones(I), hi_c, up)
p_cen_nodlog = p_e1 * df.f_nac.values                      # centralizado sem DLOG
p_cen = np.where(tem_dlog.values, df.p_central.values * mult_c, p_cen_nodlog)
bseg = {s: rng.uniform(el.ic90_inf[s], el.ic90_sup[s], (N, 1)) for s in el.index}
B = np.where(df.segmento.values == "concorrencial", bseg["concorrencial"], bseg["concentrado"])
lq_ref = np.log(df.q_ref_mediana.values)
f_nac = np.minimum(1, np.exp(B * (np.minimum(np.log(df.v_nacional.values), lvmax.values) - lq_ref)))
f_reg = np.minimum(1, np.exp(B * (np.minimum(np.log(df.v_regiao_mediana.values), lvmax.values) - lq_ref)))
teto = df.teto_aplicavel.values * idx
s2 = rng.uniform(0.40, 0.70, (N, 1))   # parcela do horizonte sob ata nacional (H13)
s3 = rng.uniform(0.20, 0.60, (N, 1))   # parcela sob blocos regionais (H14)
s4 = rng.uniform(0.00, 0.30, (N, 1))   # parcela federalizada no horizonte (H15)
cen = df.centralizado.values

def custo(p):
    return Q * np.minimum(p * idx, teto)

C = {}
C["E1"] = np.where(cen, custo(p_cen), custo(p_e1))
C["E2"] = np.where(cen, custo(p_cen), custo(p_e1 * (1 - s2 + s2 * f_nac)))
C["E3"] = np.where(cen, custo(p_cen), custo(p_e1 * (1 - s3 + s3 * f_reg)))
C["E4"] = np.where(cen, custo(p_cen), custo(p_e1 * (1 - s4 + s4 * f_nac)))
# regime pleno (12 meses inteiros sob o arranjo; referência de potencial, não do horizonte)
C["E2_pleno"] = np.where(cen, custo(p_cen), custo(p_e1 * f_nac))
C["E3_pleno"] = np.where(cen, custo(p_cen), custo(p_e1 * f_reg))

pct = lambda x: np.percentile(x, [5, 50, 95])
out = []
for k, M in C.items():
    tot, dec = M.sum(1), M[:, ~cen].sum(1)
    eco = C["E1"].sum(1) - tot
    out.append(dict(estrategia=k, custo_total_p05=pct(tot)[0], custo_total_p50=pct(tot)[1], custo_total_p95=pct(tot)[2],
                    custo_centralizados_p50=np.median(M[:, cen].sum(1)),
                    custo_descentralizados_p05=pct(dec)[0], custo_descentralizados_p50=pct(dec)[1], custo_descentralizados_p95=pct(dec)[2],
                    economia_potencial_vs_E1_p05=pct(eco)[0], economia_potencial_vs_E1_p50=pct(eco)[1], economia_potencial_vs_E1_p95=pct(eco)[2],
                    economia_pct_descentralizados_p50=np.median(eco / C["E1"][:, ~cen].sum(1))))
res = pd.DataFrame(out)

# ponto de equilíbrio do risco de fracasso do certame nacional (E2): compra emergencial ao p75 da linha de base
p75 = np.where(cen, 0, df.p_e1_p75.values)
extra_falha = (Q * s2 * np.maximum(0, np.minimum(p75 * idx, teto) - np.minimum(p_e1 * f_nac * idx, teto)))[:, ~cen].sum(1)
eco2 = C["E1"].sum(1) - C["E2"].sum(1)
pf_equilibrio = np.median(eco2 / (eco2 + extra_falha))  # p tal que eco2 - p*(eco2+extra) = 0 (perde a economia e paga p75)

# ---------------- Por item ----------------
med = {k: np.median(M, axis=0) for k, M in C.items()}
lo = {k: np.percentile(M, 5, axis=0) for k, M in C.items()}
hi = {k: np.percentile(M, 95, axis=0) for k, M in C.items()}
it = df[["ap_id", "nome", "grupo_financiamento", "centralizado", "segmento", "q_central", "p_central", "f_nac", "f_reg"]].copy()
for k in C:
    it[f"custo_{k}_p50"], it[f"custo_{k}_p05"], it[f"custo_{k}_p95"] = med[k], lo[k], hi[k]
it["eco_E2_pleno_p50"] = med["E1"] - med["E2_pleno"]
it.to_csv("trabalho/custos_item_estrategia.csv", index=False)

# ---------------- Contexto orçamentário (categorias separadas, não somadas) ----------------
rf = con.sql("SELECT * FROM recursos_federais").df()
r4705 = rf[(rf["CÓDIGO AÇÃO"].astype(str) == "4705") & (rf["EXERCÍCIO"] == 2024)].iloc[0]
cen_uniao = np.median(C["E1"][:, cen].sum(1))
sia_1b = (df.loc[df.grupo_financiamento.eq("1B") & ~df.centralizado, "valor_aprovado_sia_12m"]).sum()
with open("trabalho/mc_resumo.txt", "w", encoding="utf8") as f:
    f.write(res.round(3).to_string() + "\n\n")
    f.write(f"itens centralizados: {int(cen.sum())}; descentralizados: {int((~cen).sum())}\n")
    f.write(f"pf_equilibrio_E2 (prob. de fracasso do certame nacional que anula a economia, mediana): {pf_equilibrio:.3f}\n")
    f.write(f"custo p50 centralizados (União, valor de contratação estimado): {cen_uniao:,.0f}\n")
    f.write(f"ação 4705 em 2024 (orçamento): dotação final {r4705.dotacao_final_exercicio:,.0f}; empenhado {r4705.empenhado:,.0f}; pago {r4705.realizado_pago:,.0f}; pago/empenhado {r4705.realizado_pago / r4705.empenhado:.3f}\n")
    f.write(f"razão custo centralizados p50 / empenhado 4705 2024: {cen_uniao / r4705.empenhado:.3f}\n")
    f.write(f"valor aprovado SIA 1B 12m (itens 1B descentralizados; valor financiado, outra categoria): {sia_1b:,.0f}\n")
    # concentração da economia
    e = it[~it.centralizado].sort_values("eco_E2_pleno_p50", ascending=False)
    f.write("\neconomia E2 pleno por item (p50):\n" + e[["ap_id", "nome", "eco_E2_pleno_p50", "custo_E1_p50", "f_nac", "f_reg"]].round(3).to_string() + "\n")
    # dependência do método: sem efeito volume os centralizados sem DLOG seriam
    f.write(f"\ncentralizados sem DLOG programático: {list(df.ap_id[df.centralizado & ~tem_dlog])}\n")
    # evidência do diferencial DLOG x estados (itens com ambos)
    amb = df[tem_dlog & usa_est]
    rz = amb.dlog_prog_preco / amb.mediana_estadual_24m
    f.write(f"razão preço DLOG / mediana estadual (n={len(rz)}): p25={rz.quantile(.25):.3f} mediana={rz.median():.3f} p75={rz.quantile(.75):.3f}\n")
    f.write(f"f_nac (descentralizados) mediana={df.f_nac[~df.centralizado].median():.3f}; f_reg mediana={df.f_reg[~df.centralizado].median():.3f}\n")
print(open("trabalho/mc_resumo.txt", encoding="utf8").read())

# ---------------- Saídas ----------------
qual = {
 "E1": ("linha de base", "alta", "alta", "alta (execução corrente)", "alta", "média: 27 certames independentes, dispersão de preço", "não"),
 "E2": ("compartilhada nacional", "alta (Lei 14.133 art. 86; Dec. 11.462/2023: IRP com participantes)", "média-alta (adesão voluntária das SES; pactuação CIT; competência de aquisição/contrato permanece estadual)",
        "média (capacidade do DLOG; prazo de 4-8 meses; logística segue estadual)", "alta (não muda quem paga)", "média: concentração em fornecedor único nacional; mitigável com cadastro de reserva e lotes/cotas", "sim (recomendada)"),
 "E3": ("blocos regionais", "alta (Lei 11.107/2005 consórcios; SRP com participantes)", "média (exige 5 arranjos interestaduais; só parte das regiões tem consórcio)",
        "média-baixa (montagem de 5 estruturas no horizonte)", "alta", "baixa-média: diversifica fornecedores entre regiões", "não (alternativa de contingência)"),
 "E4": ("federalização", "baixa no horizonte (alterar PRC GM/MS 2/2017 via CIT)", "baixa (transfere à União o financiamento do Grupo 2)", "média (DLOG já distribui 1A)",
        "baixa (LOA 2025 não aprovada em 29/01/2025; aumento de despesa da União)", "média-alta: transição e concentração", "não"),
}
comp = res[res.estrategia.isin(["E1", "E2", "E3", "E4"])].copy()
for i, col in enumerate(["natureza", "viab_juridica", "viab_federativa", "viab_operacional", "viab_orcamentaria", "risco_abastecimento", "recomendada"]):
    comp[col] = comp.estrategia.map(lambda k: qual[k][i])
comp["categoria_valor"] = "valor estimado de contratação (preço homologado projetado x quantidade); não é pagamento"
comp["fonte"] = "trabalho/03_estrategias.py (Monte Carlo N=4000, p05/p50/p95)"
pl = res[res.estrategia.str.endswith("pleno")].copy()
pl["natureza"] = "regime pleno de 12 meses (referência de potencial, fora do horizonte de transição)"
pl["categoria_valor"], pl["fonte"] = comp.categoria_valor.iloc[0], comp.fonte.iloc[0]
pd.concat([comp, pl]).round(2).to_csv("saida/03_comparacao.csv", index=False)

ses = {"1A": "União (MS/DLOG): aquisição centralizada; SES: programação, armazenamento, distribuição e dispensação",
       "1B": "SES (aquisição e contrato) com financiamento federal por transferência (SIA)",
       "2": "SES (financiamento e aquisição)"}
pl = df[["ap_id", "nome", "unidade_dispensacao", "grupo_financiamento", "segmento", "cmed_laboratorios", "n_fornecedores_24m"]].copy()
pl["tratamento_E2"] = np.where(df.centralizado,
    np.where(df.ap_id.isin(CENTRALIZADO_OBSERVADO), "manter compra centralizada observada no MS; verificar grupo (formalmente 1B)",
             "1A: MS mantém compra centralizada (pregão SRP; inexigibilidade/negociação se fonte única); parcelar entregas trimestrais"),
    np.where(df.segmento == "concorrencial", "SRP nacional compartilhado (MS gerenciador, SES participantes), lote nacional com cadastro de reserva; SES contrata e paga",
             "SRP nacional compartilhado com negociação de preço nacional (fornecedor concentrado/único); SES contrata e paga"))
pl["esfera_responsavel_aquisicao"] = np.where(df.ap_id.isin(CENTRALIZADO_OBSERVADO), "União (observado) — grupo a verificar",
                                              df.grupo_financiamento.map(ses))
pl["q_planejada_central"], pl["q_planejada_baixa"], pl["q_planejada_alta"] = df.q_central.round(0), df.q_baixa.round(0), df.q_alta.round(0)
pl["base_quantidade"] = "dispensação atendida SIA (jun-out/2024 anualizada x tendência); não é demanda total"
pl["preco_referencia_unit"] = df.p_central.round(4)
fv = np.where(df.centralizado, df.f_nac, 1.0)  # centralizado sem DLOG: faixa p25-p75 x efeito volume nacional
pl["preco_ref_faixa_inf"] = np.where(tem_dlog, df.p_central * 0.95, df.p_e1_p25 * fv).round(4)
pl["preco_ref_faixa_sup"] = np.where(tem_dlog, df.p_central * hi_c, df.p_e1_p75 * fv).round(4)
pl["fonte_preco"] = df.fonte_preco
pl["preco_alvo_E2_unit"] = np.where(df.centralizado, df.p_central, df.p_e1_med * df.f_nac).round(4)
pl["categoria_valor"] = "preço unitário homologado/praticado em compra pública (não é pagamento)"
pl["teto_cmed_aplicavel_unit"] = df.teto_aplicavel.round(4)
pl["teto_cmed_min_0icms_unit"] = df.teto0_min.round(4)
pl["teto_fonte"] = np.where(df.todos_convenio_87, "CMED 06/01/2025, maior teto 0% ICMS (Convênio 87/02)", "CMED 06/01/2025, max(teto 0%, mediana teto 18%) — ICMS da UF de destino não consolidado")
pl["teto_categoria_valor"] = "teto regulatório CMED (não é preço praticado)"
pl["custo_E2_p50"], pl["custo_E2_p05"], pl["custo_E2_p95"] = it.custo_E2_p50.round(0), it.custo_E2_p05.round(0), it.custo_E2_p95.round(0)
pl["custo_categoria_valor"] = "valor estimado de contratação no horizonte (não é pagamento)"
obs = []
for _, r in df.iterrows():
    o = []
    if pd.isna(r.unidade_dispensacao) or str(r.unidade_dispensacao).startswith("biossimilar"): o.append("unidade de dispensação ausente/mal extraída na cesta")
    if r.flag_mediana_acima_teto: o.append("mediana de preço acima do teto CMED: provável mistura de apresentações (ex.: 45 mg x 90 mg) — conferir vínculo")
    if r.centralizado and not (r.dlog_prog_preco == r.dlog_prog_preco): o.append("sem compra programática do MS na base: preço por hipótese")
    if isinstance(r.dlog_prog_data, str) and r.dlog_prog_data < "2023-07-01": o.append(f"última compra DLOG antiga ({r.dlog_prog_data})")
    if r.ap_id in CENTRALIZADO_OBSERVADO: o.append(f"grupo 1B na cesta, mas MS compra centralizadamente (DLOG) e o SIA 1B financia só {r.sia_unit_1b:.2f}/unidade: classificação provavelmente incorreta; verificar")
    if r.dlog_flag_extremo: o.append("preço DLOG marcado extremo (<0,1x mediana geral) e mantido por ser compra programática do MS; faixa superior = preço do modelo; confirmar ata")
    if r.cmed_laboratorios <= 1: o.append("fonte única na CMED: risco de desabastecimento e de preço")
    if r.grupo_financiamento == "1B" and not r.centralizado: o.append(f"SIA financia {r.sia_unit_1b:.2f}/unidade (valor financiado; não é preço)")
    rb = r.bps_mediana_24m / r.mediana_24m
    if rb == rb and not (0.67 <= rb <= 1.5): o.append(f"BPS diverge do Compras.gov (mediana BPS/CG = {rb:.2f}): referência de preço incerta; conferir unidade/apresentação")
    if r.n_estadual_24m < 3: o.append("menos de 3 compras estaduais em 24m: referência usa todas as esferas")
    obs.append("; ".join(o))
pl["observacoes"] = obs
pl.to_csv("saida/plano_por_apresentacao.csv", index=False)
print("ok", len(pl))
