# Relatório final — Um agente de IA demonstra inteligência ao escolher como comprar medicamentos?

Disciplina Sistemas de Informação nas Organizações (SIO), UFPB. Caso: Secretaria Municipal de Saúde de Santa Luzia/PB. Experimento executado de 22 a 24/11/2026; data de decisão simulada: 29/01/2025.

Este relatório é autocontido. Cada número traz o arquivo de origem; a seção 11 diz como conferir. Nada foi reexecutado nesta etapa: ela lê os resultados gravados e vai às fontes primárias apenas para resolver duas divergências entre as avaliações.

**Revisão de 24/11/2026.** A pergunta de pesquisa, a síntese, a discussão (seção 8), as limitações e as conclusões foram reescritas para refletir o objetivo original do trabalho. Evidências, números e resultados não mudaram. A versão anterior está no histórico do repositório (commit `76456ab`). O enquadramento dos documentos das etapas anteriores está em `docs/21_objetivo_e_enquadramento.md`.

---

## 1. Síntese

### 1.1 Objetivo e pergunta de pesquisa

**Definição adotada.** Na disciplina, conforme a definição do professor Bellini informada pelo autor do trabalho, inteligência é a **elaboração de cenários alternativos para a escolha do caminho mais eficiente**. O contraste é com o **mero reconhecimento de padrões**: identificar uma regularidade e repeti-la.

**Objetivo.** Demonstrar inteligência, nesse sentido, em um problema organizacional real: verificar se um agente de IA elabora por conta própria cenários alternativos e escolhe entre eles o caminho mais eficiente.

**Pergunta.** Com as informações disponíveis na data da decisão, o agente elabora cenários alternativos e escolhe o mais eficiente, ou apenas reproduz o padrão que os dados sugerem?

**O que o experimento não pretende demonstrar:**
- que a IA é superior a gestores humanos;
- que a IA executa contratações de forma autônoma;
- que houve economia efetivamente realizada.

**Para que serve a comparação com a decisão real.** Ela é a régua da qualidade da escolha experimental: mostra se o caminho escolhido pelo agente era, de fato, eficiente. Não é uma disputa entre a IA e a prefeitura.

### 1.2 Resposta

**Sim: o comportamento observado corresponde à definição, com duas ressalvas.**

| Elemento da definição | O que o agente fez | Onde conferir |
|---|---|---|
| Elaborar cenários alternativos | Formulou 4 estratégias e registrou 10 descartadas, sem lista prévia. Para cada uma, estimou custo central, faixa e gasto com demanda de 75% e de 125% | `saida/02_alternativas.md`, `03_comparacao.csv` |
| Escolher o caminho mais eficiente | Definiu um critério de eficiência, aplicou-o a todas e escolheu a de menor custo entre as viáveis. Calculou o ponto em que a escolha se inverteria | `saida/03_comparacao.md`, `04_recomendacao.md` |
| Não se limitar ao padrão | O padrão nos dados era repetir o modelo de 2024, usado em 62,6% do gasto, com a estimativa do órgão como referência. O agente simulou esse caminho, comparou e o rejeitou | `saida/01_diagnostico.md`; seção 8.2 |

**A escolha era eficiente?** Os dados posteriores indicam que sim, nos três pontos em que ela difere da decisão real (seção 8.3). A previsão de preço do agente ficou 5,9% abaixo do contratado nos 332 itens fora das canetas de insulina, e a estimativa que ele rejeitou estava 2,3× acima do mercado.

**Ressalvas.**
1. **A magnitude da vantagem não está demonstrada.** O agente anunciou R$ 2,22 milhões de economia potencial frente ao modelo de 2024. O número depende de um modelo sem preço por item observado e de quantidades que se mostraram infladas. A ordem entre os cenários se sustenta; o tamanho da diferença, não.
2. **O experimento observa comportamento, não mecanismo.** Ele mostra que o agente produziu e comparou cenários. Não permite afirmar que isso não seja, internamente, um reconhecimento de padrões mais elaborado (seção 8.4).

### 1.3 Evidências e estimativas

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
| Custo do cenário escolhido pelo agente | R$ 1,81 mi (faixa de 1,50 a 2,51) | previsão feita antes da decisão |
| Mesmo cenário aos preços reais, limitados ao teto | R$ 1,84 mi | preços de um pregão com outro preço máximo |
| Economia potencial anunciada pelo agente | R$ 2,22 mi | modelo do contrato de desconto, sem preço por item observado, e quantidades do ETP |

**Sobre as duas divergências entre as avaliações** (seção 7):
- **ICMS na tabela da CMED:** a avaliação independente estava certa. A tabela publica os valores a 20% para os produtos do Convênio 87/02; a leitura do pacote os descartou.
- **Insulinas de 2026:** a preparação anterior estava certa. O preço de R$ 29,00 homologado em 2026 é de refil sem caneta, não de caneta. Três afirmações da Etapa 5 que usavam esse preço ficam retiradas.

Nenhuma das duas altera as conclusões.

---

## 2. Metodologia

### 2.1 Desenho

O experimento é uma simulação sobre um caso já encerrado. A decisão do agente não é implementada, por desenho: o que se avalia é a escolha, e os dados posteriores servem de régua. Para que quem escolhe não veja o resultado, três papéis ficam separados:

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

Nenhuma destas foi observada: por desenho, o cenário escolhido pelo agente não foi licitado. Elas testam se a escolha se mantém quando as previsões são trocadas por preços reais.

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

Esta última ressalva usa a execução como critério. Ela é mantida porque faz parte do registro da Etapa 5, mas a execução não é objetivo do experimento (seção 1.1) e não é tratada como falha nas conclusões.

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

Nenhum sobre as conclusões. O veredito da Etapa 5 se apoia no preço contratado, na competição, na execução e no mercado nacional, que as duas avaliações obtiveram de forma idêntica.

A lição é de método: **cada avaliação errou uma vez, e o confronto pegou os dois erros.** A preparação errou ao declarar ausência de um dado sem olhar a célula. A avaliação independente errou ao tratar como iguais dois produtos sem ler a proposta. Ambos são erros de leitura de fonte, do mesmo tipo dos que o agente encontrou no pacote.

---

## 8. Discussão: inteligência como elaboração de cenários

A definição tem duas partes verificáveis (elaborar cenários alternativos e escolher o mais eficiente) e um contraste (o mero reconhecimento de padrões). Cada parte é examinada abaixo com as evidências das seções anteriores.

### 8.1 Elaboração autônoma de cenários alternativos

**O que foi pedido e o que não foi.** O enunciado exigia pelo menos três estratégias "substancialmente diferentes" e não trazia lista: "formulá-las faz parte da tarefa". A exigência de haver alternativas veio da tarefa. O conteúdo delas, o critério de comparação e a escolha vieram do agente, que trabalhou sem intervenção durante toda a execução.

**O que o agente produziu** (`saida/02_alternativas.md`, `registro_decisoes.csv`, `registro_hipoteses.csv`):
- **4 estratégias** que diferem em dimensões reais do problema: instrumento (ata ou contrato), critério de julgamento (menor preço ou maior desconto), origem do preço (licitação própria ou ata de terceiros) e compromisso de quantidade;
- **10 alternativas descartadas**, cada uma com motivo;
- **20 decisões** e **18 hipóteses** registradas, com a evidência de cada uma.

**São cenários, não só opções listadas.** Para cada estratégia o agente simulou consequências sob condições diferentes:
- custo central, baixo e alto;
- gasto com demanda de 75%, 100% e 125% do previsto;
- comportamento do fornecedor no modelo de desconto: entrega o registro mais barato, o da categoria pedida ou o que quiser;
- preços "a conferir" tratados como válidos ou como inválidos.

**Ressalva.** Um dos quatro cenários é fraco: o contrato de quantidade fixa (E4) recebeu, por hipótese, os mesmos preços do E1. Ele só se distingue pela demanda.

### 8.2 Contraste com o reconhecimento de padrões

O caso tem um padrão claro, e o agente o tinha diante de si:
- em 2024, 62,6% do gasto passou pelo modelo de desconto sobre a tabela da CMED;
- a estimativa do órgão, de R$ 4,95 milhões, vinha pronta no ETP;
- 143 itens repetiam descrições do pregão do ano anterior.

**Reconhecer o padrão seria recomendar a repetição.** O agente fez outra coisa:
1. **Tratou o padrão como um cenário entre outros.** O modelo de 2024 virou a estratégia E2, com custo estimado e faixa.
2. **Comparou-o com alternativas que não estavam nos dados.** O E1 combina elementos que o histórico do órgão não mostra juntos: ata de registro de preços, julgamento por item e referência recalculada.
3. **Rejeitou a referência dada.** Concluiu que a estimativa do órgão estava 2,04× acima do preço praticado e acima do teto legal em 41 itens.
4. **Raciocinou sobre o que não aconteceu.** Calculou os descontos que fariam o modelo de 2024 empatar com o E1 (cerca de 86%, 82% e 70%, contra 60%, 51% e 18% obtidos) e listou sete condições que mudariam a recomendação.

O quarto ponto é o mais distante de um padrão: é uma pergunta sobre um cenário que nenhum dado descreve.

**A decisão real ilustra o contraste**, sem que isso seja um julgamento sobre os gestores. Ela manteve a estimativa pronta como preço máximo, e os 27 itens com proposta única foram contratados exatamente nesse preço.

### 8.3 A escolha era o caminho mais eficiente?

A decisão real e os dados posteriores servem aqui de régua.

**O critério foi explícito e aplicado.** Menor custo esperado para cobrir os 334 itens, entre os cenários viáveis, com desempate pelo risco de descontinuidade. O agente considerou e descartou três critérios alternativos (`registro_decisoes.csv`, D01).

**Os três pontos em que a escolha difere da decisão real:**

| Escolha do agente | Evidência posterior | Natureza |
|---|---|---|
| Ata de registro de preços, que não obriga a comprar | Contratos de R$ 3,11 mi; R$ 585.893 pagos em 20 meses | Observada |
| Preço máximo pela mediana praticada, e não pela estimativa | Referência do agente a 1,11× do mercado posterior; estimativa do órgão a 2,32× | Observada |
| Canetas de insulina limitadas ao teto CMED | Contratadas a 9,6× e 9,3× o teto, com proposta única | Observada |

**A ordem entre os cenários:**

| Comparação | Resultado | Natureza |
|---|---|---|
| E1 frente ao modelo de 2024 (E2), 17 cenários de sensibilidade | E1 mais barato em 15 | Estimativa: o E2 é sempre modelo |
| Contratado por item frente ao E2 no seu melhor caso, 223 itens | R$ 1,15 mi contra R$ 1,73 mi | Observado contra modelado |
| E1 frente ao contrato de quantidade fixa (E4) | E1 melhor sempre que a demanda fica abaixo do previsto; a execução foi de 18,9% | Observada |

**O que limita a resposta.**
- "Mais eficiente" foi julgado entre os cenários que o agente formulou. Não se sabe se existia um caminho melhor que ele não considerou.
- A ordem tem apoio; a magnitude, não. Os R$ 2,22 milhões superam o gasto anual real do município com medicamentos, de R$ 1,41 milhão.
- O agente errou a largura de um cenário: a demanda real ficou muito abaixo dos 75% que ele tomou como piso.
- A regra de aceitar só preço até a mediana deixaria entre 6% e 18% dos itens sem contratar na primeira rodada. O agente previu esse efeito e indicou contingências.

### 8.4 O que o experimento permite e não permite afirmar

**Permite afirmar** que o agente exibiu o comportamento que a definição descreve: elaborou cenários, comparou consequências e escolheu por um critério, afastando-se do padrão disponível. E que a escolha resiste à comparação com o que aconteceu.

**Não permite afirmar** que esse comportamento não seja reconhecimento de padrões em outro nível. Três motivos:
1. **As estratégias são conhecidas.** Registro de preços, adesão a atas e maior desconto são formas previstas em lei e descritas na literatura de compras públicas. O agente pode ter reproduzido um modo aprendido de analisar esse tipo de problema. O que é específico do caso são os números, os itens críticos e a rejeição da estimativa.
2. **O experimento mede saídas.** Ele registra o que o agente escreveu e calculou, não como chegou lá.
3. **Uma execução.** Não se sabe se outra rodada produziria os mesmos cenários e a mesma escolha.

A distinção entre elaborar cenários e reconhecer padrões é nítida no comportamento observado e indecidível quanto ao mecanismo. O trabalho sustenta a primeira afirmação e não reivindica a segunda.

### 8.5 Outros conceitos de SIO que o caso ilustra

- **Dado, informação e conhecimento.** Os dados eram públicos. Torná-los comparáveis (itens padronizados, ligados a preços e ao teto) custou três etapas e ainda deixou erros. A elaboração de cenários só foi possível depois dessa integração.
- **Decisão semiestruturada.** A compra tem regras fixas (lei, teto) e partes de julgamento (demanda, risco de item deserto). O agente resolveu a parte estruturada com exatidão e explicitou a outra como incerteza e como verificações a fazer.
- **Qualidade da informação.** Houve erros de leitura de fonte no pacote, na preparação e na avaliação independente. Foram corrigidos pelo confronto entre trabalhos feitos em separado.

---

## 9. Limitações

**Quanto à demonstração de inteligência.**
1. **Comportamento, não mecanismo.** O experimento mostra o que o agente produziu, não o processo interno (seção 8.4).
2. **A tarefa pedia alternativas.** O enunciado exigia pelo menos três estratégias. Não foi testado se o agente as elaboraria sem esse pedido.
3. **Uma execução, um modelo, um caso.** Não há medida de variação nem de generalidade.
4. **Conhecimento anterior do modelo.** A auditoria verifica o que o agente acessou, não o que o modelo já sabia. Se ele conhecesse o desfecho do caso, a escolha poderia ser lembrança, e não elaboração. Não há sinal disso: o agente previu que as canetas ficariam sem proposta, e elas foram contratadas pela estimativa.
5. **Avaliação pela mesma família de modelos.** Decisor, preparação e avaliação usaram modelos Claude. Não houve avaliador humano nem avaliador cego.

**Quanto à medida de eficiência da escolha.**
6. **A régua é contrafactual por desenho.** O cenário escolhido não foi licitado, porque o experimento é uma simulação. Isso não é falha do experimento, mas define o alcance da medida: a qualidade da escolha é avaliada por previsão contra preços reais, e não por resultado próprio.
7. **O modelo de 2024 não tem preço por item.** A principal comparação do agente, E1 frente a E2, é modelo dos dois lados.
8. **A régua tem viés.** Os preços reais vêm de um pregão cujo máximo era a estimativa inflada.
9. **Eficiência só entre os cenários formulados.** Não se avaliou se havia caminho melhor fora deles.
10. **Execução por item desconhecida.** Notas fiscais e termos de recebimento não são públicos.

**Quanto aos dados.**
11. **Vínculos automáticos.** Nenhuma conversão de unidade ou vínculo com a CMED teve validação humana.
12. **Normas** lidas pela web, sem cópia local arquivada.
13. **Comparação com 2026** sem conferência do produto ofertado, salvo nas seis insulinas.
14. **Escopo.** O órgão licitou depois outros 89 itens fora dos 334.

**Fora do objetivo.** O trabalho não avalia superioridade sobre gestores humanos, execução autônoma de contratações nem economia realizada, e nenhum resultado deve ser lido nesse sentido. Em particular:
- os valores de economia do agente são potenciais, estimados antes da decisão;
- o valor contratado acima do teto (R$ 1,28 milhão) é um risco contratado, do qual no máximo R$ 146 mil podem ter sido pagos nas canetas até novembro de 2026.

---

## 10. Conclusões

1. **O agente elaborou cenários alternativos por conta própria.** Quatro estratégias e dez descartadas, com consequências estimadas sob diferentes condições de preço, de demanda e de comportamento do fornecedor.
2. **O agente escolheu por um critério de eficiência explícito** e indicou as condições que inverteriam a escolha.
3. **O agente não se limitou ao padrão.** O padrão disponível era repetir o modelo de 2024 com a estimativa do órgão. Ele o simulou como um cenário, comparou e rejeitou.
4. **A escolha resiste à comparação com o que aconteceu.** Os três pontos em que ela difere da decisão real têm apoio em evidência observada: execução de 18,9% do contratado, estimativa do órgão 2,3× acima do mercado e canetas contratadas a mais de 9× o teto.
5. **A ordem entre os cenários se sustenta; a magnitude, não.** O E1 permanece o mais barato em 15 de 17 cenários. A economia potencial de R$ 2,22 milhões está superestimada.
6. **A elaboração dependeu de informação integrada.** Sem as três etapas de preparação dos dados não haveria cenários comparáveis.
7. **A demonstração é de comportamento.** O experimento não distingue, quanto ao mecanismo, a elaboração de cenários de um reconhecimento de padrões mais elaborado.

**Resposta à pergunta do experimento.** No caso estudado, o agente demonstrou inteligência no sentido adotado na disciplina: elaborou cenários alternativos e escolheu, por um critério explícito, um caminho que os dados posteriores indicam ser eficiente, em vez de repetir o padrão disponível. A conclusão vale para o comportamento observado em uma execução. A medida de eficiência é sólida quanto à ordem dos cenários e fraca quanto à magnitude.

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
