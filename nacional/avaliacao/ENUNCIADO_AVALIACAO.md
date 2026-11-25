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
