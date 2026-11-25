"""Gera saida/registro_evidencias.csv (afirmação, evidência, classificação). Conteúdo textual; números vêm dos scripts citados."""
import csv

R = [
 ("A01", "A", "O decisor fez 45 chamadas de ferramenta (32 Bash, 11 Write, 1 Read, 1 Handback), todas na raiz, sem internet nem agentes", "trabalho/a01_transcricao.py -> trabalho/a01_chamadas.csv", "CALCULADO"),
 ("A02", "A", "Os hashes dos arquivos de entrada são iguais antes e depois; os 45 hashes 'depois' conferem com o conteúdo atual", "trabalho/a01_transcricao.py; decisao_congelada/registro/hashes_*.csv", "CALCULADO"),
 ("A03", "A", "Duas saídas longas foram persistidas fora da raiz pelo harness e não foram abertas pelo decisor", "a01_chamadas.csv (23:08:04, 23:10:34); saida/registro_acessos.md do decisor", "OBSERVADO"),
 ("A04", "A", "O import de consulta.py criou __pycache__ em data/ (nenhum dado alterado)", "hashes_ambiente_depois.csv", "OBSERVADO"),
 ("A05", "A", "Não há fatos posteriores ao corte nos entregáveis; o índice CMED de 2025 foi explicitamente não usado", "saida/*.md do decisor; registro_decisoes.csv D13", "INFERIDO"),
 ("B01", "B", "Todas as saídas do decisor se reproduzem byte a byte (explora_*_resumo iguais após ordenar as linhas)", "trabalho/b01_reproduz.py -> trabalho/b01_reproducao.csv", "CALCULADO"),
 ("C01", "C", "Totais E1-E4, economia 221 (159-298) e regime pleno 405 (337-483) conferem", "trabalho/c01_calculos.py -> saida/02_calculos.csv C01-C09", "CALCULADO"),
 ("C02", "C", "O ponto de equilíbrio de fracasso do decisor (0,413) conta a perda da economia duas vezes; o correto é 0,704", "c01 C14; decisao_congelada/ambiente/trabalho/03_estrategias.py (pf_equilibrio)", "CALCULADO"),
 ("C03", "C", "Por sorteio pareado, E3<E4 só em 86,2% dos sorteios; E2<E3 em 99,5%", "c01 C10", "CALCULADO"),
 ("C04", "C", "MS comprou 703.302 frascos de AP007 em 2024 no pacote (o decisor declarou ~751 mil)", "c01 C20; precos_comprasgov.parquet", "CALCULADO"),
 ("C05", "C", "Nenhum preço projetado ou faixa superior passa do teto CMED aplicável", "c01 C25; plano_por_apresentacao.csv", "CALCULADO"),
 ("C06", "C", "Categorias de valor não somadas; BPS não somado ao Compras.gov; idItemCompra único; nenhum CATMAT compartilhado", "c01 C19, C29, C30; inspeção de 02_precos.py e 03_estrategias.py", "OBSERVADO"),
 ("D01", "D", "A imunoglobulina humana 5 g é Grupo 1A na RENAME 2024 (o pacote diz 1B)", "evidencias_primarias/rename/relacao_nacional_medicamentos_2024_2ed.pdf, Anexo III, p. 209 do PDF; trabalho/d01_rename.py", "OBSERVADO"),
 ("D02", "D", "Os 11 itens descentralizados têm grupo 1B/2 coerente com a RENAME 2024", "RENAME 2024 Anexo III pp. 174, 181, 182, 187, 197, 199, 212, 213, 217 do PDF; trabalho/d01_rename_trechos.txt", "OBSERVADO"),
 ("D03", "D", "Eltrombopague 25/50 mg e omalizumabe têm preço estadual quase uniforme (CV 0,04-0,08) e β do próprio item ≈0 antes do corte", "trabalho/d02_beta_por_item.py -> trabalho/d02_beta_por_item.csv", "CALCULADO"),
 ("D04", "D", "Com β por item, a economia determinística de E2 cai de 203 para 114 milhões", "trabalho/d02_beta_por_item.py", "CALCULADO"),
 ("D05", "D", "O preço de mepolizumabe repete R$ 2.028,87 em SES de vários portes, o que sugere preço negociado nacionalmente e não efeito volume", "precos_comprasgov.parquet (AP027); inspeção inline", "INFERIDO"),
 ("D06", "D", "O histórico DLOG de adalimumabe já mostrava saltos de preço por troca de fornecedor/PDP (417 -> 141 -> 127)", "precos_comprasgov.parquet (AP002, DLOG)", "OBSERVADO"),
 ("D07", "D", "O Decreto 11.462/2023, art. 2º, VI, define 'compra nacional' para execução descentralizada de programa federal com demanda dos entes", "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/decreto/d11462.htm", "OBSERVADO"),
 ("D08", "D", "A Lei 14.133, art. 86, prevê IRP com outros órgãos; o §8º veda adesão federal a ata estadual; o §7º trata da adesão emergencial a ata do MS", "https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14133.htm", "OBSERVADO"),
 ("D09", "D", "O enquadramento do Grupo 2 (financiamento estadual) em 'compra nacional' de programa federal é discutível", "Decreto 11.462, art. 2º, VI; PRC 2/2017 art. 49 via restricoes.csv", "INFERIDO"),
 ("D10", "D", "Os itens centralizados respondem por 81% do custo estimado da cesta (5,28 de 6,48 bi)", "decisao_congelada/ambiente/trabalho/mc_resumo.txt", "CALCULADO"),
 ("E01", "E", "Erro relativo mediano da quantidade central = -2,5%; |erro| mediano 5,5%; 43/50 itens melhores que a referência ingênua", "trabalho/e01_demanda.py -> trabalho/e01_demanda.csv", "CALCULADO"),
 ("E02", "E", "32 de 50 itens ficaram na faixa de quantidade; 8 acima (AP014, AP021, AP024, AP027, AP034, AP049, AP050, AP085) e 10 abaixo", "e01_demanda.csv", "CALCULADO"),
 ("E03", "E", "A base SIA reservada confere com as respostas brutas do TabNet", "trabalho/e01_demanda.py; evidencias_primarias/sia_tabnet/*.html", "CALCULADO"),
 ("E04", "E", "Razão mediana preço observado/decisor = 1,02 (26 itens com preço em H); 19 dentro da faixa", "trabalho/e02_precos.py -> trabalho/e02_precos.csv", "CALCULADO"),
 ("E05", "E", "Adalimumabe: DLOG pagou 416,31 (Fundação Butantan, 26/03/2025) contra 126,94 da referência", "dados_reservados/precos_comprasgov_pos.parquet", "OBSERVADO"),
 ("E06", "E", "Omalizumabe: o preço estadual caiu de ~1.841 para ~690-700 a partir de mai-jul/2025; DLOG comprou 12.600 un. a 500 em 11/08/2026", "precos_comprasgov_pos.parquet (AP034)", "OBSERVADO"),
 ("E07", "E", "Referência observada da cesta = R$ 6,76 bi (Q obs × P obs); E2 projetado = 6,24 bi; nos descentralizados 1,144 contra E1 projetado 1,197", "trabalho/e03_custo_orcamento.py -> trabalho/e03_custo_totais.csv", "CALCULADO"),
 ("E08", "E", "Só 61,5% do valor de referência observado tem preço observado no horizonte", "e03_custo_totais.csv", "CALCULADO"),
 ("E09", "E", "Ação 4705 em 2025: empenhado 15,49 bi (+12,7% sobre 2024); realizado 12,85 bi (83%)", "dados_reservados/orcamento_acoes_af_2025.csv; trabalho/e04_orcamento.csv", "CALCULADO"),
 ("E10", "E", "Não houve ata nacional dos 11 itens 1B/2 no horizonte; as compras DLOG desses itens em H são pontuais (12 a 1.092 un.)", "precos_comprasgov_pos.parquet; e02", "INFERIDO"),
 ("F01", "F", "O β pós-corte se mantém: -0,075 (concorrencial) e -0,078 (concentrado) no horizonte, com IC90 que exclui zero", "trabalho/f01_sensibilidade.py -> trabalho/f01_beta_pos.csv", "CALCULADO"),
 ("F02", "F", "A ordem E2>E3>E4>E1 se mantém em todas as substituições por valores observados; a economia de E2 com Q e P observados é ~210 milhões", "trabalho/f01_sensibilidade.csv", "CALCULADO"),
 ("F03", "F", "A ordem é estrutural no modelo do decisor (β<0; V_nac>V_reg; s2≥s3>s4)", "03_estrategias.py (fórmulas)", "INFERIDO"),
 ("F04", "F", "Com a mesma transição (s=0,55), a vantagem de E2 sobre E3 cai de 97 para 58 milhões", "f01_sensibilidade.csv", "CALCULADO"),
 ("G01", "G", "A queda de preço de AP034 no status quo vale ~R$ 163 mi contra a referência do decisor; não é economia de E2", "(1.841,49-699,76)×142.690; e02, e01", "CALCULADO"),
 ("G02", "G", "Economia realizada de E2: não observável (estratégia não executada; pagamento só agregado por ação)", "dados_reservados/LEIA-ME.md; orcamento_acoes_af_2025.csv", "INFERIDO"),
 ("P01", "pacote", "A regra de compatibilidade aceita SUPOSITÓRIO para item oral; AP052 recebe 21 registros pré-corte de uso retal", "codigo_preparacao/n03_pacote_nacional.py (UN_SOLIDA); trabalho/p01_pacote.py", "CALCULADO"),
 ("P02", "pacote", "Sem supositório, a mediana estadual 24m de AP052 cai de 3,815 para 2,470", "trabalho/p01_ap052.csv", "CALCULADO"),
 ("P03", "pacote", "Tetos CMED por unidade conferem com a lista primária em 411/411 apresentações", "trabalho/p01_pacote.py §6; evidencias_primarias/cmed/cmed_pmvg_20250107.xls", "CALCULADO"),
 ("P04", "pacote", "recursos_federais 2024 confere com o zip primário do Portal (baixado em 24/11/2026)", "trabalho/p01_pacote.py §5", "CALCULADO"),
 ("H01", "H", "Custo de transação e coordenação de E2 acima de ~R$ 100 mi tornaria E1 competitivo se o β por item valer", "05_sensibilidade.md §4", "HIPÓTESE"),
]
with open("saida/registro_evidencias.csv", "w", newline="", encoding="utf8") as f:
    w = csv.writer(f)
    w.writerow(["id", "dimensao", "afirmacao", "evidencia", "classificacao"])
    w.writerows(R)
print(len(R), "afirmações")
