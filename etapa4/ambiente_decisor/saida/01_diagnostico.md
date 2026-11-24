# 01 — Diagnóstico: o problema, os dados e suas lacunas

Data de decisão: **29/01/2025**. Todos os números vêm do pacote `data/decision_input/` ou dos scripts em `trabalho/`. Classes: **OBS** = observado; **CALC** = calculado por script; **INF** = inferido; **HIP** = hipótese (ver `registro_hipoteses.csv`); **CP** = conhecimento prévio (norma vigente em 29/01/2025).

## 1. Leitura do problema

| Afirmação | Classe | Fonte |
|---|---|---|
| A necessidade tem 334 itens, quantidades anuais estimadas "baseadas na utilização anual dos anos anteriores" e valor estimado de R$ 4.952.438,00 | OBS | `itens` (soma de `valor_total_estimado_orgao`), `LEIA-ME.md` §1; conferido em `trabalho/01_explora_itens.txt` |
| Nenhum item tem dado de consumo que sustente a quantidade (`status_necessidade` = "documentada (TR) — consumo que a sustenta ausente" em 334/334) | OBS | `trabalho/01_explora_itens.txt` |
| Composição por unidade: comprimidos 159 itens (34,9% do valor), "Unidade" 4 itens (27,7%), frascos 77 (25,5%), ampolas 59 (3,6%), demais 35 | OBS | idem |
| Seis insulinas (itens 194–199) somam R$ 1.407.331 (28,4% do valor); só a caneta de NPH (item 196) soma R$ 1.158.120 (23,4%) | CALC | `trabalho/40_numeros_texto.txt` |
| Gasto efetivo com medicamentos em 2024: R$ 1.953.288,72 empenhados, dos quais R$ 1.223.231,57 (62,6%) pelo PE 12/2024 (maior desconto sobre a tabela CMED, 1 credor) e R$ 656.016,25 pelo PE 01/2024 (9 credores) | OBS/CALC | `execucao_2024_licitacao`; `trabalho/40_numeros_texto.txt` |
| A estimativa de 2025 equivale a 2,54 vezes o gasto de 2024 | CALC | `trabalho/40_numeros_texto.txt` |
| Em 2024 não houve empenho em janeiro e março e houve só R$ 25,8 mil em abril; o gasto mensal subiu a partir de maio, depois do resultado do PE 12/2024 (11/04/2024) | OBS/INF | `execucao_2024_mensal`, `historico_proprio`. Inferência: o início de 2024 teve suprimento precário enquanto os pregões tramitavam. O mesmo risco existe no início de 2025 |
| O repasse federal da Assistência Farmacêutica em 2024 (R$ 191.055,78) cobre 9,8% do gasto de 2024. O resto vem de recursos próprios ou de outras fontes | OBS/CALC | `recursos.csv`, `receitas_sus_2024`; `trabalho/40_numeros_texto.txt` |
| Saldo das dotações e estoque inicial são desconhecidos | OBS | `recursos.csv` |
| Restrições operacionais: não há local adequado de armazenamento; a entrega é no endereço da SMS; a validade mínima na entrega é de 75% da vida útil ou mais de 365 dias | OBS | `restricoes.csv` |

**Leitura (INF).** O problema não está em escolher uma modalidade para um valor conhecido. A própria referência de valor está comprometida:
1. a estimativa do órgão fica acima do teto legal em 41 itens;
2. ela fica, em mediana, **2,04 vezes** acima dos preços praticados por outros compradores públicos;
3. não há dado de consumo nem de estoque.

Por isso a decisão precisa de três coisas: uma forma de compra que não obrigue a comprar a quantidade estimada (demanda incerta); entregas parceladas (não há armazém); e um valor de referência saneado.

## 2. Dados usados

| Fonte (tabela do pacote) | Uso | Observação de qualidade |
|---|---|---|
| `itens` (334) | necessidade, estimativa do órgão, status, tetos do pacote | estimativa do órgão sobre-estimada (ver §3.1) |
| `v_bps_comparavel`, `v_comprasgov_comparavel` | preço praticado compatível (referência central) | 247 itens com pelo menos 1 registro; mediana de 309 registros e 26 UFs por item; 244 itens com 5 ou mais registros nos 24 meses anteriores (`trabalho/11_inspeciona_ref.txt`). Registros com `flag_preco_extremo`, `flag_duplicata_negocio` e `flag_possivel_duplicata_bps` foram **excluídos** |
| `v_bps_a_conferir`, `v_comprasgov_a_conferir` | só sensibilidade | não entram no preço central |
| `v_pncp_comparavel` | referência alternativa (homologado e estimado de outros órgãos) e atas para adesão (E3) | amostra dirigida, não censo |
| `v_cmed_teto_unitario` + `regras_conversao` + `cmed_apresentacoes` | teto por unidade do item (PF; PMVG se CAP; alíquota da PB); modelo de desconto (E2) | nenhum vínculo tem validação humana; 210 vínculos "COM ALERTA" |
| `historico_proprio` | descontos do PE 12/2024; 3 preços homologados no PE 01/2024 | o PE 01/2024 publicou só 4 resultados de 349 itens |
| `execucao_2024_*`, `receitas_sus_2024`, `recursos`, `restricoes` | contexto orçamentário e operacional | sem saldo de dotação |

## 3. Qualidade e lacunas

### 3.1 A estimativa do órgão está sistematicamente inflada (CALC)
- Nos 246 itens com 5 ou mais preços praticados compatíveis, a razão entre a estimativa do órgão e a mediana praticada tem mediana **2,044** (P25 1,61; P75 2,568; P90 3,66). Em 227 desses 246 itens, a estimativa fica acima do P75 do mercado (`trabalho/11_inspeciona_ref.txt`).
- O próprio histórico do órgão confirma o padrão. A estimativa de 2025 é **2,14×** o preço homologado em 2024 no PE 01/2024 para o item 120 e o item 181, e **1,92×** para o item 179 (`trabalho/40_numeros_texto.txt`).
- Há **41 itens** com estimativa acima do maior teto CMED aplicável: os 40 marcados pelo pacote mais o item 210, que entra quando se excluem vínculos COM ALERTA. Esses itens somam R$ 1.932.504 (39,0%), e o excesso sobre o teto é de R$ 1.396.286,80 (`trabalho/30_itens_criticos.txt`).
- Consequência: a estimativa do órgão **não serve** como referência de preço nem como base para medir economia (ver `06_economia.md`).

### 3.2 Lacunas de referência de preço
| Situação | Itens | Valor (estimativa do órgão) | Tratamento |
|---|---|---|---|
| Preço praticado compatível disponível | 247 | R$ 3.044.282 | mediana dos últimos 24 meses (HIP H05) |
| Sem praticado; PNCP homologado ou estimado de outro órgão | 23 | R$ 1.437.257 | mediana PNCP, limitada ao teto; inclui as canetas 196 e 199 |
| Sem praticado; preço homologado no próprio PE 01/2024 | 1 (item 120) | R$ 26.880 | R$ 4,19 (próprio, 02/09/2024) |
| **Sem nenhuma referência externa utilizável** | **63** | **R$ 444.019** | estimativa do órgão ÷ 2,044 (HIP H07), faixa ÷2,568 a ÷1; **pesquisa direta obrigatória antes do edital** |
| Preço praticado só "a conferir" | 25 (dentro dos grupos acima) | R$ 1.470.360 | nunca usados como preço central; cenário de sensibilidade (`05_itens_criticos.md`) |
| Sem teto CMED utilizável (bloqueado, a conferir ou ausente) | 108 | R$ 1.098.600 (22,2%) | sem teto, a referência depende só de preços praticados ou de pesquisa |

Fontes: `trabalho/10_referencias.txt`, `trabalho/30_itens_criticos.txt`, `trabalho/40_numeros_texto.txt`.

### 3.3 Problemas de padronização encontrados (INF, sobre dados OBS)
1. **Itens 194 e 195 (insulinas análogas em caneta).** O pacote junta no grupo "compatível" registros de CATMAT de outro tipo de insulina. O item 194 (ação prolongada) recebe preços do 440255 (análoga rápida) e do 442012 (NPH com sistema de aplicação). O item 195 recebe preços do 442012 e do 468664 (`trabalho/05_insulinas_catmat.txt`, `item_catmat_oficial`). Usei apenas o CATMAT específico de cada um (decisão D04). O item 194 fica com 2 registros (referência fraca) e o 195 com 6.
2. **Item 197 (NPH frasco 10 mL).** Um dos vínculos "exata" é o HUMULIN 70N/30R, uma pré-mistura, não NPH. Sem ele, o teto máximo cai de R$ 63,46 para R$ 50,77, e a estimativa do órgão (R$ 55,49) passa a ficar **acima** do teto (`trabalho/40_numeros_texto.txt`).
3. **Item 268 (ondansetrona ampola).** O menor teto é 31 vezes a mediana praticada, o que sugere erro de fator de conversão. O item foi excluído do modelo de desconto CMED (`trabalho/07_checa_teto.txt`, `10_referencias.py`).
4. **Item 151.** A inspeção amostral por IA aponta um "ERRO" de leitura de "CX C/5 AMP". O vínculo foi excluído do teto.
5. **51 itens** têm o teto alterado quando se excluem vínculos COM ALERTA. Uso o teto "confirmado", sem alerta, e registro a diferença (`trabalho/07_checa_teto.txt`).
6. **Teto e alíquota de ICMS.** Para produtos do Convênio ICMS 87/02, a lista CMED do pacote só publica as colunas "0%" e "Sem Imposto": nenhum dos 2.810 registros do Convênio tem coluna de 20%. Se as condições do Convênio não forem atendidas, o teto a 20% **não está no pacote** (lacuna; `trabalho/13_cmed_convenio.txt`).

### 3.4 Demais lacunas (declaradas, não preenchidas)
- **Consumo real por item, estoque inicial e saldo de dotação.** Desconhecidos (OBS). Tratamento: estratégia sem compromisso de quantidade e cenários de demanda de 75%, 100% e 125% do ETP (HIP H12).
- **Preços que o mercado ofertará e desabastecimento.** Desconhecidos (H03, H04). Tratamento: faixas P25–P75 e risco de deserto por item.
- **Atas vigentes de outros órgãos.** O PNCP do pacote é uma amostra, e o aceite do gerenciador e do fornecedor não é observável. Tratamento: E3 é avaliada só como contingência.
- **Vigência e saldo do instrumento do PE 12/2024 e do PE 01/2024.** Não informados. São relevantes para a transição.
- **Base exata do desconto do PE 12/2024** (PF ou PMVG, alíquota, regra de escolha do registro). Não informada. Tratamento: faixa no E2 (HIP H09).
- **Fornecimento centralizado de insulinas pelo MS/SES-PB.** Fora do pacote (CP, a verificar).
- **Reajuste anual CMED de 2025.** O percentual não era conhecido em 29/01/2025 (CP: Lei 10.742/2003, art. 4º).

### 3.5 Representatividade da referência de mercado (CALC)
- A mediana restrita a compradores municipais é 0,97 da mediana geral (P25 0,93; P75 1,00). Trocar uma pela outra muda o custo do E1 em menos de 0,4% (`trabalho/10_referencias.txt`, `trabalho/sensibilidades.csv`).
- Os preços históricos não foram corrigidos monetariamente (HIP H06). Uma correção de 5% somaria cerca de R$ 90,6 mil ao custo central do E1 (`trabalho/40_numeros_texto.txt`).
- A ordem de grandeza da referência saneada é coerente com o histórico do órgão. O custo central do E1 para as quantidades do ETP (R$ 1,81 mi) é 0,93 vez o gasto de 2024 (CALC). Isso **não valida** as quantidades: em 2024 parte das compras foi feita pelo modelo de desconto, a preços que estimo mais altos, e não se conhece o volume físico comprado (INF).
