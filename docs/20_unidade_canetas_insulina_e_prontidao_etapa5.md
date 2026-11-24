# 20 — Unidade das insulinas em caneta (PE 04/2025) e conclusão da preparação da Etapa 5

23/11/2026. Fontes: documentos oficiais da contratação, baixados do PNCP para `data/raw/pncp/etapa2/09090689000167_2025_6/docs/`. São posteriores ao corte e **não podem ser fornecidos ao agente decisor**.

Nada foi alterado em:
- os arquivos congelados da Etapa 4;
- o pacote v1;
- as saídas anteriores de `etapa5/avaliacao/`.

A conferência dos hashes está no `LOG_PRE_ETAPA_5.md`, §8. Script: `scripts/34_canetas_insulina.py`; saídas em `etapa5/avaliacao_canetas/`.

## Resumo
- **A unidade está comprovada: é a caneta individual.** O ETP, o Termo de Referência, o Contrato nº 00054/2025 e seu Termo Aditivo nº 01 trazem "Caneta" nos itens 194, 195, 196 e 199. A ata do pregão traz "UN" e o cadastro no PNCP, "Unidade". **Nenhum documento fala em caixa.**
- **Quantidades e preços por caneta:**

  | Item | Canetas | Preço por caneta |
  |---|---|---|
  | 194 | 100 | R$ 195,68 |
  | 195 | 100 | R$ 194,76 |
  | 196 | 6.000 | R$ 193,02 |
  | 199 | 1.200 | R$ 147,36 |

  Os quatro preços são exatamente a estimativa do órgão, com desconto de 0%.
- **O produto contratado não pode ser identificado.**
  - Cada caneta teve **uma única proposta**, de ALLFAMED, com "Modelo" e "Marca/Fabricante" = **EQUIPLEX**.
  - Na CMED de jan/2025, a EQUIPLEX (CNPJ 01.784.792/0001-03) tem 68 apresentações, **todas soluções parenterais e nenhuma insulina**.
  - A proposta readequada pedida em 20/02/2025 não está publicada.
- **Compatibilidade com a CMED:**
  - as únicas canetas de NPH e Regular com preço CMED são Novolin N e R FlexPen, com teto de R$ 20,14 e R$ 15,80 por caneta;
  - o preço contratado é **9,6× e 9,3×** esse teto;
  - mesmo na hipótese de caixa com 5 canetas, que nenhum documento sustenta, ficaria 1,9× acima do teto da caixa;
  - as análogas também ficam acima do **maior** teto por caneta compatível com o tipo: 1,15× (item 194) e 5,5× (item 195).
- **Impacto na avaliação:**
  - a comparação por caneta feita no doc 19 está confirmada, e a leitura do agente (preço por caneta) coincide com o edital;
  - nenhum número de comparação, sensibilidade ou economia muda;
  - há **uma correção**, feita em arquivo separado: o número de itens homologados acima do teto passa de **15 para 17** (os itens 194 e 195 são acrescentados), e o excesso, de R$ 1.261.859 para **R$ 1.280.392**.

## 1. Evidências documentais (`evidencias_documentais.csv`)

Cada trecho é localizado automaticamente na página indicada. O script falha se algum deixar de ser encontrado.

| Id | Documento | Pág. | O que mostra |
|---|---|---|---|
| D1 | Edital PE 04/2025, Anexo I: Estudo Técnico Preliminar | 24 | "…3ml **Caneta** 100" (itens 194 e 195); "…sistema de aplicação **caneta** 6.000" (196); "…**caneta** 1.200" (199) |
| D2 | Edital PE 04/2025, Anexo II: Termo de Referência | 34 | Mesmas linhas, com unidade "Caneta" |
| D3 | Ata Final do pregão (Portal de Compras Públicas), quadro de itens | 6 | "R$ 193,02 6.000 **UN**"; "R$ 147,36 1.200 **UN**"; idem para os itens 194 e 195 |
| D4 | Ata Final, resultado por fornecedor | 30 | "EQUIPLEX EQUIPLEX 193,02 6.000 1.158.120,00" e as linhas equivalentes dos itens 194, 195 e 199 |
| D5 | Ata Final, propostas por item | 116 | Uma única proposta para cada caneta: ALLFAMED, EQUIPLEX, no valor estimado |
| D6 | Contrato Administrativo nº 00054/2025 (ALLFAMED) | 5 | "6.000 **caneta** 193,02"; "1.200 **caneta** 147,36"; "100 **Caneta** 195,68"; "100 **Caneta** 194,76" |
| D7 | Termo Aditivo nº 01 ao Contrato nº 00054/2025 (prorrogação) | 4 | "6.000 **caneta** 193,02 1.158.120,00"; "1.200 **caneta** 147,36 176.832,00" (texto por OCR) |
| D8 | PNCP: cadastro do item e resultado | — | `unidadeMedida = Unidade`; homologado 6.000 × 193,02; `percentualDesconto = 0` |

**Também consultados:**
- **Empenhos de 2025 e 2026 da contratada (TCE-PB/SAGRES):** os históricos são genéricos ("fornecimento de medicamentos… conforme Pregão Eletrônico 0004/2025"), sem item nem quantidade. Não permitem saber o que foi entregue.
- **Mensagens da sessão:** só registram eventos do sistema, sem discussão das canetas.
- **Contraste com os frascos** (197 e 198):
  - vencedora PANORAMA, marca N.NORDISK;
  - houve disputa (ALLFAMED/EQUIPLEX ofertou R$ 55,49);
  - preço de R$ 48,00, **dentro** do teto (R$ 50,77 no v2 e R$ 49,80).

## 2. Compatibilidade com a CMED (`cmed_canetas_compativeis.csv`, `impacto_canetas.csv`)

Apresentações de jan/2025 com sistema de aplicação, 100 U/mL, 3 mL, sem pré-misturas, na alíquota e no tipo de teto da PB:

| Item | Tipo | Canetas CMED compatíveis | Teto por caneta (mín.–máx.) | Homologado por caneta | Homologado ÷ teto máx. | Hipótese não documentada: caixa com 5 |
|---|---|---|---|---|---|---|
| 194 | Análoga prolongada | 17 | R$ 23,77–169,97 | R$ 195,68 | 1,15 | dentro do teto |
| 195 | Análoga rápida | 6 | R$ 28,82–35,14 | R$ 194,76 | 5,54 | 1,11× o teto |
| 196 | NPH | 2 (Novolin N FlexPen, 1 e 5) | R$ 20,14–20,15 | R$ 193,02 | **9,58** | 1,92× o teto |
| 199 | Regular | 2 (Novolin R FlexPen, 1 e 5) | R$ 15,80–15,81 | R$ 147,36 | **9,32** | 1,86× o teto |

O item 194 é a única caneta que caberia no teto se a unidade fosse uma caixa. Ainda assim, isso dependeria da substância, que o item não especifica, e da hipótese de caixa, que nenhum documento sustenta.

## 3. Impacto nos cálculos e nas conclusões da avaliação

| Aspecto (doc 19) | Antes | Agora |
|---|---|---|
| Limitação 2: "não se sabe se a unidade é caneta ou caixa" | Impedia conclusões sobre o preço das canetas | **Resolvida quanto à unidade:** caneta, em 7 documentos. Fica uma limitação mais estreita: qual produto foi contratado e entregue. |
| Erro de projeção do agente (homologado − E1 = R$ 1,29 mi; 92% nas canetas) | Podia ser artefato de unidade | É diferença real de preço por caneta |
| C4: itens homologados acima do teto | 15 itens; excesso R$ 1.261.859 | **17 itens; excesso R$ 1.280.392** (`correcao_C4.csv`). Os itens 194/195 foram comparados ao maior teto compatível, o critério mais favorável à decisão real. |
| Comparação de preços, sensibilidade (S0–S8), economia em três níveis | — | Sem alteração: a comparação já era por caneta |
| Leitura do agente | Preço por caneta, limitado ao teto CMED | Coincide com o edital |

**Contexto, não usado em cálculo** (`contexto_pe_09_2026.csv`): no PE 09/2026, as propostas para o mesmo item de caneta NPH (6.000 unidades) foram de R$ 9,31 a R$ 158,51, em apresentações heterogêneas. A vencedora, a R$ 29,00, descreveu o produto como "5 REFIL 3ML S/CANETA – NOVOLIN N penfil", isto é, refil sem caneta. Por não ser equivalente ao item, não foi usado como referência.

## 4. Limitações que permanecem (lista consolidada para a Etapa 5)

1. **Contrafactual da recomendação (E1):** não foi executada; em 18% dos itens o mercado aceitou preço acima da faixa do agente.
2. **Canetas:** a unidade está comprovada, mas não o **produto** (marca declarada sem insulina na CMED) nem a **quantidade entregue** (empenhos genéricos; o contrato com as canetas foi executado em 7,8% do valor). Isso impede concluir quanto se pagou de fato por canetas e se o produto entregue tinha registro.
   - Esclarecimento possível: notas fiscais e atestados de recebimento, por LAI.
   - Isso não afeta a avaliação da decisão do agente, que é ex ante, nem o preço contratado por caneta.
3. **E2 (desconto sobre a CMED) só modelado:** foi o canal mais usado em 2025, sem preço por item.
4. **Economia realizada não mensurável por item:** a da decisão real só existe como estimativa sob hipótese; a do agente não existe.
5. **Demanda:** execução de 18,9% do contratado.
6. **Cota federal de insulinas humanas** para Santa Luzia: desconhecida.
7. **Avaliador não cego.**
8. **Conversões sem validação humana.**
9. **Normas do Planalto** lidas pela web, sem cópia local.

## 5. Conclusão da preparação: prontidão para a Etapa 5

| Componente | Situação | Onde |
|---|---|---|
| Decisão do agente congelada, com isolamento auditado | pronta, sem alteração | `etapa4/`, `LOG_ETAPA_4.md` |
| Falhas do pacote verificadas e pacote v2 separado | pronta | `etapa5/verificacao/`, `data/decision_input_v2/` |
| Normas citadas pelo agente verificadas | pronta | doc 19, §2 |
| Protocolo de avaliação pré-registrado | pronto, sem mudança | `etapa5/PROTOCOLO_AVALIACAO.md` |
| Reprodução e verificação dos cálculos | 13/13 saídas idênticas; 20/20 verificações | `etapa5/avaliacao/` |
| Comparação com os dados reservados, viabilidade, sensibilidade, economia em três níveis | pronta | `etapa5/avaliacao/`, doc 19 |
| Unidade das canetas e compatibilidade com a CMED | comprovada; C4 corrigido em separado | `etapa5/avaliacao_canetas/`, este doc |
| Julgamento de mérito | **Etapa 5** | — |

Para a Etapa 5, falta decidir **quem avalia o mérito**. O material está pronto para um avaliador cego (outro agente ou uma pessoa sem acesso a esta sessão), a partir de:
- `etapa5/PROTOCOLO_AVALIACAO.md`;
- os entregáveis congelados do agente;
- as evidências deste doc e do doc 19.

A limitação 2 deve ser considerada no julgamento da decisão real, não no da decisão do agente.
