# 03 — Comparação das estratégias

Fonte dos números: `trabalho/03_estrategias.py` (Monte Carlo, N=4.000, semente fixa, números aleatórios comuns entre estratégias), resumido em `saida/03_comparacao.csv` e `trabalho/mc_resumo.txt`. Sensibilidade: `trabalho/04_sensibilidade.py` → `trabalho/sensibilidade.csv`.

**Categoria de valor de todos os custos:** valor estimado de contratação no horizonte (preço homologado projetado × quantidade planejada). Não é pagamento, não é orçamento e não é valor financiado SIA.

## 1. Critério de eficiência (decisão D06)

A estratégia mais eficiente é a que **minimiza o custo esperado de contratação para cobrir a necessidade projetada da cesta inteira em 12 meses**, desde que cumpra três condições:

1. **Viabilidade (filtro eliminatório):** a estratégia precisa ser jurídica, federativa e orçamentariamente executável dentro do horizonte, sem mudar normas que a coordenação não controla sozinha.
2. **Risco de abastecimento não pior que o da linha de base.** O risco entra de duas formas:
   - qualitativa: concentração de fornecedor, número de processos, transição;
   - quantitativa: a **probabilidade de fracasso do certame que anularia a economia** (ponto de equilíbrio).
3. **Robustez:** a ordenação precisa se manter em toda a faixa de incerteza (p05–p95 e cenários de sensibilidade).

**Por que este critério:**

- O objetivo do enunciado é abastecimento contínuo com o uso mais eficiente dos recursos. A cobertura projetada é a mesma em todas as estratégias, porque a quantidade planejada é a mesma. Então a eficiência se reduz a custo por unidade coberta, condicionado ao risco.
- Uso o custo consolidado das três esferas porque o recurso é público, independentemente de quem paga. A distribuição entre esferas aparece à parte.

## 2. Custos (R$ milhões, p50 com faixa p05–p95)

| Estratégia | Custo total da cesta | Itens centralizados (iguais) | Itens descentralizados (11) | Economia potencial vs. E1 no horizonte | % dos descentralizados |
|---|---|---|---|---|---|
| **E1 status quo** | 6.475 (5.930–7.185) | 5.281 | 1.197 (1.075–1.351) | — (referência) | — |
| **E2 SRP nacional compartilhado** | **6.255 (5.731–6.935)** | 5.281 | **975 (860–1.116)** | **221 (159–298)** | **18,4%** |
| E3 blocos regionais | 6.358 (5.827–7.055) | 5.281 | 1.081 (961–1.231) | 116 (63–180) | 9,7% |
| E4 federalização | 6.418 (5.879–7.126) | 5.281 | 1.138 (1.011–1.294) | 60 (6–119) | 5,0% |
| E2, regime pleno de 12 meses (referência) | 6.071 (5.566–6.731) | 5.281 | 793 (698–912) | 405 (337–483) | 33,9% |
| E3, regime pleno (referência) | 6.184 (5.671–6.859) | 5.281 | 906 (807–1.031) | 292 (241–350) | 24,4% |

[CALC: `saida/03_comparacao.csv`]

- A faixa do custo total vem sobretudo da quantidade (faixas comonotônicas, de propósito conservadoras) e do preço dos centralizados.
- A faixa da **economia** é mais estreita porque usa números aleatórios comuns.
- A ordenação **E2 < E3 < E4 < E1** em custo vale em todos os percentis: o p05 da economia de E2 (159) passa o p95 da de E4 (119) e fica perto do p95 da de E3 (180).

## 3. Sensibilidade da economia de E2 (determinística, valores centrais; `trabalho/sensibilidade.csv`)

| Cenário | Economia E2 (R$ mi) | % dos descentralizados |
|---|---|---|
| Central (parcela sob a ata nacional s=0,55; β central) | 203 | 17,9% |
| β no limite menos negativo do IC90 | 176 | 15,5% |
| β no limite mais negativo do IC90 | 243 | 21,4% |
| Transição lenta (s=0,40) / rápida (s=0,70) | 148 / 259 | 13,0% / 22,8% |
| Quantidade baixa / alta | 181 / 248 | 15,9% / 21,8% |
| Preço de base no p75 estadual | 241 | 21,2% |
| **β = 0 (nenhum efeito volume)** | **0** | 0% |
| Otimista: preço nacional na razão DLOG/estadual observada (0,29) | 444 | 39,1% |

- O cenário otimista é só um limite superior. **Não é usado** no valor central, porque o diferencial do MS inclui PDP e negociação de fonte única, que não se transferem automaticamente.
- **Ponto de equilíbrio do risco:** a economia de E2 só desaparece se a **probabilidade de fracasso do certame nacional passar de ~41%**. Isso supõe que, no fracasso, as SES compram em caráter emergencial ao p75 estadual [CALC: `pf_equilibrio_E2` em `trabalho/mc_resumo.txt`; HIP H20].

## 4. Riscos e viabilidade

| Dimensão | E1 | E2 | E3 | E4 |
|---|---|---|---|---|
| Jurídica | alta | alta (Lei 14.133, art. 86; Dec. 11.462/2023) | alta (Lei 11.107/2005 [CP]) | **baixa no horizonte** (alterar a PRC 2/2017) |
| Federativa | alta | média-alta (adesão voluntária; CIT; a SES continua contratante) | média (5 arranjos interestaduais) | baixa (muda quem financia o Grupo 2) |
| Operacional | alta | média (capacidade do DLOG; 4–8 meses) | média-baixa (montar estruturas) | média (a DLOG já distribui os 1A) |
| Orçamentária | alta | alta (não muda quem paga) | alta | **baixa** (LOA 2025 não aprovada; mais despesa para a União) |
| Mercado / abastecimento | média: 27 certames e dispersão de preço | média: concentração nacional; mitigada com cadastro de reserva, cotas e contratos estaduais vigentes como ponte | baixa-média: fornecedores diversificados | média-alta: transição e concentração |
| Principal risco | preço alto e heterogêneo; falhas locais isoladas | falha única afeta o país; recurso administrativo atrasa o certame | economia menor; poucas regiões prontas | inviável no prazo |

[INF/HIP: classificação qualitativa, justificada nas linhas e em `02_estrategias.md`]

## 5. Conclusão da comparação

- **E4** cai no filtro de viabilidade (jurídica e orçamentária no horizonte).
- Entre as viáveis, **E2 tem o menor custo em todo o intervalo**. O risco de concentração é mitigável e o ponto de equilíbrio (~41% de probabilidade de fracasso) está muito acima do plausível [HIP: avaliação; não há taxa de fracasso no pacote].
- **E3** é a segunda melhor e serve de contingência regional se as SES não aderirem a E2.
