# evaluation_only — NÃO FORNECER AO AGENTE DECISOR

Dados posteriores ao corte de 2025-01-29 (ou derivados deles), reservados para avaliar a decisão. O módulo
`scripts/consulta_agente.py` recusa caminhos fora de `data/decision_input/`.

- organizacional/: resultado homologado do PE 04/2025, execução por contrato, despesa 2025–2026, pregões 25/2025 e 09/2026,
  contratos; cópia em parquet de `data/processed/caso_santa_luzia/reservado_avaliacao/` (Etapa 2) e de `data/raw/pncp/etapa2/`.
- nacional/: BPS inserido após o corte; resultados/itens/contratações PNCP publicados após o corte; preços Compras.gov.br
  com resultado após o corte (`comprasgov_pos_corte.parquet`, pré-Etapa 4).
- auditoria/: comparação do CATMAT da Etapa 2 (obtido com dados pós-corte) com a identificação pré-corte.
- Fontes brutas pós-corte ainda fora daqui: `data/raw/complementares/cmed_lista_pmvg_20261109.xlsx` (CMED nov/2026),
  `data/raw/ms_api/` (estoque BNAFAR de nov/2026), `data/raw/complementares/tcepb/*2025*|*2026*`.
