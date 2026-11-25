# Registro de acessos do avaliador

**Raiz:** `D:\projetos\SIO\sio-compras-medicamentos\nacional\avaliacao\ambiente`.

- Todos os comandos rodaram a partir da raiz.
- Nenhuma leitura, listagem ou busca fora da raiz.
- Nada foi escrito em `decisao_congelada/`. Os 45 hashes do estado "depois" continuam conferindo (`trabalho/a01_transcricao.py`).
- Nenhum outro agente ou sessão foi iniciado.

## Arquivos lidos

| Arquivo | Como |
|---|---|
| `ENUNCIADO_AVALIACAO.md`, `PROTOCOLO_AVALIACAO_NACIONAL.md` | `cat` |
| `decisao_congelada/ambiente/ENUNCIADO.md`; `data/decision_input_nacional/LEIA-ME.md`, `MANIFESTO.csv`, `consulta.py`, `problema/*.csv` | `cat` |
| `decisao_congelada/ambiente/data/decision_input_nacional/problema/*.parquet`, `mercado/*.parquet` | DuckDB/pandas (consultas inline e scripts do avaliador) |
| `decisao_congelada/ambiente/saida/*` (todos os 11 entregáveis do decisor) | `cat`/`head` |
| `decisao_congelada/ambiente/trabalho/*.py`, `02_precos_log.txt`, `03_estrategias_log.txt`, `mc_resumo.txt`, `sensibilidade.csv`; demais CSVs pelos scripts | `cat`; scripts |
| `decisao_congelada/registro/transcricao.jsonl`, `hashes_ambiente_antes.csv`, `hashes_ambiente_depois.csv` | `head`; `a01_transcricao.py` |
| `dados_reservados/LEIA-ME.md`, `*.parquet`, `orcamento_acoes_af_2025.csv`, `orcamento_acoes_af_2026.csv` | `cat`; DuckDB; scripts e01–e03 e f01 |
| `evidencias_primarias/sia_tabnet/*.html` | `trabalho/tabnet.py` (via e01) e inspeção de cabeçalho/rodapé |
| `evidencias_primarias/comprasgov_precos/apresentacao_catmat.csv` | `head`; c01 (os JSON por CATMAT não foram abertos: o pacote e os reservados já os consolidam) |
| `evidencias_primarias/cmed/cmed_pmvg_20250107.xls` | pandas/xlrd (p01) |
| `evidencias_primarias/orcamento/orcamento_despesa_2024.zip` (lido); `_2025.zip` (só listado) | p01; `unzip -l` |
| `evidencias_primarias/rename/relacao_nacional_medicamentos_2024_2ed.pdf` | `pdftotext -layout` → `trabalho/rename2024.txt` (d01) |
| `codigo_preparacao/n03_pacote_nacional.py` (lido integralmente); os demais só listados (`wc -l`) | `cat` |

## Scripts executados (`python -I -X utf8 trabalho/<script>.py`, a partir da raiz, nesta ordem)

| Script | Função | Saídas |
|---|---|---|
| `a01_transcricao.py` | auditoria da transcrição e dos hashes (dimensão A) | `trabalho/a01_chamadas.csv` |
| `b01_reproduz.py` | reexecuta os scripts do decisor numa cópia e compara as saídas (B) | `trabalho/repro/`, `trabalho/b01_reproducao.csv` |
| `p01_pacote.py` | qualidade do pacote | `trabalho/p01_pacote.txt`, `trabalho/p01_ap052.csv` |
| `d01_rename.py` | grupos de financiamento na RENAME 2024 | `trabalho/rename2024.txt`, `trabalho/d01_rename_trechos.txt` |
| `d02_beta_por_item.py` | uniformidade de preço e β por item (D) | `trabalho/d02_beta_por_item.csv` |
| `c01_calculos.py` | verificação dos números (C); requer `repro/` | `saida/02_calculos.csv` |
| `e01_demanda.py` | E1 quantidade (usa `tabnet.py`) | `trabalho/e01_demanda.csv` |
| `e02_precos.py` | E2 preços | `trabalho/e02_precos.csv` |
| `e03_custo_orcamento.py` | E3 custo e E4 orçamento | `trabalho/e03_custo.csv`, `e03_custo_totais.csv`, `e04_orcamento.csv` |
| `f01_sensibilidade.py` | F: β pós-corte, economia com valores observados, ponto de equilíbrio; requer `repro/`, e01, e02 e p01 | `trabalho/f01_*.csv` |
| `w01_ex_post_csv.py` | monta a tabela ex post | `saida/04_comparacao_ex_post.csv` |
| `w02_registro_evidencias.py` | registro de evidências | `saida/registro_evidencias.csv` |

- **Ordem mínima para reproduzir tudo:** b01 → p01 → d01 → d02 → c01 → e01 → e02 → e03 → f01 → w01 → w02 (a01 é independente).
- **Comandos inline de inspeção:** `python -I -X utf8 -c ...` e consultas DuckDB, só leitura. Por exemplo: esquemas das tabelas, compras DLOG pré e pós por item, AP027/AP034/AP052 por UF e mês, BPS pós-corte e o arquivo `trabalho/c00_catmat_por_item.txt` (CATMAT × unidade por item).
- **Arquivo auxiliar:** `trabalho/tabnet.py`, leitor do HTML do TabNet, importado por e01.

## Acessos web (só normas oficiais)

| Data | URL | Finalidade |
|---|---|---|
| 25/11/2026 | https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/decreto/d11462.htm | Decreto 11.462/2023: art. 2º (incisos III, IV, VI, VII), art. 7º, V, e art. 33 |
| 25/11/2026 | https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14133.htm (duas leituras: início e trecho a partir do caractere 100.000) | Lei 14.133/2021: art. 75, XII, e art. 86, caput e §§7º e 8º |

Nenhum relatório ou análise de terceiros foi consultado.

## Regras não cumpridas ou cumpridas com ressalva

- **Avisos do ambiente:** apareceram mensagens sobre um servidor MCP externo (GitHub) com falha de conexão. Não o usei.
- **Pasta `trabalho/repro/`:** contém uma cópia de `data/decision_input_nacional/`, necessária para reproduzir os scripts do decisor sem escrever em `decisao_congelada/`.
- **Duas edições pontuais** em scripts meus, feitas com `sed` e Python inline: ajuste de um merge em e01 e inclusão do filtro de supositório em e02. Os scripts finais rodam do zero.
- **Avaliação jurídica:** conferi só o texto normativo, sem jurisprudência.
