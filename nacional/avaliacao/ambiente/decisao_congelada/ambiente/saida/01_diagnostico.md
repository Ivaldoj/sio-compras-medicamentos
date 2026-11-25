# 01 — Diagnóstico: leitura do problema, dados, qualidade e lacunas

Data de decisão: **29/01/2025**. Horizonte: **fev/2025 a jan/2026**. Abrangência: as 27 UFs.
Legenda: **[OBS]** observado; **[CALC]** calculado (script indicado); **[INF]** inferido; **[HIP]** hipótese (id em `registro_hipoteses.csv`); **[CP]** conhecimento prévio válido em 29/01/2025.

## 1. Leitura do problema

- A cesta tem 50 apresentações do CEAF: **38 do Grupo 1A, 6 do 1B e 6 do 2** [OBS: `cesta.grupo_financiamento`]. O grupo foi atribuído por correspondência textual com a RENAME 2024, sem validação humana (`grupo_metodo`) [OBS: LEIA-ME §3].
- Quem compra o quê está fixado [OBS: `restricoes.csv`, PRC GM/MS 2/2017, art. 49]:
  - Grupo 1A: o MS compra de forma centralizada e entrega às SES.
  - Grupo 1B: as SES compram com financiamento federal transferido (valores SIA).
  - Grupo 2: as SES financiam e compram.
  - Em todos os grupos, as SES programam, armazenam, distribuem e dispensam.
- O municípios não têm competência de compra no CEAF [INF: não aparecem nas competências de `restricoes.csv`]. As compras municipais na base de preços servem só como referência de mercado.
- A decisão real está nos itens comprados de forma **descentralizada**, onde 27 compradores adquirem o mesmo produto. Nos itens 1A, a compra já é centralizada e o espaço de decisão é tático: renovar, negociar, parcelar.

## 2. Dados usados

| Tabela | Uso | Filtro / colunas |
|---|---|---|
| `problema/cesta.parquet` | grupo, dispensação 12m e ano anterior, SIA 1B, tetos CMED | todas as 50 linhas |
| `problema/demanda_mes.parquet` | nível recente e sazonalidade | 12 meses de processamento, nov/2023 a out/2024 |
| `problema/demanda_uf.parquet` | volume por UF e por região, para os arranjos E1 e E3 | `dispensacao_12m_pre_corte` |
| `problema/recursos_federais.csv` | contexto orçamentário da União | ação 4705, 2023–2024 |
| `problema/restricoes.csv` | competências e regras legais | todas |
| `mercado/precos_comprasgov.parquet` | **base principal de preço** | `compatibilidade='compativel'`, `flag_preco_extremo=False`, `dataResultado` de 2022-02-01 a 2025-01-29 (modelo) e desde 2023-02-01 (referências de 24 meses) |
| `mercado/precos_bps.parquet` | **apenas conferência**, nunca somada ao Compras.gov | `NOT flag_preco_extremo AND NOT flag_duplicata_negocio`, `data_compra >= 2023-02-01` |
| `mercado/cmed_teto.parquet` e colunas `teto*` da cesta | teto legal de preço | lista CMED de 06/01/2025 |

Scripts (executar da raiz com `python -I -X utf8 trabalho/<script>.py`, nesta ordem):

| Script | O que faz | Saídas |
|---|---|---|
| `00_explorar.py` | exploração | `trabalho/explora_*.csv` |
| `01_demanda.py` | projeção de quantidade | `trabalho/demanda_projecao.csv`, `trabalho/demanda_uf_projecao.csv` |
| `02_precos.py` | preços de referência e efeito volume-preço | `trabalho/precos_referencia.csv`, `trabalho/elasticidade.csv` |
| `03_estrategias.py` | custos por estratégia (Monte Carlo) | `saida/03_comparacao.csv`, `saida/plano_por_apresentacao.csv`, `trabalho/mc_resumo.txt` |
| `04_sensibilidade.py` | análise de sensibilidade | `trabalho/sensibilidade.csv` |

## 3. Achados principais

1. **Os preços nos itens descentralizados sobem no tempo e variam muito entre compradores.**
   - Exemplos de mediana estadual em 24 meses [CALC: `02_precos.py`]: mesalazina 500 mg tem p25 de R$ 1,84 e p75 de R$ 4,50; mepolizumabe tem p25 de R$ 1.941 e p75 de R$ 3.352.
   - Nos 1A, **o MS compra muito abaixo dos estados.** Nos 27 itens com compra programática do MS e ao menos 3 compras estaduais, o preço DLOG fica em mediana a **0,29× da mediana estadual** (p25 0,24; p75 0,53) [CALC: `03_estrategias.py`, `trabalho/mc_resumo.txt`].
   - Esse diferencial mistura três efeitos: volume, negociação nacional e PDP/fonte pública (ex.: tofacitinibe da Fiocruz a R$ 14,40 contra mediana estadual de R$ 74) [OBS: `precos_comprasgov`, AP011].
2. **O efeito volume-preço é mensurável.** Regressão log-log com efeito fixo de item e de ano, em 4.860 registros [CALC: `trabalho/elasticidade.csv`]:

   | Segmento | β | IC90 | Registros | Itens |
   |---|---|---|---|---|
   | concorrencial (≥3 laboratórios CMED) | −0,085 | −0,118 a −0,072 | 3.495 | 23 |
   | concentrado (≤2 laboratórios) | −0,080 | −0,099 a −0,067 | 1.365 | 27 |

   Decuplicar o volume de uma compra reduz o preço em cerca de 17–18%. É associação de corte transversal, não efeito causal comprovado [HIP H16].
3. **A dispensação cresce, e há um degrau em jun/2024.**
   - A partir de jun/2024 (7º mês da série), quase todos os itens sobem 5–10% de patamar [OBS: `demanda_mes`; CALC: `00_explorar.py`].
   - Itens recém-incorporados crescem muito: risdiplam 259 → 5.424 frascos; eculizumabe 4.866 → 26.175; dapagliflozina ×2,2; upadacitinibe ×2,3 [OBS: `cesta`, d12 contra ano anterior].
4. **Custo estimado da cesta na linha de base (E1)**, em valor de contratação [CALC: `03_estrategias.py`]:
   - total: R$ 6,48 bi (p05–p95: 5,93–7,18);
   - 39 itens centralizados no MS: R$ 5,28 bi;
   - 11 itens descentralizados: R$ 1,20 bi (1,07–1,35).

   Para comparação, sem somar: o custo dos centralizados equivale a **38% do empenhado da ação 4705 em 2024** (R$ 13,74 bi). São categorias diferentes, e a comparação serve só como ordem de grandeza [CALC].

## 4. Qualidade dos dados e problemas encontrados

| # | Problema | Evidência | Tratamento |
|---|---|---|---|
| Q1 | **Dispensação atendida ≠ demanda total.** A necessidade não atendida e o estoque inicial são desconhecidos | LEIA-ME §4 | faixa de quantidade com +10% na alta [HIP H01, H05, H06] |
| Q2 | Mês de processamento ≠ mês de dispensação; a base SIA inclui reprocessamentos feitos depois do corte ("base atual com reprocessamentos") | `cesta.base_disponibilidade` | usado como está. Possível vazamento temporal pequeno, registrado [HIP H02] |
| Q3 | Grupo de financiamento atribuído por texto. **AP007 (imunoglobulina) aparece como 1B**, mas o MS compra ~751 mil frascos/ano (2024) de forma centralizada e o SIA 1B aprovou só R$ 14 mil (R$ 0,03/unidade) | `cesta`, `precos_comprasgov` (DLOG) | tratado como centralizado, com verificação obrigatória [D07, HIP H19] |
| Q4 | `unidade_dispensacao` ausente (8 itens) ou mal extraída ("biossimilar a": AP001, AP002) | `cesta` | apontado em `plano_por_apresentacao.csv` |
| Q5 | **Vínculo CATMAT ambíguo.** AP012 (ustequinumabe 45 mg/0,5 mL) usa CATMAT "90 mg/mL", que também cobre a seringa de 90 mg. A mediana de mercado (R$ 23.846) passa do teto CMED (R$ 21.340); o MS paga R$ 3.208,85 | `precos_comprasgov`, `cesta` | referência = DLOG. Item marcado |
| Q6 | `flag_preco_extremo` marca compras programáticas do MS (AP041, AP044), porque a mediana de referência é dominada por compras pequenas | `precos_comprasgov` | compras DLOG mantidas, com faixa superior = preço do modelo [D08] |
| Q7 | Compras do MS com poucas unidades (ex.: AP027 com 7 unidades; AP034 com 51) são provavelmente judiciais e não programáticas | `precos_comprasgov` | só conta como "programática" a compra DLOG com quantidade ≥10% da dispensação anual [HIP H09] |
| Q8 | BPS diverge do Compras.gov em 6 itens. Em geral, mediana BPS/CG = 0,95 (p10 0,75; p90 1,47; n=42). Fora de [0,67; 1,5]: AP001, AP008, AP012, AP027, AP042, AP068 | `04_sensibilidade.py` | BPS não é somado. A divergência é anotada no plano |
| Q9 | ICMS: a alíquota de cada UF não está no pacote | `restricoes.csv` | teto com 18% como aproximação para produtos fora do Convênio 87/02 [HIP H10] |
| Q10 | `recursos_federais.csv` 2024 foi "baixado em 2026 (valores finais)". Em 29/01/2025 o exercício já estava encerrado, mas o fechamento ainda podia ter ajustes | arquivo | usado só como ordem de grandeza. Possível vazamento temporal pequeno, registrado |
| Q11 | 9 itens 1A não têm compra programática do MS na base: AP004, AP005, AP010, AP022, AP030, AP035, AP049, AP063, AP082. Pode ser compra por outra UASG, PDP fora da base ou vínculo de CATMAT falho | `precos_comprasgov` | preço por hipótese: mediana × efeito volume nacional [HIP H18] |
| Q12 | Não há registros duplicados dentro do Compras.gov: `idItemCompra` é único (5.447/5.447) | `00`/consulta | — |

## 5. Lacunas: tratadas como incerteza, sem dados inventados

| Lacuna | Tratamento |
|---|---|
| Orçamento de 2025 (LOA ainda não aprovada) | viabilidade orçamentária avaliada qualitativamente; o empenho de 2024 entra só como ordem de grandeza |
| Financiamento estadual do Grupo 2 e contrapartidas | não quantificados |
| Estoques iniciais | estoque neutro [HIP H06] |
| Contratos e atas vigentes | a transição entra como parcela do volume que já passa pela nova estratégia no horizonte [HIP H13–H15] |
| Capacidade dos fornecedores e eventos de desabastecimento | não observados [HIP H23]. Medida de risco: número de laboratórios CMED e de fornecedores distintos em 24 meses |
| Preços futuros | reajuste de 0–5% [HIP H12]. **Não uso** o índice de ajuste CMED de 2025, pois não era conhecido em 29/01/2025 |
| Alíquotas de ICMS por UF | aproximação de 18% [HIP H10] |
| Demanda não atendida | +10% na faixa alta [HIP H05] |
