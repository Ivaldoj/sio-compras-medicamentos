"""Complementos: tipos de preço CMED, PNCP (SRP, esfera, datas), quantidades 2025 x 2024, PE 01/2024 x itens atuais."""
import sys; sys.path.insert(0, "scripts"); import consulta_agente as q
import pandas as pd
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60); pd.set_option("display.max_colwidth", 80)
con = q.conectar()
s = lambda sql: print(con.execute(sql).df().to_string(), "\n")
s("SELECT tipo_preco, aliquota_icms, count(*) FROM cmed_precos GROUP BY ALL ORDER BY 1,2")
s("SELECT esfera, srp, modalidade, criterio_selecao, count(*) n, min(data_publicacao_pncp) d0, max(data_publicacao_pncp) d1 FROM pncp_contratacoes GROUP BY ALL ORDER BY n DESC")
s("SELECT uf, count(*) FROM pncp_contratacoes GROUP BY 1 ORDER BY 2 DESC")
s("SELECT count(DISTINCT v.item) itens, count(*) n FROM v_pncp_comparavel v WHERE preco_unitario_homologado IS NOT NULL")
s("SELECT c.srp, c.esfera, count(DISTINCT v.item) itens, count(*) n, min(v.data_resultado) d0, max(v.data_resultado) d1 FROM v_pncp_comparavel v JOIN pncp_contratacoes c USING (numero_controle_pncp) WHERE v.preco_unitario_homologado IS NOT NULL GROUP BY ALL")
# quantidades 2025 x 2024
s("SELECT count(*) n, sum(quantidade_estimada) q25, sum(qtd_licitada_pregoes_proprios_2024) q24, median(quantidade_estimada/qtd_licitada_pregoes_proprios_2024) med_razao, quantile_cont(quantidade_estimada/qtd_licitada_pregoes_proprios_2024,0.1) p10, quantile_cont(quantidade_estimada/qtd_licitada_pregoes_proprios_2024,0.9) p90, count(*) FILTER (WHERE quantidade_estimada=qtd_licitada_pregoes_proprios_2024) iguais FROM itens WHERE qtd_licitada_pregoes_proprios_2024>0")
s("SELECT i.item, i.descricao, i.quantidade_estimada, i.preco_unitario_estimado_orgao, i.pregoes_proprios_2024_itens, h.preco_unitario_homologado, h.quantidade FROM itens i JOIN historico_proprio h ON list_contains(string_split(i.pregoes_proprios_2024_itens,'|'), h.pregao || '#' || h.numero_item) WHERE h.preco_unitario_homologado IS NOT NULL")
s("SELECT pregoes_proprios_2024_itens FROM itens WHERE pregoes_proprios_2024_itens IS NOT NULL LIMIT 5")
s("SELECT * FROM receitas_sus_2024 WHERE descricao_receita LIKE '%Farmac%' ORDER BY mes_ano")
