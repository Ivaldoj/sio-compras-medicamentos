# 05 — Lacunas informacionais e riscos metodológicos

## 1. O que falta para uma decisão real de compras

| Informação necessária | Situação | Melhor aproximação encontrada | Onde poderia ser obtida |
|---|---|---|---|
| Necessidade por medicamento (quantidade a adquirir no período) | **Ausente** como dado direto | Quantidades licitadas nos editais (MT/PNCP) = necessidade declarada pelo órgão no momento do edital | Termos de referência / ETP anexos no PNCP (`/arquivos`); planilhas de programação da Assistência Farmacêutica (pedido via LAI) |
| Consumo/dispensação histórica | **Ausente** em dados abertos | — | Hórus/BNAFAR (dispensação não exposta na API); pedido via LAI à SES ou SMS |
| Estoque | **Parcial** | Posição atual por lote (BNAFAR/Hórus), sem histórico; muitos lotes vencidos | Série histórica via LAI / BNAFAR |
| Orçamento para medicamentos | **Parcial** | Municípios: empenhado/liquidado/pago em "material farmacológico" (TCE-PB); SES-PB: linha agregada de R$ 756,6 mi no PCA 2026 | LOA/QDD estadual e municipal; Portal da Transparência PB (não extraído) |
| Orçamento disponível por medicamento | **Inexistente** nas fontes | — | Não é publicado; exigiria hipótese explícita de rateio |
| Preços de referência | **Disponível** com ressalvas | BPS (praticado), MT/PNCP (estimado e homologado), CMED (teto) | — |
| Instrumentos vigentes (atas/contratos) | **Parcial** | PNCP `/contratos`, `/atas`, resultados por item; MT traz SRP=True | PNCP (consultas por órgão e período) |
| Disponibilidade atual no mercado | **Ausente** | Itens fracassados (568) e desertos (208) como sinal de dificuldade de fornecimento | Anvisa (descontinuação), fornecedores |
| Prazos de entrega e condições | **Ausente** em dados estruturados | — | Editais/termos de referência (PDF) |
| Desabastecimento | **Não verificado** | Programa "JUDICIALIZAÇÃO" no estoque; compras judiciais no BPS (3.367) | Anvisa, CONASS/CONASEMS, notícias oficiais |

## 2. Riscos metodológicos

| Risco | Identificado nos dados? | Evidência | Impacto | Mitigação necessária | Mitigação realista? |
|---|---|---|---|---|---|
| 1. Ausência de demanda real | **Sim** | Nenhuma fonte traz consumo; PCA da SES-PB agrega medicamentos em uma linha | Alto: sem demanda, qualquer "plano" é arbitrário | Usar quantidades licitadas de um edital real como necessidade declarada; complementar com estoque BNAFAR | **Parcial** — viável usando um edital concreto como caso |
| 2. Ausência de orçamento | **Sim** | Só agregados (subelemento TCE-PB; linha PCA) | Alto | Usar o valor estimado do edital, ou o empenhado anual em material farmacológico, como teto — declarado como hipótese | **Parcial** |
| 3. Incompatibilidade de produtos | **Sim** | 250 CATMAT com >1 unidade; 330 grafias de unidade no MT; capacidade nula em 63% | Alto para preço | Comparar só CATMAT + unidade (+ capacidade); conversões documentadas | **Sim**, com trabalho manual em um elenco pequeno |
| 4. Preço histórico ≠ condição atual | **Sim** | Defasagem BPS mediana 111 dias; preços por data; CMED só vigente | Médio-alto | Datar cada referência; corrigir por índice declarado; usar CMED como teto | **Sim** |
| 5. Duplicidade entre fontes | **Sim (potencial)** | 5 casos confirmados BPS=MT; 391 ocids repetidos entre coletas; 306 duplicatas suspeitas no BPS | Médio | Não somar fontes; deduplicar por ocid; marcar duplicatas BPS | **Sim** |
| 6. Falta de dados de consequência | **Sim** | Sem prazos, entregas, rupturas | Alto para avaliar continuidade | Proxies: taxa de itens fracassados/desertos por CATMAT; número de fornecedores; lotes vencidos | **Parcial** |
| 7. Avaliação independente inviável | **Parcial** | Há referências externas (BPS mediana, CMED, homologado) | Médio | Definir antes do experimento a referência e as métricas; avaliar contra o resultado homologado real do edital | **Sim** se o caso for um edital já homologado |
| 8. Economia potencial ≠ realizada | **Sim** | Razão adjudicado/estimado mediana 0,80: a "economia" já acontece no pregão | Alto para interpretação | Reportar só "diferença contra referência"; nunca chamar de economia para o SUS | **Sim** (regra de redação) |

## 3. Não resolvido nesta etapa

- Significado de `validade_compra`, `vl_capacidade`, sufixo `U00xx` do código BR no BNAFAR, código `EX` no MT.
- Execução orçamentária estadual da SES-PB (não extraída).
- Dispensação/consumo (não localizado).
- 3 arquivos do MT inexistentes no bucket (DF e GO 2024-02; entrada duplicada de TO 2025-01) — problema da fonte.
- Causa dos picos de volume nas coletas 2025-03 e 2025-09 do MT.
- No nível nacional do MT só foram lidas as tabelas `releases` e `ten_items` (cobertura); adjudicações e preços foram analisados só na PB.
