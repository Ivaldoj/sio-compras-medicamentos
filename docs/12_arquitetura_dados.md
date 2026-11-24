# 12 — Arquitetura dos dados (Etapa 3)

Data de corte do experimento: **29/01/2025**. Formato: Parquet (tabelas) e CSV (tabelas pequenas), consultados com **DuckDB** (`scripts/consulta_agente.py`), que lê só as colunas e linhas pedidas.

## 1. Diretórios

```
data/
├── raw/                      fontes originais (Etapas 1–3; nunca alteradas)
├── processed/                derivados intermediários (Etapas 1–3; inclui etapa3/itens_atributos.parquet)
├── decision_input/           ÚNICO conjunto entregue ao agente decisor (só pré-corte)
│   ├── LEIA-ME.md            problema, regras de leitura e guia das tabelas
│   ├── MANIFESTO.csv/.json   arquivos, SHA-256, registros, fontes, períodos, limitações
│   ├── organizacional/       Santa Luzia: itens, restrições, recursos, despesa 2024, pregões próprios de 2024
│   ├── nacional/             BPS 2020–2024, PNCP comparáveis, CMED jan/2025
│   └── padronizacao/         CATMAT candidatos, vínculos CMED, grupos BPS compatíveis, regras de conversão
├── evaluation_only/          resultados posteriores ao corte (reservado; LEIA-ME próprio)
│   ├── organizacional/       PE 04/2025 homologado, contratos, execução 2025–26, pregões 25/2025 e 09/2026
│   ├── nacional/             BPS e PNCP posteriores ao corte
│   └── auditoria/            CATMAT da Etapa 2 (pós-corte) × identificação pré-corte
└── quarentena_temporal/      registros cuja disponibilidade não pôde ser comprovada
```

Artefatos de etapas anteriores foram preservados. `data/processed/caso_santa_luzia/pre_decisao/` (Etapa 2) foi **substituído** por `decision_input/`: ele contém CATMAT obtido com dados posteriores ao corte e não deve ser entregue ao agente.

## 2. Tabelas do pacote decisório e chaves

| Tabela (visão DuckDB) | Arquivo | Chave | Linhas | Conteúdo |
|---|---|---|---|---|
| `itens` | organizacional/itens_santa_luzia.parquet | `item` | 334 | necessidade, atributos padronizados, status por dimensão |
| `restricoes` | organizacional/restricoes.csv | — | 7 | restrições com evidência |
| `recursos` | organizacional/recursos.csv | — | 3 | estimativa, dotações, saldo (desconhecido) |
| `execucao_2024_mensal`, `execucao_2024_licitacao` | organizacional/execucao_farmaco_2024_*.csv | (ano, mês) / (ano, licitação) | 10 / 4 | despesa farmacológica 2024 |
| `historico_proprio` | organizacional/historico_proprio_pregoes_2024.parquet | (`pregao`, `numero_item`) | 352 | PE 01/2024 e PE 12/2024 |
| `bps` | nacional/bps_precos_praticados.parquet | `id_origem` (co_seq_bps) | 225.518 | compras de medicamentos 2020–2024 |
| `pncp_contratacoes` | nacional/pncp_comparaveis_contratacoes.parquet | `numero_controle_pncp` | 13 | contratações publicadas até o corte |
| `pncp_itens` | nacional/pncp_comparaveis_itens.parquet | (`numero_controle_pncp`, `numero_item`) | 1.091 | itens completos (PNCP), com `itens_caso_comparaveis` |
| `pncp_resultados` | nacional/pncp_comparaveis_resultados.parquet | (`numero_controle_pncp`, `numero_item`, `fornecedor_cnpj`) | 102 | resultados incluídos até o corte |
| `cmed_apresentacoes` | nacional/cmed_2025_01_apresentacoes.parquet | `registro` (13 dígitos) | 25.549 | apresentações, CAP, ICMS 0%, Convênio 87, embalagem |
| `cmed_precos` | nacional/cmed_2025_01_precos.parquet | (`registro`, `tipo_preco`, `aliquota_icms`) | 941.578 | PF e PMVG por alíquota, aplicabilidade |
| `item_catmat` | padronizacao/item_catmat_candidatos.parquet | (`item`, `catmat`) | 311 | CATMAT por atributos (pré-corte) |
| `item_cmed` | padronizacao/item_cmed_vinculos.parquet | (`item`, `registro`) | 20.369 | vínculo classificado em 5 classes |
| `item_bps_grupos` | padronizacao/item_bps_grupos.parquet | (`item`, `catmat`, `unidade_fornecimento`, `capacidade_descricao`) | 513 | compatibilidade de unidade e capacidade |
| `regras_conversao` | padronizacao/regras_conversao.csv | (`item`, `registro`) | 4.868 | fator, unidades, justificativa, status |

## 3. Relações

```
itens (item) ──< item_catmat (item, catmat) ──< item_bps_grupos (item, catmat, unidade, capacidade) >── bps (catmat, unidade, capacidade)
itens (item) ──< item_cmed (item, registro) >── cmed_apresentacoes (registro) ──< cmed_precos (registro, tipo_preco, aliquota)
itens (item) <── pncp_itens.itens_caso_comparaveis ("1|28|…") ;  pncp_contratacoes ──< pncp_itens ──< pncp_resultados
itens ── historico_proprio (por descrição; sem chave formal) ;  recursos/restricoes/execucao_2024 = contexto do órgão
```

- Órgãos: `comprador_cnpj` (14 dígitos) no BPS e no PNCP; município e UF por campos próprios. Não há correspondência automática entre CNPJ de Município e de Fundo Municipal de Saúde (Etapa 1).
- Contratações: `numero_controle_pncp` é a chave do PNCP. O BPS não tem essa chave; **não há junção BPS × PNCP no nível de transação**.
- Medicamentos: CATMAT (BPS) e registro Anvisa (BPS, CMED) são as chaves de produto. O PNCP não traz CATMAT; o vínculo PNCP × item usa atributos padronizados (doc 13).

## 4. Proveniência e tempo em cada linha

| Campo | Significado |
|---|---|
| `fonte`, `arquivo_origem`, `id_origem`/chave original | origem verificável do registro |
| `data_disponibilidade`, `base_disponibilidade` | quando e por qual evidência o registro estava disponível |
| `classe_temporal` | `disponivel` (único valor admitido no pacote), `posterior`, `indeterminado` |
| `categoria_valor` | tipo de valor monetário (praticado, estimado, homologado, limite regulatório) |
| `flag_*` | marcas de qualidade (não removem registros) |

## 5. Fluxo de construção

`24_bps_historico_temporal.py` (BPS 2020–2026 → classes temporais) → `25_padronizacao_vinculos.py` (atributos, CATMAT, CMED, revisão das 259) → `26_pncp_comparaveis.py` (selecionar → baixar → consolidar) → `27_montar_pacotes.py` (pacotes e manifesto) → `28_verificacoes.py` (testes e relatórios). Módulos: `padroniza.py` (regras, com autotestes) e `consulta_agente.py` (consultas). Dependências novas: `duckdb` 2.0.1 (pedido do enunciado).
