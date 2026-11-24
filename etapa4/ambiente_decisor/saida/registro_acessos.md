# Registro de acessos

Raiz: `D:\projetos\SIO\sio-compras-medicamentos\etapa4\ambiente_decisor`. Todos os comandos Bash começaram com `cd /d/projetos/SIO/sio-compras-medicamentos/etapa4/ambiente_decisor &&` e usaram caminhos relativos a ela. Não houve uso de Glob, Grep, internet, `pip` ou outros agentes. Nada foi escrito em `data/` ou `scripts/`.

## 1. Listagens de diretório (só dentro da raiz)

- `ls -la` em `.`, `data`, `data/decision_input`, `scripts`, `trabalho` e `saida`. A saída de `ls -la` mostra a entrada `../` (metadados da própria entrada de diretório). O conteúdo do diretório-pai não foi listado nem lido.
- `find data -type f`
- `ls -la saida trabalho`, para conferir os entregáveis.

## 2. Arquivos lidos diretamente

| Arquivo | Como |
|---|---|
| Enunciado da Etapa 4 | recebido na mensagem da tarefa. O arquivo `ENUNCIADO.md` da raiz apareceu na listagem, mas não foi aberto |
| `data/decision_input/LEIA-ME.md` | `cat` |
| `data/decision_input/MANIFESTO.csv` | `cat` |
| `data/decision_input/MANIFESTO.json` | `cat` |
| `scripts/consulta_agente.py` | `cat` |
| `data/decision_input/organizacional/restricoes.csv` | `cat` |
| `data/decision_input/organizacional/recursos.csv` | `cat` |
| `data/decision_input/organizacional/execucao_farmaco_2024_mensal.csv` | `cat` |
| `data/decision_input/organizacional/execucao_farmaco_2024_por_licitacao.csv` | `cat` |
| `data/decision_input/organizacional/receitas_sus_2024.csv` | `head -5`; depois via DuckDB |

## 3. Arquivos lidos via `scripts/consulta_agente.py` (DuckDB)

Todas as tabelas de `TABELAS` e as visões de `VISOES` foram abertas por `q.conectar()`: `itens`, `restricoes`, `recursos`, `execucao_2024_mensal`, `execucao_2024_licitacao`, `historico_proprio`, `bps`, `cmed_apresentacoes`, `cmed_precos`, `pncp_contratacoes`, `pncp_itens`, `pncp_resultados`, `item_catmat`, `item_cmed`, `item_bps_grupos`, `regras_conversao`, `comprasgov`, `item_comprasgov`, `item_catmat_oficial`, `receitas_sus_2024` e as visões `v_*`. Arquivos correspondentes: os parquet e csv de `data/decision_input/{organizacional,nacional,padronizacao}/`.

## 4. Scripts executados (`python -I -X utf8 <script>`, a partir da raiz)

| Script | Saída | Finalidade |
|---|---|---|
| `trabalho/00_esquemas.py` | `trabalho/00_esquemas.txt` | esquemas e contagens. A 1ª execução falhou por API do DuckDB e o script foi corrigido |
| `trabalho/01_explora_itens.py` | `trabalho/01_explora_itens.txt` | status e valores da necessidade |
| `trabalho/02_explora_historico.py` | `trabalho/02_explora_historico.txt` | pregões próprios, receitas, insulinas |
| `trabalho/03_insulinas_detalhe.py` | `trabalho/03_insulinas_detalhe.txt` | vínculos, tetos e preços das insulinas |
| `trabalho/04_explora_precos.py` | `trabalho/04_explora_precos.txt` | fontes de preço, CMED, status |
| `trabalho/05_insulinas_catmat.py` | `trabalho/05_insulinas_catmat.txt` | CATMAT das canetas; vínculo com ERRO |
| `trabalho/06_explora_complementos.py` | `trabalho/06_explora_complementos.txt` | tipos de preço CMED, PNCP/SRP, quantidades 2025 × 2024 |
| `trabalho/07_checa_teto.py` | `trabalho/07_checa_teto.txt` | cálculo do teto pelo pacote; vínculos COM ALERTA |
| `trabalho/10_referencias.py` | `trabalho/ref_itens.csv`, `trabalho/10_referencias.txt` | **referências por item** (rodado várias vezes durante os refinamentos; a versão final é a do arquivo) |
| `trabalho/11_inspeciona_ref.py` | `trabalho/11_inspeciona_ref.txt` | inspeção: sobre-estimação, itens sem referência, razão teto/mercado |
| `trabalho/13_cmed_convenio.py` | `trabalho/13_cmed_convenio.txt` | colunas de ICMS dos produtos do Convênio 87/02 |
| `trabalho/20_estrategias.py` | `trabalho/20_estrategias.txt`, `custos_estrategias.csv`, `demanda.csv`, `sensibilidades.csv`, `e2_e3_por_item.csv` | **custos por estratégia, sensibilidades** |
| `trabalho/21_e2_diagnostico.py` | `trabalho/21_e2_diagnostico.txt` | robustez da diferença E2 − E1 |
| `trabalho/30_saidas.py` | `saida/plano_por_item.csv`, `saida/03_comparacao.csv`, `trabalho/30_itens_criticos.txt` | entregáveis tabulares e itens críticos |
| `trabalho/40_numeros_texto.py` | `trabalho/40_numeros_texto.txt` | números derivados citados nos textos |
| `trabalho/50_registros.py` | `saida/registro_decisoes.csv`, `saida/registro_hipoteses.csv` | registros de decisões e hipóteses |

Ordem para reproduzir: 10 → 20 → 21 → 30 → 40 → 50. Os scripts 00–07, 11 e 13 são exploratórios e independentes.

### Execuções avulsas (exploração, sem gerar números próprios)

- `python -I -X utf8 scripts/consulta_agente.py "<SQL>"`, duas consultas:
  - registros BPS e Compras.gov.br dos CATMAT 440255, 442012 e 468664, com saída salva em `trabalho/12_insulina_catmat_precos.txt`;
  - linhas CMED dos registros 1176600040099 e 1176600030115, replicadas depois em `trabalho/13_cmed_convenio.py`.
- `python -I -X utf8 -c "..."` e `python -I -X utf8 -` (stdin) para:
  - inspecionar `trabalho/ref_itens.csv` e `saida/plano_por_item.csv`; os números usados nos textos foram reproduzidos nos scripts 11, 20, 30 e 40;
  - aplicar edições programáticas nos scripts `10_referencias.py` e `20_estrategias.py`;
  - edições com `sed` em `trabalho/30_saidas.py`, `trabalho/50_registros.py`, `saida/01_diagnostico.md` e `saida/02_alternativas.md`.

## 5. Arquivos gerados pelo harness fora da raiz

A ferramenta de execução salvou automaticamente três saídas longas de comandos meus em arquivos de resultado da própria sessão. Essas cópias não foram abertas: as mesmas saídas foram lidas a partir de `trabalho/` (`03_insulinas_detalhe.txt`, `05_insulinas_catmat.txt`, `11_inspeciona_ref.txt`).

## 6. Conhecimento prévio usado (externo ao pacote, vigente em 29/01/2025)

| Item | Uso |
|---|---|
| Lei 14.133/2021 (arts. 6º XLV, 23 §1º I/II/IV, 28 I, 33 I–II, 34, 40, 55 I a, 74, 75 II/VIII §1º, 79, 82–86, 125, 187) | modalidades, referência de preço, SRP, adesão, dispensa, prazos |
| LC 123/2006, arts. 47–49 | ME/EPP |
| Súmula TCU 247 | adjudicação por item |
| Lei 10.742/2003 e normas CMED (PF como teto; PMVG e CAP) | teto regulatório; reajuste anual |
| Portaria de Consolidação GM/MS nº 6/2017 (financiamento da AF; insulinas humanas de aquisição centralizada; CEAF) | insulinas (**a verificar**) |
| Lei 14.770/2023 (alteração do art. 86, §3º) | adesão a atas municipais (**a verificar**) |
| Decreto 12.343/2024 (valores de 2025, dispensa ~R$ 62,7 mil) | descarte da dispensa (**a verificar**; a conclusão não depende do valor exato) |

**Deixei de usar:** o percentual do reajuste CMED de 2025 e qualquer resultado do PE 04/2025 ou de eventos posteriores a 29/01/2025. Nenhuma informação desse tipo foi usada.
