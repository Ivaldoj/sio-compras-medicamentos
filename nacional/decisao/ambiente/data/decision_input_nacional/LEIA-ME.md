# Pacote de informação do decisor — planejamento nacional de compras do Componente Especializado (CEAF)

**Data de decisão: 29/01/2025.** Tudo neste diretório estava disponível até essa data. Cada tabela informa sua fonte e a base de disponibilidade.

## 1. Problema
Você atua como a **coordenação nacional, simulada, das três esferas do SUS** (União, estados e Distrito Federal, municípios). Respeita as competências e restrições reais de cada esfera e não substitui nenhum órgão específico.

A tarefa é planejar, para os **12 meses seguintes a 29/01/2025**, a aquisição pública de uma **cesta de 50 apresentações de medicamentos do CEAF** da RENAME 2024, em **todo o território nacional**.

**Objetivo:** garantir o abastecimento contínuo e adequado da cesta durante o horizonte, com o uso mais eficiente dos recursos públicos e respeitando as restrições legais, regulatórias, federativas, orçamentárias, operacionais e de mercado.

## 2. O que está no pacote
| Tabela | Conteúdo |
|---|---|
| `problema/cesta.parquet` | As 50 apresentações. Para cada uma: unidade de dispensação; grupo de financiamento (1A, 1B, 2); **dispensação nacional atendida** em 12 meses (processamentos de nov/2023 a out/2024) e no ano anterior; valor aprovado no SIA (financiamento federal do Grupo 1B); teto CMED por unidade (mínimo, mediana, máximo); resumo dos preços praticados antes do corte |
| `problema/demanda_uf.parquet` | Dispensação atendida em 12 meses, por UF |
| `problema/demanda_mes.parquet` | Dispensação nacional por mês de processamento |
| `problema/recursos_federais.csv` | Execução federal de 2023 e 2024 das ações 4705 (CEAF), 20AE e 4368: orçamento inicial, atualizado, empenhado e realizado |
| `problema/restricoes.csv` | Competências por grupo, regras legais (Lei 14.133, SRP, adesão, dispensa), regras CMED e ICMS, registro sanitário |
| `mercado/precos_comprasgov.parquet` | Compras públicas registradas no Compras.gov.br (pesquisa de preço) **com resultado até o corte**, nos CATMATs vinculados a cada apresentação: preço unitário, quantidade, esfera, UF, comprador, fornecedor, marca, modalidade e forma |
| `mercado/precos_bps.parquet` | Banco de Preços em Saúde, registros inseridos até o corte, nos mesmos CATMATs. **Fonte complementar: pode repetir compras do Compras.gov.br; não some as duas bases.** |
| `mercado/cmed_teto.parquet` | Apresentações CMED vinculadas: laboratório, tipo de produto, CAP, Convênio 87/02 e teto por unidade dispensada (0% e 18% de ICMS) |
| `consulta.py` | Consulta SQL (DuckDB) sobre essas tabelas |

## 3. Regras de leitura
- **Dispensação atendida não é demanda total.** O SIA registra o que foi dispensado e aprovado. A necessidade não atendida não aparece.
- **Quantidade comprada não é demanda.** Valor homologado ou contratado não é pagamento.
- **Categorias de valor diferentes não se somam:**
  - preço homologado/praticado em compra (Compras.gov.br, BPS);
  - teto regulatório (CMED);
  - valor financiado (SIA, Grupo 1B);
  - execução orçamentária (empenhado ou pago, agregado por ação).
- **CMED:** o PMVG é o teto só para produtos com CAP e já inclui o desconto. Para os demais, o teto é o PF. A alíquota de ICMS é a da UF de destino; os produtos do Convênio 87/02 são isentos em compra pública.
- **Vínculos:** feitos por regra (princípio ativo, concentração, forma e unidade), **sem validação humana**. Os registros do Compras.gov.br marcados `a_conferir` têm unidade de fornecimento diferente da unidade de dispensação. `flag_preco_extremo` marca preços acima de 10× ou abaixo de 0,1× da mediana.
- **Grupo de financiamento:** atribuído por correspondência textual com a RENAME 2024, Anexo III (`grupo_metodo` diz como).

## 4. O que não se sabe
- A demanda não atendida e o estoque inicial de estados e União.
- O orçamento de 2025: a lei orçamentária ainda não estava aprovada na data de decisão.
- O financiamento estadual do Grupo 2 e as contrapartidas estaduais.
- As alíquotas internas de ICMS de cada UF.
- Os contratos e atas vigentes em cada esfera.
- A capacidade dos fornecedores e eventos de desabastecimento.
- Os preços futuros.
