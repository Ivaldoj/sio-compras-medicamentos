# 09 — Evidências e lacunas do caso Santa Luzia/PB

Acessos em 23/11/2026. Hash SHA-256 e hora UTC de cada download em `reports/manifest_fontes.csv`; respostas da API do PNCP preservadas em `data/raw/pncp/etapa2/`. Status: **[C]** comprovado · **[K]** calculado · **[I]** inferido · **[A]** ausente.

## 1. Registro de evidências

| ID | Fonte / documento | URL ou endpoint | Arquivo local | Data do documento | Identificação do registro | Uso | Status |
|---|---|---|---|---|---|---|---|
| E-01 | PNCP — contratação | `https://pncp.gov.br/api/consulta/v1/orgaos/09090689000167/compras/2025/6` | `data/raw/pncp/etapa2/09090689000167_2025_6/compra.json` | publ. 30/01/2025 07:34 | 09090689000167-1-000006/2025; processo 00006/2025; PE 00004/2025 | Órgão, modalidade, datas, estimado/homologado | [C] |
| E-02 | Edital PE 04/2025 com ETP (anexo I) e TR | `https://pncp.gov.br/pncp-api/v1/orgaos/09090689000167/compras/2025/6/arquivos/1` | `…/09090689000167_2025_6/docs/01_edital.pdf` (56 p.); texto em `data/processed/etapa2_textos/` | publ. 30/01/2025 07:34:40 | "Edital Pregao Compras - Ampla Participacao.pdf" | Necessidade, método, dotações, restrições | [C] |
| E-03 | PNCP — itens | `https://pncp.gov.br/api/pncp/v1/orgaos/09090689000167/compras/2025/6/itens` | `…/09090689000167_2025_6/itens_p1.json` | atualização no PNCP | itens 1–334 | Quantidade, unidade, preço estimado | [C] |
| E-04 | PE 01/2024 (PNCP) e licitações 2024 (TCE-PB) | `…/compras/2024/1/itens`; `https://download.tce.pb.gov.br/dados-abertos/dados-por-municipio/170/licitacoes/licitacoes-2024.zip` | `…/09090689000167_2024_1/`; `data/raw/complementares/tcepb/170_santa_luzia_licitacoes-2024.zip` | publ. 12/01/2024; homol. 01/04/2024 | 09090689000167-1-000001/2024 | Plano anterior (349 itens) | [C]; PNCP incompleto |
| E-05 | PE 12/2024 — desconto sobre a CMED | `…/compras/2024/14/itens` e `/resultados` | `…/09090689000167_2024_14/` | publ. 21/03/2024 | 09090689000167-1-000014/2024 | Mecanismo alternativo vigente; descontos | [C] |
| E-05b | Termos aditivos de prorrogação (3) | `…/compras/2025/6/arquivos/12`, `/13`, `/14` | `…/09090689000167_2025_6/docs/12_aditivo.pdf` … `14_aditivo.pdf` | publ. 31/03/2026 | Contratos 00054/2025, 00056/2025, 00060/2025 | [PÓS] prorrogação até 12/03/2027 | [C] |
| E-06 | BPS 2024, 2025, 2026 (CSV) | `https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/BPS/csv/{ano}_csv.zip` | `data/raw/bps/` | arquivos de 20/11/2026 | filtro `dt_insercao ≤ 29/01/2025` | Referências de preço pré-decisão | [C]/[K] |
| E-07 | CMED — PMVG de 07/01/2025 | `https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/cmed/precos/arquivos/xls_conformidade_gov_20250107_175641971.xls/@@download/file` | `data/raw/complementares/cmed_pmvg_20250107.xls` | 07/01/2025 | lista "publicada em 06/01/2025", vigente na data de decisão | Teto regulatório; vínculo item → registro BPS pré-decisão → apresentação (`scripts/23_cmed_jan2025.py`) | [C]/[K] |
| E-08 | PNCP — resultados, contratos e pregões seguintes | `…/compras/2025/6/itens/{n}/resultados`; `https://pncp.gov.br/api/consulta/v1/contratos?cnpjOrgao=09090689000167&…`; compras `2025/99` e `2026/26` | `…/resultado_item_*.json`; `…/contratos_santa_luzia/contratos_pregoes_medicamentos.json` | 2025–2026 | contratos 09090689000167-2-000029/2025 a 000035/2025 | [PÓS] resultados | [C] |
| E-09 | Execução por contrato | cruzamento E-08 × E-10 (CNPJ do credor + nº da licitação) | `reports/caso_sl_execucao_contratos.csv` | até 31/08/2026 | — | [PÓS] taxa de execução | [K] |
| E-10 | TCE-PB/SAGRES — despesas | `https://download.tce.pb.gov.br/dados-abertos/dados-por-municipio/170/despesas/despesas-{2024,2025,2026}.zip` | `data/raw/complementares/tcepb/170_santa_luzia_despesas-*.zip` | 2024 – 31/08/2026 | subelemento "Material Farmacológico" + elemento 32 com "medicament" no histórico | Recurso realizado | [K] |
| E-11 | PNCP — PCA do município | `https://pncp.gov.br/api/pncp/v1/orgaos/09090689000167/pca/{2025,2026}/{1..}/itens` | — | — | sem itens | Planejamento anual | [A] |
| E-12 | BPS — registros de Santa Luzia | E-06, `no_municipio = SANTA LUZIA` (PB) | `reports/caso_sl_bps_santa_luzia.csv` | inseridos em 22/12/2025 | CNPJ 10.425.754/0001-47; processos 004/2025, 000252025, 78/2025 | Identificação de CATMAT; natureza do registro | [C]/[I] |
| E-13 | SES-PB/CEDMEX — "Medicamentos em desabastecimento" de 13/09/2024 | `https://paraiba.pb.gov.br/diretas/saude/cedmex/informativos/arquivos/Medicamentosemdesabastecimento13.09.24.pdf` | `…/ses_pb_cedmex_desabastecimento_2024-09-13_BLOQUEADO_captcha.html` | 13/09/2024 | — | Risco de fornecimento pré-decisão | [A] (CAPTCHA, não contornado) |
| E-14 | TCE-PB — "Preço de Referência" (guia de uso) | `https://precodereferencia.tce.pb.gov.br/ajuda/instrucoes-de-uso` | `data/raw/complementares/tcepb_precodereferencia_instrucoes.pdf` | — | — | Fonte regional, janela móvel de 12 meses | [C] |
| E-15 | IBGE — população estimada | `https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2024|2025/variaveis/9324?localidades=N6[2513406]` | `data/raw/complementares/ibge_pop_santa_luzia.json` | 2024/2025 | — | Porte | [C] |
| E-16 | Edital Fundação PB Saúde SF 22/2025 | `https://pncp.gov.br/pncp-api/v1/orgaos/38111778000140/compras/2025/13/arquivos/1` | `…/38111778000140_2025_13/docs/01_edital.zip` | assinado em 06/02/2025 | 38111778000140-1-000013/2025 | Comparação: método (média de 3 anos + 50%) | [C] |
| E-17 | HULW — ata e edital | `…/15126437000305/compras/2026/882/atas` e `/arquivos/1` | `…/15126437000305_2026_882/atas.json` | ata de 25/05/2026 | ata 00250/2026 | Comparação | [C] ata; [A] edital (HTTP 422) |
| E-18 | Edital Campina Grande PE 308/2025 | `…/08993917000146/compras/2025/159/arquivos/1` | `…/08993917000146_2025_159/docs/01_edital.zip` | publ. 21/07/2025 | 08993917000146-1-000159/2025 | Comparação | [C] digitalizado (pouco texto) |
| E-19 | Corte de 10 itens no MT | `…/compras/2025/159/itens/quantidade` (38); `…/compras/2025/6/itens/quantidade` (334) × MT (10) | saída em `LOG_ETAPA_2.md` | — | — | Correção da Etapa 1 | [C] |

## 2. Informação por categoria e status

| Informação | Status | Comentário |
|---|---|---|
| Medicamentos e especificações | [C] | 334 descrições do TR/PNCP |
| CATMAT dos itens | [K] 299/334 | Ausente no PNCP; recuperado via BPS posterior (só identidade do produto) |
| Quantidades necessárias | [C] estimativa do órgão | Consumo por item que a sustenta: [A] |
| Estoque na data de decisão | [A] | BNAFAR só oferece a posição atual (nov/2026; Etapa 1) |
| Orçamento da contratação | [C] estimativa R$ 4.952.438,00 | Saldo de dotação: [A] |
| Despesa realizada no ano anterior | [K] R$ 1.953.288,72 | Por licitação e credor; sem detalhe por item |
| Restrições operacionais | [C] | Armazenamento inadequado declarado; entrega rápida; validade |
| Restrições legais | [C] | Lei 14.133 (citada no edital); Portaria TCE-PB 138/2023 citada por outra candidata: [A] texto não localizado |
| Instrumentos vigentes | [C]/[I] | PE 12/2024 recebeu empenhos em 2025; vigência formal: [A] |
| Atas de outros órgãos para adesão | [A] | Não pesquisado item a item |
| Preços de referência pré-decisão | [K] BPS 285/334; [K] CMED 259/334 (provável) | CMED por embalagem; apresentação a conferir |
| Disponibilidade e desabastecimento de mercado | [A] | Lista estadual bloqueada por CAPTCHA |
| Prazos efetivos de entrega e rupturas | [A] | Não publicados |
| Consumo efetivo depois da decisão | [K] agregado | Execução por contrato; sem itens |

## 3. Lacunas essenciais e consequências

| Lacuna | Consequência para o experimento | Mitigação possível | O caso continua viável? |
|---|---|---|---|
| Consumo por item | Não dá para medir com precisão se a quantidade escolhida atende à demanda real | Usar a execução financeira por contrato como sinal agregado de uso; tratar a quantidade do TR como necessidade declarada (hipótese explícita) | Sim, com hipótese |
| Saldo de dotação | O limite orçamentário exato é desconhecido | Usar a estimativa da contratação e a despesa de 2024 como referências declaradas | Sim, com hipótese |
| Estoque inicial | Não dá para descontar o estoque existente | Declarar estoque inicial desconhecido; o agente deve tratar essa incerteza | Sim, com limitação |
| Preços de rotas não escolhidas (contrafactuais) | O resultado de alternativas não adotadas não é observável | Estimar por referências pré-decisão (BPS, CMED, descontos do PE 12/2024), com regras fixadas antes do experimento | Sim, como estimativa |
| Desabastecimento de mercado | Risco de fornecimento não quantificável ex ante | Usar a taxa histórica de itens fracassados/desertos (zero no caso; alta na PB Saúde) como proxy; rotular como hipótese | Parcial |
| CMED por embalagem e apresentação divergente | O teto não é diretamente comparável ao preço por unidade do item | Conferir apresentação e converter embalagem→unidade item a item, com regra documentada (259 itens vinculados) | Sim, com trabalho manual |
| PCA municipal | Sem planejamento anual formal publicado | Registrar a ausência; o ETP substitui parcialmente | Sim |

## 4. Achados de qualidade novos (afetam a Etapa 1)

1. **Medicamentos Transparentes corta em 10 itens por contratação** (CSV e JSON/OCDS). [C] E-19
2. **PNCP municipal sem CATMAT** em Santa Luzia (`catalogoCodigoItem` vazio nos 334 itens). [C]
3. **BPS registra o contrato inteiro na data de homologação** em Santa Luzia (315 registros com data 11/03/2025, R$ 2,92 mi, inseridos em 22/12/2025), não entregas. [C]/[I]
4. **PNCP com registros incompletos**: PE 01/2024 "em andamento" com valor estimado zerado, apesar de homologado no TCE-PB. Contrato 09090689000167-2-000249/2025 com valor 0. `valorGlobal` = 1/100 de `valorInicial` em 2 contratos. [C]
5. BPS 2024 tem `dt_insercao` mínima em 04/01/2021, anterior ao ano de compra (inconsistência). [C]
6. A API de consulta do PNCP exige janelas de até 365 dias e responde 504/500 em páginas altas. A API de termos aditivos devolveu 204 apesar de existirem aditivos em PDF. [C]
