"""Detalhe das insulinas (itens 194-199): vínculos CMED, tetos, preços praticados, a conferir, PNCP, bloqueios."""
import sys; sys.path.insert(0, "scripts"); import consulta_agente as q
import pandas as pd
pd.set_option("display.width", 300); pd.set_option("display.max_columns", 60); pd.set_option("display.max_colwidth", 120)
con = q.conectar()
s = lambda sql, a=None: print(con.execute(sql, a or []).df().to_string(), "\n")
s("SELECT DISTINCT pregao, classe_temporal, base_disponibilidade FROM historico_proprio")
s("SELECT * EXCLUDE(arquivo_origem, base_disponibilidade, classe_temporal) FROM historico_proprio WHERE lower(descricao) LIKE '%insulin%'")
for it in range(194, 200):
    print("#"*30, "ITEM", it)
    s("SELECT classe, count(*) n FROM item_cmed WHERE item=? GROUP BY 1", [it])
    s("SELECT registro, produto, laboratorio, apresentacao, classe, fator_conversao, justificativa, validacao_humana FROM item_cmed WHERE item=? AND classe IN ('exata','compativel_conversao','provavel_conferencia','indeterminada')", [it])
    s("SELECT registro, apresentacao, tipo_preco, aliquota_icms, valor_embalagem, fator_conversao, valor_por_unidade_item, aplicabilidade, aliquota_status FROM v_cmed_teto_unitario WHERE item=? AND aliquota_aplicavel_pb", [it])
    s("SELECT registro, apresentacao, classe, regra, teto_tipo, teto_aliquota_pb, teto_unitario_pb, razao_mediana_item, verif_consistencia_interna, verif_preco_praticado, inspecao_amostral_ia, status FROM regras_conversao WHERE item=?", [it])
    s("SELECT item, catmat, unidade_fornecimento, capacidade_descricao, registros, ufs, compatibilidade FROM item_bps_grupos WHERE item=?", [it])
    s("SELECT fonte, count(*) n, min(valor_unitario) mn, quantile_cont(valor_unitario,0.25) p25, median(valor_unitario) med, quantile_cont(valor_unitario,0.75) p75, max(valor_unitario) mx, min(data_observacao) d0, max(data_observacao) d1 FROM (SELECT * FROM __p) GROUP BY 1".replace("__p", "(SELECT 1)") if False else "SELECT 1", None)
    p = q.precos_compativeis(con, it)
    if len(p):
        p["ano"] = pd.to_datetime(p["data_observacao"], errors="coerce").dt.year
        print(p.groupby(["fonte", "categoria_valor"])["valor_unitario"].describe(percentiles=[.1,.25,.5,.75,.9]).to_string(), "\n")
        print(p[p.fonte=="PNCP"].to_string(), "\n")
    s("SELECT compatibilidade, nivel, count(*) n, median(preco_unitario_praticado) med, quantile_cont(preco_unitario_praticado,0.1) p10, quantile_cont(preco_unitario_praticado,0.9) p90, min(data_compra) d0, max(data_compra) d1 FROM v_comprasgov_a_conferir WHERE item=? GROUP BY 1,2", [it])
    s("SELECT unidade_fornecimento, capacidade_valor, capacidade_unidade, descricao_detalhada, marca, uf, data_compra, quantidade, preco_unitario_praticado FROM v_comprasgov_a_conferir WHERE item=? ORDER BY data_compra DESC LIMIT 20", [it])
