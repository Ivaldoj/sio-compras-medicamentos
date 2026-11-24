# 01 — Fontes consultadas

Data de acesso de todas as fontes: **22/11/2026** (horários UTC no `reports/manifest_fontes.csv`).
Legenda de estado: **Processado** (baixado e analisado) · **Baixado** (preservado, análise parcial) · **Consultado** (página/endpoint verificado, sem download integral) · **Falhou** (erro documentado).

## 1. Medicamentos Transparentes — Transparência Brasil (fonte prioritária 1)

| Item | Achado |
|---|---|
| Página | https://medicamentos.transparencia.org.br/dados-abertos |
| Distribuição | Página Next.js que consome a API `https://medicamentos-api.transparencia.org.br/`. A listagem de arquivos vem de `GET /dados-abertos?sort={...}&skip=&take=&custom_filters={...}` (parâmetros JSON). A própria página aponta para a documentação Swagger desse endpoint (`/docs#/DadosAbertos/DadosAbertosController_findAll`), mas **`/docs` respondeu HTTP 502** e `/docs-json` não devolveu especificação. |
| Arquivos | Um registro por UF × mês/ano de coleta, cada um com dois ZIPs (CSV e JSON/OCDS) em S3 (`medicamentos-transparentes-dados-abertos.s3.sa-east-1.amazonaws.com/<uf>-<mes>-<ano>-csv.zip`). As URLs entregues pela API são **pré-assinadas e expiram em 24 h**; o projeto grava apenas a URL sem assinatura. |
| Formulário | O botão de download do site abre um formulário (nome, e-mail, finalidade) enviado a `/mail/download-open-data-request`. **Não foi preenchido**; os arquivos foram obtidos pela listagem pública da API, que é o mesmo caminho usado pela página e documentado por ela. |
| Download em lote | `GET /dados-abertos/bulk/download` → **HTTP 500** `"ENOSPC: no space left on device"` (falha do servidor). |
| Cobertura (listagem completa, 571 registros) | 27 UFs com coletas **2025-01 a 2026-09** (21 meses); DF e GO têm também 2024-02; um código `EX` com uma coleta (2026-09), sem documentação (provavelmente exterior — **não confirmado**). SC aparece completa na listagem final. |
| Anomalias da listagem | TO 2025-01 aparece duas vezes; uma das URLs (`to-01-2025-csv.zip`) dá **HTTP 404**. |
| Estrutura do CSV | Não são 3 arquivos: cada ZIP traz **13 tabelas OCDS achatadas** (`releases`, `ten_items`, `ten_lots`, `ten_ite_activeIngredients`, `ten_ite_attributes`, `ten_lot_sustainability`, `awards`, `awa_items`, `awa_suppliers`, `awa_ite_deliveryLocations`, `parties`, `par_additionalIdentifiers`, `par_det_classifications`). UFs grandes vêm divididas em partes (`sp-3-2025-1..7`). Vírgula como separador, UTF-8. |
| Baixado | **568 dos 571 ZIPs CSV** listados (todas as UFs, 2025-01..2026-09; 84,9 MB) + 9 JSON/OCDS da PB (2026-01..2026-09; só a estrutura do de 2026-09 foi inspecionada). Todos os 577 ZIPs passaram em `zipfile.testzip()`. |
| Não obtidos | 3 entradas da listagem (ids 649–651, publicadas em 04/02/2026, com mês de dois dígitos no nome): `df/df-02-2024`, `go-02-2024`, `to-01-2025` → **HTTP 404** em duas tentativas (22 e 23/11/2026). O objeto não existe no bucket; para TO 2025-01 existe a versão `to-1-2025`. As únicas coletas de 2024 (DF e GO) ficam, portanto, indisponíveis. |
| Estado | **Processado**: PB completo (todas as tabelas); nacional completo para cobertura (`releases` e `ten_items`). |
| Licença | Rodapé com ícone Creative Commons (`/vectors/cc.svg`); variante da licença **não confirmada**. |
| Atualização | Campo `data_publicacao` por arquivo; o mais recente é o de 2026-09. |

## 2. Banco de Preços em Saúde — Ministério da Saúde (fonte prioritária 2)

| Item | Achado |
|---|---|
| Catálogo | https://dadosabertos.saude.gov.br/dataset/bps (a API CKAN `/api/3/action/...` respondeu **HTTP 404**; recursos lidos da página HTML) |
| Recursos | CSV, JSON e XML anuais de 2020 a 2026 + `Metadados_BPS_07_04_2026.pdf`. Página: "Última atualização em Novembro/2026"; arquivos com `Last-Modified: 20/11/2026`. |
| Baixados | `2025_csv.zip` (3.865.116 bytes), `2026_csv.zip` (1.612.728 bytes), `Metadados_BPS_07_04_2026.pdf`. Tamanhos verificados por HEAD antes do download. Anos 2020–2024 só tiveram o tamanho verificado (2,9–7,7 MB cada). |
| Formato | Um CSV por ZIP, `;`, UTF-8 sem BOM, campos entre aspas, datas `dd/mm/aaaa`, decimais com ponto. |
| Dicionário oficial | PDF de 07/04/2026: periodicidade **semestral**, cobertura "Nacional", texto de cobertura temporal "2º semestre de 2025" (desatualizado em relação aos arquivos), autor COGPS/CGCUSTOS/DESID/SE/MS. Descreve ~20 campos; **não descreve** `ds_esfera`, `co_pdm`, `no_pdm`, `co_classe`, `nu_processo_compra`, `nu_ata`, `validade_compra`, `ds_observacao`, `co_seq_bps`. Diz que o BPS registra compras "públicas e privadas". |
| Obrigatoriedade | Página institucional (https://www.gov.br/saude/pt-br/acesso-a-informacao/banco-de-precos): a CIT estabeleceu que o registro das compras de medicamentos é obrigatório para União, Estados, Municípios e DF. |
| API alternativa | `https://apidadosabertos.saude.gov.br/economia-da-saude/bps` (exige `codigoCatmat` ou `cnpjInstituicao`; testada: HTTP 400 sem esses filtros). |
| Licença | Portal: Creative Commons Atribuição-SemDerivações 3.0. |
| Estado | **Processado** (2025 e 2026 integrais). |

## 3. PNCP — Portal Nacional de Contratações Públicas

| Endpoint (base `https://pncp.gov.br/api`) | Teste | Resultado |
|---|---|---|
| `/consulta/v1/orgaos/{cnpj}/compras/{ano}/{seq}` | SES-PB 2026/559 e amostra de 20 do MT | 200; **20 de 20** recuperados (6 bloqueados por HTTP 429 em 22/11, obtidos na nova tentativa de 23/11 com pausa de 3 s e espera progressiva) |
| `/pncp/v1/orgaos/{cnpj}/compras/{ano}/{seq}/itens` | SES-PB 2026/559 | 200 (item, quantidade, valor unitário estimado, situação) |
| `/pncp/v1/orgaos/{cnpj}/compras/{ano}/{seq}/itens/{n}/resultados` | idem | 200 (fornecedor, quantidade/valor homologados, data do resultado) |
| `/pncp/v1/orgaos/{cnpj}/compras/{ano}/{seq}/arquivos` | idem | 200 (lista de documentos) |
| `/consulta/v1/contratacoes/publicacao` | SES-PB, set/2026, modalidade 6 | 200 |
| `/consulta/v1/contratos` | SES-PB, 1º tri/2026 | 200 |
| `/consulta/v1/atas` | SES-PB, 1º tri/2026 | 204 (sem conteúdo para o filtro) |
| `/pncp/v1/orgaos/{cnpj}/pca/{ano}/{seq}/itens` | SES-PB 2026, seq. 1–60 | 200; 40 PCAs (unidades), 2.497 itens |
| `/consulta/v1/orgaos/{cnpj}/pca/{ano}/consolidado` | SES-PB 2026 | 404 |

Especificação: `/consulta/v3/api-docs` (preservada em `data/raw/pncp/openapi_consulta.json`). Estado: **Consultado** (amostras), PCA da SES-PB **Processado**.

## 4. Fontes complementares

| Fonte | URL | O que permite conhecer | Estado |
|---|---|---|---|
| Estoque BNAFAR/Hórus (MS) | `https://apidadosabertos.saude.gov.br/daf/estoque-medicamentos-bnafar-horus` | Posição de estoque por estabelecimento (CNES), CATMAT (`BR0…`), lote, validade, quantidade, programa | **Processado** para Campina Grande (2.464 linhas) e João Pessoa (1.776). Só a posição atual (18/11/2026); consultas com `anomes_posicao_estoque=202506` e `data_posicao_estoque=2026-06-30` devolveram lista vazia. Paginação por `offset` ≥ 1000 devolve vazio; usar `limit` alto. |
| TCE-PB — Dados Abertos (SAGRES) | `https://download.tce.pb.gov.br/dados-abertos/dados-por-municipio/{cod}/despesas/despesas-{ano}.zip` | Empenhos municipais com valor empenhado, liquidado e pago, função, elemento/subelemento ("MATERIAL FARMACOLÓGICO"), credor (CNPJ), fonte de recurso, nº da licitação | **Processado** para Salgadinho 2025; consolidado estadual 2025 (192 MB) e 2026 (181 MB) só verificado por HEAD |
| TCE-PB licitações | `.../licitacoes/licitacoes-{ano}.zip` | Licitações municipais, propostas e situação | **Baixado** (Salgadinho 2025) |
| CMED/Anvisa — Lista PMVG | https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/cmed/precos (arquivo publicado em 09/11/2026) | Preço Fábrica e Preço Máximo de Venda ao Governo por apresentação, alíquota de ICMS, CAP, restrição hospitalar | **Processado** (26.694 apresentações) |
| Anvisa dados abertos | https://dados.anvisa.gov.br/dados/ | `DADOS_ABERTOS_MEDICAMENTOS.csv`, `TA_PRECO_MEDICAMENTO_GOV.csv`, `TA_RESTRICAO_MEDICAMENTO.csv` e dicionários | **Consultado** (listagem) |
| Portal da Transparência PB | https://transparencia.pb.gov.br/ | Execução orçamentária estadual (potencial para a SES-PB) | **Consultado** (página responde; dados não extraídos) |
| Dados abertos PB | https://dados.pb.gov.br/ | Catálogo estadual | **Consultado** (página responde) |

## 5. Fontes normativas identificadas (relevância, sem interpretação jurídica)

> Os textos normativos **não foram baixados nem conferidos** nesta etapa; a lista indica onde procurar. As citações da CMED vêm do cabeçalho da própria lista PMVG baixada.

| Norma/fonte | Relevância para a etapa decisória |
|---|---|
| Lei nº 14.133/2021 | Base das contratações (modalidades, dispensa, SRP, PCA — art. 12, VII; pesquisa de preços — art. 23). Os dados do PNCP/MT já trazem o amparo legal por contratação. |
| Decreto nº 11.462/2023 | Regulamenta o Sistema de Registro de Preços (atas, vigência, adesões). |
| Decreto nº 10.947/2022 | Regulamenta o Plano de Contratações Anual no âmbito federal (referência para o PCA do PNCP). |
| Resolução CMED nº 3/2011 e Resoluções CTE-CMED (ex.: nº 1/2026 citada na lista) | CAP e PMVG: teto de preço para vendas à administração pública. |
| Resolução CMED nº 2/2004 e nº 2/2019 | Regime de preços regulados/liberados (citadas no cabeçalho da lista CMED). |
| Pactuação CIT sobre alimentação do BPS | Obrigatoriedade de registro das compras (citada na página do BPS; número da resolução não verificado). |
| RENAME (Relação Nacional de Medicamentos Essenciais) | Delimita o elenco de medicamentos do SUS e responsabilidades de financiamento — **não consultada** nesta etapa. |

## 6. Fontes não localizadas ou não acessadas

- **Consumo/dispensação** por estabelecimento em dados abertos: não localizado (a API do MS expõe só estoque).
- **Histórico de estoque**: não disponível pelos parâmetros testados.
- **Orçamento por medicamento**: não existe nas fontes vistas; só agregados (subelemento de despesa, linha agregada no PCA).
- **Situações de desabastecimento**: não investigado em profundidade (a Anvisa publica descontinuações — arquivo não localizado na listagem de `dados.anvisa.gov.br`).
- **Portal da Transparência federal**: exige chave de API; não usado.
