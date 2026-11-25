# 02 — Precisão dos cálculos (dimensão C): **parcialmente adequado** (confiança alta)

Detalhe por verificação em `saida/02_calculos.csv` (31 linhas), gerado por `trabalho/c01_calculos.py`. O script reexecuta o Monte Carlo do decisor numa cópia (`trabalho/repro/`) para as checagens por sorteio.

## Resumo

| Resultado | Quantas | Itens |
|---|---|---|
| Confere | 26 | totais E1–E4, economias, %, betas, razão DLOG/estadual, contagens, tetos, categorias, BPS/CG, sensibilidade |
| Parcial | 4 | C10 ordenação "em todos os percentis"; C20 "~751 mil frascos"; C23 dispersão de AP052; C31 unidade de AP012/AP052 |
| Não confere | 1 | C14 ponto de equilíbrio do risco de fracasso |

## Erros e imprecisões registrados (os arquivos do decisor não foram corrigidos)

### 1. C14: ponto de equilíbrio do risco de fracasso (erro conceitual, de sentido conservador)

O decisor declara que a economia de E2 só se anula com probabilidade de fracasso do certame acima de ~41% (`mc_resumo.txt`, `03_comparacao.md` §3, `04_recomendacao.md`).

- **Como ele calcula:** `pf = eco2 / (eco2 + extra_falha)` (`03_estrategias.py`), onde `extra_falha = Q·s·(p75 − p_E1·f_nac)` [OBS].
- **Por que está errado:** `extra_falha` já contém a perda da economia (p_E1·(1−f)) mais o prêmio emergencial (p75 − p_E1). O custo esperado de E2 é C_E2 + p·extra, então a economia esperada é eco2 − p·extra. Ela zera em p* = eco2/extra.
- **Valores no MC reproduzido** [CALC: c01]:
  - fórmula do decisor: 0,413;
  - fórmula correta: **0,704**.
- **Efeito:** o erro subestima a robustez de E2 e não altera a recomendação.

### 2. C10: "a ordenação E2<E3<E4<E1 vale em todos os percentis"

- O decisor compara percentis marginais. Com números aleatórios comuns, o teste certo é por sorteio pareado.
- **Por sorteio pareado** [CALC: c01]:
  - E2<E3 em 99,5% dos sorteios;
  - E3<E4 em **86,2%**;
  - E4<E1 em 100%.
- A afirmação vale para E2 contra os demais, mas não para E3 contra E4.

### 3. C20: "MS compra ~751 mil frascos/ano de imunoglobulina (2024)"

- O pacote soma **703.302 frascos** em compras DLOG de 2024, contando por data de compra ou de resultado (6,4% a menos) [CALC: c01 e inspeção inline].
- O número não entra em nenhum cálculo de custo.

### 4. C23: mesalazina 500 mg (AP052)

- Os números conferem (p25 1,84; p75 4,50), mas a leitura está errada:
  - o decisor apresenta a amplitude como heterogeneidade entre compradores (`01_diagnostico.md` §3);
  - na verdade, o pacote mistura no item **21 registros de supositório / "uso retal"** (CATMAT 352414). A regra de compatibilidade do pacote aceita `SUPOSITÓRIO` como unidade de item sólido (`codigo_preparacao/n03_pacote_nacional.py`, `UN_SOLIDA`).
- **Efeito na referência E1 de AP052:** a mediana estadual de 24 meses cai de **3,815 para 2,470** sem esses registros [CALC: `trabalho/p01_pacote.py` → `trabalho/p01_ap052.csv`].
- **Efeito na economia determinística de E2** (s=0,55): cai de 203 para 197 milhões [CALC: `trabalho/f01_sensibilidade.py`, cenário "P do decisor com AP052 corrigido"].
- É uma falha do pacote, não detectada pelo decisor.

## Pontos que conferem e merecem registro

- **Totais e faixas:** E1 6.475 (5.930–7.185); E2 6.255 (5.731–6.935); economia 221 (159–298); regime pleno 405 (337–483). São idênticos [CALC: C01–C05].
- **Regime pleno** é declarado como referência e **não somado** à economia do horizonte (correto) [OBS].
- **Categorias de valor** [OBS: C29, inspeção de `02_precos.py` e `03_estrategias.py`]:
  - custo = Q × min(preço homologado × índice, teto CMED). O teto entra só como limite;
  - o valor SIA 1B (R$ 777 mi) e a execução da ação 4705 aparecem só em `mc_resumo.txt`, rotulados como de outra categoria, sem soma;
  - o BPS só entra em medianas de conferência.
- **Teto CMED:**
  - nenhum preço de referência nem limite superior de faixa passa do teto aplicável (C25);
  - os tetos por unidade do pacote conferem com a lista CMED primária em 411 das 411 apresentações [CALC: `p01_pacote.py` §6];
  - só AP054 (azatioprina, R$ 0,79) fica acima do **menor** teto 0% ICMS entre os produtos vinculados (R$ 0,51), mas abaixo do teto do produto mais caro. O decisor usa o maior teto entre produtos, o que é aceitável para uma referência de mercado, mas não garante a conformidade de cada contratação [CALC: C25].
- **Duplicidades:**
  - `idItemCompra` é único (5.447/5.447);
  - nenhum CATMAT está vinculado a mais de uma apresentação (C30);
  - BPS e Compras.gov não são somados.
- **Unidades:** o preço por unidade de dispensação é coerente com a quantidade SIA nos itens inspecionados. As exceções são AP012 (CATMAT de 90 mg/mL para a apresentação de 45 mg, tratado pelo decisor com o preço DLOG) e AP052 (não tratado) [INF: C31].

## Avaliação

Os cálculos são reprodutíveis e, quase todos, aritmeticamente corretos. As categorias de valor e os tetos foram respeitados. A nota é "parcialmente adequado" por três motivos:

1. o ponto de equilíbrio está errado;
2. a frase sobre a ordenação "em todos os percentis" é exagerada para E3 contra E4;
3. a referência de AP052 está contaminada sem que o decisor percebesse.

Nenhum desses erros inverte a recomendação [CALC: `05_sensibilidade.md`].
