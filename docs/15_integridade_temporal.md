# 15 — Integridade temporal e testes contra vazamento

> **Atualização pré-Etapa 4 (23/11/2026):** a varredura de todas as colunas removeu do pacote a situação atual dos itens PNCP, cancelamentos posteriores ao corte e datas/status atuais do Compras.gov.br; Compras.gov.br entrou como fonte com corte por `dataResultado`. Estado atual e números em `docs/18_pre_etapa4_tratamento_lacunas.md`; o texto abaixo descreve a Etapa 3.

**Data de corte: 29/01/2025** (véspera da publicação do PE 04/2025 no PNCP; dia em que o edital foi assinado). A disponibilidade é decidida pela **data em que a informação se tornou acessível**, não pela data do evento.

## 1. Classes

| Classe | Critério | Destino |
|---|---|---|
| `disponivel` | data de disponibilidade comprovada ≤ corte, ou informação interna do próprio órgão com evento ≤ corte | `data/decision_input/` |
| `posterior` | disponibilidade > corte | `data/evaluation_only/` (ou mantido em `data/raw/`, fora do pacote) |
| `indeterminado` | sem data, data inválida ou cronologia impossível | `data/quarentena_temporal/` |

## 2. Critério por fonte (`reports/validacao_temporal.csv`)

| Fonte | Data que decide | Resultado |
|---|---|---|
| BPS 2020–2026 | `dt_insercao` (entrada no sistema de consulta pública), com `dt_compra ≤ dt_insercao` | 286.467 disponíveis (225.518 medicamentos no pacote); 87.960 posteriores; 2.153 indeterminados (2.141 sem data válida, 12 com inserção anterior à compra). As inserções disponíveis vão até 13/12/2024; as compras, até 30/10/2024 |
| PNCP — contratação | `dataPublicacaoPncp` | 13 disponíveis; **1 publicada depois do corte apesar de a disputa ter começado antes** → posterior |
| PNCP — item | `dataInclusao` do item e contratação disponível | 1.091 disponíveis; 60 posteriores |
| PNCP — resultado | `dataInclusao` do resultado | **102 disponíveis; 173 posteriores** (resultados de 2024 publicados no PNCP só em 2025) |
| CMED | data impressa na lista | lista de 06/01/2025 disponível; lista de 09/11/2026 posterior |
| Edital/ETP/TR do PE 04/2025 | documento interno assinado em 29/01/2025 (PNCP 30/01/2025 07:34) | disponível (interno) |
| PE 01/2024 | PNCP: publicação 12/01/2024; 4 resultados incluídos em 02/09/2024 | disponível |
| PE 12/2024 | itens publicados em 21/03/2024; resultados incluídos no PNCP **só em 30/04/2025** | disponível **como informação interna**: contrato do próprio município, homologado em 11/04/2024 e executado em 2024 (R$ 1.223.231,57). Para terceiros, posterior |
| TCE-PB/SAGRES | data do empenho | 2024 disponível (despesa do próprio órgão); 2025–2026 posterior |
| Medicamentos Transparentes | plataforma publicada a partir de jun/2025 | **não entra no pacote**; usado só como índice para achar contratações, com datas conferidas no PNCP |
| CATMAT da Etapa 2 | derivado de registros BPS inseridos em 22/12/2025 | posterior; refeito com dados pré-corte (doc 13) |
| BNAFAR/Hórus | posição de 17–18/11/2026 | posterior (fora do pacote) |

**Regra da informação interna:** documentos e despesas do próprio órgão com data ≤ corte contam como disponíveis, mesmo que publicados depois, porque o decisor é o próprio órgão. A regra **não** vale para dados de terceiros.

## 3. O que foi excluído por indisponibilidade temporal

Resultados, contratos, aditivos e execução do PE 04/2025; pregões 25/2025 e 09/2026; despesa 2025–2026; 87.960 registros BPS posteriores; 1 contratação, 60 itens e 173 resultados do PNCP; CMED de nov/2026; estoque BNAFAR; CATMAT da Etapa 2; o pacote `data/processed/caso_santa_luzia/pre_decisao/` da Etapa 2, que contém esse CATMAT; o painel "Preço de Referência" do TCE-PB (janela móvel atual).

## 4. Testes automáticos (`scripts/28_verificacoes.py` → `reports/etapa3_testes.csv`)

| Grupo | Testes | Resultado |
|---|---|---|
| temporal | só `disponivel` em cada tabela; `max(data_disponibilidade/data_insercao/data_publicacao_pncp/data_inclusao) ≤ corte`; CMED de 06/01/2025; resultado PNCP só com item disponível | 26/26 passaram |
| vazamento | sem colunas de resultado nos itens/padronização; varredura de **nomes de arquivo, textos, CSV, JSON, Markdown e todas as colunas texto dos Parquet** por identificadores e valores pós-corte (nº de controle dos pregões 25/2025 e 09/2026, contratos, "nova demanda", R$ 3.105.249,60, R$ 586.816,65, 18,9%); BPS sem compras de Santa Luzia de 2025; nenhuma coluna dos itens reproduz o preço homologado (> 5% de coincidência); PNCP sem contratações de 2025–2026 de Santa Luzia; manifesto sem caminhos reservados; módulo de consulta recusa caminhos fora do pacote | 12/12 passaram |
| reprodutibilidade | hashes do manifesto conferem; todo arquivo do pacote está no manifesto | 2/2 passaram |

O preço unitário estimado pelo órgão coincide com o homologado em **12,9%** dos itens. Isso **não** é vazamento: a estimativa é anterior ao corte, e a coincidência resulta de lances no valor estimado.

## 5. Riscos residuais

- O arquivo atual do BPS pode ter sido revisado depois da inserção (exclusões, correções). Não dá para provar que o conteúdo de cada registro em jan/2025 era idêntico ao atual.
- A seleção das contratações PNCP usou o índice do Medicamentos Transparentes (publicado depois do corte). Isso afeta só quais contratações foram examinadas, não o conteúdo, cujas datas foram verificadas no PNCP.
- As regras de padronização foram calibradas olhando dados de todas as datas (por exemplo, a regra de caneta de insulina). Elas descrevem identidade de produto e não usam preço, fornecedor ou resultado.
