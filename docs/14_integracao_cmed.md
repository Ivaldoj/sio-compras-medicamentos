# 14 — Integração da CMED de janeiro de 2025

> **Atualização pré-Etapa 4 (23/11/2026):** a alíquota de ICMS aplicável a Santa Luzia/PB foi **determinada** (0% para isentos e Convênio ICMS 87/02; 20% nos demais) e está em `aliquota_aplicavel_pb`; teto disponível para 226 itens (77,8% do valor). Estado atual e números em `docs/18_pre_etapa4_tratamento_lacunas.md`; o texto abaixo descreve a Etapa 3.

Fonte: Lista CMED de Preços Fábrica e Preços Máximos de Venda ao Governo, **"Publicada em 06/01/2025 às 14h00min"** (arquivo `xls_conformidade_gov_20250107_175641971.xls`), vigente na data de decisão. A lista de 09/11/2026 (Etapa 1) **não** entra no pacote.

## 1. Tabelas

- `cmed_2025_01_apresentacoes.parquet` (25.549 linhas, chave `registro`): substância, laboratório, produto, apresentação, tipo de produto, regime, restrição hospitalar, `cap`, `icms_isento_so_0pct`, `convenio_confaz_87`, tarja, embalagem extraída e `teto_compras_administrativas` (PMVG se CAP, senão PF).
- `cmed_2025_01_precos.parquet` (941.578 linhas, chave `registro` + `tipo_preco` + `aliquota_icms`): **todas as colunas de PF e PMVG preservadas**, sem impostos, 0%, 12%, 17%, 17,5%, 18%, 19%, 19,5%, 20%, 20,5%, 21% e 22%, com e sem ALC (área de livre comércio). Campos `aplicabilidade`, `aliquota_status` e `categoria_valor = limite_regulatorio_por_embalagem (não é preço praticado)`.

## 2. Regras aplicadas (citadas do cabeçalho da própria lista)

| Regra | Texto da lista (trecho) | Implementação |
|---|---|---|
| PF × PMVG | "PMVG é o resultado da aplicação do Coeficiente de Adequação de Preços (CAP) sobre o Preço Fábrica – PF, PMVG = PF*(1-CAP)… o CAP é de 21,53%" | PMVG **lido da lista**, nunca recalculado. Teste: PMVG/PF = 0,7847 ± 0,01 em todos os pares |
| Aplicabilidade do PMVG | "O PMVG deverá ser… utilizado como referência, obrigatoriamente, para todos os produtos destacados pela sigla CAP. Para as demais apresentações… somente em compras por força de decisão judicial. Nos demais casos… o Preço Fábrica – PF" | `aplicabilidade`: PMVG com CAP = "teto obrigatório (produto com CAP)"; PMVG sem CAP = "somente compras por força de decisão judicial"; PF sem CAP = "teto para compras administrativas"; PF com CAP = "não é o teto para governo" |
| ICMS | "Para os medicamentos isentos de ICMS… são disponibilizados apenas os preços na alíquota de ICMS 0%" | 1.034 apresentações isentas: só 0% é válida. Demais: `aliquota_status = depende da alíquota de ICMS aplicável na PB — não determinada` |
| Convênio 87/2002 | cita o Acórdão TCU 140/2012 e a isenção de ICMS nas aquisições públicas | 2.810 apresentações com `convenio_confaz_87 = true` marcadas como "possível isenção… adesão/condições na PB não verificadas"; nenhuma alíquota é escolhida |

**Não feito, de propósito:** escolher a alíquota da Paraíba; aplicar o CAP ao PF ou ao PMVG; tratar o teto como preço de mercado.

## 3. Vínculo com os itens e teto por unidade

- Vínculo: `padronizacao/item_cmed_vinculos.parquet` (doc 13). O teto por unidade do item só existe para `exata` e `compativel_conversao`: `valor_por_unidade_item = valor_embalagem / fator_conversao` (visão `v_cmed_teto_unitario`).
- Prováveis, indeterminados e incompatíveis ficam fora do teto e aparecem em `v_bloqueados`.

| `status_teto_cmed` | Itens | % do valor estimado |
|---|---|---|
| disponível (conversão por regra) | 222 | 73,9% |
| a conferir (só prováveis/indeterminados) | 35 | 8,0% |
| bloqueado/incompatível (só apresentações distintas) | 55 | 11,3% |
| ausente (nenhuma apresentação do princípio) | 22 | 6,7% |

- 29 dos 222 itens com teto disponível têm pelo menos uma apresentação **com CAP**. Para eles, o teto administrativo é o PMVG.
- Um item com vários vínculos aceitos tem vários tetos (por laboratório e embalagem). O pacote não escolhe um.

## 4. Situação

Integração **concluída para uso com ressalvas**:
1. Alíquota de ICMS indeterminada: o teto existe como faixa entre alíquotas, não como valor único.
2. Conversões aceitas por regra, sem validação humana.
3. 112 itens (26,0% do valor) sem teto utilizável (35 a conferir, 55 bloqueados, 22 ausentes).
4. A lista vale para jan/2025. Reajustes posteriores da CMED (abr/2025) são informação futura e não foram usados.
