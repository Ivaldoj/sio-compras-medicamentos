# 19 — Pré-Etapa 5: falhas apontadas pelo agente, normas pendentes e preparação da avaliação

> **Atualização (23/11/2026, doc 20):** os documentos oficiais da contratação (ETP, TR, contrato, aditivo e ata) comprovam que a unidade das canetas é **a caneta individual**, o que resolve a limitação 2 quanto à unidade. Continua sem prova qual produto foi contratado (marca declarada EQUIPLEX, sem insulina na CMED) e qual quantidade foi entregue. O indicador C4 foi corrigido em separado: **17 itens** acima do teto, excesso de **R$ 1.280.392**. Os demais números deste documento não mudam.

23/11/2026. Os arquivos congelados da Etapa 4 (`etapa4/`) e o pacote v1 (`data/decision_input/`) **não foram alterados**: os hashes conferem com o `LOG_ETAPA_4.md` e com o `MANIFESTO.csv`. As correções estão em um pacote separado, `data/decision_input_v2/`. Esta etapa prepara a avaliação e **não atribui nota** ao agente; o julgamento de mérito fica para a Etapa 5.

## Resumo

- **Falhas do pacote:**
  - duas confirmadas: as insulinas análogas (itens 194/195) e a pré-mistura vinculada ao item 197;
  - uma não confirmada: o item 268 não tem erro de conversão;
  - uma é um fato da fonte, não falha do pacote: a lista CMED não publica a alíquota de 20% para produtos do Convênio 87/02.
  - Impacto financeiro: alguns milhares de reais. Nenhuma delas altera a decisão.
- **Normas que o agente marcou "a verificar":** as três estão corretas na fonte oficial. A mais relevante é a aquisição centralizada de insulina humana NPH e Regular pelo Ministério da Saúde, em frascos e canetas. Ela coloca em dúvida a necessidade de compra municipal dos itens 196–199, que somam 27,6% da estimativa.
- **Cálculos do agente:**
  - reproduzíveis: 13 saídas numéricas idênticas byte a byte;
  - as 20 verificações conferem.
- **Comparação com os dados reservados:**
  - fora as insulinas, o preço projetado pelo agente ficou próximo do homologado no PE 04/2025: o homologado foi 1,04× o projetado em valor, e a mediana por item, 0,97×;
  - a diferença total (homologado R$ 3,11 mi × projetado R$ 1,81 mi) vem quase toda das canetas de insulina. Elas foram homologadas exatamente na estimativa do órgão, 9,6× o teto CMED.
- **Sensibilidade:** em nenhum dos 9 cenários a recomendação muda. A margem sobre o modelo de desconto na CMED cai de R$ 2,22 mi para R$ 0,99 mi quando o E1 é precificado pelos homologados reais.
- **Economia em três níveis, que não se comparam diretamente:**
  - projetada pelo agente: R$ 2,22 mi contra o E2 e R$ 1,74 mi contra R1;
  - contratada na decisão real: R$ 1,85 mi contra a estimativa;
  - realizada: não observável para a estratégia do agente. Para a decisão real, só há uma estimativa sob hipótese.

## 1. Falhas do pacote apontadas pelo agente

| | Apontamento | Veredito | Causa | Impacto financeiro | Altera a decisão? |
|---|---|---|---|---|---|
| F1 | Itens 194/195: o grupo "compatível" mistura outros tipos de insulina | **Confirmada, e mais ampla que o apontado** | A regra de CATMAT não comparava o atributo TIPO da insulina: o item 194 (análoga prolongada) recebia os CATMATs da análoga rápida e da NPH, e o 195, os da NPH e da prolongada. Além disso, um grupo BPS em **tubete** estava como compatível com item que exige sistema de aplicação, embora a regra das canetas do Compras.gov.br já o tratasse como incompatível. | Pela mediana praticada compatível, a referência dos dois itens passa de R$ 16,0 mil para R$ 28,3 mil. Eles pesam R$ 39,0 mil na estimativa (0,8%). O agente já tinha contornado a falha usando só o CATMAT do tipo certo; no v2, o E1 dele sobe R$ 989. | Não |
| F2 | Item 197: vínculo CMED de pré-mistura (HUMULIN 70N/30R) | **Confirmada** | O vínculo CMED de insulina não distinguia pré-mistura 70/30 de NPH. É o único caso entre os itens de insulina. | Teto máximo de R$ 63,46 → R$ 50,77. A estimativa (R$ 55,49) passa a ficar acima do teto: são 41 itens, não 40. Excesso de R$ 2.360. A referência do agente (R$ 26,88) não muda. | Não |
| F3 | Item 268: teto com erro de conversão | **Não confirmada** | Os fatores estão corretos (10, 20, 50 e 100 ampolas), e o teto unitário é igual entre embalagens do mesmo produto (NAUSEDRON: R$ 53,98 a R$ 53,99). O teto CMED é que fica **25× o preço praticado** (R$ 2,17): está "descolado" do mercado, não errado. | Nenhum no pacote. O agente tirou o item do modelo de desconto (E2), com efeito de poucos milhares de reais. | Não |
| F4 | Convênio ICMS 87/02: falta a coluna de 20% | **O fato é verdadeiro, mas não é falha do pacote** | A própria lista CMED de compras públicas (06/01/2025) traz apenas "Sem Imposto" e "0%" para os **2.810** registros do convênio. Todas as colunas de 12% a 22% estão vazias na fonte, e o pacote a reproduz. | Só como sensibilidade: 54 itens têm vínculo do convênio a 0% (R$ 1,94 mi da estimativa). Com teto 1,25× (razão mediana 20%/0% dos demais produtos), o E1 sobe R$ 35 mil e o E2, R$ 158 mil. | Não |

Detalhes em `etapa5/verificacao/falhas_pacote.csv` e `impacto_itens.csv`; script `scripts/31_verifica_falhas_pacote_v2.py`.

## 2. Referências normativas pendentes

| Referência | O que o agente usou | Verificação na fonte oficial | Resultado |
|---|---|---|---|
| Lei 14.133/2021, art. 86, §3º, na redação da Lei 14.770/2023 | Adesão a atas municipais "a verificar" | [Planalto, Lei 14.133](https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14133.htm) e [Lei 14.770/2023](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/L14770.htm). A Lei 14.770 é de 22/12/2023 e vigora desde a publicação. O §3º, II, permite a órgão municipal aderir a ata de gerenciador municipal, "desde que o sistema de registro de preços tenha sido formalizado mediante licitação". Limites: 50% por aderente (§4º) e o dobro no total (§5º). Não houve alteração até 29/01/2025. | **Correta.** A adesão (E3) era juridicamente viável. O agente a manteve só como contingência, por razões operacionais, e isso não muda. |
| Decreto 12.343/2024 | Dispensa de "~R$ 62,7 mil" em 2025 | [Planalto](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2024/decreto/D12343.htm): decreto de 30/12/2024, DOU de 31/12/2024, em vigor de 01/01/2025 até a revogação pelo Decreto 12.807/2025, que vale a partir de 01/01/2026. Art. 75, II: R$ 62.725,59. | **Correta.** O descarte da dispensa para o conjunto se sustenta. |
| Fornecimento centralizado de insulinas pelo MS | "Confirmar a cota MS/SES" antes de licitar (a verificar) | [Página do MS](https://www.gov.br/saude/pt-br/composicao/sectics/daf/cbaf/insulinas-humanas). Notas Técnicas nº 169/2022-CGAFB (assinada em 29/04/2022) e nº 164/2023-CGAFB (31/05/2023), arquivadas em `data/raw/complementares/normas_etapa5/`. Base: PRC nº 2/2017, Anexo XXVIII, art. 35. | **Correta.** Ver o detalhamento abaixo. |

**O que as notas do MS estabelecem** (insulinas humanas NPH e Regular 100 UI/mL):
- o MS as compra de forma centralizada, em frascos e em canetas/tubetes, junto com as agulhas;
- distribui às Secretarias Estaduais, que repassam aos municípios;
- 70% da demanda do SUS é atendida em canetas, com público sugerido de até 19 anos e a partir de 45 anos;
- nenhum dos documentos proíbe a compra municipal complementar, nem a autoriza expressamente;
- as análogas (itens 194/195) não aparecem nessas páginas.

Os textos do Planalto foram lidos pela web, mas não puderam ser arquivados localmente: a conexão foi recusada (curl 56), como já tinha acontecido com a SEFAZ-PB.

## 3. Pacote corrigido (v2)

`data/decision_input_v2/` = v1 + `ERRATA.csv`, com manifesto próprio e nota no início do `LEIA-ME.md`:

| Errata | Correção |
|---|---|
| E-01 | Remove 4 pares item × CATMAT com tipo de insulina diferente do item. |
| E-02 | Tubete deixa de ser compatível com item que exige sistema de aplicação. |
| E-03 | A pré-mistura vinculada ao item 197 passa a "incompativel". |
| E-04 | Recalcula as colunas derivadas dos itens 194, 195 e 197. |
| E-05 | Registra a nota sobre o Convênio 87/02. |

Nenhuma informação posterior ao corte foi acrescentada. Os scripts do agente rodam sem erro sobre o v2:

| | v1 (o que o agente usou) | v2 |
|---|---|---|
| E1 (recomendada) | R$ 1.812.130 | R$ 1.813.119 |
| E2 (desconto na CMED) | R$ 4.035.750 | R$ 4.035.753 |
| E3 (adesão + E1) | R$ 1.711.564 | R$ 1.712.553 |
| R1 (estimativa limitada ao teto) | R$ 3.556.151 | R$ 3.553.791 |

## 4. Preparação da avaliação

### 4.1 Protocolo
- **Pré-registro:** `etapa5/PROTOCOLO_AVALIACAO.md` (sha256 `b61f65dc…`) foi escrito **antes** do cálculo e não mudou depois.
- **Avaliador não cego:** a sessão conhece desde a Etapa 2 o resultado agregado do PE 04/2025.
- **Ajustes durante a execução:** três foram de implementação do script, não das regras:
  - B1: tolerância de arredondamento;
  - B5: o arredondamento do NumPy difere do arredondamento do Python;
  - B8: o critério ME/EPP é reportado pelas duas bases de valor.

### 4.2 Reprodutibilidade (`scripts/32_reproduz_agente.py`; `etapa5/avaliacao/reproducao.csv`)
- Os 6 scripts da ordem declarada (10 → 20 → 21 → 30 → 40 → 50) rodam sem erro em cópia. As **13 saídas numéricas são idênticas byte a byte** às congeladas.
- Os 8 textos de `saida/*.md` foram escritos pelo agente, não gerados por script; seus números são verificados em 4.3.
- Lacunas menores:
  - `12_insulina_catmat_precos.txt` não tem script: veio de comando avulso;
  - 11 saídas exploratórias ficam fora da ordem declarada.

### 4.3 Verificação dos cálculos (`verificacao_calculos.csv`): 20 de 20 conferem
- Conferem:
  - o E1 e suas faixas;
  - as oito economias e faixas declaradas;
  - nenhuma referência acima do teto;
  - nenhum preço "a conferir" usado como referência central;
  - todo teto usado vem de vínculo aceito;
  - uma única categoria de valor por referência;
  - as contagens (41 itens acima do teto, 63 sem referência, 25 a conferir) e o excesso de R$ 1.396.286, 85,6% dele nas canetas.
- Duas ressalvas:
  - **Arredondamento:** os preços unitários do CSV têm 4 casas, o que gera R$ 4 de diferença.
  - **ME/EPP:** o agente marcou 332 itens como exclusivos com base no **seu** valor de referência. Pela estimativa original do órgão:
    - quatro marcados passariam de R$ 80 mil (itens 28, 100, 199 e 294);
    - um não marcado ficaria abaixo (item 32).

    O critério dele só vale se a referência saneada virar o valor estimado do edital, que é exatamente o que ele recomenda.

### 4.4 Comparação com os dados reservados (`comparacao_itens.csv`, `comparacao_resumo.csv`, `execucao.csv`)

**A decisão real** foi pregão por item, sem ata: 7 contratos de 12 meses, que somam R$ 3.105.249,60, com os 334 itens homologados nas quantidades do ETP. Em **43 itens** (R$ 1,80 mi, incluindo as 4 canetas) o preço homologado foi **exatamente a estimativa** do órgão.

**Preço projetado pelo agente × preço homologado:**

| Grupo | Itens | E1 do agente | Homologado | Razão (valor) | Mediana por item | Na faixa do agente | Acima da faixa |
|---|---|---|---|---|---|---|---|
| Todos | 334 | R$ 1,81 mi | R$ 3,11 mi | 1,71 | 0,97 | 55% | 18% |
| Sem as insulinas | 328 | R$ 1,64 mi | R$ 1,70 mi | **1,04** | 0,96 | 56% | 16% |
| Insulinas 194–199 | 6 | R$ 0,17 mi | R$ 1,40 mi | 8,13 | 4,63 | 0% | 100% |
| Canetas 196 e 199 | 2 | R$ 0,14 mi | R$ 1,33 mi | 9,54 | 9,45 | 0% | 100% |

Outros cortes:
- **Itens sem referência externa (63):** o homologado foi 1,07× o projetado. A regra provisória do agente (estimativa ÷ 2,04) não foi pior que a média.
- **Mercado nacional de 2025** (247 itens com registros compatíveis; exclui o próprio município):
  - mediana nacional / referência do agente = **0,90**: as referências do agente ficaram cerca de 10% acima do mercado de 2025;
  - homologado / mediana nacional = 1,02.
- **Teto CMED:** 15 itens foram homologados acima do teto de jan/2025, com excesso de R$ 1,26 mi, quase todo nas canetas (R$ 193,02 e R$ 147,36 contra tetos de R$ 20,15 e R$ 15,81).
- **Execução** (o detalhe está em `execucao.csv`):
  - do PE 04/2025, foram empenhados R$ 586.816,65 até 08/2026, ou **18,9%** do contratado;
  - o contrato que inclui as canetas (R$ 2,10 mi, 128 itens) foi executado em **7,8%**;
  - em 2025, o principal canal de compra foi o **contrato de desconto sobre a CMED (PE 12/2024)**: R$ 865.727 de R$ 1,41 mi;
  - em 2026 (até agosto), o mesmo contrato somou R$ 625.305.
- **Escopo:** o PE 25/2025 comprou 89 itens novos (1 em comum com o PE 04/2025), com R$ 2,78 mi homologados. Nenhuma das estratégias, a do agente ou a real, cobria essa demanda.

### 4.5 Viabilidade (`viabilidade.csv`)

| Dimensão | Evidência |
|---|---|
| Jurídica | O registro de preços (E1) e a adesão (E3) eram permitidos, e as normas que o agente citou foram confirmadas. A exclusividade ME/EPP depende do valor estimado adotado no edital (4.3). |
| Regulatória | Todas as referências do agente respeitam o teto. A decisão real homologou 15 itens acima do teto. |
| Operacional | As entregas parceladas do E1 atendem à falta de armazenamento; os contratos reais também previam "fornecimento parcelado". Não há dado de ruptura nem de entrega. |
| Orçamentária | A decisão real comprometeu R$ 3,1 mi e executou 18,9%. O E1, por registro de preços, só compromete o que for pedido. É coerente com o argumento do agente contra o contrato de quantidade fixa (E4). |
| Mercado | Em 60 itens (18%) o mercado aceitou, para este comprador, preço acima do limite alto do agente. Sem as insulinas, são 54 itens e R$ 0,46 mi homologados. É o principal risco de deserto do E1, e não pode ser medido sem um certame com a referência saneada. |
| Transição | O contrato de desconto (PE 12/2024) continuou vigente e foi o canal principal. Isso resolve, ex post, uma incerteza que o agente havia declarado. |

### 4.6 Sensibilidade da recomendação (`sensibilidade.csv`)
O cálculo usa as fórmulas do próprio agente. A recomendação **muda** se o E1 deixar de ser o menor custo entre E1, E2 e E4.

| Cenário | E1 | E2 | E2 − E1 | Muda? |
|---|---|---|---|---|
| S0: base, modelo do agente | 1.812.130 | 4.035.750 | 2.223.619 | não |
| S1: pacote v2 | 1.813.119 | 4.035.753 | 2.222.634 | não |
| S2: teto a 20% no Convênio 87/02 | 1.847.114 | 4.193.413 | 2.346.299 | não |
| S3: sem as insulinas humanas 196–199 (cota federal) | 1.656.302 | 3.902.057 | 2.245.756 | não |
| S4: E1 aos preços homologados reais | 3.105.250 | 4.097.557 | **992.308** | não |
| S5: E1 à mediana nacional de 2025 | 1.719.818 | 3.999.685 | 2.279.867 | não |
| S6: itens sem referência pela estimativa limitada ao teto | 2.038.899 | 4.262.518 | 2.223.619 | não |
| S7: demanda = 18,9% observado (E4 compromete R$ 1,81 mi) | 342.449 | 762.659 | 420.210 | não |
| S8: S2 + S3 + S4 | 1.741.498 | 4.093.780 | 2.352.282 | não |

O E2 é sempre o modelo do agente. **Nenhum preço por item observado** do contrato de desconto existe para testá-lo.

### 4.7 Economia: projetada × contratada × realizada (`economia_niveis.csv`)

| Nível | Objeto | Referência | Valor | O que é |
|---|---|---|---|---|
| Projetada (ex ante) | Estratégia do agente | E2 (modelo de desconto) | R$ 2.223.619 | contrafactual, nunca observável |
| Projetada (ex ante) | Estratégia do agente | R1 (estimativa limitada ao teto) | R$ 1.744.021 | contrafactual |
| Contratada (ex post) | Decisão real | R0 (estimativa) | R$ 1.847.188 (37,3%) | observada no certame; **não é realizada** |
| Contratada (ex post) | Decisão real | R1 | R$ 450.902 | a maior parte da diferença contra R0 vem de estimativas acima do teto legal |
| Realizada (ex post) | Decisão real | R0, sobre os R$ 585.893 pagos | R$ 552.404 | **estimativa** sob hipótese de mix proporcional por contrato |
| Realizada (ex post) | Decisão real | R1, sobre o pago | R$ 420.183 | estimativa, mesma hipótese |
| Realizada | Estratégia do agente | — | não observável | a estratégia não foi executada |
| **Não é economia** | Projeção × certame | homologado − E1 | R$ 1.293.124 | erro de projeção de preço: 95% nas seis insulinas, 92% só nas duas canetas |

## 5. Limitações que impedem conclusões confiáveis

1. **Contrafactual do E1.** A estratégia recomendada nunca foi executada, e a única régua de preço observada é um certame cujo preço máximo era a estimativa inflada do órgão.
   - Em 18% dos itens o mercado aceitou preço acima da faixa do agente.
   - Não dá para afirmar que o E1 alcançaria R$ 1,81 mi, nem quantos itens ficariam desertos.
2. **Unidade das canetas de insulina.** O homologado (R$ 193,02 e R$ 147,36 por "unidade") é igual à estimativa e 9,6× o teto CMED de uma caneta.
   - Sem o contrato ou as notas fiscais, não se sabe se a "unidade" comprada é uma caneta ou uma caixa.
   - Esses dois itens explicam 92% da diferença entre projeção e homologado (R$ 1,20 mi de R$ 1,29 mi).
   - Enquanto isso não for esclarecido, **nenhuma conclusão de preço sobre as canetas é confiável**. O mesmo vale para a possível violação do teto na decisão real.
3. **E2 só modelado.** O contrato de desconto foi o canal mais usado em 2025, mas não há preço por item. A vantagem do E1 sobre o E2 depende inteiramente do modelo de desconto do agente.
4. **Economia realizada não mensurável.** A execução é conhecida por contrato, não por item. Os números de "realizada" da decisão real são estimativas sob hipótese, e a estratégia do agente não tem realização.
5. **Demanda.** A execução de 18,9% sugere superestimação do ETP ou uso de outros canais, como o contrato de desconto. Isso afeta o custo absoluto de todas as estratégias, não a ordem entre elas.
6. **Cota federal de insulinas** para Santa Luzia desconhecida: o S3 é só um limite superior.
7. **Avaliador não cego.** A mesma sessão preparou os dados, verificou as falhas e montou a avaliação.
8. **Conversões sem validação humana** (desde a Etapa 3). A F1 mostrou que a regra de CATMAT ignorava o tipo da insulina; falhas análogas em outros atributos não podem ser descartadas.
9. **Normas do Planalto** lidas pela web, sem cópia local.

## 6. O que fica para a Etapa 5
- Julgar o mérito: alternativas formuladas, critério de eficiência, qualidade das justificativas, tratamento das incertezas, insulinas e itens críticos.
- Decidir como ponderar a limitação 2 (unidade das canetas). Se possível, obter o contrato e as notas fiscais do item 196.
- Decidir se a avaliação será feita por avaliador cego (outro agente ou pessoa) com base neste material.
