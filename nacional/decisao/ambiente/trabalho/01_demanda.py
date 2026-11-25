"""Projeção da quantidade a adquirir (fev/2025-jan/2026) a partir da DISPENSAÇÃO ATENDIDA (SIA).

Entrada: cesta, demanda_mes, demanda_uf (data/decision_input_nacional).
Saída:   trabalho/demanda_projecao.csv (1 linha por apresentação)
         trabalho/demanda_uf_projecao.csv (1 linha por apresentação x UF, rateio pela participação observada)

Regras (todas HIPÓTESES registradas em saida/registro_hipoteses.csv):
- R5 = média mensal dos 5 últimos meses de processamento (jun-out/2024): nível recente, pois há degrau
  de patamar a partir de jun/2024 em quase todos os itens (OBSERVADO em demanda_mes).
- g  = dispensação 12m / dispensação 12m do ano anterior - 1, limitada a [-10%, +30%] (H03).
- Q_baixa   = 12*R5*(1+min(g,0))             -> sem crescimento
- Q_central = 12*R5*(1+g/2)                  -> metade da tendência anual (H04)
- Q_alta    = 12*R5*(1+g)*1.10               -> tendência cheia + 10% de demanda reprimida/recomposição de estoque (H05)
- Estoque inicial desconhecido: assume-se estoque neutro (compra = consumo projetado) (H06).
Dispensação atendida NÃO é demanda total; quantidade projetada NÃO é demanda: é necessidade de compra estimada.
"""
import os, sys
sys.path.insert(0, os.path.join("data", "decision_input_nacional"))
import consulta as q

con = q.conectar()
MES = {"Jan": 1, "Fev": 2, "Mar": 3, "Abr": 4, "Mai": 5, "Jun": 6, "Jul": 7, "Ago": 8, "Set": 9, "Out": 10, "Nov": 11, "Dez": 12}

c = con.sql("SELECT ap_id, nome, grupo_financiamento, dispensacao_12m_pre_corte d12, dispensacao_12m_ano_anterior d12a FROM cesta").df()
m = con.sql("SELECT * FROM demanda_mes").df()
m["t"] = m.mes_processamento.map(lambda s: int(s[:4]) * 12 + MES[s[5:]])
ult5 = sorted(m.t.unique())[-5:]
assert len(m.t.unique()) == 12 and len(ult5) == 5
r5 = m[m.t.isin(ult5)].groupby("ap_id").dispensacao.mean().rename("r5_mensal")
c = c.merge(r5, on="ap_id")
c["g_bruto"] = c.d12 / c.d12a - 1
c["g"] = c.g_bruto.clip(-0.10, 0.30)
c["q_baixa"] = 12 * c.r5_mensal * (1 + c.g.clip(upper=0))
c["q_central"] = 12 * c.r5_mensal * (1 + c.g / 2)
c["q_alta"] = 12 * c.r5_mensal * (1 + c.g) * 1.10
assert (c.q_baixa <= c.q_central).all() and (c.q_central <= c.q_alta).all()
c.round(1).to_csv("trabalho/demanda_projecao.csv", index=False)

u = con.sql("SELECT ap_id, uf, dispensacao_12m_pre_corte d_uf FROM demanda_uf").df()
u["part"] = u.d_uf / u.groupby("ap_id").d_uf.transform("sum")
u = u.merge(c[["ap_id", "q_central"]], on="ap_id")
u["q_central_uf"] = u.part * u.q_central  # rateio pela participação observada (H07)
u.round(4).to_csv("trabalho/demanda_uf_projecao.csv", index=False)
print(c[["ap_id", "d12", "g_bruto", "q_baixa", "q_central", "q_alta"]].round(2).to_string())
