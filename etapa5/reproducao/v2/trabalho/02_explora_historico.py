"""Pregões próprios 2024, receitas SUS 2024 e insulinas (detalhe)."""
import sys; sys.path.insert(0, "scripts"); import consulta_agente as q
import pandas as pd
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60); pd.set_option("display.max_colwidth", 100)
con = q.conectar()
s = lambda sql: print(con.execute(sql).df().to_string(), "\n")
s("SELECT pregao, numero_controle_pncp, data_publicacao_pncp, criterio, count(*) n, count(preco_unitario_homologado) n_hom, count(percentual_desconto) n_desc, min(data_resultado) r FROM historico_proprio GROUP BY ALL")
s("SELECT * EXCLUDE (arquivo_origem, base_disponibilidade, classe_temporal) FROM historico_proprio WHERE preco_unitario_homologado IS NOT NULL OR percentual_desconto IS NOT NULL OR pregao NOT LIKE '%01/2024%'")
s("SELECT descricao_receita, codigo_fonte_recurso, round(sum(valor),2) v FROM receitas_sus_2024 GROUP BY 1,2 ORDER BY 3 DESC")
s("SELECT * EXCLUDE (fonte, arquivo_origem, base_disponibilidade, data_disponibilidade, classe_temporal, principio_tokens, catmat_candidatos) FROM itens WHERE item BETWEEN 194 AND 199")
