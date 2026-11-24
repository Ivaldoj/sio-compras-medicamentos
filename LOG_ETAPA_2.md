# LOG — Etapa 2 (definição do caso organizacional)

23/11/2026. Só as atividades e descobertas novas; os arquivos da Etapa 1 foram preservados (nenhum documento da Etapa 1 foi editado; correções estão registradas aqui e em `docs/09`).

## 1. Triagem das candidatas com dados existentes
- `scripts/17_candidatas.py` sobre os parquet da Etapa 1 → `reports/etapa2_candidatas_resumo.csv`, `etapa2_contratacoes_candidatas.csv`, `etapa2_candidatas_stdout.txt`. Candidatas: SES-PB, Campina Grande, Fundação PB Saúde, EBSERH (HUs PB), Salgadinho, Santa Luzia.
- Observação: no MT, a SES-PB só tem dispensas (126). Seus pregões provavelmente correm pela Secretaria de Estado da Administração (inferência não verificada).

## 2. Descoberta: o Medicamentos Transparentes corta em 10 itens
- Distribuição de itens por contratação no MT-PB: máximo 10 (281 contratações com exatamente 10).
- PNCP `/itens/quantidade`: 38 (Campina Grande 2025/159) e 334 (Santa Luzia 2025/6), contra 10 no MT. O JSON/OCDS da PB 2026 tem o mesmo corte.
- Consequência: as contagens de itens e CATMAT da Etapa 1 estão subestimadas; nesta etapa os itens vêm do PNCP.

## 3. PNCP — contratações completas (`scripts/18_pncp_compra_completa.py`, cache em `data/raw/pncp/etapa2/`)
- Cabeçalho, itens, documentos e atas: Campina Grande 2025/159 (38 itens), Santa Luzia 2025/6 (334), PB Saúde 2025/13 (33), HULW 2026/882 (151; ata 00250/2026), Santa Luzia 2025/99 (87) e 2026/26 (329), Santa Luzia 2024/1 (349; PNCP "em andamento") e 2024/14 (3 itens, desconto CMED).
- Resultados por item (`--resultados`, pausa de 3 s): 2025/6 **334/334**; 2025/99 78/78; 2024/1 4; 2024/14 3; 2026/26 326/326 (concluído depois; dado pós-decisão, reservado; não usado nas análises).
- Contratos: `/consulta/v1/contratos` exige janelas ≤ 365 dias (HTTP 422 com janela maior); recebeu HTTP 504 e 500 em algumas páginas; uma página de 2026 ficou sem resposta, então a lista de contratos do PE 09/2026 pode estar incompleta. Termos aditivos estruturados: 204 nos 7 contratos; os aditivos existem só em PDF (arquivos 12–14).
- PCA: Santa Luzia 2025/2026, Campina Grande (Município e FMS) 2025 e PB Saúde 2025 → nenhum item.
- Edital HULW (`/arquivos/1`) → HTTP 422 (não obtido).

## 4. Documentos (downloads registrados em `reports/manifest_fontes.csv`)
- Editais: Santa Luzia PE 04/2025 (PDF de 56 p.); Campina Grande e PB Saúde vieram como **ZIP com extensão .pdf** e foram renomeados para `01_edital.zip` (conteúdo intacto; o manifest guarda o nome original `.pdf`).
- Aditivos 12–14 do PE 04/2025.
- `scripts/19_textos_documentos.py`: texto dos PDFs (inclusive dentro de ZIP, lido em memória) → `data/processed/etapa2_textos/`. O edital de Campina Grande é digitalizado (13,6 mil caracteres em 67 páginas).

## 5. TCE-PB (Santa Luzia, cód. 170)
- Despesas 2024, 2025 e 2026 (até 31/08/2026) e licitações 2024–2026.
- `scripts/20_caso_santa_luzia_despesas.py` → `reports/caso_sl_farmaco_*.csv`. Medicamentos = subelemento "Material Farmacológico" mais o elemento 32 com "medicament" no histórico. Empenhado: 2024 R$ 1.953.288,72; 2025 R$ 1.410.230,18; 2026 R$ 1.350.148,81.
- O número da licitação nos empenhos (`000042025`) também é usado por procedimentos que não são de medicamentos; o filtro por subelemento evita misturá-los.

## 6. Itens, preços e execução do caso
- `scripts/21_caso_santa_luzia_itens.py`: PNCP sem CATMAT (`catalogoCodigoItem` vazio). CATMAT recuperado para 299/334 itens via BPS (fornecedor + preço + quantidade; 7 chaves ambíguas). BPS inserido até 29/01/2025: 285 itens com preço.
- Novos dados: BPS 2024 (`2024_csv.zip`, 2,86 MB). Descoberta: o BPS de Santa Luzia registra contratos na data de homologação (315 registros de 11/03/2025 inseridos em 22/12/2025).
- Execução por contrato (TCE × PNCP) → `reports/caso_sl_execucao_contratos.csv`: PE 04/2025 com 18,9% empenhado até ago/2026.
- Anomalias do PNCP: contrato 2-000249/2025 com valor 0; `valorGlobal` = 1/100 do inicial em 2 contratos.

## 7. Fontes complementares
- CMED: página "anos anteriores" → PMVG de 07/01/2025 baixada (27,4 MB, `.xls` BIFF). Processada depois de o usuário autorizar a instalação do `xlrd` (seção 11).
- Busca na web: (a) "Preço de Referência" do TCE-PB — guia baixado; janela móvel de 12 meses, inútil para jan/2025; (b) lista estadual de desabastecimento (CEDMEX, 13/09/2024) — o portal devolveu **CAPTCHA**; não foi contornado. O arquivo salvo é a página HTML, renomeada para `…_BLOQUEADO_captcha.html`; (c) Portaria TCE-PB 138/2023 — texto não localizado.
- IBGE: população de Santa Luzia, 15.387 (2024).

## 8. Separação pré/pós-decisão
- `scripts/22_caso_pacotes_decisao.py` → `data/processed/caso_santa_luzia/pre_decisao/` (4 arquivos) e `reservado_avaliacao/` (6 arquivos). Autoverificação: nenhuma coluna de resultado no pacote pré-decisão; 334 itens com quantidade.

## 9. Decisões metodológicas
- Caso: Santa Luzia/PB, PE 04/2025; data de decisão 29/01/2025; horizonte de 12 meses.
- Restrições incluídas no problema: só as legais e os fatos operacionais. Escolhas de desenho do órgão (modalidade, critério, garantia, prazo de entrega, contrato de 12 meses) foram tratadas como **decisão observada** e reservadas.
- Nenhuma alternativa, estratégia, fornecedor ou rateio foi proposto.

## 10. Pendências
- CMED jan/2025: conferir apresentação e converter embalagem→unidade nos 259 itens vinculados.
- Regras de estimativa contrafactual (próxima etapa).
- Consumo por item e estoque: só via LAI.
- ~~Resultados do PE 09/2026~~ — baixados (326/326), reservados à avaliação.

## 11. CMED de jan/2025 (após autorização do usuário)
- `python -m pip install xlrd` → xlrd 2.0.2 (única dependência nova; adicionada a `requirements.txt`).
- `scripts/23_cmed_jan2025.py`: planilha única "Planilha1", cabeçalho na linha 53, 25.549 apresentações, 65 colunas, "Publicada em 06/01/2025 às 14h00min", CAP 21,53%. Regulado 22.791; liberado 2.758; CAP=Sim 2.568; restrição hospitalar 3.911. Os nomes de coluna diferem da lista de nov/2026 (espaços em "PF 12 %", coluna "COMERCIALIZAÇÃO 2022", erro de digitação "PF 20,5%2"). Saída: `data/processed/cmed_pmvg_20250107.parquet`.
- A planilha não informa a alíquota de ICMS da Paraíba; todas as colunas de alíquota foram mantidas no vínculo.
- Vínculo pré-decisão (item → CATMAT → registros Anvisa do BPS inseridos até 29/01/2025 → CMED): 263 itens com registro, **259 com ≥ 1 apresentação (79,7% do valor estimado)**, mediana de 3 apresentações por item, 14 itens com CAP=Sim. Saídas: `data/processed/caso_santa_luzia/pre_decisao/itens_cmed_jan2025.csv`, `reports/caso_sl_cmed_cobertura.csv`, `reports/caso_sl_cmed_stdout.txt`.
- Achado: o vínculo por CATMAT pode levar a outra apresentação (insulina pedida em 3 mL com sistema de aplicação × frasco-ampola de 10 mL na CMED; amoxicilina de 60 mL × 150 mL). Por isso é correspondência provável, sem conversão automática.
