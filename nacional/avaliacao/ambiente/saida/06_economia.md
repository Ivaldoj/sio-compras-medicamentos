# 06 — Economia (dimensão G), em três níveis: **parcialmente adequado** (confiança média-baixa)

> Os três níveis abaixo são categorias diferentes e **nunca se somam**:
> - **projetada:** contrafactual do decisor;
> - **praticada ou contratada observada:** preços homologados ou praticados no mercado depois do corte;
> - **realizada:** pagamento efetivo, que só existe agregado por ação orçamentária.
>
> A estratégia E2 **não foi executada**. Não existe economia realizada de E2 que se possa observar.

## Nível 1 — Economia projetada pelo decisor (contrafactual)

| Medida | Valor (R$ mi) | Referência | Evidência |
|---|---|---|---|
| E2 × E1 no horizonte fev/2025–jan/2026 | **221 (159–298)** | E1 = mediana estadual de 24 meses × mesma Q | `03_comparacao.csv` [OBS]; reproduzido [CALC: c01 C03] |
| E2 em regime pleno (referência, não somada) | 405 (337–483) | idem | C04 |
| Limite otimista (razão DLOG/estadual 0,29), não usado | 444 | idem | `sensibilidade.csv` |

**Avaliação do nível 1:**

- **O que está correto** [OBS: `05_economia.md`]:
  - a referência é adequada: mesma categoria de valor, preço praticado, mesma quantidade;
  - o teto CMED foi rejeitado como referência;
  - o decisor separou potencial de efetiva e descreveu como medir a efetiva: Σ (preço contrafactual − preço pago) × quantidade paga, com dados de NF e ordens bancárias, grupo de comparação de SES não aderentes e controle do reajuste CMED.
- **O que está superestimado:**
  - o β agregado aplicado aos monopólios 1B de preço uniforme (§4.1 de `03_qualidade_decisao.md`) infla a projeção;
  - com β por item, a economia determinística no horizonte é ~114 milhões, contra 203 [CALC: `trabalho/d02_beta_por_item.py`];
  - a referência de AP052, contaminada pelo pacote, soma ~6 milhões a mais [CALC: f01].

## Nível 2 — Praticado ou contratado observado (mercado em 2025)

### O que aconteceu de fato

- **Nenhuma ata nacional para os 11 itens 1B/2 no horizonte.**
  - As compras DLOG desses itens na janela H são pontuais, com 12 a 1.092 unidades, provavelmente judiciais [OBS: `dados_reservados/precos_comprasgov_pos.parquet`, e02].
  - O único registro de compra centralizada de volume num item 1B é **AP034 omalizumabe: 12.600 unidades a R$ 500,00 em 11/08/2026**, fora do horizonte. Equivale a 0,72× do preço estadual vigente na época (~R$ 690–700) [OBS].
- **O mundo observado é, portanto, o status quo E1.**

### Valor de referência observado do status quo, nos 11 descentralizados

O cálculo é quantidade SIA observada × mediana estadual praticada em H:

| Medida | Valor (R$ mi) |
|---|---|
| Valor de referência observado | **1.144** |
| E1 projetado pelo decisor | 1.197 |
| Diferença | −4,7% |

[CALC: e03]

Esse valor é homologado ou praticado, **não pagamento**.

### Variações de preço observadas no status quo, sem relação com a estratégia

- **AP034 omalizumabe:** o preço praticado pelas SES caiu de ~R$ 1.841 para ~R$ 690–700 a partir de mai–jul/2025 [OBS: e02].
  - Aplicada à quantidade observada, a diferença em relação à referência do decisor é de cerca de **R$ 163 milhões** [CALC: (1.841,49 − 699,76) × 142.690].
  - Isso **não é economia de E2**. É uma mudança de preço de mercado que aconteceu sem a estratégia e que reduz a base sobre a qual E2 economizaria.
- **AP052 mesalazina 500 mg:** a mediana estadual corrigida em H é 1,37, contra a referência do decisor de 3,815. A diferença vem quase toda da contaminação do pacote, não de mercado [CALC: p01, e02].

### Economia que E2 teria gerado com os valores observados (estimativa do avaliador; hipótese, não observação)

| Hipótese de β | Economia no horizonte (s=0,55) |
|---|---|
| β agregado | ~210 milhões |
| β pós-corte | 204 milhões |
| β por item | bem menor; ~114 milhões com Q e P projetados |

[CALC: f01, d02]

**Não há como observar** se essa economia teria ocorrido.

## Nível 3 — Realizado (pagamento efetivo)

- **Não observável por item.** A execução federal existe só agregada por ação:
  - ação 4705 em 2025: empenhado R$ 15,49 bi, realizado R$ 12,85 bi (83%) [OBS: `dados_reservados/orcamento_acoes_af_2025.csv`; CALC: e03].
- Não dá para atribuir nenhuma parcela desse pagamento aos 50 itens nem a qualquer estratégia.
- As compras estaduais (1B, 2) são pagas pelos tesouros estaduais (SIAFE), que não estão nos dados.
- **Economia realizada de E2: não avaliável.** A estratégia não foi executada.

## Conclusão

- **Distinção entre níveis:** o decisor separou corretamente potencial de efetiva e definiu um protocolo de medição adequado.
- **Magnitude:** a economia potencial projetada (221 milhões) é plausível em ordem de grandeza só sob o β agregado. Com a heterogeneidade por item, já visível em 29/01/2025, o valor central esperado fica mais perto de 100–120 milhões.
- **Ex post:** não há como confirmar nem refutar a economia de E2. O que se observou foi uma redução de preço de mercado em AP034 que aconteceria de qualquer forma, e uma demanda maior que a projetada.
