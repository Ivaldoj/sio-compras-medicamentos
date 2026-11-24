"""Etapa 5 / 06 — síntese: evidências de viabilidade (ex ante × ex post) e números-chave consolidados.

Lê resultados/*.json e *.csv produzidos pelos scripts 01–05. Não calcula nada novo sobre os dados brutos:
só organiza as evidências por dimensão do protocolo (D. Viabilidade) e junta os números citados no relatório.

Saídas: resultados/viabilidade_evidencias.csv, resultados/resumo.json
"""
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e5_comum import RES

J = lambda f: json.load(open(os.path.join(RES, f), encoding="utf-8"))
X, I, E = J("expost_numeros.json"), J("insulinas_numeros.json"), J("economia_numeros.json")
ver = pd.read_csv(os.path.join(RES, "verificacao_calculos.csv"))
rep = pd.read_csv(os.path.join(RES, "reproducao.csv"))
esc = pd.read_csv(os.path.join(RES, "expost_escopo.csv")).set_index("indicador").valor
m = lambda v: f"R$ {v:,.0f}".replace(",", ".")
V = []
def via(dim, alegacao, ex_ante, ex_post, leitura):
    V.append({"dimensao": dim, "o_que_o_agente_afirmou_ou_recomendou": alegacao, "evidencia_ex_ante": ex_ante, "evidencia_ex_post": ex_post, "leitura": leitura})

via("Jurídica", "pregão eletrônico por item, menor preço (via típica da Lei 14.133)",
    "arts. 28, 33 e 40 da Lei 14.133; Súmula TCU 247 (conhecimento prévio do agente)",
    "a Administração fez exatamente pregão eletrônico por item e menor preço (PE 04/2025); o mesmo formato foi repetido no PE 25/2025 e no PE 09/2026",
    "confirmada: a forma de julgamento recomendada é a que o órgão adotou e repetiu")
via("Jurídica", "registro de preços (ata de 12 meses, sem obrigação de contratar) em vez de contrato de quantidade fixa",
    "arts. 82–86; demanda, estoque e saldo desconhecidos no pacote",
    f"o órgão assinou 7 contratos de quantidade total ({m(X['pe04_contratado'])}) e empenhou {X['pe04_pct_empenhado']:.1f}% em ~20 meses; prorrogou-os por mais 12 meses",
    "o desenho real comprometeu juridicamente 5× o que foi executado; o argumento do agente a favor do SRP é sustentado pela execução")
via("Jurídica", "teto CMED como critério de aceitabilidade; nunca aceitar acima do teto",
    f"{int(ver.loc[ver.id == 'V07a', 'recalculado'].iloc[0])} itens com estimativa do órgão acima do teto (recalculado)",
    f"{X['itens_hom_acima_teto_agente']} itens foram homologados acima do teto aplicável; excesso contratado de {m(X['excesso_hom_sobre_teto'])}, "
    f"dos quais {m(X['excesso_hom_sobre_teto_canetas'])} nas canetas 196/199",
    "o risco de conformidade apontado se materializou na decisão real; a regra do agente o teria barrado (com risco de item fracassado)")
via("Jurídica", "bases legais citadas como conhecimento prévio (art. 86 §3º; Decreto 12.343/2024; LC 123 art. 48, I)",
    "o agente marcou-as como 'a verificar'",
    "o LOG_PRE_ETAPA_5 registra leitura no Planalto do art. 86 §3º, II e do Decreto 12.343/2024 (R$ 62.725,59); o download local falhou e não foi refeito nesta etapa",
    "sem divergência conhecida; a conferência textual não foi repetida pelo avaliador (limitação)")
via("Operacional", "entregas parceladas sob demanda (não há armazém)", "restricoes.csv: 'a administração não possui local adequado para armazenamento'",
    "Contrato 00054/2025: 'fornecimento parcelado', entrega em até 5 dias úteis do pedido, com a mesma justificativa de falta de armazém",
    "confirmada: a operação real foi parcelada sob pedido")
via("Operacional", "muitos fornecedores e 334 itens a gerir (viabilidade média-alta)", "PE 01/2024: 9 credores",
    f"PE 04/2025: 7 contratados; mediana de {X['proponentes_mediana']:.0f} proponentes por item; {X['itens_1_proponente']} itens com um único proponente",
    "viável; a competição é alta na maioria dos itens e nula em uma minoria que concentra o valor")
via("Operacional", "transição: risco de meses sem cobertura até a nova contratação; verificar a vigência do PE 12/2024",
    "em 2024 não houve empenho em janeiro e março (pacote)",
    f"jan–abr/2025: {m(X['gasto_2025_jan_abr'])} empenhados no total, contra média de {m(X['gasto_2025_mai_dez_media_mensal'])}/mês de maio a dezembro; "
    f"o PE 12/2024 seguiu ativo e respondeu por {X['gasto_2025_pct_pe12']:.0f}% do gasto de 2025",
    "confirmada: o vale de início de ano se repetiu e o instrumento de 2024 era de fato a ponte disponível")
via("Orçamentária", "reservar ao menos o limite alto do E1 (R$ 2,51 mi), não a estimativa de R$ 4,95 mi",
    "gasto de 2024: R$ 1,95 mi (pacote)",
    f"gasto total com medicamentos: {m(X['gasto_2025_empenhado'])} em 2025 e {m(X['gasto_2026_empenhado'])} em 2026 (até nov.); 12 meses de mar/2025 a fev/2026: {m(X['gasto_12m_mar2025_fev2026'])}",
    "confirmada: o gasto real de todas as vias ficou abaixo do E1 central e muito abaixo da estimativa do órgão")
via("Orçamentária", "quantidades do ETP sem dado de consumo: tratar a demanda como incerta (75%–125%)",
    "status_necessidade: consumo ausente em 334/334 itens",
    f"execução do PE 04/2025: {X['pe04_pct_empenhado']:.1f}% do contratado; o contrato de maior valor (ALLFAMED, {m(X['contrato54_valor'])}) executou {100 * X['contrato54_pago'] / X['contrato54_valor']:.1f}%",
    "a direção estava certa, mas a faixa de 75%–125% foi estreita demais: a execução ficou muito abaixo de 75%")
via("Mercado", "referência saneada = mediana praticada (24 meses) limitada ao teto; faixa P25–P75",
    "247 itens com preço praticado compatível; sobre-estimação mediana do órgão de 2,04×",
    f"fora as canetas: E1 central {m(X['E1_central_sem_canetas'])} × homologado {m(X['homologado_sem_canetas'])} (+{100 * (X['homologado_sem_canetas'] / X['E1_central_sem_canetas'] - 1):.1f}%); "
    f"razão mediana homologado/referência {X['hom_sobre_ref_mediana_sem_canetas']:.2f}; referência/mediana nacional do horizonte {X['ref_sobre_nac_mediana']:.2f} "
    f"(estimativa do órgão: {X['org_sobre_nac_mediana']:.2f})",
    "confirmada: a referência do agente previu o mercado com erro de ~10–20%; a do órgão errou por ~2,3×")
via("Mercado", "risco de item deserto onde a referência está no teto ou é fraca (canetas 196/199; 194/195; 63 itens sem referência)",
    "registros 'a conferir' de canetas em 2024 acima do teto (pacote)",
    f"{X['itens_hom_acima_faixa']} itens homologados acima do limite alto do agente ({E['deserto_itens_com_ate_3_proponentes']} deles com até 3 proponentes); "
    f"entre os {E['itens_4mais_proponentes']} itens com 4 ou mais proponentes, {E['itens_4mais_proponentes_acima_do_alto']}; "
    f"canetas: um só proponente, e o mesmo comprador pagou R$ 29,00 em 2026 (acima do teto de 0%)",
    "risco real e corretamente localizado; a regra 'preço ≤ referência' produziria itens fracassados na faixa de 6% a 18% dos itens")
via("Mercado", "o modelo de desconto sobre a CMED (E2) custa ~2,2× o E1",
    "tetos CMED e descontos de 2024 (pacote); preço por item do E2 não observável",
    f"não há preço por item do PE 12/2024. Nos {E['e2_teste_itens']} itens cobertos, o homologado real por item ({m(E['e2_teste_hom'])}) ficou abaixo do E2 central modelado "
    f"({m(E['e2_teste_E2_central'])}) e do E2 baixo ({m(E['e2_teste_E2_baixo'])}); o órgão continuou a gastar {m(E['gasto_pe12_2024_2025_2026'])} pelo PE 12/2024 em 2025–2026",
    "direção sustentada (o pregão por item real bateu o E2 modelado), mas a magnitude continua sendo modelo, não observação")
pd.DataFrame(V).to_csv(os.path.join(RES, "viabilidade_evidencias.csv"), index=False, encoding="utf-8")

resumo = {"reproducao": {"v1_csv_identicos_em_bytes": int(((rep.pacote == "v1") & (rep.tipo == "csv") & (rep.identico_bytes == True)).sum()),
                         "v1_csv_total": int(((rep.pacote == "v1") & (rep.tipo == "csv")).sum()),
                         "v1_scripts_executados": int(((rep.pacote == "v1") & (rep.tipo == "execucao") & rep.ok).sum()),
                         "v2_scripts_executados": int(((rep.pacote == "v2") & (rep.tipo == "execucao") & rep.ok).sum())},
          "verificacao_calculos": {"total": int(len(ver)), "conferem": int(ver.confere.sum()), "nao_conferem": ver.loc[~ver.confere, "id"].tolist()},
          "expost": X, "insulinas": I, "economia": E, "escopo": {k: (float(v) if str(v).replace(".", "", 1).isdigit() else v) for k, v in esc.items()}}
json.dump(resumo, open(os.path.join(RES, "resumo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(pd.DataFrame(V)[["dimensao", "o_que_o_agente_afirmou_ou_recomendou", "leitura"]].to_string(index=False, max_colwidth=120))
print(json.dumps(resumo["reproducao"]), json.dumps(resumo["verificacao_calculos"]))
