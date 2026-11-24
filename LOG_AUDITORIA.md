# LOG da auditoria — Etapa 1

Registro de ações observáveis. Datas/horas: 22–23/11/2026 (UTC no `reports/manifest_fontes.csv`). Ambiente: Windows 11, Python 3.13.2, pandas 2.2.3, pyarrow 21.0.0, openpyxl 3.1.5 (já instalados; DuckDB ausente e **não instalado**). Disco D: 203 GB livres.

## 1. Ambiente e estrutura
- Criada a árvore `sio-compras-medicamentos/` (data/raw, samples, processed, docs, reports, scripts). Diretório `D:\projetos\SIO` estava vazio; nada preexistente foi alterado.
- Conectividade confirmada (HTTP 200 em medicamentos.transparencia.org.br).

## 2. BPS — verificação de tamanho e download
- `HEAD` em `2025_csv.zip` (3.865.116 B) e `2026_csv.zip` (1.612.728 B), `Last-Modified` 20/11/2026. Baixados com `scripts/02_download.py` (SHA-256 no manifest).
- Estrutura (`scripts/03_inspect_zip.py`): um CSV por ZIP, `;`, UTF-8, 34 colunas iguais nos dois anos; descompactados 23,1 MB e 10,1 MB → lidos inteiros em memória (adequado ao tamanho).
- Dicionário: API CKAN (`/api/3/action/package_show?id=bps`) → **404**. Recursos extraídos do HTML da página do dataset; baixado `Metadados_BPS_07_04_2026.pdf`. Anos 2020–2024: só HEAD (2,9–7,7 MB).

## 3. Medicamentos Transparentes
- HTML de `/dados-abertos` analisado (`scripts/00_inspect_html.py`) e o bundle JS da página: listagem em `GET https://medicamentos-api.transparencia.org.br/dados-abertos` com `sort`, `skip`, `take`, `custom_filters` (JSON).
- `GET /dados-abertos/bulk/download` → **HTTP 500** (ENOSPC no servidor). `/docs` → **502**.
- Comando de listagem (Git Bash):
  `curl -s -G 'https://medicamentos-api.transparencia.org.br/dados-abertos' --data-urlencode 'sort={"id":"ASC"}' --data-urlencode 'skip=0' --data-urlencode 'take=500' --data-urlencode 'custom_filters={}'` (+ `skip=500`). 571 registros → `listing_merged.json`.
- Erro inicial: PowerShell remove aspas de argumentos JSON (HTTP 400 "sort must be an object"); resolvido usando Git Bash.
- Formulário de download do site (nome/e-mail/finalidade) **não foi preenchido**.
- Download PB 2025-01..2026-09 (21 ZIPs CSV) e JSON 2026-01..2026-09 (9 ZIPs; o filtro `ano=2026 mes_max=9` trouxe todos os meses, não só setembro — só o de 2026-09 foi inspecionado).
- Download nacional de todos os meses iniciado em segundo plano e **interrompido pelo ambiente/usuário** após 113 arquivos; `.part` removido. Decisão: limitar a comparação nacional a jan–mar/2025 (argumento `mes_max` adicionado ao script). Falhas: `sp-3-2025` (timeout, baixado na 2ª tentativa) e `to-01-2025` (**404**, entrada duplicada da listagem).
- **Erro corrigido**: UFs grandes vêm em partes (`sp-1-2025-1/…`); a 1ª versão do `06_profile_transparencia.py` criava tabelas separadas por parte. Regex corrigida, parquet nacional regenerado. A análise de PB não foi afetada (PB não tem partes — verificado).

## 4. Perfis e análises
- `04_profile_bps.py` → `reports/perfil_colunas_bps.csv`, `bps_*.csv`, `data/processed/bps_2025_2026.parquet`; saída em `reports/bps_profile_stdout.txt`.
- `05_bps_checks.py` → outliers, PB, duplicidades (`reports/bps_checks_stdout.txt`).
- `06/07_*` → tabelas OCDS PB, análise (`reports/mt_pb_analise_stdout.txt`). Erro de codificação do console (cp1252) — `-I` ignora `PYTHONIOENCODING`; resolvido com `-X utf8`.
- `08_mt_cobertura_nacional.py` → `reports/mt_cobertura_uf_2025T1.csv`.

## 5. Integração
- `09_integracao_bps_mt.py` (níveis N1–N4 e N1b/N3b) → `reports/integracao_bps_mt_pb.csv`, `integracao_exemplos_bps_mt_pb.csv`, `integracao_stdout.txt`. Corrigido erro de formatação (`%` literal).
- `14_rastreio_mt_pncp.py`: amostra de 20 (semente 42). 1ª execução: 9 ok, 11 **HTTP 429**. Adicionados cache e pausa de 3 s; 2ª execução: 14 ok, 6 ainda 429 — **não insistido** para não forçar o limite.
- `13_cmed_pmvg.py`: lista PMVG (13,6 MB) baixada; 1ª aba é só cabeçalho; dados na aba "Lista PMVG". Corrigido falso positivo (registro vazio casava com vazio). Um `Set-Content` do PowerShell corrompeu acentos do script; arquivo reescrito em UTF-8.

## 6. PNCP
- Sondas com `curl` (respostas em `data/raw/pncp/`): compra, itens, resultados, arquivos da compra 08778268000160-1-000559/2026 (200); contratos SES-PB 1º tri/2026 (200); atas (204); `pca/consolidado` (404); `/v1/pca/usuario?idUsuario=1` (204).
- `10_pncp_pca.py`: PCA SES-PB 2026, sequenciais 1–60 → 40 com itens, 2.497 itens. `11_pca_farmaco.py`: itens farmacológicos → linha agregada 33903009.

## 7. Fontes complementares
- `dadosabertos.saude.gov.br` CKAN `package_search` → 404 (bnafar, horus, estoque, dispensação, siops).
- `apidadosabertos.saude.gov.br/static/swagger.json` (137 endpoints) → encontrados `/daf/estoque-medicamentos-bnafar-horus` e `/economia-da-saude/bps`.
- BNAFAR: `offset` ≥ 1000 devolve vazio (testado); passou-se a usar `limit=50000`. Campina Grande (250400) 2.464 linhas; João Pessoa (250750) 1.776. Histórico (`anomes_posicao_estoque=202506`, `data_posicao_estoque=2026-06-30`) → lista vazia. Linhas iniciais do manifest para `bnafar_250400_20.json` (argumento vazio perdido pelo PowerShell) e a versão de 1.000 linhas estão **superadas** (arquivos removidos/substituídos).
- TCE-PB: URL dos arquivos extraída do bundle JS do portal; `despesas-2025.zip` e `licitacoes-2025.zip` de Salgadinho (cód. 164) baixados; consolidados estaduais só HEAD (192/181 MB, não baixados por proporcionalidade). `12_tcepb_despesas.py`: 1ª versão filtrou o subelemento pelo código errado (coluna `codigo_subelemento_exibicao` traz o nome) — corrigido.
- CMED: página de preços → link da lista PMVG de 09/11/2026. Anvisa `dados.anvisa.gov.br/dados/` listado (não baixado).

## 8. Relatórios
- `15_build_reports.py` → `reports/inventario_arquivos.csv` (todos os brutos com SHA-256), `perfil_colunas.csv`, `estatisticas_bases.csv`.
- `reports/matriz_integracao.csv` montada a partir dos resultados dos testes.
- Docs 01–06 e README escritos com números copiados das saídas dos scripts.

## 9. Nova tentativa (23/11/2026, a pedido do usuário)
- Listagem do MT refeita (`listing_merged_v2.json`): mesmos 571 registros; URLs assinadas inalteradas (`X-Amz-Date` 22/11 17:30 UTC, válidas por 24 h).
- Download nacional em primeiro plano: **446 novos**, 122 já existentes (pulados), 3 falhas **HTTP 404** — `df/df-02-2024`, `go-02-2024`, `to-01-2025` (ids 649–651, publicados em 04/02/2026). Segunda verificação confirmou que os objetos não existem no bucket (o HEAD com URL assinada para GET devolve 403 e não serve como teste). Total: 568 de 571 ZIPs CSV, 84,9 MB.
- Integridade: 577 ZIPs (568 CSV + 9 JSON) testados com `zipfile.testzip()`; nenhum corrompido.
- `14_rastreio_mt_pncp.py` ganhou função `fetch` com espera progressiva em 429 (respeita `Retry-After`). As 6 consultas pendentes responderam na **1ª tentativa** → 20/20 com mesmo órgão e valor estimado.
- `08_mt_cobertura_nacional.py` reescrito para ler direto dos ZIPs só `releases` e `ten_items` (colunas mínimas), cobrindo o período completo: 86.068 ocids únicos, 324.999 itens; saídas `reports/mt_cobertura_uf.csv`, `mt_cobertura_uf_mes.csv`, `mt_cobertura_uf_2025T1.csv`, `mt_cobertura_nacional_stdout.txt`.
- Removidos os parquet derivados `data/processed/mt_*_28ufs.parquet` (misturavam PB completo com o 1º trimestre das demais UFs; nenhum script os usa mais). Dados brutos intactos.
- `15_build_reports.py` passou a incluir as estatísticas nacionais do MT; inventário regenerado (694 arquivos brutos, 127,6 MB).

## Decisões metodológicas
- BPS: medicamentos = `co_classe` 6505; comparações de preço só por CATMAT + `un_fornecimento`; nenhuma linha removida (duplicatas e outliers só marcados/descritos).
- MT: deduplicação por `ocid` / `ocid`+item; coleta mais recente para valores.
- Integração BPS↔MT só considerada confirmada no nível N4.
- Sem estatística amostral apresentada como populacional. Recorte nacional do MT: período completo para cobertura (desde 23/11); adjudicações e preços só na PB.

## Dados não obtidos / pendências
- Consumo/dispensação e histórico de estoque (não localizados em dados abertos).
- Execução orçamentária estadual (Portal da Transparência PB não extraído).
- 3 arquivos do MT inexistentes na fonte (404). ~~MT nacional completo; 6 rastreios PNCP~~ — resolvidos em 23/11 (seção 9).
- Significado de `validade_compra`, `vl_capacidade`, sufixo `U00xx` do BNAFAR, UF `EX`.
- Textos normativos não baixados; RENAME não consultada.
