# 04 — Comparação ex post (dimensão E): **parcialmente adequado** (confiança média)

- **Tabela por apresentação e totais:** `saida/04_comparacao_ex_post.csv` (50 linhas + 4 de total).
- **Scripts:** `trabalho/e01_demanda.py`, `e02_precos.py`, `e03_custo_orcamento.py` e `w01_ex_post_csv.py`.
- **Horizonte (janela H):** 30/01/2025 a 31/01/2026.
- **Cuidados de leitura:**
  - a dispensação SIA é **demanda atendida**, não demanda total;
  - a base TabNet é a atual, com reprocessamentos, e os últimos seis meses estão "sujeitos a atualização" [OBS: notas TabNet em `evidencias_primarias/sia_tabnet/pos_qtd_proc_uf.html`];
  - o período SIA é por **mês de processamento**, de fev/2025 a jan/2026.

## Conferência dos dados reservados contra as evidências primárias

- **SIA pós-corte:** o total reservado e a soma por UF conferem com o TabNet bruto (`pos_qtd_proc_uf.html`). O valor aprovado também confere (`pos_valor_proc.html`) [CALC: e01].
- **SIA pré-corte:** `dispensacao_12m_pre_corte` e o ano anterior do pacote conferem com `pre_qtd_proc_uf.html` e `pre0_qtd_proc.html` [CALC: e01].

## E1 — Quantidade projetada × dispensação observada

| Medida | Valor |
|---|---|
| Erro relativo da quantidade central (projetada/observada − 1): mediana | **−2,5%** |
| Erro absoluto: mediana / média / p90 | 5,5% / 10,6% / 25,8% |
| Referência ingênua (repetir os 12 meses pré-corte): mediana / erro absoluto mediano | −11,7% / 12,4% |
| Itens em que o decisor errou menos que a referência ingênua | **43 de 50** |
| Observado dentro da faixa [baixa, alta] | **32 de 50**; 8 acima e 10 abaixo |
| Centralizados (39): na faixa / mediana do erro | 27 / −2,1% |
| Descentralizados (11): na faixa / mediana do erro | 5 / −8,5% |

[CALC: e01]

**Itens acima da faixa** (crescimento subestimado):

| Item | Projeção central | Observado | Erro |
|---|---|---|---|
| AP050 dapagliflozina | 50,6 mi | 82,8 mi | −39% |
| AP021 vedolizumabe | 23.017 | 39.601 | −42% |
| AP027 mepolizumabe | 61.358 | 89.348 | −31% |
| AP024 risdiplam | 8.559 | 11.592 | −26% |
| AP014 upadacitinibe | 3,50 mi | 4,71 mi | −26% |
| AP034 omalizumabe | 109.404 | 142.690 | −23% |
| AP085 everolimo | 1,95 mi | 2,19 mi | −11% |
| AP049 leflunomida | 21,03 mi | 23,23 mi | −9,5% |

- Três desses itens (AP050, AP027 e AP034) estão entre os seis que concentram a economia de E2.
- A causa é o limite de crescimento de +30% (H03) somado a uma folga de só 10% na faixa alta (H05). O decisor havia apontado o risco [OBS: `registro_hipoteses.csv`].

**Itens abaixo da faixa:** dez, com erros pequenos (3–13%), exceto AP041 (+24%) e **AP080 alentuzumabe** (+97%; 2.194 projetados contra 1.113 observados) [CALC: e01].

**Leitura:** a projeção de quantidade foi boa no agregado e melhor que a referência ingênua. A faixa, porém, não funciona como intervalo de cobertura: cobriu só 64% dos itens [CALC].

## E2 — Preço de referência × preços observados depois do corte

### Regras usadas na comparação

- **Preço observado para comparar com o decisor** (mesma categoria de valor, homologado ou praticado):
  - itens centralizados: compra DLOG programática na janela H (quantidade ≥10% da dispensação, regra H09 do próprio decisor);
  - itens descentralizados: mediana estadual em H (Compras.gov, `compativel`, sem preço extremo).
- **Correção do avaliador:** excluí 23 registros pós-corte de supositório / uso retal vinculados a AP052 (falha do pacote).
- **BPS:** só conferência, nunca somado.

[CALC: e02]

### Resultado

| Medida | Valor |
|---|---|
| Itens com preço observado em H | 26 de 50 (15 centralizados e os 11 descentralizados) |
| Preço observado / preço do decisor: mediana (p25–p75) | **1,02** (0,96–1,06) |
| Preço observado dentro da faixa do decisor | 19 de 26 |
| BPS / Compras.gov em H (medianas; n=43): mediana (p10–p90) | 1,00 (0,62–1,22). Sem esfera federal no BPS pós-corte |

### Principais desvios

| Item | Decisor | Observado | Razão | Leitura |
|---|---|---|---|---|
| AP002 adalimumabe (1A) | 126,94 (DLOG Pfizer, 2024) | 416,31 (DLOG Fundação Butantan, mar/2025) | ×3,28 | troca de fornecedor/PDP; o histórico pré-corte já mostrava 417 em 2022 [OBS] |
| AP059 deferasirox (1A) | 6,38 (DLOG 2023) | 11,29 (DLOG mai/2025) | ×1,77 | renovação muito acima da faixa H11 |
| AP044 cinacalcete (1A) | 0,68 | 1,24 | ×1,82 | dentro da faixa ampliada pela regra D08 |
| AP034 omalizumabe (1B) | 1.841,49 (estadual 24m) | ~690–700 a partir de mai–jul/2025; mediana estadual em H = 699,76 | ×0,38 | queda de preço do monopolista no status quo, sem compra nacional; o DLOG pagou depois 500,00 (ago/2026, 12.600 un.) [OBS] |
| AP052 mesalazina 500 mg (2) | 3,815 | 1,371 (BPS em H: 1,28) | ×0,36 | o desvio vem da contaminação do pacote por supositório; sem ela, a referência pré-corte seria 2,47 [CALC: p01] |
| AP016 quetiapina 200 mg (1A) | 0,93 | 0,75 | ×0,81 | redução |

- **Itens 1A sem DLOG em H (24):** preço não observado no horizonte.
- **Compras DLOG depois do horizonte (proxy, fora da janela)** mostram que a hipótese H18 do decisor superestimou alguns itens sem DLOG visível:
  - AP049 leflunomida: 0,76 contra 3,14;
  - AP030 sevelamer: 1,29 contra 2,25.
- Em outros, o proxy fica acima da referência do decisor:
  - AP012 ustequinumabe: 5.112 contra 3.209 [OBS: e02, colunas `dlog_X_*`].

## E3 — Custo projetado × valor de referência observado

- **Definição:** valor de referência observado = quantidade SIA observada × preço observado. É **homologado/praticado, nunca pagamento**.
- **Cascata quando não há preço observado em H:**
  1. último preço DLOG contratado depois do horizonte (10 itens, marcado como proxy);
  2. preço do decisor mantido (14 itens).

[CALC: e03 → `trabalho/e03_custo.csv`, `trabalho/e03_custo_totais.csv`]

| Bloco | E1 projetado (soma p50, R$ mi) | E2 projetado (R$ mi) | Q observada × P do decisor | **Referência observada (R$ mi)** | E2 proj./ref. − 1 | Parcela da referência com preço observado em H |
|---|---|---|---|---|---|---|
| Cesta (50) | 6.465 | 6.243 | 6.511 | **6.761** | −7,7% | 61,5% |
| Centralizados (39) | 5.268 | 5.268 | 5.162 | **5.617** | −6,2% | 53,7% |
| Descentralizados (11) | 1.197 | 975 | 1.349 | **1.144** | −14,8% (E1: +4,7%) | 100% |
| Só itens com preço observado em H (26) | 3.711 | 3.489 | 3.826 | **4.160** | −16,1% | 100% |

**Leitura:**

1. **Centralizados.** A projeção ficou abaixo da referência observada sobretudo por AP002: +R$ 0,50 bi só nesse item (712,6 mi observados contra 210,3 mi projetados). O efeito quantidade sozinho quase não pesa (5.162 contra 5.268) [CALC].
2. **Descentralizados** (o que a decisão de fato muda). No status quo efetivamente observado:
   - a quantidade foi maior que a projetada (1.349 mi a preços do decisor contra 1.197 mi);
   - o preço foi menor, por causa de AP034 e AP052;
   - os dois efeitos quase se compensam: a referência observada é 1.144 mi, 4,7% abaixo do E1 projetado [CALC].
3. **Faixas por item.** A faixa p05–p95 de E2 cobre a referência observada em 22 de 50 itens; a de E1, em 23 [CALC].

## E4 — Contexto orçamentário federal (agregado, sem item; não somado a nada)

| Ação 4705 | 2024 | 2025 | 2026 (parcial) |
|---|---|---|---|
| Dotação atualizada | 13,74 bi | 15,49 bi | 17,52 bi |
| Empenhado | 13,74 bi | 15,49 bi (+12,7%) | 16,04 bi |
| Realizado (Portal) | 9,92 bi | 12,85 bi (83% do empenhado) | 12,36 bi |

[OBS/CALC: `dados_reservados/orcamento_acoes_af_2025.csv` e `_2026.csv`, `trabalho/e04_orcamento.csv`]

- A LOA 2025 não comprimiu a ação 4705: o empenhado cresceu 12,7%. A premissa do decisor de que E2 não depende do orçamento federal não foi testada pela realidade, mas também não foi contrariada [INF].
- O custo projetado dos centralizados (5,27 bi, valor de contratação) equivale a 34% do empenhado de 2025. É só ordem de grandeza: são categorias diferentes, e a ação 4705 cobre muito mais que 39 itens [CALC].

## Limitações desta comparação

1. **Preço observado só para parte da cesta:** 24 dos 39 centralizados não têm compra DLOG programática em H. A referência observada desses itens usa um proxy posterior ou o preço do decisor (38,5% do valor da cesta).
2. **Uma compra DLOG em H não é o preço de todo o consumo do ano.** Contratos e atas de 2024 podem ter abastecido parte de 2025 (caso de AP002) [INF].
3. **SIA é demanda atendida**, com meses recentes sujeitos a reprocessamento.
4. **E2 não foi executada.** O mundo observado é o status quo (E1). Não há preço observado de "SRP nacional" para os 11 itens no horizonte: as compras DLOG desses itens em H são pequenas, provavelmente judiciais (AP027: 25 un.; AP050: 180 un.; AP034: 12–26 un.) [OBS: e02].
