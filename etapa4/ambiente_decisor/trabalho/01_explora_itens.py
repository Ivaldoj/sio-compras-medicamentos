"""Exploração da tabela itens: status, valores, distribuição (diagnóstico)."""
import sys; sys.path.insert(0, "scripts"); import consulta_agente as q
import pandas as pd
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60); pd.set_option("display.max_colwidth", 80)
con = q.conectar()
s = lambda sql: print(con.execute(sql).df().to_string(), "\n")
s("SELECT count(*) n, sum(valor_total_estimado_orgao) v, sum(quantidade_estimada*preco_unitario_estimado_orgao) v2 FROM itens")
for c in ["status_necessidade","status_identificacao","status_preco_praticado","status_teto_cmed","catmat_status","cmed_melhor_classe","fonte","classe_temporal","unidade"]:
    s(f"SELECT {c}, count(*) n, round(sum(valor_total_estimado_orgao),2) valor, round(100*sum(valor_total_estimado_orgao)/4952438,2) pct FROM itens GROUP BY 1 ORDER BY 3 DESC")
s("SELECT alerta_estimativa_acima_teto_cmed, count(*) n, round(sum(valor_total_estimado_orgao),2) v FROM itens GROUP BY 1")
s("SELECT inconsistencia_unidade, count(*) n, round(sum(valor_total_estimado_orgao),2) v FROM itens GROUP BY 1")
s("SELECT cmed_alguma_com_cap, count(*) n, round(sum(valor_total_estimado_orgao),2) v FROM itens GROUP BY 1")
s("SELECT fontes_preco_praticado, count(*) n FROM itens GROUP BY 1 ORDER BY 2 DESC")
s("SELECT count(*) FILTER (WHERE qtd_licitada_pregoes_proprios_2024>0) n_lic, sum(valor_total_estimado_orgao) FILTER (WHERE qtd_licitada_pregoes_proprios_2024>0) v FROM itens")
s("SELECT item, descricao, unidade, quantidade_estimada q, preco_unitario_estimado_orgao p, valor_total_estimado_orgao v, status_preco_praticado, status_teto_cmed, teto_cmed_unitario_pb_min tmin, teto_cmed_unitario_pb_max tmax, alerta_estimativa_acima_teto_cmed alerta FROM itens ORDER BY v DESC LIMIT 40")
s("SELECT item, descricao FROM itens WHERE lower(descricao) LIKE '%insulin%'")
s("SELECT DISTINCT base_disponibilidade, data_disponibilidade FROM itens")
