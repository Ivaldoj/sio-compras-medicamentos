# LOG — Etapa 3 (preparação e integração dos dados)

23/11/2026. Data de corte: 29/01/2025. Arquivos das Etapas 1 e 2 preservados (nenhum documento anterior editado).

## 1. Verificações iniciais
- Itens do PNCP sem CATMAT (`catalogoCodigoItem` vazio) em todas as contratações examinadas, inclusive federais. O CATMAT do Medicamentos Transparentes (MT) é classificação da própria plataforma.
- Datas de publicação: resultados do PE 12/2024 incluídos no PNCP em **30/04/2025** (resultado de 11/04/2024); resultados do PE 01/2024 incluídos em 02/09/2024.
- Edital do PE 04/2025 assinado em "Santa Luzia - PB, 29 de janeiro de 2025".
- Universo MT com início de disputa ≤ corte e objeto de medicamento: 8.280 contratações (27 UFs).
- O PNCP não tem endpoint de resultados por contratação (`/itens/resultados` → 400; `/resultados` → 403).

## 2. Dependência e downloads
- `pip install duckdb` → 2.0.1 (pedido no enunciado).
- BPS 2020, 2021, 2022 e 2023 (`02_download.py`, SHA-256 no manifest). Os tamanhos diferem levemente do HEAD da Etapa 1 (arquivos republicados em 20/11/2026).

## 3. Scripts e resultados
- `24_bps_historico_temporal.py`: BPS 2020–2026 (376.580 registros; 35 colunas iguais em todos os anos) → disponível 286.467 / posterior 87.960 / indeterminado 2.153. Pacote: 225.518 registros de medicamentos (classe 6505). Marcas: 3.008 preços extremos e 473 duplicatas de negócio (no pacote).
- `padroniza.py`: regras e 31 autotestes. Correções feitas durante a etapa:
  - **mistura 70/30** e **caneta × refil** (Humulin 70/30 e carpules eram aceitos para a NPH com sistema de aplicação);
  - comprimido/cápsula ambíguos;
  - "g" como concentração (ceftriaxona 1 g) e normalização mg/g/mcg;
  - forma genérica "injetável";
  - associações no catálogo ("COMPOSIÇÃO: ASSOCIADO À …");
  - "PÓ P/ SOLUÇÃO INJETÁVEL";
  - "60 mg/0,6 mL" → 100 mg/mL;
  - sinônimos entre parênteses;
  - grafia benzerazida/benserazida;
  - abreviação CMED "CM".
  - Um patch via heredoc inseriu caracteres de controle (backspace) em 3 expressões regulares; detectado e corrigido, e as correções seguintes passaram a ser feitas por arquivo.
- `25_padronizacao_vinculos.py`:
  - CATMAT pré-corte: 210 único, 32 múltiplo, 14 parcial, 78 ausente.
  - CMED: 20.369 pares (252 exatos, 4.616 compatíveis, 64 prováveis, 232 indeterminados, 15.205 incompatíveis).
  - Revisão das 259 da Etapa 2: 20 exata, 148 compatível, 9 provável, 69 incompatível, 13 indeterminada.
  - Auditoria × Etapa 2: 95,9% de concordância (217 itens).
  - Pendências: 296 para conferir e 1.611 bloqueados.
  - O intermediário `itens_atributos.parquet` foi movido para `data/processed/etapa3/`: o script 27 apagava um arquivo que o 26 ainda lia.
- `26_pncp_comparaveis.py`:
  - Seleção gulosa de 66 contratações (16 UFs; cobertura de 195 itens via índice).
  - Download em segundo plano, cerca de 6 minutos por contratação (resultados item a item, pausa de 3 s). **Interrompido de propósito após 14 contratações**; 52 listadas em `data/raw/pncp/etapa3/nao_baixadas.csv`. Retomável pelo cache.
  - Consolidação: contratações 13 disponíveis / 1 posterior; itens 1.091 / 60; resultados **102 / 173**.
  - O download usou a versão das regras vigente no momento. A consolidação usa a final, então itens que passaram a casar depois podem estar sem resultado consultado.
- `27_montar_pacotes.py`: CMED longa (941.578 preços), itens com status, organizacional (restrições, recursos, despesa 2024, pregões 2024), `evaluation_only` (PE 04/2025, contratos, execução, pregões 25/2025 e 09/2026) e manifesto (17 arquivos, SHA-256).
- `consulta_agente.py`: visões DuckDB e funções; recusa caminhos fora do pacote.
- `28_verificacoes.py`: 75 testes, todos passando. Falhas encontradas no caminho e corrigidas:
  - CMED sem `data_disponibilidade`;
  - falso positivo da varredura de valores, porque "586816" aparecia dentro de identificadores (padrão restrito a formato monetário);
  - item 76 sem histórico (defeito de regra de forma sólida);
  - produto cartesiano numa consulta do teste;
  - precedência de AND/OR num filtro.

## 4. Decisões
- Informação interna do órgão com data ≤ corte conta como disponível (edital, despesa 2024, contrato do PE 12/2024). Dados de terceiros exigem data de publicação ≤ corte.
- O MT é usado só como índice; não entra no pacote.
- Vínculos e conversões só por regras explícitas; nada provável é tratado como equivalente. Bloqueios testados.
- Alíquota de ICMS da PB não escolhida; PMVG nunca recalculado.
- Nenhum item excluído; lacunas medidas em % do valor.

## 5. Pendências
- Validação humana das conversões aceitas (4.868 vínculos).
- 52 contratações PNCP não baixadas.
- 78 itens sem CATMAT (41,0% do valor; insulinas em caneta: 27%).
- Alíquota de ICMS aplicável na PB.
