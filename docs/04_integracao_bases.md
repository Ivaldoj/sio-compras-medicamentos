# 04 — Integração entre as bases

Testes reais executados em `scripts/09_integracao_bps_mt.py`, `13_cmed_pmvg.py`, `14_rastreio_mt_pncp.py`, `15_build_reports.py`, `16_bnafar_estoque.py`. Matriz completa: `reports/matriz_integracao.csv`.

## 1. Níveis de confiabilidade adotados

| Nível | Critério | Uso permitido |
|---|---|---|
| **Confirmada** | Chave nativa compartilhada (ocid, numeroControlePNCP, registro Anvisa de 13 dígitos) ou N3 + nº do processo compatível | Afirmar que é o mesmo registro/produto |
| **Provável** | Órgão/município + CATMAT + CNPJ do fornecedor + preço unitário (±0,5%) | Análise com marcação; nunca somar duas fontes |
| **Não verificável** | Só texto da descrição, só CATMAT, só nome do órgão | Não integrar; apenas comparar distribuições |

## 2. Medicamentos Transparentes interno (contratação → itens → resultados)

- `ocid` liga as 13 tabelas; `tender/items/id` = `awards/items/id` liga item licitado a item adjudicado; `awards/id` liga adjudicação a fornecedor.
- 48,0% dos itens licitados em PB têm adjudicação (o restante está em andamento, fracassado, deserto ou anulado).
- Risco: o mesmo `ocid` aparece em até 5 coletas na PB e até 7 no Brasil (20,1% dos 86.068 ocids nacionais repetem) → **deduplicar antes de qualquer soma**. Nenhum ocid aparece em arquivos de duas UFs.

## 3. Medicamentos Transparentes → PNCP

`id` do release tem o formato do `numeroControlePNCP` (`<cnpj>-1-<seq>/<ano>`). Amostra aleatória de 20 contratações PB (semente 42): **20 recuperadas, 20 com mesmo órgão e mesmo valor estimado** (`reports/rastreio_mt_pncp_amostra.csv`). Seis delas foram bloqueadas por HTTP 429 na primeira rodada (22/11) e obtidas na nova tentativa (23/11), todas na primeira chamada, com pausa de 3 s entre consultas. Para a contratação 08778268000160-1-000559/2026 foram recuperados também itens, resultado homologado (fornecedor, quantidade 60, R$ 8.465,31) e lista de documentos. **Rastreabilidade: confirmada.**

## 4. BPS ↔ Medicamentos Transparentes (PB, 2025–2026)

| Nível | Critério | Registros BPS-PB correspondentes (de 4.205) |
|---|---|---|
| N1 | CNPJ do órgão | 12,6% (4 de 21 órgãos: SES-PB, FMS 11164805000197, Sobrado, Serra Grande) |
| N1b | UF + município | 91,1% (19 de 21 municípios; faltam Lagoa de Dentro e Pedra Branca) |
| N2 | CNPJ + CATMAT | 1,1% (48) |
| N3 | CNPJ + CATMAT + fornecedor + preço ±0,5% | 0,2% (7) |
| N3b | Município + CATMAT + fornecedor + preço ±0,5% | 0,9% (39; 4 ambíguos com >1 ocid) |
| N4 | N3 + processo compatível | **0,1% (5)** — todos do FMS 11164805000197, processo 037/2025 = ocid …_2025_24, mesmas quantidades |

**Por que tão pouco?**
1. **Identificadores de órgão diferentes**: o BPS usa o CNPJ do Fundo Municipal de Saúde; o PNCP/MT, frequentemente o do Município (ex.: BPS "FMS – Salgadinho" × MT "Município de Salgadinho", CNPJ 08881666000108).
2. **Defasagem temporal**: compras de 2025 no BPS derivam de atas de 2024 ou antes (ex.: SES-PB, nitisinona, processo 2024/11591 a R$ 8.465,41 em fev/2025), enquanto o MT só cobre coletas desde jan/2025. O par N3 SES-PB × ocid `…_2026_559` coincide em preço, mas é outro processo — **falso positivo** que só o N4 elimina.
3. **Eventos diferentes**: o MT registra contratações (edital/resultado); o BPS registra compras/aquisições informadas pelo órgão.

**Conclusão**: não há chave confiável BPS↔MT/PNCP. A mesma compra pode estar nas duas fontes, mas isso só foi **demonstrado em 5 registros**. As bases devem ser usadas **separadamente**: BPS como referência de preço praticado; MT/PNCP como trilha do processo de contratação do órgão. Não somar valores das duas.

## 5. Produto: CATMAT entre bases

- 72,6% dos 1.281 CATMAT licitados em PB (MT) existem no BPS nacional (42,3% no BPS-PB); 82,7% dos itens MT-PB têm CATMAT presente no BPS.
- BNAFAR usa `BR0` + CATMAT + sufixo (`BR0267140U0042`); extraindo o número, 66,9% (CG) e 68,9% (JP) dos CATMAT em estoque existem no BPS. Significado do sufixo **não documentado**.
- **Ressalva**: mesmo CATMAT não garante unidade comparável — 250 CATMAT têm mais de uma unidade de fornecimento no BPS e o MT usa 330 grafias de unidade. Equivalência de preço exige CATMAT **e** unidade de fornecimento compatível (e capacidade, quando houver).

## 6. BPS ↔ CMED (registro Anvisa)

98,0% dos registros BPS de medicamentos com registro informado (38.776) encontram a apresentação de 13 dígitos na lista PMVG; 98,7% pelo registro do produto (9 dígitos). **Integração confirmada no nível produto/apresentação.** Limite: o PMVG é por embalagem (ex.: "CT BG AL X 40 G"), o BPS por unidade de fornecimento; a lista é a vigente (nov/2026), não a da data da compra.

## 7. TCE-PB ↔ BPS / MT

- CNPJ do credor ↔ CNPJ do fornecedor: em Salgadinho, 3 dos 5 fornecedores BPS de 2025 são credores de material farmacológico.
- Nº da licitação: 1 número em comum (`9/2025`).
- O empenho não identifica o medicamento → serve como **restrição orçamentária agregada e realizada**, não como item.

## 8. PNCP PCA ↔ demais

Na SES-PB 2026 o PCA usa catálogo "Outros" e agrega medicamentos num único código de natureza de despesa → **sem integração por produto**.

## 9. Recomendações técnicas

1. Chave do processo: `numeroControlePNCP` (MT/PNCP). Chave do produto: CATMAT + unidade de fornecimento (+ registro Anvisa quando houver). Chave do órgão: CNPJ normalizado a 14 dígitos **e** agrupamento por UF+município para unir Município e FMS.
2. Nunca integrar BPS e MT/PNCP no nível de transação sem N4.
3. Produzir um de-para de unidades do MT (330 grafias) antes de comparar preços.
4. Tratar o BNAFAR como fotografia de estoque, não série.
