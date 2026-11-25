# 05 — Economia potencial e como medir a economia efetiva

> **Economia potencial ≠ economia efetiva.** Esta é uma estimativa condicionada a hipóteses. A economia efetiva só existe depois da contratação e do pagamento, e **não é observável em 29/01/2025**. As duas nunca se somam.

## 1. Referência

- **Contra o quê:** E1, status quo federativo. Para os 11 itens descentralizados (1B exceto AP007, e 2), é o custo que as 27 SES teriam comprando separadamente, ao preço mediano (p25–p75) das compras estaduais homologadas nos 24 meses anteriores ao corte.
  - Fonte: `precos_comprasgov`, filtro `esfera='E'`, `compatibilidade='compativel'`, `NOT flag_preco_extremo`, `dataResultado` de 2023-02-01 a 2025-01-29.
  - Se houver menos de 3 registros estaduais, todas as esferas.
  - Multiplicado pela mesma quantidade planejada usada em E2.
- **Por que essa referência é adequada:**
  1. Representa o que efetivamente aconteceria sem a decisão, porque as SES são as compradoras legais desses itens.
  2. É observada, recente e anterior ao corte.
  3. Usa a mesma categoria de valor que a estratégia avaliada (preço homologado × quantidade).
  4. Usa a mesma quantidade, então a diferença isola o efeito preço.
- **Referências rejeitadas:**
  - **Teto CMED:** é limite legal, não preço praticado. Medir contra o teto inflaria a economia.
  - **Valor SIA 1B:** é valor financiado, outra categoria.
  - **Execução orçamentária:** é agregada por ação e mistura todos os itens.
- **Itens centralizados (1A e AP007):** não há economia potencial atribuída. O custo é igual em todas as estratégias, e as táticas de renegociação não foram quantificadas por falta de base.

## 2. Cálculo

Para o item *i* descentralizado, numa simulação:

```
custo_E1_i = Q_i × P_E1_i × idx
custo_E2_i = Q_i × P_E1_i × idx × [(1 − s) + s × f_nac_i]
f_nac_i    = min(1, exp(β_seg × (ln min(V_nac_i, Vmax_obs_i) − ln q_ref_i)))
economia   = Σ_i (custo_E1_i − custo_E2_i)
```

| Termo | Definição | Fonte / classificação |
|---|---|---|
| Q_i | quantidade planejada, triangular (baixa, central, alta) | `trabalho/demanda_projecao.csv` [CALC/HIP H03–H06] |
| P_E1_i | preço de referência, triangular (p25, mediana, p75) | [CALC] |
| idx | reajuste de preços em 2025, U(1,00; 1,05) | [HIP H12] |
| β_seg | efeito volume-preço por segmento, U(IC90) | `trabalho/elasticidade.csv` [CALC/HIP H16] |
| V_nac_i | volume anual nacional | [CALC] |
| Vmax_obs_i | maior compra já observada do item; sem extrapolação | [CALC] |
| q_ref_i | mediana das quantidades das compras de referência | [CALC] |
| s | parcela do volume do horizonte sob a ata nacional, U(0,40; 0,70) | [HIP H13] |

Preços limitados ao teto CMED aplicável [HIP H10]. Monte Carlo com N=4.000 (`trabalho/03_estrategias.py`).

## 3. Resultado

| Medida | Valor (R$ milhões) | Faixa p05–p95 | % do custo E1 dos descentralizados |
|---|---|---|---|
| **Economia potencial no horizonte (fev/2025–jan/2026)** | **221** | **159–298** | 18,4% |
| Economia potencial em regime pleno de 12 meses (após a transição; não somar à anterior) | 405 | 337–483 | 33,9% |
| Limite otimista (preço na razão DLOG/estadual de 0,29; não usado) | 444 | — | 39,1% |

[CALC: `saida/03_comparacao.csv`, `trabalho/sensibilidade.csv`]

**Itens que concentram a economia** (regime pleno, p50, `trabalho/mc_resumo.txt`):

| Item | Economia (R$ mi) |
|---|---|
| omalizumabe (AP034) | 86 |
| eltrombopague 50 mg (AP029) | 81 |
| mepolizumabe (AP027) | 59 |
| dapagliflozina (AP050) | 52 |
| eltrombopague 25 mg (AP060) | 35 |
| mesalazina 500 mg (AP052) | 33 |

Os seis somam ~85% do total.

- AP027 tem referência de preço incerta: a mediana BPS é 2,4× a do Compras.gov.
- Em itens de fonte única (AP027, AP029, AP034, AP050, AP052, AP060, AP070), a economia depende de **negociação**, não de concorrência.

**Quem se beneficia:**

- **Grupo 2:** as SES.
- **Grupo 1B:** as SES, pela redução da contrapartida acima do valor SIA. A União também, se o valor de financiamento SIA for revisto para baixo.
- Isso não está quantificado, porque o SIA é valor financiado e não se soma ao valor contratado.

## 4. Condições para que a economia potencial se realize

1. Pelo menos cerca de metade das SES participa da IRP com quantidades firmes [HIP H13].
2. O certame nacional não fracassa nem é suspenso. A economia se anula com probabilidade de fracasso ≥ ~41% [CALC].
3. O efeito volume observado vale para volumes consolidados [HIP H16]. Com β=0, a economia é 0.
4. As SES compram ao preço da ata, em vez de manter contratos mais caros além da vigência.
5. Os preços de mercado em 2025 se comportam de forma parecida entre os arranjos (o mesmo idx em E1 e E2).

## 5. Como medir a economia efetiva (após a contratação e o pagamento)

| Elemento | Especificação |
|---|---|
| **Quando** | Primeira medição 6 meses depois da homologação da ata nacional; medição final após o fim do horizonte (jan/2026), quando houver liquidação e pagamento, inclusive restos a pagar até meados de 2026. Em 2024, só 72% do empenhado na ação 4705 foi pago no exercício [CALC: `recursos_federais.csv`, pago/empenhado], então o pagamento atrasa |
| **Dados** | (a) ata nacional: preço homologado por item; (b) contratos e notas de empenho de cada SES vinculados à ata (Compras.gov/PNCP); (c) **notas fiscais e ordens bancárias**, ou seja, quantidade efetivamente entregue e paga por SES (SIAFE estaduais, SIAFI para o 1B); (d) preços das SES que não aderiram (grupo de comparação); (e) dispensação SIA do período, para conferir a cobertura |
| **Cálculo** | economia efetiva = Σ (preço contrafactual − preço efetivamente pago) × quantidade efetivamente paga |
| **Preço contrafactual** | (i) o preço E1 de referência registrado aqui, corrigido pelo reajuste CMED efetivo de 2025, e (ii) por diferenças-em-diferenças, a variação de preço das SES não participantes ou de itens não incluídos |
| **Controles** | separar o efeito do reajuste CMED; excluir compras judiciais e emergenciais (medir à parte, como custo da contingência); não incluir quantidade contratada e não paga; não somar valores BPS e Compras.gov |
| **Cobertura** | verificar se a dispensação não caiu nem ficou desabastecida. Economia com ruptura não conta como eficiência; registrar os episódios de falta |
| **Relato** | separar economia efetiva de preço e variação de quantidade; **não somar com a potencial**; relatar sempre a referência e o período |
