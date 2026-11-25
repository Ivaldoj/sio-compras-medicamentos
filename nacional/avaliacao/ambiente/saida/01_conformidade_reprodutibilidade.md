# 01 — Conformidade do protocolo (A) e reprodutibilidade (B)

Legenda: **[OBS]** observado; **[CALC]** calculado (script indicado); **[INF]** inferido; **[HIP]** hipótese do avaliador.
Todos os scripts estão em `trabalho/` e rodam da raiz com `python -I -X utf8 trabalho/<script>.py`.

## A. Conformidade do protocolo: **adequado** (confiança alta)

### O que foi verificado

- **Integridade da decisão congelada.**
  - Os 45 arquivos de `hashes_ambiente_depois.csv` conferem com o conteúdo atual de `decisao_congelada/ambiente/`, e não há arquivo fora dessa lista [CALC: `trabalho/a01_transcricao.py`, bloco final].
  - Os 12 arquivos de `hashes_ambiente_antes.csv` (enunciado e pacote) têm o mesmo hash antes e depois: o decisor não alterou os dados [CALC].
- **Transcrição** (`decisao_congelada/registro/transcricao.jsonl`, 190 linhas):
  - 45 chamadas de ferramenta, entre 23:07 e 23:24 (UTC) de 25/11/2026: 32 Bash, 11 Write, 1 Read e 1 SubagentHandback. Modelo: `claude-opus-5-5` [CALC: `trabalho/a01_transcricao.py` → `trabalho/a01_chamadas.csv`].
  - Nenhuma chamada a WebFetch, WebSearch, Agent ou Task. Nenhum `curl`, `pip` ou URL [CALC: a01].
  - Todos os Bash começam com `cd` para a raiz do decisor ou para `data/decision_input_nacional`. A única leitura (Read) e as 11 escritas (Write) ficam em `trabalho/` ou `saida/` [OBS: a01_chamadas.csv].
  - Nenhuma referência a `dados_reservados`, `evaluation_only`, `evidencias_primarias` ou `codigo_preparacao` [CALC: a01].
- **Conhecimento posterior ao corte.**
  - As referências normativas nos entregáveis são o pacote (`restricoes.csv`) ou conhecimento anterior ao corte, marcado como [CP]: Lei 11.107/2005, art. 75, XII, da Lei 14.133 e Consórcio Nordeste (2019) [OBS: busca em `saida/*.md`].
  - O decisor declarou que **não** usou o índice CMED de 2025, a LOA 2025 nem resultados de licitações posteriores (D13, H12) [OBS: `registro_decisoes.csv`].
  - Não encontrei nenhum número ou fato posterior a 29/01/2025 nos entregáveis [INF: leitura integral dos `.md` e dos registros].

### Ocorrências menores (não comprometem a conformidade)

1. **Saídas gravadas fora da raiz pelo harness.** Duas saídas longas de comando (às 23:08:04 e às 23:10:34) foram gravadas fora da raiz, na pasta `tool-results` da sessão, pelo próprio harness. O decisor **não as abriu**, refez as consultas com saída reduzida e registrou o fato em `saida/registro_acessos.md` [OBS: a01_chamadas.csv, sinal `saida_persistida_fora`; `registro_acessos.md` §Integridade].
2. **`__pycache__` em `data/`.** O `import consulta` criou `data/decision_input_nacional/__pycache__/consulta.cpython-313.pyc`, que aparece em `hashes_ambiente_depois.csv`. É um subproduto automático do Python. Formalmente fere a regra "não modifique nada em `data/`", mas nenhum dado foi alterado [OBS].
3. **Contagem de unidades corrigida no próprio texto.** O decisor editou `01_diagnostico.md` com `sed`, depois da reexecução final, só para corrigir "7 itens" para "8 itens". Nenhum número calculado mudou [OBS: chamada das 23:23:57].

## B. Reprodutibilidade: **adequado** (confiança alta)

**Procedimento** [CALC: `trabalho/b01_reproduz.py` → `trabalho/b01_reproducao.csv`]:

1. Copiei `data/` e os seis scripts do decisor para `trabalho/repro/`, sem tocar em `decisao_congelada/`.
2. Executei a cadeia 00→05 com `python -I -X utf8`.
3. Comparei cada saída com a versão congelada.

**Resultado:**

| Saída | Resultado |
|---|---|
| `demanda_projecao.csv`, `demanda_uf_projecao.csv`, `elasticidade.csv`, `precos_referencia.csv`, `custos_item_estrategia.csv`, `mc_resumo.txt`, `sensibilidade.csv` | idênticas byte a byte |
| `saida/03_comparacao.csv`, `saida/plano_por_apresentacao.csv`, `registro_decisoes.csv`, `registro_hipoteses.csv` | idênticas byte a byte |
| `explora_cg_resumo.csv`, `explora_bps_resumo.csv` | mesmo conteúdo, ordem de linhas diferente: `GROUP BY ALL ... ORDER BY ap_id` não fixa a ordem dentro do item. Idênticas depois de ordenar |
| `02_precos_log.txt`, `03_estrategias_log.txt`, `explora_dlog.txt` | logs gerados por redirecionamento no terminal, fora dos scripts. Não reproduzíveis pelos scripts, mas não carregam números usados nos entregáveis |

- Todos os números dos entregáveis `.md` que conferi têm origem nesses arquivos. Ver `02_calculos.csv`.
- **Uma exceção:** "~751 mil frascos" de imunoglobulina em 2024 não sai de nenhum script. O pacote dá 703.302 (C20).
