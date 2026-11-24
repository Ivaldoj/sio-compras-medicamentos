# 08 — Dossiê organizacional: Santa Luzia/PB

Legenda de status: **[C]** comprovado em documento ou registro oficial · **[K]** calculado pelos scripts a partir de dados oficiais · **[I]** inferido (não confirmado) · **[A]** ausente. Códigos de evidência (E-nn) remetem a `09_evidencias_e_lacunas.md`.

Marca temporal: **[PRÉ]** disponível até a data de decisão (29/01/2025) · **[PÓS]** posterior (reservado à avaliação; não entregar ao agente decisor).

## 1. Organização e unidade responsável

| Atributo | Valor | Status | Evidência |
|---|---|---|---|
| Órgão contratante | Prefeitura Municipal de Santa Luzia — CNPJ 09.090.689/0001-67; unidade PNCP 2039; IBGE 2513406 | [C] [PRÉ] | E-01 |
| Unidade orçamentária da saúde | Secretaria Municipal de Saúde (02.030) e Fundo Municipal de Saúde (02.090) | [C] [PRÉ] | E-02 |
| CNPJ do FMS (usado no BPS) | 10.425.754/0001-47 | [C] | E-12 |
| Unidade demandante | Secretaria Municipal de Saúde — Assistência Farmacêutica / Farmácia Básica ("setor demandante" no TR) | [C] [PRÉ] | E-02 |
| População | 15.387 (estimativa 2024) e 15.418 (2025) | [C] | E-15 |
| Porte da compra | Gasto com material farmacológico de R$ 1,95 mi em 2024 | [K] [PRÉ] | E-10 |

## 2. Período de análise

- **Data de decisão (estudo retrospectivo): 29/01/2025**, véspera da publicação do PE 04/2025 no PNCP (30/01/2025 07:34). [C]
- **Horizonte da decisão**: 12 meses de abastecimento, correspondendo à vigência contratual prevista no TR (no caso real, 12/03/2025–12/03/2026). [C]
- **Janela de avaliação [PÓS]**: 30/01/2025 a 31/08/2026 (último empenho no TCE-PB: 31/08/2026). [K]
- **Histórico [PRÉ]**: 2024 (pregões 01/2024 e 12/2024; despesa TCE-PB 2024; BPS inserido até 29/01/2025).

## 3. Medicamentos e especificações [PRÉ]

- Objeto: "fornecimento parcelado de medicamentos diversos destinados a Assistência Farmacêutica Básica, Assistência Farmacêutica Especializada e medicamentos que não fazem parte do RENAME". [C] E-02
- **334 itens**, cada um com descrição, concentração, forma e unidade. Unidades: comprimido 159, frasco 77, ampola 59, cápsula 16, bisnaga 14, unidade 4, seringa 3, sachê 1, envelope 1. [C] E-03
- CATMAT: **não informado** no PNCP [A]. Identificado para 299 itens pelo registro BPS do mesmo contrato (fornecedor + preço + quantidade), com 7 chaves ambíguas no BPS [K]. Como esse vínculo usa uma fonte posterior (BPS inserido em 22/12/2025), serve apenas para identificar o produto, nunca para revelar preço.
- Lista completa: `data/processed/caso_santa_luzia/pre_decisao/itens_necessidade_e_referencias.csv`.

## 4. Quantidades necessárias [PRÉ]

| Indicador | Valor | Status |
|---|---|---|
| Base declarada | "As estimativas foram baseadas na utilização anual dos anos anteriores" (ETP, item IV) | [C] E-02 |
| Consumo por item que sustenta a base | **não publicado** | [A] |
| Itens com descrição idêntica no plano anterior (PE 01/2024, 349 itens) | 143; desses, 64 com a mesma quantidade, 24 menores e 55 maiores (mediana da razão 1,00) | [K] E-04 |
| Maiores itens por valor estimado | Insulina NPH 100 UI/mL, 6.000 un × R$ 193,02 = R$ 1.158.120 (23,4%); Insulina Regular, 1.200 × R$ 147,36; Amoxicilina susp. 5.000 fr × R$ 29,90; os 10 maiores somam 39,9% | [K] E-03 |

## 5. Recursos financeiros [PRÉ]

| Indicador | Valor | Status |
|---|---|---|
| Estimativa da contratação (soma dos itens) | **R$ 4.952.438,00** | [C] E-02, E-03 |
| Preços unitários estimados | Sigilosos para licitantes (art. 18, §1º, VI, Lei 14.133); conhecidos pelo órgão | [C] E-02 |
| Dotações | 02.030 SMS — 10.301.2016.2018; 02.090 FMS — 10.301.1006.2061 (Manutenção dos Recursos do SUS), 10.301.1006.2067 (Manutenção da Farmácia Básica), 10.302.1008.2069 (SAMU); elementos 3390.30 (material de consumo) e 3390.32 (distribuição gratuita); fontes 1.500.1002, 1.500.0000, 1.600.0000 | [C] E-02 |
| Valor da dotação disponível | **não informado** no edital | [A] |
| Despesa com material farmacológico em 2024 (TCE-PB) | Empenhado e liquidado R$ 1.953.288,72; pago R$ 1.876.052,11 (248 empenhos) | [K] E-10 |
| Por licitação em 2024 | PE 12/2024 (desconto CMED) R$ 1.223.231,57; PE 01/2024 R$ 656.016,25; sem licitação R$ 73.830,90; PE 03/2024 R$ 210 | [K] E-10 |
| Fontes de recurso (2024–2026) | Fundo a Fundo SUS federal (Bloco de Manutenção), recursos não vinculados de impostos, Fundo a Fundo estadual | [K] E-10 |

A estimativa da compra (R$ 4,95 mi) equivale a **2,5 vezes** a despesa farmacológica total de 2024 [K]. O dado era conhecido na data de decisão.

## 6. Contratos, atas e instrumentos

| Instrumento | Situação na data de decisão | Status |
|---|---|---|
| PE 12/2024 — "maior percentual de desconto" sobre a tabela CMED (éticos 18,01%; genéricos 60,11%; similares 51,01%), fornecedor único 07.839.945/0001-40, homologado R$ 690.370 | Vigente na prática: recebeu empenhos em 2024 (R$ 1,22 mi), 2025 (R$ 866 mil) e 2026 (R$ 625 mil). Vigência formal **não verificada**; execução acima do homologado, causa **não verificada** | [C]/[K]/[I] E-05, E-10 |
| PE 01/2024 (349 itens) | Homologado em 01/04/2024 (TCE-PB, 12 vencedores); no PNCP aparece "em andamento", com 4 resultados e valor estimado zerado — **registro incompleto** | [C] E-04 |
| Atas de registro de preços próprias | Nenhuma (os pregões não são SRP) | [C] E-01 |
| Atas de outros órgãos disponíveis para adesão | **Não verificado** | [A] |
| PCA municipal no PNCP (2025 e 2026) | Ausente, embora o ETP afirme alinhamento ao "Planejamento das Contratações Públicas Municipais" | [C]/[A] E-11 |

## 7. Prazos, condições e restrições [PRÉ]

| Restrição | Texto ou valor | Tipo | Evidência |
|---|---|---|---|
| Registro Anvisa | Exigido, salvo dispensa legal | Legal | E-02 (ETP III; TR) |
| Validade mínima | ≥ 75% da vida útil ou > 365 dias (orientação do painel de medicamentos do TCE-PB) | Regulatória/operacional | E-02 (ETP III; TR 4.9) |
| Entrega | Até 5 dias úteis a partir do pedido, "tendo-se em vista a administração não possuir local adequado para armazenamento" | **Operacional** | E-02 (TR 8.4) |
| Local | Endereço da Secretaria Municipal de Saúde | Operacional | E-02 |
| Pagamento | Até 30 dias após a liquidação | Contratual | E-02 (TR, cláusula de pagamento) |
| Reajuste | Preços fixos por 12 meses a partir do orçamento estimado; correção anual mediante requerimento | Contratual | E-02 (TR 11) |
| Garantia de execução | 5% do valor inicial (art. 96, Lei 14.133) | Escolha do órgão dentro da lei | E-02 (TR 12.1) |
| Amostras | Podem ser exigidas | Procedimento | E-02 (edital 8.5.3) |
| Critério | Menor preço por item; modo de disputa aberto | Escolha do órgão | E-02 |
| Sanções | Advertência, multa, impedimento, inidoneidade (Lei 14.133) | Legal | E-02 (TR, sanções) |
| Base legal | Lei 14.133/2021, art. 28, I (pregão) | Legal | E-01 |

Inconsistência: o edital declara preços unitários sigilosos, mas o PNCP registra a compra como "Compra sem sigilo" e publica os preços estimados por item. [C]

## 8. Histórico de aquisições e preços comparáveis [PRÉ]

| Fonte | Cobertura para os 334 itens | Status |
|---|---|---|
| BPS (qualquer UF), inserido até 29/01/2025 (7.347 registros, compras de jan a out/2024) | 285 itens com ≥ 1 preço (84,6% do valor estimado); 225 com ≥ 5; 210 com preço da PB | [K] E-06 |
| CMED PF/PMVG "publicada em 06/01/2025" (arquivo de 07/01/2025; 25.549 apresentações; CAP 21,53%) | 259 itens (79,7% do valor estimado) ligados a ≥ 1 apresentação via registros Anvisa do BPS inseridos até 29/01/2025 (mediana de 3 apresentações por item). Correspondência **provável**: a apresentação pode diferir da pedida (ex.: insulina pedida em 3 mL com sistema de aplicação × frasco-ampola de 10 mL na CMED). Preço por embalagem, sem conversão | [C]/[K] E-07 |
| Resultados do PE 01/2024 no PNCP | Incompletos (4 de 349) | [C] E-04 |
| Painel "Preço de Referência" TCE-PB | Só os últimos 12 meses a partir da consulta, portanto não reconstrói jan/2025 | [C] E-14 |
| Lista estadual de medicamentos em desabastecimento (CEDMEX, 13/09/2024) | **Não obtida**: o portal estadual devolveu CAPTCHA (não contornado) | [A] E-13 |

## 9. Objetivo organizacional (formulado a partir do ETP, item IX)

Garantir, por 12 meses, o "suprimento das necessidades de estoque adequado" dos 334 medicamentos da Assistência Farmacêutica municipal, com os recursos orçamentários indicados e respeitando as restrições legais e operacionais da seção 7, de forma eficiente no uso dos recursos públicos. [C] (texto do ETP) / [I] (síntese)

## 10. O que aconteceu depois [PÓS — reservado à avaliação]

| Fato | Valor | Status |
|---|---|---|
| Homologação | 11/03/2025 (TCE-PB); 334/334 itens homologados; 7 fornecedores | [C] E-08 |
| Contratos | 7 contratos, 12/03/2025–12/03/2026, total **R$ 3.105.249,60** (−37,3% sobre a estimativa); o maior soma R$ 2.096.243,50 | [C]/[K] E-08 |
| Execução até 31/08/2026 | Empenhado R$ 586.816,65 = **18,9%** do contratado; por contrato, de 7,8% a 90,9% | [K] E-09 |
| Prorrogações | 3 aditivos: +12 meses (até 12/03/2027), "preços unitários renovados e inalterados" | [C] E-05b |
| "Nova demanda" | PE 25/2025 (set/2025): 87 itens, só 1 com descrição igual a item do PE 04/2025; estimado R$ 5,59 mi; homologado R$ 2,78 mi; 6 contratos R$ 1,17 mi; empenhado R$ 67,7 mil até ago/2026 | [C]/[K] E-08 |
| Plano seguinte | PE 09/2026: 329 itens, 312 com descrição igual; 207 com a mesma quantidade, 37 menores, 68 maiores | [K] E-08 |
| Despesa farmacológica total | 2025: R$ 1.410.230,18; 2026 (até ago): R$ 1.350.148,81 empenhados | [K] E-10 |
| BPS | 315 registros do processo 004/2025 com data 11/03/2025 (R$ 2,92 mi), inseridos em 22/12/2025: o BPS registrou o **contrato**, não as entregas | [C]/[I] E-12 |
