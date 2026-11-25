# Conteúdo dos 26 slides — Planejamento de compras de medicamentos do SUS com IA generativa

> **Atenção (D-16):** a divisão original dos 26 slides e a numeração dos 8 apresentadores **não foram encontradas** no projeto, nas conversas, no Google Drive, no Gamma nem no Canva. Esta é uma **estrutura reconstruída**: 8 blocos temáticos, de 3 a 4 slides cada. Se houver a divisão original, basta mover cada slide para o número e o apresentador corretos; o conteúdo é independente da ordem.

---

## Apresentador 1 — Contexto e pergunta (slides 1–3)

**Slide 1 — Título**
- Planejamento de compras públicas de medicamentos do SUS com IA generativa
- Experimento retrospectivo em escala nacional: decisão de 29/01/2025, horizonte de 12 meses
- Sistemas de Informação nas Organizações — UFPB

**Slide 2 — O problema organizacional**
- O SUS compra medicamentos nas três esferas, com competências diferentes.
- Comprar o mesmo item de formas diferentes tem consequências: preço, abastecimento, compromisso orçamentário.
- Equifinalidade: vários arranjos atingem o objetivo, com custos e riscos diferentes.

**Slide 3 — A pergunta do experimento**
- A IA consegue, sozinha e só com dados reais disponíveis na data, formular cenários de aquisição, comparar consequências e escolher a estratégia mais eficiente?
- E essa escolha resiste ao que de fato aconteceu depois?

## Apresentador 2 — Dados públicos e auditoria (slides 4–6)

**Slide 4 — Fontes auditadas**
- SIA/SUS (dispensação), CMED (teto de preço), Compras.gov.br (preços homologados), BPS, PNCP, RENAME 2024, Portal da Transparência (orçamento).
- Tudo baixado e examinado; nada presumido pela descrição da plataforma.

**Slide 5 — O que os dados permitem**
- Só o **Componente Especializado (CEAF)** tem demanda nacional anterior ao corte: o SIA traz a dispensação de 305 procedimentos, em 27 UFs, por mês.
- O Componente Básico e o Estratégico não têm dispensação nacional aberta. Para eles só há quantidade comprada, e comprar não é demandar.
- O BPS cobre 747 compradores e quase nenhuma compra federal: não representa o país.

**Slide 6 — Regras de rigor**
- Corte temporal: só entra o que estava publicado até 29/01/2025.
- Dados posteriores ficam guardados para a avaliação.
- Sem dados inventados; quantidade comprada ≠ demanda; homologado ≠ pago; sem somar bases duplicadas.

## Apresentador 3 — Do caso municipal ao problema nacional (slides 7–9)

**Slide 7 — Primeira versão: um município**
- Caso piloto: Santa Luzia/PB (PE 04/2025), arquivado na branch `experimento-santa-luzia`.
- Lição: um município de 15 mil habitantes não sustenta conclusões sobre o SUS.

**Slide 8 — Reformulação nacional**
- Quem decide: a coordenação nacional simulada das três esferas, respeitando a competência de cada uma (Grupos 1A, 1B e 2 do CEAF).
- Cesta: 50 apresentações do CEAF da RENAME 2024, escolhidas por relevância econômica nacional e qualidade dos dados.

**Slide 9 — A cesta**
- 38 itens 1A (MS compra), 6 itens 1B (MS financia, estados compram), 6 itens 2 (estados financiam e compram).
- Exemplos: adalimumabe, golimumabe, ustequinumabe, infliximabe, tacrolimo, alfaepoetina.
- Valor anual estimado: R$ 11,1 bi, a mesma ordem do orçamento federal do CEAF (R$ 13,7 bi empenhados em 2024).

## Apresentador 4 — Preparação dos dados (slides 10–12)

**Slide 10 — Demanda**
- Dispensação atendida, 12 meses (nov/2023 a out/2024), por UF e mês.
- Ressalva: é demanda atendida, não total; a base atual do DATASUS inclui reprocessamentos.

**Slide 11 — Preços e tetos**
- Compras.gov.br: preços homologados antes do corte em 159 CATMATs, por esfera e UF.
- CMED: teto por unidade dispensada (PF/PMVG, CAP, Convênio 87/02).
- Vínculos SIA × CMED × CATMAT feitos por regra (princípio, concentração, forma, unidade).

**Slide 12 — Integridade**
- 112 verificações automáticas: datas ≤ corte, nenhuma coluna de situação atual, disjunção entre decisão e avaliação.
- Mesmo assim, a avaliação independente achou 2 falhas na preparação (slide 21).

## Apresentador 5 — Protocolo do experimento (slides 13–15)

**Slide 13 — Isolamento do decisor**
- Sessão nova do Claude Opus 5.5, sem o histórico da coordenação.
- Ambiente com cópia do pacote; sem internet; sem conhecimento posterior ao corte.
- Transcrição integral auditada chamada por chamada: 45 chamadas, nenhuma violação.

**Slide 14 — Sem cenários prontos**
- O enunciado traz problema, objetivo, restrições e dados, e **nenhuma alternativa**.
- Exige: pelo menos 3 estratégias, critério de eficiência explícito, faixas de incerteza, economia potencial separada da efetiva.

**Slide 15 — Pré-registro**
- Protocolo de avaliação com hash **antes** da decisão.
- Avaliador independente em outra sessão isolada, sem acesso a relatórios da coordenação.
- Desvio registrado: o Fable 5.2 exigiu créditos de uso e a avaliação usou o Opus 5.5.

## Apresentador 6 — A decisão da IA (slides 16–19)

**Slide 16 — Estratégias formuladas pela IA**
- E1: status quo federativo (27 compras estaduais).
- E2: compra nacional compartilhada (ata do MS com as 27 SES participantes).
- E3: blocos regionais.
- E4: federalizar 1B/2.
- Mais 7 estratégias descartadas, com o motivo de cada uma.

**Slide 17 — Comparação**
- Custo de contratação estimado (p50):
  - E1 R$ 6,48 bi;
  - **E2 R$ 6,25 bi**;
  - E3 R$ 6,36 bi;
  - E4 R$ 6,42 bi, inviável no prazo.
- Faixas por simulação Monte Carlo (4.000 sorteios); valores de contratação, não de pagamento.

**Slide 18 — Recomendação: E2**
- Ata nacional para os 11 itens 1B/2; os 1A seguem centralizados no MS.
- Preserva as competências (PRC nº 2/2017, art. 49) e não depende do orçamento de 2025.

**Slide 19 — Economia potencial (projetada)**
- R$ 221 mi (159–298) no horizonte; R$ 405 mi/ano em regime pleno.
- Referência: o que as SES pagavam comprando sozinhas.
- Origem: efeito volume-preço medido nos dados.
- Economia efetiva só depois do pagamento; a IA descreveu como medi-la.

## Apresentador 7 — Avaliação independente (slides 20–23)

**Slide 20 — Veredito: parcialmente adequado**
- Conformidade e reprodutibilidade: adequado (saídas idênticas byte a byte).
- Cálculos, qualidade ex ante, ex post e economia: parcialmente adequado.
- Sensibilidade: a ordem das estratégias resiste.

**Slide 21 — Pontos fortes e erros**
- **Pontos fortes:**
  - decisão juridicamente viável e coerente com as competências;
  - a IA detectou sozinha um erro de classificação no pacote (imunoglobulina).
- **Erros:**
  - ponto de equilíbrio do risco de fracasso calculado em 41%, quando o correto é 70% (erro conservador);
  - contaminação de preço da mesalazina não detectada;
  - bloco 1A (81% do custo) sem alternativa quantificada.

**Slide 22 — O que aconteceu depois (ex post)**
- **Demanda:** erro mediano de −2,5%, melhor que repetir o ano anterior em 43 dos 50 itens.
- **Preços:** razão observado/projetado de 1,02 (26 itens).
- **Valor de referência observado:** R$ 6,76 bi (homologado/praticado), contra R$ 6,24 bi projetados para E2.

**Slide 23 — Economia em três níveis**
- **Projetada:** R$ 221 mi, superestimada; ~R$ 114 mi com o efeito volume calculado por item.
- **Praticada:** E2 não foi executada, então não existe.
- **Realizada:** não há pagamento por item; só a execução federal agregada (R$ 15,49 bi empenhados no CEAF em 2025).
- Os três níveis nunca se somam.

## Apresentador 8 — Conclusões (slides 24–26)

**Slide 24 — O que aprendemos sobre a IA**
- Formulou alternativas reais, respeitou competências e restrições, documentou tudo e acertou a direção.
- Errou na magnitude da economia, por generalizar um efeito médio a itens de fornecedor único.

**Slide 25 — Limites do experimento**
- O contrafactual não é observável: E2 nunca foi executada.
- Demanda atendida ≠ demanda total; sem pagamento por item.
- Falhas de preparação, PNCP inacessível e avaliador do mesmo modelo do decisor.
- Escopo restrito ao CEAF por falta de dados nacionais de demanda dos outros componentes.

**Slide 26 — Recomendações e próximos passos**
- Obter a dispensação do Componente Básico (BNAFAR) para ampliar o escopo.
- Validar os vínculos com farmacêutico.
- Repetir com avaliador de outro modelo.
- Para gestores: a IA é útil para estruturar e documentar alternativas, mas números de economia exigem conferência item a item.
