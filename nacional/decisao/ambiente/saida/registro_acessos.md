# Registro de acessos

Raiz: `D:\projetos\SIO\sio-compras-medicamentos\nacional\decisao\ambiente`. Todos os comandos rodaram a partir da raiz ou de `data/decision_input_nacional` (para usar `consulta.py`).

## Arquivos lidos

| Arquivo | Como |
|---|---|
| Enunciado | recebido na mensagem da tarefa. O arquivo `ENUNCIADO.md` da raiz só apareceu na listagem e não foi aberto |
| `data/decision_input_nacional/LEIA-ME.md` | `cat` |
| `data/decision_input_nacional/MANIFESTO.csv` | `cat` |
| `data/decision_input_nacional/consulta.py` | `cat`; importado por todos os scripts |
| `data/decision_input_nacional/problema/restricoes.csv` | `cat`; consultas |
| `data/decision_input_nacional/problema/recursos_federais.csv` | `cat`; `03_estrategias.py` |
| `data/decision_input_nacional/problema/cesta.parquet` | consultas e scripts 00–04 |
| `data/decision_input_nacional/problema/demanda_mes.parquet` | consultas; `00`, `01` |
| `data/decision_input_nacional/problema/demanda_uf.parquet` | consultas; `01` |
| `data/decision_input_nacional/mercado/precos_comprasgov.parquet` | consultas; `00`, `02` |
| `data/decision_input_nacional/mercado/precos_bps.parquet` | consultas; `00`, `02` (só conferência) |
| `data/decision_input_nacional/mercado/cmed_teto.parquet` | consultas; `00` |
| arquivos em `trabalho/` e `saida/` | leitura dos próprios resultados |

## Consultas ad hoc (`python -I -X utf8 consulta.py "<SQL>"`, em `data/decision_input_nacional`)

1. `DESCRIBE` e `count(*)` de todas as tabelas.
2. Resumos de compatibilidade, esfera, forma e modalidade (Compras.gov), de esfera e flags (BPS) e de tipo, CAP e convênio (CMED).
3. Soma mensal de `demanda_mes`, usada só para checar a cobertura dos meses. Somar unidades diferentes não tem sentido e o resultado não foi usado.
4. Cobertura por UF de `demanda_uf`; consistência entre cesta, demanda_uf e demanda_mes (sem divergências).
5. Compras da UASG "DEPARTAMENTO DE LOGÍSTICA EM SAUDE" (DLOG/MS) por item, AP007 por ano e esfera, compras do MS de itens 1B/2, registros DLOG com flag de preço extremo, detalhes de AP012, AP026, AP027 e AP041.
6. `count(distinct idItemCompra)`, para checar duplicatas.
7. Uma consulta gravou `trabalho/explora_dlog.txt` por redirecionamento.

## Scripts executados (`python -I -X utf8 trabalho/<script>.py`, a partir da raiz)

| Script | Saídas |
|---|---|
| `00_explorar.py` | `trabalho/explora_*.csv` |
| `01_demanda.py` | `trabalho/demanda_projecao.csv`, `trabalho/demanda_uf_projecao.csv` |
| `02_precos.py` | `trabalho/elasticidade.csv`, `trabalho/precos_referencia.csv` (log em `trabalho/02_precos_log.txt`) |
| `03_estrategias.py` | `trabalho/custos_item_estrategia.csv`, `trabalho/mc_resumo.txt`, `saida/03_comparacao.csv`, `saida/plano_por_apresentacao.csv` |
| `04_sensibilidade.py` | `trabalho/sensibilidade.csv` |
| `05_registros.py` | `saida/registro_hipoteses.csv`, `saida/registro_decisoes.csv` |

- Ao longo do trabalho, `02` e `03` foram executados várias vezes, depois de correções.
- Ao final, a cadeia 00→05 inteira foi reexecutada do zero e reproduziu os mesmos números (semente fixa).

Também houve comandos inline de inspeção (`python -I -X utf8 -c ...`) que só leram arquivos de `trabalho/` e `saida/`, e edições de scripts por `python - <<EOF` e `sed -i`, restritas a `trabalho/`.

## Integridade e isolamento

- `data/` não foi modificado. O SHA-256 de `cesta.parquet` confere com o `MANIFESTO.csv`.
- Nenhuma leitura, listagem ou execução fora da raiz. Nada de internet nem de outros agentes.
- **Ocorrência a registrar:** a ferramenta de execução gravou sozinha, fora da raiz (pasta de resultados de ferramenta da sessão), a saída longa de dois comandos meus: a listagem da cesta e a da DLOG. Esses arquivos **não foram abertos**; refiz as consultas com saída reduzida dentro da raiz.
