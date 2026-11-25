"""Gera saida/registro_hipoteses.csv e saida/registro_decisoes.csv (conteúdo textual, sem cálculo)."""
import csv

H = [
 ("H01", "Dispensação atendida (SIA) é proxy da necessidade de compra, com faixa", "demanda não atendida e estoques não observados (LEIA-ME §4)", "01_demanda.py; plano (quantidades)", "subestimação da necessidade -> risco de falta; custos maiores (faixa alta cobre +10%)"),
 ("H02", "Mês de processamento SIA ≈ mês de dispensação; reprocessamentos ignorados", "só há mês de processamento", "01_demanda.py (R5)", "nível recente distorcido em ±5%"),
 ("H03", "Crescimento anual g limitado a [-10%, +30%]", "itens recém-incorporados têm crescimento explosivo e não sustentável (ex.: risdiplam ×21)", "01_demanda.py", "itens em rampa (AP013, AP014, AP024, AP050) podem ser subestimados"),
 ("H04", "Quantidade central = 12 × média jun-out/2024 × (1+g/2)", "degrau de patamar em jun/2024 e desaceleração da tendência", "01_demanda.py", "erro de ±10-15% na quantidade e no custo"),
 ("H05", "Faixa alta = 12×R5×(1+g)×1,10 (demanda reprimida e recomposição de estoque)", "necessidade não atendida desconhecida", "01_demanda.py", "se a demanda reprimida passar de 10%, a quantidade alta fica insuficiente"),
 ("H06", "Estoque inicial neutro (compra = consumo projetado)", "estoques não informados", "01_demanda.py; plano", "estoque alto -> compra menor; estoque baixo -> risco de ruptura no início"),
 ("H07", "Rateio por UF pela participação observada na dispensação", "sem dado de necessidade por UF", "01_demanda.py; volumes E1/E3", "efeito pequeno no volume regional, quase nulo no custo"),
 ("H08", "Registros 'compativel' do Compras.gov estão vinculados corretamente à apresentação", "vínculo por regra, sem validação humana", "02_precos.py; todas as referências", "preço de referência errado (ver AP012 e divergências BPS)"),
 ("H09", "Compra DLOG com quantidade ≥10% da dispensação anual é programática; as menores são judiciais ou pontuais", "compras do MS com poucas unidades a preço de PMVG", "02_precos.py (dlog_prog_*)", "preço centralizado errado no item"),
 ("H10", "Teto aplicável = maior teto entre os produtos; ICMS de 18% como aproximação para itens fora do Convênio 87/02", "alíquota da UF de destino não consolidada", "02_precos.py; 03 (limite de preço); plano", "teto real ±3-5 p.p.; nenhum preço projetado chega ao teto"),
 ("H11", "Renovação dos itens centralizados entre -5% e +10% do último preço DLOG (com preço extremo: até o preço do modelo)", "sem atas vigentes informadas", "03_estrategias.py", "custo dos centralizados ±; não muda a ordenação"),
 ("H12", "Reajuste de preços em 2025 de 0-5%, igual em todas as estratégias", "ajuste CMED de 2025 desconhecido em 29/01/2025", "03_estrategias.py", "afeta o nível, não a ordenação"),
 ("H13", "E2: 40-70% do volume do horizonte já sob a ata nacional (IRP+pregão em 4-8 meses; contratos estaduais como ponte)", "prazos usuais de SRP; atas vigentes desconhecidas", "03, 04, 05", "transição mais lenta reduz a economia no horizonte (s=0,4 -> R$148 mi)"),
 ("H14", "E3: 20-60% do volume sob blocos regionais no horizonte", "só parte das regiões tem consórcio interestadual", "03", "E3 mais rápido -> aproxima de E2, mas sem superar em regime pleno"),
 ("H15", "E4: 0-30% do volume federalizado no horizonte", "depende de alterar a PRC e da LOA", "03", "não altera a inviabilidade"),
 ("H16", "O efeito volume-preço estimado (β≈-0,08) vale para compras consolidadas, sem extrapolar além do maior volume observado", "associação de corte transversal com efeitos fixos; não é experimento", "02, 03, 04, 05", "se β=0, a economia de E2 é zero e a recomendação passa a depender só de risco e gestão"),
 ("H17", "O preço que cada SES pagaria em E1 = mediana estadual em 24 meses (p25-p75)", "o status quo é a compra estadual", "03, 05", "referência mais baixa -> economia menor"),
 ("H18", "Item 1A sem compra DLOG programática: preço = mediana × efeito volume nacional", "9 itens sem registro DLOG utilizável", "03; plano", "custo dos centralizados ± (igual em todas as estratégias)"),
 ("H19", "AP007 (imunoglobulina) continua comprado pelo MS, apesar de constar como 1B", "compras DLOG de ~751 mil frascos em 2024 e SIA 1B quase nulo", "03; plano", "se for de fato 1B estadual, entra nos descentralizados e a economia de E2 aumenta"),
 ("H20", "Se o certame nacional fracassar, as SES compram emergencialmente ao p75 estadual", "regra de contingência para o ponto de equilíbrio", "03 (pf_equilibrio)", "um prêmio emergencial maior reduz o ponto de equilíbrio"),
 ("H21", "Erros de quantidade perfeitamente correlacionados entre itens (comonotônicos)", "conservador para a faixa de custo total", "03", "a faixa real do custo total seria mais estreita"),
 ("H22", "Grupos de financiamento do pacote corretos (exceto AP007)", "atribuição textual não validada", "todo o estudo", "muda o conjunto de itens descentralizados e as esferas responsáveis"),
 ("H23", "Fornecedores têm capacidade para o volume nacional", "capacidade não informada", "E2; plano", "risco de ruptura -> exigir lotes ou cotas e cadastro de reserva"),
 ("H24", "O MS pode gerenciar SRP com as SES como participantes para itens que não adquire, com pactuação CIT", "Lei 14.133, art. 86; Dec. 11.462/2023 (participantes); sem vedação no pacote", "E2", "se houver vedação ou insegurança jurídica, migrar para E3 (estado gerenciador regional)"),
]
D = [
 ("D01", "Base de preços principal", "Compras.gov; BPS; ambas somadas", "Compras.gov principal; BPS só para conferência", "BPS pode repetir compras; o Compras.gov tem esfera, UASG e fornecedor", "LEIA-ME §2; precos_bps.observacao", "OBSERVADO", "divergência BPS/CG em 6 itens", "alta", "BPS mais completo e com vínculo validado"),
 ("D02", "Filtro de preços", "todos; só compatíveis; compatíveis sem extremo", "compatível, sem flag extremo; 36m para o modelo e 24m para as referências", "evita unidades diferentes e erros grosseiros; recência", "precos_comprasgov.compatibilidade, flag_preco_extremo", "OBSERVADO", "perda de registros a_conferir (~6%)", "média-alta", "validação manual dos vínculos"),
 ("D03", "Método de projeção da quantidade", "12m observado; tendência linear; média recente + meia tendência", "média jun-out/2024 × (1+g/2), faixa sem crescimento até tendência cheia +10%", "degrau em jun/2024; crescimento heterogêneo", "demanda_mes; cesta d12/d12a", "CALCULADO/HIPÓTESE", "±10-15%", "média", "estoques e filas de demanda reprimida informados pelas SES"),
 ("D04", "Segmentação de mercado", "nenhuma; nº de laboratórios CMED; nº de fornecedores", "≥3 laboratórios CMED = concorrencial", "proxy observável de concorrência", "cesta.cmed_laboratorios", "CALCULADO", "β semelhante nos dois segmentos", "média", "dados de market share"),
 ("D05", "Linha de base para a economia", "teto CMED; mediana geral; mediana estadual; SIA", "E1 = mediana estadual 24m × mesma quantidade", "contrafactual realista e mesma categoria de valor", "precos_comprasgov esfera E", "CALCULADO", "p25-p75", "média-alta", "atas estaduais vigentes com preço diferente"),
 ("D06", "Critério de eficiência", "menor custo; custo-efetividade; minimax regret", "menor custo esperado para a mesma cobertura, com filtro de viabilidade, risco (ponto de equilíbrio) e robustez", "a cobertura projetada é igual entre as estratégias; o recurso público é consolidado", "enunciado §1", "INFERIDO", "—", "alta", "se as estratégias diferissem em cobertura, usar custo por unidade efetivamente dispensada"),
 ("D07", "Tratamento de AP007 (imunoglobulina)", "1B estadual; centralizado", "centralizado como observado; verificar grupo", "MS compra ~751 mil frascos/ano; SIA 1B R$14 mil", "precos_comprasgov DLOG; cesta.valor_aprovado_sia_12m", "OBSERVADO/INFERIDO", "classificação real desconhecida", "média", "confirmação do Anexo III da RENAME"),
 ("D08", "Compras DLOG marcadas como preço extremo", "excluir; manter", "manter, com faixa superior = preço do modelo", "a flag compara com mediana dominada por compras pequenas", "precos_comprasgov AP041/AP044", "OBSERVADO", "preço de AP044 de R$0,68 a R$14,6", "média", "ata DLOG vigente confirmando o preço"),
 ("D09", "Conjunto de estratégias", "várias", "avaliar E1-E4; descartar X1-X7", "ver 02_estrategias.md", "restricoes.csv; dados", "INFERIDO", "—", "alta", "nova opção legal (ex.: compra centralizada pactuada para o Grupo 2)"),
 ("D10", "Estratégia recomendada", "E1, E2, E3, E4", "E2: SRP nacional compartilhado para 1B/2; 1A mantido na DLOG", "menor custo em toda a faixa, viável, risco mitigável", "03_comparacao.csv; sensibilidade.csv", "CALCULADO", "economia R$159-298 mi", "média-alta", "β≈0; prob. de fracasso >40%; baixa adesão das SES"),
 ("D11", "Método de incerteza", "cenários determinísticos; Monte Carlo", "Monte Carlo com números aleatórios comuns + sensibilidade determinística", "faixas coerentes e comparação pareada", "03, 04", "CALCULADO", "—", "alta", "—"),
 ("D12", "Uso do orçamento federal", "como teto de 2025; como contexto", "só contexto de ordem de grandeza, sem somar categorias", "LOA 2025 não aprovada; empenho ≠ pagamento", "recursos_federais.csv", "OBSERVADO", "LOA 2025", "alta", "LOA aprovada"),
 ("D13", "Corte temporal do conhecimento", "usar conhecimento recente; restringir a 29/01/2025", "não uso o ajuste CMED de 2025, a LOA 2025 nem resultados de licitação posteriores", "regra do enunciado", "enunciado §4", "CONHECIMENTO PRÉVIO", "—", "alta", "—"),
 ("D14", "Quantidade planejada × demanda", "tratar como demanda; tratar como necessidade de compra estimada", "necessidade de compra estimada a partir da dispensação atendida", "regra do enunciado e LEIA-ME", "LEIA-ME §3", "OBSERVADO", "demanda reprimida", "alta", "dados de fila e estoque"),
 ("D15", "Horizonte da economia", "regime pleno; horizonte com transição", "economia principal = horizonte com transição; regime pleno só como referência, nunca somado", "o horizonte de 12 meses inclui o tempo de licitação", "enunciado §1", "HIPÓTESE (H13)", "s 0,4-0,7", "média", "atas nacionais já existentes"),
]
with open("saida/registro_hipoteses.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["id", "hipotese", "motivo", "onde_e_usada", "impacto_se_falsa"]); w.writerows(H)
with open("saida/registro_decisoes.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "decisao", "opcoes_consideradas", "escolha", "justificativa", "evidencias", "classificacao_evidencia", "incerteza", "confianca", "o_que_mudaria_a_decisao"])
    w.writerows(D)
print(len(H), len(D))
