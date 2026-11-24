# 11 — Viabilidade do experimento (comparar decisões e quantificar eficiência)

> Documento para os pesquisadores. Contém resultados posteriores à data de decisão; **não fornecer ao agente decisor**.

## 1. Desenho retrospectivo

| Elemento | Definição |
|---|---|
| Caso | Prefeitura de Santa Luzia/PB — aquisição anual de medicamentos da Assistência Farmacêutica |
| Data de decisão | **29/01/2025** (véspera da publicação do PE 04/2025 no PNCP) |
| Conjunto de informação do agente | `docs/10_problema_organizacional.md` + `data/processed/caso_santa_luzia/pre_decisao/` |
| Conjunto reservado | `data/processed/caso_santa_luzia/reservado_avaliacao/` + `docs/08` (seção 10) |
| Decisão real observada (linha de base) | Pregão eletrônico por item, menor preço, sem registro de preços; 334 itens com as quantidades do ETP; contratos de 12 meses; garantia de 5%; entrega em até 5 dias úteis; preços estimados sigilosos |
| Janela de resultados | 30/01/2025 – 31/08/2026 |

### Controle de vazamento

| Risco | Controle aplicado |
|---|---|
| BPS com registros posteriores | Filtro `dt_insercao ≤ 29/01/2025` (inserção, não data de compra) |
| CMED atual (nov/2026) | Usar só a lista publicada em 07/01/2025 |
| CATMAT obtido do BPS de dez/2025 | Só a identidade do produto entra no pacote; preço, quantidade e fornecedor homologados ficam fora (autoverificação em `scripts/22_caso_pacotes_decisao.py`) |
| Preços unitários estimados publicados depois no PNCP | São a estimativa interna do órgão, conhecida por ele antes da publicação; ficam no pacote como informação legítima do decisor |
| Execução de 2025 do PE 12/2024 | Excluída; o agente sabe só da execução de 2024 |
| Painel "Preço de Referência" do TCE-PB | Excluído: a janela móvel de 12 meses hoje cobre só o período posterior |
| BNAFAR (estoque) | Excluído: só existe a posição de nov/2026 |
| Documentos do PNCP | Só o edital/ETP; resultados, contratos e aditivos ficam reservados |

## 2. Resultados reais disponíveis para comparação (reservados)

| Resultado | Valor | Fonte |
|---|---|---|
| Valor homologado e contratado | R$ 3.105.249,60 (−37,3% sobre a estimativa); 7 fornecedores; 334/334 itens | E-08 |
| Preço homologado por item | 334 itens com fornecedor e quantidade | `reservado_avaliacao/resultado_homologado_PE04_2025.csv` |
| Execução financeira por contrato | Empenhado R$ 586.816,65 = 18,9% do contratado até 31/08/2026; de 7,8% a 90,9% por contrato | `execucao_contratos.csv` |
| Despesa farmacológica total | 2025: R$ 1.410.230,18; 2026 (jan–ago): R$ 1.350.148,81 | `farmaco_anual_2025_2026.csv` |
| Prorrogações | 3 de 7 contratos prorrogados por 12 meses, preços e quantidades inalterados | E-05b |
| Necessidades não previstas | PE 25/2025: 87 itens novos (1 coincide com o PE 04/2025); estimado R$ 5,59 mi; homologado R$ 2,78 mi; contratado R$ 1,17 mi | E-08 |
| Plano seguinte | PE 09/2026: 312 de 329 itens repetidos; 207 com a mesma quantidade | `evolucao_itens.csv` |

## 3. Indicadores que podem ser calculados depois (sem calcular agora)

| Indicador | Dados | Observável ou estimado |
|---|---|---|
| Custo total da alternativa escolhida pelo agente | Quantidades × preço de referência fixado ex ante (BPS até a data, CMED jan/2025, descontos do PE 12/2024) | **Estimado** (contrafactual) |
| Custo da decisão real | R$ 3.105.249,60 contratado; R$ 586.816,65 empenhado | Observado |
| Custo por unidade compatível | Preço por item vs. mediana BPS (mesmo CATMAT e unidade) | Observado (real) / estimado (agente) |
| Compromisso financeiro assumido vs. uso efetivo | Contratado vs. empenhado por contrato | Observado (real); estimado (agente) sob hipótese de demanda |
| Exposição a garantias e encargos | 5% do valor contratado na decisão real | Observado (regra); efeito no preço não observável |
| Atendimento das quantidades | Itens com fonte de suprimento definida; itens fracassados ou desertos | Observado (real: 0 fracassos) |
| Necessidades fora do plano | Itens do PE 25/2025 | Observado |
| Conformidade com as restrições | Registro, validade, armazenamento, entrega, CMED | Verificável por regras |
| Economia potencial | Diferença contra uma referência declarada | Estimado; **nunca** "economia realizada" |

## 4. O caso permite uma decisão além da comparação de preços?

Sim, com ressalvas. A decisão envolve dimensões com consequências diferentes e documentadas:

- **Incerteza de demanda × compromisso financeiro.** A quantidade declarada é 2,5 vezes o gasto do ano anterior. Na decisão real, só 18,9% do contratado foi empenhado em 18 meses. Logo, o tamanho e a forma do compromisso têm consequência mensurável.
- **Mecanismos alternativos já usados pela organização.** O pregão por item e o pregão por desconto sobre a CMED têm resultados observados. A Lei 14.133 prevê outros instrumentos, como registro de preços e adesão a atas.
- **Restrição operacional de armazenamento**, que afeta a forma e a frequência das entregas.
- **Itens de alto valor concentrado** (insulinas, 27% do valor estimado) e itens fora da RENAME.

Nenhuma alternativa foi formulada nesta etapa. A lista acima apenas mostra que o problema tem mais de uma dimensão.

## 5. Limitações que permanecem

1. **Contrafactual**: o preço e a execução de alternativas não adotadas não são observáveis. A comparação precisa de regras de estimativa fixadas antes do experimento, com as referências pré-decisão.
2. **Demanda por item desconhecida**: a execução é observada por contrato e fornecedor, não por item. A avaliação de "atendimento" fica agregada.
3. **Estoque inicial desconhecido**.
4. **Risco de mercado não quantificado** (lista de desabastecimento não obtida).
5. **CMED de jan/2025 processada, mas por embalagem**: 259 itens vinculados de forma provável; a apresentação pode divergir da pedida e a conversão para unidade de fornecimento não foi feita.
6. **Caso pequeno** (município de 15 mil habitantes; R$ 3,1 mi contratados), o que limita a generalização.
7. **Causa da baixa execução não verificada**: pode ser superestimação, entregas registradas de outra forma ou mudança de demanda. Não usar como prova de erro do órgão.

## 6. Avaliação

| Dimensão (Etapa 1, §9) | Antes (PB genérica) | Caso Santa Luzia |
|---|---|---|
| Objetivo | Parcial | **Suficiente** (ETP) |
| Necessidades | Parcial (fraca) | **Parcialmente suficiente**: quantidades e método declarados; sem consumo nem estoque |
| Recursos | Parcial | **Parcialmente suficiente**: estimativa, dotações e despesa realizada; sem saldo de dotação |
| Condições de aquisição | Parcial | **Suficiente** para condições contratuais; insuficiente para disponibilidade de mercado |
| Eficiência | Parcial | **Parcialmente suficiente**: real observado; alternativas estimadas |
| Consequências | Insuficiente | **Parcialmente suficiente**: execução, prorrogações e nova demanda observadas; sem dados de ruptura e entrega |

**Conclusão:** o experimento é **viável com hipóteses explícitas** (classificação B mantida, agora com um caso concreto). Dá para comparar a decisão do agente com a decisão real em custo, compromisso financeiro e uso efetivo, com resultados reais e auditáveis. A comparação das alternativas não adotadas é necessariamente uma estimativa.

Pendências antes da próxima etapa (decisão do usuário): (a) ~~processar a CMED de jan/2025~~ — feito em 23/11 (conferência de apresentação e conversão por item ainda pendentes); (b) fixar as regras de estimativa contrafactual antes de rodar o agente; (c) opcionalmente, pedir via LAI à Prefeitura o consumo por item de 2023–2024.
