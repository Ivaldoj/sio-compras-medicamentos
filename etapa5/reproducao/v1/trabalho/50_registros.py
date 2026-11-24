"""Escreve saida/registro_decisoes.csv e saida/registro_hipoteses.csv (texto das decisões e hipóteses; números vêm das saídas citadas)."""
import csv

DEC = ["id", "decisao", "opcoes_consideradas", "escolha", "justificativa", "evidencias", "classificacao_evidencia", "incerteza", "confianca", "o_que_mudaria"]
decisoes = [
 ("D01", "Critério de eficiência", "menor custo central; custo ajustado a risco monetizado; multicritério ponderado; custo de cobertura integral com filtros de viabilidade",
  "menor custo esperado de cobertura integral (334 itens, 12 meses, qtd. ETP) entre estratégias viáveis jurídica e operacionalmente; desempate por risco de descontinuidade e flexibilidade orçamentária",
  "o produto (cobertura da necessidade) é igual entre estratégias; sem dados para monetizar risco (H04) — riscos explicitados separadamente",
  "ENUNCIADO §1; restricoes.csv; 03_comparacao.md", "INFERIDO", "pesos implícitos do desempate", "alta", "dados de probabilidade de deserto/desabastecimento permitiriam custo ajustado a risco"),
 ("D02", "Preço de referência central por item", "estimativa do órgão; média praticada; P25; mediana praticada; teto CMED",
  "mediana dos preços praticados compatíveis (BPS + Compras.gov.br), limitada ao teto CMED",
  "art. 23 §1º I da Lei 14.133 cita a mediana do banco de preços em saúde; mediana é robusta a extremos; estimativa do órgão = 2,044× a mediana (inflada)",
  "trabalho/10_referencias.py -> ref_itens.csv; 11_inspeciona_ref.txt", "CALCULADO + CONHECIMENTO PRÉVIO", "lances reais podem desviar (faixa P25–P75)", "alta", "evidência de que lances para Santa Luzia ficam sistematicamente acima do P75"),
 ("D03", "Janela temporal dos preços praticados", "todo o histórico 2020+; 12 meses; 24 meses", "24 meses (29/01/2023–29/01/2025); histórico total se n<5",
  "equilíbrio entre atualidade e tamanho de amostra: 244 itens com n≥5 na janela", "trabalho/10_referencias.py (JANELA)", "CALCULADO", "preços não corrigidos monetariamente (H06)", "média", "inflação de preços relevante no período"),
 ("D04", "Itens 194/195 (insulinas análogas): quais registros 'compatíveis' usar", "todos os do grupo compatível do pacote; só o CATMAT específico",
  "só CATMAT 468664 (194) e 440255 (195)", "o grupo do pacote mistura NPH (442012) e outra análoga, o que contaminaria o preço",
  "trabalho/05_insulinas_catmat.txt; item_catmat_oficial", "OBSERVADO + INFERIDO", "194 fica com n=2 (referência fraca)", "média", "pesquisa direta"),
 ("D05", "Teto CMED a usar", "todos os vínculos exata/compatível (como o pacote); só vínculos sem alerta", "teto 'confirmado': exclui vínculos COM ALERTA e o vínculo com ERRO da inspeção (item 151)",
  "LEIA-ME: vínculos COM ALERTA devem ser conferidos antes de uso decisivo", "trabalho/07_checa_teto.txt", "OBSERVADO + CALCULADO", "51 itens mudam de teto; item 210 passa a ficar acima do teto", "média", "validação humana dos vínculos"),
 ("D06", "Tratamento dos preços 'a conferir'", "usar como preço; descartar; usar só em sensibilidade", "nunca como preço central/teto; cenário 'compatível' na sensibilidade",
  "exigência do enunciado §3.4; efeito no E1 de +R$ 5,8 mil e conclusão inalterada", "trabalho/sensibilidades.csv; 30_itens_criticos.txt", "CALCULADO", "risco de deserto nas canetas depende da compatibilidade", "alta", "conferência manual dos registros"),
 ("D07", "Itens sem referência externa (63)", "estimativa do órgão; estimativa deflacionada; excluir; teto×desconto", "estimativa do órgão ÷ 2,044 (faixa ÷2,568 a ÷1) + pesquisa direta obrigatória antes do edital",
  "sobre-estimação mediana observada em 246 itens e confirmada pelo próprio PE 01/2024 (2,14×, 2,14×, 1,92×)", "trabalho/10_referencias.txt; 40_numeros_texto.txt", "HIPÓTESE (H07) sobre CALCULADO", "R$ 0,17–0,44 mi nesses itens", "média", "resultado da pesquisa direta"),
 ("D08", "Referência acima do teto", "manter estimativa; limitar ao teto", "limitar ao teto máximo confirmado (itens 196 e 199 ficam no teto)",
  "venda ao governo acima do teto é vedada (Lei 10.742/2003, normas CMED; restrição do pacote)", "ref_itens.csv (ref_limitada_teto)", "OBSERVADO + CONHECIMENTO PRÉVIO", "risco de deserto", "alta", "teto a 20% se Conv. 87/02 não se aplicar (não publicado no pacote)"),
 ("D09", "Conjunto de estratégias", "E1–E4 avaliadas; X1–X10 descartadas", "4 estratégias comparadas quantitativamente e 10 descartadas com motivo",
  "cobrir modalidades e formas substancialmente diferentes (item × desconto; licitar × aderir; SRP × contrato fixo)", "02_alternativas.md", "INFERIDO + CONHECIMENTO PRÉVIO", "base legal a conferir em 2 pontos", "alta", "nova alternativa (ex.: consórcio com ata vigente)"),
 ("D10", "Estratégia recomendada", "E1; E2; E3; E4; híbridos", "E1 (SRP por item, referência saneada) com E3 como contingência",
  "menor custo esperado entre viáveis (R$ 1,81 mi vs 4,04 mi do E2); E3 inexequível como principal; E4 dominada", "trabalho/20_estrategias.txt; 03_comparacao.md", "CALCULADO + INFERIDO", "faixa E1 R$ 1,50–2,51 mi", "alta", "descontos CMED ≥ ~86/82/70%; atas confirmadas para itens de alto valor"),
 ("D11", "Referência para economia potencial", "R0; R1; E2", "E2 principal; R1 secundária; R0 rejeitada",
  "E2 é o contrafactual provável (62,6% do gasto 2024); R1 é o máximo legal orçado; R0 contém R$ 1,40 mi acima do teto", "06_economia.md; 40_numeros_texto.txt", "CALCULADO + INFERIDO", "E2 é modelado (H09)", "média", "dados reais de faturamento do PE 12/2024 por item"),
 ("D12", "Insulinas em caneta (196, 199)", "estimativa do órgão; PNCP estimado; teto; trocar por frasco", "referência = teto CMED; confirmar cota MS/SES; não aceitar acima do teto; troca por frasco só como decisão clínica",
  "estimativa 9,6×/9,3× o teto; sem praticado compatível; PNCP acima do teto", "05_itens_criticos.md; 03_insulinas_detalhe.txt", "OBSERVADO + CALCULADO + CONHECIMENTO PRÉVIO", "deserto provável (praticados 'a conferir' 2024 acima do teto)", "média", "cota MS/SES; teto a 20%"),
 ("D13", "Item 197: vínculo HUMULIN 70N/30R", "aceitar vínculo; sinalizar", "sinalizar como provável vínculo indevido (pré-mistura ≠ NPH); referência não muda",
  "sem ele, teto máx. 50,77 < estimativa 55,49", "40_numeros_texto.txt", "OBSERVADO + INFERIDO", "classificação do pacote sem validação humana", "alta", "validação humana"),
 ("D14", "Registros suspeitos de preço", "manter; excluir flags", "excluir flag_preco_extremo, flag_duplicata_negocio, flag_possivel_duplicata_bps",
  "LEIA-ME: registros suspeitos marcados e não removidos", "10_referencias.py", "OBSERVADO", "pequena", "alta", "—"),
 ("D15", "Cenário central do E2", "registro mais barato; mediana de todos; categoria mais barata (gestão ativa); registro mais caro", "gestão ativa como central; mais barato = baixo; mediana de todos = alto; mais caro = extremo",
  "SMS competente pede genérico quando existe; fornecedor escolhe o registro dentro da categoria", "10_referencias.py (e2_pref); 21_e2_diagnostico.txt", "HIPÓTESE (H09)", "E2 de R$ 2,30 a 4,54 mi (extremo 10,29)", "média", "regras do edital/contrato do PE 12/2024 e faturas reais"),
 ("D16", "Demanda", "usar só ETP; cenários", "cenários 75%/100%/125% do ETP", "consumo e estoque desconhecidos; ±25% = margem do art. 125 e p10 da razão de quantidades 2025/2024 (0,75)",
  "06_explora_complementos.txt; demanda.csv", "HIPÓTESE (H12)", "alta", "média", "dados de consumo (Hórus/BNAFAR)"),
 ("D17", "Transição até a nova ata", "nenhuma; dispensa emergencial; instrumento vigente do PE 12/2024", "verificar vigência/saldo do PE 12/2024; dispensa só dentro do limite; emergencial só se comprovado",
  "2024 teve meses sem empenho até o pregão (OBS)", "execucao_2024_mensal", "OBSERVADO + INFERIDO", "vigência desconhecida", "média", "vigência confirmada"),
 ("D18", "ME/EPP", "ignorar; exclusividade ≤ R$ 80 mil", "aplicar LC 123 art. 48 I (332 itens), com exceções motivadas do art. 49", "obrigação legal", "30_itens_criticos.txt", "CONHECIMENTO PRÉVIO + CALCULADO", "pode reduzir competição", "média", "falta de ≥3 ME/EPP competitivas na região"),
 ("D19", "Item 120 (sem praticado)", "estimativa do órgão; PNCP; preço próprio", "preço homologado no próprio PE 01/2024 (R$ 4,19)", "contratação similar da própria Administração (art. 23 §1º II)", "historico_proprio; 10_referencias.py", "OBSERVADO", "preço de 2024", "média", "pesquisa direta"),
 ("D20", "Item 268 (teto suspeito)", "usar teto; excluir do E2", "excluir do modelo de desconto; teto não afeta a referência E1", "menor teto = 31× a mediana praticada (provável erro de fator)", "10_referencias.py (flag_teto_suspeito)", "CALCULADO + INFERIDO", "pequena (R$ 684 na estimativa do órgão; R$ 522 na referência E1)", "alta", "validação do fator"),
]

HIP = ["id", "hipotese", "motivo", "onde_e_usada", "impacto_se_falsa"]
hipoteses = [
 ("H01", "A quantidade do ETP é a estimativa oficial de 12 meses (H1 do pacote)", "fixada pelo experimento; sem dado de consumo", "todas as estimativas de custo", "custos escalam; mitigado por SRP (sem compromisso)"),
 ("H02", "R$ 4.952.438 é a referência de recurso reservada; R$ 1,95 mi foi o gasto efetivo de 2024 (H2 do pacote)", "fixada pelo experimento", "06_economia (R0), 04 (reserva)", "se o saldo for menor que E1 alto (R$ 2,51 mi), priorizar itens"),
 ("H03", "Preços futuros desconhecidos; só referências do pacote (H3 do pacote)", "fixada pelo experimento", "todas", "—"),
 ("H04", "Ausência de informação sobre desabastecimento não significa disponibilidade (H4 do pacote)", "fixada pelo experimento", "riscos de mercado; não monetização do risco", "—"),
 ("H05", "O preço contratado em pregão SRP por item fica em torno da mediana dos preços praticados compatíveis (24 meses), com faixa P25–P75", "preços praticados são resultados de certames semelhantes; art. 23 §1º I", "E1, E3, E4, economia", "se lances ficarem acima do P75, E1 alto (R$ 2,51 mi) — ainda < E2 central"),
 ("H06", "Sem correção monetária dos preços históricos", "evitar índice externo; efeito estimado pequeno", "E1", "+5% ≈ +R$ 90,6 mil no E1 central"),
 ("H07", "Itens sem referência externa têm a mesma sobre-estimação mediana (2,044×) observada nos itens com referência", "razão mediana em 246 itens; confirmada no PE 01/2024 (1,92–2,14×)", "63 itens (referência provisória R$ 217 mil)", "faixa R$ 173–444 mil; até +R$ 227 mil no E1"),
 ("H08", "Referências pontuais (PNCP, preço próprio) têm a dispersão empírica dos itens com praticado (×0,846 a ×1,25), com limite alto até a estimativa deflacionada", "medianas de P25/mediana e P75/mediana em 246 itens", "24 itens", "faixas mais largas"),
 ("H09", "E2: descontos do PE 12/2024 (genérico 60,11%, similar 51,01%, demais 18,01%) sobre o PF na alíquota aplicável, limitado ao teto (PMVG se CAP); central = SMS pede a categoria mais barata", "base exata do PE 12/2024 não informada", "E2, economia principal", "base PMVG ou descontos maiores reduziriam E2; empate exige ~86/82/70%"),
 ("H10", "E3: atas SRP do PNCP com resultado ≥ 29/01/2024 estão vigentes e aceitariam adesão até 50% da qtd. registrada", "aceite não observável; amostra PNCP", "E3", "E3 converge para E1"),
 ("H11", "E4: preço unitário igual ao do E1", "favorece E4 (lotes reduzem competição); E4 ainda é dominada", "E4", "E4 ficaria mais cara"),
 ("H12", "Demanda real entre 75% e 125% da quantidade do ETP", "±25% = margem do art. 125; p10 da razão de quantidades 2025/2024 = 0,75", "demanda.csv", "fora da faixa, gastos escalam; ranking inalterado"),
 ("H13", "Teto 'confirmado' exclui vínculos COM ALERTA e o vínculo com ERRO (item 151)", "LEIA-ME exige conferência antes de uso decisivo", "teto, flags acima do teto, E2", "se os vínculos forem corretos, tetos maiores em 51 itens; item 210 sai da lista acima do teto"),
 ("H14", "Itens 194/195 só com o CATMAT específico", "evitar contaminação por outros tipos de insulina", "referência 194/195", "referências diferentes (valor pequeno: R$ 16,8 mil)"),
 ("H15", "Alíquota de ICMS aplicável conforme o pacote (0% para isentos/Conv. 87/02; 20% demais)", "regra do pacote; condições do Convênio não verificadas", "tetos", "teto a 20% (não publicado para produtos do Convênio) — tetos maiores, menos deserto"),
 ("H16", "A mediana nacional representa o preço para Santa Luzia/PB", "mediana municipal/geral = 0,97 (P25 0,93; P75 1,00)", "E1", "frete/pequenos volumes podem elevar preços (coberto pela faixa alta)"),
 ("H17", "Item 268: teto suspeito de erro de conversão excluído do E2", "teto = 31× mediana praticada", "E2", "irrelevante para a conclusão"),
 ("H18", "Na falta de confirmação da cota MS/SES, a quantidade de insulinas do ETP é integralmente comprada pelo município", "não há dado da cota no pacote", "insulinas", "se o MS/SES fornecer, −R$ 156 mil na referência E1"),
]

with open("saida/registro_decisoes.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(DEC); w.writerows(decisoes)
with open("saida/registro_hipoteses.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(HIP); w.writerows(hipoteses)
assert all(len(d) == len(DEC) for d in decisoes) and all(len(h) == len(HIP) for h in hipoteses)
print(len(decisoes), "decisões;", len(hipoteses), "hipóteses")
