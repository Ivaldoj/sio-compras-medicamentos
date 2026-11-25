"""Sensibilidade determinística da economia potencial (itens descentralizados: 1B exceto AP007, e 2).

Entradas: trabalho/precos_referencia.csv, trabalho/demanda_projecao.csv, trabalho/elasticidade.csv, cesta.
Saída:    trabalho/sensibilidade.csv  (economia anual vs E1 por cenário; valor estimado de contratação, não pagamento)
Fórmulas iguais às de 03_estrategias.py, em valores centrais (índice de preço 2025 = 1,025).
"""
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.join("data", "decision_input_nacional"))
import consulta as q

con = q.conectar()
g = con.sql("SELECT ap_id, grupo_financiamento FROM cesta").df()
d = (pd.read_csv("trabalho/precos_referencia.csv").merge(g, on="ap_id")
     .merge(pd.read_csv("trabalho/demanda_projecao.csv")[["ap_id", "q_baixa", "q_central", "q_alta"]], on="ap_id"))
d = d[(d.grupo_financiamento != "1A") & (d.ap_id != "AP007")].copy()
assert len(d) == 11
el = pd.read_csv("trabalho/elasticidade.csv").set_index("segmento")
usa = d.n_estadual_24m >= 3
p1 = np.where(usa, d.mediana_estadual_24m, d.mediana_24m)
p75 = np.where(usa, d.p75_estadual_24m, d.p75_24m)
IDX = 1.025


def f(v, beta):
    return np.minimum(1, np.exp(beta * (np.minimum(np.log(v), np.log(d.lq_max_obs)) - np.log(d.q_ref_mediana))))


def eco(Q, s, beta, v=None, p=p1):
    v = d.v_nacional if v is None else v
    return float((Q * p * IDX * s * (1 - f(v, beta))).sum())


bc = d.segmento.map(el.beta)
bi, bs = d.segmento.map(el.ic90_inf), d.segmento.map(el.ic90_sup)
e1 = float((d.q_central * p1 * IDX).sum())
lin = [
    ("E1 custo descentralizados (referência)", e1, ""),
    ("E2 central (s=0,55; beta central; Q central)", eco(d.q_central, .55, bc), ""),
    ("E2 beta = 0 (sem efeito volume)", eco(d.q_central, .55, 0 * bc), "economia desaparece; E2 só se justifica por risco/gestão"),
    ("E2 beta no limite menos negativo do IC90", eco(d.q_central, .55, bs), ""),
    ("E2 beta no limite mais negativo do IC90", eco(d.q_central, .55, bi), ""),
    ("E2 transição lenta (s=0,40)", eco(d.q_central, .40, bc), ""),
    ("E2 transição rápida (s=0,70)", eco(d.q_central, .70, bc), ""),
    ("E2 regime pleno (s=1)", eco(d.q_central, 1, bc), "potencial anual após transição"),
    ("E2 Q baixa", eco(d.q_baixa, .55, bc), ""),
    ("E2 Q alta", eco(d.q_alta, .55, bc), ""),
    ("E2 preço base = p75 (estados pagam mais)", eco(d.q_central, .55, bc, p=p75), ""),
    ("E3 central (s=0,40; volume regional)", eco(d.q_central, .40, bc, v=d.v_regiao_mediana), ""),
    ("E3 regime pleno", eco(d.q_central, 1, bc, v=d.v_regiao_mediana), ""),
    ("E4 central (s=0,15)", eco(d.q_central, .15, bc), ""),
]
# cenário otimista: preço nacional = razão DLOG/mediana estadual observada (mediana 0,29) — limite superior, não central
r = pd.read_csv("trabalho/precos_referencia.csv")
r = r[r.dlog_prog_preco.notna() & (r.n_estadual_24m >= 3)]
razao = float((r.dlog_prog_preco / r.mediana_estadual_24m).median())
lin.append(("E2 otimista: preço nacional = razão DLOG/estadual observada (s=0,55)",
            float((d.q_central * p1 * IDX * .55 * (1 - razao)).sum()), f"razão mediana = {razao:.3f}; não usada no central"))
out = pd.DataFrame(lin, columns=["cenario", "valor_R$", "nota"])
out["pct_de_E1_descentralizados"] = out["valor_R$"] / e1
out.to_csv("trabalho/sensibilidade.csv", index=False)
print(out.round(3).to_string())

# Conferência (não soma): mediana BPS 24m / mediana Compras.gov 24m por item
r = pd.read_csv("trabalho/precos_referencia.csv")
x = (r.bps_mediana_24m / r.mediana_24m).dropna()
print(f"\nBPS/Compras.gov (medianas 24m): n={len(x)} p10={x.quantile(.1):.2f} mediana={x.median():.2f} p90={x.quantile(.9):.2f}; "
      f"itens fora de [0,67;1,5]: {list(r.loc[x[(x < 0.67) | (x > 1.5)].index, 'ap_id'])}")
