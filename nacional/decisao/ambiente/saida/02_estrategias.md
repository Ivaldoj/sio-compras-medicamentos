# 02 — Estratégias formuladas: avaliadas e descartadas

Legenda: [OBS] observado, [CALC] calculado, [INF] inferido, [HIP] hipótese, [CP] conhecimento prévio válido em 29/01/2025.

## Pontos comuns a todas as estratégias avaliadas

- **Itens 1A (38) e AP007:** o MS (DLOG) continua comprando de forma centralizada, como manda a PRC GM/MS 2/2017, art. 49 [OBS: `restricoes.csv`]. Nos 39 itens, o custo estimado é o mesmo em todas as estratégias.
- **Táticas para os 1A** (não mudam o custo central):
  - SRP de 12 meses com entregas parceladas;
  - inexigibilidade ou negociação quando há fonte única;
  - aquisição de PDP por dispensa (Lei 14.133, art. 75, XII [CP]);
  - renovação antecipada dos 9 itens sem compra programática visível e das atas DLOG de 2022 (AP047, AP071, AP078, AP084, AP085).
- **Quantidade planejada:** é a dispensação projetada, não a demanda [HIP H01, H04–H06]. Ver `plano_por_apresentacao.csv`.
- **Onde as estratégias diferem:** nos **11 itens descentralizados**:
  - Grupo 1B: AP027 mepolizumabe, AP029/AP060 eltrombopague, AP034 omalizumabe, AP062 leuprorrelina;
  - Grupo 2: AP036 atorvastatina, AP050 dapagliflozina, AP052/AP061 mesalazina, AP054 azatioprina, AP070 calcitriol.

## E1 — Status quo federativo (linha de base)

- **Descrição:** cada uma das 27 SES compra por conta própria os itens 1B e 2 (pregão, SRP próprio ou adesão), com seu volume.
- **Base legal e federativa:**
  - PRC GM/MS 2/2017, art. 49;
  - Lei 14.133/2021;
  - competências preservadas.
- **Premissas:**
  - preço = mediana estadual em 24 meses (p25–p75) [HIP H17];
  - 27 processos por item.
- **Por que é a linha de base:** é o que ocorre sem nenhuma decisão nova de coordenação. É a referência natural de "custo evitável".

## E2 — Compra nacional compartilhada (SRP nacional com participação das SES) — **recomendada**

- **Descrição:**
  - o MS/DLOG faz a Intenção de Registro de Preços e gerencia uma ata nacional para os 11 itens 1B/2;
  - as 27 SES entram como **participantes**, declarando suas quantidades;
  - cada SES assina seu contrato e paga: com recurso próprio no Grupo 2, com recurso federal transferido + contrapartida no 1B;
  - o MS não compra nem paga esses itens.
- **Desenho de mitigação:**
  - cadastro de reserva;
  - para itens concorrenciais, permitir adjudicação a mais de um fornecedor por cota/lote quando o edital comportar;
  - para itens de fonte única (CMED com 1 laboratório: AP027, AP029, AP034, AP050, AP052, AP060, AP070), negociação nacional de preço abaixo do PMVG;
  - as SES mantêm os contratos vigentes até a ata nacional entrar em vigor.
- **Base legal:**
  - Lei 14.133/2021, arts. 82–86: SRP com órgão gerenciador e participantes;
  - Decreto 11.462/2023 (IRP);
  - pela Lei 14.133, art. 86, §8º, órgão federal não pode aderir a ata estadual, mas aqui o gerenciador é o MS e as SES participam, o que é permitido [OBS: `restricoes.csv`];
  - a §7º do art. 86 facilita adesões emergenciais de medicamentos a atas do MS [OBS].
- **Base federativa:**
  - a competência de adquirir e contratar continua estadual; o MS presta apoio técnico e gerencia a ata;
  - exige adesão voluntária das SES e pactuação na CIT [INF/CP: a CIT pactua a operação do CEAF].
- **Premissas:**
  - preço = preço E1 × efeito volume nacional, limitado ao maior volume já observado para o item [HIP H16];
  - 40–70% do volume do horizonte já passa pela ata nacional (4–8 meses de IRP + pregão) [HIP H13].

## E3 — Blocos regionais (consórcios interestaduais ou SRP regional com estado gerenciador)

- **Descrição:** cinco arranjos regionais (N, NE, CO, SE, S) compram os 11 itens, cada um com o volume da sua região.
- **Base legal:**
  - Lei 11.107/2005, consórcios públicos [CP];
  - Lei 14.133, art. 86.
- **Base federativa:** competência estadual preservada.
- **Limitação:** só parte das regiões tem consórcio interestadual em funcionamento (ex.: Consórcio Nordeste, criado em 2019 [CP]). Montar 5 estruturas no horizonte é difícil.
- **Premissas:**
  - preço = preço E1 × efeito volume regional (mediana das regiões);
  - 20–60% do volume do horizonte sob o arranjo [HIP H14].

## E4 — Federalização: reclassificar os itens 1B e 2 para o Grupo 1A

- **Descrição:** o MS passa a comprar e financiar todos os 50 itens.
- **Base:** exige alterar a PRC GM/MS 2/2017 com pactuação na CIT [OBS: `restricoes.csv`, competência e regulatória], além de transferir para a União o financiamento do Grupo 2.
- **Viabilidade:**
  - **orçamentária baixa**: a LOA 2025 não estava aprovada em 29/01/2025 [OBS: LEIA-ME §4];
  - **temporal baixa**: a transição normativa leva meses.
- **Premissas:**
  - preço igual ao de E2 em regime pleno;
  - 0–30% do volume do horizonte federalizado [HIP H15].

## Estratégias consideradas e descartadas

| Id | Estratégia | Motivo do descarte |
|---|---|---|
| X1 | **Descentralizar os 1A**: cada SES compraria tudo | Viola a PRC 2/2017, art. 49. E os dados mostram que o MS paga em mediana 0,29× o preço estadual [CALC]. Custo muito maior |
| X2 | **Adesão em massa ("carona")** às atas mais baratas já existentes, inclusive municipais | Limite de 50% por aderente e do dobro no total (art. 86, §§4º–5º) [OBS]. As atas existentes têm volume muito menor que a necessidade nacional. Exige vantagem demonstrada caso a caso. Serve como **contingência**, não como estratégia |
| X3 | **Importação direta ou Fundo Estratégico da OPAS** | Exige registro Anvisa do produto entregue (Lei 6.360/1976) [OBS]. O pacote não tem preços nem prazos dessa via. Seria um número sem fonte |
| X4 | **Compras municipais ou consórcios intermunicipais** | Municípios não têm competência no CEAF [OBS/INF]. Volumes pequenos significam preço maior (β<0) |
| X5 | **Estoque estratégico de 18–24 meses comprado de uma vez** | Imobiliza recursos sem orçamento 2025 aprovado, traz risco de vencimento e passa do horizonte. Fica só a faixa alta de quantidade (+10%) |
| X6 | **Comprar por demanda judicial ao PMVG** | Não é estratégia de abastecimento. O PMVG é teto, e as compras judiciais observadas (q < 10% da dispensação) ficam acima das programáticas [OBS: AP012 a R$ 25.181 contra R$ 3.209] |
| X7 | **Renegociar só os 1A, sem mexer nos 1B/2** | Os 1A já estão na DLOG a preços baixos. O espaço restante não é quantificável com o pacote. Entra como tática comum, não como estratégia distinta |
