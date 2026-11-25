# Decisões metodológicas — experimento nacional

Registro cumulativo. Cada decisão traz a data, a origem (aprovação dos coordenadores ou decisão técnica tomada na execução) e o motivo. **As decisões não são reescritas:** quando uma muda, uma nova entrada a substitui e referencia a anterior.

| Id | Data | Origem | Decisão | Motivo |
|---|---|---|---|---|
| D-01 | 25/11/2026 | coordenadores | Unidade de decisão: **coordenação nacional simulada das três esferas do SUS**, que respeita as competências e restrições reais de cada esfera. Nenhum órgão específico decide. | Escopo nacional obrigatório; o papel não é atribuído a uma organização concreta. |
| D-02 | 25/11/2026 | coordenadores | Data de corte: **29/01/2025**. Horizonte: 12 meses. | Reaproveita a classificação temporal já construída. |
| D-03 | 25/11/2026 | coordenadores | Escopo de produtos: **cesta de 50 apresentações da RENAME**, escolhidas por relevância econômica nacional e qualidade dos dados. **Inclui medicamentos de aquisição centralizada**, respeitando suas particularidades. | Mantém o problema tratável sem recorte geográfico. |
| D-04 | 25/11/2026 | coordenadores | Uma execução completa do decisor com **Claude Opus 5.5** e avaliação independente com **Claude Fable 5.2**. | — |
| D-05 | 25/11/2026 | coordenadores | **O experimento municipal fica arquivado** na branch `experimento-santa-luzia` e não é incorporado. Nesta branch, nenhum artefato municipal (pacote, vínculos por item, dados reservados, documentos 07–20, Etapas 4 e 5) entra em qualquer etapa. Só se reaproveitam dados brutos nacionais e código genérico. | Separação dos experimentos. |
| D-06 | 25/11/2026 | coordenadores | A reformulação fica na branch `reformulacao-nacional` até ser validada. | — |
| D-07 | 25/11/2026 | coordenadores | A **abrangência nacional é restrição obrigatória**. Não se pode reduzir o escopo geográfico, trocar o problema nem alterar o objetivo para contornar lacunas. Um impedimento fundamental interrompe a execução e é apresentado aos coordenadores. | Regra do projeto. |
| D-08 | 25/11/2026 | coordenadores | **Distinções obrigatórias:** quantidade comprada ≠ demanda real; valor homologado ou contratado ≠ pagamento efetivo. É proibido duplicar registros entre bases e extrapolar para o país sem fundamento. | Rigor da referência econômica. |
| D-09 | 25/11/2026 | coordenadores | Ao fim de cada etapa, verificar o **objetivo global** (problema nacional, cenários formulados pelo agente, escolha da estratégia mais eficiente), além da qualidade técnica das entregas. | Evitar a deriva de escopo ocorrida no experimento municipal. |
| D-10 | 25/11/2026 | coordenadores | **Autonomia do agente decisor:** nenhuma alternativa é antecipada e a recomendação não é direcionada. Os resultados originais de cada agente são preservados, inclusive os erros. | Validade do experimento. |
| D-11 | 25/11/2026 | coordenadores | A **Etapa 1-B** (suficiência dos dados de demanda nacional e da referência econômica) vem antes de qualquer execução decisória, e o diagnóstico vai aos coordenadores. | — |
| D-12 | 25/11/2026 | técnica | A dispensação do SIA/SUS (APAC de medicamentos) é usada como **demanda atendida** do CEAF, na janela de **processamento de nov/2023 a out/2024** (meses publicados antes do corte). Ressalva registrada: a base atual inclui reprocessamentos. | É a única fonte nacional de dispensação encontrada. |
| D-13 | 25/11/2026 | técnica | O BPS **não** é usado para medir a relevância econômica nacional. | Cobertura de 747 compradores e 88 registros federais: não representa o gasto nacional. |
| D-14 | 25/11/2026 | técnica | **Execução interrompida** (D-07): não há demanda nacional, anterior ao corte, para os componentes Básico e Estratégico. A composição da cesta aguarda decisão dos coordenadores (diagnóstico 01B, §5). | Impedimento para a cesta aprovada. |
