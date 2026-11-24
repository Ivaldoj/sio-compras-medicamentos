"""Confere como o pacote calcula teto_cmed_unitario_pb_min/max e quantos tetos dependem de vínculos COM ALERTA."""
import sys; sys.path.insert(0, "scripts"); import consulta_agente as q
import pandas as pd
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60); pd.set_option("display.max_colwidth", 80)
con = q.conectar()
s = lambda sql: print(con.execute(sql).df().to_string(), "\n")
base = """WITH t AS (SELECT t.*, r.status, r.inspecao_amostral_ia FROM v_cmed_teto_unitario t JOIN regras_conversao r ON r.item=t.item AND CAST(r.registro AS VARCHAR)=t.registro
      WHERE t.aliquota_aplicavel_pb AND t.aplicabilidade IN ('teto para compras administrativas','teto obrigatório (produto com CAP)'))"""
s(base + """, a AS (SELECT item, min(valor_por_unidade_item) mn_all, max(valor_por_unidade_item) mx_all,
      min(valor_por_unidade_item) FILTER (WHERE status NOT LIKE '%COM ALERTA%' AND coalesce(inspecao_amostral_ia,'') NOT LIKE 'ERRO%') mn_ok,
      max(valor_por_unidade_item) FILTER (WHERE status NOT LIKE '%COM ALERTA%' AND coalesce(inspecao_amostral_ia,'') NOT LIKE 'ERRO%') mx_ok, count(*) n FROM t GROUP BY item)
    SELECT count(*) itens, count(*) FILTER (WHERE abs(mn_all - i.teto_cmed_unitario_pb_min)<1e-6 AND abs(mx_all-i.teto_cmed_unitario_pb_max)<1e-6) iguais_pacote,
      count(*) FILTER (WHERE mx_ok IS NULL) so_alerta, count(*) FILTER (WHERE mx_ok <> mx_all OR mn_ok <> mn_all) muda_com_alerta
    FROM a JOIN itens i USING (item)""")
s(base + """ SELECT item, registro, apresentacao, fator_conversao, tipo_preco, valor_embalagem, valor_por_unidade_item, status FROM t WHERE status LIKE '%COM ALERTA%' AND item IN (SELECT item FROM itens WHERE alerta_estimativa_acima_teto_cmed) ORDER BY item LIMIT 60""")
s("SELECT count(*) n, count(*) FILTER (WHERE teto_cmed_unitario_pb_max IS NOT NULL) com_teto FROM itens")
