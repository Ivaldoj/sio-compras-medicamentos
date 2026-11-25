# Proposta de reformulação do experimento: planejamento de compras públicas de medicamentos em escala nacional

**Status: proposta para aprovação. Nada foi executado.** O experimento anterior, o caso Santa Luzia/PB, está preservado sem alterações na branch `experimento-santa-luzia` (e em `main`, até vocês decidirem qual linha segue como principal).

**Regras desta proposta:**
- Não restringe o problema a município, estado ou organização específica.
- Não antecipa cenários. Cabe ao agente decisor formulá-los; o papel de vocês é coordenar o experimento, não participar da decisão.

---

## 1. O problema organizacional em escala nacional

**Problema proposto.** Na data de decisão, planejar para os 12 meses seguintes a **aquisição pública, em todo o território nacional, de uma cesta definida de medicamentos essenciais do SUS**. O plano deve atender à demanda pública estimada com o **menor custo total para o SUS** e respeitar as restrições legais, regulatórias, federativas, orçamentárias, logísticas e de mercado.

O objeto da decisão é a **forma de organizar essas compras**, e quem formula as alternativas é o agente.

| Elemento | Proposta | Observação |
|---|---|---|
| **Quem decide** | A coordenação nacional da aquisição pública de medicamentos do SUS, entendida como o sistema das três esferas que compram (União, estados e municípios). Não é um órgão específico. | Precisa de aprovação: o papel não é delimitado a uma organização. Atribuí-lo a um órgão concreto, como o Ministério da Saúde, só com autorização expressa de vocês. |
| **Data de decisão** | **29/01/2025**, a mesma do experimento anterior | Reaproveita toda a classificação temporal já feita (disponível, posterior, indeterminado). |
| **Horizonte** | 12 meses (fev/2025 a jan/2026) | Os dados posteriores ao corte (2025–2026) servem para avaliar. |
| **Escopo de produtos** | Cesta de medicamentos da RENAME, escolhida por critérios objetivos aplicados aos dados nacionais anteriores ao corte. Exemplo: os itens de maior gasto público observado em 2023–2024 que tenham padronização confiável (CATMAT, apresentação, CMED). | É um recorte de **produto**, não de território. O tamanho da cesta (algo entre 30 e 60 apresentações) fica para vocês decidirem. Ele controla a viabilidade da análise. |
| **Objetivo** | Atender à demanda nacional da cesta durante o horizonte, com eficiência no uso dos recursos e continuidade do abastecimento | Equifinalidade: vários arranjos podem atingir o objetivo, com custos e riscos diferentes. |
| **Restrições** | Lei 14.133/2021 e Decreto 11.462/2023 (SRP, adesão, dispensa); CMED (PF/PMVG, CAP, ICMS da UF de destino, Convênio 87/02); LC 123/2006; repartição de responsabilidades por componente da Assistência Farmacêutica (PRC nº 2 e nº 6/2017; RENAME); registro na Anvisa e validade; capacidade de fornecimento | São fatos e normas, não alternativas. |

**Por que é um problema organizacional real**
- A compra pública de medicamentos é feita por milhares de compradores, em diversos instrumentos e com preços muito dispersos para o mesmo item. Só os dados já coletados mostram 747 compradores no BPS e 1.365 unidades compradoras no Compras.gov.br antes do corte.
- Decidir como organizar essas compras tem consequências mensuráveis: custo total, abastecimento, compromisso orçamentário e concentração de fornecedores.

## 2. O que já existe e pode ser reaproveitado

| Ativo | Situação para o escopo nacional |
|---|---|
| **BPS 2020–2026** (arquivos brutos nacionais) | **Reaproveitável integralmente.** Antes do corte: 225.518 registros, 3.388 CATMATs, 23 UFs e 747 compradores (93% municipais, 0,04% federais). Depois do corte, para avaliação: 87.960 registros. |
| **CMED** jan/2025 (lista completa) e nov/2026 | **Reaproveitável integralmente** (teto por apresentação e alíquota). |
| **Medicamentos Transparentes** 2025–2026 (27 UFs) | Reaproveitável como índice nacional para a avaliação ex post. Limite já conhecido: corta em 10 itens por contratação, então o PNCP completa. |
| **PNCP:** cliente da API, coleta de itens, resultados e documentos | **Código reaproveitável.** A amostra coletada (95 contratações) foi dirigida a Santa Luzia e não serve como base nacional. |
| **Compras.gov.br:** coletor e cache | **Código reaproveitável.** O cache cobre só 401 CATMATs, os dos itens de Santa Luzia. É preciso coletar os da cesta. |
| **Regras de padronização** (`padroniza.py`, 47 autotestes, defeitos já corrigidos) | **Reaproveitável.** Inclui as lições de insulina: tipo, pré-mistura e caneta × refil. |
| **Regras de integridade temporal e separação dos dados de avaliação** (varredura de datas, disjunção, quarentena) | **Reaproveitável** como método e como testes. |
| **Protocolo de decisão isolada** (ambiente isolado, enunciado sem cenários, transcrição integral, `scripts/30_auditoria_etapa4.py`) | **Reaproveitável.** |
| **Ferramentas de avaliação** (reprodução, verificação de cálculos, sensibilidade, economia em três níveis: scripts 32 e 33) | **Reaproveitáveis como padrão.** As métricas precisam ser redefinidas para a escala nacional. |
| **Normas já verificadas na fonte** (Lei 14.770/2023, Decreto 12.343/2024, NTs do MS sobre insulinas, Convênio 87/02) | **Reaproveitáveis.** |
| **Caso Santa Luzia** (branch preservada) | Opcional: pode servir de piloto e de validação do método. |

**Não se reaproveita** o que foi construído em torno dos 334 itens de Santa Luzia:
- os itens e os vínculos item × CATMAT × CMED;
- as regras de conversão por item;
- a amostra PNCP;
- a camada organizacional (TCE-PB, recursos, ICMS da PB);
- os dados reservados do PE 04/2025;
- as conclusões dos docs 07 a 20.

## 3. Informações adicionais necessárias

Para cada fonte, é preciso comprovar a **disponibilidade em 29/01/2025** pelas mesmas regras do experimento anterior.

| Necessidade | Fonte candidata (oficial) | Para quê |
|---|---|---|
| **Demanda nacional por item** | DATASUS/SIA-SUS (APAC de medicamentos do Componente Especializado); dispensações do Farmácia Popular (dados abertos do MS); quantidades das compras centralizadas do MS (TRs e atas no PNCP); quantidades compradas no BPS, Compras.gov.br e PNCP | Estimar a demanda de 12 meses com faixa de incerteza. **É a principal lacuna** (ver §6). |
| **Cobertura dos dados de compra** | IBGE: população de todos os municípios (estimativa de 2024) | Medir que parte do país os compradores observados representam e corrigir a subcobertura do BPS. |
| **Compras federais** | PNCP: contratações, atas e contratos de compradores federais para os itens da cesta, 2023–2024 | O BPS quase não tem compras federais (88 registros). |
| **Recursos** | LOA 2025 (SIOP): dotações federais da Assistência Farmacêutica; FNS: repasses fundo a fundo de 2024; contrapartidas mínimas por habitante (PRC nº 6/2017) | Restrição orçamentária nacional e por esfera. |
| **Responsabilidades** | RENAME vigente na data de corte (edição a confirmar), com o componente de cada item; PRC nº 2/2017, Anexo XXVIII (aquisição centralizada) | Restrição federativa: quem pode ou deve comprar o quê. |
| **Tributação** | Alíquotas internas de ICMS por UF em 2025 | Teto CMED por UF de destino. Hoje só existe a regra da PB. |
| **Oferta** | Anvisa: registros ativos por substância (`DADOS_ABERTOS_MEDICAMENTOS`); notificações de descontinuação ou desabastecimento anteriores ao corte; fornecedores por item (já nos dados de compra) | Risco de mercado e concentração. |
| **Preços da cesta** | Compras.gov.br (coletor existente) para os CATMATs ainda não coletados | Completar a cobertura de preços. |
| **Logística e armazenagem** | Provavelmente sem fonte pública | Ficam como hipóteses explícitas do agente, sem preencher com dados inventados. |

## 4. Como a IA vai elaborar os cenários de forma autônoma

Mantém o protocolo da Etapa 4, que funcionou: isolamento auditado, transcrição integral, nenhuma intervenção.

1. **Pacote nacional isolado** (`decision_input_nacional/`), com documentação e consulta SQL:
   - cesta;
   - demanda estimada com faixas;
   - preços praticados nacionais;
   - teto CMED por UF;
   - recursos;
   - restrições;
   - oferta.
2. **Enunciado neutro**, com problema, objetivo, restrições e recursos:
   - **nenhum cenário, exemplo ou taxonomia de alternativas**;
   - antes da execução, uma revisão confere o enunciado contra uma lista de termos que sugeririam cenários.
3. **O agente formula** pelo menos três cenários substancialmente diferentes, à sua escolha, mais os que descartar e o motivo. Para cada um:
   - define o critério de eficiência;
   - estima custo, cobertura, risco e viabilidade com faixas;
   - recomenda um cenário e diz o que mudaria a recomendação.
4. **Exigências mantidas:**
   - rastreabilidade (observado, calculado, inferido, hipótese, conhecimento prévio);
   - separação entre economia potencial e efetiva;
   - proibição de usar conhecimento posterior ao corte e de acessar a internet.
5. **Novidade proposta:** **várias execuções independentes** (por exemplo, três) com o mesmo enunciado, para medir se os cenários e a recomendação são estáveis ou dependem da execução. Vocês decidem o modelo do agente decisor.

## 5. Como medir e avaliar a eficiência da decisão

**Lição do experimento anterior:** as regras de avaliação ficaram para depois da decisão. Aqui, o **protocolo de avaliação será pré-registrado (hash) antes de o agente decidir**.

| Dimensão | Métrica | Natureza |
|---|---|---|
| Custo | Custo total esperado para atender à demanda da cesta em 12 meses, com faixa | Projetado pelo agente (contrafactual) |
| Linha de base | O que o sistema real pagou em 2025 pela cesta, segundo BPS, Compras.gov.br, PNCP e Medicamentos Transparentes depois do corte, corrigido pela cobertura | Observado (contratado ou praticado), com extrapolação declarada |
| Precisão | Preços e quantidades projetados pelo agente × observados em 2025, por item e tipo de comprador | Observado × projetado |
| Abastecimento | Cobertura da demanda; dependência de poucos fornecedores; itens com risco de deserto | Projetado e confrontado com eventos observados (desabastecimento, licitações desertas) |
| Conformidade | Teto CMED por UF, regras legais e responsabilidades federativas | Verificável por regra |
| Viabilidade | Jurídica, operacional, orçamentária e de mercado | Evidências ex ante e ex post |
| Robustez | Sensibilidade da recomendação (demanda, preço, cobertura, teto) e estabilidade entre execuções | Calculada |
| Economia | **Projetada** (agente × linha de base) separada de **contratada** e **realizada** (só observáveis para o que de fato aconteceu) | Nunca somadas |

**Avaliador:** um agente novo e independente (modelo e esforço a definir), num ambiente com:
- o protocolo;
- os resultados congelados;
- os dados reservados;
- as evidências primárias;
- **nenhum relatório interpretativo anterior.**

## 6. Etapas a refazer

| Etapa | Ação |
|---|---|
| 1. Auditoria das fontes | **Não refazer.** Complementar com as fontes do §3 (uma "Etapa 1-B"), respondendo a uma pergunta: há dado anterior ao corte suficiente para estimar a demanda nacional da cesta? |
| 2. Definição do caso | **Refazer** como definição do problema nacional: unidade de decisão, cesta, horizonte, objetivo, restrições, lacunas e viabilidade. Gera documentos novos; os docs 07–11 ficam na branch preservada. |
| 3. Preparação dos dados | **Refazer a camada do problema** (cesta, demanda, recursos, restrições, ICMS por UF, oferta) e a padronização por CATMAT/apresentação. **Reaproveitar** o mercado nacional (BPS, CMED, Medicamentos Transparentes), as regras e os testes. Coletar Compras.gov.br e PNCP para a cesta. |
| Pré-Etapa 4 | Reaproveitar as correções de regra. A validação humana das conversões continua pendente: propõe-se uma amostra validada por pessoa antes da Etapa 4. |
| 4. Decisão | **Refazer**, com novo enunciado e execuções independentes. |
| 5. Avaliação | **Refazer**, com protocolo pré-registrado antes da Etapa 4 e avaliador independente. |

## 7. Riscos principais

- **Demanda nacional.** É o elo mais fraco. Se a Etapa 1-B mostrar que não há dado suficiente antes do corte, a demanda vira faixa ampla com hipótese explícita, ou a cesta é restringida a itens com dado de dispensação (por exemplo, do Componente Especializado). Essa escolha seria de vocês.
- **Subcobertura das compras observadas.** Os 747 compradores do BPS não são o país inteiro. A linha de base observada precisa de correção declarada.
- **Escala.** Sem uma cesta limitada, o problema fica grande demais para o agente analisar com rastreabilidade.
- **Vazamento pela formulação.** A forma de descrever o problema pode sugerir cenários. Por isso a revisão do enunciado antes de rodar.
- **Avaliador e organizadores não cegos.** A avaliação independente mitiga isso, mas não elimina.

## 8. Decisões que dependem de vocês

1. **Quem decide:** aprovar que seja a coordenação nacional das três esferas, sem órgão específico.
2. **Data de corte:** manter **29/01/2025**, o que maximiza o reaproveitamento, ou outra.
3. **Cesta:** critério e tamanho, e se inclui itens de aquisição já centralizada.
4. **Execuções do agente decisor:** número e modelo.
5. **Caso Santa Luzia:** usar como piloto de validação ou só arquivar.
6. **Branch principal:** se `reformulacao-nacional` assume o trabalho principal.

Depois da aprovação, a ordem de execução seria:
1. Etapa 1-B (fontes adicionais e teste de suficiência da demanda);
2. definição do problema nacional;
3. pacote nacional;
4. protocolo de avaliação pré-registrado;
5. Etapa 4 (decisão);
6. Etapa 5 (avaliação independente).
