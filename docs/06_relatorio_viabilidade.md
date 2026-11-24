# 06 — Relatório de viabilidade (Etapa 1)

Projeto: Planejamento de Compras de Medicamentos pelo SUS com IA Generativa — SIO/UFPB. Auditoria executada em 22/11/2026.

## 1. Resumo executivo

As bases públicas permitem reconstruir com boa rastreabilidade **o processo de contratação** de órgãos reais da Paraíba (o que foi licitado, em que quantidade, a que preço estimado e homologado, com quais fornecedores) e oferecem **referências de preço** (BPS, resultados de pregões, teto CMED). **Não** permitem conhecer, por medicamento, a necessidade real de abastecimento, o consumo histórico nem o orçamento disponível. Há aproximações públicas: quantidades licitadas, estoque atual (BNAFAR/Hórus) e despesa empenhada/liquidada/paga em material farmacológico (TCE-PB). Com elas o experimento é **viável na classificação B**, com hipóteses explícitas e um caso delimitado. Não é viável na classificação A.

Três achados mudam o desenho esperado:
1. **BPS e Medicamentos Transparentes quase não se cruzam** no nível de transação (5 de 4.205 registros BPS-PB confirmados).
2. **O BPS é pequeno e tem erros graves**: 53.346 registros e 262 compradores em 2025–2026, sem esfera federal, com valores impossíveis (os 100 maiores registros respondem por 88,5% do valor somado).
3. **O MT é rastreável até o PNCP**: o `id` é o `numeroControlePNCP`, e 20 de 20 consultas bateram em órgão e valor.

## 2. Bases efetivamente acessadas

| Base | Estado | Volume obtido |
|---|---|---|
| Medicamentos Transparentes | Processado | 568 de 571 ZIPs CSV (todas as UFs, 2025-01..2026-09, 84,9 MB) + 9 JSON da PB; PB com todas as tabelas, Brasil só cobertura |
| BPS | Processado | 2025 e 2026 integrais (5,5 MB zip; 33,2 MB descompactado) + dicionário PDF |
| PNCP | Consultado / PCA processado | Amostras de compra, itens, resultados, arquivos, contratos; PCA SES-PB 2026 (40 unidades, 2.497 itens) |
| BNAFAR/Hórus (API MS) | Processado (2 municípios) | Campina Grande 2.464 e João Pessoa 1.776 linhas de estoque |
| TCE-PB SAGRES | Processado (1 município) | Salgadinho 2025: 10.130 empenhos; licitações |
| CMED PMVG | Processado | 26.694 apresentações |
| Falhas | — | Download em lote do MT (HTTP 500); Swagger do MT (502); API CKAN do MS (404); 3 arquivos MT inexistentes na fonte (404). As 6 consultas ao PNCP bloqueadas por 429 foram obtidas na nova tentativa. |

## 3. Registros e períodos

- BPS: 37.641 (2025) + 15.705 (2026); compras de 01/01/2025 a 11/11/2026; 23 UFs; PB 4.205 registros, 21 órgãos.
- MT-PB: 1.883 contratações únicas, 9.206 itens, 4.449 itens adjudicados, 272 compradores, 559 fornecedores.
- MT nacional (coletas 2025-01..2026-09): 86.068 contratações únicas e 324.999 itens; SP concentra 32,4%; PB em 11º lugar (2,2%), 4ª do Nordeste. Volume por coleta irregular (picos em 2025-03 e 2025-09).

## 4. Principais variáveis

Produto (CATMAT, registro Anvisa, unidade de fornecimento, princípio ativo), órgão (CNPJ, município, esfera, unidade compradora), quantidade (licitada, adjudicada, comprada), valor (estimado, adjudicado/homologado, praticado, teto CMED), processo (numeroControlePNCP, modalidade, SRP, situação do item), fornecedor (CNPJ), estoque (lote, validade, quantidade) e despesa (empenhado, liquidado, pago). Detalhes em `02_dicionario_dados.md`.

## 5. Qualidade e representatividade

- BPS: campos centrais completos e aritmeticamente consistentes, mas com outliers impossíveis, 306 duplicatas suspeitas, unidades mistas por CATMAT e defasagem de inserção mediana de 111 dias. Cobertura muito parcial: em Salgadinho, o BPS 2025 equivale a ≈ 11% da despesa empenhada em material farmacológico.
- MT: rastreável; contém contratações não medicamentosas (odontológicas, laboratoriais); valores estimados zerados por sigilo (1.782 itens); unidades em texto livre; registros repetidos entre coletas.
- Conclusões valem **só para as compras registradas** nas fontes, não para "todas as compras do SUS".

## 6. Integração

Confirmada: MT↔PNCP (ID), BPS↔CMED (registro Anvisa, 98,0%), MT interno (ocid). Provável/limitada: CATMAT entre BPS, MT e BNAFAR (67–73% de sobreposição de códigos). Não confiável: BPS↔MT/PNCP por transação (0,1% confirmado). Ver `04_integracao_bases.md`.

## 7. Organizações potencialmente adequadas (lista preliminar — sem escolha definitiva)

| Organização | Fontes com dados | Período | Registros aprox. | Dados relevantes | Principais lacunas | Viabilidade preliminar |
|---|---|---|---|---|---|---|
| **Secretaria de Estado da Saúde da Paraíba** (CNPJ 08.778.268/0001-60, João Pessoa) | MT, PNCP (compras, itens, resultados, contratos, PCA), BPS, BNAFAR (unidades estaduais aparecem em estoque) | 2025–2026 | MT 192 contratações; BPS 397 registros (245 CATMAT, 12 meses); PCA 2026: 2.497 itens | Editais com quantidades e homologações; teto agregado de R$ 756,6 mi para material farmacológico no PCA 2026; preços praticados no BPS | Necessidade por medicamento; execução orçamentária estadual não extraída; estoque estadual parcialmente identificado (município "ignorado") | **Média-alta** — o caso mais completo em dados de processo e planejamento agregado |
| **Campina Grande** (Município 08.993.917/0001-46 e FMS 24.513.574/0001-21) | MT, PNCP, BNAFAR, TCE-PB (despesas 2025: 2,1 MB, não baixado) | 2025–2026 | MT 41 contratações; estoque 2.464 linhas em 22 CNES | Estoque atual por lote; despesa municipal detalhada disponível | Ausente no BPS; consumo; dois CNPJs | **Média** — melhor combinação de processo + estoque + orçamento municipal |
| **Salgadinho** (FMS; Município 08.881.666/0001-08) | BPS, TCE-PB, MT | 2025–2026 | BPS 880 registros (16 meses); TCE-PB 92 empenhos farmacológicos; MT 3 contratações | Série de compras + despesa empenhada/liquidada/paga | Município muito pequeno; quase sem editais no MT; BNAFAR não testado (código IBGE não resolvido) | **Média-baixa** — bom para testar restrição orçamentária, fraco em processo |
| **João Pessoa** (SMS) | BNAFAR | posição 18/11/2026 | 1.776 linhas, 5 CNES | Estoque | Ausente no BPS; quase ausente no MT; 76% de lotes vencidos | **Baixa** com os dados vistos |

Evidências: `reports/bps_pb_instituicoes.csv`, `reports/mt_compradores_PB.csv`, `reports/pncp_pca_08778268000160_2026_resumo.csv`, `data/raw/ms_api/`, `reports/tcepb_farmaco_mensal_Salgadinho.csv`.

## 8. Suficiência dos dados para decisões

| Dimensão | Classificação | Justificativa |
|---|---|---|
| 9.1 Objetivo da organização | **Parcialmente suficiente** | O objeto de cada edital documenta uma finalidade concreta de aquisição; não há metas de abastecimento por medicamento |
| 9.2 Necessidades de aquisição | **Parcialmente suficiente (fraca)** | Quantidades licitadas por item (necessidade declarada) e estoque atual; **sem consumo nem demanda prevista**; PCA agregado |
| 9.3 Recursos financeiros | **Parcialmente suficiente** (municípios) / **Não verificado** (SES-PB) | Empenhado/liquidado/pago em material farmacológico (TCE-PB) e valor estimado dos editais; nenhum orçamento por medicamento; execução estadual não extraída |
| 9.4 Condições de aquisição | **Parcialmente suficiente** | Preços históricos, homologados e teto CMED; situação dos itens (homologado, fracassado, deserto); contratos/atas consultáveis no PNCP; **nada sobre disponibilidade atual** |
| 9.5 Eficiência | **Parcialmente suficiente** | É possível calcular depois custo total, custo por unidade compatível (CATMAT + unidade), atendimento de quantidades e consumo de um orçamento definido; economia apenas como diferença contra referência |
| 9.6 Consequências | **Insuficiente** | Prazos, entregas, rupturas e continuidade não são observáveis; só proxies (fracassados/desertos, número de fornecedores, lotes vencidos) |

## 9. Lacunas e riscos

Os 8 riscos solicitados foram **identificados nos dados**; nenhum está resolvido. Os mais graves: ausência de demanda real (1), de orçamento por medicamento (2) e de dados de consequência (6). Detalhes e mitigação em `05_lacunas_informacionais.md`.

## 10. Viabilidade de uma avaliação financeira

Possível **calcular** depois, para um caso delimitado: custo total de um conjunto de itens; custo por unidade compatível; comparação com referências independentes (mediana BPS por CATMAT + unidade e período; resultado homologado real do edital; teto PMVG convertido por embalagem). **Não é possível** demonstrar economia realizada para o SUS, nem efeitos de prazo e abastecimento. Toda "economia" deverá ser apresentada como diferença potencial contra uma referência declarada.

## 11. Classificação final

**B — Viável com complementações e hipóteses explícitas.**

- Não é A: necessidade por medicamento, consumo, orçamento por medicamento e consequências operacionais não existem nas fontes públicas examinadas.
- Não é C: há um núcleo real e verificável (editais com quantidades, homologações rastreáveis ao PNCP, preços de referência, teto regulatório, estoque atual e despesa municipal) suficiente para caracterizar um problema organizacional concreto, desde que as lacunas sejam preenchidas por hipóteses rotuladas ou por dados obtidos via LAI.

## 12. Recomendação para a próxima etapa

1. Escolher o caso entre SES-PB e Campina Grande, priorizando **um edital (ou poucos) com itens de medicamentos já homologados no PNCP**, para haver uma referência real independente do resultado.
2. Tomar o MT/PNCP como espinha dorsal (processo e quantidades), o BPS e a CMED como referências de preço, o BNAFAR como estoque e o TCE-PB/PCA como restrição orçamentária agregada.
3. Registrar como **hipóteses** explícitas: necessidade = quantidade licitada; orçamento = valor estimado do edital ou fração documentada da despesa farmacológica; indisponibilidade = itens fracassados/desertos.
4. Antes do experimento: de-para das unidades do MT, tratamento de outliers do BPS (mediana/IQR por CATMAT + unidade + período) e conversão embalagem→unidade para a CMED nos itens escolhidos.
5. Opcional: pedido via LAI de consumo/estoque histórico ao órgão escolhido.

Esta etapa termina aqui; nenhuma estratégia de compra foi formulada.
