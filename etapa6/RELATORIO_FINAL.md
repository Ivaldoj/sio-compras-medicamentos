# Relatório final — Uma IA consegue decidir uma compra pública de medicamentos?

Disciplina Sistemas de Informação nas Organizações (SIO), UFPB. Caso: Secretaria Municipal de Saúde de Santa Luzia/PB. Experimento executado de 22 a 24/11/2026; data de decisão simulada: 29/01/2025.

Este relatório é autocontido. Cada número traz o arquivo de origem; a seção 11 diz como conferir. Nada foi reexecutado nesta etapa: ela lê os resultados gravados e vai às fontes primárias apenas para resolver duas divergências entre as avaliações.

---

## 1. Síntese

**Pergunta.** Um agente de IA, com as informações que a organização tinha no dia da decisão, formula e escolhe uma estratégia de compra melhor que a adotada?

**Resposta.** Em parte. O agente fez bem a análise e apontou três problemas que os dados posteriores confirmaram. Não ficou demonstrado que a estratégia dele funcionaria, porque ela nunca foi executada.

**O que foi observado** (fatos, não estimativas):

| Fato | Valor |
|---|---|
| Estimativa do órgão para os 334 itens | R$ 4.952.438 |
| Valor contratado na decisão real (PE 04/2025) | R$ 3.105.250 |
| Valor pago em cerca de 20 meses | R$ 585.893 (18,9%) |
| Itens com proposta única, todos contratados no preço máximo do edital | 27 itens, 50% do valor contratado |
| Canetas de insulina humana: preço contratado sobre o teto legal (CMED) | 9,6× e 9,3× |
| Valor contratado acima do teto CMED | R$ 1.280.392, em 17 itens |
| Cálculos do agente que conferem ao serem refeitos | todos (20 de 20 e 59 de 59, em duas verificações separadas) |

**O que é estimativa:**

| Estimativa | Valor | De que depende |
|---|---|---|
| Custo da estratégia do agente | R$ 1,81 mi (faixa de 1,50 a 2,51) | previsão feita antes da decisão |
| Mesma estratégia aos preços reais, limitados ao teto | R$ 1,84 mi | preços de um pregão com outro preço máximo |
| Economia potencial anunciada pelo agente | R$ 2,22 mi | modelo do contrato de desconto, sem preço por item observado, e quantidades do ETP |

**Sobre as duas divergências entre as avaliações** (seção 7):
- **ICMS na tabela da CMED:** a avaliação independente estava certa. A tabela publica os valores a 20% para os produtos do Convênio 87/02; a leitura do pacote os descartou.
- **Insulinas de 2026:** a preparação anterior estava certa. O preço de R$ 29,00 homologado em 2026 é de refil sem caneta, não de caneta. Três afirmações da Etapa 5 que usavam esse preço ficam retiradas.

Nenhuma das duas altera o veredito.

---

## 2. Metodologia

### 2.1 Desenho

O experimento separa três papéis, para que quem decide não veja o resultado:

1. **Preparação dos dados**, com corte temporal em 29/01/2025.
2. **Decisão** por um agente isolado, que recebe só o que existia até o corte.
3. **Avaliação** contra os dados posteriores, que ficaram reservados.

### 2.2 Etapas

| Etapa | O que fez | Registro |
|---|---|---|
| 1. Auditoria de dados | Avaliou seis fontes públicas (BPS, Medicamentos Transparentes, PNCP, BNAFAR, TCE-PB, CMED). Classificação: viável com complementações e hipóteses explícitas | `LOG_AUDITORIA.md`, `docs/01` a `06` |
| 2. Caso organizacional | Triou seis organizações da Paraíba e escolheu Santa Luzia, que tem ETP, edital, resultado por item e execução públicos | `LOG_ETAPA_2.md`, `docs/07` a `11` |
| 3. Integração | Padronizou os 334 itens, vinculou-os a preços praticados e ao teto CMED, e classificou cada registro como anterior ou posterior ao corte | `LOG_ETAPA_3.md`, `docs/12` a `17` |
| Pré-4. Lacunas | Acrescentou o Compras.gov.br, a regra de ICMS da Paraíba e contratações comparáveis | `LOG_PRE_ETAPA_4.md`, `docs/18` |
| 4. Decisão | Um agente (Claude Opus 5.5) recebeu um enunciado e o pacote. Trabalhou 24 minutos, em 56 chamadas de ferramenta, sem internet. A transcrição foi auditada chamada por chamada | `LOG_ETAPA_4.md`, `etapa4/` |
| Pré-5. Preparação da avaliação | Verificou as falhas que o agente apontou no pacote, criou o pacote v2 com errata, pré-registrou o protocolo e calculou os indicadores, sem veredito | `LOG_PRE_ETAPA_5.md`, `docs/19` e `20`, `etapa5/` |
| 5. Avaliação independente | Uma sessão nova (Claude Fable 5.2) refez os cálculos com código próprio e deu o veredito | `LOG_ETAPA_5.md`, `etapa5_avaliacao_independente/` |
| 6. Consolidação | Confrontou as duas avaliações e resolveu as divergências | `LOG_ETAPA_6.md`, `etapa6/` |

### 2.3 O que o agente recebeu

- **O problema:** 334 medicamentos para 12 meses, estimados pelo órgão em R$ 4.952.438, com forma de aquisição a decidir.
- **Restrições:** Lei 14.133/2021; teto CMED; não há local para armazenar; entrega na Secretaria; validade mínima.
- **Dados:** preços praticados por outros órgãos (BPS e Compras.gov.br), tabela CMED de janeiro de 2025, contratações comparáveis do PNCP e a execução de 2024 do próprio município.
- **O que não se sabia:** consumo real, estoque, saldo orçamentário e os preços que o mercado ofertaria.
- **Exigências:** pelo menos três estratégias próprias; custos com faixa; toda afirmação classificada como observada, calculada, inferida, hipótese ou conhecimento prévio; economia potencial separada de efetiva.

### 2.4 Controles

- **Isolamento.** A auditoria da transcrição não encontrou leitura fora do ambiente, acesso à internet nem uso de outro agente (`etapa4/registro/auditoria_resumo.json`).
- **Congelamento.** Os arquivos da decisão têm sha256 registrado. Nesta etapa, 143 de 143 arquivos conferidos estão íntegros (`etapa6/resultados/integridade.csv`).
- **Protocolo pré-registrado**, com hash anterior ao cálculo (`etapa5/PROTOCOLO_AVALIACAO.md`).
- **Duas avaliações**, feitas por sessões diferentes, com código diferente.

---

## 3. Alternativas elaboradas pelo agente

Fonte: `etapa4/ambiente_decisor/saida/02_alternativas.md` e `03_comparacao.csv`. Todos os custos são estimativas do agente, nas quantidades do ETP.

| Estratégia | Custo central | Faixa | Avaliação do agente |
|---|---:|---:|---|
| **E1.** Pregão para registro de preços, por item, com referência saneada | R$ 1,81 mi | 1,50 a 2,51 mi | Recomendada |
| **E2.** Maior desconto sobre a tabela CMED (modelo usado pelo órgão em 2024) | R$ 4,04 mi | 2,30 a 4,54 mi | 2,2× mais cara |
| **E3.** Adesão a atas de outros órgãos, com E1 no restante | R$ 1,71 mi | 1,46 a 2,26 mi | Só como contingência: dezenas de adesões a atas de outros estados |
| **E4.** Contrato de quantidade fixa | R$ 1,81 mi | igual à do E1 | Dominada: compromete o total mesmo se a demanda cair |

O agente também registrou dez alternativas descartadas, com motivo. Entre elas: dispensa por valor, dispensa emergencial, credenciamento, lote único, consórcio e uso da estimativa do órgão como referência.

**Critério de eficiência adotado:** menor custo esperado para cobrir os 334 itens por 12 meses, entre as estratégias viáveis; desempate pelo risco de descontinuidade.

---

## 4. A decisão do agente e a decisão real

| | Agente (E1) | Decisão real (PE 04/2025) |
|---|---|---|
| Modalidade e julgamento | Pregão eletrônico, por item, menor preço | Igual |
| Instrumento | Ata de registro de preços: não obriga a comprar | Sete contratos de quantidade total |
| Preço máximo aceito | Mediana dos preços praticados em 24 meses, limitada ao teto CMED | Estimativa do órgão |
| Insulinas em caneta | Referência no teto CMED; confirmar antes a cota do Ministério da Saúde | Contratadas pela estimativa |

As duas decisões coincidem na forma de licitar e diferem em três pontos. A comparação possível é, portanto, sobre esses três pontos.

**O diagnóstico do agente**, que sustenta a recomendação (`01_diagnostico.md`):
1. a estimativa do órgão está, em mediana, 2,04× acima do preço praticado;
2. em 41 itens ela supera o teto legal, com excesso de R$ 1,40 mi, 85,6% disso nas duas canetas de insulina;
3. não há dado de consumo nem de estoque que sustente as quantidades.

---

## 5. Resultados quantitativos

Origem dos números: `etapa5_avaliacao_independente/resultados/`, salvo indicação. Os valores marcados como idênticos na seção 7 foram obtidos também pela preparação anterior.

### 5.1 Evidências observadas

**Preços contratados.**

| | 334 itens | Canetas 196 e 199 | Demais 332 |
|---|---:|---:|---:|
| Estimativa do órgão | R$ 4.952.438 | R$ 1.334.952 | R$ 3.617.486 |
| Contratado | R$ 3.105.250 | R$ 1.334.952 | R$ 1.770.298 |

As duas canetas foram contratadas exatamente pela estimativa, com uma única proposta (`expost_totais.csv`, `insulinas_evidencias_documentais.csv`).

**Competição** (propostas extraídas da Ata Final; `expost_competicao.csv`).

| Proponentes no item | Itens | Contratados exatamente na estimativa | Valor contratado |
|---|---:|---:|---:|
| 1 | 27 | 27 | R$ 1.558.701 |
| 2 ou 3 | 61 | 14 | R$ 425.315 |
| 4 ou mais | 246 | 2 | R$ 1.121.234 |

**Teto CMED.** Quinze itens foram contratados acima do teto, com excesso de R$ 1.261.859. Com as duas insulinas análogas, comparadas ao maior teto possível do seu tipo, são 17 itens e R$ 1.280.392. Os tetos fora das insulinas vêm de vínculos automáticos, sem validação humana.

**Canetas de insulina humana.** A unidade é a caneta no ETP, no Termo de Referência, no contrato e no aditivo; nenhum documento menciona caixa. O preço contratado supera o teto em todas as hipóteses testadas, inclusive nas não documentadas (`insulinas_impacto.csv`).

**Execução** (`expost_execucao_contratos.csv`, `expost_gasto_por_licitacao.csv`).
- Contratado: R$ 3.105.250. Empenhado: R$ 586.817. Pago: R$ 585.893.
- O contrato que inclui as canetas, de R$ 2.096.244, teve 7,8% pagos. Ele foi prorrogado até março de 2027.
- O órgão seguiu comprando principalmente pelo contrato de desconto sobre a CMED: R$ 865.727 em 2025, ou 61% do gasto com medicamentos.
- Gasto total com medicamentos em 2025: R$ 1.410.230.

**Mercado nacional posterior** (`expost_itens.csv`; 245 itens com 5 registros ou mais nos 12 meses seguintes).

| Preço comparado à mediana nacional posterior | Razão mediana |
|---|---:|
| Referência do agente | 1,11 |
| Estimativa do órgão | 2,32 |
| Contratado | 1,02 |

**Previsão do agente contra o contratado.** Nos 332 itens fora das canetas, o agente previu R$ 1.672.237 e o contratado foi R$ 1.770.298, 5,9% acima e dentro da faixa. Por item: 185 dentro da faixa, 89 abaixo e 58 acima.

**Normas anteriores ao corte.** Notas técnicas do Ministério da Saúde, de 2022 e 2023, registram que o Ministério compra de forma centralizada as insulinas humanas NPH e Regular, em frascos e canetas. O agente havia marcado esse ponto como "a verificar". A cota de Santa Luzia é desconhecida.

### 5.2 Estimativas contrafactuais

Nenhuma destas foi observada. A estratégia do agente não foi licitada.

| Estimativa | Valor | Ressalva |
|---|---:|---|
| E1 aos preços contratados, limitados ao teto | R$ 1.843.391 | Os preços vêm de um pregão cujo máximo era a estimativa inflada |
| E1 limitado ao máximo que o agente aceitaria | R$ 1.712.434 | Supõe que os itens acima do limite seriam comprados no limite |
| E1 à mediana nacional posterior | R$ 1.765.928 | 245 itens; os demais pelo preço contratado com teto |
| Custo do modelo de desconto (E2) | R$ 4.035.750 | Modelo do agente. O contrato real não tem preço por item |
| Itens que ficariam sem contratar na primeira rodada do E1 | 19 a 60 (6% a 18%) | Mínimo: itens acima do limite mesmo com 4 ou mais proponentes. Máximo: todos os que ficaram acima |

**Sensibilidade.** A preparação testou 9 cenários e nenhum mudou a recomendação. A avaliação independente testou 17 e dois mudaram, ambos cruzando o pior caso do E1 com o melhor do E2. Em todos os cenários o E2 é modelo.

### 5.3 Economia em três níveis

Os níveis não se somam.

| Nível | Decisão real | Estratégia do agente |
|---|---|---|
| **Potencial** (estimada antes) | — | R$ 2.223.619 frente ao E2; R$ 1.744.021 frente à estimativa limitada ao teto |
| **Contratada** (observada) | R$ 1.847.188 frente à estimativa do órgão; R$ 450.902 frente à estimativa limitada ao teto | Não existe |
| **Realizada** | Pago: R$ 585.893. Por item, não observável. Estimativa sob hipótese de mix proporcional: R$ 552.404 | Não existe |

**Sobre os R$ 2,22 milhões.** O número supera o gasto anual real com medicamentos, de R$ 1,41 milhão. Ele resulta de aplicar uma diferença de preço modelada às quantidades do ETP, que a execução mostrou serem muito maiores que as compradas. A direção tem apoio indireto: nos 223 itens cobertos pelo modelo de desconto, o contratado por item (R$ 1.147.518) ficou abaixo do E2 no seu cenário mais favorável (R$ 1.728.956). A magnitude não tem apoio (`e2_teste_expost.csv`).

**Sobre o sobrepreço das canetas.** Foi contratado, não necessariamente pago. O contrato pagou R$ 162.874 no total de seus 128 itens. O excesso pago nas canetas está entre zero e R$ 145.869.

---

## 6. Avaliação independente (Etapa 5)

Veredito registrado em `etapa5_avaliacao_independente/RELATORIO_ETAPA5.md`, mantido como foi escrito.

| Dimensão | Resultado |
|---|---|
| Precisão dos cálculos | Alta |
| Qualidade da referência de preço | Alta |
| Qualidade da decisão | Boa, com ressalvas |
| Viabilidade | Provável, não demonstrada |
| Identificação de riscos | Boa |
| Economia projetada | Correta na direção, fraca como número |

**Ressalvas do veredito:**
- a economia anunciada está superestimada em valor absoluto;
- a faixa de demanda do agente (75% a 125% do ETP) foi estreita;
- a regra de aceitar só preço até a mediana deixaria itens sem contratar;
- o agente entregou uma recomendação com nove verificações a fazer por pessoas, não uma decisão executada.

---

## 7. Confronto entre as duas avaliações

`etapa6/scripts/e6_01_confronto.py` compara 25 indicadores (`etapa6/resultados/confronto_numeros.csv`).

- **12 idênticos**, entre eles o contratado, o pago, os itens acima do teto, o excesso e as três economias.
- **11 convergentes ou compatíveis**, com diferenças explicadas por escolhas de método, como a janela de mercado (ano civil de 2025 ou 12 meses a partir do corte).
- **2 divergentes**, tratados abaixo.

A concordância é evidência mais forte que qualquer das avaliações sozinha: os números saíram de códigos diferentes. Ela não é independência completa: as duas avaliações foram feitas por modelos da mesma família, sobre o mesmo pacote.

### 7.1 Divergência 1: valores de ICMS a 20% na tabela da CMED

| | Preparação (errata E-05) | Avaliação independente |
|---|---|---|
| Afirmação | A tabela não publica a coluna de 20% para os 2.810 registros do Convênio ICMS 87/02. "Fato da fonte, não falha do pacote" | A tabela publica esses valores, com asterisco |

**Verificação na fonte**, célula a célula, no arquivo `cmed_pmvg_20250107.xls` (sha256 `1d3f27dd…`; `divergencia_cmed_icms_celulas.csv`):
- os 2.810 registros do Convênio têm a célula "PF 20%" preenchida, como texto com asterisco (por exemplo, `25.18*` para a caneta Novolin N);
- nenhuma está vazia e nenhuma é número puro;
- outras 650 células fora do Convênio têm o mesmo asterisco.

**Causa.** O script que montou o pacote converteu a coluna para número e descartou o que não era número puro (`scripts/23_cmed_jan2025.py`, linha 23). A frase "0 de 2.810 na lista bruta" está escrita como texto fixo no script de verificação, e não calculada (`scripts/31_verifica_falhas_pacote_v2.py`, linha 180).

**Resolução: a avaliação independente está certa quanto ao fato.** É uma falha de leitura do pacote. A errata E-05 descreve a causa de forma incorreta.

**O que não muda:**
- A alíquota aplicável continua sendo 0%. A nota (viii) da própria tabela diz que ela mostra todas as alíquotas mesmo quando não se aplicam, e marca com asterisco os preços das apresentações com isenção.
- A preparação estimou o valor a 20% multiplicando por 1,25. A razão real na tabela é 1,25. Por isso as duas sensibilidades coincidem: E1 de R$ 1.847.114 e de R$ 1.847.101.
- O agente declarou a lacuna e usou a alíquota mais restritiva.

### 7.2 Divergência 2: equivalência das insulinas de 2026

| | Preparação (doc 20) | Avaliação independente (Etapa 5) |
|---|---|---|
| Uso do preço de R$ 29,00 do PE 09/2026 | Não usado: o vencedor ofertou refil sem caneta | Usado como preço da "mesma caneta" |

**Verificação na fonte**, na Ata Final do PE 09/2026, página 26 (`divergencia_insulinas_2026.csv`):

| Item de 2026 | Item de 2025 | Produto declarado pelo vencedor | Preço | Equivale ao item? |
|---|---|---|---:|---|
| 191 | 196, NPH em caneta | "5 REFIL 3ML S/CANETA NOVOLIN N penfil" | R$ 29,00 | **Não**: refil sem caneta |
| 194 | 199, Regular em caneta | "5 REFIL 3ML S/CANETA NOVOLIN R" | R$ 29,00 | **Não**: refil sem caneta |
| 189 | 194, análoga prolongada | "INJ BIOM" | R$ 55,00 | Indeterminado: sem apresentação |
| 190 | 195, análoga rápida | "5 CAN 3ML HUMALOG" | R$ 55,49 | Indeterminado: não se sabe se o preço é por caneta ou por caixa |
| 192 e 193 | 197 e 198, frascos | "INJ NOVO NORDISK" | R$ 25,81 | Sim |

**Resolução: a preparação está certa.** A avaliação independente leu só a tabela de resultados do PNCP, que traz a descrição do item do edital, e não o produto ofertado.

**Afirmações da Etapa 5 que ficam retiradas:**
1. "Em 2026 o mesmo comprador homologou a caneta a R$ 29,00."
2. "Risco de deserto real", na parte em que se apoiava nesse preço. O risco continua sendo o que o agente declarou antes da decisão; não há evidência posterior que o confirme ou negue.
3. "A referência do agente ficou 27% abaixo do que o mercado entregou depois" nas insulinas. O valor de R$ 235.335 usado nessa conta tinha R$ 208.800 vindos do preço de refil.

**O que não muda:**
- o preço contratado em 2025 e sua relação com o teto (9,6× e 9,3×), que não dependem de 2026;
- os frascos, em que a equivalência se confirma: o agente previu R$ 26,88 e R$ 25,00, e em 2026 o município pagou R$ 25,81.

**Consequência mais ampla.** A Etapa 5 também comparou 309 itens repetidos no PE 09/2026 (razão mediana de 0,85 sobre a referência do agente). O produto ofertado não foi conferido item a item. Esse resultado passa a valer só como contexto.

### 7.3 Efeito sobre o veredito

Nenhum. O veredito da Etapa 5 se apoia no preço contratado, na competição, na execução e no mercado nacional, que as duas avaliações obtiveram de forma idêntica.

A lição é de método: **cada avaliação errou uma vez, e o confronto pegou os dois erros.** A preparação errou ao declarar ausência de um dado sem olhar a célula. A avaliação independente errou ao tratar como iguais dois produtos sem ler a proposta. Ambos são erros de leitura de fonte, do mesmo tipo dos que o agente encontrou no pacote.

---

## 8. Relação com os conceitos de SIO: inteligência

O enunciado desta etapa cita "inteligência" sem detalhar. Adotei três leituras usuais na disciplina. Se a intenção era outra, esta seção deve ser ajustada.

### 8.1 Inteligência como fase do processo decisório (Simon)

O modelo de Simon divide a decisão em inteligência (perceber e definir o problema), concepção (formular alternativas), escolha e implementação.

| Fase | O que o experimento mostrou |
|---|---|
| **Inteligência** | Foi onde o agente mais agregou. Redefiniu o problema: de "qual modalidade para um valor conhecido" para "a referência de valor está errada". A organização não fez essa leitura, embora tivesse acesso às mesmas fontes |
| **Concepção** | Quatro estratégias e dez descartadas, sem lista prévia |
| **Escolha** | Critério explícito e aplicado de forma coerente. A escolha coincide com a real na modalidade |
| **Implementação** | Não ocorreu. É a fase em que o experimento não diz nada |

Leitura: o ganho esteve nas fases de inteligência e concepção, não na escolha. A decisão real não falhou por escolher mal entre alternativas; falhou antes, por não perceber o problema.

### 8.2 Dado, informação, conhecimento e inteligência

| Nível | No caso |
|---|---|
| **Dado** | Milhares de registros de preço em bases públicas, a tabela da CMED, os 334 itens do ETP |
| **Informação** | Itens padronizados e ligados a preços comparáveis e ao teto. Custou três etapas de trabalho e ainda continha erros |
| **Conhecimento** | "A estimativa está 2× acima do mercado"; "as canetas estão quase 10× acima do teto" |
| **Inteligência** | Usar esse conhecimento para agir: mudar o preço máximo do edital e o instrumento de contratação |

Os dados eram públicos e a organização os tinha ao alcance. O que faltou foi a transformação em informação utilizável. O agente só fez a passagem para conhecimento porque recebeu a informação já integrada. **A parte cara do sistema de informação foi a integração, não a análise.**

A passagem para inteligência, no sentido de ação, não aconteceu: o conhecimento existiu apenas dentro do experimento.

### 8.3 Inteligência organizacional e apoio à decisão

- **Tipo de decisão.** A compra é semiestruturada: tem regras fixas (lei, teto) e partes de julgamento (demanda, risco de deserto, capacidade da equipe). O agente resolveu a parte estruturada com exatidão e devolveu a não estruturada à organização, como nove verificações.
- **Papel adequado.** O resultado descreve um sistema de apoio à decisão, não um decisor. Ele informa, calcula e alerta; a responsabilidade e a execução ficam com pessoas.
- **Aprendizado organizacional.** Em 2026 o órgão repetiu a estimativa inflada: a estimativa unitária de 2026 foi, em mediana, 0,98 da de 2025 (`expost_escopo.csv`). A organização não incorporou o que a execução de 2025 já mostrava. Inteligência organizacional exige um ciclo de retorno que o caso não tem.
- **Qualidade da informação.** Os erros encontrados em todas as camadas (no pacote, na preparação e na avaliação independente) mostram que a confiabilidade de um sistema de apoio à decisão depende de verificação cruzada, e não da capacidade de quem analisa.

---

## 9. Limitações

**Do experimento.**
1. **Uma execução, um modelo, um caso.** Não há medida de variação.
2. **A estratégia não foi executada.** Todo resultado atribuído a ela é contrafactual.
3. **Linha de base fraca.** Superar uma decisão com estimativa 2× acima do mercado não mostra julgamento superior.
4. **O contrato de desconto não tem preço por item.** A principal comparação do agente é modelo dos dois lados.
5. **Execução por item desconhecida.** Notas fiscais e termos de recebimento não são públicos.
6. **Vínculos automáticos.** Nenhuma conversão de unidade ou vínculo com a CMED teve validação humana.
7. **Vazamento temporal não excluído.** A auditoria verifica o que o agente acessou, não o que o modelo já sabia.
8. **Escopo.** O órgão licitou depois outros 89 itens fora dos 334.

**Das avaliações.**
9. **Mesma família de modelos** no decisor, na preparação e na avaliação. Não houve avaliador humano nem avaliador cego.
10. **Normas** lidas pela web, sem cópia local arquivada.
11. **Comparação com 2026** sem conferência do produto ofertado, salvo nas seis insulinas.

**Do que não se pode concluir.**
- Que a IA decide melhor que a organização.
- Que a economia de R$ 2,22 milhões existiria.
- Que o pregão do agente teria fechado todos os itens.
- Quanto foi pago a mais nas canetas.

---

## 10. Conclusões

1. **O agente analisou corretamente.** Os cálculos são exatos e reproduzíveis, e a referência de preço ficou a 11% do mercado posterior, contra 132% de erro mediano da estimativa do órgão.
2. **Os três avisos centrais se confirmaram:** estimativa inflada, canetas acima do teto, quantidades sem base de consumo.
3. **A magnitude da economia não se confirma.** O número de R$ 2,22 milhões é maior que o gasto anual real e depende de um modelo sem observação.
4. **A decisão real e a do agente coincidem na forma de licitar.** A diferença está no preço máximo, no instrumento e no tratamento das insulinas.
5. **O dano realizado é menor que o risco contratado.** Dos R$ 1,28 milhão acima do teto, no máximo R$ 146 mil podem ter sido pagos nas canetas até novembro de 2026. O contrato segue vigente.
6. **O valor da IA esteve na fase de inteligência**, sobre informação que alguém teve de integrar antes.
7. **Ninguém acertou tudo.** O pacote, a preparação e a avaliação independente tiveram erros de leitura de fonte. O que os corrigiu foi o confronto entre trabalhos independentes.

**Resposta à pergunta do experimento.** A IA executou com rigor a parte analítica de uma decisão organizacional. Não ficou demonstrado que ela toma a decisão, e o desenho do experimento não permite demonstrá-lo.

---

## 11. Rastreabilidade e reprodução

**Onde está cada coisa.**

| Conteúdo | Local |
|---|---|
| Enunciado e pacote entregues ao agente | `etapa4/ambiente_decisor/ENUNCIADO.md`, `data/decision_input/` |
| Decisão congelada e transcrição | `etapa4/ambiente_decisor/saida/`, `etapa4/registro/` |
| Dados posteriores ao corte | `data/evaluation_only/` |
| Preparação da avaliação | `etapa5/`, `docs/19`, `docs/20` |
| Avaliação independente | `etapa5_avaliacao_independente/` |
| Confronto e este relatório | `etapa6/` |
| Documentos primários (PNCP, CMED, normas) | `etapa5_avaliacao_independente/ambiente_avaliador/evidencias_primarias/` |

**Para conferir esta etapa**, da raiz do projeto:

```
python -I -X utf8 etapa6/scripts/e6_01_confronto.py .
```

O script só lê. Ele refaz a conferência de integridade, a leitura das células da CMED, a extração das propostas de insulina de 2026 e a tabela de confronto. Dependências: pandas, xlrd e pypdf.

**Para conferir as etapas anteriores:** os comandos estão em `etapa5/LEIA-ME.md` e em `etapa5_avaliacao_independente/LEIA-ME.md`. Não é necessário executá-los para ler este relatório.

**Preservação.** Nenhum arquivo das etapas anteriores foi alterado, inclusive o relatório da Etapa 5, cujas três afirmações retiradas estão registradas aqui e no `LOG_ETAPA_6.md`. O pacote v2 e a errata E-05 também não foram alterados; a correção da E-05 fica como recomendação para uma eventual versão 3.
