# Pacote de informação do decisor — Santa Luzia/PB, data de decisão 29/01/2025
> **Versão 2 (errata de 23/11/2026, pré-Etapa 5).** Igual à versão usada na Etapa 4 (`data/decision_input/`), com as correções de `ERRATA.csv`: itens 194/195 sem CATMAT de outro tipo de insulina e sem tubete como preço de caneta; item 197 sem o vínculo da pré-mistura HUMULIN 70N/30R (o item passa a ter estimativa acima do teto: 41 itens no total). Nota sobre o Convênio ICMS 87/02: a lista CMED de compras públicas só publica as colunas 'Sem Imposto' e '0%' para os produtos do convênio; o teto a 20% desses produtos não existe na fonte. Nenhuma informação posterior a 29/01/2025 foi acrescentada.


Tudo neste diretório estava disponível até **29/01/2025**: era informação interna da Prefeitura ou estava publicada antes dessa data. Cada tabela informa a data e a base de disponibilidade.

## 1. Problema

A Secretaria Municipal de Saúde de **Santa Luzia, Paraíba** (Prefeitura CNPJ 09.090.689/0001-67; Fundo Municipal de Saúde CNPJ 10.425.754/0001-47; população estimada de 15.387 habitantes em 2024) precisa abastecer por **12 meses** a Assistência Farmacêutica municipal: Básica, Especializada e medicamentos fora da RENAME.

O Estudo Técnico Preliminar e o Termo de Referência, assinados em 29/01/2025, documentam **334 itens** com quantidades anuais estimadas ("baseadas na utilização anual dos anos anteriores") e um valor estimado de **R$ 4.952.438,00**. A forma de aquisição ainda deve ser decidida e justificada.

**Objetivo:** garantir o suprimento contínuo e adequado dos 334 itens durante 12 meses, usando os recursos públicos com eficiência e respeitando as restrições legais, regulatórias e operacionais.

**Tarefa:** formular alternativas de aquisição, estimar e comparar suas consequências (financeiras e operacionais, com as incertezas) e escolher e justificar uma alternativa, explicitando as hipóteses adicionais usadas.

## 2. O que se sabe

| Tema | Onde | Observação |
|---|---|---|
| Necessidade (334 itens) | `organizacional/itens_santa_luzia.parquet` | quantidade, unidade, preço estimado pelo órgão, atributos padronizados, status de cada informação, teto CMED unitário (mín./máx.) e quantidade do mesmo item licitada nos pregões próprios de 2024 |
| Restrições | `organizacional/restricoes.csv` | inclui: **a administração não possui local adequado para armazenamento**; regra de ICMS do teto CMED |
| Recursos | `organizacional/recursos.csv` | estimativa, dotações e fontes; repasses federais SUS de 2024 (Assistência Farmacêutica: R$ 191.055,78); população; saldo de dotação e estoque **desconhecidos** |
| Receitas SUS de 2024 | `organizacional/receitas_sus_2024.csv` | repasses federais fundo a fundo por mês e bloco (TCE-PB/SAGRES) |
| Despesa com medicamentos em 2024 | `organizacional/execucao_farmaco_2024_*.csv` | R$ 1.953.288,72 empenhados; por mês e por licitação |
| Pregões próprios de 2024 | `organizacional/historico_proprio_pregoes_2024.parquet` | PE 01/2024 (349 itens; só 4 resultados publicados) e PE 12/2024 (desconto sobre a tabela CMED: éticos 18,01%, genéricos 60,11%, similares 51,01%) |
| Preços praticados — BPS | `nacional/bps_precos_praticados.parquet` | 2020–2024, registros inseridos até 13/12/2024; 225.518 registros de medicamentos, 23 UFs |
| Preços praticados — Compras.gov.br | `nacional/comprasgov_precos_praticados.parquet` | pesquisa de preço oficial; 141.599 registros com resultado até 29/01/2025, 27 UFs, esferas municipal, estadual e federal |
| Contratações comparáveis | `nacional/pncp_comparaveis_*.parquet` | amostra dirigida do PNCP: 84 contratações (15 UFs), 4.988 itens e 269 resultados, só o que tinha sido publicado até 29/01/2025 |
| Limites regulatórios | `nacional/cmed_2025_01_*.parquet` | lista CMED publicada em 06/01/2025; PF e PMVG em todas as alíquotas; `aliquota_aplicavel_pb` marca a válida para Santa Luzia |
| Padronização | `padronizacao/` | CATMAT por atributos (catálogo BPS e catálogo oficial), vínculos com a CMED classificados, regras de conversão com verificação, grupos BPS e registros Compras.gov.br compatíveis |

## 3. Regras de leitura

- **Não misture categorias de valor** (`categoria_valor`). São coisas diferentes:
  - preço praticado por unidade de fornecimento (BPS e Compras.gov.br);
  - preço estimado ou homologado por outros órgãos (PNCP);
  - limite regulatório por embalagem (CMED).
- **CMED: teto e CAP.**
  - O PMVG é teto obrigatório **só** para produtos com CAP (`cap = true`). Nos demais, vale apenas em compras por decisão judicial; nos outros casos o teto é o PF.
  - O PMVG publicado **já inclui** o CAP: não aplique o desconto de novo.
- **CMED: alíquota de ICMS para Santa Luzia/PB** (`aliquota_aplicavel_pb = true`):
  - **0%** para produtos isentos (coluna "ICMS 0%") e para os do **Convênio ICMS 87/02**, que isenta as vendas à administração pública municipal;
  - **20%** para os demais (Lei estadual 6.379/96, art. 11, I).
  - As condições do Convênio não foram conferidas produto a produto.
  - `teto_cmed()` já filtra essa alíquota; as demais colunas continuam disponíveis.
- **Vínculos item × CMED:**
  - `exata` e `compativel_conversao` têm fator de conversão por regra.
  - Em `padronizacao/regras_conversao.csv`, cada vínculo traz uma verificação automática (`verif_*`) e, numa amostra, o veredito de uma inspeção textual feita por IA. Nenhum passou por **validação humana**.
  - Vínculos "COM ALERTA" devem ser conferidos antes de uso decisivo.
  - `provavel_conferencia` e `indeterminada` não convertem.
  - `incompativel` não pode ser usado: por exemplo, a insulina pedida em 3 mL com sistema de aplicação não equivale a frasco de 10 mL nem a refil.
- **Compras.gov.br:** a compatibilidade com o item está em `padronizacao/item_comprasgov_registros.parquet`. Só `compativel` serve como preço do item; `a_conferir: …` exige conferência. `flag_possivel_duplicata_bps` marca registros que podem repetir um registro do BPS.
- **BPS:** `flag_preco_extremo` e `flag_duplicata_negocio` marcam registros suspeitos, que **não foram removidos**.
- Preços históricos não são ofertas atuais.
- **Estimativa do órgão:** em 41 itens (39,4% do valor estimado) o preço unitário estimado está acima do maior teto CMED unitário aplicável (`alerta_estimativa_acima_teto_cmed`). É um dado do caso, não um preço de mercado.

## 4. O que não se sabe

- **Demanda, estoque e orçamento:** consumo real por item; estoque existente na data de decisão (não há posição histórica disponível); saldo orçamentário exato.
- **Mercado:** preços que o mercado vai oferecer; desabastecimento de mercado; prazos reais de entrega; atas vigentes de outros órgãos para adesão.
- **Lacunas do pacote:**
  - 66 itens sem código CATMAT pré-corte, entre eles as insulinas em caneta: no catálogo, o código de insulina é genérico e a apresentação só aparece na unidade de fornecimento.
  - 56 itens (7,7% do valor) sem preço praticado compatível.
  - 25 itens (29,7% do valor) só com preço praticado "a conferir". Entre eles estão as **insulinas humanas NPH e Regular em caneta (itens 196 e 199)**, para as quais não há preço praticado identificado explicitamente como caneta. Há teto CMED e uma estimativa de outro município.

## 5. Hipóteses fixadas pelo experimento

- **H1:** a quantidade do ETP é a estimativa oficial de 12 meses; a demanda real é incerta.
- **H2:** R$ 4.952.438,00 é a referência de recurso reservada à necessidade; R$ 1,95 mi foi o gasto efetivo de 2024.
- **H3:** preços futuros são desconhecidos; só as referências deste pacote podem ser usadas.
- **H4:** falta de informação sobre desabastecimento não significa disponibilidade.

## 6. Como consultar

`scripts/consulta_agente.py` abre estas tabelas no DuckDB sem carregá-las inteiras na memória.

- **Funções:**
  - `necessidades(con)`
  - `historico(con, item=…, uf=…, de=…, ate=…)`: BPS
  - `precos_compativeis(con, item)`: BPS, Compras.gov.br e PNCP, com fonte e categoria
  - `teto_cmed(con, item, aliquota=…, so_pb=True)`
  - `bloqueados(con, item)`
- **SQL livre** sobre as tabelas e as visões:
  - `v_bps_comparavel` e `v_bps_a_conferir`
  - `v_comprasgov_comparavel` e `v_comprasgov_a_conferir`
  - `v_cmed_teto_unitario`
  - `v_pncp_comparavel`
  - `v_bloqueados`
