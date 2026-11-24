"""Etapa 5 / 05 — economia em três níveis (potencial × contratada × realizada) e sensibilidade da recomendação.

Lê os resultados dos scripts 01–04 (resultados/) e os arquivos congelados. Não altera nada fora de resultados/.

Saídas em resultados/:
  economia_tres_niveis.csv     cada linha traz nível, quem, valor, referência, observabilidade e ressalva
  sensibilidade_recomendacao.csv  cenários sobre os custos E1/E2/E4 e se a ordenação muda
  risco_deserto.csv            itens em que o mercado real ficou acima do limite alto do agente
  e2_teste_expost.csv          modelo de desconto sobre a CMED (E2) × preços por item realmente homologados
  economia_numeros.json
Regra: os três níveis NUNCA são somados entre si.
"""
import json
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e5_comum import RES, SAIDA, TRAB

N = {}
it = pd.read_csv(os.path.join(RES, "expost_itens.csv"))
X = json.load(open(os.path.join(RES, "expost_numeros.json"), encoding="utf-8"))
I = json.load(open(os.path.join(RES, "insulinas_numeros.json"), encoding="utf-8"))
ref = pd.read_csv(os.path.join(TRAB, "ref_itens.csv"))  # arquivo de trabalho congelado do agente (colunas e2_*), conferido em V10
custos = pd.read_csv(os.path.join(TRAB, "custos_estrategias.csv"))
c12 = pd.read_csv(os.path.join(RES, "reproducao_custos_v1_v2.csv"))
exe = pd.read_csv(os.path.join(RES, "expost_execucao_contratos.csv"))
linha = lambda p: custos[custos.estrategia.str.startswith(p)].iloc[0]
E1c, E1b, E1a = (float(linha("E1")[k]) for k in ("central", "baixo", "alto"))
E2c, E2b, E2a = (float(linha("E2")[k]) for k in ("central", "baixo", "alto"))
R0, R1 = float(linha("R0").central), float(linha("R1").central)
HOM = X["homologado_total"]
d = it.merge(ref[["item", "e2_pref", "e2_min", "e2_med", "flag_teto_suspeito", "prat_n"]], on="item", how="left")
cob = d.e2_pref.notna() & ~d.flag_teto_suspeito.fillna(False).astype(bool)
caneta = d.item.isin([196, 199])
tot = lambda s, m=None: float((d.q * s)[m].sum()) if m is not None else float((d.q * s).sum())

# ================================================================== 1. três níveis
E = []
def eco(nivel, quem, indicador, valor, referencia, observ, ressalva):
    E.append({"nivel": nivel, "de_quem": quem, "indicador": indicador, "valor": valor, "referencia": referencia, "observabilidade": observ, "ressalva": ressalva})

# --- F1 potencial (ex ante, do agente)
eco("1. POTENCIAL (ex ante)", "estratégia do agente (E1)", "E2 − E1, central", E2c - E1c, "E2: modelo de desconto sobre a CMED (PE 12/2024), na quantidade do ETP",
    "projeção; nunca observada", "contrafactual modelado; quantidade do ETP (não a executada)")
eco("1. POTENCIAL (ex ante)", "estratégia do agente (E1)", "E2 − E1, faixa plausível (baixo×baixo a alto×alto)", f"{E2b - E1b:.0f} a {E2a - E1a:.0f}", "idem", "projeção", "")
eco("1. POTENCIAL (ex ante)", "estratégia do agente (E1)", "E2 − E1, extremos cruzados", f"{E2b - E1a:.0f} a {E2a - E1b:.0f}", "idem", "projeção", "inclui cenário em que o E1 perde")
eco("1. POTENCIAL (ex ante)", "estratégia do agente (E1)", "R1 − E1, central", R1 - E1c, "R1: estimativa do órgão limitada ao teto CMED", "projeção",
    "mede orçamento liberado, não ganho de mercado")
eco("1. POTENCIAL (ex ante)", "estratégia do agente (E1)", "R0 − R1 (correção de conformidade; NÃO é economia)", R0 - R1, "estimativa do órgão acima do teto CMED",
    "calculado ex ante", "o agente separou corretamente este valor")

# --- potencial reavaliado com informação ex post (ainda NÃO é contratado nem realizado)
eco("1b. POTENCIAL REAVALIADO (ex post, estimativa)", "estratégia do agente (E1)", "E1 a preços reais do PE 04/2025 limitados ao teto (contrafactual A)", X["contrafactual_A"],
    "preço homologado por item, limitado ao teto CMED do agente; quantidade do ETP", "estimativa; a estratégia não foi executada",
    "os preços reais vêm de um certame com teto de aceitação = estimativa do órgão; viés para cima")
eco("1b. POTENCIAL REAVALIADO (ex post, estimativa)", "estratégia do agente (E1)", "E1 a min(homologado, limite alto do agente) (contrafactual B)", X["contrafactual_B"],
    "idem, com o limite alto do agente como teto de aceitação", "estimativa", "supõe que os itens acima do limite seriam adquiridos no limite (senão: deserto)")
eco("1b. POTENCIAL REAVALIADO (ex post, estimativa)", "estratégia do agente (E1)", "E1 à mediana nacional do horizonte (contrafactual C)", X["contrafactual_C"],
    "mediana BPS + Compras.gov.br de 30/01/2025 a 29/01/2026", "estimativa", f"{X['itens_com_mediana_nacional']} itens com ≥5 registros; demais = A")
eco("1b. POTENCIAL REAVALIADO (ex post, estimativa)", "estratégia do agente (E1)", "homologado real − contrafactual A", HOM - X["contrafactual_A"],
    "decisão real contratada × E1 com a regra de teto", "estimativa", f"R$ {X['excesso_hom_sobre_teto']:,.0f} disso é excesso sobre o teto CMED ({X['itens_hom_acima_teto_agente']} itens)")

# --- F2 contratada (ex post, decisão real)
eco("2. CONTRATADA (ex post)", "decisão real (PE 04/2025)", "R0 − homologado", R0 - HOM, "estimativa do órgão (R$ 4.952.438)", "observada (PNCP)",
    "referência inflada ~2×; não é economia de mercado nem realizada")
eco("2. CONTRATADA (ex post)", "decisão real (PE 04/2025)", "R1 − homologado", R1 - HOM, "estimativa do órgão limitada ao teto", "observada/calculada",
    "o homologado mantém R$ 1,26 mi acima do teto; por isso a diferença é pequena")
eco("2. CONTRATADA (ex post)", "decisão real (PE 04/2025)", "R0 − homologado, só os 332 itens fora das canetas", (R0 - 1334952.0) - X["homologado_sem_canetas"],
    "estimativa do órgão dos 332 itens", "observada", "as canetas foram homologadas exatamente na estimativa: contribuição zero")
eco("2. CONTRATADA (ex post)", "decisão real (PE 04/2025)", "homologado − E1 central do agente (332 itens fora das canetas)", X["homologado_sem_canetas"] - X["E1_central_sem_canetas"],
    "referência saneada do agente", "observada × projeção", "positivo = o real ficou acima da referência do agente")
eco("2. CONTRATADA (ex post)", "estratégia do agente (E1)", "contratada", np.nan, "—", "NÃO OBSERVÁVEL", "a estratégia do agente não foi licitada")

# --- F3 realizada
e4 = exe[exe.pregao == "PE 04/2025"].copy()
hom_c = d.groupby("cnpj_fornecedor").apply(lambda g: pd.Series({"hom": g.v_hom.sum(), "r0": (g.q * g.p_org).sum(), "ref": g.v_ref.sum(),
                                                               "hom_teto": (g.q * np.where(g.teto.notna(), np.minimum(g.p_hom, g.teto), g.p_hom)).sum()})).reset_index()
e4 = e4.merge(hom_c, left_on="forn", right_on="cnpj_fornecedor", how="left")
assert np.allclose(e4.valor, e4.hom, atol=1)  # valor do contrato = soma homologada do fornecedor
e4["eco_real_estimada_vs_r0"] = e4.pago_total * (e4.r0 / e4.hom - 1)
e4["gasto_no_agente_estimado"] = e4.pago_total * (e4.ref / e4.hom)
e4.to_csv(os.path.join(RES, "economia_execucao_por_contrato.csv"), index=False, encoding="utf-8")
PAGO, EMP = float(e4.pago_total.sum()), float(e4.empenhado_total.sum())
eco("3. REALIZADA (ex post)", "decisão real (PE 04/2025)", "valor pago nos 7 contratos (até nov/2026)", PAGO, "contratado: R$ 3.105.249,60", "observada (TCE-PB/SAGRES)",
    f"{100 * PAGO / HOM:.1f}% do contratado, em ~20 meses (contratos prorrogados até 03/2027)")
eco("3. REALIZADA (ex post)", "decisão real (PE 04/2025)", "economia realizada por item", np.nan, "—", "NÃO OBSERVÁVEL",
    "não existem quantidades entregues nem preços pagos por item (empenhos com histórico genérico; notas fiscais não públicas)")
eco("3. REALIZADA (ex post)", "decisão real (PE 04/2025)", "ESTIMATIVA: economia realizada frente a R0, mix proporcional por contrato", float(e4.eco_real_estimada_vs_r0.sum()),
    "estimativa do órgão", "estimativa (hipótese: cada contrato executou os itens na proporção do valor contratado)",
    "sob a mesma hipótese, o contrato 54 não gera economia nas canetas; referência inflada")
eco("3. REALIZADA (ex post)", "decisão real (PE 04/2025)", "LIMITE SUPERIOR: pago acima do teto CMED nas canetas", I["canetas_excesso_pago_limite_superior"],
    "teto CMED por caneta (R$ 20,15)", "limite superior (se TODO o pago no contrato 54 fosse caneta NPH)",
    f"o contrato 54 pagou R$ {I['contrato54_pago_total']:,.0f} no total de 128 itens; o excesso realizado nas canetas está entre 0 e este valor")
eco("3. REALIZADA (ex post)", "estratégia do agente (E1)", "realizada", np.nan, "—", "NÃO OBSERVÁVEL", "a estratégia não foi executada; não há economia realizada atribuível ao agente")
pd.DataFrame(E).to_csv(os.path.join(RES, "economia_tres_niveis.csv"), index=False, encoding="utf-8")

# ================================================================== 2. teste ex post do modelo E2
hom_cob, e2_cob, e1_cob = tot(d.p_hom, cob & ~caneta), tot(d.e2_pref, cob & ~caneta), tot(d.p_ref, cob & ~caneta)
e2min_cob = tot(d.e2_min, cob & ~caneta)
t2 = [{"indicador": "itens cobertos pelo modelo de desconto (E2), sem as canetas 196/199", "valor": int((cob & ~caneta).sum())},
      {"indicador": "E1 central do agente nesses itens (quantidade do ETP)", "valor": e1_cob},
      {"indicador": "homologado real por item nesses itens (PE 04/2025)", "valor": hom_cob},
      {"indicador": "E2 central modelado (CMED − desconto de 2024, categoria mais barata)", "valor": e2_cob},
      {"indicador": "E2 baixo modelado (registro de menor preço)", "valor": e2min_cob},
      {"indicador": "itens em que o homologado real < E2 central", "valor": int(((d.p_hom < d.e2_pref) & cob & ~caneta).sum())},
      {"indicador": "itens em que o homologado real < E2 baixo", "valor": int(((d.p_hom < d.e2_min) & cob & ~caneta).sum())},
      {"indicador": "razão mediana E2 central / homologado real", "valor": float((d.e2_pref / d.p_hom)[cob & ~caneta].median())},
      {"indicador": "razão mediana E2 baixo / homologado real", "valor": float((d.e2_min / d.p_hom)[cob & ~caneta].median())},
      {"indicador": "gasto real 2025–2026 pelo PE 12/2024 (desconto sobre CMED), empenhado", "valor": X["gasto_2025_pe12_2024_desconto_cmed"] + X["gasto_2026_pe12_2024_desconto_cmed"]},
      {"indicador": "gasto real 2025–2026 pelo PE 04/2025 (por item), empenhado", "valor": X["gasto_2025_pe04_2025"] + X["gasto_2026_pe04_2025"]}]
m_emp = e1_cob / e2_cob
g12 = X["gasto_2025_pe12_2024_desconto_cmed"] + X["gasto_2026_pe12_2024_desconto_cmed"]
t2 += [{"indicador": "EXTRAPOLAÇÃO (modelo do agente): parcela evitável do gasto real pelo PE 12/2024 se a razão E1/E2 central valesse", "valor": g12 * (1 - m_emp)},
       {"indicador": "EXTRAPOLAÇÃO (preços reais): idem, com a razão homologado real / E2 central", "valor": g12 * (1 - hom_cob / e2_cob)},
       {"indicador": "EXTRAPOLAÇÃO (prudente): idem, com a razão homologado real / E2 baixo", "valor": g12 * (1 - min(hom_cob / e2min_cob, 1))}]
pd.DataFrame(t2).to_csv(os.path.join(RES, "e2_teste_expost.csv"), index=False, encoding="utf-8")

# ================================================================== 3. risco de deserto do E1
ac = d[d.hom_acima_faixa].copy()
ac["mercado_nacional_ate_o_limite_alto"] = ac.nac_med <= ac.p_hi
ac["mesmo_comprador_2026_ate_o_limite_alto"] = ac.p_hom_2026 <= ac.p_hi
ac[["item", "descricao", "q", "p_org", "p_ref", "p_hi", "p_hom", "n_proponentes", "hom_igual_estimativa", "nac_n", "nac_med", "nac_frac_ate_alto",
    "p_hom_2026", "mercado_nacional_ate_o_limite_alto", "mesmo_comprador_2026_ate_o_limite_alto", "v_hom", "grupo_fonte"]].to_csv(
    os.path.join(RES, "risco_deserto.csv"), index=False, encoding="utf-8")
sc = ac[~ac.item.isin([196, 199])]
N.update({"deserto_itens_acima_do_alto": int(len(ac)), "deserto_itens_acima_do_alto_sem_canetas": int(len(sc)),
          "deserto_valor_hom_sem_canetas": float(sc.v_hom.sum()), "deserto_valor_no_alto_sem_canetas": float((sc.q * sc.p_hi).sum()),
          "deserto_pct_valor_E1_alto": float(100 * (ac.q * ac.p_hi).sum() / E1a),
          "deserto_itens_com_1_proponente": int((ac.n_proponentes == 1).sum()), "deserto_itens_com_ate_3_proponentes": int((ac.n_proponentes <= 3).sum()),
          "deserto_itens_hom_igual_estimativa": int(ac.hom_igual_estimativa.sum()),
          "deserto_itens_com_mediana_nacional": int(ac.nac_med.notna().sum()),
          "deserto_itens_mercado_nacional_ate_o_alto": int(ac.mercado_nacional_ate_o_limite_alto.sum()),
          "deserto_itens_com_preco_2026": int(ac.p_hom_2026.notna().sum()),
          "deserto_itens_2026_ate_o_alto": int(ac.mesmo_comprador_2026_ate_o_limite_alto.sum()),
          "itens_4mais_proponentes": int((d.n_proponentes >= 4).sum()), "itens_4mais_proponentes_acima_do_alto": int(((d.n_proponentes >= 4) & d.hom_acima_faixa).sum())})

# ================================================================== 4. sensibilidade da recomendação
S = []
def cen(i, nome, e1, e2, e4, obs=""):
    menor = min(("E1", e1), ("E2", e2), ("E4", e4), key=lambda t: (round(t[1], 2), t[0]))[0]
    S.append({"id": i, "cenario": nome, "E1": e1, "E2": e2, "E4": e4, "E2_menos_E1": e2 - e1, "E1_e_o_menor_custo": bool(e1 <= e2 + 1e-6 and e1 <= e4 + 1e-6),
              "altera_a_recomendacao": bool(not (e1 <= e2 + 1e-6 and e1 <= e4 + 1e-6)), "observacao": obs})

cen("S0", "base do agente (pacote v1, central)", E1c, E2c, E1c, "E4 = E1 por hipótese do agente; o desempate é a demanda (S7)")
v2 = lambda p, k: float(c12[c12.estrategia.str.startswith(p)].iloc[0][k + "_v2"])
cen("S1", "pacote v2 (com a errata E-01 a E-05), central", v2("E1", "central"), v2("E2", "central"), v2("E4", "central"), "scripts do agente reexecutados sobre o v2")
t20 = I["teto_cmed_jan2025_por_caneta"]
e1_s2 = E1c + float(d.loc[d.item == 196, "q"].iloc[0]) * (t20["196"]["teto_20pct_max"] - t20["196"]["teto_0pct_max"]) \
            + float(d.loc[d.item == 199, "q"].iloc[0]) * (t20["199"]["teto_20pct_max"] - t20["199"]["teto_0pct_max"])
cen("S2", "canetas com teto na coluna de 20% da CMED bruta (Convênio 87/02 não aplicável)", e1_s2, E2c, e1_s2, "E2 mantido (conservador contra o E1)")
m_ins = d.item.between(196, 199)
e1_s3 = E1c - float(d.loc[m_ins, "v_ref"].sum())
e2_s3 = E2c - tot(np.where(cob, d.e2_pref, d.p_ref), m_ins)
cen("S3", "insulinas humanas 196–199 fora da compra municipal (fornecimento centralizado pelo MS)", e1_s3, e2_s3, e1_s3, "NT 169/2022 e NT 164/2023 do MS")
cen("S4a", "preços do E1 = homologados reais, sem nenhum limite (inclui canetas a R$ 193,02)", HOM, E2c, HOM, "não é o E1: o E1 veda aceitar acima do teto")
cen("S4b", "preços do E1 = homologados reais limitados ao teto CMED (contrafactual A)", X["contrafactual_A"], E2c, X["contrafactual_A"])
cen("S5", "preços do E1 = mediana nacional do horizonte (contrafactual C)", X["contrafactual_C"], E2c, X["contrafactual_C"])
sem = d.flag_sem_referencia_externa.astype(bool)
e1_s6 = E1c - float(d.loc[sem, "v_ref"].sum()) + tot(np.where(d.teto.notna(), np.minimum(d.p_org, d.teto), d.p_org), sem)
cen("S6", "63 itens sem referência externa precificados pela estimativa do órgão limitada ao teto", e1_s6, E2c - float(d.loc[sem & ~cob, "v_ref"].sum())
    + tot(np.where(d.teto.notna(), np.minimum(d.p_org, d.teto), d.p_org), sem & ~cob), e1_s6)
d_obs = X["pe04_pct_empenhado"] / 100
cen("S7a", f"demanda = fração empenhada observada no PE 04/2025 ({100 * d_obs:.1f}%): SRP paga d×C, contrato fixo compromete C", d_obs * E1c, d_obs * E2c, E1c,
    "E4 compromete o total contratado")
cen("S7b", "demanda = 50% do ETP", 0.5 * E1c, 0.5 * E2c, E1c)
cen("S8", "E1 no limite alto × E2 no limite baixo (extremo cruzado do próprio agente)", E1a, E2b, E1a, "o agente declarou este cenário")
cen("S9", "pior caso combinado: E1 = homologado real sem limite × E2 no limite baixo", HOM, E2b, HOM, "exige aceitar canetas acima do teto, o que o E1 proíbe")
cen("S10", "E1 = contrafactual A × E2 no limite baixo", X["contrafactual_A"], E2b, X["contrafactual_A"], "E1 com a regra de teto, E2 no cenário mais favorável")
cen("S11", "E1 central + 5% de correção monetária × E2 central", 1.05 * E1c, E2c, 1.05 * E1c)
cen("S12", "E2 a preços por item realmente homologados não é possível; teste: E2 central só nos itens cobertos × homologado real desses itens",
    hom_cob, e2_cob, hom_cob, "subconjunto: itens cobertos pelo desconto, sem as canetas")
pA = np.where(d.teto.notna(), np.minimum(d.p_hom, d.teto), d.p_hom)
e1_s13 = tot(pd.Series(pA, index=d.index), ~m_ins)
cen("S13", "combinado (S8 do protocolo): insulinas humanas 196–199 fora + preços reais homologados limitados ao teto", e1_s13, e2_s3, e1_s13,
    "com as canetas fora da compra, a coluna de ICMS (S2) deixa de ter efeito")
cen("S14", "idem S13 × E2 no limite baixo", e1_s13, E2b - tot(np.where(cob, d.e2_min, d.p_lo), m_ins), e1_s13)
pd.DataFrame(S).to_csv(os.path.join(RES, "sensibilidade_recomendacao.csv"), index=False, encoding="utf-8")

N.update({"potencial_E2_menos_E1": E2c - E1c, "potencial_R1_menos_E1": R1 - E1c, "contratada_R0_menos_hom": R0 - HOM, "contratada_R1_menos_hom": R1 - HOM,
          "realizada_pago_pe04": PAGO, "realizada_empenhado_pe04": EMP, "realizada_pct_pago": 100 * PAGO / HOM,
          "realizada_estimativa_economia_vs_R0_mix_proporcional": float(e4.eco_real_estimada_vs_r0.sum()),
          "hom_menos_contrafactual_A": HOM - X["contrafactual_A"],
          "e2_teste_itens": int((cob & ~caneta).sum()), "e2_teste_E1": e1_cob, "e2_teste_hom": hom_cob, "e2_teste_E2_central": e2_cob, "e2_teste_E2_baixo": e2min_cob,
          "e2_teste_itens_hom_menor_que_E2_central": int(((d.p_hom < d.e2_pref) & cob & ~caneta).sum()),
          "e2_teste_itens_hom_menor_que_E2_baixo": int(((d.p_hom < d.e2_min) & cob & ~caneta).sum()),
          "gasto_pe12_2024_2025_2026": g12, "extrapolacao_evitavel_modelo_agente": g12 * (1 - m_emp), "extrapolacao_evitavel_precos_reais": g12 * (1 - hom_cob / e2_cob),
          "extrapolacao_evitavel_prudente_E2_baixo": g12 * (1 - min(hom_cob / e2min_cob, 1)),
          "cenarios": len(S), "cenarios_que_alteram": [s["id"] for s in S if s["altera_a_recomendacao"]]})
json.dump(N, open(os.path.join(RES, "economia_numeros.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30); pd.set_option("display.max_colwidth", 100); pd.set_option("display.float_format", "{:,.0f}".format)
print(pd.DataFrame(E)[["nivel", "de_quem", "indicador", "valor", "observabilidade"]].to_string(index=False))
print(pd.DataFrame(S)[["id", "cenario", "E1", "E2", "E4", "altera_a_recomendacao"]].to_string(index=False))
pd.set_option("display.float_format", "{:,.2f}".format)
print(pd.DataFrame(t2).to_string(index=False))
print(e4[["nomeRazaoSocialFornecedor", "valor", "empenhado_total", "pago_total", "pct_pago_calc", "r0", "ref", "eco_real_estimada_vs_r0"]].to_string(index=False))
for k, v_ in N.items():
    print(k, ":", f"{v_:,.2f}" if isinstance(v_, float) else v_)
