# Relatório final — Planejamento nacional de compras de medicamentos do SUS por IA generativa

Experimento retrospectivo com data de decisão em **29/01/2025** e horizonte de 12 meses. Branch `reformulacao-nacional`, ainda em validação. Projeto da disciplina Sistemas de Informação nas Organizações (UFPB).

## 1. Pergunta e desenho
**Pergunta:** o Claude consegue usar informações organizacionais reais para formular cenários de aquisição, comparar consequências e escolher a estratégia mais eficiente num problema de **escala nacional**?

**Desenho:**
- **Problema** construído só com dados públicos disponíveis até o corte.
- **Decisor:** Claude Opus 5.5, em sessão isolada.
- **Avaliador:** agente independente, em outra sessão isolada.
- **Avaliação:** feita com dados posteriores ao corte, guardados à parte e nunca mostrados ao decisor.
- **Protocolo:** pré-registrado (com hash) **antes** da decisão.

## 2. O problema nacional
- **Quem decide:** a coordenação nacional, **simulada**, das três esferas do SUS, respeitando as competências reais (D-01).
- **Escopo:** cesta de **50 apresentações do Componente Especializado (CEAF)** da RENAME 2024, em todo o país.
  - 38 no Grupo 1A (compra centralizada pelo MS);
  - 6 no Grupo 1B (MS financia, estados compram);
  - 6 no Grupo 2 (estados financiam e compram).
- **Por que o CEAF:** a Etapa 1-B mostrou que só ele tem **demanda nacional anterior ao corte**. O Componente Básico e o Estratégico não têm dispensação nacional em dados abertos (D-14). Usar quantidade comprada como demanda, ou extrapolar a partir dos compradores do BPS, violaria as regras do projeto. Por isso a cesta foi restrita ao CEAF (D-15).
- **Objetivo:** abastecimento contínuo, com uso eficiente dos recursos, dentro das restrições legais, regulatórias, federativas, orçamentárias e de mercado.

## 3. Dados (pacote `nacional/dados/decision_input_nacional/`)
| Dado | Fonte | Uso |
|---|---|---|
| Dispensação nacional atendida, 12 meses (processamentos de nov/2023 a out/2024), por UF e mês | SIA/SUS — TabNet | Demanda atendida (não é demanda total) |
| Teto por unidade dispensada | CMED, lista de 06/01/2025 | Limite regulatório |
| Preços homologados e praticados antes do corte, por esfera e UF | Compras.gov.br (pesquisa de preço, 159 CATMATs); BPS como fonte complementar, sem soma | Referência de preço |
| Grupo de financiamento | RENAME 2024, Anexo III | Competência federativa |
| Execução federal 2023–2024, ações 4705, 20AE e 4368 | Portal da Transparência | Ordem de grandeza dos recursos |
| Restrições | Lei 14.133, Lei 14.770, Decreto 11.462, Decreto 12.343, PRC nº 2/2017, CMED, Convênio 87/02 | Viabilidade |

- **Integridade:** 112 verificações automáticas aprovadas (datas ≤ corte, nenhuma coluna de situação atual, disjunção pacote × avaliação).
- **Valor anual da cesta:** R$ 11,1 bi pela relevância econômica de seleção (dispensação × preço praticado mediano antes do corte). É compatível com o empenho federal da ação 4705 em 2024, de R$ 13,7 bi.

## 4. Decisão do agente (Opus 5.5, isolado)
**Conformidade:**
- 45 chamadas de ferramenta, todas dentro do ambiente, sem internet;
- o prompt é idêntico ao enunciado registrado;
- as entradas não foram alteradas;
- os 4 alertas da auditoria são falsos positivos (variáveis `dlog_*`).

**Estratégias formuladas por ele:** quatro avaliadas e sete descartadas.

| Estratégia | Custo de contratação estimado (p50; p05–p95) | Situação |
|---|---|---|
| E1: status quo federativo (27 compras estaduais nos itens 1B/2; MS nos 1A) | R$ 6,48 bi (5,93–7,18) | linha de base |
| **E2: compra nacional compartilhada** (ata nacional do MS com as 27 SES participantes nos 11 itens 1B/2; 1A e imunoglobulina centralizados) | **R$ 6,25 bi (5,73–6,93)** | **recomendada** |
| E3: blocos regionais (consórcios ou SRP regional) | R$ 6,36 bi | contingência |
| E4: federalizar 1B/2 no Grupo 1A | R$ 6,42 bi | inviável no horizonte |

**Economia potencial (projetada):**
- R$ 221 mi (159–298) no horizonte, 18% do gasto com os 11 itens descentralizados;
- R$ 405 mi/ano em regime pleno, valor que não se soma ao anterior;
- referência: o preço mediano das compras estaduais antes do corte;
- origem: efeito volume-preço medido nos dados (β ≈ −0,08).

O decisor separou contratação de pagamento e descreveu como medir a economia efetiva. Também detectou sozinho a classificação errada da imunoglobulina no pacote.

## 5. Avaliação independente
**Veredito: parcialmente adequado.**

| Dim. | Classificação | Confiança |
|---|---|---|
| A Conformidade | Adequado | Alta |
| B Reprodutibilidade (saídas idênticas byte a byte) | Adequado | Alta |
| C Cálculos (26 de 31 verificações conferem) | Parcialmente adequado | Alta |
| D Qualidade ex ante | Parcialmente adequado | Média |
| E Comparação ex post | Parcialmente adequado | Média |
| F Sensibilidade | Adequado quanto à ordem; magnitude frágil | Média |
| G Economia | Parcialmente adequado | Média-baixa |
| H Veredito | Parcialmente adequado | Média |

**Principais achados:**
1. **A recomendação se sustenta.** A ordem E2 > E3 > E4 > E1 resiste à demanda, aos preços e ao β observados depois do corte (β de −0,075 a −0,078).
2. **A economia projetada está superestimada.** O β agregado foi aplicado a monopólios do Grupo 1B cujo preço já era uniforme entre as SES. Com β por item, a economia cai cerca de 44%: de ~R$ 203 mi para **~R$ 114 mi**, na métrica do avaliador.
3. **Erros de cálculo, nenhum inverte a decisão:**
   - ponto de equilíbrio do risco de fracasso de 41% (o correto é 70%, então o erro é conservador);
   - "ordem em todos os percentis" é falso para E3 × E4 (vale em 86%);
   - "751 mil frascos" de imunoglobulina não se reproduz (o pacote dá 703 mil).
4. **Comparação ex post:**
   - **demanda:** erro mediano de −2,5%, melhor que repetir o ano anterior em 43 dos 50 itens, mas só 32 dos 50 dentro da faixa;
   - **preço:** razão observado/projetado de 1,02 (26 itens com preço observado);
   - **valor de referência observado da cesta** (homologado/praticado): R$ 6,76 bi, contra R$ 6,24 bi projetados para E2. Só 61,5% desse valor tem preço observado no horizonte.
5. **Lacunas da decisão:** o bloco 1A (81% do custo) ficou sem alternativa quantificada; a faixa de preço de renovação era estreita; o instrumento "compra nacional" (Decreto 11.462, art. 2º, VI) não foi citado.

## 6. Economia em três níveis (nunca somados)
| Nível | Valor | Natureza |
|---|---|---|
| Projetada (decisor, E2 contra E1) | R$ 221 mi (159–298); ~R$ 114 mi com β por item, segundo o avaliador | Contrafactual, ex ante |
| Praticada/contratada observada | Não existe para E2, que não foi executada. A queda de preço do omalizumabe no status quo (~R$ 163 mi contra a referência) é mudança de mercado, não economia de E2. | Observado |
| Realizada (pagamento) | Não observável por item. Só há a execução federal agregada: ação 4705, R$ 15,49 bi empenhados em 2025 (+12,7%) | Observado, agregado |

## 7. Avaliação independente × análises da coordenação: divergências
| Tema | Coordenação (preparação) | Avaliador | Divergência |
|---|---|---|---|
| Qualidade do pacote | 112 verificações aprovadas | Achou **2 falhas**: (a) supositório aceito como unidade de comprimido, contaminando a mesalazina 500 mg (AP052); (b) imunoglobulina 5 g classificada como 1B, quando é 1A (RENAME, p. 209) | **Sim.** As verificações da coordenação eram de integridade temporal e estrutural, não de compatibilidade de forma nem de grupo. A coordenação reconferiu e **confirma as duas**: a lista de unidades sólidas aceitava supositório, e o parser de grupos caía na entrada de 0,5 g. Os arquivos congelados não foram alterados. |
| Coerência dos grupos | 100% de coerência entre Grupo 1B e valor aprovado no SIA | O decisor detectou o erro do AP007 pelos dados de compra | **Sim.** A checagem de coerência não pega um 1A rotulado como 1B se o procedimento do SIA tiver valor zero. |
| Relevância econômica | Cesta = R$ 11,1 bi por ano (dispensação × preço praticado) | Valor de referência observado em 2025 = R$ 6,76 bi (outra métrica: quantidade observada × preço observado, com 38,5% imputado) | Métricas diferentes; não são comparáveis diretamente. |
| BPS | Não serve para relevância nacional (D-13) | Usado só como complemento; 6 divergências BPS × Compras.gov apontadas pelo decisor | Coerente |
| Modelo do avaliador | Planejado: Fable 5.2 (D-04) | Executado com Opus 5.5 (D-17) | Desvio: o Fable exigiu créditos de uso. Mesmo modelo do decisor, o que reduz a independência. |

## 8. Verificação do objetivo global (D-09)
| Requisito | Situação |
|---|---|
| Problema em escala nacional | **Cumprido**: 27 UFs, três esferas, demanda e preços nacionais |
| Cenários formulados pela IA, sem direcionamento | **Cumprido**: 4 avaliados e 7 descartados; o enunciado não trazia alternativas |
| Escolha da estratégia mais eficiente, com justificativa | **Cumprido**, com ressalva na magnitude da economia |
| Eficiência mensurável | **Parcial**: a ordem é verificável ex post; a economia realizada não é observável, porque E2 não foi executada e não há pagamento por item |
| Escopo de produtos | Restrito ao CEAF (D-15), por falta de demanda nacional dos componentes Básico e Estratégico |

## 9. Limitações
1. **Contrafactual:** a estratégia recomendada não foi executada. A avaliação ex post verifica premissas (demanda, preço, β), não resultado.
2. **Dispensação do SIA:** é demanda atendida, e a base atual inclui reprocessamentos.
3. **Pacote:** duas falhas de preparação, confirmadas, com efeito localizado (AP052 e AP007); vínculos feitos por regra, sem validação humana; 20 candidatos de alto valor excluídos por qualidade de dados (natalizumabe, rituximabe, certolizumabe e outros).
4. **Fontes inacessíveis:** PNCP inacessível durante a execução (conexão recusada), então atas e contratos federais não entraram.
5. **Lacunas:** sem ICMS por UF, sem orçamento de 2025 na data de decisão (a lei orçamentária foi aprovada depois), sem estoques.
6. **Independência:** avaliador do mesmo modelo do decisor (D-17), e coordenação não cega.
7. **Estrutura dos slides:** a estrutura original de 26 slides não foi encontrada (D-16).

## 10. Registros e reprodução
- **Decisões metodológicas:** `nacional/DECISOES_METODOLOGICAS.md`.
- **Cronologia e hashes:** `nacional/LOG_NACIONAL.md`.
- **Preparação:** `nacional/scripts/n01` a `n03` (dados), `n05` (auditoria); pacote em `nacional/dados/`.
- **Decisão:**
  - `nacional/decisao/ambiente/` (entregáveis e scripts do decisor, congelados);
  - `nacional/decisao/registro/` (transcrição integral, auditoria, hashes).
- **Avaliação:**
  - `nacional/avaliacao/ambiente/saida/` (12 entregáveis do avaliador);
  - `nacional/avaliacao/registro/` (transcrição, auditoria, hashes; tentativa do Fable sem nenhuma ação).
- **Experimento municipal:** arquivado na branch `experimento-santa-luzia`.
