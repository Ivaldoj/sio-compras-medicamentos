# Etapa 5 — Avaliação independente (índice)

- **Relatório e veredito:** `RELATORIO_ETAPA5.md`.
- **Cronologia, desvios do protocolo e hashes:** `LOG_ETAPA_5.md`, na raiz do projeto.
- **Protocolo:** `etapa5/PROTOCOLO_AVALIACAO.md` (pré-registrado; cópia em `ambiente_avaliador/`).

Nada foi alterado em `etapa4/`, `data/decision_input/`, `data/decision_input_v2/`, `data/evaluation_only/` nem em `etapa5/`. Esta etapa só escreve em `etapa5_avaliacao_independente/scripts/` e `resultados/`, além deste índice, do relatório e do log.

**Atenção:** `resultados/` contém dados posteriores ao corte. **Não deve ser fornecido a nenhum agente decisor.**

## Pastas

| Caminho | Conteúdo |
|---|---|
| `ambiente_avaliador/` | Entradas da avaliação, já existentes: decisão congelada, dados reservados, evidências primárias (PNCP, CMED, normas, TCE-PB) e protocolo |
| `scripts/` | Scripts desta etapa (`e5_*.py`) |
| `resultados/` | Saídas dos scripts |

## Scripts e saídas

| Script | O que faz | Saídas em `resultados/` |
|---|---|---|
| `e5_00_integridade.py` | Confere por sha256 os arquivos congelados, os pacotes, o protocolo e as cópias do ambiente do avaliador | `integridade_antes.csv`, `integridade_depois.csv` |
| `e5_01_reproducao.py` | Reexecuta os 6 scripts do agente em cópia temporária, sobre os pacotes v1 e v2, e compara com as saídas congeladas | `reproducao.csv`, `reproducao_custos_v1_v2.csv`, `reproducao_v2_diferencas.csv` |
| `e5_02_verificacao_calculos.py` | Recalcula com código próprio os números do agente (59 verificações) | `verificacao_calculos.csv`, `verificacao_referencias_item.csv` |
| `e5_03_expost.py` | Compara a decisão com o homologado, o mercado nacional posterior, o PE 09/2026, a competição e a execução | `expost_itens.csv`, `expost_resumo_grupos.csv`, `expost_totais.csv`, `expost_competicao.csv`, `expost_execucao_contratos.csv`, `expost_gasto_por_licitacao.csv`, `expost_gasto_mensal.csv`, `expost_escopo.csv`, `expost_numeros.json` |
| `e5_04_insulinas.py` | Evidências documentais, teto CMED pela lista bruta, mercado posterior, normas do MS e verificação das 4 falhas do pacote | `insulinas_evidencias_documentais.csv`, `insulinas_cmed_bruta.csv`, `insulinas_cmed_analogas.csv`, `insulinas_impacto.csv`, `insulinas_mercado_posterior.csv`, `insulinas_normas_ms.csv`, `insulinas_agente_x_evidencia.csv`, `falhas_pacote_verificacao_independente.csv`, `insulinas_numeros.json` |
| `e5_05_economia_sensibilidade.py` | Economia potencial, contratada e realizada; 17 cenários de sensibilidade; risco de deserto; teste do modelo de desconto | `economia_tres_niveis.csv`, `economia_execucao_por_contrato.csv`, `sensibilidade_recomendacao.csv`, `risco_deserto.csv`, `e2_teste_expost.csv`, `economia_numeros.json` |
| `e5_06_sintese.py` | Organiza as evidências de viabilidade e junta os números-chave | `viabilidade_evidencias.csv`, `resumo.json` |

## Como regerar

Da raiz do projeto, na ordem (o script 05 lê as saídas do 01, 03 e 04; o 06 lê todas):

```
python -I -X utf8 etapa5_avaliacao_independente/scripts/e5_00_integridade.py . antes
python -I -X utf8 etapa5_avaliacao_independente/scripts/e5_01_reproducao.py .
python -I -X utf8 etapa5_avaliacao_independente/scripts/e5_02_verificacao_calculos.py .
python -I -X utf8 etapa5_avaliacao_independente/scripts/e5_03_expost.py .
python -I -X utf8 etapa5_avaliacao_independente/scripts/e5_04_insulinas.py .
python -I -X utf8 etapa5_avaliacao_independente/scripts/e5_05_economia_sensibilidade.py .
python -I -X utf8 etapa5_avaliacao_independente/scripts/e5_06_sintese.py .
python -I -X utf8 etapa5_avaliacao_independente/scripts/e5_00_integridade.py . depois
```

- **Dependências:** pandas, pyarrow, duckdb, pypdf, xlrd e openpyxl (as do `requirements.txt`).
- **Ambiente usado:** Python 3.10.0, pandas 2.3.3, pyarrow 21.0.0 e duckdb 1.5.6, em ambiente virtual fora do projeto. Difere do ambiente original (Python 3.13.2, pandas 2.2.3, duckdb 2.0.1); mesmo assim os CSVs do agente saíram idênticos byte a byte.
- **Determinismo:** uma segunda execução completa produziu os mesmos 33 arquivos de `resultados/`, com sha256 idênticos.
- **Arquivos temporários:** a reprodução do agente roda em um diretório temporário do sistema e o apaga ao final. O texto extraído dos PDFs fica em cache no diretório temporário do sistema, com nome derivado do sha256 do PDF.

## Correspondência com o protocolo

| Protocolo | Onde está |
|---|---|
| A. Reprodutibilidade | `reproducao.csv`; relatório, seção 3.1 |
| B1–B8. Verificação dos cálculos | `verificacao_calculos.csv` (V01–V18); relatório, seção 3.2 |
| C1–C3. Preços e totais | `expost_itens.csv`, `expost_resumo_grupos.csv`, `expost_totais.csv`; seção 4.1 |
| C4. Homologado acima do teto | `expost_numeros.json`, `insulinas_impacto.csv`; seções 4.3 e 5 |
| C5. Risco de deserto | `risco_deserto.csv`; seção 6 |
| C6. Execução | `expost_execucao_contratos.csv`, `expost_gasto_por_licitacao.csv`; seção 4.4 |
| C7. Escopo | `expost_escopo.csv`; seção 4.5 |
| D. Viabilidade | `viabilidade_evidencias.csv`; seção 6 |
| E. Sensibilidade | `sensibilidade_recomendacao.csv`; seção 7 |
| F. Economia em três níveis | `economia_tres_niveis.csv`; seção 8 |
