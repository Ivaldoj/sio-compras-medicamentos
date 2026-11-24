# LOG — Etapa 6 (consolidação e conclusões)

24/11/2026. Relatório final em `etapa6/RELATORIO_FINAL.md`. **O experimento não foi reexecutado**: nenhum script do agente nem das avaliações anteriores foi rodado nesta etapa.

## 1. O que foi feito
- Lidos, pela primeira vez por esta sessão, `docs/19`, `docs/20` e os resultados de `etapa5/avaliacao/`, `avaliacao_canetas/` e `verificacao/`.
- `etapa6/scripts/e6_01_confronto.py` (somente leitura): integridade, confronto de 25 indicadores e ida às fontes primárias para as duas divergências.
- Integridade: 143 de 143 arquivos conferem (ambiente do decisor, resultados da Etapa 5 independente e saídas da pré-Etapa 5 com hash registrado).

## 2. Divergências resolvidas
| Divergência | Quem estava certo | Evidência |
|---|---|---|
| Coluna de ICMS 20% da CMED para o Convênio 87/02 | Avaliação independente (Etapa 5) | `cmed_pmvg_20250107.xls`: 2.810 de 2.810 células "PF 20%" são texto com asterisco; nenhuma vazia. A conversão numérica em `scripts/23_cmed_jan2025.py` (linha 23) as descartou; a frase "0 de 2.810" em `scripts/31_verifica_falhas_pacote_v2.py` (linha 180) é texto fixo |
| Preço de R$ 29,00 do PE 09/2026 como preço de caneta | Preparação (doc 20) | Ata Final do PE 09/2026, p. 26: "5 REFIL 3ML S/CANETA NOVOLIN N penfil" e "NOVOLIN R" |

## 3. Afirmações da Etapa 5 retiradas (o arquivo original não foi alterado)
Em `etapa5_avaliacao_independente/RELATORIO_ETAPA5.md`:
1. Seções 1, 5.4 e 6: o mesmo comprador teria homologado "a caneta" a R$ 29,00 em 2026.
2. Seção 5.4: "Risco real" de deserto, na parte apoiada nesse preço.
3. Seção 5.4: custo das insulinas "aos preços de 2026" (R$ 235.335) e a conclusão de que a referência do agente ficou 27% abaixo do mercado posterior.
Também rebaixado a contexto: a comparação com 309 itens do PE 09/2026 (seção 4.1), por falta de conferência do produto ofertado.
O resumo rápido dado ao usuário na conversa repetia a afirmação 1 e também está errado nesse ponto.

## 4. Pendências, sem alteração de arquivos
- Errata E-05 do pacote v2: a causa descrita ("fonte, não falha") está incorreta. Correção só em nova versão do pacote.
- "Inteligência" no enunciado da etapa foi interpretada em três sentidos (seção 8 do relatório); a confirmar com o autor.

## 5. Hashes (sha256)
```
f2ff336641a49f593e39a130bd08ea499bf692916d9a13317e082beb5a3e8044  etapa6/RELATORIO_FINAL.md
8a76df02a5b0766ee67b94ebe0ff69be5ae95c73cab3792e0eeb9d8043ec5282  etapa6/scripts/e6_01_confronto.py
547d96eb456b6db9170e58166a1531fa656af08babb7714bfbbc79c487ab7fb1  etapa6/resultados/confronto_numeros.csv
a7219fd76f6c15df11d6ebd33ac414fc974a78aaf2eda859e10e64a1a2518d7a  etapa6/resultados/confronto_numeros.json
9bf1dfd69b2949ee676730ecaf82e7ea7c0b791ac34d8764e212e7745aed2562  etapa6/resultados/divergencia_cmed_icms_celulas.csv
5f0e88d1785161d94183d13211d3794628a6bc195b63d9c317c577b6983fd185  etapa6/resultados/divergencia_cmed_icms_exemplos.csv
e3c2f3ab42b798df95993688b9f74d5edafa07008061fc1d8803de25b4bd8ddf  etapa6/resultados/divergencia_insulinas_2026.csv
633bbfe26f6509887095851a238bc161296ea102e7f41e7edb4fa835cd2f8659  etapa6/resultados/insulinas_quadro_corrigido.csv
e901fc321fdfcaff852875402fc52e80e81c624a670f31322d2d5fdf4e9ef685  etapa6/resultados/integridade.csv
```
