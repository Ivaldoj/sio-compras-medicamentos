# 13 — Padronização de medicamentos, correspondências e conversões

> **Atualização pré-Etapa 4 (23/11/2026):** 9 defeitos de regra foram corrigidos (contagem de recipientes, liberação modificada, nome do catálogo, sais, associações); CATMAT agora 227/27/14/66 e 4.876 vínculos aceitos (263 exatos), cada um com verificação automática. Estado atual e números em `docs/18_pre_etapa4_tratamento_lacunas.md`; o texto abaixo descreve a Etapa 3.

Regras implementadas em `scripts/padroniza.py` (com autotestes, inclusive os bloqueios obrigatórios) e aplicadas por `scripts/25_padronizacao_vinculos.py`. Toda identificação do pacote usa **apenas evidência anterior ao corte**: texto do edital/TR, catálogo observado no BPS inserido até 29/01/2025 e lista CMED de 06/01/2025.

## 1. Atributos extraídos

| Atributo | Regra | Observações |
|---|---|---|
| Princípio ativo | tokens alfabéticos (≥ 4 letras) antes do 1º número, sem sais/radicais (cloridrato, sódico, sulfato…), sem palavras de forma/uso e sem sinônimos entre parênteses | o catálogo usa PDM + `ORIGEM:`/`TIPO:` + `COMPOSIÇÃO: ASSOCIADO À …`; sinônimo ortográfico documentado: benzerazida → benserazida |
| Concentração | pares (valor, unidade): massas em mg (1 g = 1.000 mg; 1 mcg = 0,001 mg), UI, mEq, %; denominador /mL ou /g; "60 mg/0,6 mL" → 100 mg/mL; "100+25 mg" → 100 mg + 25 mg | "g" sem denominador só é concentração se não houver outra (senão é conteúdo da bisnaga) |
| Forma | categorias: comprimido, cápsula, solução/suspensão/pó injetável, injetável genérico (catálogo), solução oral, suspensão oral, pó para suspensão oral, xarope, creme, pomada, gel, colírio, spray, supositório | modificadores que precisam coincidir: liberação prolongada, orodispersível, mastigável, sublingual, vaginal, efervescente, **mistura 70/30**, **sistema de aplicação** |
| Conteúdo do recipiente | último volume (mL) ou massa (g) do texto do item | frascos, ampolas, bisnagas, seringas, canetas |
| Embalagem CMED | nº de recipientes (`CT n FA/AMP/FR…`), volume por recipiente (`X v ML/G`), unidades sólidas (`X n` × `CT n BL`), embalagem composta (diluente/2º recipiente; copo e aplicador não contam) | — |
| Unidade de fornecimento | unidade do PNCP; inconsistências registradas (`inconsistencia_unidade`: 1 item com descrição "cápsula" e unidade "comprimido") | — |

Compatibilidades de forma: iguais; "injetável" genérico do catálogo com qualquer injetável; "suspensão oral" do catálogo com "pó para suspensão oral" (mesma suspensão reconstituída); comprimido × cápsula só quando o item aceita os dois ("cáps./comp.") ou quando o catálogo é comprado nas duas formas. **Na CMED a forma é sempre estrita.**

## 2. Identificação CATMAT (pré-corte)

Catálogo = 3.388 CATMATs de medicamentos presentes no BPS inserido até o corte. Um CATMAT é candidato quando princípio, concentração, forma e modificadores coincidem.

| Status (`status_identificacao`) | Itens | % do valor estimado |
|---|---|---|
| validada por atributos — 1 CATMAT | 210 | 44,7% |
| validada — vários CATMAT equivalentes | 32 | 13,0% |
| incompleta (forma não confirmada) | 14 | 1,2% |
| ausente | 78 | 41,0% |

Causas verificadas dos maiores itens sem CATMAT:
- **Insulinas humanas NPH e Regular em caneta com sistema de aplicação** (itens 196 e 199; 27% do valor). O BPS anterior ao corte só tem esses CATMATs em frasco (271157, 271154). A ausência é real, não erro de regra.
- **Colecalciferol**: nenhum registro no BPS anterior ao corte.
- **Enoxaparina, ceftriaxona e associações**: parte foi resolvida pelas regras de §1; o restante depende de "características adicionais" do catálogo (seringa, diluente) que não foram modeladas.

**Auditoria (fora do pacote):** dos 217 itens que têm CATMAT nas duas abordagens, **95,9%** coincidem com o CATMAT da Etapa 2, obtido via contrato posterior ao corte (`data/evaluation_only/auditoria/catmat_etapa2_vs_pre_corte.csv`). O CATMAT da Etapa 2 **não** é usado no pacote.

## 3. Correspondência item × CMED (pré-corte, direta por atributos)

| Classe | Definição | Pares | Itens (melhor classe) |
|---|---|---|---|
| `exata` | mesmo princípio, concentração, forma/modificadores e conteúdo; 1 embalagem = 1 unidade do item | 252 | 36 |
| `compativel_conversao` | idem, e a embalagem contém *n* unidades do item, com *n* extraído por regra | 4.616 | 186 |
| `provavel_conferencia` | princípio e forma coincidem, mas há incerteza (unidades de concentração diferentes, embalagem composta, nº de unidades não extraído) | 64 | 16 |
| `indeterminada` | concentração ou forma não extraídas do texto | 232 | 19 |
| `incompativel` | concentração, forma/modificador ou conteúdo do recipiente diferentes | 15.205 | 55 |
| — | nenhuma apresentação com o mesmo princípio | — | 22 |

Todos os vínculos aceitos (`exata`, `compativel_conversao`) estão com `validacao_humana = pendente`.

## 4. Regras de conversão (`padronizacao/regras_conversao.csv`, 4.868 vínculos)

| Regra | Origem → destino | Fator | Justificativa |
|---|---|---|---|
| R0 | embalagem CMED → unidade do item | 1 | embalagem com um único recipiente/unidade idêntico ao pedido |
| R1 (sólidos) | caixa → comprimido/cápsula | n de `X n` × n de `CT n BL` | contagem impressa na apresentação |
| R2 (recipientes) | caixa → frasco/ampola/frasco-ampola/bisnaga/caneta | n de `CT n FA/AMP/FR/BG/CAR` | **só** se o volume/massa por recipiente for igual ao do item |

**Bloqueios obrigatórios (testados):**
- **Item 196 (insulina NPH 3 mL com sistema de aplicação):** frasco de 10 mL e refis sem caneta são `incompativel`. Só as canetas de 3 mL com sistema de aplicação convertem.
- **Item 28 (amoxicilina 60 mL):** apresentações de 150 mL são `incompativel`. Só a de 60 mL é `exata`, e as caixas com 50 frascos de 60 mL são `compativel_conversao` (fator 50).
- Mistura 70/30 nunca equivale a NPH; liberação prolongada nunca equivale a liberação convencional.

## 5. Revisão das 259 correspondências da Etapa 2

As 259 foram descobertas via um CATMAT obtido de dados posteriores ao corte. Por isso foram **reclassificadas** pelo mesmo classificador e **excluídas** do pacote; o pacote usa só os vínculos refeitos com dados anteriores ao corte. Detalhes em `reports/etapa3_revisao_259_cmed.csv`.

| Melhor classe por item | Itens | Pares (de 1.023) |
|---|---|---|
| correspondência exata verificada (por regra) | 20 | 42 |
| compatível após conversão documentada | 148 | 599 |
| provável que exige conferência | 9 | 17 |
| incompatível | 69 | 315 |
| indeterminada | 13 | 50 |

931 dos 1.023 pares foram reencontrados pela via pré-corte.

## 6. Pendências (`reports/pendencias_conversao.csv`)

- **296 pares "exige conferência humana"** (provável ou indeterminado).
- **1.611 pares "bloqueado: apresentação distinta (não converter)"** (conteúdo ou forma diferentes).
- 152 itens envolvidos. Cada linha traz item, registro, apresentação, classe, fator (se houver), justificativa e valor estimado do item.

## 7. Limites

- Regras textuais: abreviações raras da CMED (ex.: "SUS" sem "OR") ficam como `indeterminada`.
- "Revestido" é ignorado para comprimidos (regra explícita, registrada na justificativa).
- A validação humana das conversões aceitas não foi feita.
- Alíquota de ICMS e aplicabilidade do teto: ver doc 14.
