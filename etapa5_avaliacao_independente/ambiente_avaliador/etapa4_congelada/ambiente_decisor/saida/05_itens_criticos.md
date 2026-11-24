# 05 — Itens críticos: insulinas, preços "a conferir" e estimativas acima do teto

Fontes:
- `trabalho/03_insulinas_detalhe.txt`, `05_insulinas_catmat.txt`, `12_insulina_catmat_precos.txt` (consultas OBS);
- `trabalho/10_referencias.py` → `ref_itens.csv`;
- `trabalho/30_itens_criticos.txt`;
- `trabalho/40_numeros_texto.txt` (CALC).

O detalhe por item está em `plano_por_item.csv`.

## 1. Insulinas

O peso no valor é calculado (CALC) sobre o valor do órgão (R0 = R$ 4.952.438) e sobre a referência do E1 (R$ 1.812.130).

| Item | Apresentação exigida (OBS) | Qtd. | Estimativa do órgão | Peso em R0 | Teto CMED aplicável, por unidade (OBS: `v_cmed_teto_unitario`, alíquota da PB) | Referências de preço disponíveis e limites | Referência adotada no E1 (faixa) | Peso no E1 |
|---|---|---:|---:|---:|---|---|---|---:|
| **196** | Insulina humana NPH 100 UI/mL, suspensão injetável, **3 mL com sistema de aplicação** (caneta) | 6.000 | R$ 193,02 → R$ 1.158.120 | **23,4%** | **PF 0% R$ 20,14** (NOVOLIN N FlexPen, 1 caneta) / R$ 20,152 (caixa com 5). Produto **sem CAP**: o teto é o PF; o PMVG de R$ 15,80 vale só em compra judicial. Alíquota 0% pelo Conv. ICMS 87/02, com condições não verificadas | Não há preço praticado compatível: o CATMAT não foi identificado e o código é genérico. "A conferir": 15 registros (2021–2024), mediana de R$ 18,90; os de 2024 em "SERINGA 3 mL" ficam entre R$ 21,00 e R$ 33,51, **acima do teto**. PNCP: estimativa de outro município de R$ 46,19 (acima do teto, inutilizável). O CATMAT 442012 ("NPH c/ sistema de aplicação") tem compras em 2023–2024 entre R$ 9,89 e R$ 44,00, mas o pacote não o vincula ao item 196 (só informativo) | **Teto: R$ 20,152** (R$ 17,05 a R$ 20,15) → R$ 120.912 | 6,7% |
| **199** | Insulina humana Regular 100 UI/mL, solução injetável, **3 mL com sistema de aplicação** (caneta) | 1.200 | R$ 147,36 → R$ 176.832 | 3,6% | **PMVG 0% R$ 15,80** (NOVOLIN R FlexPen). Produto **com CAP**: PMVG obrigatório, que já inclui o CAP | Não há praticado compatível. "A conferir": 5 registros recentes, mediana de R$ 35,22, acima do teto. PNCP: estimativa de R$ 39,33, acima do teto | **Teto: R$ 15,814** (R$ 13,38 a R$ 15,81) → R$ 18.977 | 1,0% |
| 197 | NPH 100 UI/mL, frasco 10 mL | 500 | R$ 55,49 → R$ 27.745 | 0,6% | De R$ 29,82 (Bahiafarma, PMVG-CAP) a R$ 50,77 (PF 0%). O máximo do pacote, R$ 63,46, vem do HUMULIN 70N/30R, uma **pré-mistura e não NPH**, vínculo que parece indevido | 211 praticados compatíveis (24 meses), mediana de R$ 26,88 | R$ 26,88 (R$ 20,57 a R$ 35,00) → R$ 13.440 | 0,7% |
| 198 | Regular 100 UI/mL, frasco 10 mL | 100 | R$ 55,90 → R$ 5.590 | 0,1% | PMVG 20% (CAP), de R$ 29,25 a R$ 49,80 | 213 praticados, mediana de R$ 25,00; PNCP homologado de R$ 22,58 | R$ 25,00 (R$ 20,50 a R$ 34,00) → R$ 2.500 | 0,1% |
| 194 | Análoga de ação prolongada, 100 UI/mL, caneta 3 mL | 100 | R$ 195,68 → R$ 19.568 | 0,4% | **Sem teto**: não há candidato CMED no pacote | O grupo "compatível" do pacote mistura CATMATs de outras insulinas. Restrito ao CATMAT 468664, ficam 2 registros (RJ, 2023), de R$ 141,58: referência fraca | R$ 141,58 (R$ 119,80 a R$ 176,98) → R$ 14.158 | 0,8% |
| 195 | Análoga de ação rápida, 100 UI/mL, caneta 3 mL | 100 | R$ 194,76 → R$ 19.476 | 0,4% | **Sem teto** | Restrito ao CATMAT 440255: 6 registros, mediana de R$ 26,52 | R$ 26,52 (R$ 21,33 a R$ 32,01) → R$ 2.652 | 0,1% |
| **Total** | | | **R$ 1.407.331** | **28,4%** | | | **R$ 172.639** (R$ 144.813 a R$ 181.685) | **9,5%** |

**Leitura e consequências (INF).**
- **Itens 196 e 199.** A estimativa do órgão é 9,6× e 9,3× o teto (CALC). Ela está próxima da estimativa das análogas (R$ 195), o que sugere confusão de apresentação ou de referência. Ela **não pode** ser usada.
  - Só esses dois itens respondem por **85,6%** do excesso das estimativas sobre o teto (R$ 1,195 mi de R$ 1,396 mi, CALC).
  - Pela regra de teto, o valor admissível cai de R$ 1,335 mi para no máximo R$ 139,9 mil.
- **Risco principal: deserto.** As compras de canetas observadas em 2024 (registros "a conferir") ficaram em geral **acima** de R$ 20,14 (NPH) e de R$ 15,80 (Regular). É possível que nenhum fornecedor aceite vender pelo teto. Mesmo assim, aceitar preço acima do teto é vedado.
- **Contingências, na ordem:**
  1. Confirmar a cota MS/SES. CP, a verificar: no Componente Básico, as insulinas humanas NPH e Regular são de aquisição centralizada pelo Ministério da Saúde (Portaria de Consolidação GM/MS nº 6/2017), e a compra municipal seria complementar.
  2. Repetir o item com pesquisa direta.
  3. Aderir a ata em que a caneta tenha sido registrada até o teto.
  4. Como **decisão clínica**, não de compras, atender parte dos pacientes com frasco e seringa. O custo por UI cai: a sensibilidade "canetas → frasco equivalente" reduz o E1 em R$ 82,5 mil, sem contar seringas e agulhas (CALC).
- **Se o Convênio ICMS 87/02 não se aplicar** (condições do §1º não verificadas), o teto passaria à coluna de 20%, **que o pacote não publica** para esses registros. É uma lacuna: o teto poderia ser mais alto, e o risco de deserto, menor.
- **Item 197.** Excluído o vínculo HUMULIN 70N/30R, o teto máximo é de R$ 50,77, e a estimativa do órgão (R$ 55,49) **também fica acima do teto**. O item não estava entre os 40 do pacote. A referência E1 (R$ 26,88) não muda.
- **Itens 194 e 195 (análogas).** Têm valor baixo, mas não têm teto vinculado e têm referência fraca. CP, a verificar: no SUS, as análogas são dispensadas pelo Componente Especializado (CEAF/SES), conforme protocolo. A compra municipal tende a atender demandas fora do protocolo ou judiciais. Exigem pesquisa direta e confirmação do fluxo.
- **Comparação com o modelo de desconto (E2):** o custo das insulinas pelo desconto seria de R$ 99.106 para o item 196 (PF − 18,01%) e de R$ 11.843 para o item 199 (PF − 51,01%, cadastrado como "Similar"). No papel, é menor que o E1, mas pressupõe que o fornecedor entregue canetas abaixo do teto quando o mercado observado está acima dele. É a mesma razão do descarte do híbrido X7.

## 2. Preços "a conferir"

**Tratamento adotado (D06).**
- Registros "a conferir" (BPS e Compras.gov.br) **nunca** são usados como preço central nem como teto.
- Nos 25 itens com `status_preco_praticado = a conferir`, a referência central vem, nesta ordem, de:
  1. PNCP limitado ao teto: itens 196, 199 e 77;
  2. estimativa do órgão deflacionada por 2,044 (H07): os outros 22 itens.
- A mediana "a conferir" (limitada ao teto) só aparece como cenário de sensibilidade (coluna `observacao` do plano).

**Efeito na conclusão (CALC, `trabalho/sensibilidades.csv`).**

| Cenário | Valor dos 25 itens na referência | E1 total | E2 − E1 |
|---|---:|---:|---:|
| "A conferir" **incompatível** (base) | R$ 206.142 | R$ 1.812.130 | R$ 2.223.619 |
| "A conferir" **compatível** | R$ 211.900 | R$ 1.817.889 | R$ 2.231.131 |

- A conclusão **não muda** em nenhum dos dois casos.
- O efeito é pequeno porque, nas canetas 196 e 199, a mediana "a conferir" é limitada pelo mesmo teto. Nos demais itens, ela fica próxima da estimativa deflacionada: a razão mediana entre estimativa do órgão e preço "a conferir" é 1,54 (CALC).
- O que muda é o **risco**. Se os registros "a conferir" das canetas forem de fato canetas, o mercado de 2024 estava acima do teto, e o risco de deserto nos itens 196 e 199 é alto.

## 3. Estimativas acima do teto regulatório

**Identificação (CALC, `trabalho/30_itens_criticos.txt`).**
- 40 itens marcados pelo pacote (`alerta_estimativa_acima_teto_cmed`) e mais o **item 210**, que entra quando se usa o teto "confirmado" (sem vínculos COM ALERTA). Total: **41 itens**.
- Esses itens somam **R$ 1.932.504** (39,0% de R0).
- Limitados ao teto máximo, valem R$ 536.217. O excesso é de **R$ 1.396.287**, dos quais 85,6% estão nas canetas 196 e 199.
- A razão entre estimativa e teto tem mediana de 1,40 e máximo de 9,58.
- Adicionalmente, o item 197 ficaria acima do teto se o vínculo HUMULIN 70N/30R fosse excluído.
- A lista completa, com teto mínimo e máximo, tipo (PF ou PMVG), razão e referência adotada, está em `trabalho/30_itens_criticos.txt` e nas colunas `flag_acima_teto_*` do plano.

**Efeitos.**
1. **No valor de referência.** A estimativa do órgão desses itens é **inadmissível** como valor de referência ou critério de aceitabilidade: o preço máximo de venda ao governo é o teto do produto ofertado (CP: Lei 10.742/2003 e normas da CMED; restrição do pacote). No E1, a referência é a mediana praticada, que já fica abaixo do teto em 39 dos 41 itens; nos itens 196 e 199, é o próprio teto. A referência E1 desses 41 itens soma R$ 319.289.
2. **Na economia calculada.** Medir economia contra R0 contaria R$ 1,396 mi de "economia" que é só a retirada de um valor ilegal. Por isso R0 **não** é usada como referência de economia, e o excesso R0 − R1 aparece separado, como **correção de conformidade** (`06_economia.md`).
3. **Na conformidade da contratação.**
   - O edital deve fixar como critério de aceitabilidade "≤ teto CMED do registro ofertado", com PF ou PMVG (se CAP) na alíquota da PB.
   - O licitante deve declarar o registro Anvisa, e a conferência deve ser feita na lista CMED vigente na data da sessão.
   - Homologar acima do teto exporia a contratação a glosa e a responsabilização.
   - Os 41 itens e o item 197 devem ser reprecificados no ETP e no TR antes da publicação.

## 4. Bloqueios do pacote

- Vínculos `incompativel`, `indeterminada` e `provavel_conferencia`, e grupos BPS sem compatibilidade comprovada, **não entram** como preço nem como teto. As visões `v_cmed_teto_unitario` e `v_bps_comparavel` já os excluem, e não usei `item_cmed` diretamente.
- Excluí também do teto os vínculos COM ALERTA e o vínculo do item 151 apontado como "ERRO" pela inspeção.
- 108 itens (R$ 1,10 mi em R0) ficam **sem teto utilizável**. Neles a aceitabilidade depende só da referência de mercado ou da pesquisa direta, e o teto deverá ser verificado por produto ofertado na sessão.
