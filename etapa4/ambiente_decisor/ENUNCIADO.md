# Etapa 4 — Enunciado para o agente decisor

Você vai assessorar uma decisão de compra pública, colocando-se na data de **29/01/2025**. Trabalhe de forma autônoma, apenas com as informações descritas abaixo, e registre tudo o que fizer. Suas alternativas, decisões e justificativas serão avaliadas depois, de forma independente. Escreva em português.

## 1. O problema

A Secretaria Municipal de Saúde de **Santa Luzia (Paraíba)** precisa abastecer por **12 meses** a Assistência Farmacêutica municipal. O Estudo Técnico Preliminar e o Termo de Referência, assinados em 29/01/2025, listam **334 itens** de medicamentos, com quantidades anuais estimadas e valor estimado total de **R$ 4.952.438,00**. A forma de aquisição ainda não foi decidida.

**Objetivo organizacional:** garantir o suprimento contínuo e adequado dos 334 itens durante 12 meses, usando os recursos públicos com eficiência e respeitando as restrições legais, regulatórias e operacionais.

**Restrições registradas** (`data/decision_input/organizacional/restricoes.csv`):
- Lei 14.133/2021 (modalidades, dispensa, registro de preços, garantias, contratos, sanções).
- Registro na Anvisa, salvo isenção legal.
- Validade mínima de 75% da vida útil ou mais de 365 dias na entrega (orientação do TCE-PB).
- A administração não possui local adequado para armazenamento de medicamentos.
- Entrega no endereço da Secretaria Municipal de Saúde.
- Teto CMED nas vendas ao governo: PMVG para produtos com CAP; PF nos demais.
- Alíquota de ICMS do teto CMED para Santa Luzia/PB: 0% para isentos e produtos do Convênio ICMS 87/02; 20% nos demais.
- A necessidade inclui itens fora da RENAME.

**Recursos registrados** (`data/decision_input/organizacional/recursos.csv`): valor estimado da necessidade; dotações e fontes orçamentárias; repasses federais do SUS recebidos em 2024; população. O saldo das dotações e o estoque inicial são **desconhecidos**.

Os arquivos são a referência: em caso de diferença entre este resumo e o pacote, vale o pacote.

## 2. O que fazer

1. Entenda a necessidade e avalie a qualidade e as lacunas das informações disponíveis.
2. Formule, por conta própria, **pelo menos três estratégias de aquisição** substancialmente diferentes entre si. Não há lista prévia de alternativas: formulá-las faz parte da tarefa. Registre também as que considerar e descartar, com o motivo.
3. Para cada estratégia, estime e compare **custos** (com faixa de incerteza), **riscos** e **viabilidade** (jurídica, operacional, orçamentária e de mercado), considerando as restrições do pacote.
4. Defina e justifique o critério de eficiência usado na comparação.
5. **Recomende** a estratégia mais eficiente. Diga o que faria a recomendação mudar e o que precisa ser verificado antes de executá-la.

## 3. Exigências

### 3.1 Justificativas rastreáveis
- Todo número deve ter origem identificável: arquivo ou tabela, colunas e filtro; ou o script em `trabalho/` que o produziu e a saída correspondente.
- Classifique cada afirmação relevante como:
  - **OBSERVADO**: lido do pacote;
  - **CALCULADO**: produzido por script seu;
  - **INFERIDO**: raciocínio sobre dados observados ou calculados;
  - **HIPÓTESE**: premissa adotada por você, com justificativa;
  - **CONHECIMENTO PRÉVIO**: conhecimento seu, externo ao pacote (por exemplo, legislação). Cite a norma ou fonte e use apenas o que já valia em 29/01/2025.
- Os scripts devem ser reprodutíveis: `python -I -X utf8 trabalho/<script>.py`, executados a partir da raiz do ambiente.

### 3.2 Incertezas explícitas
- Trate explicitamente as incertezas, no mínimo as listadas na seção 4 do `LEIA-ME.md`, e as que você identificar.
- Use faixas, não só valores pontuais, e mostre como a recomendação reage a elas.
- Não preencha lacunas com dados inventados. Lacuna é lacuna: declare-a e trate-a como incerteza ou como hipótese explícita.

### 3.3 Economia potencial × economia efetiva
- Toda economia deve declarar a referência contra a qual é medida e por que essa referência é adequada.
- **Economia potencial:** diferença estimada na data de decisão, condicionada a hipóteses explícitas.
- **Economia efetiva:** só existe depois da contratação e da execução (preço efetivamente contratado × quantidade efetivamente adquirida e entregue, comparados à mesma referência). Ela não é observável em 29/01/2025: não a apresente como resultado. Descreva como, quando e com quais dados ela deverá ser medida.
- Nunca some as duas nem apresente economia potencial como certa.

### 3.4 Pontos que exigem tratamento específico e separado
- **Insulinas.** Identifique as insulinas da necessidade e trate cada uma separadamente: apresentação exigida, referências de preço disponíveis e suas limitações, teto regulatório, peso no valor total e consequências da decisão para elas.
- **Preços "a conferir".** Não os use como preço do item sem tratamento explícito. Diga como os tratou e como a conclusão muda se forem, ou não, compatíveis com o item.
- **Estimativas acima do teto regulatório.** Identifique os itens cuja estimativa do órgão supera o teto CMED aplicável e explique como isso afeta o valor de referência, a economia calculada e a conformidade da contratação.
- **Bloqueios do pacote.** Vínculos `incompativel`, `indeterminada` e `provavel_conferencia` e grupos sem compatibilidade comprovada não podem ser usados como preço nem como teto do item.

## 4. Regras de isolamento (obrigatórias)

- **Raiz do ambiente:** `D:\projetos\SIO\sio-compras-medicamentos\etapa4\ambiente_decisor`. No Bash: `/d/projetos/SIO/sio-compras-medicamentos/etapa4/ambiente_decisor`.
- **Leia apenas:**
  - `data/decision_input/`: o pacote e sua documentação (`LEIA-ME.md`, `MANIFESTO.csv`, `MANIFESTO.json`);
  - `scripts/consulta_agente.py`;
  - este enunciado.
- **Escreva apenas em:**
  - `trabalho/`: scripts, consultas e resultados intermediários;
  - `saida/`: entregáveis.
- **Fora da raiz do ambiente, é proibido** ler, listar, buscar ou executar qualquer coisa, inclusive nos diretórios-pai e em outras pastas do projeto. Para isso:
  - em Glob e Grep, informe sempre `path` dentro da raiz do ambiente;
  - no Bash, comece os comandos com `cd /d/projetos/SIO/sio-compras-medicamentos/etapa4/ambiente_decisor &&` e use caminhos relativos a ela;
  - nos scripts, não use `..` nem caminhos absolutos fora da raiz.
- **Sem internet:** não use busca na web, navegadores, `curl`, APIs, `pip install` nem outro acesso externo. Não inicie outros agentes ou sessões.
- **Corte temporal:** você está em 29/01/2025.
  - Não use conhecimento sobre fatos posteriores: preços, resultados de licitações, normas, eventos de mercado, inclusive sobre este caso.
  - Se perceber que algo que você "sabe" pode ser posterior, não use e registre que deixou de usar.
- Não modifique nada em `data/` nem em `scripts/`.
- Registre em `saida/registro_acessos.md` cada arquivo lido e cada script executado.

## 5. Ferramentas

- **Python:** Python 3.13 com pandas, pyarrow e duckdb. Execute com `python -I -X utf8`.
- **`scripts/consulta_agente.py`:** abre as tabelas e visões do pacote no DuckDB (seção 6 do `LEIA-ME.md`).
  - Em Python:
    ```python
    import sys; sys.path.insert(0, "scripts"); import consulta_agente as q
    con = q.conectar()
    ```
  - Na linha de comando: `python -I -X utf8 scripts/consulta_agente.py "<SQL>"`.
  - Esquemas: use `DESCRIBE <tabela>`.

## 6. Entregáveis (em `saida/`)

| Arquivo | Conteúdo |
|---|---|
| `00_resumo_executivo.md` | Em até duas páginas: recomendação, custo estimado com faixa, economia potencial e sua referência, principais riscos e incertezas. |
| `01_diagnostico.md` | Leitura do problema; dados usados; qualidade e lacunas. |
| `02_alternativas.md` | Todas as estratégias formuladas, inclusive as descartadas. Para cada uma: descrição, base legal ou procedimental e premissas. |
| `03_comparacao.md` e `03_comparacao.csv` | Por estratégia: custos com faixas, riscos, viabilidade e o critério de eficiência. |
| `04_recomendacao.md` | Estratégia recomendada e justificativa; condições que mudariam a decisão; verificações necessárias antes da execução. |
| `05_itens_criticos.md` | Insulinas, preços a conferir e estimativas acima do teto (seção 3.4). |
| `06_economia.md` | Economia potencial (referência, cálculo, faixa e condições) e como a economia efetiva deverá ser medida. |
| `plano_por_item.csv` | Uma linha por item (334), com: o tratamento do item na estratégia recomendada; o preço de referência unitário adotado, sua fonte e `categoria_valor`; o teto CMED unitário aplicável; a faixa de preço considerada; as sinalizações (a conferir, acima do teto, sem referência); e observação. |
| `registro_decisoes.csv` | Uma linha por decisão relevante: id, decisão, opções consideradas, escolha, justificativa, evidências (arquivo, consulta ou script), classificação da evidência (seção 3.1), incerteza, confiança e o que mudaria a decisão. |
| `registro_hipoteses.csv` | id, hipótese, motivo, onde é usada e impacto se for falsa. |
| `registro_acessos.md` | Arquivos lidos e scripts executados. |

Scripts e resultados intermediários ficam em `trabalho/`.

## 7. Encerramento

Ao terminar, responda com um resumo curto contendo:
- estratégia recomendada;
- custo estimado e faixa;
- economia potencial e sua referência;
- principais incertezas;
- arquivos produzidos;
- qualquer regra deste enunciado que você não tenha conseguido cumprir.
