# Resumo executivo: planejamento nacional de compras CEAF (cesta de 50 apresentações), fev/2025 a jan/2026

Data de decisão: 29/01/2025. Coordenação nacional simulada das três esferas, com abrangência nas 27 UFs.

**Todos os valores são valor estimado de contratação** (preço homologado projetado × quantidade). Não são pagamento nem orçamento.

## Recomendação

**E2: compra nacional compartilhada.**

- **1B e 2 (11 itens):** o Ministério da Saúde gerencia um Sistema de Registro de Preços nacional, com Intenção de Registro de Preços. As 27 SES participam, cada uma contrata e paga.
- **1A (38 itens) e imunoglobulina:** continuam na compra centralizada do MS (DLOG).

As competências da PRC GM/MS 2/2017, art. 49, ficam preservadas. A estratégia não depende da LOA 2025 nem de mudar normas.

## Custo estimado (p50, faixa p05–p95)

| | Status quo (E1) | **Recomendada (E2)** |
|---|---|---|
| Cesta inteira | R$ 6,48 bi (5,93–7,18) | **R$ 6,25 bi (5,73–6,93)** |
| 39 itens centralizados (União) | R$ 5,28 bi | R$ 5,28 bi |
| 11 itens 1B/2 (SES) | R$ 1,20 bi (1,07–1,35) | **R$ 0,98 bi (0,86–1,12)** |

[CALC: `trabalho/03_estrategias.py` → `saida/03_comparacao.csv`]

As alternativas avaliadas, com o custo total p50:

- E3, blocos regionais: R$ 6,36 bi;
- E4, federalizar 1B/2: R$ 6,42 bi; **inviável no horizonte**.

## Economia potencial

- **R$ 221 milhões (159–298) no horizonte de 12 meses**, 18% do gasto com os 11 itens descentralizados. Em regime pleno, depois da transição, chega a R$ 405 mi/ano (337–483). Esse é um valor de referência e não se soma ao anterior.
- **Referência:** status quo E1, ou seja, o que as SES pagam comprando separadamente. É o preço mediano (p25–p75) das compras estaduais homologadas nos 24 meses anteriores ao corte (Compras.gov), aplicado à mesma quantidade planejada. É o contrafactual real e está na mesma categoria de valor. O teto CMED não serve de referência porque é limite legal, não preço.
- **De onde vem a economia:** efeito volume-preço medido nos dados.
  - β ≈ −0,08 (IC90 −0,12 a −0,07): decuplicar o volume reduz o preço em ~17%.
  - Onde o MS já compra nacionalmente, paga em mediana **0,29×** o preço estadual. Esse valor fica só como limite otimista e não entra na estimativa.
- **Concentração:** seis itens (omalizumabe, eltrombopague 50 e 25 mg, mepolizumabe, dapagliflozina, mesalazina 500 mg) somam ~85% da economia.
- **Economia efetiva:** não é observável em 29/01/2025. Deve ser medida depois do pagamento, pela fórmula Σ(preço de referência − preço pago) × quantidade paga, com controle do reajuste CMED e das SES não participantes. Ver `05_economia.md`.

## Principais riscos e incertezas

1. **O efeito volume pode não se transferir.** Se β≈0, a economia é zero. E2 não fica mais cara que E1, mas perde a vantagem.
2. **Falha ou atraso do certame nacional** afeta o país inteiro.
   - A economia só se anula com probabilidade de fracasso acima de ~41%.
   - Mitigação: cadastro de reserva, cotas e contratos estaduais como ponte; adesão emergencial à ata do MS (art. 86, §7º) ou SRP regional (E3) como contingência.
3. **Transição:** a ata nacional deve vigorar 4–8 meses depois do início. Isso explica a diferença entre a economia no horizonte e em regime pleno.
4. **Adesão das SES:** é voluntária e exige pactuação na CIT.
5. **Fornecedor único:** 7 dos 11 itens descentralizados têm um só laboratório na CMED. O ganho depende de negociação, e a capacidade de fornecimento não é conhecida.
6. **Qualidade dos dados:**
   - a dispensação atendida não é demanda total: estoques e demanda reprimida são desconhecidos;
   - o grupo de financiamento foi atribuído por texto: AP007 aparece como 1B, mas é comprado pelo MS;
   - há vínculos CATMAT ambíguos (AP012) e 6 itens com divergência entre BPS e Compras.gov;
   - 9 itens 1A não têm compra programática do MS visível na base.
7. **Lacunas:** LOA 2025, atas vigentes, ICMS por UF e preços futuros (reajuste de 0–5% por hipótese).

## Antes de executar

- Validar os grupos de financiamento na RENAME 2024, Anexo III.
- Conferir os vínculos CATMAT marcados.
- Levantar atas, contratos e estoques das SES.
- Fazer consulta de mercado sobre capacidade e registro Anvisa.
- Obter parecer jurídico e pactuar na CIT a Intenção de Registro de Preços nacional.
- Aplicar o teto CMED vigente com o ICMS da UF de destino.

Detalhes em `04_recomendacao.md`.
