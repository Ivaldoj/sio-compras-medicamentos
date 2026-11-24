# 10 — Problema organizacional (versão para o agente decisor)

> **Regra de uso:** este documento contém **apenas informação disponível até 29/01/2025**. Resultados posteriores (licitação, contratos, execução, compras seguintes) estão em `data/processed/caso_santa_luzia/reservado_avaliacao/` e em `docs/08` (seção 10) e `docs/11`, e **não devem ser fornecidos ao agente**. Cada fato traz seu status: [C] comprovado, [K] calculado, [A] ausente/desconhecido.

## 1. Contexto

Você apoia a **Secretaria Municipal de Saúde de Santa Luzia, Paraíba** (Prefeitura CNPJ 09.090.689/0001-67; Fundo Municipal de Saúde CNPJ 10.425.754/0001-47; população estimada de 15.387 habitantes em 2024) [C]. A data é **29 de janeiro de 2025**.

A Secretaria precisa abastecer, pelos próximos **12 meses**, a Assistência Farmacêutica do município: medicamentos da Assistência Farmacêutica Básica, da Especializada e medicamentos fora da RENAME, dispensados à população [C]. O Estudo Técnico Preliminar já levantou a necessidade e o orçamento estimado. A forma de aquisição ainda deve ser decidida e justificada.

## 2. Objetivo organizacional

Garantir o **suprimento contínuo e adequado** dos medicamentos listados durante 12 meses, usando os recursos públicos com **eficiência**, dentro das restrições legais, orçamentárias e operacionais abaixo. Consequências relevantes: custo total, compromisso financeiro assumido, atendimento das quantidades, risco de falta, risco de perda por validade, carga operacional e conformidade legal.

## 3. Necessidade documentada [C]

- **334 itens**, cada um com descrição, concentração, forma farmacêutica, unidade e quantidade anual estimada.
- Método declarado pelo órgão: "as estimativas foram baseadas na utilização anual dos anos anteriores". O consumo por item que sustenta a estimativa **não está disponível** [A].
- Unidades: comprimido 159 itens; frasco 77; ampola 59; cápsula 16; bisnaga 14; unidade 4; seringa 3; sachê 1; envelope 1.
- Valor estimado pelo órgão (pesquisa no "Banco de Preços" e com fornecedores da região): **R$ 4.952.438,00**. Os 10 maiores itens somam 39,9%. O maior é a insulina humana NPH 100 UI/mL, 6.000 unidades a R$ 193,02 (R$ 1.158.120; 23,4%) [C]/[K].
- No plano anterior (pregão 01/2024, 349 itens), 143 itens têm descrição idêntica: 64 com a mesma quantidade, 24 com quantidade menor e 55 com maior [K].
- Tabela item a item: `data/processed/caso_santa_luzia/pre_decisao/itens_necessidade_e_referencias.csv` (colunas: item, descrição, unidade, quantidade estimada, preço unitário estimado pelo órgão, CATMAT identificado, referências de preço BPS até a data, quantidade no plano de 2024).

## 4. Recursos financeiros

| Informação | Valor | Status |
|---|---|---|
| Valor estimado da necessidade | R$ 4.952.438,00 | [C] |
| Dotações indicadas | SMS (02.030) — 10.301.2016.2018; FMS (02.090) — 10.301.1006.2061 Manutenção dos Recursos do SUS, 10.301.1006.2067 Manutenção da Farmácia Básica, 10.302.1008.2069 SAMU; elementos 3390.30 (material de consumo) e 3390.32 (distribuição gratuita); fontes 1.500.1002, 1.500.0000, 1.600.0000 | [C] |
| Saldo disponível nas dotações | desconhecido | [A] |
| Despesa com medicamentos em 2024 (empenhado = liquidado) | R$ 1.953.288,72; pago R$ 1.876.052,11 (248 empenhos) | [K] |
| Composição de 2024 | Pregão 12/2024 R$ 1.223.231,57; Pregão 01/2024 R$ 656.016,25; sem licitação R$ 73.830,90; outros R$ 210,00 | [K] |
| Fontes da despesa de 2024 | Fundo a Fundo SUS federal, Bloco de Manutenção: R$ 1.549.928,07 (79,4%); recursos não vinculados de impostos: R$ 403.360,65 (20,6%) | [K] |

Séries mensais de 2024: `pre_decisao/execucao_farmaco_2024_mensal.csv`.

## 5. Instrumentos e histórico de aquisição conhecidos

- **Pregão 01/2024**: medicamentos da Assistência Farmacêutica, 349 itens, homologado em 01/04/2024 com 12 propostas vencedoras. Resultados por item não estão disponíveis no PNCP [C]/[A].
- **Pregão 12/2024**: medicamentos fora do elenco básico, contratados pelo **maior percentual de desconto sobre a tabela CMED**, com um único fornecedor. Descontos: éticos 18,01%; genéricos 60,11%; similares 51,01%. Valor homologado R$ 690.370; gerou R$ 1.223.231,57 de empenhos em 2024. A vigência em 2025 é desconhecida [C]/[K]/[A].
- O município **não publicou** Plano de Contratações Anual no PNCP para 2025 [A].
- Atas de registro de preços de outros órgãos disponíveis para adesão: **não levantadas** [A].

## 6. Restrições

| Restrição | Tipo | Status |
|---|---|---|
| Lei nº 14.133/2021 (modalidades, dispensa, registro de preços, garantias, prazos de contrato, sanções) | Legal | [C] (norma) |
| Produtos com registro na Anvisa, salvo isenção legal | Legal/sanitária | [C] |
| Validade mínima de 75% da vida útil ou mais de 365 dias na entrega (orientação do TCE-PB) | Regulatória | [C] |
| **A administração não possui local adequado para armazenamento** de medicamentos | Operacional | [C] |
| Entregas no endereço da Secretaria Municipal de Saúde | Operacional | [C] |
| Preço máximo nas vendas ao poder público definido pela CMED: PMVG para os medicamentos sujeitos ao CAP; Preço Fábrica para os demais (lista de 07/01/2025 disponível) | Regulatória | [C] |
| Itens fora da RENAME estão na necessidade | Escopo | [C] |

## 7. Referências de preço disponíveis em 29/01/2025

| Fonte | Cobertura | Status |
|---|---|---|
| Preço unitário estimado pelo próprio órgão | 334 itens | [C] |
| Banco de Preços em Saúde (registros inseridos até 29/01/2025; compras de jan a out/2024; 112 instituições) | 285 itens com ≥ 1 preço do mesmo CATMAT (84,6% do valor estimado); 225 com ≥ 5; 210 com preço da Paraíba | [K] |
| Lista CMED PF/PMVG publicada em 06/01/2025 (CAP de 21,53%) | 259 itens (79,7% do valor estimado) ligados a apresentações registradas, via registros Anvisa do BPS anteriores à data; tabela em `pre_decisao/itens_cmed_jan2025.csv`, com PF e PMVG por alíquota de ICMS | [K]; correspondência provável — conferir apresentação e converter embalagem→unidade |
| Descontos obtidos no Pregão 12/2024 sobre a tabela CMED | 3 categorias | [C] |

Cuidados: preço do BPS é histórico e por unidade de fornecimento (conferir a unidade); preço da CMED é teto por embalagem; nenhum desses valores garante o preço que será obtido.

## 8. O que não se sabe na data de decisão

Consumo real por item; estoque existente; saldo orçamentário exato; preços que o mercado vai oferecer; disponibilidade ou desabastecimento de cada medicamento (a lista estadual de desabastecimento de set/2024 não pôde ser obtida); prazos reais de entrega dos fornecedores; atas vigentes de outros órgãos.

## 9. Hipóteses que o experimento fixa (explícitas, não verificadas)

- **H1 — Necessidade:** a quantidade do ETP é a estimativa oficial do órgão para 12 meses; a demanda real pode ser diferente e é incerta.
- **H2 — Orçamento:** o valor estimado (R$ 4.952.438,00) é a referência de recurso reservado para a necessidade; a despesa de 2024 (R$ 1,95 mi) indica o nível de gasto efetivamente realizado num ano.
- **H3 — Preços:** preços futuros são desconhecidos; só as referências da seção 7 podem ser usadas.
- **H4 — Mercado:** ausência de informação sobre desabastecimento não significa disponibilidade garantida.

## 10. Tarefa esperada (sem antecipar a resposta)

Formular alternativas de aquisição para atender à necessidade, estimar e comparar suas consequências (financeiras e operacionais, com as incertezas acima), escolher uma alternativa e justificá-la com os dados desta página, explicitando as hipóteses adicionais que usar.
