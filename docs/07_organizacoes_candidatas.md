# 07 — Organizações candidatas e escolha do caso

Etapa 2, 23/11/2026. Base: dados da Etapa 1 (`data/processed/`, `reports/`) + investigação dirigida no PNCP, TCE-PB e editais. Scripts: `17_candidatas.py`, `18_pncp_compra_completa.py`, `19_textos_documentos.py`, `20`–`22`.

> **Correção da Etapa 1 descoberta aqui:** o Medicamentos Transparentes (CSV e JSON) traz **no máximo 10 itens por contratação**. O PNCP mostra 38, 151 e 334 itens em contratações que o MT lista com 10. Contagens de itens e CATMAT da Etapa 1 são, portanto, **subestimadas** nas contratações grandes. Nesta etapa os itens vêm sempre da API do PNCP.

## 1. Critério

Completude do contexto decisório, não volume. Para cada candidata, verifiquei se há documento oficial com:
(N) medicamentos e quantidades necessárias e a **base de cálculo**; (O) orçamento ou recursos aplicáveis; (C) contratos ou atas; (P) prazos e condições de fornecimento; (R) restrições legais e operacionais; (H) histórico de aquisições e preços comparáveis; e (X) **consequências observáveis depois da decisão** (execução, fracassos, novas compras).

## 2. Candidatas investigadas

| | **Santa Luzia/PB** (Prefeitura 09.090.689/0001-67; FMS 10.425.754/0001-47) | **Fundação PB Saúde** (38.111.778/0001-40) | **Campina Grande/PB** (Município 08.993.917/0001-46; FMS 24.513.574/0001-21) | **EBSERH – HU Lauro Wanderley** (15.126.437/0003-05) | **SES-PB** (08.778.268/0001-60) |
|---|---|---|---|---|---|
| Tipo | Município pequeno (15.387 hab., IBGE 2024) | Fundação estadual que gere hospitais | Município grande | Hospital universitário federal | Secretaria estadual |
| Licitação examinada | PE 04/2025 (PNCP 09090689000167-1-000006/2025) | SF 22/2025 (38111778000140-1-000013/2025) | PE 308/2025 (08993917000146-1-000159/2025) | 15126437000305-1-000882/2026 | — (só dispensas no MT) |
| Itens no PNCP | **334**, todos homologados | 33: 19 homologados, 13 fracassados, 1 deserto | 38, todos homologados | 151: 119 homologados, 26 fracassados, 5 desertos, 1 anulado | — |
| (N) Quantidades e base | **Sim**: TR com 334 quantidades "baseadas na utilização anual dos anos anteriores"; mais 349 itens no PE 01/2024 e 329 no PE 09/2026 | **Sim**: média de consumo de 3 anos **+ 50%** de margem (TR, p. 30) | Parcial: lista de itens; edital de 67 p. digitalizado (13,6 mil caracteres extraíveis) | Não lido (download do edital: **HTTP 422**) | Só linha agregada no PCA 2026 (R$ 756,6 mi) |
| (O) Orçamento | **Sim**: dotações e fontes no edital; estimativa R$ 4.952.438,00; execução empenhada/liquidada/paga 2024–2026 (TCE-PB) | Parcial: Contratos de Gestão nº 002/2023 e 043/2023 citados; valores não obtidos | Parcial: TCE-PB disponível (não baixado); não está no BPS | Não verificado (federal; Portal da Transparência exige chave) | PCA agregado; execução estadual não extraída |
| (C) Contratos/atas | **Sim**: 7 contratos (R$ 3.105.249,60) + 3 aditivos de prorrogação (PDF) | SRP (ata não listada na API) | Contratos não verificados; não SRP | **Ata 00250/2026** (vigência 26/05/2026–26/05/2027) | — |
| (P) Prazos e condições | **Sim**: entrega ≤ 5 dias úteis por pedido; contrato de 12 meses; pagamento em 30 dias; reajuste anual | Sim (edital legível) | Não extraível (digitalizado) | Não lido | — |
| (R) Restrições | **Sim**: registro Anvisa, validade ≥ 75%, garantia de 5%, **sem local adequado de armazenamento** | Sim: regras de adesão SRP; Decreto Estadual 43.759/2023; Portaria TCE-PB 138/2023 (citada) | Parcial | Não lido | — |
| (H) Histórico e preços | **Sim**: pregões 2024 no PNCP (01/2024 incompleto; 12/2024 completo); 285 itens com preço no BPS antes da decisão | Médio (não está no BPS) | Fraco (não está no BPS) | Fraco (não está no BPS) | BPS 397 registros |
| (X) Consequências observáveis | **Sim**: execução por contrato (TCE-PB × CNPJ), prorrogações, pregão de "nova demanda" (25/2025), plano 2026 | Itens fracassados e segunda sessão | 13 dispensas emergenciais em 2025–26 (MT) | Fracassados/desertos e "reedições" | Dispensas emergenciais |
| Integração de produto | CATMAT **ausente** no PNCP; recuperado para 299/334 itens via BPS | CATMAT no MT (truncado) | idem | idem | idem |

Salgadinho/PB (Etapa 1) foi descartado: no PNCP/MT há um único pregão de medicamentos, e ele está "em andamento"; o município é forte só em BPS e TCE-PB.

**Outros estados.** Não examinei outros estados. As lacunas que pesam no problema — consumo por item, estoque histórico, orçamento por medicamento — são estruturais das fontes nacionais (Etapa 1). Uma organização de outro estado só superaria Santa Luzia se tivesse um equivalente ao TCE-PB/SAGRES (despesa por credor e licitação), e isso não foi verificado.

## 3. Comparação

| Critério (peso igual) | Santa Luzia | PB Saúde | Campina Grande | HULW | SES-PB |
|---|---|---|---|---|---|
| N | ●● | ●● | ● | ○ | ○ |
| O | ●● | ● | ● | ○ | ● |
| C | ●● | ● | ○ | ●● | ○ |
| P | ●● | ●● | ○ | ○ | ○ |
| R | ●● | ●● | ● | ○ | ○ |
| H | ●● | ● | ○ | ○ | ● |
| X | ●● | ● | ●● | ● | ● |
| **Total (0–14)** | **14** | 10 | 6 | 4 | 4 |

●● documentado e verificado · ● parcial · ○ ausente ou não verificado. A pontuação ordena as candidatas; não é uma medida.

## 4. Escolha: Prefeitura Municipal de Santa Luzia/PB — aquisição anual de medicamentos da Assistência Farmacêutica (PE 04/2025)

Justificativa com evidências:
1. **Necessidade documentada pela própria organização**: 334 itens com quantidade, unidade e especificação no ETP/TR, e a declaração de método ("utilização anual dos anos anteriores"). Fonte: edital PE 04/2025, anexo I, p. 19–27.
2. **Recurso financeiro identificado em dois níveis**: dotações e fontes no edital, e despesa realizada (empenhada, liquidada e paga) por ano, licitação e credor no TCE-PB (R$ 1.953.288,72 empenhados em 2024).
3. **Restrições operacionais explícitas e verificáveis**: entrega em até 5 dias úteis "tendo-se em vista a administração não possuir local adequado para armazenamento"; validade mínima; garantia de 5%.
4. **Ciclo de decisão repetido e observável**: pregões anuais em 2024, 2025 e 2026, mais um pregão de "nova demanda" e um mecanismo alternativo já usado (pregão por **maior desconto sobre a tabela CMED**, PE 12/2024).
5. **Consequências mensuráveis depois da decisão**: contratos, aditivos e execução por contrato. Exemplo: 18,9% do valor contratado no PE 04/2025 foi empenhado até ago/2026 (reservado à avaliação; ver `11`).
6. **Referências de preço independentes e anteriores à decisão**: BPS inserido até 29/01/2025 cobre 285 dos 334 itens (84,6% do valor estimado); lista CMED/PMVG de 07/01/2025 obtida.

Principais fraquezas aceitas: município pequeno (decisão de porte modesto), ausência de consumo e estoque por item, CATMAT ausente no PNCP, PCA municipal não publicado no PNCP. Ver `09` e `11`.

A **Fundação PB Saúde** é a segunda opção: tem método de quantificação explícito e risco de fornecimento documentado (fracassos). Faltam dados de execução financeira acessíveis.
