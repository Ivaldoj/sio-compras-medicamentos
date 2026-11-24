# 21 — Objetivo do trabalho e como ler os documentos anteriores

24/11/2026. Nota de contextualização. **Nenhum documento anterior foi alterado**, com exceção do `README.md`, que foi reescrito como apresentação do projeto. Os registros experimentais, o enunciado, a decisão do agente e as avaliações ficam como foram escritos; esta nota diz como lê-los.

## 1. Objetivo do trabalho

**Demonstrar inteligência**, segundo a definição do professor Bellini adotada na disciplina: a **elaboração autônoma de cenários alternativos e a escolha do caminho mais eficiente**, em contraste com o **mero reconhecimento de padrões**.

O experimento verifica se um agente de IA, diante de um problema organizacional real e com as informações da data da decisão, elabora cenários, compara suas consequências e escolhe por um critério de eficiência, em vez de repetir o padrão que os dados sugerem.

**Não são objetivos do trabalho:**
- demonstrar superioridade da IA sobre gestores humanos;
- demonstrar execução autônoma de contratações;
- demonstrar economia efetivamente realizada.

A decisão real da prefeitura e os dados posteriores servem de régua para avaliar a qualidade da escolha experimental. O cenário escolhido pelo agente não foi implementado, por desenho: o experimento é uma simulação sobre um caso já encerrado.

O relatório que responde a esse objetivo é `etapa6/RELATORIO_FINAL.md`.

## 2. Por que esta nota existe

O objetivo acima orientou o trabalho desde o início, mas **não estava escrito em nenhum documento do repositório** até a revisão do relatório final. Cada etapa registrou o que fez, e algumas adotaram um enquadramento mais estreito ou diferente. Isso não invalida os registros; pede uma chave de leitura.

## 3. Documentos com enquadramento diferente

| Documento | O que diz | Como ler |
|---|---|---|
| `README.md`, versão anterior | Apresentava o projeto como "Auditoria de dados (Etapa 1)" e afirmava que nenhuma estratégia de compra havia sido formulada | Descrevia só a Etapa 1. Foi reescrito; o conteúdo de reprodução da Etapa 1 foi mantido |
| `docs/06_relatorio_viabilidade.md` | Trata da viabilidade dos dados para um projeto de "planejamento de compras com IA generativa" | Compatível. Avalia se os dados permitem montar o problema; não enuncia o objetivo |
| `docs/11_viabilidade_do_experimento.md` | Subtítulo: "comparar decisões e quantificar eficiência" | Compatível em parte. A comparação de decisões é o instrumento de medida, não o fim do trabalho |
| `etapa4/ambiente_decisor/ENUNCIADO.md` | Pede ao agente uma decisão de compra, sem mencionar inteligência nem a definição | Correto e intencional. O agente não deveria saber o que estava sendo testado. O enunciado exige pelo menos três estratégias e não fornece lista: é a operacionalização do objetivo |
| `etapa5/PROTOCOLO_AVALIACAO.md` | Avalia reprodutibilidade, cálculos, comparação ex post, viabilidade, sensibilidade e economia | Compatível. Mede a qualidade da escolha. Não tem uma dimensão para a elaboração de cenários; ela é examinada na seção 8 do relatório final |
| `docs/19` e `docs/20` | Listam como limitação o "contrafactual do E1": a estratégia não foi executada | Correto como limite da medida de eficiência. Não é falha do experimento |
| `etapa5_avaliacao_independente/RELATORIO_ETAPA5.md`, seções 1 e 10 | Responde à pergunta "o que o experimento demonstra sobre a capacidade da IA de tomar decisões organizacionais". Conclui que "não ficou demonstrado que a IA decide" e lista entre o que não ficou demonstrado a execução, a superação de um bom decisor humano e o funcionamento da estratégia | **Enquadramento incompatível com o objetivo.** A pergunta veio do pedido daquela etapa. As evidências e o veredito por dimensão valem; as frases que tratam a falta de execução ou de superioridade como algo "não demonstrado" respondem a perguntas que o trabalho não faz |
| `etapa5_avaliacao_independente/RELATORIO_ETAPA5.md`, seção 9, limitação 7 | "É uma recomendação com condições [...] a parte difícil ficou para a organização" | Mesma ressalva. Descreve o alcance do que foi produzido, não uma falha |
| `etapa6/RELATORIO_FINAL.md`, versão do commit `76456ab` | Título "Uma IA consegue decidir uma compra pública de medicamentos?"; resposta "em parte"; seção 8 com três leituras de "inteligência" (Simon; dado, informação e conhecimento; inteligência organizacional) | **Substituída** pela revisão de 24/11/2026, com a definição correta. A versão anterior fica no histórico |
| `LOG_ETAPA_5.md` e `LOG_ETAPA_6.md` | Registros cronológicos | Sem objetivo declarado. O `LOG_ETAPA_6.md` registra que a interpretação de "inteligência" estava "a confirmar"; foi confirmada nesta revisão |

Os demais documentos (`docs/01` a `05`, `07` a `10`, `12` a `18`, os outros logs e os arquivos de `etapa4/`) descrevem fontes, dados, preparação e execução, sem enunciar objetivo. Não precisam de ressalva.

## 4. O que não muda

- Nenhuma evidência, número ou resultado.
- As limitações metodológicas: uma execução, um caso, avaliação pela mesma família de modelos, comparação com o modelo de 2024 sem preço por item, vínculos sem validação humana.
- As três afirmações da Etapa 5 retiradas na Etapa 6 (insulinas de 2026) e a divergência sobre a errata E-05.
- A ressalva sobre a magnitude: a economia potencial de R$ 2,22 milhões segue superestimada.

## 5. Por que os originais não receberam notas no próprio arquivo

- Os arquivos de `etapa4/` e os resultados da Etapa 5 têm sha256 registrado nos logs, e os scripts de integridade os conferem. Qualquer edição quebraria essa verificação.
- O relatório da Etapa 5 é a avaliação original; alterá-lo depois de conhecido o objetivo comprometeria seu valor de registro.

Por isso a contextualização fica nesta nota, apontada pelo `README.md`.
