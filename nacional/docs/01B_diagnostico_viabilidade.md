# Etapa 1-B — Diagnóstico de viabilidade: demanda nacional e referência econômica

25/11/2026. Branch `reformulacao-nacional`. Decisões em `nacional/DECISOES_METODOLOGICAS.md`. **Nenhuma etapa decisória foi executada.**

## Conclusão

**Há um impedimento para a cesta tal como aprovada** (50 apresentações da RENAME de todos os componentes). Fiz as verificações abaixo e não encontrei fonte pública, anterior ao corte, que permita estimar a **demanda nacional dos medicamentos do Componente Básico** (compra municipal) **nem dos do Componente Estratégico**. Usar quantidade comprada no lugar de demanda, ou extrapolar para o país a partir dos 747 compradores do BPS, violaria a D-08. Por isso, conforme a D-07, **interrompi a execução** e apresento o impedimento.

**O que é viável em escala nacional:** o **Componente Especializado (CEAF)**. Ele tem:
- dispensação nacional mensal por apresentação (SIA/SUS);
- compra centralizada pelo Ministério e compras estaduais;
- preços federais e estaduais observáveis antes e depois do corte.

O caminho depende de uma decisão de vocês (§5). Restringir a cesta ao CEAF mantém a abrangência nacional, mas muda a composição de produtos aprovada. Por isso não fiz essa mudança por conta própria.

## 1. Demanda nacional: fontes verificadas

| Fonte | O que contém | Nacional? | Disponível em 29/01/2025? | Serve como demanda? |
|---|---|---|---|---|
| **SIA/SUS — APAC de medicamentos** (DATASUS: FTP `SIASUS/Dados/AM*.dbc` e TabNet `sia/cnv/qabr.def`) | Quantidade e valor aprovados por procedimento-medicamento (grupo 06), UF/município e mês | **Sim**: 27 UFs, 2008 até hoje | **Sim, com ressalva.** Os meses de processamento até out/2024 estavam publicados, mas a base atual inclui reprocessamentos (o arquivo AMPB2412 foi regravado em 09/01/2026). | **Sim, para o CEAF:** é a dispensação efetiva, ou seja, demanda atendida, não demanda total. |
| Farmácia Popular (Portal de Dados Abertos do SUS, conjunto MGDI) | **Pessoas atendidas**, não unidades dispensadas | Sim | **Não:** conjunto criado em 25/11/2025 | Não |
| BNAFAR / Hórus (Portal do SUS e API) | **Só posição de estoque** (atual) | Parcial | Não há série histórica (consultas de dez/2024 e jan/2025 vazias) | Não |
| SasiSUS — Farmácia (saúde indígena) | Entregas aos DSEIs | Só saúde indígena | Não: criado em 2026 | Não |
| Dispensação do Componente Básico (municipal) | — | **Não encontrada** em dados abertos | — | — |
| Distribuição do Componente Estratégico pelo MS | — | **Não encontrada** em dados abertos | — | — |
| Quantidades compradas (BPS, Compras.gov.br, PNCP) | Compras registradas | Parcial (ver §2) | Sim | **Não** (D-08): compra ≠ demanda |

**Teste com dados reais (SIA, processamento de nov/2023 a out/2024, TabNet):**
- **305** procedimentos de medicamentos com quantidade nacional;
- **243** deles com valor aprovado igual a zero. Isso é compatível com aquisição centralizada pelo Ministério (Grupo 1A, distribuído sem financiamento via APAC). É uma inferência a confirmar pela tabela SIGTAP/PRC nº 2/2017;
- **62** com valor aprovado positivo, que somam R$ 1,40 bilhão (financiamento, não preço de compra).

Exemplos de quantidade nacional em 12 meses: eltrombopague 50 mg, 989.692 comprimidos; sacubitril/valsartana 100 mg, 9,9 milhões; mepolizumabe, 42.437 frascos.

## 2. Referência econômica nacional

| Fonte | Cobertura nacional | Para o CEAF | Observação |
|---|---|---|---|
| **BPS** (2023–2024, sem extremos nem duplicatas) | R$ 2,95 bi, 2.283 CATMATs, 747 compradores; **só 88 registros federais** | Fraca: compras do MS quase ausentes | **Não representa o gasto nacional.** O "top 100" é dominado por itens com 1 a 8 compradores. Não serve para medir relevância econômica nacional. |
| **Compras.gov.br — pesquisa de preço** | Federal, estadual e municipal, com quantidade e data de resultado | **Boa.** Teste com adalimumabe 40 mg e infliximabe 100 mg: 167 e 152 registros, 73 e 85 federais, incluindo o **Departamento de Logística em Saúde** (compra centralizada do MS). Série de 2021 a 2026. | O cache atual cobre só 401 CATMATs; é preciso coletar os da cesta. O coletor e a regra temporal (`dataResultado`) já existem. |
| **PNCP** | Contratações, atas e contratos, inclusive federais e PCA | Boa em tese | **Inacessível daqui** desde 25/11/2026 (conexão recusada, também pela leitura web). Uma tentativa posterior é necessária. |
| CMED jan/2025 | Teto por apresentação | Completa | Para outras UFs falta a alíquota de ICMS de cada estado (Etapa 3). |
| Pagamentos efetivos por item | — | **Indisponível nacionalmente** | Existem empenhos federais (Portal da Transparência) e estaduais e municipais (tribunais de contas), sem item nem quantidade. **A referência econômica será homologada, contratada ou praticada, nunca paga** (D-08), e a avaliação terá de dizer isso. |

**Avaliação ex post** (depois do corte), para o CEAF:
- SIA de 2025, com a dispensação efetivamente observada;
- Compras.gov.br e BPS de 2025, com os preços observados;
- PNCP, quando voltar a responder.

## 3. Outras verificações

| Item | Situação |
|---|---|
| **RENAME vigente em 29/01/2025** | Portaria GM/MS nº 6.324, de 26/12/2024 (Rename 2024), vigente desde a publicação. A data de DOU indicada, 30/12/2024, ainda precisa de confirmação. **O PDF disponível é a 2ª edição, alterado em out/2025**: falta localizar a versão vigente no corte. Não há versão legível por máquina, só o painel "em tempo real". |
| População | API do IBGE/SIDRA (tabela 6579) responde; a estimativa de 2024 é anterior ao corte. |
| Orçamento | A **LOA 2025 não existia em 29/01/2025** (foi sancionada depois). No corte só havia o PLOA 2025 e a execução de 2024. A verificar na Etapa 2. |
| ICMS por UF, Anvisa (registros e descontinuação) | Não verificados nesta etapa: não decidem a viabilidade. Ficam para a Etapa 3. |

## 4. Verificação do objetivo global (D-09)

| Requisito | Com a cesta aprovada (todos os componentes) | Com uma cesta do CEAF |
|---|---|---|
| Problema em escala nacional | Sim | Sim (todas as UFs, três esferas: MS no Grupo 1A, estados nos Grupos 1B e 2) |
| Demanda nacional estimável sem extrapolação infundada | **Não** para os itens dos componentes Básico e Estratégico | **Sim** (dispensação do SIA) |
| Referência econômica comparável | Parcial | **Sim** (Compras.gov.br federal e estadual, BPS, CMED; PNCP pendente) |
| Inclui itens de aquisição centralizada (D-03) | Sim | **Sim** (Grupo 1A) |
| Espaço para cenários formulados pelo agente | Sim | Sim |
| Resultado observável para avaliar | Parcial | Sim (SIA e compras de 2025) |

## 5. Decisão necessária

1. **Cesta restrita ao CEAF.** 50 apresentações do Componente Especializado (que é parte da RENAME), escolhidas por relevância econômica nacional e qualidade dos dados, com itens de aquisição centralizada.
   - Mantém a abrangência nacional e as três esferas.
   - Muda a composição de produtos aprovada.
2. **Manter a cesta mista** e buscar a dispensação do Componente Básico por **pedido de LAI** ao Ministério (BNAFAR e Farmácia Popular).
   - O prazo e a resposta são incertos.
   - A disponibilidade desses dados em 29/01/2025 provavelmente não poderá ser comprovada.
3. **Outra definição** de vocês.

**Pendências que valem para qualquer opção:**
- PNCP inacessível, a tentar de novo;
- localizar a edição da RENAME vigente no corte;
- registrar a ressalva de reprocessamento do SIA.

## 6. Arquivos desta etapa

- `data/raw/nacional/datasus_sia/`: respostas do TabNet (quantidade e valor aprovados por procedimento, processamento de nov/2023 a out/2024).
- `data/raw/nacional/comprasgov_probe_*.json`: teste de cobertura federal no Compras.gov.br.
