# Etapa 5 — Avaliação independente da decisão do agente (Etapa 4)

Santa Luzia/PB · necessidade de 334 medicamentos por 12 meses · data de decisão simulada: 29/01/2025 · avaliação feita em 24/11/2026.

Todo número deste relatório sai de um script em `scripts/` e está em um arquivo de `resultados/` (indicado entre parênteses). Como regerar: `LEIA-ME.md`. Cronologia, desvios e hashes: `LOG_ETAPA_5.md`, na raiz.

---

## 1. Veredito em uma página

**A decisão do agente é adequada e, nos três pontos em que difere da decisão real, é melhor que ela. A economia que o agente anunciou, porém, não é verificável e está superestimada em valor absoluto.**

| Dimensão avaliada | Resultado | Evidência principal |
|---|---|---|
| Precisão dos cálculos | **Alta** | 59 de 59 verificações conferem com recálculo próprio; os 9 CSVs do agente são regenerados idênticos byte a byte |
| Qualidade da referência de preço | **Alta** | Fora as canetas de insulina, o custo previsto ficou 5,9% abaixo do homologado real e 11% acima da mediana nacional posterior; a estimativa do órgão ficou 2,3× acima |
| Qualidade da decisão | **Boa, com ressalvas** | Os três desvios em relação à decisão real (registro de preços, referência saneada, teto nas insulinas) são sustentados pelos dados posteriores |
| Viabilidade | **Provável, não demonstrada** | A forma recomendada é a que o órgão usou e repetiu; a regra de aceitação do agente deixaria de 6% a 18% dos itens sem contratar na primeira rodada |
| Identificação de riscos | **Boa** | Previu o sobrepreço das canetas, o vale de abastecimento do início do ano e o risco de item deserto; errou a largura da faixa de demanda |
| Economia projetada | **Fraca como número, correta como direção** | R$ 2,22 mi de economia potencial supera o gasto anual real com medicamentos (R$ 1,41 mi em 2025); depende de um modelo do contrato de desconto que nenhum dado confirma item a item |

**Os três níveis de economia, que não se somam:**

| Nível | Decisão real (PE 04/2025) | Estratégia do agente |
|---|---|---|
| Potencial (antes de decidir) | — | R$ 2,22 mi frente ao modelo de desconto; R$ 1,74 mi frente à estimativa limitada ao teto |
| Contratada (homologação) | R$ 1,85 mi frente à estimativa do órgão; R$ 0,45 mi frente à estimativa limitada ao teto | Não observável: a estratégia não foi licitada |
| Realizada (pago) | R$ 585.893 pagos, 18,9% do contratado; economia por item não observável | Não observável: a estratégia não foi executada |

**O que o experimento demonstra.** A IA produziu, em 24 minutos e sem ajuda, uma análise de compra correta nos cálculos, calibrada na incerteza e capaz de encontrar um sobrepreço de R$ 1,2 milhão que o processo real contratou. Isso é diligência analítica barata e auditável. Não é prova de que a IA decide melhor que a organização: ela recomendou, não executou; trabalhou sobre um pacote de dados preparado ao longo de quatro etapas; e a linha de base com que é comparada era fraca. Detalhes na seção 10.

---

## 2. O que foi avaliado e por quem

- **Decisão avaliada:** os entregáveis congelados em `etapa4/ambiente_decisor/saida/` e os scripts em `trabalho/`. O agente recomendou a estratégia E1: pregão eletrônico para registro de preços, por item e menor preço, com valor de referência igual à mediana dos preços praticados limitada ao teto CMED, ata de 12 meses e entregas sob demanda.
- **Linha de base:** a decisão real, o PE 04/2025. Foi um pregão eletrônico por item e menor preço, com preço máximo igual à estimativa do órgão e sete contratos de quantidade total, sem ata de registro de preços.
- **Avaliador:** uma sessão nova do Claude (modelo Fable 5.2), que não preparou os dados nem participou das etapas anteriores.
- **Protocolo:** `etapa5/PROTOCOLO_AVALIACAO.md`, pré-registrado, com hash conferido.

**Limites da independência.**
- O avaliador é da mesma família de modelos do agente decisor (Claude Opus 5.5). A independência é de sessão e de contexto, não de linhagem. Vieses comuns aos dois modelos não seriam detectados.
- O avaliador leu `etapa5/LEIA-ME.md`, o protocolo e o `LOG_PRE_ETAPA_5.md`. O log traz resultados resumidos da preparação anterior, entre eles o veredito das quatro falhas do pacote e o teto das canetas. O avaliador **não leu** os documentos 19 e 20 nem as tabelas de `etapa5/avaliacao/`, `avaliacao_canetas/` e `verificacao/`.
  - Exceção: `avaliacao_canetas/correcao_C4.csv` foi aberto depois de fechado o cálculo próprio, para explicar uma diferença de contagem (seção 5.3).
- Todos os números foram recalculados com código próprio, a partir do pacote, dos dados reservados e dos documentos primários.

**Arquivos congelados.** Os 220 arquivos conferidos por sha256 estavam íntegros antes e depois do trabalho: `etapa4/`, os pacotes v1 e v2, o protocolo e as cópias do ambiente do avaliador (`resultados/integridade_antes.csv`, `integridade_depois.csv`).

---

## 3. Reprodutibilidade e precisão dos cálculos

### 3.1 Reprodução (protocolo, dimensão A)

Os seis scripts do agente foram reexecutados em cópia temporária, na ordem que ele declarou, depois de apagadas as saídas (`resultados/reproducao.csv`).

- **Pacote v1:** 6 de 6 scripts rodaram. Os 9 CSVs gerados são idênticos byte a byte aos congelados.
- **Saídas de texto:** 4 de 5 são iguais em conteúdo. A quinta, `20_estrategias.txt`, difere em quatro linhas da listagem de atas: quando duas atas têm o mesmo preço, a ordenação escolhe uma ou outra conforme a versão do pandas. Nenhum custo muda.
- **Pacote v2 (com a errata):** 6 de 6 scripts rodaram. O custo central do E1 passa de R$ 1.812.130 para R$ 1.813.119 e a ordenação das estratégias não muda (`resultados/reproducao_custos_v1_v2.csv`).

O ambiente desta reexecução é diferente do original (Python 3.10, pandas 2.3.3 e duckdb 1.5.6, contra Python 3.13.2, pandas 2.2.3 e duckdb 2.0.1). A igualdade byte a byte nos CSVs, apesar disso, é evidência forte de determinismo.

### 3.2 Verificação independente (dimensão B)

`scripts/e5_02_verificacao_calculos.py` não usa o código do agente. Ele recalcula os números a partir do pacote v1 e compara com o que o agente declarou. **Conferem 59 de 59** (`resultados/verificacao_calculos.csv`). Os principais:

| Verificado | Declarado pelo agente | Recalculado |
|---|---:|---:|
| Mediana praticada limitada ao teto, item a item (247 itens) | — | 247 de 247 conferem |
| Teto CMED "confirmado", item a item | — | 334 de 334 conferem |
| Itens com referência acima do teto | 0 | 0 |
| E1 central / baixo / alto | 1.812.130 / 1.499.016 / 2.508.722 | iguais |
| E2 central (modelo de desconto) | 4.035.750 | 4.035.750 |
| Estimativa do órgão limitada ao teto (R1) | 3.556.151 | 3.556.151 |
| Itens com estimativa acima do teto; excesso | 41; 1.396.287 | 41; 1.396.287 |
| Parte das canetas no excesso | 85,6% | 85,6% |
| Sobre-estimação mediana da estimativa do órgão | 2,044× | 2,044× |
| Preço "a conferir" usado como referência central | nenhum | nenhum (25 itens conferidos) |
| Descontos que empatariam E2 com E1 | 85,6% / 82,4% / 70,5% | iguais |

Os sete valores citados no resumo executivo batem com os arquivos de dados. **Não encontrei erro de cálculo.**

### 3.3 As quatro falhas do pacote apontadas pelo agente

Verificação própria em `resultados/falhas_pacote_verificacao_independente.csv`.

| Falha apontada | Resultado | Observação |
|---|---|---|
| F1: itens 194 e 195 recebem preços de outros tipos de insulina | **Confirmada** | Os quatro pares item × CATMAT que o agente citou são exatamente os quatro removidos pela errata E-01 |
| F2: item 197 (NPH) vinculado a uma pré-mistura 70N/30R | **Confirmada** | Corrigida pela errata E-03. Sem o vínculo, o teto cai de R$ 63,46 para R$ 50,77, como o agente calculou |
| F3: item 268 com teto "suspeito de erro de conversão" | **Não confirmada** | O fator de conversão está certo (caixa com 10 ampolas, R$ 53,99 por ampola). O preço-fábrica da CMED é que fica dezenas de vezes acima do praticado. Falso positivo, sem efeito na ordenação |
| F4: o pacote não traz o teto a 20% para produtos do Convênio ICMS 87/02 | **Confirmada como lacuna do pacote** | Ver abaixo |

**Divergência em relação à errata E-05.** A errata registra F4 como "fato da fonte": a lista da CMED não publicaria a coluna de 20% para os 2.810 registros do Convênio. A lista bruta de 06/01/2025 **publica** esses valores, marcados com asterisco (por exemplo, `25,18*` para a caneta NOVOLIN N FlexPen). A nota (viii) da própria lista explica a marcação. Os 2.810 registros têm a coluna preenchida; a leitura do pacote descartou os valores por não serem números puros. O efeito sobre a decisão é pequeno (seção 5.2), mas a classificação correta é falha de leitura do pacote, não ausência na fonte.

---

## 4. Comparação com o que aconteceu (dimensão C)

### 4.1 Preços: a referência do agente previu o mercado

Quantidades do ETP nos três casos (`resultados/expost_totais.csv`, `expost_resumo_grupos.csv`).

| | 334 itens | Canetas 196 e 199 | Demais 332 itens |
|---|---:|---:|---:|
| Estimativa do órgão | R$ 4.952.438 | R$ 1.334.952 | R$ 3.617.486 |
| E1 do agente, central | R$ 1.812.130 | R$ 139.889 | R$ 1.672.237 |
| E1 do agente, faixa | 1,50 a 2,51 mi | — | 1,38 a 2,37 mi |
| **Homologado real** | **R$ 3.105.250** | **R$ 1.334.952** | **R$ 1.770.298** |

- **Fora as canetas, o homologado ficou 5,9% acima do central do agente e dentro da faixa.** A razão mediana homologado ÷ referência é 0,97.
- **Por item**, dos 332: 185 foram homologados dentro da faixa do agente, 89 abaixo dela e 58 acima.
- **Toda a diferença entre o total real e a faixa do agente está nas duas canetas**, homologadas exatamente na estimativa do órgão.

**Mercado nacional nos 12 meses seguintes** (BPS e Compras.gov.br, compras de 30/01/2025 a 29/01/2026, mesma regra de compatibilidade do pacote; 245 itens com 5 registros ou mais):

| Preço comparado à mediana nacional posterior | Razão mediana | Itens a até 20% da mediana |
|---|---:|---:|
| Referência do agente | 1,11 | 68% |
| Estimativa do órgão | 2,32 | 3% |
| Homologado real | 1,02 | — |

A referência do agente errou para cima, não para baixo: em um item típico, 66% das compras nacionais posteriores saíram por preço igual ou menor que a referência, e 82% por preço igual ou menor que o limite alto. A mediana nacional caiu dentro da faixa do agente em 70% dos itens.

**O mesmo comprador, 15 meses depois (PE 09/2026).** Dos 334 itens, 309 voltaram a ser licitados e homologados. A razão mediana entre o preço de 2026 e a referência do agente é 0,85. A estimativa do órgão para 2026 continuou 1,88× acima da referência do agente: a causa do problema não foi corrigida.

**Itens sem referência externa (63).** O agente usou a estimativa do órgão dividida por 2,044 e avisou que era hipótese. O homologado ficou em R$ 232.829 contra R$ 217.250 previstos; 78% dos itens caíram na faixa. A heurística funcionou, mas continua sendo heurística.

### 4.2 Competição: onde ela faltou, o preço foi a estimativa

Extraí da Ata Final as propostas dos 334 itens (`resultados/expost_competicao.csv`).

| Proponentes no item | Itens | Homologado ÷ referência do agente (mediana) | Homologados exatamente na estimativa do órgão | Valor homologado |
|---|---:|---:|---:|---:|
| 1 | 27 | 2,04 | 27 de 27 | R$ 1.558.701 |
| 2 ou 3 | 61 | 1,29 | 14 | R$ 425.315 |
| 4 ou mais | 246 | 0,91 | 2 | R$ 1.121.234 |

- Os 27 itens com um único proponente saíram todos pelo preço máximo do edital e somam **50% do valor contratado**.
- Com quatro ou mais proponentes, o preço ficou 9% abaixo da referência do agente.
- A correlação entre o número de proponentes e a razão homologado ÷ referência é −0,50.

Este é o achado que mais sustenta o diagnóstico central do agente: com a estimativa inflada como teto de aceitação, "um pregão com pouca competição aceitaria lances até essa referência". Foi o que ocorreu.

### 4.3 Teto CMED

- **15 itens foram homologados acima do teto aplicável**, com excesso contratado de **R$ 1.261.859**, dos quais R$ 1.195.063 nas canetas 196 e 199. O resultado é o mesmo com o teto do agente e com o teto dos pacotes v1 e v2.
- Somadas as duas análogas 194 e 195 (seção 5.3), são **17 itens e R$ 1.280.392**.
- Os outros 13 itens somam R$ 66.795 de excesso. Aqui cabe cautela: os vínculos com a CMED não tiveram validação humana.

### 4.4 Execução e demanda

`resultados/expost_execucao_contratos.csv`, `expost_gasto_por_licitacao.csv`.

- **O PE 04/2025 gerou sete contratos no valor total de R$ 3.105.250. Em cerca de 20 meses, foram empenhados R$ 586.817 (18,9%) e pagos R$ 585.893.**
- O maior contrato (ALLFAMED, R$ 2.096.244, que inclui as canetas) teve 7,8% pagos. Os outros seis executaram entre 20% e 91%.
- Três contratos foram prorrogados até 12/03/2027, aos mesmos preços. O da ALLFAMED é um deles.
- **O órgão continuou comprando principalmente pelo contrato de desconto sobre a CMED (PE 12/2024):** R$ 865.727 em 2025 (61% do gasto com medicamentos) e R$ 625.305 em 2026 (46%, até novembro). O PE 04/2025 respondeu por 31% e 11%.
- Gasto total com medicamentos: R$ 1.410.230 em 2025; R$ 1.350.149 em 2026, até novembro.

Dois valores de empenho do PE 04/2025 aparecem nas fontes: R$ 586.817 pela soma dos contratos e R$ 576.015 pela classificação por licitação. A diferença, de R$ 10,8 mil, não muda nenhuma conclusão.

**Leituras.**
1. O agente tratou a demanda como incerta e escolheu um instrumento que não obriga a comprar. A execução confirma o diagnóstico, com sobra: as quantidades do ETP estavam muito acima do que foi comprado por essa via.
2. A faixa de demanda do agente, de 75% a 125% do ETP, foi estreita demais.
3. O contrafactual que o agente adotou como referência de economia, "o órgão continuaria usando o modelo de desconto", descreve o que de fato aconteceu.

### 4.5 Transição e escopo

- **Transição.** O agente alertou para meses sem cobertura até a nova contratação e mandou verificar a vigência do PE 12/2024. De janeiro a abril de 2025 foram empenhados R$ 62.757 no total; de maio a dezembro, a média mensal foi de R$ 168.434. O instrumento de 2024 era de fato a ponte disponível.
- **Escopo.** Em setembro de 2025 o órgão abriu o PE 25/2025 com 89 itens, dos quais só 1 constava dos 334. A necessidade documentada em janeiro era incompleta. Isso está fora do alcance do agente, que recebeu os 334 itens como dados (`resultados/expost_escopo.csv`).

---

## 5. Insulinas

Fontes: documentos do PNCP, lista bruta da CMED e notas técnicas do Ministério da Saúde, em `ambiente_avaliador/evidencias_primarias/`. Resultados nos arquivos `resultados/insulinas_*.csv`.

### 5.1 A unidade contratada é a caneta

| Documento | Página | Unidade | Quantidade e preço |
|---|---|---|---|
| Edital, ETP | 24 | "caneta" | 6.000 e 1.200 |
| Edital, Termo de Referência | 34 | "caneta" | 6.000 e 1.200 |
| Contrato 00054/2025 | 5 | "caneta" | 6.000 a R$ 193,02; 1.200 a R$ 147,36 |
| Termo Aditivo 01 | 4 | "caneta" | os mesmos, total de R$ 1.158.120,00 para o item 196 |
| Ata Final | 6, 30, 116, 273 | não consta nos trechos | proposta única de R$ 193,02 e de R$ 147,36 |
| PNCP (API) | — | "Unidade" | homologado com desconto de 0% |

Nenhum dos 16 trechos menciona caixa. Houve **uma única proposta** para cada caneta, da ALLFAMED, com o valor exato da estimativa e marca declarada "EQUIPLEX". A lista da CMED de janeiro de 2025 tem 68 apresentações desse laboratório e nenhuma insulina. As quatro apresentações de caneta de insulina humana registradas são todas da Novo Nordisk.

### 5.2 Contratado × teto, em todas as hipóteses

| Hipótese | Teto NPH | Contratado ÷ teto | Teto Regular | Contratado ÷ teto |
|---|---:|---:|---:|---:|
| Caneta, ICMS 0% (Convênio 87/02): a documentada e a que o agente usou | R$ 20,15 | 9,6× | R$ 15,81 | 9,3× |
| Caneta, coluna de 20% da lista bruta | R$ 25,19 | 7,7× | R$ 19,77 | 7,5× |
| Teste: o preço seria de caixa com 5, ICMS 0% (não documentado) | R$ 100,76 | 1,9× | R$ 79,07 | 1,9× |
| Teste: caixa com 5, ICMS 20% (não documentado, o mais favorável ao contrato) | R$ 125,95 | 1,5× | R$ 98,83 | 1,5× |

**O preço contratado supera o teto em todas as hipóteses**, inclusive nas que nenhum documento sustenta. O excesso contratado é de R$ 1.195.063 na hipótese documentada.

O agente acertou os dois tetos e o tipo de cada um: preço-fábrica para a NPH, que não tem CAP, e PMVG para a Regular, que tem.

### 5.3 Análogas em caneta (itens 194 e 195)

O pacote não tinha teto para elas, porque o item não diz a substância. Comparei o preço contratado com o **maior** teto por caneta entre todas as análogas do mesmo tipo:

- Item 194, ação prolongada: R$ 195,68 contra R$ 169,97 (Tresiba). Acima.
- Item 195, ação rápida: R$ 194,76 contra R$ 35,14 (Humalog). 5,5× acima.

O excesso é de R$ 18.533. O cálculo próprio resultou em 15 itens acima do teto; com essas duas, 17. A consulta posterior ao arquivo `correcao_C4.csv` da preparação mostrou os mesmos 15, os mesmos 17 e o mesmo excesso, obtidos por outro caminho.

### 5.4 O que o agente disse e o que os dados mostram

| Afirmação do agente (29/01/2025) | Evidência posterior | Resultado |
|---|---|---|
| A estimativa das canetas é 9,6× e 9,3× o teto e não pode ser usada | Homologadas exatamente na estimativa, com proposta única | **Acertou. É o maior achado da decisão** |
| "Sugere confusão de apresentação ou de referência" | A unidade é caneta em todos os documentos | Não houve confusão de unidade; o preço é que não tem base |
| Risco de deserto: o mercado de canetas em 2024 estava acima do teto | Em 2026 o mesmo comprador homologou a caneta a R$ 29,00, acima do teto de 0% (R$ 21,16 em nov/2026) e do de 20% (R$ 26,45) | **Risco real.** Limitada ao teto de 0%, a caneta provavelmente ficaria sem proposta |
| Confirmar a cota do MS: insulinas humanas seriam de aquisição centralizada | Notas técnicas 169/2022 e 164/2023, anteriores ao corte: o MS compra NPH e Regular, em frascos e canetas, e a rede é abastecida com 70% em canetas | **Acertou na substância.** Citou a Portaria de Consolidação nº 6; as notas citam a nº 2, Anexo XXVIII, art. 35 |
| Frascos 197 e 198: referência de R$ 26,88 e R$ 25,00 | Homologado em 2025: R$ 48,00, com 2 proponentes. Em 2026: R$ 25,81 | Acertou o mercado; o pregão de 2025 pagou 1,8× mais |
| Análoga rápida 195: R$ 26,52, "referência fraca" | 2025: R$ 194,76. 2026: R$ 55,49 | Errou por 2×, na direção certa, e avisou |
| Análoga prolongada 194: R$ 141,58, "referência fraca" | 2025: R$ 195,68. 2026: R$ 55,00 | Errou por 2,6× para cima, e avisou |

Custo das seis insulinas nas quantidades do ETP: R$ 1.402.796 no contratado de 2025; R$ 172.639 na referência do agente; R$ 235.335 aos preços que o próprio município obteve em 2026 (`resultados/insulinas_agente_x_evidencia.csv`). **A referência do agente ficou 27% abaixo do que o mercado entregou depois; a decisão real ficou 6× acima.**

### 5.5 Contratado não é pago

O contrato que inclui as canetas pagou R$ 162.874 no total de seus 128 itens. Isso equivale a 12,2% do valor das canetas. Mesmo que tudo tivesse sido gasto com canetas NPH, seriam no máximo 844 das 6.000 contratadas. **O excesso efetivamente pago nas canetas está entre zero e R$ 145.869.** O valor exato não é observável: os empenhos têm histórico genérico e as notas fiscais não são públicas.

O sobrepreço de R$ 1,2 milhão é, portanto, um risco contratado e ainda aberto, porque o contrato foi prorrogado até março de 2027. O dano realizado é muito menor.

---

## 6. Viabilidade e riscos (dimensão D)

Evidência por dimensão em `resultados/viabilidade_evidencias.csv`.

**Jurídica.** A forma de julgamento recomendada é a que o órgão adotou em 2025 e repetiu em 2026. O registro de preços teria evitado contratos de R$ 3,1 milhões para uma execução de R$ 0,59 milhão. As normas que o agente citou como conhecimento prévio constam no log da preparação como conferidas no Planalto; não refiz essa conferência.

**Operacional.** O contrato real previu fornecimento parcelado, com entrega em até cinco dias úteis do pedido, pela mesma razão que o agente apontou: não há armazém. A mediana foi de 6 proponentes por item e houve 7 contratados.

**Orçamentária.** O agente recomendou reservar o limite alto do E1, R$ 2,51 milhões, em vez dos R$ 4,95 milhões. O gasto real por todas as vias foi de R$ 1,54 milhão nos 12 meses de março de 2025 a fevereiro de 2026.

**Mercado: o risco de itens sem contratação.** Esta é a principal fragilidade prática do E1.
- A regra do agente é aceitar só preço igual ou menor que a referência. O mercado real, para este comprador, ficou acima do limite alto do agente em 60 itens (18%).
- Desses 60, 41 tinham no máximo 3 proponentes e 26 saíram exatamente na estimativa do órgão. Entre os 246 itens com 4 ou mais proponentes, só 19 (7,7%) ficaram acima do limite.
- O mercado nacional mostra que o limite era alcançável em 42 dos 50 itens com mediana disponível, e o próprio município ficou dentro dele em 37 dos 51 itens repetidos em 2026 (`resultados/risco_deserto.csv`).
- Leitura: entre 6% e 18% dos itens exigiriam negociação ou segunda rodada. O agente previu isso, fixou o gatilho de revisão em 20% de itens desertos e indicou contingências. A contingência por adesão a atas de outros estados é a parte menos testada do plano.

**Riscos que o agente não quantificou.**
- A exclusividade para micro e pequenas empresas em 332 itens pode reduzir a competição, que foi o que determinou o preço. O edital real foi de ampla participação.
- O custo administrativo de pesquisar preço para 63 itens e conferir manualmente 25 itens e dezenas de vínculos antes do edital, com a equipe de um município de 15 mil habitantes.
- A comparação com o contrato de quantidade fixa (E4) supõe que o fornecedor exigiria a quantidade contratada. Na prática o órgão tratou os contratos fixos como se fossem ata, sem consequência observada até aqui.

---

## 7. Sensibilidade da recomendação (dimensão E)

Critério do protocolo: a decisão muda se o E1 deixar de ter o menor custo entre E1, E2 e E4. São 17 cenários em `resultados/sensibilidade_recomendacao.csv`.

| Cenário | E1 | E2 | Muda? |
|---|---:|---:|---|
| Base do agente | 1.812.130 | 4.035.750 | não |
| Pacote v2, com a errata | 1.813.119 | 4.035.753 | não |
| Canetas com teto a 20% | 1.847.101 | 4.035.750 | não |
| Insulinas humanas fora da compra municipal | 1.656.302 | 3.902.057 | não |
| Preços reais homologados, limitados ao teto | 1.843.391 | 4.035.750 | não |
| Preços reais homologados, sem limite (canetas a R$ 193,02) | 3.105.250 | 4.035.750 | não |
| Mediana nacional posterior | 1.765.928 | 4.035.750 | não |
| Itens sem referência pela estimativa do órgão | 2.038.899 | 4.262.519 | não |
| Demanda igual à fração executada (18,9%) | 342.449 | 762.659 | não; o contrato fixo comprometeria 1.812.130 |
| Insulinas fora, preços reais com teto, E2 no limite baixo | 1.674.702 | 2.172.335 | não |
| **E1 no limite alto e E2 no limite baixo** | 2.508.722 | 2.300.004 | **sim** |
| **Preços reais sem limite e E2 no limite baixo** | 3.105.250 | 2.300.004 | **sim** |

A recomendação se mantém em 15 de 17 cenários. Os dois em que muda combinam o melhor caso do E2 com o pior do E1. O primeiro foi declarado pelo próprio agente. O segundo exige aceitar as canetas acima do teto, o que o E1 proíbe.

**Ressalva que vale para a tabela inteira:** o E2 é sempre um modelo. Ver a seção 8.2.

---

## 8. Economia: potencial, contratada e realizada (dimensão F)

Tabela completa em `resultados/economia_tres_niveis.csv`. Os níveis não se somam.

### 8.1 Os três níveis

**Potencial (do agente, antes de decidir).**
- R$ 2.223.619 frente ao modelo de desconto sobre a CMED; faixa plausível de R$ 0,80 a 2,03 milhões.
- R$ 1.744.021 frente à estimativa do órgão limitada ao teto.
- O agente separou os R$ 1.396.287 de estimativas acima do teto como correção de conformidade, e não como economia. Está correto.

**Contratada (da decisão real).**
- R$ 1.847.188 frente à estimativa do órgão. Toda essa diferença vem dos 332 itens fora das canetas. A referência é inflada em cerca de 2×; não mede ganho de mercado.
- R$ 450.902 frente à estimativa limitada ao teto.
- O homologado real ficou R$ 98.060 acima do central do agente nos 332 itens e R$ 1.261.859 acima do que resultaria de aplicar o teto CMED aos mesmos preços.

**Realizada.**
- Observado: R$ 585.893 pagos, 18,9% do contratado.
- Não observável: quantidade entregue e preço pago por item. Não há economia realizada mensurável por item.
- Estimativa, sob a hipótese de que cada contrato executou seus itens na proporção do valor contratado: R$ 552.404 frente à estimativa do órgão. É estimativa, contra uma referência inflada.
- Da estratégia do agente: **nenhuma.** Ela não foi executada.

### 8.2 Por que o número de R$ 2,22 milhões não se sustenta

1. **É maior que o gasto real.** O município gastou R$ 1,41 milhão com medicamentos em 2025, por todas as vias. Uma economia de R$ 2,22 milhões é impossível nessa escala. Ela resulta de multiplicar a diferença de preço pelas quantidades do ETP, que a execução mostrou serem muito maiores que as compradas.
2. **Depende de um modelo que nenhum dado confirma.** O custo do E2, de R$ 4,04 milhões, supõe que o fornecedor cobra o preço-fábrica da CMED menos o desconto de 2024. O PE 12/2024 não publica preço por item. A própria faixa do agente para o E2 vai de R$ 2,30 a 4,54 milhões.
3. **O agente avisou.** Declarou a hipótese, deu a faixa, mostrou que a economia cai na proporção da demanda e escreveu que o custo do E1 "não valida as quantidades". Mesmo assim, apresentou R$ 2,22 milhões como número principal do resumo executivo.

### 8.3 O que os dados posteriores dizem sobre a direção

Nos 223 itens cobertos pelo modelo de desconto, fora as canetas (`resultados/e2_teste_expost.csv`):

| | Valor, nas quantidades do ETP |
|---|---:|
| E1 do agente | R$ 1.111.265 |
| Homologado real por item (PE 04/2025) | R$ 1.147.518 |
| E2 modelado, limite baixo | R$ 1.728.956 |
| E2 modelado, central | R$ 3.363.828 |

O pregão por item real, mesmo com a estimativa inflada como teto, ficou abaixo do E2 modelado no cenário mais favorável ao E2. A direção da conclusão do agente se sustenta. A magnitude segue sendo modelo.

**Extrapolação, não observação.** O órgão gastou R$ 1.491.033 pelo contrato de desconto em 2025 e 2026. Se a razão entre os preços por item e os preços do modelo de desconto valesse para esse gasto, a parcela evitável ficaria entre R$ 0,5 milhão (E2 no limite baixo) e R$ 1,0 milhão (E2 central), em 23 meses. Essa é a ordem de grandeza defensável, e ela depende inteiramente do modelo.

---

## 9. Qualidade da decisão: acertos e limitações

### Acertos

1. **Diagnóstico.** "O problema não está em escolher uma modalidade para um valor conhecido. A própria referência de valor está comprometida." Os dados posteriores confirmam: a estimativa do órgão ficou 2,3× acima do mercado e determinou o preço de todos os itens sem competição.
2. **Referência de preço calibrada.** Erro mediano de 13% em relação ao mercado posterior, contra 132% da estimativa do órgão.
3. **Faixa de incerteza honesta.** O resultado real, sem as canetas, caiu dentro da faixa. Com teto, os três contrafactuais de preço ficaram entre R$ 1,71 e 1,84 milhão, contra o central de R$ 1,81 milhão.
4. **Canetas de insulina.** Identificou, isolou e quantificou o que veio a ser o maior desvio do processo real.
5. **Instrumento adequado à incerteza de demanda.** Registro de preços em vez de quantidade fixa.
6. **Crítica aos próprios dados.** Três das quatro falhas apontadas no pacote foram confirmadas; duas viraram errata.
7. **Disciplina.** Não usou preço "a conferir", não misturou categorias de valor, separou economia potencial de efetiva e correção de conformidade de economia, e descreveu como medir a economia efetiva.
8. **Riscos de transição** previstos e confirmados.

### Limitações

1. **Economia superestimada em valor absoluto** e apoiada em um contrafactual não verificável (seção 8.2).
2. **Faixa de demanda estreita.** O agente tinha o gasto de 2024 e a observação de que a estimativa de 2025 era 2,54× esse gasto. Poderia ter concluído que as quantidades estavam infladas; preferiu não concluir.
3. **Regra de aceitação rígida.** "Preço igual ou menor que a mediana" deixa itens sem contratar onde há pouca competição. A contingência principal, adesão a atas de outros estados, é a de menor viabilidade operacional, como o próprio agente reconheceu.
4. **Canetas no teto de 0%.** A referência adotada ficou abaixo do que o mercado praticou para este comprador. O agente avisou do risco, mas a solução dependia de terceiros (cota do MS).
5. **Referências fracas nas análogas**, com erro de 2× a 2,6×.
6. **Um falso positivo** (item 268) e uma citação normativa imprecisa.
7. **É uma recomendação com condições.** O texto lista nove verificações antes de executar: saldo, estoque, consumo, vigência de instrumentos, regulamento municipal, validação humana de vínculos, Convênio 87/02, cota de insulinas e pesquisa direta. Sem elas não há edital. A decisão é boa como análise; a parte difícil ficou para a organização.
8. **Custos de transação e capacidade administrativa** não entraram no critério de eficiência.

---

## 10. O que o experimento demonstra sobre a capacidade da IA de tomar decisões organizacionais

### O que ficou demonstrado

- **Estruturar um problema mal definido.** Sem lista de alternativas, o agente formulou quatro estratégias, descartou dez com motivo, definiu um critério de eficiência e o aplicou de forma coerente.
- **Calcular de forma exata, rastreável e reprodutível.** Zero erro em 59 verificações, com scripts que outro avaliador reexecuta e obtém os mesmos bytes. Poucos processos administrativos reais têm esse padrão.
- **Fazer a diligência que a norma já exige, a custo quase nulo.** A vantagem do agente sobre a decisão real não veio de uma ideia nova. Veio de consultar o Banco de Preços em Saúde e a tabela da CMED para os 334 itens, o que o art. 23 da Lei 14.133 já pede, e que o processo real não fez de modo efetivo. A IA levou 24 minutos.
- **Encontrar inconsistências nos dados que recebeu**, inclusive duas que escaparam a quem montou o pacote.
- **Declarar o que não sabe.** A incerteza declarada cobriu o resultado real, e as hipóteses frágeis foram marcadas como tais.
- **Respeitar um limite de informação**, conforme a auditoria da Etapa 4.

### O que não ficou demonstrado

- **Que a IA decide.** O produto é uma recomendação condicionada a nove verificações humanas. Decidir inclui responder pela escolha, negociar com fornecedor, lidar com item deserto, ajustar durante a execução. Nada disso foi testado.
- **Que a estratégia funcionaria.** O E1 nunca foi licitado. Todo resultado atribuído a ele é contrafactual. O que se observou é que a referência de preço era boa, não que o pregão do agente teria fechado.
- **Que a IA dispensa a preparação dos dados.** O agente recebeu um pacote com itens padronizados, vínculos classificados, corte temporal garantido e incertezas listadas, fruto de três etapas de trabalho. Esse pacote ainda continha erros. A qualidade da decisão é, em boa parte, a qualidade dessa curadoria.
- **Que a IA supera um bom decisor humano.** A linha de base era fraca: estimativa 2× acima do mercado e canetas a quase 10× o teto. Superar essa linha de base mostra que o processo real tinha falhas básicas, não que a IA tem julgamento superior.
- **Generalidade.** É uma execução, de um modelo, em um caso. Não há medida de variação entre execuções.

### O que o desenho não permite afirmar

- **Ausência de vazamento temporal.** A auditoria verifica o que o agente acessou, não o que o modelo já sabia. Não encontrei sinal de uso de informação posterior: o agente previu deserto nas canetas, e não a homologação pela estimativa. Mas ausência de sinal não é prova.
- **Independência plena da avaliação.** Decisor e avaliador são da mesma família de modelos (seção 2).

### Conclusão

O experimento sustenta uma afirmação mais modesta e mais útil do que "a IA toma decisões organizacionais": **a IA executa com rigor a parte analítica de uma decisão organizacional**, isto é, diagnóstico, alternativas, estimativa com incerteza e identificação de riscos, e o faz de modo auditável. O valor aparece onde a organização tem os dados e não tem tempo ou método para usá-los. O limite aparece em tudo o que depende de fatos fora do pacote, de execução e de responsabilidade.

Para Santa Luzia, o ganho concreto não seria "seguir o agente". Seria ter recebido, em janeiro de 2025, três avisos que os dados posteriores confirmaram: a estimativa está duas vezes acima do mercado; as canetas de insulina estão quase dez vezes acima do teto legal; as quantidades não têm base de consumo.

---

## 11. Limitações desta avaliação

1. **Contrafactual.** Nenhuma estratégia não adotada tem resultado observado. Os contrafactuais de preço usam preços de um certame cujo teto era a estimativa inflada, o que tende a superestimá-los.
2. **Execução por item desconhecida.** Só há empenho e pagamento por contrato. Notas fiscais e termos de recebimento não são públicos.
3. **Contrato de desconto sem preço por item.** A comparação entre E1 e E2 é modelo dos dois lados.
4. **Mercado nacional posterior.** A regra de compatibilidade para o Compras.gov.br foi inferida dos registros anteriores ao corte (408 combinações, nenhuma ambígua). Para 89 itens não há 5 registros compatíveis. Os registros de canetas são poucos e têm unidade inconsistente; por isso a evidência de mercado das canetas é o PE 09/2026 do próprio município.
5. **Tetos CMED sem validação humana.** A contagem de 13 itens acima do teto fora das insulinas depende de vínculos automáticos.
6. **Normas.** Não refiz a leitura do art. 86 da Lei 14.133 nem do Decreto 12.343/2024.
7. **Avaliador não cego** aos resultados resumidos da preparação e da mesma família de modelos do decisor.
8. **Desvios do protocolo**, registrados no `LOG_ETAPA_5.md`: horizonte de 12 meses em vez do ano civil de 2025 na comparação nacional; cenários de sensibilidade renumerados e ampliados; e atribuição de veredito, que o protocolo reservava a esta etapa.
