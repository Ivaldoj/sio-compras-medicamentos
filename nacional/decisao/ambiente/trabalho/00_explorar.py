"""Exploração inicial: despeja a cesta e resumos das bases em trabalho/explora_*.csv (leitura apenas)."""
import os, sys
sys.path.insert(0, os.path.join("data", "decision_input_nacional"))
import consulta as q
con = q.conectar()
os.makedirs("trabalho", exist_ok=True)
con.sql("SELECT * FROM cesta ORDER BY posicao_relevancia").df().to_csv("trabalho/explora_cesta.csv", index=False)
con.sql("SELECT ap_id, compatibilidade, flag_preco_extremo, esfera, categoria_valor, count(*) n FROM precos_comprasgov GROUP BY ALL ORDER BY ap_id").df().to_csv("trabalho/explora_cg_resumo.csv", index=False)
con.sql("SELECT ap_id, esfera, flag_preco_extremo, flag_duplicata_negocio, count(*) n, min(data_compra) dmin, max(data_compra) dmax, max(data_insercao) imax FROM precos_bps GROUP BY ALL ORDER BY ap_id").df().to_csv("trabalho/explora_bps_resumo.csv", index=False)
con.sql("SELECT * FROM cmed_teto ORDER BY ap_id").df().to_csv("trabalho/explora_cmed.csv", index=False)
con.sql("SELECT * FROM demanda_mes ORDER BY ap_id, mes_processamento").df().to_csv("trabalho/explora_demanda_mes.csv", index=False)
print("ok")
