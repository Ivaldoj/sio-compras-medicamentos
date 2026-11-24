# Inteligência em uma decisão de compra de medicamentos pelo SUS

Disciplina Sistemas de Informação nas Organizações (SIO) — UFPB. Caso: Secretaria Municipal de Saúde de Santa Luzia/PB.

## Objetivo

Demonstrar **inteligência** segundo a definição do professor Bellini adotada na disciplina: a **elaboração autônoma de cenários alternativos e a escolha do caminho mais eficiente**, em contraste com o **mero reconhecimento de padrões**.

**Pergunta.** Com as informações disponíveis na data da decisão, um agente de IA elabora cenários alternativos e escolhe o mais eficiente, ou apenas reproduz o padrão que os dados sugerem?

**Não são objetivos do trabalho:** demonstrar superioridade sobre gestores humanos, execução autônoma de contratações ou economia efetivamente realizada. O experimento é uma simulação sobre um caso já encerrado: a escolha do agente não é implementada, e a decisão real serve de régua para avaliar a qualidade dessa escolha.

## Leia primeiro

1. [`etapa6/RELATORIO_FINAL.md`](etapa6/RELATORIO_FINAL.md) — relatório final, autocontido.
2. [`docs/21_objetivo_e_enquadramento.md`](docs/21_objetivo_e_enquadramento.md) — como ler os documentos das etapas anteriores, alguns dos quais adotam enquadramento diferente.

## Resultado em resumo

- O agente formulou 4 estratégias e registrou 10 descartadas, definiu um critério de eficiência e escolheu por ele.
- O padrão disponível era repetir o modelo de compra de 2024 com a estimativa do órgão. O agente o simulou como um cenário, comparou e rejeitou.
- Os dados posteriores apoiam a escolha nos três pontos em que ela difere da decisão real.
- A ordem entre os cenários se sustenta. A magnitude da economia potencial anunciada (R$ 2,22 milhões) está superestimada.
- A demonstração é de comportamento: o experimento não distingue, quanto ao mecanismo, a elaboração de cenários de um reconhecimento de padrões mais elaborado.

## Etapas

| Etapa | Conteúdo | Onde |
|---|---|---|
| 1. Auditoria de dados | Fontes, qualidade, integração e suficiência | `docs/01` a `06`, `LOG_AUDITORIA.md` |
| 2. Caso organizacional | Escolha de Santa Luzia e definição do problema | `docs/07` a `11`, `LOG_ETAPA_2.md` |
| 3. Integração | Padronização dos 334 itens e corte temporal em 29/01/2025 | `docs/12` a `17`, `LOG_ETAPA_3.md` |
| Pré-4. Lacunas | Fontes complementares e regra de ICMS | `docs/18`, `LOG_PRE_ETAPA_4.md` |
| 4. Decisão do agente | Enunciado, decisão congelada e transcrição auditada | `etapa4/`, `LOG_ETAPA_4.md` |
| Pré-5. Preparação da avaliação | Verificação das falhas do pacote, protocolo e indicadores | `etapa5/`, `docs/19`, `docs/20`, `LOG_PRE_ETAPA_5.md` |
| 5. Avaliação independente | Recálculo e veredito por outra sessão | `etapa5_avaliacao_independente/`, `LOG_ETAPA_5.md` |
| 6. Consolidação | Confronto das avaliações e relatório final | `etapa6/`, `LOG_ETAPA_6.md` |

## Estrutura

```
data/raw/               arquivos originais, sem modificação
data/processed/         parquet derivados
data/decision_input/    pacote entregue ao agente (só informação até 29/01/2025)
data/decision_input_v2/ o mesmo pacote com errata
data/evaluation_only/   dados posteriores ao corte — NÃO fornecer a agente decisor
docs/                   documentos numerados, na ordem das etapas
etapa4/ a etapa6/       decisão, avaliações e consolidação
reports/                CSVs e saídas de console da Etapa 1
scripts/                scripts numerados na ordem de execução
LOG_*.md                registro cronológico de cada etapa
```

## Regras de preservação

- A decisão do agente (`etapa4/`) e o pacote que ele recebeu estão congelados, com sha256 registrado.
- `data/evaluation_only/`, `etapa5/`, `etapa5_avaliacao_independente/resultados/` e `etapa6/resultados/` contêm dados posteriores ao corte.
- Correções são feitas em arquivos novos, nunca sobre os originais.

## Reproduzir

Requisitos: Python 3.13 e `pip install -r requirements.txt`. Rode da raiz do projeto (`-I` isola o interpretador; `-X utf8` evita erro de codificação no console do Windows).

- **Etapa 6 (confronto, somente leitura):** `python -I -X utf8 etapa6/scripts/e6_01_confronto.py .`
- **Etapa 5 independente:** comandos em `etapa5_avaliacao_independente/LEIA-ME.md`.
- **Preparação da avaliação:** comandos em `etapa5/LEIA-ME.md`.
- **Auditoria da Etapa 4:** `python -I -X utf8 scripts/30_auditoria_etapa4.py . etapa4/registro/transcricao_agente_decisor.jsonl`

### Etapa 1 (aquisição e auditoria de dados)

Exige acesso à internet.

```powershell
python -I -X utf8 scripts\02_download.py url https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/BPS/csv/2025_csv.zip data\raw\bps\2025_csv.zip "BPS/MS"
python -I -X utf8 scripts\02_download.py url https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/BPS/csv/2026_csv.zip data\raw\bps\2026_csv.zip "BPS/MS"
python -I -X utf8 scripts\04_profile_bps.py .
python -I -X utf8 scripts\05_bps_checks.py .
```

Medicamentos Transparentes (as URLs da listagem expiram em 24 h; gere uma nova listagem antes — comando `curl` no `LOG_AUDITORIA.md`, passo 3):

```powershell
python -I -X utf8 scripts\01_transparencia_listing.py data\raw\transparencia\listing_merged.json reports\transparencia_listagem_arquivos.csv
python -I -X utf8 scripts\02_download.py transparencia data\raw\transparencia\listing_merged.json PB csv
python -I -X utf8 scripts\02_download.py transparencia data\raw\transparencia\listing_merged_v2.json all csv
python -I -X utf8 scripts\06_profile_transparencia.py . PB --perfil
python -I -X utf8 scripts\07_analyze_transparencia.py . PB
```

Demais (na ordem): `08_mt_cobertura_nacional.py .` (lê direto dos ZIPs), `09_integracao_bps_mt.py .`, `10_pncp_pca.py . 08778268000160 2026 60`, `11_pca_farmaco.py . 08778268000160 2026`, `12_tcepb_despesas.py . <zip> Salgadinho`, `13_cmed_pmvg.py . <xlsx>`, `14_rastreio_mt_pncp.py . 20`, `16_bnafar_estoque.py . <ibge6> "" 1`, `15_build_reports.py .` (por último). Cada script documenta parâmetros no cabeçalho. Os scripts não sobrescrevem arquivos brutos já existentes.

## Fontes

Medicamentos Transparentes (Transparência Brasil), Banco de Preços em Saúde (MS), PNCP, Compras.gov.br, API de Dados Abertos do MS (BNAFAR/Hórus), TCE-PB (SAGRES), CMED/Anvisa. URLs e estado de acesso em [`docs/01_fontes.md`](docs/01_fontes.md); downloads com data, URL e SHA-256 em `reports/manifest_fontes.csv`.

## Avisos

- Somas do BPS são dominadas por valores impossíveis; use medianas por CATMAT + unidade.
- BPS e Medicamentos Transparentes **não** devem ser somados nem unidos por transação.
- Dados pessoais presentes nas fontes (credores pessoa física no TCE-PB, contatos no BNAFAR) não foram usados nos relatórios.
