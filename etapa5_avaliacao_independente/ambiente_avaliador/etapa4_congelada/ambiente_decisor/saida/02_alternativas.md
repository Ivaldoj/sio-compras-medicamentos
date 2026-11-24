# 02 — Estratégias formuladas (inclusive as descartadas)

As bases legais citadas são **conhecimento prévio (CP)** vigente em 29/01/2025: Lei 14.133/2021 (LLC), LC 123/2006, Lei 10.742/2003 (CMED) e Súmula TCU 247. Cada uma deve ser conferida no texto consolidado antes da execução. Onde tenho dúvida sobre a redação vigente, digo isso. As hipóteses (H..) estão em `registro_hipoteses.csv`.

---

## E1 — Pregão eletrônico para registro de preços, menor preço por item, com referência saneada (RECOMENDADA)

**Descrição.**
- Um pregão eletrônico SRP com os 334 itens, cada um julgado separadamente, e ata de 12 meses.
- Valor de referência por item: mediana dos preços praticados compatíveis (BPS e Compras.gov.br, 24 meses), **limitada ao teto CMED** aplicável (PF; PMVG para produtos com CAP; alíquota de ICMS da PB).
- Itens sem referência externa (63) passam por pesquisa direta antes do edital.
- Critério de aceitabilidade: preço ≤ referência e ≤ teto CMED do registro ofertado. O licitante declara o registro Anvisa.
- Entregas parceladas sob demanda no endereço da SMS. Validade mínima na entrega de 75% da vida útil ou mais de 365 dias.
- Itens de valor até R$ 80 mil são exclusivos de ME/EPP, salvo exceção motivada.
- Insulinas em itens próprios, com o tratamento descrito em `05_itens_criticos.md`.
- As atas SRP identificadas no PNCP ficam como contingência para itens desertos ou fracassados (ver E3).

**Base legal ou procedimental (CP).**
- LLC: art. 6º, XLV (SRP); art. 28, I (pregão); art. 33, I (menor preço); art. 40 (planejamento de compras, parcelamento, SRP quando pertinente); arts. 82–86 (SRP); art. 83 (a ata não obriga a Administração a contratar); art. 84 (vigência de 1 ano, prorrogável por igual período se o preço continuar vantajoso).
- Art. 23, §1º, I: mediana do item no painel de preços ou no **banco de preços em saúde**. Art. 23, §1º, IV: pesquisa direta com fornecedores.
- Súmula TCU 247 (adjudicação por item em objeto divisível).
- LC 123/2006, arts. 47–49.
- Lei 10.742/2003 e normas da CMED: PF é o teto em compras públicas; PMVG é teto obrigatório para produtos com CAP.

**Premissas.** H05 (o preço contratado se aproxima da mediana praticada, com faixa P25–P75), H06, H07, H08, H12–H16. O município pode aplicar regulamentos federais de SRP e de pesquisa de preços (LLC, art. 187) ou ter regulamento próprio, a verificar.

---

## E2 — Pregão eletrônico SRP por maior desconto sobre a tabela CMED (modelo do PE 12/2024)

**Descrição.** Repetir o modelo de 2024: três itens (medicamentos éticos, genéricos e similares), julgados pelo maior desconto percentual sobre a tabela CMED. A SMS pede o medicamento e o fornecedor fatura o preço CMED do registro entregue, menos o desconto da categoria. Em 2024, os descontos foram 18,01%, 60,11% e 51,01%, com 1 fornecedor e R$ 1,22 mi empenhados (OBS: `historico_proprio`, `execucao_2024_licitacao`).

**Base legal (CP).** LLC, art. 33, II, e art. 34 (maior desconto); arts. 82–86 (SRP).

**Premissas.** H09: desconto sobre o PF na alíquota aplicável, limitado ao teto (PMVG se houver CAP). Os descontos de 2024 se repetem. Na central, a SMS pede a categoria mais barata disponível. Itens sem teto CMED utilizável (108; o item 268 é tratado à parte, com teto suspeito) não podem ser precificados pelo desconto e precisam de **processo complementar**, cujo custo é estimado como no E1.

**Problemas estruturais (INF).**
- A tabela CMED é um **limite regulatório**, não preço de mercado. Para genéricos comuns, o PF fica muito acima do praticado: a mediana da razão entre o menor teto do item e sua mediana praticada é 2,88, em 220 itens (CALC, `trabalho/11_inspeciona_ref.txt`).
- O preço final depende do registro que o fornecedor decide entregar.
- O preço de cada item não é conhecido na licitação, o que dificulta demonstrar a compatibilidade com o mercado exigida pelo art. 23.

---

## E3 — Adesão a atas de registro de preços de outros órgãos ("carona"), com licitação para o restante

**Descrição.** Aderir às atas SRP homologadas no PNCP desde 29/01/2024 cuja metade da quantidade registrada cubra a necessidade do município e cujo preço não supere o teto. Os itens sem ata entram em um pregão E1.

**Base legal (CP).**
- LLC, art. 86, §2º: justificativa, demonstração de vantagem e aceite do gerenciador e do fornecedor.
- §4º: limite de 50% por item para cada aderente. §5º: limite total de duas vezes.
- **Ressalva:** a adesão de município a ata de **gerenciador municipal** depende da redação vigente do art. 86, §3º. Pelo que lembro, ela foi alterada pela Lei 14.770/2023. Confirmar no texto consolidado antes de usar.

**Premissas.** H10: as atas estão vigentes, mas o aceite do gerenciador e do fornecedor **não é observável**. Resultado do cálculo: 111 itens, que representam 26,2% do valor do E1. A maioria das atas é de municípios de GO, SP, BA, PR e MG (CALC, `trabalho/20_estrategias.txt`).

---

## E4 — Pregão (sem SRP) com contrato de quantidade fixa e entrega integral ou escalonada, por lotes

**Descrição.** Licitar e contratar de uma vez a quantidade do ETP, em lotes por classe terapêutica, com empenho do valor total e entrega integral ou em poucas parcelas programadas.

**Base legal (CP).** LLC, arts. 28, 33 e 40. Art. 125: acréscimo de até 25%.

**Premissas.** H11: preço unitário igual ao do E1. É uma premissa otimista para o E4, porque lotes reduzem a competição. A quantidade fica comprometida, qualquer que seja a demanda real.

---

## Estratégias consideradas e descartadas

| Id | Estratégia | Motivo do descarte | Classe |
|---|---|---|---|
| X1 | **Dispensa por valor** (LLC, art. 75, II) para toda ou parte da necessidade | O limite anual por objeto de mesma natureza (art. 75, §1º) fica muito abaixo da necessidade: ~R$ 62,7 mil em 2025, pelo Decreto 12.343/2024, valor a conferir. A necessidade é de R$ 1,5–2,5 mi mesmo saneada. Dividir em várias dispensas seria fracionamento ilegal. Serve só como ponte pontual dentro do limite | CP + CALC |
| X2 | **Dispensa emergencial** (art. 75, VIII) | A necessidade é planejada e previsível, então a emergência seria "fabricada". Só seria cabível diante de desabastecimento comprovado e por prazo limitado | CP |
| X3 | **Credenciamento** (art. 79) | Supõe preço fixado pela Administração e contratação paralela de todos os credenciados. Não há disputa de preço, e os preços de medicamentos variam muito entre fornecedores | CP + INF |
| X4 | **Lote único ou menor preço global** | Objeto divisível: a Súmula TCU 247 exige adjudicação por item. Lote único reduz a competição e aumenta o risco de concentração | CP |
| X5 | **Entrega integral imediata** (E4 em forma pura) | Contraria a restrição "não possui local adequado para armazenamento" e o risco de vencimento, dada a validade exigida | OBS + INF |
| X6 | **Consórcio público ou compra compartilhada regional** (Lei 11.107/2005) | O pacote não traz evidência de participação em consórcio com ata vigente. Criar ou aderir leva mais tempo que o horizonte da necessidade. **Recomendo estudar para o próximo ciclo** | INF |
| X7 | **Híbrido "E1 + E2 item a item"** (desconto CMED só nos 66 itens em que o E2 central sai mais barato) | O ganho teórico é de R$ 136,6 mil (R$ 1.812.130 → R$ 1.675.570, CALC `trabalho/20_estrategias.txt`). Mas esses são justamente os itens em que o mercado praticado está **acima** de CMED × (1 − desconto), ou seja, onde o desconto de 2024 tem menos chance de ser honrado. Exigiria ainda dois regimes paralelos | CALC + INF |
| X8 | **Usar a estimativa do órgão como referência** (status quo do ETP) | 41 itens ficam acima do teto CMED, o que torna a referência ilegal, e a sobre-estimação mediana é de 2,04×. Com pouca competição, o pregão aceitaria lances até essa referência, e o pior caso seria R$ 3,56 mi (R1) contra R$ 1,81 mi do E1 | CALC |
| X9 | **Inexigibilidade** (art. 74) | Só serve para fornecedor exclusivo, e o pacote não identifica item com registro único que a justifique | CP |
| X10 | **Deixar a cargo do MS/SES** (componentes centralizados) | Não é uma estratégia de compra do município. Para insulinas humanas e análogas é uma **verificação** que pode reduzir a quantidade comprada (ver `05_itens_criticos.md`) | CP (a verificar) |
