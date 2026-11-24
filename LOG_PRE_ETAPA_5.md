# LOG — Pré-Etapa 5 (verificação das falhas, normas e preparação da avaliação)

23/11/2026. Resultados em `docs/19_pre_etapa5_verificacao_e_avaliacao.md`; índice dos arquivos em `etapa5/LEIA-ME.md`. **Nenhuma nota ou veredito de mérito foi atribuído ao agente.**

## 1. Preservação da Etapa 4
- Verificação somente leitura antes e depois do trabalho:
  - os 75 arquivos de `etapa4/ambiente_decisor/` conferem com `etapa4/registro/hashes_ambiente_depois.csv`;
  - os 7 arquivos de `etapa4/registro/` conferem com os hashes do `LOG_ETAPA_4.md`;
  - `data/decision_input/` confere com o `MANIFESTO.csv`.
- A reprodução (script 32) rodou em cópias, em `etapa5/reproducao/`, e verifica por *assert* que `etapa4/` não mudou.

## 2. Falhas apontadas pelo agente (`scripts/31_verifica_falhas_pacote_v2.py`)
- **F1, itens 194/195:** confirmada e mais ampla. O atributo TIPO da insulina não era comparado; além disso, um tubete estava compatível com caneta.
- **F2, item 197:** confirmada. A pré-mistura 70N/30R estava vinculada como NPH.
- **F3, item 268:** não confirmada. A conversão está certa; o teto CMED é que fica 25× o preço praticado.
- **F4, Convênio 87/02:** fato da fonte. A lista CMED não publica 20% para 2.810 registros.
- **Pacote v2:** `data/decision_input_v2/` (v1 + `ERRATA.csv` E-01 a E-05), com manifesto próprio e autoverificação por *assert*.

## 3. Normas (fontes oficiais)
- **Lei 14.133, art. 86, §3º, II (Lei 14.770/2023):** a adesão de município a ata municipal licitada era permitida em 29/01/2025. Lido no Planalto por um agente de leitura web.
- **Decreto 12.343/2024:** R$ 62.725,59 (art. 75, II), em vigor de 01/01/2025 a 31/12/2025. Lido no Planalto.
- **Insulinas humanas NPH e Regular:** aquisição centralizada pelo MS, em frascos e canetas/tubetes (PRC nº 2/2017, Anexo XXVIII, art. 35).
  - Fontes: NT 169/2022 (29/04/2022) e NT 164/2023 (31/05/2023), arquivadas em `data/raw/complementares/normas_etapa5/`.
  - As NTs de 2026 encontradas na mesma página são posteriores ao corte e não foram arquivadas.
- **Falha:** o download local das páginas do Planalto foi recusado pelo servidor (curl 56, "Connection was reset"). Não houve nova tentativa.

## 4. Avaliação (preparação)
1. **Protocolo pré-registrado:** `etapa5/PROTOCOLO_AVALIACAO.md`, com sha256 `b61f65dc…` registrado às 21:11, antes de rodar o script 33. O arquivo não mudou depois.
2. **`scripts/32_reproduz_agente.py`:** 6 de 6 scripts do agente rodaram, sobre v1 e v2. As 13 saídas numéricas são idênticas às congeladas.
3. **`scripts/33_avaliacao.py`:** 20 de 20 verificações conferem. Gera a comparação com os dados reservados, a viabilidade, 9 cenários de sensibilidade (nenhum muda a decisão) e a economia em três níveis.
   - Ajustes de implementação feitos durante a execução, sem mudar regras do protocolo:
     - B1: o plano arredonda preços a 4 casas, então a soma usa `valor_ref_total`;
     - B5: comparação por tolerância, porque o arredondamento do NumPy difere do arredondamento do Python;
     - B8: a regra ME/EPP é reportada pelas duas bases de valor.

## 5. Comandos
```
python -I -X utf8 scripts/31_verifica_falhas_pacote_v2.py .
python -I -X utf8 scripts/32_reproduz_agente.py .
python -I -X utf8 scripts/33_avaliacao.py .
```

## 6. Hashes (sha256)
```
b61f65dcdc4b7581866def868ee3bcfe2b31054b742007165eb5087f518f1af4  etapa5/PROTOCOLO_AVALIACAO.md
c0637cebe95f73a09d5ddcf466c7c45057497e6fa119d4a7f567614a480fe37d  etapa5/verificacao/falhas_pacote.csv
6db38817b53196fac5c84e12f727f45cb90d39edcda501b287c1613ef41f4025  etapa5/verificacao/impacto_itens.csv
dcae64f7e69c4519770de8083576ff33bb2c51957e1fc0d1a8898508d620638f  etapa5/avaliacao/comparacao_itens.csv
cadc06cc1089298589956ba4ee77986caf01f0fed4965ff56cae41cfc842221d  etapa5/avaliacao/comparacao_resumo.csv
7b9ca44e93738dd1962f46d293205affcced0ec7a5894915b0142908c1b8ff13  etapa5/avaliacao/economia_niveis.csv
9dadde70f8bebd8b82b7829dc48d19290a8e187ee3e3bdd3f4e7dc7f27135084  etapa5/avaliacao/execucao.csv
68dfad8f2d88fe1a8b02b6fe287b33fb28f857b6ce540cefcfd113b2363e5401  etapa5/avaliacao/reproducao.csv
83e88248d3b49086ca389fe250b9c9929d09fb8f2ce02e55bd16fed2fb3a11ec  etapa5/avaliacao/sensibilidade.csv
dc10b16879f1b735f0e2a618ec2795b19ff99190145497333916a69fc310be77  etapa5/avaliacao/verificacao_calculos.csv
cfd56e15e40d1e0b0e679547105b93582109f934218e70ec6d495a1638b3390b  etapa5/avaliacao/viabilidade.csv
39fe3a8bf3261500457ccbe740e6246e5f7075fae1b2a08e2b75ce7c43653555  etapa5/avaliacao/resumo.json
8bbae7c7843df60970f6d110657df6b689a3e26008f085468ca2b1ca78cf01da  data/decision_input_v2/MANIFESTO.csv
5ccd5813a2e6af27bf273736d2bef81481e3061be2a0699763bc1858232e897b  data/decision_input_v2/ERRATA.csv
121c3cc9bde08c9d92c60e62cdc2e62d38c464c6a3b134f8780957f7dc5f7b0e  data/raw/complementares/normas_etapa5/ms_nota_tecnica_164_2023_logistica_insulina.pdf
b35d297eec09b27c249c9c7ed7596d2f59959760901f04bce2968bf40cffc939  data/raw/complementares/normas_etapa5/ms_nota_tecnica_169_2022_canetas_insulina.pdf
```

## 7. Pendências para a Etapa 5 (atualizadas no §8)
- **Julgamento de mérito:** de preferência por avaliador cego, porque a sessão que preparou os dados os conhece.
- ~~Canetas 196/199: esclarecer a unidade comprada.~~ **Resolvido no §8:** a unidade é a caneta. Continuam sem prova o produto contratado e a quantidade entregue.
- **Contrato de desconto PE 12/2024:** não há preço por item. A comparação E1 × E2 continua sendo modelo.

## 8. Unidade das insulinas em caneta (`scripts/34_canetas_insulina.py`; doc 20)

**Downloads do PNCP** (contratação 09090689000167-1-000006/2025, API `…/compras/2025/6/arquivos/N`), todos HTTP 200 e guardados em `data/raw/pncp/etapa2/09090689000167_2025_6/docs/`:
- 7 contratos (arquivos 5–11);
- 1 e-mail de fornecedor (3);
- Ata Parcial e Ata Final (15, 16), em zip, extraídas em pastas próprias depois de checar os caminhos;
- da contratação do PE 09/2026, só a Ata Final (9), em `…_2026_26/docs/`, usada apenas como contexto.

**Resultado:**
- **Unidade:** "Caneta" no ETP (p. 24), no TR (p. 34), no Contrato 00054/2025 (p. 5) e no Aditivo 01 (p. 4); "UN" na Ata Final (p. 6); "Unidade" no PNCP. 30 trechos conferidos automaticamente, nenhuma menção a caixa.
- **Propostas:** uma única proposta por caneta (ALLFAMED), com marca/fabricante EQUIPLEX. Na CMED de jan/2025, a EQUIPLEX tem 68 apresentações e nenhuma insulina.
- **Teto CMED por caneta:** NPH R$ 20,14 e Regular R$ 15,80. O contratado é 9,6× e 9,3× esse valor.
- **Avaliação:** só o C4 muda (15 → 17 itens; excesso de R$ 1.280.392), em `etapa5/avaliacao_canetas/correcao_C4.csv`.

**O que não se obteve:**
- a proposta readequada (pedida em 20/02/2025), que não foi publicada;
- itens e quantidades nos empenhos (TCE-PB), cujos históricos são genéricos;
- notas fiscais e atestados de recebimento, que não são públicos (só por LAI).

**Integridade:** depois do trabalho, conferem com os hashes registrados:
- `etapa4/`;
- o pacote v1;
- as saídas anteriores de `etapa5/avaliacao/` e o protocolo.

**Hashes (sha256):**
```
90c4254f42dce5adaea9dad4b132f2e8d4ba5b7b29eb82f3c13d664ee9f1347c  data/raw/pncp/etapa2/09090689000167_2025_6/docs/01_edital.pdf
b11efd57d31090743e446c8645a7745c9ce2abc8d2f7e36732420379a0b35a5d  data/raw/pncp/etapa2/09090689000167_2025_6/docs/05_arquivo.pdf  (Contrato 00054/2025)
6b3b75601c4bbf3b5c5fc76136ee43e383e6062990ee8b9b2ea1a1cc5e0e437b  data/raw/pncp/etapa2/09090689000167_2025_6/docs/12_aditivo.pdf  (Aditivo 01)
121ac2f28e334b17249df4d80d06dd604068731a680b5f1b32b73c784bd525e8  data/raw/pncp/etapa2/09090689000167_2025_6/docs/16_arquivo.zip  (Ata Final)
016237bbd4eeedc3cae44b9864aa41047865916321a5e422f46cd35c1c7c9a0c  data/raw/pncp/etapa2/09090689000167_2025_6/docs/15_arquivo.zip  (Ata Parcial)
0999e5d879602009a69e4b6be1353fb3ceab887e879ffc0132880a6eaae11e0d  data/raw/pncp/etapa2/09090689000167_2026_26/docs/09_ata_final.zip
0bee26936c09da40deb4d29aa968cbbccd20c51f02339a24da91c3ec0013c63c  etapa5/avaliacao_canetas/evidencias_documentais.csv
038a303cc194fa2c8b0e982197aef5e93e1a3b1b254d283f1b370dad8a9716ae  etapa5/avaliacao_canetas/cmed_canetas_compativeis.csv
4967c02eacd9a9209f37f22363628e291c9bb8a85e33b016e27d47e7241b4d07  etapa5/avaliacao_canetas/impacto_canetas.csv
65ba07cfd9f90de034d712f019ecfaf5c07dd32eb3f494240a9f48fe2cb10089  etapa5/avaliacao_canetas/correcao_C4.csv
```

**Preparação da Etapa 5 concluída** (doc 20, §5). Falta o julgamento de mérito.
