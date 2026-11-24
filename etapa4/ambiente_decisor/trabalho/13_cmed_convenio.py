"""Linhas de preço CMED das canetas de insulina (196/199) e verificação: produtos do Convênio ICMS 87/02 têm coluna de 20% no pacote?"""
import sys; sys.path.insert(0, "scripts"); import consulta_agente as q
import pandas as pd
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 60)
con = q.conectar()
s = lambda sql: print(con.execute(sql).df().to_string(), "\n")
s("SELECT registro, tipo_preco, aliquota_icms, valor_embalagem, aplicabilidade, aliquota_aplicavel_pb FROM cmed_precos WHERE registro IN ('1176600040099','1176600030115') ORDER BY 1,2,3")
s("SELECT registro, produto, tipo_produto, cap, icms_isento_so_0pct, convenio_confaz_87, teto_compras_administrativas, aliquota_icms_pb FROM cmed_apresentacoes WHERE registro IN ('1176600040099','1176600030115','1176600040102','1176600030123')")
s("SELECT count(DISTINCT p.registro) registros_conv87_com_coluna_20pct FROM cmed_precos p JOIN cmed_apresentacoes a USING (registro) WHERE a.convenio_confaz_87 AND p.aliquota_icms = '20%'")
s("SELECT count(*) registros_conv87 FROM cmed_apresentacoes WHERE convenio_confaz_87")
