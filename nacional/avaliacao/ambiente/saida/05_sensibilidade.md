# 05 — Sensibilidade (dimensão F): **adequado** quanto à ordem; **frágil** quanto à magnitude (confiança média)

- **Script:** `trabalho/f01_sensibilidade.py`.
- **Saídas:** `trabalho/f01_sensibilidade.csv`, `trabalho/f01_beta_pos.csv` e `trabalho/f01_eco_item.csv`.
- **Método:** apliquei a mesma fórmula determinística do decisor (`04_sensibilidade.py`: índice 1,025, s=0,55 para E2, 0,40 para E3 e 0,15 para E4), trocando os insumos projetados pelos observados.
- **Unidade:** todos os valores são valor de contratação (R$ milhões), não pagamento.

## 1. O efeito volume-preço se mantém fora da amostra?

Reestimei a especificação do decisor (efeito fixo de item e de ano, β por segmento, IC90 por bootstrap de itens) com os preços **pós-corte** do Compras.gov [CALC: f01 → `trabalho/f01_beta_pos.csv`]:

| Amostra | β concorrencial (IC90) | β concentrado (IC90) |
|---|---|---|
| Decisor, pré-corte 2022–jan/2025 | −0,085 (−0,118; −0,072) | −0,080 (−0,099; −0,067) |
| Pós-corte, horizonte | −0,075 (−0,097; −0,061) | −0,078 (−0,096; −0,057) |
| Pós-corte, até nov/2026 | −0,079 (−0,107; −0,066) | −0,074 (−0,093; −0,058) |

- A **associação** transversal volume-preço se repete, com magnitude quase igual [CALC].
- Isso **não** prova que consolidar a compra causaria a redução, como o próprio decisor advertiu em H16.
- Também não resolve a heterogeneidade por item: nos monopólios do 1B, o β de cada item é ≈0 (`03_qualidade_decisao.md` §4.1).

## 2. A ordem das estratégias resiste aos valores observados?

| Cenário | Base E1 descentralizados | Economia E2 | E3 | E3 com a mesma transição de E2 | E4 | E2 pleno | Ordem |
|---|---|---|---|---|---|---|---|
| Decisor (Q e P projetados) | 1.136 | 203 | 106 | 146 | 55 | 370 | E2 > E3 > E4 > E1 |
| Q observada | 1.383 | 254 | 133 | 183 | 69 | 463 | igual |
| P observado (mediana estadual em H) | 963 | 167 | 87 | 119 | 46 | 304 | igual |
| **Q e P observados** | 1.173 | **210** | 110 | 151 | 57 | 382 | igual |
| P do decisor com AP052 corrigido | 1.102 | 197 | 103 | 141 | 54 | 358 | igual |
| Q e P observados + β pós-corte | 1.173 | 204 | 106 | 146 | 56 | 370 | igual |
| β por item, pré-corte (Q e P projetados) | 1.136 | **114** | — | — | — | — | E2 > E1 (E3 e E4 recalculáveis pela mesma lógica) |

[CALC: f01; última linha: `trabalho/d02_beta_por_item.py`]

**Por que a ordem é tão estável:**

- No modelo do decisor, as estratégias diferem só pelo fator f = exp(β·Δln V) aplicado à mesma Q e ao mesmo P.
- Com β<0, volume nacional > regional e transições s₂ ≥ s₃ > s₄, a ordem E2 > E3 > E4 > E1 é **estrutural**: não depende de Q nem de P.
- Trocar demanda e preço pelos observados muda só a magnitude [INF].

**Efeitos que se compensaram nos valores observados:**

- A **quantidade maior** (AP050 +63% sobre a projeção; AP027 +46%; AP034 +30%) aumenta a economia.
- O **preço menor** em AP034 (queda do monopolista) e em AP052 (correção da contaminação) a reduz.
- Saldo: 210 milhões, contra 203 do decisor [CALC].

## 3. Ponto de equilíbrio do risco de fracasso

| | Fórmula do decisor | Fórmula correta |
|---|---|---|
| Probabilidade de fracasso que anula a economia (mediana do MC) | 41,3% | **70,4%** |

[CALC: f01 e c01; ver `02_calculos.md` C14]

O erro é conservador: com a fórmula correta, a recomendação fica **mais** robusta ao risco de certame.

## 4. Que premissas mudariam a escolha

1. **β efetivo ≈ 0 nos itens que concentram a economia.** É o caso observado ex ante nos três monopólios 1B, AP029, AP060 e AP034 [CALC: d02].
   - A economia cai para ~114 milhões, mas continua positiva por causa de AP027, AP050, AP052 e dos genéricos.
   - E2 deixaria de ser preferível a E1 só se β≈0 em **todos** os itens, ou se o custo de transação e coordenação, não modelado pelo decisor, passasse de ~R$ 100 milhões no horizonte [INF].
2. **Mudanças de preço do monopolista independentes do arranjo de compra.** A queda de ~62% de AP034 em 2025 aconteceu no status quo [OBS: e02].
   - Eventos assim reduzem a base sobre a qual a economia de E2 é medida (AP034 passa de 42 para 21 milhões no cenário Q e P observados).
   - Não invertem a ordem [CALC: f01_eco_item.csv].
3. **Adesão das SES e enquadramento jurídico do Grupo 2 em "compra nacional"** (Decreto 11.462, art. 2º, VI). Se o Grupo 2 ficar de fora, a economia cai para a parcela 1B: cerca de 64% da economia central do decisor (131 de 203 milhões: AP027, AP029, AP034, AP060 e AP062). Com β por item, essa parcela 1B encolhe muito, porque AP029, AP034 e AP060 têm β≈0 [CALC: soma de `eco_decisor` dos itens 1B em f01_eco_item.csv; INF].
4. **Transição.** Com s ≤ ~0,2, a economia no horizonte fica abaixo de ~R$ 75 milhões, o que o decisor já reconheceu [OBS: `04_recomendacao.md`].

## Conclusão

- A **recomendação** (E2 para os 11 itens 1B/2; 1A mantido no MS) **resiste** aos valores observados de demanda, preço e β e à correção do ponto de equilíbrio.
- A **magnitude** da economia é frágil:
  - fica estável (~200 milhões) com o β agregado;
  - cai pela metade (~114 milhões) com β específico por item, informação que já estava disponível em 29/01/2025.
