# 06 — Economia potencial e como medir a economia efetiva

Fontes: `trabalho/20_estrategias.py`, `trabalho/40_numeros_texto.py` e suas saídas `.txt`. Todos os valores abaixo são **economia potencial**: diferenças estimadas em 29/01/2025, condicionadas às hipóteses H05–H16. **Nenhum deles é economia efetiva.**

## 1. Referências e adequação

| Referência | Valor (R$) | É adequada para medir economia? |
|---|---:|---|
| **E2: custo esperado do modelo de desconto sobre a CMED** (o que o órgão fez em 2024 com 62,6% do gasto) | 4.035.750 (faixa de 2.300.004 a 4.543.594) | **Sim, é a referência principal.** É o contrafactual mais provável, ou seja, o que aconteceria sem a recomendação: o modelo já usado e já aceito pelo mercado local. Limite: é um custo modelado, não observado (H09) |
| **R1: estimativa do órgão limitada ao teto CMED** | 3.556.151 | **Sim, como referência secundária, orçamentária.** É o maior valor legalmente admissível da necessidade tal como orçada. Limite: herda a sobre-estimação de ~2× da estimativa do órgão. Mede o **orçamento liberado**, não um ganho de mercado |
| R0: estimativa do órgão (R$ 4.952.438) | — | **Não.** Contém R$ 1.396.287 acima do teto CMED. Medir contra ela contaria como economia a simples retirada de um valor ilegal |

## 2. Cálculo (CALC)

### 2.1 Economia potencial principal: E1 em relação a E2

| | E1 baixo (1.499.016) | E1 central (1.812.130) | E1 alto (2.508.722) |
|---|---:|---:|---:|
| **E2 baixo** (2.300.004) | 800.988 | 487.874 | **−208.718** |
| **E2 central** (4.035.750) | 2.536.734 | **2.223.619** | 1.527.028 |
| **E2 alto** (4.543.594) | 3.044.578 | 2.731.464 | 2.034.872 |

- **Central: R$ 2,22 mi** (55% do custo do E2).
- **Faixa plausível**, com os cenários de preço na mesma direção para as duas estratégias: **R$ 0,80 a 2,03 mi**.
- **Faixa extrema**, com os cenários cruzados: de **−R$ 0,21 mi** a +R$ 3,04 mi.

**Condições.** H09 (descontos de 2024, base PF, gestão ativa da categoria), H05 (preço contratado em torno da mediana praticada) e demanda do ETP. Com demanda de 75%, a diferença central cai na mesma proporção: R$ 3,03 mi − R$ 1,36 mi = R$ 1,67 mi. Ela some se os descontos sobre a CMED chegarem a ~86% em genéricos, ~82% em similares e ~70% em éticos (`03_comparacao.md`).

### 2.2 Economia potencial secundária: E1 em relação a R1 (orçamento)

- **Central: R$ 1,74 mi** (49% de R1).
- **Faixa: R$ 1,05 a 2,06 mi.**

Condições: as mesmas do E1. Leitura: valor da reserva de R$ 4,95 mi (H02) que **não precisa** ser comprometido, além do ajuste de conformidade.

### 2.3 Correção de conformidade (não é economia)

R0 − R1 = **R$ 1.396.287**. É o excesso das estimativas sobre o teto CMED em 41 itens, sendo 85,6% nas canetas de insulina 196 e 199. Fica separado e não se soma a nenhuma economia.

### 2.4 O que não se soma

- As economias 2.1 e 2.2 usam referências diferentes e **não se somam**.
- Nenhuma delas se soma à economia efetiva, que ainda não existe.
- A diferença entre E3 e E1 (R$ 100,6 mil) é uma opção de contingência e não entra na economia da recomendação.

## 3. Por que a economia potencial é incerta

1. **Preço real dos lances (H05).** Lances acima da mediana em itens de baixa competição levam ao E1 alto.
2. **Itens sem referência externa (H07).** São 63 itens com referência provisória de R$ 217 mil, que pode chegar a R$ 444 mil.
3. **Desertos.** Sobretudo nas canetas: os itens desertos seriam comprados depois por outra via, possivelmente mais cara.
4. **Base e comportamento no E2 (H09).** Com o registro mais barato, a economia cai a R$ 0,49 mi (E1 central); com escolha livre do fornecedor, sobe a R$ 2,73 mi.
5. **Demanda (H12).** Muda o valor absoluto, mas não o sinal.

## 4. Como medir a economia efetiva

A economia efetiva **não é observável em 29/01/2025**. Ela deve ser medida assim.

**Quando.**
- Na homologação: economia de preço **contratado**, ainda potencial quanto à quantidade.
- Trimestralmente durante a ata.
- No fechamento dos 12 meses: **economia efetiva**.

**Com quais dados.**
- Ata e preços homologados por item (PNCP).
- Notas de empenho, liquidação e pagamento por item (SAGRES/TCE-PB e sistema contábil).
- Notas fiscais e termos de recebimento com quantidade entregue, lote e validade.
- Registro de entradas e dispensação (Hórus/BNAFAR).
- Lista CMED vigente em cada mês de compra.
- Compras feitas fora da ata (dispensas, adesões, judiciais).

**Como.**
1. **Fórmula principal:** Economia efetiva = Σ_i (p_ref_E2,i − p_contratado,i) × q_entregue,i.
   - p_ref_E2,i é o preço que o modelo de 2024 teria cobrado pelo **mesmo registro entregue**: PF (ou PMVG) da lista CMED do mês × (1 − desconto da categoria).
   - Usa-se a **mesma quantidade entregue** nos dois lados, para não confundir economia com compra de quantidade menor.
2. **Indicador secundário:** Σ_i (p_ref_R1,i − p_contratado,i) × q_entregue,i, com p_ref_R1 congelado em `plano_por_item.csv`: estimativa do órgão limitada ao teto.
3. **Itens comprados fora da ata** (desertos, emergências) entram com o preço efetivamente pago, e não são excluídos. Desabastecimentos devem ser registrados à parte: dias sem estoque por item.
4. **Reajustes ou reequilíbrios da ata** entram no p_contratado da data de cada compra.
5. **Resultado:** economia efetiva total e por item, com a lista de itens em que o E1 saiu mais caro que a referência.
