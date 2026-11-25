# 07 — Qualidade do pacote de decisão e impacto das falhas

- **Fontes:** `codigo_preparacao/n03_pacote_nacional.py` e as evidências primárias.
- **Checagens:** `trabalho/p01_pacote.py` (relato em `trabalho/p01_pacote.txt`), `trabalho/d01_rename.py`, `trabalho/e01_demanda.py` e `trabalho/c01_calculos.py`.

## Conferências que passaram

| Item | Resultado | Evidência |
|---|---|---|
| Dispensação SIA pré-corte (12m e ano anterior) | confere com o TabNet bruto em todos os 50 itens | [CALC: e01] |
| Dispensação e valor SIA pós-corte (reservados) | conferem com o TabNet bruto, total e por UF | [CALC: e01] |
| Teto CMED por unidade (0% ICMS; PMVG se CAP, PF caso contrário) | 411/411 apresentações conferem com `cmed_pmvg_20250107.xls` | [CALC: p01 §6] |
| Execução 4705/2024 em `recursos_federais.csv` | confere com `orcamento_despesa_2024.zip` | [CALC: p01 §5] |
| Separação temporal Compras.gov (pacote × reservado) | `idItemCompra` sem interseção (verificação do próprio n03) e sem duplicatas internas | [OBS: n03; CALC: c01 C19] |
| CATMAT compartilhado entre apresentações | nenhum | [CALC: c01 C30] |

## Falhas encontradas

| # | Falha | Evidência | Impacto na decisão |
|---|---|---|---|
| P1 | **Grupo de financiamento errado de AP007** (imunoglobulina 5 g): o pacote diz 1B; a RENAME 2024, Anexo III, **p. 209 do PDF**, diz **1A**. O método "1º grupo do trecho da substância" pegou o grupo da apresentação de 0,5 g | [OBS: `trabalho/d01_rename_trechos.txt`; `cesta.grupo_metodo`] | **Neutralizado pelo decisor**, que tratou AP007 como centralizado com base nos dados (D07). Se ele tivesse aceitado o 1B, AP007, de R$ 0,77 bi, entraria nos descentralizados e inflaria a economia de E2. 12 itens usam o mesmo método frágil. Conferi 10 deles na RENAME: AP001, AP003, AP016, AP035, AP053, AP055, AP059, AP068 e AP085 são 1A, e AP070 é 2, todos consistentes. AP012 não foi localizado na extração |
| P2 | **Regra de compatibilidade aceita `SUPOSITÓRIO` como unidade de item sólido oral** (`UN_SOLIDA` em n03) e vincula a AP052 (mesalazina 500 mg comprimido LP) o CATMAT 352414 "uso retal" | [CALC: p01 §1: 21 registros pré-corte e 23 pós-corte] | A referência estadual de AP052 sobe de 2,47 para 3,815 (+54%). A economia central de E2 aumenta ~6 milhões (3%). O decisor leu a amplitude como dispersão de mercado. A comparação ex post de AP052 também fica distorcida se não for corrigida |
| P3 | **CATMAT de AP012** (ustequinumabe 45 mg) é "90 mg/mL" e mistura as seringas de 45 e 90 mg: a mediana passa do teto | [OBS: `trabalho/c00_catmat_por_item.txt`] | Detectado e tratado pelo decisor, que usou o preço DLOG. Sem efeito na recomendação; a referência de AP012 continua incerta (DLOG pós-corte: 5.112) |
| P4 | **`flag_preco_extremo` usa a mediana de todas as esferas** e marca compras DLOG programáticas (8 de 105; AP041, AP044) | [CALC: p01 §4] | Detectado e tratado pelo decisor (D08). Sem efeito relevante |
| P5 | **`unidade_dispensacao` vazia em 8 itens** e "biossimilar a" em 2 (AP001, AP002) | [CALC: p01 §3] | Só documental; os preços usam o vínculo CATMAT. Apontado pelo decisor |
| P6 | **SIA "base atual com reprocessamentos"** usada também no pré-corte: possível vazamento temporal pequeno | [OBS: `cesta.base_disponibilidade`] | Declarado pelo decisor (H02). Impacto provavelmente pequeno, mas não mensurável sem a base histórica [INF] |
| P7 | **`recursos_federais.csv` de 2024 baixado em 2026** ("valores finais"; zip de 24/11/2026) | [OBS: p01 §5] | Vazamento mínimo, porque o exercício estava encerrado. Usado só como ordem de grandeza. Declarado pelo decisor |
| P8 | **ICMS:** o pacote não traz a alíquota por UF; a lista primária tem colunas de 20%, 20,5%, 21% e 22% | [OBS: p01 §6] | A aproximação de 18% subestima o teto em algumas UFs. Sem efeito: nenhum preço projetado chega ao teto (C25) |
| P9 | **Seleção da cesta por relevância** = quantidade × mediana de **todas** as esferas, com ≥5 preços compatíveis | [OBS: n03] | Viés de seleção para itens caros e com mercado ativo. Não afeta a lógica da decisão, mas limita a generalização |
| P10 | **BPS pós-corte sem esfera federal e sem flag de compatibilidade**; datas em texto dd/mm/aaaa | [OBS: `precos_bps_2025_2026.parquet`] | Limita a conferência E2 dos itens 1A. Tratado pelo avaliador com filtro por unidade |
| P11 | **Lista CMED citada como de 06/01/2025**; o arquivo primário é `cmed_pmvg_20250107.xls` | [OBS] | Diferença de rótulo, sem efeito (os valores conferem) |

## Conclusão sobre o pacote

- O pacote é, em geral, **fiel às fontes primárias**: SIA, CMED e orçamento conferem.
- Tem **duas falhas de vínculo com efeito material**:
  - P1 (grupo de AP007), que o decisor neutralizou;
  - P2 (supositório em AP052), que passou e infla levemente a economia projetada.
- As demais falhas são documentais ou de baixo impacto e, em geral, foram declaradas pelo decisor.
- Nenhuma falha do pacote muda a recomendação [CALC: `05_sensibilidade.md`].
