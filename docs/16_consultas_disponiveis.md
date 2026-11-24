# 16 — Consultas disponíveis ao agente decisor

> **Atualização pré-Etapa 4 (23/11/2026):** novas tabelas (`comprasgov`, `item_comprasgov`, `item_catmat_oficial`, `receitas_sus_2024`) e visões (`v_comprasgov_comparavel`, `v_comprasgov_a_conferir`); `precos_compativeis` inclui o Compras.gov.br e `teto_cmed` filtra a alíquota da PB por padrão (`so_pb=False` mostra todas). Estado atual e números em `docs/18_pre_etapa4_tratamento_lacunas.md`; o texto abaixo descreve a Etapa 3.

O módulo `scripts/consulta_agente.py` cria uma conexão DuckDB em memória com **visões** sobre os arquivos de `data/decision_input/`. As linhas são lidas sob demanda: a base nacional não é carregada inteira. Qualquer caminho fora de `decision_input` é recusado (`PermissionError`), e isso é testado.

```python
import sys; sys.path.insert(0, "scripts")
import consulta_agente as q
con = q.conectar()
```

Linha de comando: `python -I -X utf8 scripts/consulta_agente.py "<SQL>"`.

## 1. Funções

| Função | Retorna | Parâmetros |
|---|---|---|
| `necessidades(con)` | 334 itens: quantidade, unidade, preço estimado, status de identificação, preço praticado e teto CMED | — |
| `historico(con, item=None, catmat=None, uf=None, regiao=None, de=None, ate=None)` | compras BPS pré-corte; com `item`, só os grupos CATMAT × unidade × capacidade **compatíveis** com o item | datas no formato `'AAAA-MM-DD'` |
| `precos_compativeis(con, item)` | preços **por unidade do item**, de BPS e PNCP, com `fonte`, `id_origem`, `categoria_valor`, datas e `flag_preco_extremo` | — |
| `teto_cmed(con, item, aliquota=None)` | teto CMED por unidade do item, só para vínculos `exata`/`compativel_conversao`, com `tipo_preco`, `aplicabilidade` e `aliquota_status` | ex.: `'0%'`, `'20%'` |
| `bloqueados(con, item)` | vínculos CMED e grupos BPS que **não podem** ser usados, com o motivo | — |

## 2. Visões

| Visão | Definição resumida |
|---|---|
| `v_bps_comparavel` | `item_bps_grupos` (compatibilidade = 'compativel') ⨝ `bps` por CATMAT, unidade de fornecimento e capacidade |
| `v_bps_a_conferir` | idem, para capacidade não informada ou conteúdo do item não extraído |
| `v_cmed_teto_unitario` | `item_cmed` (exata/compatível, fator ≥ 1) ⨝ `cmed_precos`; `valor_por_unidade_item = valor_embalagem / fator_conversao` (sem recalcular CAP) |
| `v_pncp_comparavel` | itens do PNCP marcados como comparáveis a cada item do caso, com o resultado quando disponível |
| `v_bloqueados` | vínculos CMED incompatíveis, indeterminados ou prováveis, mais grupos BPS sem compatibilidade comprovada |

Tabelas-base: `itens`, `restricoes`, `recursos`, `execucao_2024_mensal`, `execucao_2024_licitacao`, `historico_proprio`, `bps`, `cmed_apresentacoes`, `cmed_precos`, `pncp_contratacoes`, `pncp_itens`, `pncp_resultados`, `item_catmat`, `item_cmed`, `item_bps_grupos`, `regras_conversao` (esquemas no doc 12).

## 3. Exemplos de SQL

```sql
-- necessidades com maior valor estimado e o que se sabe de cada uma
SELECT item, descricao, quantidade_estimada, valor_total_estimado_orgao, status_identificacao, status_preco_praticado, status_teto_cmed
FROM itens ORDER BY valor_total_estimado_orgao DESC LIMIT 10;

-- histórico nacional de um item, por ano e região (mediana e quartis; sem os marcados como extremos)
SELECT year(data_compra) ano, regiao, count(*) n, median(preco_unitario_praticado) mediana,
       quantile_cont(preco_unitario_praticado, 0.25) p25, quantile_cont(preco_unitario_praticado, 0.75) p75
FROM v_bps_comparavel WHERE item = 76 AND NOT flag_preco_extremo GROUP BY ALL ORDER BY ano, regiao;

-- compras de municípios nordestinos de um CATMAT, com quantidade e comprador
SELECT data_compra, uf, comprador_nome, quantidade, preco_unitario_praticado, modalidade, fonte, id_origem
FROM bps WHERE catmat = '267625' AND regiao = 'NE' AND esfera = 'MUNICIPAL' ORDER BY data_compra DESC;

-- teto CMED unitário aplicável a compras administrativas (PF sem CAP; PMVG com CAP), alíquota 0%
SELECT item, registro, produto, apresentacao, classe, tipo_preco, valor_por_unidade_item, aplicabilidade
FROM v_cmed_teto_unitario
WHERE item = 28 AND aliquota_icms = '0%' AND aplicabilidade IN ('teto para compras administrativas', 'teto obrigatório (produto com CAP)');

-- por que um item não tem teto CMED utilizável
SELECT * FROM v_bloqueados WHERE item = 196;

-- contratações comparáveis no PNCP (publicadas até o corte) para um item
SELECT numero_controle_pncp, descricao, unidade, quantidade, preco_unitario_estimado, preco_unitario_homologado, data_inclusao_resultado
FROM v_pncp_comparavel WHERE item = 76;

-- despesa farmacológica de 2024 por mês (informação interna do órgão)
SELECT mes, valor_empenhado, valor_liquidado, valor_pago FROM execucao_2024_mensal ORDER BY mes;
```

## 4. Cuidados embutidos nas consultas

- Os valores vêm sempre acompanhados de `categoria_valor`; as funções nunca somam categorias diferentes.
- `v_cmed_teto_unitario` não inclui vínculos prováveis, indeterminados ou incompatíveis.
- `historico(item=…)` usa só grupos compatíveis; os casos a conferir ficam em `v_bps_a_conferir`.
- Nenhuma consulta produz ranking, recomendação ou escolha.
