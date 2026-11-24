# 18 — Pré-Etapa 4: tratamento das limitações da Etapa 3

23/11/2026. O corte em **29/01/2025** foi mantido, assim como a separação entre `decision_input`, `evaluation_only` e `quarentena_temporal`. Os bloqueios de correspondências incompatíveis continuam e são testados. Nenhuma lacuna foi preenchida por suposição: o que não tem fonte oficial está marcado como ausente. Prioridade dada pelo impacto no valor estimado (R$ 4.952.438,00). Cronologia em `LOG_PRE_ETAPA_4.md`.

## 1. Resumo

| Limitação da Etapa 3 | Situação | O que mudou | O que falta |
|---|---|---|---|
| Alíquota de ICMS da PB | **resolvida, com ressalva** | Regra por apresentação: 0% para isentos e produtos do Convênio ICMS 87/02 (compra pública municipal); 20% nos demais. Campo `aliquota_aplicavel_pb` | Condições do §1º, I–II, do Convênio não verificadas por produto; RICMS-PB consolidado não baixado (§2) |
| Conversões sem validação | **verificadas por máquina e por amostra; validação humana pendente** | 9 defeitos de regra corrigidos; verificação automática nos 4.876 vínculos aceitos; inspeção de 330 apresentações (61 itens, 80% do valor com vínculo) | Validação humana; 210 vínculos com alerta |
| Cobertura de preços praticados | **ampliada** | Disponível: de 55,3% para **62,6%** do valor; nova fonte oficial (Compras.gov.br) | 25 itens a conferir (29,7%, quase tudo insulina) e 56 ausentes (7,7%) |
| Insulinas em caneta (27% do valor) | **parcial** | Teto CMED nos dois itens (antes só no 196); estimativa pré-corte de outro município com "caneta 3 mL" explícito; registros Compras.gov.br a conferir | Nenhum preço **praticado** explicitamente de caneta antes do corte |
| Amostra do PNCP | **ampliada e completa** | 95 de 95 contratações selecionadas baixadas (66 por CATMAT + 29 por descrição); 84 publicadas até o corte | Continua amostra dirigida; muitos itens sem resultado publicado antes do corte |
| Dados organizacionais | **parcial** | Repasses SUS 2024, população 2024, quantidades licitadas em 2024 por item | Consumo por item, estoque e saldo de dotação (sem fonte pública; §7) |
| Vazamento (achado nesta etapa) | **corrigido** | Removidas do pacote 4 colunas com estado atual (2026) ou datas posteriores ao corte (§8) | — |

## 2. ICMS da Paraíba

**Fontes oficiais (todas anteriores ao corte):**
- Lista CMED de 06/01/2025, cabeçalho:
  - o comprador deve "checar a alíquota aplicável ao estado de destino";
  - para medicamentos de convênios do CONFAZ, inclusive o 87/02, PF e PMVG devem ser calculados com desoneração (Acórdão TCU 140/2012; Nota Técnica 17/2012/DAF/SCTIE/MS).
- CONFAZ, Convênio ICMS 87/02 (texto consolidado):
  - **Cl. 1ª:** isenção nas operações com os fármacos e medicamentos do Anexo Único destinados à administração pública direta e indireta federal, estadual e municipal.
  - **Vigência:** prorrogado até 30/04/2026 pelo Conv. ICMS 226/23, portanto vigente em jan/2025.
  - **§5º:** autoriza a PB a dispensar a condição do §1º, IV, e o §6º.
  - Arquivo: `data/raw/complementares/icms_pb/confaz_convenio_icms_87_02.html`.
- SEFAZ-PB, Lei 6.379/96 consolidada em 02/10/2023, art. 11, I: **20%** nas operações internas, com efeitos a partir de 01/01/2024 (redação da Lei 12.788/23). O art. 11 não traz alíquota específica para medicamentos. Arquivo: `data/raw/complementares/icms_pb/lei_6379_96_icms_pb_consolidada_2023-10-02.pdf`.

**Regra aplicada** (`scripts/27_montar_pacotes.py`; comprador = Prefeitura/FMS de Santa Luzia, destino PB):

| Apresentação CMED | Alíquota aplicável | Apresentações |
|---|---|---|
| "ICMS 0%" = Sim (isenta) | 0% | 1.034 |
| "CONFAZ 87" = Sim (e não isenta) | 0% | 2.426 |
| demais | 20% | 22.089 |

Nos vínculos aceitos, o teto unitário fica em 20% em 3.779 vínculos e em 0% em 1.097. Por item: 149 itens só a 20%, 19 só a 0% e 58 com apresentações nas duas situações. `teto_cmed()` devolve por padrão só a coluna aplicável (`so_pb=False` mostra todas). As demais colunas continuam no pacote: nada foi apagado.

**Ressalvas:**
1. As condições do §1º do Convênio, (I) isenção ou alíquota zero de II/IPI e (II) desoneração de PIS/COFINS, não foram verificadas produto a produto. A coluna `lista_pis_cofins` da CMED foi preservada como indício.
2. O RICMS-PB consolidado (SEFAZ-PB, versão de 15/04/2024) não pôde ser baixado: o servidor encerrou a conexão em 4 tentativas. Por isso a internalização do Convênio e eventuais reduções de base de cálculo no regulamento não foram conferidas no texto consolidado. A lei não prevê alíquota diferenciada para medicamentos.
3. Alterações da lei entre 02/10/2023 e 29/01/2025 não foram verificadas.

## 3. Conversões item × CMED

**Verificação automática** (colunas novas em `padronizacao/regras_conversao.csv`):
- **Consistência interna:** o teto unitário na alíquota da PB deve ficar entre 0,25× e 4× a mediana do item.
- **Coerência com preço praticado:** compara com a mediana do BPS. Há alerta se o praticado passar de 2× o teto ou se o teto passar de 50× o praticado.
- **Ressalva de recipiente:** ampola × frasco-ampola.
- **Status:** "sem alerta" ou "COM ALERTA". A validação humana continua **pendente** em todos.

**Inspeção amostral pelo assistente de IA** (não substitui validação humana):
- Escopo: uma apresentação por fator distinto em cada um dos 61 itens que somam 80% do valor com vínculo, 330 apresentações no total.
- Registro: `reports/pre4_inspecao_conversoes_amostra.csv`.
- Resultado: 326 confirmadas, das quais 3 com ressalva de recipiente, e **4 erros (1,2%)**, todos de padrão de texto e corrigidos na regra.
- 327 das 330 continuam como vínculos aceitos e levam o veredito na coluna `inspecao_amostral_ia`.

**Defeitos de regra encontrados e corrigidos** (todos com autoteste em `scripts/padroniza.py`):

| # | Defeito | Achado por | Efeito |
|---|---|---|---|
| 1 | "CT EST 50 AMP" e "CX C/ 25 AMP" lidos como 1 recipiente | preço unitário fora da faixa | itens 130 e 151: fator 1 → 50 e 25 |
| 2 | "CX C/5 AMP" (sem espaço) lido como 1 | inspeção | item 151: fator 1 → 5 |
| 3 | "CT DISP 10 BL X 10" lido como 10 | preço unitário fora da faixa | item 129: 10 → 100 |
| 4 | "CX 50 BL … X 350" multiplicado (17.500 cápsulas) | preço unitário fora da faixa | item 29: rebaixado a provável |
| 5 | "COM LIB MOD" (liberação modificada) não reconhecida | inspeção | itens 8, 205, 206 e 277: vínculos com liberação modificada viram incompatíveis; item 52 (liberação controlada) passa a casar com "LIB RETARD" |
| 6 | Registros de teste da própria lista CMED ("EMPRESA DE TESTE") aceitos | inspeção | excluídos (item 63) |
| 7 | Tipo "regular" impedia achar a insulina humana na CMED | revisão das insulinas | itens 198 e 199 passam a ter teto |
| 8 | PDM genérico ("VITAMINA D"), sal "hemifumarato" e "PRINCÍPIO ATIVO: ASSOCIADA COM" ignorados no catálogo | busca no catálogo oficial | CATMAT pré-corte encontrado para colecalciferol 1.000/2.000/7.000 UI, quetiapina 25/100/200 mg e amoxicilina + clavulanato 500 + 125 mg |
| 9 | "50 mg + 12,5 mg/ml": o denominador não valia para a 1ª parcela | busca no catálogo oficial | concentração de associações líquidas (ex.: item 26) |

**Resultado:**
- Vínculos aceitos: 4.876, sendo 263 exatos e 4.613 com conversão.
- Com alerta: 210, em 51 itens que somam 10,3% do valor. **Nenhum item tem todos os vínculos em alerta.**
- Tipos de alerta: 104 de consistência interna; 113 "teto > 50× o praticado", típico de marca × genérico como o alendronato de referência; 6 "praticado > 2× teto"; 8 de recipiente.
- Pendências de conversão (`reports/pendencias_conversao.csv`): 285 pares exigem conferência humana e 1.659 estão bloqueados por apresentação distinta.
- Bloqueios exigidos continuam testados: item 196 (3 mL × 10 mL e refis), item 28 (60 × 150 mL), mistura 70/30.

## 4. Identificação (CATMAT)

| Status | Etapa 3 (itens / % valor) | Agora |
|---|---|---|
| 1 CATMAT | 210 / 44,7% | 227 / 51,4% |
| vários equivalentes | 32 / 13,0% | 27 / 11,5% |
| incompleta (forma não confirmada) | 14 / 1,2% | 14 / 1,2% |
| ausente | 78 / 41,0% | 66 / 36,0% |

A concordância com o CATMAT da Etapa 2 (só auditoria, em `evaluation_only`) passou a 96,0% em 226 itens.

Também foi consultado o **catálogo CATMAT oficial** (dadosabertos.compras.gov.br, módulo material), resultando em `padronizacao/item_catmat_catalogo_oficial.parquet`:
- 274 dos 334 itens têm ao menos um código compatível ou parcial.
- O catálogo é atual e a API não informa a data de criação dos códigos. A coluna `existencia_no_corte` só diz "comprovada" quando há preço com resultado ou registro BPS anterior ao corte.
- O status e a data de atualização atuais do catálogo ficaram fora do pacote (§8).

As insulinas em caneta não têm CATMAT próprio: 271157 (NPH) e 271154 (Regular) são genéricos "injetável", e a apresentação (frasco, tubete, seringa ou caneta) aparece só na unidade de fornecimento da compra. Ficam como `generico_apresentacao_na_unidade`.

## 5. Cobertura de preços praticados

**Nova fonte:** Compras.gov.br, Pesquisa de Preço (dados abertos oficiais), consultada para os 653 CATMATs ligados aos 334 itens.

| Classe temporal | Registros | Destino |
|---|---|---|
| disponível (`dataResultado` ≤ 29/01/2025 e compra ≤ resultado) | 141.599 (27 UFs; municipal 77.886, federal 53.584, estadual 10.129; compras desde 12/2021) | `decision_input/nacional/comprasgov_precos_praticados.parquet` |
| posterior | 87.287 | `evaluation_only/nacional/comprasgov_pos_corte.parquet` |
| indeterminado (sem data ou compra posterior ao resultado) | 3.128 | `quarentena_temporal/` |

**Regras:**
- **Compatibilidade por registro:** igual à do BPS (unidade de fornecimento para sólidos; capacidade igual ao conteúdo do item para líquidos). Para canetas, refil, tubete ou frasco são **incompatíveis**, e seringa 3 mL sem menção a caneta ou unidade não informada ficam **a conferir**.
- **Sobreposição com o BPS** (mesmo fornecedor, CATMAT, data e preço): 1.058 registros marcados em `flag_possivel_duplicata_bps`, não removidos.

| Status do preço praticado | Etapa 3 (itens / % valor) | Agora (itens / % valor) |
|---|---|---|
| disponível | 234 / 55,3% | **253 / 62,6%** |
| a conferir | 10 / 2,6% | 25 / 29,7% |
| ausente | 90 / 42,1% | **56 / 7,7%** |

- **Fontes dos itens com preço disponível:** BPS + Compras.gov.br + PNCP, 130; BPS + Compras.gov.br, 112; só PNCP, 6; só Compras.gov.br, 4; só BPS, 1.
- **Por fonte:** 246 itens (60,6% do valor) têm registro compatível no Compras.gov.br.
- **"A conferir":** a alta vem sobretudo das insulinas, que passaram de ausente para a conferir.

### Insulinas em caneta (itens 196 e 199; 27,0% do valor)

| Evidência anterior ao corte | NPH (196) | Regular (199) | Categoria |
|---|---|---|---|
| CMED, PF 0% (isenta), 1 caneta (Novolin FlexPen) | R$ 20,14 | R$ 15,80 (PMVG; produto com CAP) | teto regulatório |
| PNCP, município BA (13927801000149-1-000050/2024, publ. 18/07/2024), "caneta 3 ml" | R$ 46,19 | R$ 39,33 | preço **estimado** por outro órgão (sem resultado) |
| Compras.gov.br, CATMAT genérico, unidade "seringa 3 mL", 2023–2024 | 4 registros, R$ 16,60–33,51 | 6 registros, R$ 13,94–90,39 | praticado, **a conferir** (caneta não explícita) |
| Compras.gov.br, unidade de fornecimento não informada, 2021–2022 | 11 registros, R$ 16,78–22,90 | 9 registros, R$ 16,78–39,66 | praticado, **a conferir** (provavelmente frasco) |
| BPS, tubete 3 mL; Compras.gov.br, tubete/cartucho/frasco | — | — | **incompatível** (refil ou frasco sem sistema de aplicação) |
| Estimativa de Santa Luzia | **R$ 193,02** | **R$ 147,36** | estimativa do órgão |

A estimativa do órgão para as canetas é **9,6× (NPH) e 9,3× (Regular) o teto CMED unitário** e cerca de 4× a estimativa do outro município. Isso é constatação, não correção: o pacote não altera a estimativa.

## 6. PNCP

- **Seleção 2, por descrição do item.** O índice MT foi varrido pelas descrições dos itens, com o alvo nos itens sem preço praticado. Foram 29 contratações, cobrindo 35 desses itens e 78% do valor deles. A maior parte não tinha resultado publicado; os itens trazem preço estimado.
- **Retomada das 52 contratações da seleção por CATMAT:** concluída; todas as 66 estão baixadas.
- **Consolidado:** 95 contratações selecionadas e 95 baixadas.

| Tabela | Disponível (pacote) | Posterior (evaluation_only) |
|---|---|---|
| contratações | 84 (15 UFs; publicadas de 13/07/2023 a 28/01/2025) | 11 |
| itens | 4.988 | 468 |
| resultados | 269 | 335 |

- **Itens do caso com comparável PNCP disponível:** 243 (83,0% do valor); com resultado homologado disponível, 136.
- **Resultados posteriores ao corte:** são a maioria (335 de 604). Licitações de 2024 só tiveram resultado publicado em 2025.
- **Mesmo item, dois resultados:** em um caso, o resultado original (31/10/2024) está no pacote e o novo resultado do mesmo item e fornecedor (12/05/2025, após cancelamento) está em `evaluation_only`. São registros distintos, e o teste de separação usa a data de inclusão na chave.

## 7. Dados organizacionais

**Acrescentado** (informação interna do órgão com data ≤ corte, ou publicação ≤ corte):
- `organizacional/receitas_sus_2024.csv` (TCE-PB/SAGRES, receitas 2024 do município):
  - repasse federal do Bloco de Manutenção, Assistência Farmacêutica: **R$ 191.055,78** em 2024;
  - repasses federais SUS fundo a fundo, fontes 600 e 605: R$ 15.678.387,46;
  - para comparação, a despesa com medicamentos em 2024 foi de R$ 1.953.288,72.
- `recursos.csv`: população estimada 2024 (IBGE, **15.387**), os repasses acima e as lacunas com a evidência de ausência.
- `itens_santa_luzia.parquet`: `qtd_licitada_pregoes_proprios_2024` para 206 itens, com a quantidade do item comparável nos pregões 01/2024 e 12/2024 do próprio órgão. É **demanda planejada em 2024, não consumo**. Exemplo: canetas NPH, 6.000 em 2024 e 6.000 em 2025.

**Continua ausente, com evidência da busca:**
- **Estoque na data de decisão:** a API BNAFAR/Hórus não tem posição histórica; as consultas `anomes_posicao_estoque` 202412 e 202501 para Santa Luzia voltaram vazias em 23/11/2026.
- **Consumo/dispensação por item:** a API de dados abertos do MS expõe só o estoque.
- **Saldo de dotação:** não consta do edital nem dos dados abertos do TCE-PB (receitas e despesas).

## 8. Integridade temporal e separação: correções feitas nesta etapa

Uma varredura de **todas** as colunas de data e de situação do pacote achou informação de estado atual (2026) que não deveria estar lá. Os dois primeiros casos vinham da Etapa 3.

| Coluna | Problema | Correção |
|---|---|---|
| `pncp_comparaveis_itens.situacao` | Situação **atual** do item no PNCP: 1.874 itens marcados "Homologado" sem resultado disponível até o corte (desfecho posterior) | Removida do pacote; cópia de auditoria em `data/processed/pre4/pncp_itens_situacao_atual.parquet` |
| `pncp_comparaveis_resultados.cancelado` | Marcava cancelamentos ocorridos depois do corte (63 resultados) | Agora só conta cancelamento até o corte (`data_cancelamento` ≤ corte); nenhum ocorreu até o corte |
| `comprasgov_precos_praticados.data_atualizacao_item` | Data de atualização na fonte; 45.871 registros disponíveis foram atualizados depois do corte | Removida do pacote; auditoria em `data/processed/pre4/comprasgov_datas_atualizacao.parquet` |
| `item_catmat_catalogo_oficial.status_catalogo` e `data_atualizacao_catalogo` | Estado do catálogo em 2026 | Removidos do pacote; ficam em `data/processed/pre4/catalogo_oficial_candidatos.parquet` |

**Exceção mantida e documentada:** a data de inclusão no PNCP (30/04/2025) do resultado do PE 12/2024. É contrato do próprio município, usado como informação interna (doc 15), e o teste a lista explicitamente.

**Separação:** nenhum registro (BPS, Compras.gov.br, resultados e itens PNCP) está ao mesmo tempo no pacote e em `evaluation_only`. O manifesto não aponta para `evaluation_only` nem para `reports`, e o módulo de consulta recusa caminhos fora do pacote. A quarentena tem 2.153 registros BPS e 3.128 do Compras.gov.br, nenhum no pacote.

**Risco residual:** 32% dos registros Compras.gov.br disponíveis foram atualizados na fonte após o corte. O conteúdo atual pode diferir do visível em jan/2025, o mesmo risco já registrado para o BPS.

## 9. Constatação nova: estimativa do órgão × teto CMED

Com a alíquota da PB definida:
- **40 itens, 38,9% do valor estimado**, têm preço unitário estimado acima do **maior** teto CMED unitário aplicável entre os vínculos aceitos;
- a soma do excedente sobre esse teto é **R$ 1.390.210,40**, 28,1% do valor estimado, quase toda nas canetas de insulina.

Campos: `teto_cmed_unitario_pb_min`, `teto_cmed_unitario_pb_max`, `estimativa_sobre_teto_max` e `alerta_estimativa_acima_teto_cmed`. São dados anteriores ao corte. Não são estratégia nem decisão.

## 10. Testes

`scripts/28_verificacoes.py` → `reports/etapa3_testes.csv`: **108 testes, todos passando**, contra 75 na Etapa 3.

| Grupo | Testes |
|---|---|
| temporal | 31 |
| vazamento | 16 |
| integridade referencial | 9 |
| validade das correspondências | 9 |
| proveniência | 9 |
| unicidade | 8 |
| consultas | 5 |
| ICMS PB | 4 |
| consistência | 4 |
| separação | 4 |
| verificação de conversões | 3 |
| organizacional | 2 |
| reprodutibilidade | 2 |
| compatibilidade de unidades | 1 |
| duplicidade | 1 |

Os novos testes cobrem:
- regra de ICMS e `teto_cmed` só na alíquota da PB;
- temporalidade, unicidade e referência do Compras.gov.br;
- refil e frasco nunca compatíveis com caneta;
- erros da inspeção corrigidos (C/5 AMP, LIB MOD, "CX 50 BL … X 350", registros de teste);
- item 199 só com solução e sistema de aplicação;
- verificação registrada em todos os vínculos;
- varredura genérica de datas;
- ausência de colunas com situação atual;
- cancelamento só até o corte;
- disjunção pacote × `evaluation_only`;
- repasse de assistência farmacêutica e quantidades de 2024.

Autotestes de `padroniza.py`: 47 asserções.

## 11. Impacto na confiabilidade do experimento

1. **Teto regulatório:** deixou de ser uma faixa entre 11 alíquotas e passou a ter valor único por apresentação. Comparações com o teto ficam bem definidas. O risco residual vem das condições do Convênio 87/02.
2. **Conversões:**
   - Os erros achados eram sistemáticos (padrões de texto), não aleatórios, e foram corrigidos na regra, não caso a caso.
   - Na amostra, 4 de 330 (1,2%) estavam errados antes da correção.
   - Padrões não representados na amostra podem ter erros; os 210 vínculos com alerta indicam onde olhar.
   - Continua sem validação humana.
3. **Preço praticado:**
   - Agora cobre 62,6% do valor, com duas ou três fontes independentes para 242 itens.
   - Para as canetas de insulina (27%) não há preço praticado comprovadamente de caneta. A avaliação dessas linhas dependerá do teto CMED, de uma estimativa de outro órgão e de registros a conferir. São as linhas de **menor confiabilidade**, e as de maior peso.
4. **Estimativa do órgão como referência:** 28% do valor estimado está acima do teto legal. Qualquer métrica de "economia" calculada contra a estimativa ficará inflada. A Etapa 4 deve tratar a estimativa como dado do caso, não como preço de mercado.
5. **Vazamento:** a correção do §8 remove do pacote um sinal de desfecho (situação "Homologado") presente desde a Etapa 3. Resultados de qualquer teste anterior com o agente devem ser considerados potencialmente contaminados.
6. **Demanda e estoque:** continuam declarados (TR) e desconhecidos (estoque). A quantidade licitada em 2024 só mostra que a demanda declarada se repete; não a valida.
7. **Amostra PNCP:** completa dentro da seleção, mas continua dirigida. A maioria dos resultados de licitações de 2024 só foi publicada depois do corte.

## 12. Pendências

1. Validação humana das conversões, a começar pelos 210 vínculos com alerta e pelos itens de maior valor.
2. Condições do Convênio 87/02 por produto e conferência do RICMS-PB consolidado quando o servidor da SEFAZ-PB permitir.
3. Preço praticado de canetas de insulina antes do corte. A fonte provável são atas do MS ou de estados com descrição explícita, que não foram encontradas nos índices usados.
4. Consumo, estoque e saldo de dotação, só obtêveis do próprio município (pedido via LAI).
5. Os 25 itens "a conferir" e os 56 sem preço praticado (7,7% do valor), entre eles Ringer com lactato, que não tem concentração declarada, e itens sem CATMAT pré-corte.
