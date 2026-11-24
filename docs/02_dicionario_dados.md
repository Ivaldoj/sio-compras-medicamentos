# 02 — Dicionário dos campos relevantes

Percentuais de preenchimento calculados sobre os arquivos completos (perfil completo de todas as colunas em `reports/perfil_colunas.csv`).
**Status da definição**: *Oficial* = texto do dicionário da fonte; *Não confirmado* = interpretação inferida dos dados, sem documentação.

## 1. BPS (2025 + 2026: 53.346 registros, 34 colunas idênticas nos dois anos)

| Campo | Descrição | Status | Tipo / unidade | Exemplo real | % preench. 2025 / 2026 | Utilidade | Problemas | Relação com outras bases |
|---|---|---|---|---|---|---|---|---|
| `co_seq_bps` | Identificador sequencial do registro | Não confirmado | inteiro | 36908729 | 100 / 100 | Chave técnica | Não descrito | — |
| `ano_compra` | Ano da compra | Oficial | inteiro | 2025 | 100 / 100 | Recorte | Coincide 100% com o ano de `dt_compra` | — |
| `dt_compra` | Data da compra informada | Oficial | data dd/mm/aaaa | 12/06/2025 | 100 / 100 | Dimensão temporal | "Compra" pode ser homologação, ata ou empenho — **não definido** | Data do resultado no PNCP (não equivalente) |
| `dt_insercao` | Data de inserção no BPS | Oficial | data | 21/07/2025 | 100 / 100 | Atualidade | Defasagem mediana de 111 dias | — |
| `validade_compra` | Validade (meses?) | Não confirmado | inteiro | 12 | ver perfil | Vigência de ata | Unidade não documentada | Vigência de ata no PNCP |
| `cnpj_instituicao` | CNPJ da compradora | Oficial | texto 14 díg. | 12403819000189 | 100 / 100 | Identificar órgão | Municípios usam o CNPJ do Fundo Municipal de Saúde | `buyer/id` MT (CNPJ sem zeros à esquerda) |
| `no_instituicao` | Nome da compradora | Oficial | texto | FUNDO MUNICIPAL DE SAUDE DE FARO | 100 / 100 | Rótulo | 56 CNPJs com o mesmo nome "FUNDO MUNICIPAL DE SAUDE"; grafias como "SSFUNDO..." | `buyer/name` |
| `no_municipio`, `sg_uf` | Município e UF | Oficial | texto | FARO / PA | 100 / 100 | Geografia | Sem código IBGE | Localidade em `parties` (MT) |
| `ds_esfera` | Esfera | Não confirmado | MUNICIPAL/ESTADUAL | MUNICIPAL | 100 / 100 | Recorte | Não há registros federais nem privados nos arquivos | Classificação BRA-ESFERA (MT) |
| `co_catmat` | Código BR/CATMAT | Oficial | texto | 271111 | 100 / 100 | **Identificação do produto** | Um CATMAT pode ter várias unidades de fornecimento (250 casos) | `tender/items/classification/id` (MT); `codigo_catmat` BNAFAR (com prefixo BR0) |
| `ds_item` | Descrição CATMAT | Oficial | texto | AMOXICILINA, CONCENTRAÇÃO: 50MG/ML, APRESENTAÇÃO: PÓ PARA SUSPENSÃO ORAL | 100 / 100 | Leitura humana | Texto padronizado por CATMAT, não pela embalagem comprada | Descrição do item (MT/PNCP) |
| `co_pdm`, `no_pdm` | Padrão descritivo de material (princípio ativo) | Não confirmado | texto | 2436 / AMOXICILINA | 100 / 100 | Agrupar por princípio ativo | Agrupa concentrações diferentes — não usar para preço | — |
| `co_classe`, `no_classe` | Classe de material | Não confirmado | texto | 6505 / DROGAS E MEDICAMENTOS | 100 / 100 | **Separar medicamentos** (6505) de outros produtos | 16 classes; 18–21% dos registros não são medicamentos | — |
| `fg_generico` | Genérico S/N | Oficial | S/N | S | ~73 / ~73 (27% nulo no total) | Atributo | Nulo em 14.380 registros | CMED "TIPO DE PRODUTO" |
| `tp_compra` | Tipo de compra | Oficial | ADMINISTRATIVA/JUDICIAL | JUDICIAL | 100 / 100 | Separar demanda judicial | Dicionário cita "emergencial, regular", valores reais são outros | Programa "JUDICIALIZAÇÃO" (BNAFAR) |
| `modalidade` | Modalidade | Oficial | texto | Pregão | 100 / 100 | Contexto | "Registro de Preços" tratado como modalidade | Modalidade PNCP |
| `un_fornecimento` | Unidade de fornecimento | Oficial | texto | COMPRIMIDO | ~100 | **Base do preço unitário** | Mesmo CATMAT com AMPOLA e FRASCO etc. | `unit/name` (MT, texto livre) |
| `vl_capacidade`, `un_medida_capacidade`, `sg_unidade_medida` | Capacidade da unidade e sua medida | Oficial (parcial) | número / texto | 6000.0 / FRASCO 60,00 ML / ML | `sg_unidade_medida` nulo em 63% | Converter volume | Nomes de coluna não batem com o dicionário; `vl_capacidade` parece multiplicado (6000 para 60 ml) — **não confirmado** | Apresentação CMED |
| `qt_medicamento` | Quantidade comprada | Oficial | número (unidades de fornecimento) | 300 | 100 / 100 | Volume | Unidade = `un_fornecimento` | `quantity` (MT/PNCP) |
| `vl_preco_unitario` | Preço unitário pago | Oficial | R$ por unidade de fornecimento | 10.74 | 100 / 100 | **Referência de preço** | Valores impossíveis (ex.: R$ 294.400 por cápsula) | `unit/value/amount` (MT); PMVG (CMED, por embalagem) |
| `vl_preco_total` | Unitário × quantidade | Oficial | R$ | 3222.0 | 100 / 100 | Valor | Fórmula confere em 100% dos registros | Valor homologado do item (PNCP) |
| `cnpj_fornecedor`, `no_fornecedor` | Fornecedor | Oficial | texto | 04389760000193 | ~100 | Mercado fornecedor | — | `awards/suppliers/id` (MT); credor (TCE-PB) |
| `cnpj_fabricante`, `no_fabricante` | Fabricante | Oficial | texto | 73856593000166 | ver perfil | Mercado | — | CNPJ/LABORATÓRIO (CMED) |
| `registro_anvisa` | Registro Anvisa (13 dígitos) | Oficial ("Código CMED") | texto | 1256801560024 | 73% no total; 89,7% em medicamentos | **Chave para CMED** | — | `REGISTRO` (CMED): 98,0% de correspondência |
| `nu_processo_compra`, `nu_ata` | Nº do processo e da ata | Não confirmado | texto livre | 0720257001 / 027/2024 | 100 / 96,7 | Rastrear o processo | Formatos heterogêneos; não traz nº de controle PNCP | `tender/id` (MT) — compatível em poucos casos |
| `ds_observacao` | Observação livre | Não confirmado | texto | "AQUISIÇÃO DE MEDICAMENTOS PROCESSO: 2735 EDITAL…" | ~40 | Contexto | Nenhuma ocorrência de "PNCP" | — |

## 2. Medicamentos Transparentes (OCDS achatado; PB, 21 coletas)

Nomes de coluna simplificados (`awards/0/x` → `awards/x`). Tabelas ligadas por `ocid`. Fonte de definição: padrão OCDS (https://standard.open-contracting.org) — o significado OCDS é oficial; o mapeamento para o PNCP feito pela Transparência Brasil é **não confirmado** salvo indicação.

| Tabela.campo | Descrição | Status | Tipo / unidade | Exemplo real | % preench. (PB) | Utilidade | Problemas | Relações |
|---|---|---|---|---|---|---|---|---|
| todas.`ocid` | ID do processo de contratação | Oficial OCDS | texto | ocds-ye9ov3-394452000103_2026_15134 | 100 | Chave entre tabelas | Repetido entre coletas (391 ocids em >1 coleta) | — |
| todas.`id` | ID do release | Oficial OCDS | texto | 00394452000103-1-015134/2026 | 100 | **= numeroControlePNCP** (20/20 confirmados) | — | PNCP |
| releases.`date` | Data do release | Oficial OCDS | ISO 8601 | 2026-07-30T07:03:00Z | 100 | Data de publicação/atualização | Coincide com o mês de coleta só em 49,5% | `dataPublicacaoPncp` |
| releases.`tag` | Estágios | Oficial OCDS | texto | tender;award | 100 | — | Sempre "tender;award" | — |
| releases.`buyer/id`, `buyer/name` | Comprador | Oficial OCDS | `BR-CNPJ-<cnpj sem zeros à esquerda>` | BR-CNPJ-8778268000160 | 100 | Órgão | Precisa de `zfill(14)` | `cnpj_instituicao` (BPS) |
| releases.`tender/value/amount` | Valor estimado da contratação | Oficial OCDS | R$ | 430617.86 | 100 | Tamanho da compra | Muda entre coletas; outlier EBSERH (CNPJ …0143) soma R$ 28,9 bi em 41 contratações | `valorTotalEstimado` PNCP (20/20 iguais) |
| releases.`tender/procurementMethodDetails` | Modalidade, modo de disputa, **SRP** | Não confirmado (texto concatenado) | texto | "modalidadeNome: Pregão - Eletrônico; … srp: True" | 100 | Modalidade e registro de preços | Precisa de parsing | Campos PNCP |
| releases.`tender/tenderPeriod/*` | Período de propostas | Oficial OCDS | datas | 2026-07-30 / 2026-08-11 | alto | Prazos | — | PNCP |
| ten_items.`tender/items/classification/id` | Código CATMAT | Oficial OCDS + scheme=CATMAT | texto | 272913 | 100 | **Produto** | — | `co_catmat` BPS |
| ten_items.`quantity` | Quantidade licitada | Oficial OCDS | unidades de `unit/name` | 89 | 100 | **Necessidade declarada no edital** | Quantidade planejada, não comprada | `quantidade` PNCP |
| ten_items.`unit/value/amount` | Valor unitário estimado | Oficial OCDS | R$ | 25.93 | 100 | Preço de referência do órgão | **0 em 1.782 itens** (orçamento sigiloso) | `valorUnitarioEstimado` PNCP |
| ten_items.`unit/name` | Unidade | Oficial OCDS | texto livre | Pote 12 G | 100 | — | **330 grafias** (Comprimido, COMPRIMIDO, Comp.) | `un_fornecimento` BPS |
| ten_items.`dosageForm`, `administrationRoute` | Forma farmacêutica, via | Extensão OCDS | texto | Gel Tópico | 17,5 / 38,4 | Equivalência | Baixo preenchimento | — |
| ten_ite_activeIngredients.`name`, `strength/value` | Princípio ativo e concentração | Extensão OCDS | texto/número | Benzocaína / 0.2 | ver perfil | Equivalência | Unidade da concentração vazia no exemplo | — |
| ten_lots.`statusDetails` | Situação do item | Não confirmado (mapeado do PNCP) | texto | Homologado | 100 | **Resultado** | Em andamento 4.433; Homologado 3.910; Fracassado 568; Deserto 208; Anulado/Revogado/Cancelado 87 | `situacaoCompraItemNome` PNCP |
| ten_lots.`lotsDetails/confidentialBudget` | Orçamento sigiloso | Não confirmado | bool | True | 19 | Explica valor 0 | — | `orcamentoSigiloso` PNCP |
| awa_items.`quantity`, `unit/value/amount` | Quantidade e valor unitário adjudicados | Oficial OCDS | unidades / R$ | 89 / 7.51 | 100 (dos adjudicados) | **Preço resultante** | Só 48,0% dos itens licitados têm adjudicação | `quantidadeHomologada`, `valorUnitarioHomologado` PNCP |
| awa_items.`status` | Situação do item adjudicado | Não confirmado | Informado/Cancelado | Informado | 100 | — | — | — |
| awa_suppliers.`suppliers/id` | Fornecedor | Oficial OCDS | `BR-CNPJ-…` | BR-CNPJ-11511020000143 | 100 | Mercado | — | `cnpj_fornecedor` BPS |
| par_det_classifications (scheme BRA-ESFERA) | Esfera do órgão | Não confirmado | texto | Federal | 100 | Recorte | — | `ds_esfera` BPS |
| par_additionalIdentifiers | Unidade compradora (UASG) | Não confirmado | código + nome | 160139 / HOSPITAL DE GUARNICAO DE JOAO PESSOA | — | Unidade real dentro do CNPJ | — | `codigoUnidade` PNCP |

**Distinção de valores**: estimado (`tender/value`, `tender/items/unit/value`), homologado (status do lote + `awards`), adjudicado (`awards/items`). **Contratado** (contrato/empenho) **não está** no MT — exige `/consulta/v1/contratos` do PNCP ou empenhos do TCE-PB.

## 3. Fontes complementares (campos usados)

| Fonte.campo | Descrição | Status | Utilidade | Problema |
|---|---|---|---|---|
| PNCP PCA.`quantidade`, `valorUnitario`, `valorTotal`, `valorOrcamentoExercicio`, `dataDesejada`, `classificacaoSuperiorNome`, `codigoItem`, `nomeUnidade` | Itens do Plano de Contratações Anual | Oficial (API PNCP) | Planejamento declarado | Na SES-PB 2026, medicamentos aparecem numa linha agregada `33903009 MATERIAL FARMACOLOGICO` (93.593.844 "un" × R$ 8,0839) |
| BNAFAR.`codigo_catmat` | `BR0` + CATMAT + sufixo (ex. `BR0267140U0042`) | Sufixo **não confirmado** | Produto | — |
| BNAFAR.`quantidade_estoque`, `numero_lote`, `data_validade`, `data_posicao_estoque`, `codigo_cnes`, `descricao_programa_saude` | Estoque por lote | Oficial (descrição da API) | **Estoque atual** | Muitos lotes já vencidos na data de posição (28% CG, 76% JP) |
| TCE-PB.`valor_empenhado`, `valor_liquidado`, `valor_pago` | Estágios da despesa | Oficial (SAGRES) | **Restrição orçamentária realizada** | Decimal com vírgula; subelemento não identifica o medicamento |
| TCE-PB.`codigo_subelemento_exibicao` | Nome do subelemento (ex. "MATERIAL FARMACOLÓGICO") | Não confirmado (nome da coluna engana: traz texto) | Filtrar medicamentos | — |
| CMED.`REGISTRO`, `APRESENTAÇÃO`, `PMVG <alíquota>`, `PF <alíquota>`, `CAP`, `RESTRIÇÃO HOSPITALAR` | Teto de preço ao governo | Oficial (CMED) | Teto regulatório | Preço por **embalagem**; lista vigente, não histórica; decimal com vírgula |

**Campos com dados pessoais**: BNAFAR traz telefone/e-mail de estabelecimentos; TCE-PB traz credores pessoa física (CPF) e nomes. Não foram usados nem reproduzidos nos relatórios.
