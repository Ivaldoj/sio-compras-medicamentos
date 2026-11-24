"""Insulinas em caneta: registros BPS/Compras.gov.br dos CATMAT 440255, 442012, 468664 (e vínculo aos itens 194/195); vínculo com ERRO da inspeção IA."""
import sys; sys.path.insert(0, "scripts"); import consulta_agente as q
import pandas as pd
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60); pd.set_option("display.max_colwidth", 70)
con = q.conectar()
s = lambda sql: print(con.execute(sql).df().to_string(), "\n")
s("SELECT item, catmat, descricao_catmat, nivel, criterio FROM item_catmat WHERE item BETWEEN 194 AND 199")
s("SELECT catmat, descricao_catmat, unidade_fornecimento, capacidade_descricao, uf, esfera, data_compra, quantidade, preco_unitario_praticado, flag_preco_extremo, flag_duplicata_negocio FROM bps WHERE catmat IN ('440255','442012','468664') ORDER BY catmat, data_compra")
s("SELECT catmat, descricao_detalhada, unidade_fornecimento, capacidade_valor, marca, uf, esfera, data_compra, quantidade, preco_unitario_praticado, flag_possivel_duplicata_bps FROM comprasgov WHERE catmat IN ('440255','442012','468664') ORDER BY catmat, data_compra")
s("SELECT r.item, r.catmat, r.compatibilidade, count(*) FROM item_comprasgov r WHERE item BETWEEN 194 AND 199 GROUP BY ALL ORDER BY 1")
s("SELECT item, registro, apresentacao, fator_conversao, teto_unitario_pb, inspecao_amostral_ia, status FROM regras_conversao WHERE inspecao_amostral_ia LIKE 'ERRO%' OR inspecao_amostral_ia LIKE '%RESSALVA%'")
