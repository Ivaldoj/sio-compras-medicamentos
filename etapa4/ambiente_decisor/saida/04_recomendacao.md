# 04 — Recomendação

## 1. Estratégia recomendada

**E1: pregão eletrônico para registro de preços (SRP), com julgamento por item e critério de menor preço, valor de referência saneado e limitado ao teto CMED, ata de 12 meses e entregas parceladas sob demanda. As atas SRP já identificadas ficam como contingência (E3) para itens desertos ou fracassados.**

**Custo potencial estimado** (CALC: `trabalho/20_estrategias.txt`), na quantidade do ETP:
- central: **R$ 1.812.130**;
- faixa: **R$ 1.499.016 a R$ 2.508.722**;
- com demanda real de 75% a 125% do ETP: de R$ 1,36 mi a R$ 2,27 mi no cenário central.

São valores estimados na data de decisão. Não são resultado observado.

## 2. Justificativa

1. **Eficiência (critério D01).** O E1 tem o menor custo esperado entre as estratégias viáveis como via principal.
   - O E2, modelo de 2024, custa 2,2× mais no cenário central (R$ 4,04 mi). O E1 só perde no cruzamento extremo "E2 mais favorável × E1 mais desfavorável", e por R$ 0,21 mi.
   - O E4 é dominado pelo E1.
   - O E3 é R$ 0,10 mi mais barato no papel, mas não é executável como via principal (`03_comparacao.md`).
2. **Restrições.**
   - Ausência de armazém: resolvida pelas entregas parceladas.
   - Entrega na SMS e validade mínima: cláusulas do edital.
   - Registro Anvisa: exigido na proposta.
   - Teto CMED: aplicado tanto na referência quanto na aceitabilidade.
   - Itens fora da RENAME: tratados como os demais, item a item.
3. **Incerteza de demanda e de orçamento.** A ata não obriga a contratar (LLC, art. 83, CP), e a dotação é comprometida pedido a pedido. Isso é adequado quando consumo, estoque e saldo são desconhecidos (OBS).
4. **Referência saneada.** Substituir a estimativa do órgão pela mediana praticada limitada ao teto (D02, D08) corrige duas falhas:
   - 41 itens com estimativa acima do teto legal;
   - sobre-estimação mediana de 2,04×.

   Sem esse saneamento, um pregão com pouca competição poderia aceitar lances até R$ 3,56 mi (R1).
5. **Respaldo normativo da referência (CP).** O art. 23, §1º, I, da LLC aponta expressamente a mediana do banco de preços em saúde como parâmetro.

## 3. Como executar (medidas que fazem parte da recomendação)

| # | Medida | Por quê |
|---|---|---|
| 1 | **Antes do edital**, fazer pesquisa direta (art. 23, §1º, IV) para os **63 itens sem referência externa** (R$ 444 mil na estimativa do órgão; referência provisória de R$ 217 mil) e para os itens de referência fraca (194, 195) | A referência provisória é uma hipótese (H07) |
| 2 | Conferir manualmente os **25 itens "a conferir"** e validar por amostragem humana os vínculos CMED. Prioridade: os 51 itens cujo teto muda com vínculos COM ALERTA e os itens 151, 197 e 268 | O pacote não tem validação humana |
| 3 | Insulinas: confirmar com a SES-PB e o MS a cota municipal das insulinas humanas (NPH e Regular, frasco e caneta) e o atendimento das análogas pelo CEAF; registrar no SRP apenas a quantidade complementar; usar como referência das canetas o teto CMED (R$ 20,14 NPH/PF; R$ 15,80 Regular/PMVG-CAP) | Ver `05_itens_criticos.md` |
| 4 | No edital: critério de aceitabilidade "≤ valor de referência e ≤ teto CMED do registro ofertado (PF ou PMVG se CAP, alíquota da PB)"; declaração do registro Anvisa; validade ≥ 75% da vida útil ou > 365 dias; entrega na SMS com prazo curto | Restrições do pacote |
| 5 | Aplicar a LC 123/2006, art. 48, I: participação exclusiva de ME/EPP em itens de até R$ 80 mil (332 itens pela referência), motivando no ETP eventual exceção do art. 49 | Lei. Na sessão, acompanhar se a exclusividade eleva os preços |
| 6 | **Transição:** verificar se a ata ou o contrato do PE 12/2024 (resultado em 11/04/2024) continua vigente e com saldo, para cobrir o período até a nova ata. Se não estiver, usar compras pontuais dentro do limite legal de dispensa e solicitar remanejamentos à SES | Em 2024 houve meses sem empenho até o pregão sair (OBS) |
| 7 | Itens desertos ou fracassados: (a) adesão a ata da lista de contingência (`plano_por_item.csv`, 111 itens), cumprido o art. 86; (b) nova rodada com pesquisa atualizada. **Nunca** aceitar preço acima do teto | Contingência |
| 8 | Separar o valor de referência do saneamento, R$ 1,81 mi (faixa de R$ 1,50 a 2,51 mi), da reserva orçamentária de R$ 4,95 mi (H02). Reservar ao menos o limite alto da faixa | Saldo desconhecido |

## 4. O que faria a recomendação mudar

| Condição | Efeito |
|---|---|
| Descontos sobre a CMED em níveis de empate, oferecidos de forma verificável: ~86% em genéricos, ~82% em similares, ~70% em éticos | O E2 empataria em custo. A simplicidade operacional poderia então pesar a seu favor |
| Os preços praticados para Santa Luzia/PB ficarem sistematicamente acima do P75 nacional (por exemplo, por frete) **e** o fornecedor do E2 entregar sempre o registro mais barato | Cruzamento extremo: o E2 pode ficar até R$ 0,21 mi mais barato. Pouco provável, porque são duas condições independentes e desfavoráveis ao E1 |
| Confirmação de atas vigentes, com aceite do gerenciador e do fornecedor, para os itens de maior valor (pregabalina, risperidona solução, sinvastatina, dipirona, sertralina…) | Aderir a essas atas, como complemento do E1, captura parte dos ~R$ 0,10 mi do E3 |
| Existência de consórcio ou compra compartilhada regional com ata vigente | Avaliar a adesão. É a melhor via para o ciclo seguinte |
| MS/SES fornecendo as insulinas humanas | Retirar ou reduzir os itens 196, 197, 198 e 199 (−R$ 156 mil na referência E1) |
| Saldo de dotação abaixo de R$ 1,5 mi | Mantém o E1 (SRP permite priorizar pedidos), mas exige uma lista de itens essenciais |
| Deserto generalizado no pregão (por exemplo, mais de 20% dos itens) | Rever as referências (pesquisa direta) e usar o E3 de forma ampla |

## 5. Verificações necessárias antes de executar

1. Saldo das dotações listadas em `recursos.csv` e inventário físico do estoque, para ajustar as quantidades do ETP.
2. Dados de consumo (Hórus/BNAFAR ou registros de dispensação) para validar as quantidades. O ETP não tem consumo por item.
3. Vigência e saldo dos instrumentos do PE 12/2024 e do PE 01/2024.
4. Regulamento municipal de SRP e de pesquisa de preços, ou adoção dos regulamentos federais (LLC, art. 187).
5. Validação humana dos fatores de conversão CMED e dos itens 151, 197 e 268. Lista CMED vigente na data da sessão (o reajuste anual altera os tetos).
6. Condições do Convênio ICMS 87/02 por produto (§1º, I–II). Se não forem atendidas, o teto passa à coluna de 20%, que não está no pacote.
7. Cota de insulinas MS/SES e fluxo do CEAF.
8. Redação vigente do art. 86, §3º, da LLC, antes de aderir a atas de gerenciador municipal.
9. Pesquisa direta para os 63 itens sem referência e para os de referência fraca.
