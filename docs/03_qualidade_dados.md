# 03 — Análise exploratória e qualidade dos dados

Todos os números abaixo foram **calculados** pelos scripts indicados sobre os arquivos completos citados (salvo quando dito "amostra"). Saídas brutas: `reports/*_stdout.txt` e CSVs em `reports/`.

## 1. BPS 2025–2026 (`scripts/04_profile_bps.py`, `05_bps_checks.py`)

### 1.1 Cobertura

| Indicador | 2025 | 2026 |
|---|---|---|
| Registros | 37.641 | 15.705 |
| Instituições (CNPJ) | 229 | 137 |
| UFs | 23 | 20 |
| CATMAT distintos | 5.362 | 3.976 |
| % classe 6505 (medicamentos) | 81,7% | 79,4% |
| Datas de compra | 01/01/2025–30/12/2025 | 02/01/2026–11/11/2026 |

- Total 2025+2026: **53.346 registros, 262 instituições (242 municipais, 20 estaduais), 6.345 CATMAT, 1.428 PDM**. **Nenhum registro federal** e nenhuma compra privada, apesar de o dicionário mencionar ambas.
- UFs **ausentes**: AM, AP, DF, RR. Concentração: RS 8.641, RO 8.228, PR 7.493, SP 5.397, SE 4.672, **PB 4.205** (6º lugar), MA 36, RN 30.
- Registros por mês caem fortemente no fim de 2026 (ago 595, set 934, out 313, nov 43) — efeito da **defasagem de inserção** (mediana 111 dias; p75 233; p90 354; máx. 644), não de queda real de compras.
- Esfera: municipal 44.540, estadual 8.806. Tipo: administrativa 49.979, **judicial 3.367**. Modalidade: Pregão 41.067; "Registro de Preços" 10.470; Dispensa 1.759; Inexigibilidade 26; Leilão 23 (provável erro de classificação); Diálogo Competitivo 1.
- **Representatividade**: 262 instituições num país com 5.570 municípios e 27 UFs indicam que o arquivo aberto contém uma fração pequena dos compradores do SUS. Teste concreto em Salgadinho/PB (seção 4): o BPS registra R$ 78.155,58 em 2025, enquanto o TCE-PB mostra R$ 688.897,13 empenhados em material farmacológico no mesmo ano (≈ 11%; os conceitos não são idênticos — ver seção 4).

### 1.2 BPS na Paraíba

21 instituições, 4.205 registros, 1.048 CATMAT, 97,1% medicamentos. Concentração extrema: os 3 maiores (FMS Salgadinho 880; FMS Itaporanga 458; SES-PB 397) somam 41%. Vários órgãos têm 1 único mês (Pedra Branca, Emas, Congo…). Registros por mês: 762 (mar/25), 892 (abr/25), 729 (jun/25) contra 1 (jun/26) e 0 (ago/26, out/26). **João Pessoa e Campina Grande (prefeituras/FMS) não aparecem.** Lista completa: `reports/bps_pb_instituicoes.csv`.

### 1.3 Dados financeiros

| Indicador | Valor |
|---|---|
| Preço unitário — mínimo / p1 / p25 / **mediana** / p75 / p99 / máximo | R$ 0,003 / 0,03 / 0,36 / **2,07** / 8,02 / 2.721,70 / 1.149.000,00 |
| Valor total — mediana por registro | R$ 4.200,00 (2025); R$ 6.110,22 (2026) |
| Soma de `vl_preco_total` | R$ 51,0 bi (2025); R$ 24,2 bi (2026) — **não utilizável** |
| Participação dos 100 maiores registros na soma | **88,5%** |
| `vl_preco_total` = unitário × quantidade (±1%) | 53.346 de 53.346 |
| Quantidade ≤ 0 ou preço ≤ 0 | 0 |

Exemplos de valores **impossíveis ou altamente suspeitos** (registros reais):

| UF | Instituição | Produto (PDM) | Unidade | Qtde | Preço unit. (R$) | Total (R$) |
|---|---|---|---|---|---|---|
| PR | SES | PENICILAMINA | CÁPSULA | 77.500 | 294.400,00 | 22,8 bi |
| SP | SES | OCTREOTIDA | AMPOLA | 28.060 | 520.000,00 | 14,6 bi |
| PR | Fazenda Rio Grande | AMOXICILINA | CÁPSULA | 261.600 | 51.038,16 | 13,4 bi |
| RS | CIS-CAI | CARBONATO DE CÁLCIO | COMPRIMIDO | 699 | 1.149.000,00 | 803 mi |

Hipótese (não confirmada): valor total ou preço de embalagem digitado como preço unitário, ou separador decimal perdido. **Consequência**: somas e médias do BPS sem tratamento de outliers são inválidas; medianas e quartis por CATMAT + unidade são o mínimo aceitável.

**Dispersão por produto comparável**: nos 408 grupos CATMAT + unidade de fornecimento com n ≥ 30, a razão máximo/mínimo tem **mediana de 67** (`reports/bps_dispersao_preco_catmat_unidade.csv`). Exemplo: soro fisiológico 0,9% (CATMAT 268236) — mediana R$ 0,21 (ampola, n=15), R$ 3,89 (bolsa, n=111), R$ 3,56 (frasco, n=176), com máximos de R$ 59,49 e R$ 99,50. A variação mistura volume (capacidade), quantidade, região, data e erro; **não pode ser lida como sobrepreço**.

### 1.4 Qualidade

| Dimensão | Achado |
|---|---|
| Completude | `sg_unidade_medida` nulo em 63%; `fg_generico` nulo em 27%; `registro_anvisa` 73% (89,7% em medicamentos); `nu_ata` 96,7%; `nu_processo_compra` 100%; conversões numéricas e de data sem falhas |
| Consistência | Total = unitário × quantidade em 100%; `ano_compra` coerente com a data em 100%; 250 CATMAT com mais de uma unidade de fornecimento (ex.: 267161 AMPOLA/FRASCO; 267504 CÁPSULA/COMPRIMIDO); dicionário descreve "Tipo de Compra" como emergencial/regular, mas os valores são ADMINISTRATIVA/JUDICIAL; nomes inconsistentes ("SSFUNDO MUNICIPAL…") |
| Duplicidade | `co_seq_bps` único. **306** registros repetem a chave de negócio (CNPJ, data, CATMAT, fornecedor, quantidade, preço, processo); **74** são idênticos em todos os campos exceto `co_seq_bps`/`dt_insercao`. Exemplo: SES-SP, dapagliflozina, 90.487.070 comprimidos a R$ 2,21 em 21/05/2025 e de novo em 05/06/2025 (R$ 199,98 mi cada) — pode ser compra parcelada legítima ou duplicação; **não decidível com os dados**. Critério proposto: só remover quando idênticos em todos os campos de negócio e inseridos no mesmo dia; os demais ficam marcados. |
| Atualidade | Inserção 14/03/2025–19/11/2026; meses recentes subnotificados por defasagem |
| Rastreabilidade | Sem nº de controle PNCP; `nu_processo_compra` livre; `ds_observacao` nunca cita PNCP |
| Natureza do registro | Dicionário: "valor efetivamente negociado". Não informa se a "compra" é ata, contrato, empenho ou entrega — **não verificado** |

## 2. Medicamentos Transparentes (`scripts/06…08`)

### 2.1 PB, coletas 2025-01 a 2026-09

| Indicador | Valor |
|---|---|
| Linhas em `releases` / ocids únicos | 2.367 / **1.883** |
| ocids em mais de uma coleta | 391 (máx. 5 coletas) |
| Compradores (CNPJ) | 272 — municipal 1.196, estadual 475, federal 145, "não se aplica" 66, distrital 1 contratações |
| Itens licitados únicos (ocid+item) | 9.206 — 100% com CATMAT; 1.281 CATMAT distintos |
| Itens adjudicados únicos | 4.449 (Informado 4.403; Cancelado 46) |
| Fornecedores | 559 |
| Situação dos itens | Em andamento 4.433; Homologado 3.910; Fracassado 568; Deserto 208; Anulado/Revogado/Cancelado 87 |
| Itens licitados com adjudicação | 48,0% |
| Razão unitário adjudicado / estimado (n=4.084) | p5 0,27; p25 0,57; **mediana 0,80**; p75 0,98; p95 1,00; 56 acima de 1; 48 fora de [0,1; 10] |
| Quantidade adjudicada ≠ licitada | 0,1% |
| Valor unitário estimado = 0 | 1.782 itens (1.755 lotes com orçamento sigiloso) |
| `unit/name` distintos | 330 (Comprimido 1.838; COMPRIMIDO 168; Comp. 167…) |
| Forma farmacêutica / via preenchidas | 17,5% / 38,4% |
| Modalidade (linhas) | Pregão eletrônico 1.818; Dispensa 476; Pregão presencial 48; Inexigibilidade 13; Credenciamento 12; SRP=True 1.056 |
| Objeto cita "medicament" | 1.039 de 1.883; cita "odontol" 141, "laborat" 87, "material" 348 → **o recorte inclui contratações mistas e não medicamentosas** |
| Maiores compradores | SES-PB 192 contratações; Sec. Est. Administração 132; Fundação Paraibana de Gestão em Saúde 60; FMS (CNPJ 08715618000140) 57; EBSERH (…0305) 46 |

**Datas**: `date` do release vai de 17/05/2023 a 30/09/2026; só 49,5% coincidem com o mês da coleta. A coleta indica quando a Transparência Brasil capturou o registro, não quando a compra ocorreu. Há datas de período de propostas (`tenderPeriod`), de adjudicação (`awards/date`) e de release; **homologação, contrato e vigência não estão** no CSV.

**Duplicidade entre coletas**: entre coletas do mesmo ocid mudam título, descrição, valor estimado, detalhes da modalidade e prazos. Regra adotada nos scripts: deduplicar por `ocid` (e `ocid`+item) mantendo uma ocorrência; para valores, usar a coleta mais recente.

**Valores suspeitos**: EBSERH (CNPJ 15126437000143) soma R$ 28,9 bi de valor estimado em 41 contratações em PB — incompatível com o porte; não investigado item a item.

### 2.2 Comparação nacional (coletas 2025-01 a 2026-09, todas as UFs — `scripts/08_mt_cobertura_nacional.py`)

| Indicador | Valor |
|---|---|
| Linhas em `releases` / contratações únicas (ocid) | 106.784 / **86.068** |
| Itens licitados únicos | 324.999 |
| ocids em mais de uma coleta | 17.296 (20,1%); máximo 7 coletas |
| ocids em arquivos de mais de uma UF | 0 |
| UFs com as 21 coletas | 27 (o código `EX` tem uma única contratação, em 2026-09) |

| UF | Contratações | % | Compradores | Itens |
|---|---|---|---|---|
| SP | 27.878 | 32,4 | 809 | 99.669 |
| MG | 8.307 | 9,7 | 1.049 | 31.318 |
| RS | 6.731 | 7,8 | 515 | 24.749 |
| PR | 5.580 | 6,5 | 571 | 22.698 |
| RJ | 5.537 | 6,4 | 245 | 20.136 |
| … | | | | |
| PE | 2.164 | 2,5 | 360 | 9.052 |
| **PB** | **1.883** | **2,2** | **272** | **9.206** |
| RN | 1.675 | 1,9 | 254 | 7.680 |
| … | | | | |
| AC / AP | 169 / 131 | 0,2 / 0,15 | 27 / 39 | 747 / 777 |

A PB é a **11ª** em contratações (era 10ª no recorte jan–mar/2025, `reports/mt_cobertura_uf_2025T1.csv`); 4ª do Nordeste, atrás de BA (3.528), CE (2.847) e PE (2.164). Tabela completa: `reports/mt_cobertura_uf.csv`; matriz UF × coleta: `reports/mt_cobertura_uf_mes.csv`.

**Irregularidade temporal**: as coletas 2025-03 (11.039 contratações) e 2025-09 (10.615) têm cerca do dobro das vizinhas (≈ 4.300–5.700); 2025-01 (2.970) e 2026-01 (2.532) são as menores. O padrão aparece também na PB (236 e 211 contra ≈ 100). Causa não documentada (provável recoleta ou carga acumulada). Consequência: **contagens por mês de coleta não medem a atividade de compra do mês**; para séries temporais, usar datas próprias da contratação (`tenderPeriod`, `awards/date`) e deduplicar por ocid.

## 3. PNCP — PCA da SES-PB 2026 (`scripts/10`, `11`)

40 PCAs (um por unidade: maternidades, hospitais regionais, hemocentro…), 2.497 itens, R$ 9,22 bi. Catálogo "Outros" (não CATMAT) em 100% dos itens. Serviço 2.276 / Material 221. Medicamentos: **uma única linha** "MATERIAL FARMACOLOGICO" (código 33903009, natureza de despesa) de ≈ R$ 756,6 mi, quantidade 93.593.844 "un" a R$ 8,0839, data desejada 31/12/2027. Os demais itens "farmacológicos" são material odontológico, locações e sedação. **Conclusão**: o PCA dá um teto agregado de planejamento, não a necessidade por medicamento.

## 4. TCE-PB — despesas de Salgadinho 2025 (`scripts/12`)

10.130 empenhos. Material farmacológico: **92 empenhos, R$ 688.897,13 empenhados, R$ 688.897,13 liquidados, R$ 675.273,22 pagos**, todos na função Saúde; 73 empenhos com fonte "Transferências Fundo a Fundo… Bloco de Manutenção". Série mensal fev–dez em `reports/tcepb_farmaco_mensal_Salgadinho.csv`. Comparação com BPS (mesmo município, 2025): 459 registros, R$ 78.155,58; 3 dos 5 fornecedores do BPS são credores farmacológicos no TCE-PB. Ressalvas: empenho ≠ compra (pode cobrir entregas de atas antigas); o BPS de Salgadinho usa o CNPJ do FMS e o TCE-PB a unidade gestora "Prefeitura"; a razão (~11%) é indicativa, não uma medida de cobertura.

## 5. BNAFAR/Hórus (`scripts/16`)

| Município | Linhas | CNES | CATMAT | Data de posição | Lotes vencidos na data | CATMAT presentes no BPS |
|---|---|---|---|---|---|---|
| Campina Grande (250400) | 2.464 | 22 | 634 | 18/11/2026 | 694 (28%) | 66,9% |
| João Pessoa (250750) | 1.776 | 5 | 736 | 17–18/11/2026 | 1.349 (76%) | 68,9% |

Programas mais frequentes: Assistência Farmacêutica, Judicialização, Antimicrobianos, Saúde Mental. A alta fração de lotes vencidos indica registros não baixados ou estoque realmente vencido — **não decidível**. Apenas 5 CNES em João Pessoa sugerem cobertura parcial dos estabelecimentos. Sem histórico pela API.

## 6. CMED PMVG (`scripts/13`)

26.694 apresentações, 74 colunas, publicada em 09/11/2026. 38.776 registros BPS de medicamentos têm registro Anvisa; **98,0%** encontram a apresentação exata na CMED (98,7% pelo produto). O preço CMED é por embalagem e por alíquota de ICMS; o BPS, por unidade de fornecimento — a comparação exige conversão documentada (não feita).

## 7. Síntese de qualidade por dimensão

| Dimensão | BPS | Medicamentos Transparentes | PNCP | BNAFAR | TCE-PB |
|---|---|---|---|---|---|
| Completude | Boa nos campos centrais; ruim em capacidade/medida | Boa em CATMAT/quantidade; ruim em forma/via; valor 0 com sigilo | Boa | Boa nos campos de estoque | Boa |
| Consistência | Outliers graves; unidades mistas | 330 grafias de unidade; valores estimados extremos | — | Lotes vencidos | — |
| Duplicidade | 306 suspeitas | ocid repetido entre coletas | — | — | — |
| Atualidade | Defasagem mediana 111 dias | Coleta mensal irregular (picos em 2025-03 e 2025-09); dados até set/2026 | Tempo real | Posição diária, sem histórico | Diária (2026 atualizado em 22/11/2026) |
| Rastreabilidade | Fraca (sem ID PNCP) | **Forte** (ID PNCP) | Origem | CNES + lote | Nº do empenho e licitação |
| Representatividade | Fração pequena dos compradores | Só o que está no PNCP com itens de medicamento | Lei 14.133 (obrigatório) | Quem usa Hórus/BNAFAR | 223 municípios PB |
