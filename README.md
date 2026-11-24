# Auditoria de dados — Planejamento de Compras de Medicamentos pelo SUS (Etapa 1)

Disciplina Sistemas de Informação nas Organizações (SIO) — UFPB. Esta etapa é **só** aquisição, exploração, qualidade, integração e suficiência dos dados. Nenhuma estratégia de compra foi formulada.

**Leia primeiro:** [`docs/06_relatorio_viabilidade.md`](docs/06_relatorio_viabilidade.md) — classificação final **B (viável com complementações e hipóteses explícitas)**.

## Estrutura

```
data/raw/            arquivos originais, sem modificação (hash em reports/inventario_arquivos.csv)
  bps/               BPS 2025 e 2026 (CSV zip) + dicionário PDF
  transparencia/     Medicamentos Transparentes: listagem da API + ZIPs por UF (todas as UFs, 2025-01..2026-09; 568 de 571)
  pncp/              respostas da API do PNCP (compras, itens, resultados, contratos, PCA, rastreio)
  ms_api/            estoque BNAFAR/Hórus (API de Dados Abertos do MS)
  complementares/    CMED PMVG, TCE-PB, páginas HTML consultadas
data/processed/      parquet derivados (BPS tipado; tabelas OCDS do MT)
data/samples/        extratos pequenos (itens farmacológicos do PCA da SES-PB)
docs/01..06          fontes, dicionário, qualidade, integração, lacunas, viabilidade
reports/             CSVs gerados por script + saídas de console (*_stdout.txt)
scripts/             scripts numerados na ordem de execução
LOG_AUDITORIA.md     registro cronológico
```

## Fontes

Medicamentos Transparentes (Transparência Brasil), Banco de Preços em Saúde (MS), PNCP, API de Dados Abertos do MS (BNAFAR/Hórus), TCE-PB (SAGRES), CMED/Anvisa. URLs e estado de acesso em [`docs/01_fontes.md`](docs/01_fontes.md); downloads com data, URL e SHA-256 em `reports/manifest_fontes.csv`.

## Reproduzir

Requisitos: Python 3.13, `pip install -r requirements.txt`, acesso à internet. Rode da raiz do projeto (`-I` isola o interpretador; `-X utf8` evita erro de codificação no console do Windows):

```powershell
python -I -X utf8 scripts\02_download.py url https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/BPS/csv/2025_csv.zip data\raw\bps\2025_csv.zip "BPS/MS"
python -I -X utf8 scripts\02_download.py url https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/BPS/csv/2026_csv.zip data\raw\bps\2026_csv.zip "BPS/MS"
python -I -X utf8 scripts\04_profile_bps.py .
python -I -X utf8 scripts\05_bps_checks.py .
```

Medicamentos Transparentes (as URLs da listagem expiram em 24 h; gere uma nova listagem antes — comando `curl` no `LOG_AUDITORIA.md`, passo 3):

```powershell
python -I -X utf8 scripts\01_transparencia_listing.py data\raw\transparencia\listing_merged.json reports\transparencia_listagem_arquivos.csv
python -I -X utf8 scripts\02_download.py transparencia data\raw\transparencia\listing_merged.json PB csv
python -I -X utf8 scripts\02_download.py transparencia data\raw\transparencia\listing_merged_v2.json all csv
python -I -X utf8 scripts\06_profile_transparencia.py . PB --perfil
python -I -X utf8 scripts\07_analyze_transparencia.py . PB
```

Demais (na ordem): `08_mt_cobertura_nacional.py .` (lê direto dos ZIPs), `09_integracao_bps_mt.py .`, `10_pncp_pca.py . 08778268000160 2026 60`, `11_pca_farmaco.py . 08778268000160 2026`, `12_tcepb_despesas.py . <zip> Salgadinho`, `13_cmed_pmvg.py . <xlsx>`, `14_rastreio_mt_pncp.py . 20`, `16_bnafar_estoque.py . <ibge6> "" 1`, `15_build_reports.py .` (por último). Cada script documenta parâmetros no cabeçalho. Os scripts não sobrescrevem arquivos brutos já existentes.

## Avisos

- Somas do BPS são dominadas por valores impossíveis; use medianas por CATMAT + unidade.
- BPS e Medicamentos Transparentes **não** devem ser somados nem unidos por transação.
- Dados pessoais presentes nas fontes (credores pessoa física no TCE-PB, contatos no BNAFAR) não foram usados nos relatórios.
