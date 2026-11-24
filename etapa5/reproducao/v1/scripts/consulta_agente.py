"""Consultas do agente decisor sobre data/decision_input (DuckDB lendo Parquet/CSV sob demanda; nada é carregado inteiro).
Só arquivos dentro de data/decision_input/ podem ser abertos: qualquer outro caminho levanta PermissionError.

Uso em Python:
    import sys; sys.path.insert(0, "scripts"); import consulta_agente as q
    con = q.conectar()
    q.necessidades(con).head(); q.historico(con, item=76, uf="PB"); q.teto_cmed(con, item=28)
    con.sql("SELECT uf, count(*) FROM bps GROUP BY uf").df()
Uso na linha de comando:  python -I -X utf8 scripts/consulta_agente.py "<SQL>"
Esquemas: DESCRIBE <tabela> no DuckDB. Documentação do pacote: data/decision_input/LEIA-ME.md"""
import os, sys
import duckdb

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DI = os.path.join(RAIZ, "data", "decision_input")

TABELAS = {
    "itens": "organizacional/itens_santa_luzia.parquet",
    "restricoes": "organizacional/restricoes.csv",
    "recursos": "organizacional/recursos.csv",
    "execucao_2024_mensal": "organizacional/execucao_farmaco_2024_mensal.csv",
    "execucao_2024_licitacao": "organizacional/execucao_farmaco_2024_por_licitacao.csv",
    "historico_proprio": "organizacional/historico_proprio_pregoes_2024.parquet",
    "bps": "nacional/bps_precos_praticados.parquet",
    "cmed_apresentacoes": "nacional/cmed_2025_01_apresentacoes.parquet",
    "cmed_precos": "nacional/cmed_2025_01_precos.parquet",
    "pncp_contratacoes": "nacional/pncp_comparaveis_contratacoes.parquet",
    "pncp_itens": "nacional/pncp_comparaveis_itens.parquet",
    "pncp_resultados": "nacional/pncp_comparaveis_resultados.parquet",
    "item_catmat": "padronizacao/item_catmat_candidatos.parquet",
    "item_cmed": "padronizacao/item_cmed_vinculos.parquet",
    "item_bps_grupos": "padronizacao/item_bps_grupos.parquet",
    "regras_conversao": "padronizacao/regras_conversao.csv",
    # pré-Etapa 4
    "comprasgov": "nacional/comprasgov_precos_praticados.parquet",
    "item_comprasgov": "padronizacao/item_comprasgov_registros.parquet",
    "item_catmat_oficial": "padronizacao/item_catmat_catalogo_oficial.parquet",
    "receitas_sus_2024": "organizacional/receitas_sus_2024.csv",
}
VISOES = {
    # registros BPS (pré-corte) do mesmo CATMAT, unidade e capacidade compatíveis com o item
    "v_bps_comparavel": """SELECT g.item, g.compatibilidade, b.* FROM item_bps_grupos g JOIN bps b ON b.catmat = g.catmat
        AND b.unidade_fornecimento IS NOT DISTINCT FROM g.unidade_fornecimento AND b.capacidade_descricao IS NOT DISTINCT FROM g.capacidade_descricao
        WHERE g.compatibilidade = 'compativel'""",
    "v_bps_a_conferir": """SELECT g.item, g.compatibilidade, b.* FROM item_bps_grupos g JOIN bps b ON b.catmat = g.catmat
        AND b.unidade_fornecimento IS NOT DISTINCT FROM g.unidade_fornecimento AND b.capacidade_descricao IS NOT DISTINCT FROM g.capacidade_descricao
        WHERE g.compatibilidade IN ('capacidade_nao_informada', 'conteudo_item_nao_extraido')""",
    # teto CMED por unidade do item: só vínculos exatos/compatíveis com fator por regra; nunca recalcula CAP
    "v_cmed_teto_unitario": """SELECT v.item, v.registro, v.produto, v.apresentacao, v.classe, v.fator_conversao, p.tipo_preco, p.aliquota_icms,
        p.valor_embalagem, p.valor_embalagem / v.fator_conversao AS valor_por_unidade_item, p.aplicabilidade, p.aliquota_aplicavel_pb, p.aliquota_status, p.categoria_valor
        FROM item_cmed v JOIN cmed_precos p USING (registro)
        WHERE v.classe IN ('exata', 'compativel_conversao') AND v.fator_conversao >= 1""",
    # registros Compras.gov.br (resultado até o corte) compatíveis com o item por CATMAT + unidade de fornecimento/capacidade
    "v_comprasgov_comparavel": """SELECT r.item, r.nivel, r.compatibilidade, c.* FROM item_comprasgov r JOIN comprasgov c USING (id_origem)
        WHERE r.compatibilidade = 'compativel'""",
    "v_comprasgov_a_conferir": """SELECT r.item, r.nivel, r.compatibilidade, c.* FROM item_comprasgov r JOIN comprasgov c USING (id_origem)
        WHERE r.compatibilidade LIKE 'a_conferir%'""",
    "v_bloqueados": """SELECT item, 'CMED' AS fonte, registro AS id, apresentacao AS descricao, classe AS situacao, justificativa AS motivo FROM item_cmed
        WHERE classe IN ('incompativel', 'indeterminada', 'provavel_conferencia')
        UNION ALL SELECT item, 'BPS' AS fonte, catmat AS id, coalesce(unidade_fornecimento, '') || ' ' || coalesce(capacidade_descricao, '') AS descricao,
        compatibilidade AS situacao, 'grupo CATMAT × unidade × capacidade sem compatibilidade comprovada' AS motivo FROM item_bps_grupos WHERE compatibilidade <> 'compativel'""",
    "v_pncp_comparavel": """SELECT CAST(t.item AS INTEGER) AS item, i.*, r.fornecedor_cnpj, r.preco_unitario_homologado, r.quantidade_homologada, r.data_resultado,
        r.data_inclusao AS data_inclusao_resultado FROM (SELECT *, unnest(string_split(itens_caso_comparaveis, '|')) AS item FROM pncp_itens
        WHERE itens_caso_comparaveis IS NOT NULL) t JOIN pncp_itens i USING (numero_controle_pncp, numero_item)
        LEFT JOIN pncp_resultados r USING (numero_controle_pncp, numero_item)""",
}


def caminho(rel):
    p = os.path.realpath(os.path.join(DI, rel))
    if not p.startswith(os.path.realpath(DI) + os.sep):
        raise PermissionError(f"acesso negado fora de data/decision_input: {rel}")
    return p


def conectar():
    con = duckdb.connect()
    for nome, rel in TABELAS.items():
        p = caminho(rel)
        if not os.path.exists(p):
            continue
        leitor = "read_parquet" if p.endswith(".parquet") else "read_csv_auto"
        con.execute(f"CREATE VIEW {nome} AS SELECT * FROM {leitor}('{p.replace(os.sep, '/')}')")
    for nome, sql in VISOES.items():
        try:
            con.execute(f"CREATE VIEW {nome} AS {sql}")
        except duckdb.Error:
            pass  # visão depende de tabela ausente (ex.: PNCP ainda não consolidado)
    return con


def necessidades(con):
    return con.sql("SELECT item, descricao, unidade, quantidade_estimada, preco_unitario_estimado_orgao, valor_total_estimado_orgao, "
                   "status_identificacao, status_preco_praticado, status_teto_cmed FROM itens ORDER BY item").df()


def historico(con, item=None, catmat=None, uf=None, regiao=None, de=None, ate=None):
    """Compras nacionais pré-corte (BPS) do medicamento: por item do caso (CATMAT+unidade+capacidade compatíveis) ou por CATMAT."""
    w, a = [], []
    base = "v_bps_comparavel" if item is not None else "bps"
    if item is not None: w.append("item = ?"); a.append(item)
    if catmat is not None: w.append("catmat = ?"); a.append(str(catmat))
    if uf: w.append("uf = ?"); a.append(uf)
    if regiao: w.append("regiao = ?"); a.append(regiao)
    if de: w.append("data_compra >= ?"); a.append(de)
    if ate: w.append("data_compra <= ?"); a.append(ate)
    return con.execute(f"SELECT * FROM {base}" + (" WHERE " + " AND ".join(w) if w else "") + " ORDER BY data_compra", a).df()


def precos_compativeis(con, item):
    """Preços por unidade do item, de fontes distintas, sem misturar categorias (campo categoria_valor)."""
    bps = """SELECT 'BPS' AS fonte, id_origem, catmat AS identificacao, data_compra AS data_observacao, data_insercao AS data_disponibilidade,
            uf, comprador_nome, quantidade, preco_unitario_praticado AS valor_unitario, categoria_valor, flag_preco_extremo
            FROM v_bps_comparavel WHERE item = ?"""
    tem = lambda v: con.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = ?", [v]).fetchone()[0]
    args = [item]
    if tem("v_comprasgov_comparavel"):
        bps += """
        UNION ALL SELECT 'Compras.gov.br', id_origem, catmat, data_compra, data_resultado, uf, comprador_nome, quantidade, preco_unitario_praticado,
            categoria_valor, flag_possivel_duplicata_bps FROM v_comprasgov_comparavel WHERE item = ?"""
        args.append(item)
    if not tem("v_pncp_comparavel"):
        return con.execute(bps + " ORDER BY fonte, data_observacao", args).df()
    return con.execute(bps + """
        UNION ALL SELECT 'PNCP', numero_controle_pncp || '#' || numero_item, descricao, data_resultado, data_inclusao_resultado, NULL, NULL,
            quantidade_homologada, preco_unitario_homologado, 'preco_unitario_homologado (por unidade do item)', NULL
            FROM v_pncp_comparavel WHERE item = ? AND preco_unitario_homologado IS NOT NULL
        UNION ALL SELECT 'PNCP', numero_controle_pncp || '#' || numero_item, descricao, data_inclusao, data_inclusao, NULL, NULL,
            quantidade, preco_unitario_estimado, categoria_valor, NULL
            FROM v_pncp_comparavel WHERE item = ? AND preco_unitario_estimado > 0
        ORDER BY fonte, data_observacao""", args + [item, item]).df()


def teto_cmed(con, item, aliquota=None, so_pb=True):
    """Teto por unidade do item. Padrão: só a coluna de ICMS aplicável a Santa Luzia/PB (aliquota_aplicavel_pb); so_pb=False mostra todas."""
    sql = ("SELECT * FROM v_cmed_teto_unitario WHERE item = ?" + (" AND aliquota_icms = ?" if aliquota else "") + (" AND aliquota_aplicavel_pb" if so_pb and not aliquota else "")
           + " ORDER BY classe, registro, tipo_preco, aliquota_icms")
    return con.execute(sql, [item] + ([aliquota] if aliquota else [])).df()


def bloqueados(con, item):
    return con.execute("SELECT * FROM v_bloqueados WHERE item = ? ORDER BY fonte, situacao", [item]).df()


if __name__ == "__main__":
    import pandas as pd
    pd.set_option("display.width", 250)
    print(conectar().sql(sys.argv[1]).df().to_string() if len(sys.argv) > 1 else __doc__)
