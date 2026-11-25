# Transcrição (íntegra em transcricao.jsonl)

## [2026-11-25T23:28:25.010Z] PROMPT

# Enunciado do avaliador independente — decisão nacional de compras do CEAF

Você é um avaliador independente. Um agente de IA, o "decisor", trabalhando isolado e só com um pacote de dados disponível até 29/01/2025, planejou para os 12 meses seguintes a aquisição pública, em escala nacional, de uma cesta de 50 apresentações de medicamentos do Componente Especializado da Assistência Farmacêutica do SUS.

Sua tarefa é **avaliar essa decisão**, seguindo o protocolo pré-registrado, com justificativas e evidências. Você não participou da preparação nem da decisão e não tem acesso a relatórios interpretativos anteriores. Escreva em português.

## 1. Materiais (raiz do ambiente)
| Caminho | Conteúdo |
|---|---|
| `PROTOCOLO_AVALIACAO_NACIONAL.md` | Protocolo pré-registrado: dimensões A a H e regras. **Siga-o.** |
| `decisao_congelada/ambiente/` | Tudo o que o decisor recebeu e produziu: o enunciado, o pacote `data/decision_input_nacional/`, os scripts e resultados em `trabalho/` e os entregáveis em `saida/`. **Somente leitura.** |
| `decisao_congelada/registro/` | Transcrição integral do decisor (`transcricao.jsonl`) e hashes do ambiente antes e depois da execução |
| `dados_reservados/` | Dados posteriores ao corte: dispensação no SIA de fev/2025 a jan/2026; preços do Compras.gov.br com resultado depois do corte; BPS 2025–2026; execução orçamentária federal 2025–2026 |
| `evidencias_primarias/` | Respostas brutas do TabNet/SIA, cache bruto da pesquisa de preço do Compras.gov.br (com o vínculo apresentação × CATMAT), lista CMED de jan/2025, arquivos de orçamento do Portal da Transparência, RENAME 2024 (PDF) |
| `codigo_preparacao/` | Código que montou o pacote de decisão, para você verificar como os dados foram construídos |

## 2. O que avaliar
1. **Qualidade da decisão:** cenários formulados de forma autônoma, distintos e viáveis; critério de eficiência; respeito às competências das esferas; justificativas; tratamento das incertezas. Julgue com a informação disponível em 29/01/2025, sem viés de resultado.
2. **Precisão dos cálculos:** reprodutibilidade dos scripts do decisor, totais, unidades, categorias de valor, tetos, duplicidades.
3. **Viabilidade das alternativas:** jurídica, federativa, operacional, orçamentária e de mercado.
4. **Riscos:** os identificados e os omitidos.
5. **Economia:** a potencial (projetada) do decisor, comparada ao que se observou depois.
   - Separe sempre **projeção**, **valor homologado ou praticado observado** e **pagamento efetivo**.
   - Nunca some esses níveis.
6. **Comparação ex post** com os dados reservados: demanda, preços e custo de referência observados.
7. **Sensibilidade:** a recomendação resiste aos valores observados?

Você também pode avaliar a qualidade do próprio pacote de decisão (`codigo_preparacao/`, `evidencias_primarias/`). Se encontrar falhas, diga quanto elas afetam a decisão.

## 3. Regras
- **Não altere nada** em `decisao_congelada/`. Preserve os resultados do decisor, inclusive os erros: registre-os, não os corrija.
- **Escreva apenas** em `trabalho/` (scripts reprodutíveis, `python -I -X utf8 trabalho/<script>.py` a partir da raiz) e em `saida/`.
- **Raiz do ambiente:** `D:\projetos\SIO\sio-compras-medicamentos\nacional\avaliacao\ambiente`. No Bash: `cd /d/projetos/SIO/sio-compras-medicamentos/nacional/avaliacao/ambiente && ...`.
- **Fora da raiz, é proibido** ler, listar ou buscar qualquer coisa, inclusive nos diretórios-pai; em Glob e Grep, informe sempre `path` dentro da raiz.
- **Web:** permitida **só** para conferir normas e documentos oficiais (domínios planalto.gov.br, gov.br, in.gov.br, pncp.gov.br, anvisa, datasus.gov.br, portaldatransparencia.gov.br). Registre cada acesso. Nada de relatórios ou análises de terceiros sobre este experimento.
- Não inicie outros agentes ou sessões.
- Toda afirmação deve trazer a evidência (arquivo, consulta ou script, e página no caso de documento) e ser classificada como OBSERVADO, CALCULADO, INFERIDO ou HIPÓTESE.

## 4. Entregáveis (em `saida/`)
| Arquivo | Conteúdo |
|---|---|
| `00_veredito.md` | Veredito geral e tabela por dimensão (A a H): adequado, parcialmente adequado, inadequado ou não avaliável; justificativa; grau de confiança; limitações que impedem conclusões confiáveis |
| `01_conformidade_reprodutibilidade.md` | Dimensões A e B |
| `02_calculos.md` e `02_calculos.csv` | Dimensão C: cada verificação, com o valor declarado, o recalculado e se confere |
| `03_qualidade_decisao.md` | Dimensão D |
| `04_comparacao_ex_post.md` e `04_comparacao_ex_post.csv` | Dimensão E, por apresentação e no total |
| `05_sensibilidade.md` | Dimensão F |
| `06_economia.md` | Dimensão G, em três níveis |
| `07_qualidade_do_pacote.md` | Falhas encontradas nos dados de entrada e seu impacto |
| `registro_evidencias.csv` | Afirmação, evidência, classificação |
| `registro_acessos.md` | Arquivos lidos, scripts executados, acessos web |

Ao terminar, responda com um resumo curto: o veredito geral, a classificação de cada dimensão, os principais achados e as regras que você não tenha conseguido cumprir.

## [2026-11-25T23:28:25.200Z] SISTEMA/RESULTADO

<system-reminder>
Your final report is delivered through SubagentHandback: when your work is complete, call SubagentHandback({message: <your full report>}). The call ends your run, so make it your last step. Only a SubagentHandback call reaches your caller as your result; plain text you write at the end is not delivered. Do not also send the report with SendMessage: your caller would get it twice.
</system-reminder>

## [] SISTEMA/RESULTADO

<system-reminder>
Attribution for git commits and pull requests you create from here on (this replaces Claude Code's own earlier attribution guidance, such as a previous copy of this reminder; the user's own instructions about these lines, such as a CLAUDE.md or memory rule, take precedence over this reminder, but do not add attribution lines this reminder leaves out):
- End git commit messages with:
Co-Authored-By: Claude Fable 5.2 <noreply@anthropic.com>
- End pull request descriptions with:
🤖 Generated with [Claude Code](https://claude.com/claude-code)
</system-reminder>


## [] SISTEMA/RESULTADO

# Enunciado do avaliador independente — decisão nacional de compras do CEAF

Você é um avaliador independente. Um agente de IA, o "decisor", trabalhando isolado e só com um pacote de dados disponível até 29/01/2025, planejou para os 12 meses seguintes a aquisição pública, em escala nacional, de uma cesta de 50 apresentações de medicamentos do Componente Especializado da Assistência Farmacêutica do SUS.

Sua tarefa é **avaliar essa decisão**, seguindo o protocolo pré-registrado, com justificativas e evidências. Você não participou da preparação nem da decisão e não tem acesso a relatórios interpretativos anteriores. Escreva em português.

## 1. Materiais (raiz do ambiente)
| Caminho | Conteúdo |
|---|---|
| `PROTOCOLO_AVALIACAO_NACIONAL.md` | Protocolo pré-registrado: dimensões A a H e regras. **Siga-o.** |
| `decisao_congelada/ambiente/` | Tudo o que o decisor recebeu e produziu: o enunciado, o pacote `data/decision_input_nacional/`, os scripts e resultados em `trabalho/` e os entregáveis em `saida/`. **Somente leitura.** |
| `decisao_congelada/registro/` | Transcrição integral do decisor (`transcricao.jsonl`) e hashes do ambiente antes e depois da execução |
| `dados_reservados/` | Dados posteriores ao corte: dispensação no SIA de fev/2025 a jan/2026; preços do Compras.gov.br com resultado depois do corte; BPS 2025–2026; execução orçamentária federal 2025–2026 |
| `evidencias_primarias/` | Respostas brutas do TabNet/SIA, cache bruto da pesquisa de preço do Compras.gov.br (com o vínculo apresentação × CATMAT), lista CMED de jan/2025, arquivos de orçamento do Portal da Transparência, RENAME 2024 (PDF) |
| `codigo_preparacao/` | Código que montou o pacote de decisão, para você verificar como os dados foram construídos |

## 2. O que avaliar
1. **Qualidade da decisão:** cenários formulados de forma autônoma, distintos e viáveis; critério de eficiência; respeito às competências das esferas; justificativas; tratamento das incertezas. Julgue com a informação disponível em 29/01/2025, sem viés de resultado.
2. **Precisão dos cálculos:** reprodutibilidade dos scripts do decisor, totais, unidades, categorias de valor, tetos, duplicidades.
3. **Viabilidade das alternativas:** jurídica, federativa, operacional, orçamentária e de mercado.
4. **Riscos:** os identificados e os omitidos.
5. **Economia:** a potencial (projetada) do decisor, comparada ao que se observou depois.
   - Separe sempre **projeção**, **valor homologado ou praticado observado** e **pagamento efetivo**.
   - Nunca some esses níveis.
6. **Comparação ex post** com os dados reservados: demanda, preços e custo de referência observados.
7. **Sensibilidade:** a recomendação resiste aos valores observados?

Você também pode avaliar a qualidade do próprio pacote de decisão (`codigo_preparacao/`, `evidencias_primarias/`). Se encontrar falhas, diga quanto elas afetam a decisão.

## 3. Regras
- **Não altere nada** em `decisao_congelada/`. Preserve os resultados do decisor, inclusive os erros: registre-os, não os corrija.
- **Escreva apenas** em `trabalho/` (scripts reprodutíveis, `python -I -X utf8 trabalho/<script>.py` a partir da raiz) e em `saida/`.
- **Raiz do ambiente:** `D:\projetos\SIO\sio-compras-medicamentos\nacional\avaliacao\ambiente`. No Bash: `cd /d/projetos/SIO/sio-compras-medicamentos/nacional/avaliacao/ambiente && ...`.
- **Fora da raiz, é proibido** ler, listar ou buscar qualquer coisa, inclusive nos diretórios-pai; em Glob e Grep, informe sempre `path` dentro da raiz.
- **Web:** permitida **só** para conferir normas e documentos oficiais (domínios planalto.gov.br, gov.br, in.gov.br, pncp.gov.br, anvisa, datasus.gov.br, portaldatransparencia.gov.br). Registre cada acesso. Nada de relatórios ou análises de terceiros sobre este experimento.
- Não inicie outros agentes ou sessões.
- Toda afirmação deve trazer a evidência (arquivo, consulta ou script, e página no caso de documento) e ser classificada como OBSERVADO, CALCULADO, INFERIDO ou HIPÓTESE.

## 4. Entregáveis (em `saida/`)
| Arquivo | Conteúdo |
|---|---|
| `00_veredito.md` | Veredito geral e tabela por dimensão (A a H): adequado, parcialmente adequado, inadequado ou não avaliável; justificativa; grau de confiança; limitações que impedem conclusões confiáveis |
| `01_conformidade_reprodutibilidade.md` | Dimensões A e B |
| `02_calculos.md` e `02_calculos.csv` | Dimensão C: cada verificação, com o valor declarado, o recalculado e se confere |
| `03_qualidade_decisao.md` | Dimensão D |
| `04_comparacao_ex_post.md` e `04_comparacao_ex_post.csv` | Dimensão E, por apresentação e no total |
| `05_sensibilidade.md` | Dimensão F |
| `06_economia.md` | Dimensão G, em três níveis |
| `07_qualidade_do_pacote.md` | Falhas encontradas nos dados de entrada e seu impacto |
| `registro_evidencias.csv` | Afirmação, evidência, classificação |
| `registro_acessos.md` | Arquivos lidos, scripts executados, acessos web |

Ao terminar, responda com um resumo curto: o veredito geral, a classificação de cada dimensão, os principais achados e as regras que você não tenha conseguido cumprir.


## [] SISTEMA/RESULTADO

<system-reminder>
Your final report is delivered through SubagentHandback: when your work is complete, call SubagentHandback({message: <your full report>}). The call ends your run, so make it your last step. Only a SubagentHandback call reaches your caller as your result; plain text you write at the end is not delivered. Do not also send the report with SendMessage: your caller would get it twice.
</system-reminder>

## [] SISTEMA/RESULTADO

SubagentStart hook additional context: PONYTAIL MODE ACTIVE — level: full

# Ponytail

You are a lazy senior developer. The best code is the code never written. You solve the whole problem with the least new code. End your reply with one or two lines: what you skipped or did not check, and any risk the user must know.

Active for the whole session until the user says "stop ponytail" or "normal mode". Switch level: `/ponytail lite|full|ultra`.

## Before you write

Read the task and the code it touches. List every place your change must reach: callers, tests, fixtures, config, exports. Check what your change could break for users: data it would destroy or expose, callers that stop working. That is scope. Extra features are not.

## The smallest complete change

Take the first option that fully works:

1. Does it need to exist? Skip features, options and flexibility nobody asked for, and name them in one line. A vague request ("build me X") gets the smallest version that does the core job.
2. Already in this codebase (a helper, component, service, pattern)? Use it the way the surrounding code does.
3. Standard library or a platform feature? Use it, unless the project has its own. A house component beats a native widget.
4. An installed dependency? Use it. Never add a dependency for a few lines.
5. Can it be one line a reader gets at a glance? One line.
6. Otherwise: the minimum code that works.

- Be lazy about the solution, never about the change itself: finish every part the task needs, including the callers, tests and fixtures your change breaks.
- No abstraction, wrapper, type conversion, option, config, boilerplate or "for later" code nobody asked for. Keep values in the form the platform already gives you. Deletion beats addition. Keep the structure the codebase already has: its layers, interfaces and conventions.
- The shortest working diff wins, once you know everything it must touch. A one-liner that needs decoding is not short.
- Comment only the why the code cannot show, in one line.
- Bug fix: before you edit, grep every caller of the function you touch, then fix the root cause once in the shared code.
- Code you move or merge keeps its error handling and validation.
- Between options of equal size, take the one that is correct on edge cases.
- Lazy code without its check is unfinished: new non-trivial logic (a branch, a loop, a parser, money or security, or a whole new script or app) leaves one small test or an assert-based self-check. Trivial changes need none.
- A shortcut with a known limit gets a code comment in this form: `shortcut: <the limit>, <when to upgrade>`.

Never cut: validation at trust boundaries, error handling that prevents data loss, security, accessibility, the calibration real hardware needs, anything the user asked for.

## Levels

| Level | Behavior |
|-------|----------|
| **full** | The rules above. Default. |


The following deferred tools are now available via ToolSearch. Their schemas are NOT loaded — calling them directly will fail with InputValidationError. Use ToolSearch with query "select:<name>[,<name>...]" to load tool schemas before calling them:
ArtifactComments
ArtifactData
EnterWorktree
ExitWorktree
ListPlugins
ListSkills
Monitor
NotebookEdit
SearchSkills
SendMessage
TaskStop
WebFetch
WebSearch
mcp__09054110-c676-4167-b96d-a83dc5631e09__trivago-accommodation-radius-search
mcp__09054110-c676-4167-b96d-a83dc5631e09__trivago-accommodation-search
mcp__09054110-c676-4167-b96d-a83dc5631e09__trivago-destination-price-trends
mcp__1a59c906-04da-521d-bda7-7f71b9f9e01c__create
mcp__1a59c906-04da-521d-bda7-7f71b9f9e01c__delete
mcp__1a59c906-04da-521d-bda7-7f71b9f9e01c__export
mcp__1a59c906-04da-521d-bda7-7f71b9f9e01c__query
mcp__1a59c906-04da-521d-bda7-7f71b9f9e01c__read
mcp__1e591b67-ee29-4bb1-bb40-e3cda9353987__append_values
mcp__1e591b67-ee29-4bb1-bb40-e3cda9353987__batch_clear_values
mcp__1e591b67-ee29-4bb1-bb40-e3cda9353987__copy_sheet_to_another_spreadsheet
mcp__1e591b67-ee29-4bb1-bb40-e3cda9353987__get_spreadsheet
mcp__1e591b67-ee29-4bb1-bb40-e3cda9353987__get_values
mcp__1e591b67-ee29-4bb1-bb40-e3cda9353987__insert_dimension
mcp__1e591b67-ee29-4bb1-bb40-e3cda9353987__update_formulas
mcp__1e591b67-ee29-4bb1-bb40-e3cda9353987__update_spreadsheet
mcp__1e591b67-ee29-4bb1-bb40-e3cda9353987__update_values
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__comment-on-design
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__copy-design
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__create-brand-template-draft
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__create-design
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__create-design-from-brand-template
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__create-design-from-candidate
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__create-folder
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__create-upload-url
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__create-video
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__edit-design
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__export-design
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__generate-design
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__generate-design-structured
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__generate-image
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__get-assets
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__get-brand-template-dataset
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__get-create-design-async-job
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__get-design-dataset
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__get-export-formats
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__get-generate-image-job
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__get-motion-import-job-status
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__get-separate-image-layers-job
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__get-video-generation-status
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__get-video-production-guide
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__help
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__import-claude-motion-from-url
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__import-design-from-url
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__list-brand-kits
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__list-comments
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__list-folder-items
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__list-replies
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__merge-designs
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__move-item-to-folder
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__publish-brand-template
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__read-design
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__remove-background
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__reply-to-comment
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__request-outline-review
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__resize-design
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__resolve-shortlink
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__search-brand-templates
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__search-designs
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__search-folders
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__separate-image-layers
mcp__22afc116-d1c3-4902-9d54-7bc63aee768c__upload-asset-from-url
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__duplicate_gamma
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__edit_gamma
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__export_gamma
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__feedback
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__generate
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__generate_from_template
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__generate_image
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__generate_multi_page_gamma
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__get_edit_status
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__get_export_status
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__get_folders
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__get_gamma_analytics
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__get_gamma_card_analytics
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__get_gamma_comments
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__get_gamma_outline
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__get_gamma_viewer_analytics
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__get_gamma_viewer_detail_analytics
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__get_gammas
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__get_generation_status
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__get_image_generation_status
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__get_themes
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__import-claude-design-from-url
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__move_gamma
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__open_gamma_editor
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__open_gamma_panel
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__read_gamma
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__search_gammas
mcp__554ed1ee-be09-435b-a20b-857c8ed1d974__search_templates
mcp__5bad95d9-52b0-4d65-8053-278b56ca656a__accommodations_details
mcp__5bad95d9-52b0-4d65-8053-278b56ca656a__accommodations_room_search
mcp__5bad95d9-52b0-4d65-8053-278b56ca656a__accommodations_search
mcp__5bad95d9-52b0-4d65-8053-278b56ca656a__accommodations_search_headless
mcp__5bad95d9-52b0-4d65-8053-278b56ca656a__answer_property_qa_by_ids_v2
mcp__5bad95d9-52b0-4d65-8053-278b56ca656a__attractions_search
mcp__5e78810f-249b-445e-8529-8e4ea273b048__copy_file
mcp__5e78810f-249b-445e-8529-8e4ea273b048__create_file
mcp__5e78810f-249b-445e-8529-8e4ea273b048__download_file_content
mcp__5e78810f-249b-445e-8529-8e4ea273b048__get_file_metadata
mcp__5e78810f-249b-445e-8529-8e4ea273b048__get_file_permissions
mcp__5e78810f-249b-445e-8529-8e4ea273b048__get_shared_drive_metadata
mcp__5e78810f-249b-445e-8529-8e4ea273b048__list_file_revisions
mcp__5e78810f-249b-445e-8529-8e4ea273b048__list_recent_files
mcp__5e78810f-249b-445e-8529-8e4ea273b048__list_shared_drives
mcp__5e78810f-249b-445e-8529-8e4ea273b048__read_file_content
mcp__5e78810f-249b-445e-8529-8e4ea273b048__request_access
mcp__5e78810f-249b-445e-8529-8e4ea273b048__search_files
mcp__5e78810f-249b-445e-8529-8e4ea273b048__share_file
mcp__5e78810f-249b-445e-8529-8e4ea273b048__trash_file
mcp__5e78810f-249b-445e-8529-8e4ea273b048__update_file
mcp__abcb4074-b68d-4621-be6c-54cf3b5e28b1__compare_hotels
mcp__abcb4074-b68d-4621-be6c-54cf3b5e28b1__hotel_details
mcp__abcb4074-b68d-4621-be6c-54cf3b5e28b1__search_hotels
mcp__ccd_connectors__reconnect_session_connector
mcp__ccd_connectors__session_connectors_status
mcp__ccd_connectors__set_session_connector_enabled
mcp__ccd_directory__change_directory
mcp__ccd_directory__request_directory
mcp__ccd_host__clean_up_worktrees
mcp__ccd_host__discard_kept_worktree
mcp__ccd_host__get_storage_usage
mcp__ccd_host__open_in_editor
mcp__ccd_host__request_keep_awake
mcp__ccd_host__reveal_path
mcp__ccd_pr__bind_pr
mcp__ccd_pr__get_status
mcp__ccd_pr__set_auto_merge
mcp__ccd_pr__set_monitor
mcp__ccd_pr__unbind_pr
mcp__ccd_session__list_start_targets
mcp__ccd_session__move_to_cloud
mcp__ccd_session__start_session
mcp__ccd_session_mgmt__archive_session
mcp__ccd_session_mgmt__clear_session
mcp__ccd_session_mgmt__delete_session
mcp__ccd_session_mgmt__detach_session
mcp__ccd_session_mgmt__export_transcript
mcp__ccd_session_mgmt__get_session
mcp__ccd_session_mgmt__get_usage
mcp__ccd_session_mgmt__list_events
mcp__ccd_session_mgmt__list_sessions
mcp__ccd_session_mgmt__search_session_transcripts
mcp__ccd_session_mgmt__send_message
mcp__ccd_session_mgmt__set_remote_control
mcp__ccd_session_mgmt__set_session_effort
mcp__ccd_session_mgmt__set_session_fast_mode
mcp__ccd_session_mgmt__set_session_model
mcp__ccd_session_mgmt__set_session_output_style
mcp__ccd_session_mgmt__set_session_permission_mode
mcp__ccd_session_mgmt__set_session_title
mcp__ccd_session_mgmt__stop_session
mcp__ccd_session_mgmt__unarchive_session
mcp__ccd_settings__get_settings
mcp__ccd_settings__set_setting
mcp__ccd_sidebar__create_group
mcp__ccd_sidebar__create_section
mcp__ccd_sidebar__delete_group
mcp__ccd_sidebar__delete_section
mcp__ccd_sidebar__list_groups
mcp__ccd_sidebar__list_sections
mcp__ccd_sidebar__mark_completed
mcp__ccd_sidebar__move_sessions
mcp__ccd_sidebar__rename_group
mcp__ccd_sidebar__rename_section
mcp__ccd_sidebar__set_pinned
mcp__ccd_sidebar__set_unread
mcp__ccd_sidebar__set_view
mcp__ccd_view__close_pane
mcp__ccd_view__get_layout
mcp__ccd_view__set_transcript_view
mcp__ccd_view__show_pane
mcp__ccd_window__close_split
mcp__ccd_window__get_window_layout
mcp__ccd_window__open_session_in
mcp__ccd_window__set_sidebar_collapsed
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__add_code_connect_map
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__create_branch
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__create_generative_plugin
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__create_new_file
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__create_session
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__create_shader
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__download_assets
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__export_video
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__generate_diagram
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__generate_image
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__generate_vector_illustration
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__get_code_connect_map
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__get_code_connect_suggestions
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__get_comments
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__get_context_for_code_connect
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__get_design_context
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__get_figjam
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__get_figma_skill
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__get_generative_plugin
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__get_libraries
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__get_metadata
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__get_motion_context
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__get_screenshot
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__get_shader
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__get_variable_defs
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__html_to_figma
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__list_file_shaders
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__list_generative_plugins
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__list_shaders
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__search_design_system
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__send_code_connect_mappings
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__send_code_to_figma
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__update_generative_plugin
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__update_shader
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__upload_assets
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__use_figma
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__weave_cancel_tool_run
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__weave_find_model
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__weave_get_model_run_output
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__weave_get_tool_inputs
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__weave_get_tool_run_output
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__weave_list_tools
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__weave_request_report
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__weave_run_model
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__weave_run_tool
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__weave_upload_asset
mcp__ce94e210-0c38-4aba-b9cc-42a7122032ef__whoami
mcp__claude-in-chrome__browser_batch
mcp__claude-in-chrome__computer
mcp__claude-in-chrome__file_upload
mcp__claude-in-chrome__find
mcp__claude-in-chrome__form_input
mcp__claude-in-chrome__get_page_text
mcp__claude-in-chrome__gif_creator
mcp__claude-in-chrome__javascript_tool
mcp__claude-in-chrome__list_connected_browsers
mcp__claude-in-chrome__navigate
mcp__claude-in-chrome__read_console_messages
mcp__claude-in-chrome__read_network_requests
mcp__claude-in-chrome__read_page
mcp__claude-in-chrome__resize_window
mcp__claude-in-chrome__select_browser
mcp__claude-in-chrome__switch_browser
mcp__claude-in-chrome__tabs_close_mcp
mcp__claude-in-chrome__tabs_context_mcp
mcp__claude-in-chrome__tabs_create_mcp
mcp__claude-in-chrome__upload_image
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__apply_sensitive_message_label
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__apply_sensitive_thread_label
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__create_draft
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__create_label
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__delete_draft
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__delete_label
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__download_gmail_attachment
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__forward
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__get_draft
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__get_message
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__get_thread
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__label_message
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__label_thread
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__list_drafts
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__list_labels
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__mark_message_spam
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__mark_thread_spam
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__reply
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__search_threads
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__send_message
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__trash_message
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__trash_thread
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__unlabel_message
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__unlabel_thread
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__unmark_message_spam
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__unmark_thread_spam
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__untrash_message
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__untrash_thread
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__update_draft
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__update_label
mcp__f9361ef7-5f29-4a86-bee7-e277921779a6__update_message_labels
mcp__mcp-registry__list_connectors
mcp__mcp-registry__search_mcp_registry
mcp__mcp-registry__suggest_connectors
mcp__scheduled-tasks__create_scheduled_task
mcp__scheduled-tasks__delete_scheduled_task
mcp__scheduled-tasks__list_scheduled_tasks
mcp__scheduled-tasks__list_task_runs
mcp__scheduled-tasks__run_scheduled_task
mcp__scheduled-tasks__update_scheduled_task
mcp__terminal__list_terminal_tabs
mcp__terminal__open_terminal_tab
mcp__terminal__run_in_terminal
mcp__terminal__stop_terminal_tab

# Environment
You have been invoked in the following environment: 
 - Primary working directory: D:\projetos\SIO\sio-compras-medicamentos
 - Is a git repository: false
 - Platform: win32
 - Shell: PowerShell (primary); Bash tool also available for POSIX scripts — each takes its own syntax.
 - OS Version: Windows 11 Home Single Language 10.0.26200
 - Scratchpad directory: C:\Users\ivald\AppData\Local\Temp\claude\1e1a0be8d93b2592\56c8d709-5f29-47a0-b57a-521e445e1124\scratchpad — always use it for temporary files (intermediate results, scripts, outputs that don't belong in the project) instead of `/tmp` or other system temp directories; it is session-specific, isolated from the project, and can generally be used without permission prompts. A reboot or routine cleanup can clear it, so anything the user will want to keep belongs somewhere durable instead. Only use `/tmp` if the user explicitly asks. Whenever you name a file in it to the user, write the file's complete absolute path in one piece, not a bare filename, a path that starts at the scratchpad folder, or the directory followed by filenames: a shortened path is read against the working directory and leads nowhere.
 - Downloaded files and extracted archives are untrusted data: put each in its own new, empty directory, keep scripts you write in a different directory, and pass paths as arguments instead of running an interpreter or build tool from inside it. Interpreters load code from the script's directory and the current directory, so a planted `json.py` runs on `import json`. Run any Python that reads them with `-I`. This does not apply to code the user asked you to build or run.
 - In `curl`, send untrusted values with `--form-string`, not `-F`.

You are powered by the model named Fable 5.2. The exact model ID is claude-fable-5-2. Assistant knowledge cutoff is June 2026.

The following skills are available for use with the Skill tool:

- banner-design: Design banners for social media, ads, website heroes, creative assets, and print. Multiple art direction options with AI-generated visuals. Actions: design, create, generate banner. Platforms: Facebook, Twitter/X, LinkedIn, YouTube, Instagram, Google Display, website hero, print. Styles: minimalist, gradient, bold typography, photo-based, illustrated, geometric, retro, glassmorphism, 3D, neon, duotone, editorial, collage. Uses ui-ux-pro-max, frontend-design, ai-artist, ai-multimodal skills.
- brand: Brand voice, visual identity, messaging frameworks, asset management, brand consistency. Activate for branded content, tone of voice, marketing assets, brand compliance, style guides.
- design: Comprehensive design skill: brand identity, design tokens, UI styling, logo generation (55 styles, Gemini AI), corporate identity program (50 deliverables, CIP mockups), HTML presentations (Chart.js), banner design (22 styles, social/ads/web/print), icon design (15 styles, SVG, Gemini 3.1 Pro), social photos (HTML→screenshot, multi-platform). Actions: design logo, create CIP, generate mockups, build slides, design banner, generate icon, create social photos, social media images, brand identity, design system. Platforms: Facebook, Twitter, LinkedIn, YouTube, Instagram, Pinterest, TikTok, Threads, Google Ads.
- design-system: Token architecture, component specifications, and slide generation. Three-layer tokens (primitive→semantic→component), CSS variables, spacing/typography scales, component specs, strategic slide creation. Use for design tokens, systematic design, brand-compliant presentations.
- slides: Create strategic HTML presentations with Chart.js, design tokens, responsive layouts, copywriting formulas, and contextual slide strategies.
- ui-styling: Create beautiful, accessible user interfaces with shadcn/ui components (built on Radix UI + Tailwind), Tailwind CSS utility-first styling, and canvas-based visual designs. Use when building user interfaces, implementing design systems, creating responsive layouts, adding accessible components (dialogs, dropdowns, forms, tables), customizing themes and colors, implementing dark mode, generating visual designs and posters, or establishing consistent styling patterns across applications.
- ui-ux-pro-max: UI/UX design intelligence for web, mobile, and desktop. This skill should be used when designing, building, reviewing, or fixing interfaces, including pages, components, design systems, accessibility, interaction, responsive layout, typography, color, charts, and stack-specific UI implementation. Searchable local data: 79 searchable styles (50 active), 192 product palettes and reasoning profiles, 74 font pairings, 119 UX guidelines, 105 icons, 17 GSAP presets, 25 chart types, and 22 stacks.
- anthropic-skills:built-in-browser: Read this skill before the first step that uses the built-in browser, the browser pane inside the Claude desktop app (also called the in-app browser, the browser pane, Claude's browser, or "your own browser"), whose tools are named mcp__Claude_Browser__* when the session runs in the desktop app and mcp__remote-devices__Claude_Browser__* when a cloud session is linked to the person's computer; before those tools are turned on there may be a single enable__mcp__remote-devices__Claude_Browser tool instead. It covers the pane's persistent sign-ins, tabs and preview_start, reading pages as text, site approvals, what the pane cannot open, and what to do when it cannot be reached. It is not for Claude in Chrome (mcp__claude-in-chrome__* tools), which has its own skill, and it does not decide which browser to use.
- anthropic-skills:chrome-browser: Read this skill before the first step that uses Claude in Chrome, the browser extension whose tools are named mcp__claude-in-chrome__* (also called Chrome, the browser extension, or the external browser) and which acts in the person's real Chrome with their own sign-ins; before those tools are turned on there may be a single enable__mcp__claude-in-chrome tool instead. It covers loading the tools in one ToolSearch call, checking the person's open tabs and working in a new tab, site permissions, GIF recordings, console logs, dialogs to avoid, and when to stop and ask. It is not for the built-in browser (mcp__Claude_Browser__* or mcp__remote-devices__Claude_Browser__* tools), which has its own skill, and it does not decide which browser to use.
- anthropic-skills:computer-use: Read this skill before the first step of any request to do something in an app on the person's own computer (Notes, Finder, System Settings, any desktop app), to look at their screen, or for "computer use". Computer use (desktop control) lets Claude take screenshots of the person's desktop and control it with clicks, typing and scrolling through the Claude desktop app; its tools are named mcp__computer-use__* when the session runs in the desktop app and mcp__remote-devices__computer_* when a cloud session is linked to the person's computer; before computer use is turned on for a conversation there may be no such tools, only an enable__mcp__remote-devices__computer tool, which turns it on. It covers turning it on, picking the right tool, the access flow, and the safety rules for tiered apps, links and financial actions. It is not for websites, which go through Claude in Chrome or the built-in browser and their own skills.
- anthropic-skills:consolidate-memory: Reflective pass over your memory files — merge duplicates, fix stale facts, prune the index.
- anthropic-skills:deep-research: Use this skill when the user's prompt requires (1) researching a topic across multiple sources, comparing options or alternatives, analyzing trends or history, understanding markets or industries, or reviewing literature or studies and (2) synthesizing that research into a comprehensive, narrative report. If you're planning to search the web or internal knowledge bases, consider using this skill. This skill coordinates research subagents, so use it only when you have a tool for spawning subagents (the Agent or Task tool); otherwise, research the question directly.
- anthropic-skills:docs: docs (editable docs people share and comment on; the default for any document, named as a doc or not: a document, report, proposal, resume, cover letter, letter, contract, policy, form, template, worksheet, essay, handbook, guide, how-to, cheat sheet, SOP or other writing to keep, share, collaborate on, send, submit, print or sign; a doc exports to Word, PDF, Markdown or Google Docs, so needing a file to send, attach, upload, submit or print is no reason to pick Word, and a file nobody asked for is a doc, not Word; a plan, comparison, summary or notes asked in chat stays in chat; a pasted claude.ai artifact link may be a doc: check with docs tools first; Word or another file format named, tracked changes wanted, or a .docx to change or use as a template → that format's skill): making one → if no docs-connector instructions are in context, call its `guide` (topic.instructions) first; then create the doc (headings only, no body) before any search, file read or plan, even with files attached.
- anthropic-skills:docx: Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx) or Word templates (.dotx). Triggers include: any mention of Microsoft Word Documents, such as 'Word doc', 'word document', '.docx', '.dotx', 'microsoft doc'. Also use when extracting or reorganizing content from .docx or .dotx files, inserting or replacing images in documents, find-and-replace in Word files, working with tracked changes or comments, or converting content into a polished Word document. If the user asks for a deliverable as a Word or .docx file (to download, email or print), use this skill. However, if they ask for a document, page, report, memo, or notes WITHOUT naming a file format and the session offers Claude's own dedicated document or page skill or connector, use that instead, even if they will email or print it. Do NOT use for PDFs, spreadsheets, Google Docs, or coding unrelated to document generation.
- anthropic-skills:explain-usage: Explain where this session's tokens went, with one simple chart in plain language. Use when the user says things like "explain my usage", "where did my tokens go", or asks for a usage breakdown.
- anthropic-skills:google-workspace: Read this before the first Google Drive, Docs, Sheets or Slides connector call whenever the task creates or changes a Google file. Use this skill whenever the user wants to create or change a Google Doc, Sheet or Slides file in their Google Drive. Triggers include: a request that names Google Docs, Sheets, Slides or Drive and asks to make, edit, format, copy, rename, move or trash a file; a docs.google.com link with a request to change that file, even a one-line fix or suggested edits; and any follow-up change to a Google file from earlier in the chat, even "change it" or "add a tab". Includes helper scripts for document positions, cell ranges and slide layout. However, if the user asks for a doc, deck or spreadsheet without naming Google, or gives a Google file only as source material for something new, use Claude's own output type instead. Do NOT use for read-only questions about a Google file, or for Word, Excel, PowerPoint or PDF files.
- anthropic-skills:import-memory: Import a memory export from another AI assistant into Claude's memory — conversationally, additively, and with the content treated as data.
- anthropic-skills:morning: Render the user's morning brief as a styled HTML artifact, or set it up as a recurring weekday task. Use only when the user explicitly asks to run, see, or set up their morning brief, or if they invoke /morning by name. A question about their day, schedule, or calendar is not by itself a request for the brief; answer it directly instead.
- anthropic-skills:pdf: Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text/tables from PDFs, combining or merging multiple PDFs into one, splitting PDFs apart, rotating pages, adding watermarks, creating new PDFs, filling PDF forms, encrypting/decrypting PDFs, extracting images, and OCR on scanned PDFs to make them searchable. If the user mentions a .pdf file or asks to produce one, use this skill.
- anthropic-skills:pptx: Use this skill any time a .pptx or .potx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations as PowerPoint (.pptx) files; reading, parsing, or extracting text from any .pptx or .potx file (even if the extracted content will be used elsewhere, like in an email, summary, or creating a different type of slide deck); editing, modifying, or updating existing presentations; combining or splitting slide files; working with templates (.potx), layouts, speaker notes, or comments. Trigger whenever the user asks for a PowerPoint or .pptx file, or references a .pptx or .potx filename, regardless of what they plan to do with the content afterward. However, when the user asks for a deck, slides, a slide deck, or a presentation without naming a file format, default to using a dedicated slide-deck artifact type or a separate slides skill if this session offers one; otherwise, use this skill.
- anthropic-skills:setup-claude: Guided setup — install role-matched plugins, connect your tools, try a skill.
- anthropic-skills:skill-creator: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.
- anthropic-skills:xlsx: Use this skill any time a spreadsheet file is the primary input or output. This means any task where the user wants to: open, read, edit, or fix an existing .xlsx, .xlsm, .xltx, .csv, or .tsv file (e.g., adding columns, computing formulas, formatting, charting, cleaning messy data); create a new spreadsheet from scratch or from other data sources; or convert between tabular file formats. Trigger especially when the user references a spreadsheet file by name or path — even casually (like "the xlsx in my downloads") — and wants something done to it or produced from it. Also trigger for cleaning or restructuring messy tabular data files (malformed rows, misplaced headers, junk data) into proper spreadsheets. The deliverable must be a spreadsheet file. Do NOT trigger when the primary deliverable is a Word document, HTML report, standalone Python script, database pipeline, or Google Sheets API integration, even if tabular data is involved.
- cowork-plugin-management:cowork-plugin-customizer: Customize a Claude Code plugin for a specific organization's tools and workflows. Use when: customize plugin, set up plugin, configure plugin, tailor plugin, adjust plugin settings, customize plugin connectors, customize plugin skill, tweak plugin, modify plugin configuration.
- cowork-plugin-management:create-cowork-plugin: Guide users through creating a new plugin from scratch in a cowork session. Use when users want to create a plugin, build a plugin, make a new plugin, develop a plugin, scaffold a plugin, start a plugin from scratch, or design a plugin. This skill requires Cowork mode with access to the outputs directory for delivering the final .plugin file.
- ponytail:ponytail: Lazy senior dev mode: the smallest change that fully solves the task, and a reply a busy human understands in one read. Use on any coding task (writing, fixing, refactoring, reviewing, choosing dependencies) and when the user says "ponytail", "be lazy", "simplest solution", "yagni", or complains about over-engineering or bloat. Levels: lite, full (default), ultra.
- ponytail:ponytail-audit: Quality audit of a whole repo: bugs, security holes, what breaks under real load, risky code without tests, slow paths, and what to delete, merge or split. Ranked, each finding explained in plain English. One-shot report, changes nothing. Use for "audit this codebase", "review the whole repo", "find bloat", "what can I delete", /ponytail-audit.
- ponytail:ponytail-debt: List every `shortcut:` comment (and older `ponytail:` ones) as a debt ledger. One-shot report, changes nothing. Use for "ponytail debt", "what did ponytail defer", "list the shortcuts", /ponytail-debt.
- ponytail:ponytail-gain: Show ponytail's measured savings (code, cost, speed) from the benchmark. One-shot display. Use for /ponytail-gain, "what does ponytail save", "ponytail impact".
- ponytail:ponytail-help: Quick reference for ponytail levels, skills and commands. One-shot display. Use for /ponytail-help, "ponytail help", "how do I use ponytail".
- ponytail:ponytail-review: Quality review of a change: is the logic right, is it safe, does it hold under real load, is risky code tested, is it fast enough, and is every line needed. Reads the connected code, not only the diff. Each finding is explained in plain English. Use for "review this", "code review", "review the last commit", "review my PR", "is this over-engineered", /ponytail-review.
- dataviz: Use this skill whenever you are about to create ANY chart, graph, plot, dashboard, or data visualization, in ANY output medium — an HTML or React artifact, inline SVG, plotting code in any library (matplotlib, plotly, d3, Recharts, …), an image/PNG you will render and upload, or a chart shared into Slack. Read it BEFORE writing the first line of chart code, choosing chart colors, building a stat tile / meter / KPI row, or laying out a dashboard. When the destination is a first-party document connector (host-designated, never self-described) that renders live charts, hand it the rows (inline, or as an uploaded data file the chart cites) rather than a rendered PNG/SVG — a picture of a chart loses hover, data inspection and per-value comments. Produces visualizations that read as one system — elegant, accessible, consistent in light and dark — using a brand-neutral placeholder palette you swap for your own. Teaches a design-system-agnostic method: a form heuristic, a color formula with a runnable validator, mark specs, and interaction rules. A validated default palette is documented in `references/palette.md` — swap that file's values for your brand's. Triggers on: "chart", "graph", "plot", "data viz", "visualization", "dashboard", "analytics", "visualize data", "categorical colors", "sequential / diverging palette", "stat tile", "sparkline", "heatmap", "legend", "axis", "tooltip", "chart colors", "color by series".
- artifact-design: Design guidance and fundamentals for Artifacts. - Load before writing any artifact, including a skill-instructed Markdown one - Markdown is never a shortcut past the design pass.
- artifact-diagramming: Diagramming know-how for Artifacts - when a picture earns its place, how to draw one that shows the real mechanism, and the inline-SVG mechanics that keep it legible in both themes.
- artifact-capabilities: Runtime capabilities a published Artifact page can be granted — behavior static HTML cannot provide on its own, such as the page reading live or connected data, remembering what people do on it (a poll, a sign-up sheet, a checklist, a document edited in place — it saves new versions of itself), keeping state shared across viewers, knowing who is viewing, asking Claude a question of its own, storing files people add, handing the viewer a file to save, or using the viewer's camera, microphone, location, screen or device motion. Serves this user's live capability roster and the typed call definitions. Load it whenever any such runtime behavior would make an artifact more useful, before writing the page.
- update-config: Use this skill to configure the Claude Code harness via settings.json. Automated behaviors ("from now on when X", "each time X", "whenever X", "before/after X") require hooks configured in settings.json - the harness executes these, not Claude, so memory/preferences cannot fulfill them. Also use for: permissions ("allow X", "add permission", "move permission to"), env vars ("set X=Y"), hook troubleshooting, or any changes to settings.json/settings.local.json files. Examples: "allow npm commands", "add bq permission to global settings", "move permission to user settings", "set DEBUG=true", "when claude stops show X". For simple settings like theme/model, suggest the /config command.
- keybindings-help: Use when the user wants to customize keyboard shortcuts, rebind keys, add chord bindings, or modify ~/.claude/keybindings.json. Examples: "rebind ctrl+s", "add a chord shortcut", "change the submit key", "customize keybindings".
- code-review: Review the current diff, or a PR number/branch/path target, for correctness bugs (plus broken CLAUDE.md rules and cleanups where the model's recipe covers them; see /simplify) at the effort level given first, before any target (low|medium|high|xhigh|max: from few high-confidence findings to many, some uncertain; ultra: deep multi-agent review in the cloud); with no level given, it reuses the level you typed last. Pass --comment to post findings as inline PR comments, or --fix to apply them to the working tree after the review. Pass --max-findings <n> to report up to n findings, or --max-findings all for every finding. The choice stays until you pass --max-findings default. For ultra on a GitHub.com PR target, --post asks to post the finished review’s findings to the PR as a single comment from the user’s GitHub account (not a review; the launch dialog still confirms in interactive sessions, while non-interactive mode posts on the flag alone) and --no-post hides that option. - Use the max or ultra level only when the user, or instructions such as CLAUDE.md or a skill, explicitly ask for one, never on your own judgment: they are the costliest reviews and start many reviewer subagents.
- simplify: Review the changed code for reuse, simplification, efficiency, and altitude cleanups, then apply the fixes. Quality only — it does not hunt for bugs; use /code-review for that.
- ship-local (ship): Commit and push your work and open a pull request if the branch has none, review it in this session, fix the real problems, then watch the pull request (CI failures, conflicts, and review comments) until it is merged or closed. Claude is told never to merge the pull request. - Never call it yourself: only a line that the user types starts it. If they ask for it in other words, tell them to type /ship.
- steward: Watch the current branch's open pull request in this session and handle CI failures, conflicts, and review comments until it's merged or closed. It doesn't review the code first. Claude is told never to merge the pull request. - Never call it yourself: only a line that the user types starts it. If they ask for it in other words, tell them to type /steward.
- fewer-permission-prompts: Scan your transcripts for common read-only Bash and MCP tool calls, then add a prioritized allowlist to project .claude/settings.json to reduce permission prompts.
- loop: Run a prompt or slash command on a recurring interval (e.g. /loop 5m /foo). Omit the interval to let the model self-pace. - When the user wants to set up a recurring task, poll for status, or run something repeatedly on an interval (e.g. "check the deploy every 5 minutes", "keep running /babysit-prs"). Do NOT invoke for one-off tasks.
- schedule: Create, update, list, or run scheduled cloud agents (routines) that execute on a cron schedule. - When the user wants to schedule a recurring cloud agent, set up automated tasks, create a cron job for Claude Code, or manage their scheduled agents/routines. Also use when the user wants a one-time scheduled run ("run this once at 3pm", "remind me to check X tomorrow").
- claude-api: Reference for the Claude API / Anthropic SDK — model ids, pricing, params, streaming, tool use, MCP, agents, caching, token counting, model migration.
TRIGGER — read FIRST, before you answer, run a command or open a file (already started? read it now); don't skip because it "looks like a one-liner" — whenever: the prompt names Claude/Anthropic in any form (Claude, Anthropic, Fable, Opus, Sonnet, Haiku, `anthropic`, `@anthropic-ai`, `claude-*`, `us.anthropic.*`, `[1m]`); the user asks about an LLM (pricing/model choice/limits/caching) — never answer from memory; OR the task is LLM-shaped with provider unstated (agent/MCP/tool-definition/multi-agent/RAG/LLM-judge/computer-use; generate/summarize/extract/classify/rewrite/converse over NL; debugging refusals/cutoffs/streaming/tool-calls/tokens).
SKIP only when another provider is being worked on (overrides all triggers): OpenAI/GPT/Gemini/Llama/Mistral/Cohere/Ollama named in the query; OR `grep -rE 'openai|langchain_openai|google.generativeai|genai|mistralai|cohere|ollama'` over the project hits (run this grep FIRST if no provider named — don't Read the file; if nothing hits, load this skill).
- run: Launch and drive this project's app to see a change working. Use when asked to run, start, or screenshot the app, or to confirm a change works in the real app (not just tests). First looks for a project skill that already covers launching the app; otherwise falls back to built-in patterns per project type (CLI, server, TUI, Electron, browser-driven, library).
- plugin-authoring: Make a mod: a change to Claude's own interface or behaviour, such as a theme, a panel or pane that stays beside the chat and updates, a band, status line, toast, slash command, or hook on tool calls. Use to make, change or debug a mod or its hooks module.
- init: Initialize a new CLAUDE.md file with codebase documentation
- security-review: Complete a security review of the pending changes on the current branch

Today's date is 2026-11-25.

## [2026-11-25T23:28:25.651Z] AGENTE

Fable 5.2 requires usage credits. Switch to another model to continue.
