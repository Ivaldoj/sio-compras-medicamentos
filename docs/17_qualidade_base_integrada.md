# 17 — Qualidade da base integrada

> **Atualização pré-Etapa 4 (23/11/2026):** agora são 108 testes (todos passando) e a cobertura de preço praticado disponível é de 62,6% do valor (antes 55,3%). Estado atual e números em `docs/18_pre_etapa4_tratamento_lacunas.md`; o texto abaixo descreve a Etapa 3.

Resultados de `scripts/28_verificacoes.py` (23/11/2026) e de `scripts/padroniza.py` (autotestes). Detalhe linha a linha em `reports/etapa3_testes.csv`; cobertura em `reports/cobertura_integracao.csv`.

## 1. Testes

| Grupo | Nº | Resultado | Exemplos do que é verificado |
|---|---|---|---|
| Integridade temporal | 26 | 26 PASSOU | classe `disponivel` em todas as tabelas; datas máximas ≤ 29/01/2025; CMED de 06/01/2025 |
| Vazamento | 12 | 12 PASSOU | nomes de arquivo, textos e colunas sem identificadores/valores posteriores; nenhuma coluna reproduz preço homologado; módulo de consulta recusa `evaluation_only` |
| Integridade referencial | 7 | 7 PASSOU | item_cmed → itens e CMED; item_catmat → itens e BPS; grupos BPS → item_catmat; itens PNCP → contratações |
| Unicidade | 7 | 7 PASSOU | `item`; `id_origem` do BPS; `registro` CMED; (item, registro); (item, catmat); chaves PNCP |
| Consistência | 4 | 4 PASSOU | 334 itens somando R$ 4.952.438,00 com total = qtd × preço; BPS com preço ≥ 0, quantidade > 0 e total = unitário × quantidade; CMED não negativa; PMVG = PF × (1 − 21,53%) |
| Compatibilidade de unidades | 1 | PASSOU | vínculos aceitos com fator inteiro ≥ 1; exata = 1 |
| Validade das correspondências | 3 | 3 PASSOU | reclassificação determinística; item 196 não converte 10 mL; item 28 não converte 150 mL |
| Proveniência | 7 | 7 PASSOU | fonte, id e arquivo de origem preenchidos; data/base de disponibilidade em todas as tabelas de dados |
| Duplicidade | 1 | PASSOU (informativo) | 473 duplicatas de negócio e 3.008 preços extremos no BPS do pacote, marcados e não removidos |
| Reprodutibilidade | 2 | 2 PASSOU | SHA-256 do manifesto; manifesto completo |
| Consultas (item 22) | 5 | 5 PASSOU | ver §2 |
| Autotestes de padronização | 31 asserções | ok | bloqueios da insulina e da amoxicilina, mistura 70/30, caneta × refil, sinônimos, combinações |
| **Total** | **75** | **75 PASSOU** | |

## 2. Testes de consulta (item 22)

| Pergunta | Resultado |
|---|---|
| Necessidades e restrições documentadas de Santa Luzia | 334 itens e 7 restrições recuperados, inclusive a falta de local de armazenamento |
| Histórico nacional elegível de um medicamento (item 76, cefalexina 500 mg) | 768 registros BPS de 22 UFs, compras de 03/01/2020 a 27/09/2024, todos inseridos até o corte (`historico(con, item=76)`) |
| Preços compatíveis e fontes | `precos_compativeis(con, 76)`: 768 preços praticados (BPS), 3 preços estimados e 1 homologado (PNCP), separados por `categoria_valor`, com id de origem e marcas de qualidade |
| Referências CMED confirmadas | item 28: 1 vínculo exato (60 mL) e 2 compatíveis (caixas com 50 frascos); 88 linhas de PF/PMVG em 21 alíquotas, com aplicabilidade |
| Registros impedidos | item 196: 27 apresentações incompatíveis (10 mL, refis, 70/30) em `v_bloqueados`; nenhuma aparece no teto unitário |

## 3. Cobertura

| Dimensão | Disponível | A conferir | Bloqueado | Ausente |
|---|---|---|---|---|
| CATMAT (itens / % valor) | 242 / 57,7% (210 único + 32 múltiplo) | 14 / 1,2% (forma não confirmada) | — | 78 / 41,0% |
| Preço praticado compatível (BPS ou PNCP) | 234 / 55,3% | 10 / 2,6% | — | 90 / 42,1% |
| Teto CMED por unidade | 222 / 73,9% | 35 / 8,0% | 55 / 11,3% | 22 / 6,7% |
| Comparável no PNCP | 156 / 38,7% | — | — | 178 |

Nenhum item foi excluído. Os 334 itens, com seu valor estimado (R$ 4.952.438,00), continuam no pacote com o status de cada dimensão. O impacto das lacunas aparece em % do valor acima.

**Base nacional pré-corte:**
- BPS: 225.518 registros de medicamentos (2020–2024; 747 compradores; 3.388 CATMATs; 23 UFs). 92.588 são compatíveis com itens do caso; um registro pode servir a mais de um item.
- PNCP: 13 contratações, de 7 UFs e publicadas de 31/10/2023 a 27/01/2025, com 1.091 itens (344 comparáveis a itens do caso) e 102 resultados incluídos até o corte.
- CMED: 25.549 apresentações.

## 4. Limitações

1. **PNCP é amostra pequena.** De 66 contratações selecionadas, 14 foram baixadas: o download item a item, com pausa, levaria mais de 8 horas. A lista das 52 restantes está em `data/raw/pncp/etapa3/nao_baixadas.csv`, e o download pode ser retomado (há cache). O PNCP não traz CATMAT; a comparabilidade é por atributos.
2. **BPS** cobre uma fração dos compradores (quase só esfera municipal: 712 compradores municipais), tem valores extremos (marcados) e a disponibilidade é inferida pela data de inserção.
3. **Identificação**: 78 itens (41,0% do valor) sem CATMAT no catálogo pré-corte, sobretudo as insulinas em caneta (27% do valor), sem equivalente no BPS anterior ao corte.
4. **CMED**: alíquota de ICMS da PB indeterminada; conversões sem validação humana.
5. **Organizacional**: sem consumo por item, estoque ou saldo de dotação (lacunas da Etapa 2, inalteradas).
6. O PE 01/2024 só tem 4 resultados publicados, então os preços do próprio órgão em 2024 são quase inexistentes no pacote.

## 5. Prontidão para a Etapa 4

**Pronto com ressalvas.** O pacote permite ao agente:
- consultar a necessidade completa, as restrições e os recursos;
- consultar histórico nacional de preços praticados para cerca de 55% do valor;
- consultar tetos regulatórios por unidade para cerca de 74% do valor;
- consultar contratações comparáveis publicadas antes do corte, com controle de vazamento testado.

Antes ou durante a Etapa 4 convém:
- validar por amostragem humana as conversões aceitas, priorizando os itens de maior valor;
- decidir como tratar itens sem referência (as insulinas em caneta);
- se o volume justificar, retomar o download do PNCP.
