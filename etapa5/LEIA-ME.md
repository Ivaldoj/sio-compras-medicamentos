# Etapa 5 — material preparado para a avaliação independente

Os resultados e as limitações estão em `docs/19_pre_etapa5_verificacao_e_avaliacao.md` e `docs/20_unidade_canetas_insulina_e_prontidao_etapa5.md` (unidade das canetas e prontidão para a Etapa 5); a cronologia e os hashes, em `LOG_PRE_ETAPA_5.md`. A Etapa 4 congelada (`etapa4/`) e o pacote v1 (`data/decision_input/`) não foram alterados.

| Caminho | Conteúdo |
|---|---|
| `PROTOCOLO_AVALIACAO.md` | Regras da avaliação, pré-registradas antes do cálculo |
| `verificacao/falhas_pacote.csv` | Veredito, causa, evidência e impacto das 4 falhas apontadas pelo agente |
| `verificacao/impacto_itens.csv` | v1 × v2 nos itens 194, 195 e 197 |
| `reproducao/v1/`, `reproducao/v2/` | Cópias em que os scripts do agente foram reexecutados: pacote original e pacote com errata |
| `avaliacao/reproducao.csv` | Execução e comparação byte a byte com as saídas congeladas |
| `avaliacao/verificacao_calculos.csv` | 20 verificações dos números e das regras do agente |
| `avaliacao/comparacao_itens.csv` | Por item: referência do agente, faixa, teto, homologado no PE 04/2025 e mediana nacional de 2025 |
| `avaliacao/comparacao_resumo.csv` | Os mesmos indicadores por grupo (insulinas, a conferir, sem referência, acima do teto, fonte) |
| `avaliacao/execucao.csv` | Contratos do PE 04/2025: homologado × empenhado × pago |
| `avaliacao/viabilidade.csv` | Evidências ex ante e ex post por dimensão, sem nota |
| `avaliacao/sensibilidade.csv` | 9 cenários sobre as fórmulas do agente; indica se a recomendação muda |
| `avaliacao/economia_niveis.csv` | Economia projetada, contratada e realizada (separadas, com observabilidade) |
| `avaliacao/resumo.json` | Números-chave |
| `avaliacao_canetas/evidencias_documentais.csv` | Unidade, quantidade, preço e marca das canetas em 8 fontes oficiais, com página e trecho conferidos |
| `avaliacao_canetas/cmed_canetas_compativeis.csv` | Canetas registradas na CMED de jan/2025, por tipo, com teto por caneta |
| `avaliacao_canetas/impacto_canetas.csv` | Preço contratado × teto por caneta, mais a hipótese de caixa (não documentada) como teste |
| `avaliacao_canetas/correcao_C4.csv` | Correção do indicador C4: 15 → 17 itens acima do teto. Substitui o C4 de `avaliacao/`, que fica preservado |
| `avaliacao_canetas/contexto_pe_09_2026.csv` | Propostas do PE 09/2026 para os mesmos itens (só contexto) |

**O pacote corrigido** está em `data/decision_input_v2/` (`ERRATA.csv`, `MANIFESTO.csv`; nota no `LEIA-ME.md`).

**Para regerar tudo:**
```
python -I -X utf8 scripts/31_verifica_falhas_pacote_v2.py .
python -I -X utf8 scripts/32_reproduz_agente.py .
python -I -X utf8 scripts/33_avaliacao.py .
python -I -X utf8 scripts/34_canetas_insulina.py .   # requer os documentos do PNCP em data/raw/pncp/etapa2/
```

**Prontidão:** todos os componentes da preparação estão concluídos (doc 20, §5). Falta o julgamento de mérito da Etapa 5, de preferência por avaliador cego.

**Atenção:** este diretório contém dados posteriores ao corte. Ele **não deve ser fornecido a nenhum agente decisor**.
