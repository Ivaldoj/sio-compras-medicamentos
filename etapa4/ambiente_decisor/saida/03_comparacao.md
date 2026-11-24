# 03 — Comparação das estratégias

Fontes dos números:
- `trabalho/20_estrategias.py`: saídas `trabalho/20_estrategias.txt`, `custos_estrategias.csv`, `demanda.csv`, `sensibilidades.csv`.
- `trabalho/40_numeros_texto.py`: saída `trabalho/40_numeros_texto.txt`.
- Tabela-resumo: `saida/03_comparacao.csv`.

Todos os valores estão em R$ e foram calculados para a quantidade do ETP, salvo indicação contrária. São **custos potenciais**, estimados na data de decisão, e não custos observados.

## 1. Critério de eficiência (decisão D01)

**Critério:** o menor **custo esperado para cobrir integralmente** a necessidade (334 itens, 12 meses, quantidade do ETP), considerando apenas as estratégias que passam em dois filtros:
- **viabilidade jurídica:** Lei 14.133/2021 e teto CMED;
- **viabilidade operacional:** sem armazém próprio e com entrega na SMS.

Desempate: risco de descontinuidade do suprimento e flexibilidade orçamentária (saldo de dotação desconhecido).

**Justificativa.**
- O objetivo da organização é manter o suprimento contínuo dos 334 itens usando os recursos com eficiência. O "produto" (cobertura da necessidade) é o mesmo em todas as estratégias, então eficiência equivale a cobrir a mesma necessidade ao menor custo.
- Quando uma estratégia não cobre todos os itens sozinha (E2, E3), somo o custo do processo complementar. Assim a comparação é feita sempre sobre cobertura integral.
- Os riscos não foram monetizados, porque não há dado de probabilidade de deserto ou de desabastecimento (H04). Eles aparecem em separado, com nível qualitativo justificado, e são usados como critério de desempate e de veto.
- Também mostro o gasto sob demanda incerta (75% e 125% do ETP), porque é aí que SRP e contrato fixo se diferenciam.

## 2. Custos com faixa (CALC)

| Id | Estratégia | Central | Baixo | Alto | Gasto se demanda = 75% | Gasto se demanda = 125% | Cobertura própria |
|---|---|---:|---:|---:|---:|---:|---|
| R0 | Estimativa do órgão (referência, não é estratégia) | 4.952.438 | — | — | — | — | — |
| R1 | Estimativa do órgão limitada ao teto CMED (referência) | 3.556.151 | — | — | — | — | — |
| **E1** | **SRP por item, menor preço, referência saneada** | **1.812.130** | **1.499.016** | **2.508.722** | 1.359.098 | 2.265.163 | 334 itens |
| E2 | SRP por maior desconto sobre CMED (+ complementar) | 4.035.750 | 2.300.004 | 4.543.594 | 3.026.812 | 5.044.687 | 225 itens pelo desconto |
| E3 | Adesão a atas + E1 no restante | 1.711.564 | 1.457.405 | 2.262.119 | 1.283.673 | 2.139.455 | 111 itens por ata (26,2% do valor) |
| E4 | Contrato de quantidade fixa (preço unitário = E1) | 1.812.130 | 1.499.016 | 2.508.722 | **1.812.130** (paga o contratado) | 2.265.163 | 334 itens |

**Como as faixas foram construídas.**
- **E1.** Por item: P25 e P75 dos preços praticados compatíveis, limitados ao teto. Nas referências pontuais (PNCP ou preço próprio), aplica-se a dispersão empírica (×0,846 a ×1,25), e o limite alto vai até a estimativa do órgão deflacionada. Nos 63 itens sem referência externa, a faixa vai de estimativa/2,568 até a própria estimativa do órgão (H05–H08).
- **E2.** Baixo: o fornecedor entrega o registro de menor preço. Central: a SMS pede a categoria mais barata (genérico, depois similar, depois ético), na mediana dos registros. Alto: o fornecedor escolhe livremente (mediana de todos os registros). No extremo em que o fornecedor sempre entrega o registro de maior preço, o E2 chega a **R$ 10,29 mi**.
- **E3.** Faixa do E1 nos itens sem ata.
- **E4.** Mesmos preços do E1, mas com quantidade comprometida.

## 3. Sensibilidades (CALC, `trabalho/sensibilidades.csv`)

| Cenário | E1 central | E2 central | E2 − E1 |
|---|---:|---:|---:|
| Base | 1.812.130 | 4.035.750 | 2.223.619 |
| Preços "a conferir" tratados como compatíveis | 1.817.889 | 4.049.020 | 2.231.131 |
| Preços "a conferir" incompatíveis (= base: a central nunca os usa) | 1.812.130 | 4.035.750 | 2.223.619 |
| Mediana só de compradores municipais | 1.806.267 | 4.030.624 | 2.224.357 |
| E2: fornecedor entrega o registro mais barato | 1.812.130 | 2.300.004 | 487.874 |
| E2: fornecedor escolhe livremente | 1.812.130 | 4.543.594 | 2.731.464 |
| Canetas 196/199 trocadas por frasco (mesmo número de UI; decisão clínica) | 1.729.626 | — | — |
| Referência = estimativa do órgão limitada ao teto (pior caso sem saneamento) | 3.556.151 | — | — |
| Correção monetária de +5% nos preços históricos | ≈ 1.902.737 | — | — |

**Ponto de virada E1 × E2 (CALC).**
- Para empatar com o E1 nos 225 itens cobertos, os preços do E2 teriam de ser 0,36 do que o modelo de 2024 produz. Isso equivale a descontos de aproximadamente **85,6% em genéricos, 82,4% em similares e 70,5% em éticos**, contra 60,11%, 51,01% e 18,01% obtidos em 2024.
- Só no cruzamento extremo (E2 no cenário mais favorável e E1 no mais desfavorável) o E2 sai mais barato, por R$ 208,7 mil.
- O peso está concentrado em genéricos de alto volume. Os 10 itens de maior diferença (pregabalina, escitalopram, sertralina, risperidona, colecalciferol, carvedilol, alendronato etc.) respondem por 39,7% da diferença (`trabalho/21_e2_diagnostico.txt`).
- O resultado se mantém ao excluir 13 itens com teto mais de 10 vezes a mediana, possíveis erros de conversão residuais: E2 − E1 = R$ 1,87 mi.

## 4. Riscos e viabilidade

| Dimensão | E1 | E2 | E3 | E4 |
|---|---|---|---|---|
| **Jurídica** | **Alta.** É a via típica, e o art. 23 cita o BPS. Risco: impugnação de referência em itens sem pesquisa sólida. Mitigação: pesquisa direta | **Média-baixa.** A referência é um teto regulatório, e o preço de cada item depende do registro entregue, o que dificulta provar a compatibilidade com o mercado. Precedente local em 2024 | **Média.** Depende do aceite do gerenciador e do fornecedor, dos limites de 50% por item e de 2× no total e da redação do art. 86, §3º, para atas municipais | **Média.** Quantidade fixa sem dado de consumo nem de estoque fragiliza a motivação |
| **Operacional** | Média-alta. Compatível com a falta de armazém (entregas parceladas). Muitos fornecedores: em 2024 foram 9 só no PE 01/2024. Gestão de 334 itens | Alta. 1 fornecedor e 1 processo, mas ainda precisa de processo complementar para 109 itens | **Baixa como via principal.** Dezenas de adesões a atas de outras UFs, com entrega remota de pequenos volumes em Santa Luzia/PB | **Baixa.** Entrega integral é inviável sem armazém; entrega escalonada com quantidade fixa traz risco de vencimento |
| **Orçamentária** | Alta. A ata não obriga a contratar (art. 83) e a dotação é exigida por pedido | Alta (SRP), mas com custo esperado 2,2× o do E1 | Alta | **Baixa.** Exige empenho do total na assinatura, com saldo desconhecido |
| **Mercado** | Média. Pode haver deserto onde a referência está no teto (canetas 196 e 199: as compras de canetas observadas em 2024 ficaram em geral acima de R$ 20,14) e em itens de referência fraca | Alta adesão (precedente de 2024), mas concentração em 1 fornecedor | Baixa-média. Aceite incerto; a amostra do PNCP não é censo | Média. Lotes reduzem a competição |
| **Continuidade e prazo** | Médio. O pregão leva semanas, com publicação mínima de 8 dias úteis (art. 55, I, a), e precisa de ponte (ver `04_recomendacao.md`) | Médio. Rápido, mas a falha de 1 fornecedor interrompe tudo | Alto se usada como via principal | Médio |
| **Faixa de custo** | 1,50–2,51 mi | 2,30–4,54 mi (extremo 10,29) | 1,46–2,26 mi (no papel) | 1,50–2,51 mi, mais desperdício se a demanda ficar abaixo do ETP |

## 5. Ordenação pelo critério

1. **E1.** Tem o menor custo esperado entre as estratégias viáveis como via principal, viabilidade alta e flexibilidade orçamentária.
2. **E3 como complemento do E1, não como via principal.** O custo no papel é R$ 100,6 mil menor (5,5%), metade disso concentrada em 10 itens. Mas a viabilidade operacional e de mercado é baixa para 111 adesões, e o ganho fica dentro da faixa de incerteza do E1. Por isso entra como **contingência** para itens desertos ou fracassados e para adesões pontuais de alto valor, depois de verificado o aceite.
3. **E4.** Os preços seriam no máximo iguais aos do E1. O E4 é dominado por ele: tem o mesmo custo com demanda de 100% e custo maior com demanda de 75% (R$ 1,81 mi contra R$ 1,36 mi), além de inviabilidade operacional (armazenagem) e orçamentária (empenho do total).
4. **E2.** O custo central é 2,2× o do E1. O E2 só é competitivo no cenário extremo descrito acima ou se os descontos subirem para os níveis de empate. A simplicidade operacional e a adesão de mercado não compensam uma diferença potencial de R$ 0,8 a 2,0 mi (cenários na mesma direção).
