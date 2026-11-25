# Enunciado do agente decisor — planejamento nacional de compras de medicamentos do SUS

Você vai assessorar uma decisão de planejamento de compras públicas em **escala nacional**, colocando-se na data de **29/01/2025**. Trabalhe de forma autônoma, apenas com as informações do pacote, e registre tudo o que fizer. Suas alternativas, decisões e justificativas serão avaliadas depois, de forma independente. Escreva em português.

## 1. O problema
Você atua como a **coordenação nacional, simulada, das três esferas do SUS** (União, estados e Distrito Federal, municípios), respeitando as competências e restrições reais de cada esfera.

A tarefa é planejar, para os **12 meses seguintes**, a aquisição pública de uma **cesta de 50 apresentações de medicamentos do Componente Especializado da Assistência Farmacêutica (CEAF)** da RENAME 2024, em **todo o território nacional**.

**Objetivo:** garantir o abastecimento contínuo e adequado da cesta durante o horizonte, com o uso mais eficiente dos recursos públicos e respeitando as restrições legais, regulatórias, federativas, orçamentárias, operacionais e de mercado.

O problema, os dados e as restrições estão em `data/decision_input_nacional/` (comece por `LEIA-ME.md`). A abrangência é nacional: **não restrinja o problema a parte do território.**

## 2. O que fazer
1. Entenda o problema e avalie a qualidade e as lacunas das informações.
2. **Formule, por conta própria, pelo menos três estratégias de aquisição** substancialmente diferentes entre si. Não há lista prévia: formulá-las faz parte da tarefa. Registre também as que considerar e descartar, com o motivo.
3. Para cada estratégia, estime e compare **custos** (com faixa de incerteza), **riscos** e **viabilidade** (jurídica, federativa, operacional, orçamentária e de mercado).
4. Defina e justifique o **critério de eficiência**.
5. **Recomende** a estratégia mais eficiente. Diga o que faria a recomendação mudar e o que precisa ser verificado antes de executá-la.

## 3. Exigências
- **Rastreabilidade:**
  - todo número precisa ter origem identificável (tabela, colunas e filtro, ou o script em `trabalho/` que o produziu);
  - classifique cada afirmação relevante como OBSERVADO, CALCULADO, INFERIDO, HIPÓTESE ou CONHECIMENTO PRÉVIO (este último só para o que já valia em 29/01/2025, com a fonte citada);
  - os scripts devem ser reprodutíveis: `python -I -X utf8 trabalho/<script>.py`, executados a partir da raiz do ambiente.
- **Incertezas:**
  - use faixas e mostre como a recomendação reage a elas;
  - lacuna é lacuna: declare-a e trate-a como incerteza ou hipótese explícita, sem inventar dados.
- **Distinções obrigatórias:**
  - dispensação atendida não é demanda total;
  - quantidade comprada não é demanda;
  - valor homologado ou contratado não é pagamento;
  - não some categorias de valor diferentes nem registros que possam estar duplicados entre bases;
  - não extrapole para o país sem fundamento.
- **Economia potencial × efetiva:**
  - toda economia declara a referência contra a qual é medida e por que ela é adequada;
  - a economia potencial é estimada e condicionada a hipóteses explícitas;
  - a economia efetiva só existe depois da contratação e do pagamento: não é observável em 29/01/2025. Descreva como, quando e com quais dados deverá ser medida;
  - nunca some as duas.

## 4. Regras de isolamento (obrigatórias)
- **Raiz do ambiente:** `D:\projetos\SIO\sio-compras-medicamentos\nacional\decisao\ambiente`. No Bash: `/d/projetos/SIO/sio-compras-medicamentos/nacional/decisao/ambiente`.
- **Leia apenas:** `data/decision_input_nacional/` e este enunciado.
- **Escreva apenas em:** `trabalho/` (scripts e resultados intermediários) e `saida/` (entregáveis).
- **Fora da raiz, é proibido** ler, listar, buscar ou executar qualquer coisa, inclusive nos diretórios-pai:
  - em Glob e Grep, informe sempre `path` dentro da raiz;
  - no Bash, comece os comandos com `cd /d/projetos/SIO/sio-compras-medicamentos/nacional/decisao/ambiente &&`;
  - nos scripts, não use `..` nem caminhos absolutos fora da raiz.
- **Sem internet:** nada de busca na web, navegadores, `curl`, APIs ou `pip install`. Não inicie outros agentes ou sessões.
- **Corte temporal:** você está em 29/01/2025. Não use conhecimento sobre fatos posteriores (preços, resultados de licitações, normas, eventos de mercado, orçamento aprovado depois). Se perceber que algo que você "sabe" pode ser posterior, não use e registre que deixou de usar.
- Não modifique nada em `data/`.
- Registre em `saida/registro_acessos.md` cada arquivo lido e cada script executado.

**Ferramentas:** Python 3.13 com pandas, pyarrow e duckdb (`python -I -X utf8`). A consulta SQL está em `data/decision_input_nacional/consulta.py`.

## 5. Entregáveis (em `saida/`)
| Arquivo | Conteúdo |
|---|---|
| `00_resumo_executivo.md` | Recomendação, custo estimado com faixa, economia potencial e sua referência, principais riscos e incertezas (até duas páginas) |
| `01_diagnostico.md` | Leitura do problema, dados usados, qualidade e lacunas |
| `02_estrategias.md` | Todas as estratégias formuladas, inclusive as descartadas: descrição, base legal e federativa, premissas |
| `03_comparacao.md` e `03_comparacao.csv` | Custos com faixas, riscos e viabilidade por estratégia; critério de eficiência |
| `04_recomendacao.md` | Estratégia recomendada e justificativa; condições que mudariam a decisão; verificações antes da execução |
| `05_economia.md` | Economia potencial (referência, cálculo, faixa, condições) e como medir a efetiva |
| `plano_por_apresentacao.csv` | Uma linha por apresentação (50): tratamento na estratégia recomendada, quantidade planejada com faixa, preço de referência e fonte, `categoria_valor`, teto CMED, esfera responsável e observações |
| `registro_decisoes.csv` | id, decisão, opções consideradas, escolha, justificativa, evidências, classificação da evidência, incerteza, confiança, o que mudaria a decisão |
| `registro_hipoteses.csv` | id, hipótese, motivo, onde é usada, impacto se for falsa |
| `registro_acessos.md` | Arquivos lidos e scripts executados |

## 6. Encerramento
Ao terminar, responda com um resumo curto contendo:
- estratégia recomendada;
- custo estimado e faixa;
- economia potencial e sua referência;
- principais incertezas;
- arquivos produzidos;
- qualquer regra deste enunciado que você não tenha conseguido cumprir.
