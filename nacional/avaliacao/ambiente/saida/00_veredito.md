# 00 — Veredito da avaliação independente: decisão nacional de compras do CEAF (corte em 29/01/2025)

## Veredito geral: **PARCIALMENTE ADEQUADO**

**A recomendação se sustenta.** O decisor recomendou E2: um SRP nacional gerenciado pelo MS, com as 27 SES como participantes, para os 11 itens 1B/2, mantendo os 39 itens 1A e a imunoglobulina na compra centralizada do MS. A recomendação é:

- juridicamente sustentável, com a "compra nacional" do Decreto 11.462/2023, art. 2º, VI, como fundamento mais preciso;
- coerente com as competências federativas;
- conforme ao protocolo e reprodutível byte a byte;
- robusta quanto à **ordem** das estratégias quando se usam a demanda, os preços e o β observados.

**Mas a economia potencial anunciada está superestimada.** O valor declarado é R$ 221 mi (159–298) no horizonte. Ele vem de um efeito volume-preço agregado (β ≈ −0,08) aplicado também a monopólios do Grupo 1B cujo preço, já em 29/01/2025, era praticamente uniforme entre as SES (eltrombopague, omalizumabe). Com β por item, a economia central cai cerca de 44%, para ~R$ 114 mi.

**Erros adicionais** (nenhum inverte a recomendação):

- ponto de equilíbrio do risco de fracasso errado: 41% em vez de 70%, um erro conservador;
- faixa de renovação estreita para os 1A, que respondem por 81% do custo;
- contaminação de AP052 (supositório) não detectada.

**Ex post:**

- **Demanda:** prevista com erro mediano de −2,5%, melhor que a referência ingênua em 43 dos 50 itens. Mas só 32 dos 50 itens ficaram dentro da faixa, e o crescimento de itens em rampa foi subestimado.
- **Preços:** onde houve observação no horizonte, a razão mediana observado/decisor foi 1,02 (26 itens). Houve desvios grandes em AP002 (×3,3, troca de fornecedor/PDP), AP059 (×1,8) e AP034 (×0,38, queda de preço do monopolista no status quo).

## Tabela por dimensão

| Dim. | Classificação | Justificativa (resumo) | Evidência principal | Confiança |
|---|---|---|---|---|
| **A** Conformidade | **Adequado** | 45 chamadas, todas dentro da raiz; sem internet, agentes ou dados reservados. Nenhum fato posterior ao corte usado. Hashes de `data/` inalterados. Ocorrências menores declaradas (saídas longas persistidas pelo harness e não lidas; `__pycache__` em `data/`) | `trabalho/a01_transcricao.py`; hashes; `01_conformidade_reprodutibilidade.md` | Alta |
| **B** Reprodutibilidade | **Adequado** | Cadeia 00→05 reexecutada em cópia: todas as saídas idênticas byte a byte, exceto dois arquivos exploratórios com ordem de linhas diferente e conteúdo igual. Só "~751 mil frascos" não sai dos scripts (o pacote dá 703 mil) | `trabalho/b01_reproduz.py`, `b01_reproducao.csv` | Alta |
| **C** Precisão dos cálculos | **Parcialmente adequado** | 26 de 31 verificações conferem: totais, faixas, categorias de valor, teto CMED, sem duplicidade. Erros: ponto de equilíbrio (fórmula conta a perda duas vezes: 0,41 contra 0,70); "ordenação em todos os percentis" falsa para E3×E4 (86% dos sorteios); AP052 lido como dispersão quando é mistura de produtos | `02_calculos.md`, `02_calculos.csv`, `trabalho/c01_calculos.py` | Alta |
| **D** Qualidade ex ante | **Parcialmente adequado** | Quatro estratégias distintas e sete descartadas; critério explícito; competências respeitadas; incertezas com Monte Carlo; boa separação de categorias; detectou o erro de grupo de AP007 (confirmado na RENAME, p. 209). Fragilidades: β agregado aplicado a monopólios de preço uniforme (economia ~44% menor com β por item); faixa de renovação dos 1A estreita apesar do histórico de PDP; bloco 1A (81% do custo) sem alternativa quantificada; não citou o instrumento "compra nacional" | `03_qualidade_decisao.md`; `trabalho/d02_beta_por_item.py`; `d01_rename.py` | Média |
| **E** Comparação ex post | **Parcialmente adequado** | E1: erro mediano −2,5%, |erro| mediano 5,5%, melhor que a referência ingênua em 43/50, mas 32/50 na faixa. E2: razão de preço 1,02 (26 itens), 19/26 na faixa; grandes desvios em AP002, AP059, AP034 e AP052. E3: referência observada da cesta R$ 6,76 bi contra E2 projetado R$ 6,24 bi (−7,7%); nos descentralizados, 1,144 bi observado contra 1,197 bi do E1 projetado. Só 61,5% da referência tem preço observado no horizonte. E4: a ação 4705 cresceu 12,7% em 2025 (empenho) | `04_comparacao_ex_post.md`, `.csv`; `trabalho/e01`–`e03` | Média |
| **F** Sensibilidade | **Adequado** (ordem) / magnitude frágil | A ordem E2 > E3 > E4 > E1 se mantém com Q, P e β observados (β pós-corte −0,075/−0,078). A economia vai a ~210 mi com o β agregado e cai a ~114 mi com β por item. O ponto de equilíbrio correto (70%) reforça E2 | `05_sensibilidade.md`; `trabalho/f01_sensibilidade.py` | Média |
| **G** Economia | **Parcialmente adequado** | Os três níveis foram separados corretamente pelo decisor, com bom protocolo de medição da efetiva. A projeção (221 mi) está inflada pelo β agregado. Praticado observado: E2 não executada; houve queda de preço de AP034 no status quo (~R$ 163 mi contra a referência), que não é economia de E2. Realizado: não observável por item | `06_economia.md` | Média-baixa |
| **H** Veredito | **Parcialmente adequado** | Decisão certa na direção, bem documentada e robusta na ordem; magnitude da economia e alguns cálculos de risco com erros | este arquivo | Média |

## Limitações que impedem conclusões mais firmes

1. **E2 não foi executada.** Não existe economia praticada nem realizada da estratégia. O único indício de compra centralizada de volume num item 1B (AP034, R$ 500 em ago/2026, 0,72× do preço estadual) está fora do horizonte e é uma compra pequena.
2. **Preço observado no horizonte só para 26 dos 50 itens.** Em 24 itens centralizados, uso o preço DLOG posterior ao horizonte (10 itens) ou o preço do decisor (14 itens); juntos, são 38,5% do valor de referência. Uma compra DLOG em H também não representa o preço de todo o consumo, porque contratos anteriores podem ter abastecido 2025.
3. **SIA é demanda atendida, por mês de processamento**, na base atual com reprocessamentos. Os últimos meses estão sujeitos a atualização.
4. **O β por item usa poucos registros** (39 a 201 por item). A conclusão de que β≈0 nos monopólios 1B se apoia também na uniformidade de preço (CV de 4–8%), que é um dado mais robusto, mas a inferência causal continua limitada.
5. **Pagamento** só existe agregado por ação (federal) e não está disponível nos estados.
6. **Viabilidade jurídica** conferida nas normas (Lei 14.133 e Decreto 11.462 em planalto.gov.br), sem jurisprudência nem pareceres. O enquadramento do Grupo 2 em "compra nacional" fica como questão aberta.
