"""Gera saida/plano_por_item.csv, saida/03_comparacao.csv e trabalho/30_itens_criticos.txt a partir de
trabalho/ref_itens.csv (10_referencias.py) e trabalho/custos_estrategias.csv, demanda.csv, e2_e3_por_item.csv (20_estrategias.py)."""
import pandas as pd, numpy as np

r = pd.read_csv("trabalho/ref_itens.csv").merge(pd.read_csv("trabalho/e2_e3_por_item.csv"), on="item")
LIM_EPP = 80000.0  # LC 123/2006, art. 48, I

def tratamento(x):
    t = ["item próprio no pregão eletrônico SRP, menor preço por item; entrega parcelada sob demanda no endereço da SMS"]
    if x["item"] in (196, 199):
        t.append("insulina humana em caneta: especificação '3 mL com sistema de aplicação'; referência = teto CMED; confirmar antes a cota MS/SES e só aceitar proposta ≤ teto do produto ofertado")
    elif x["item"] in (194, 195):
        t.append("insulina análoga em caneta: sem vínculo CMED no pacote e referência fraca; pesquisa direta e verificação do fornecimento pelo CEAF/SES antes de fixar quantidade")
    elif x["item"] in (197, 198):
        t.append("insulina humana em frasco 10 mL: referência praticada compatível; confirmar cota MS/SES")
        if x["item"] == 197:  # ver trabalho/40_numeros_texto.txt
            t.append("vínculo CMED 'HUMULIN 70N/30R' (pré-mistura, não NPH) parece indevido: sem ele o teto máx. é R$ 50,77 e a estimativa do órgão (R$ 55,49) fica acima do teto")
    if x.flag_sem_referencia_externa:
        t.append("pesquisa direta com ≥3 fornecedores (Lei 14.133, art. 23, §1º, IV) antes do edital; referência provisória")
    if x.flag_a_conferir:
        t.append("conferir manualmente os registros 'a conferir' antes de fixar a referência")
    if x.flag_acima_teto_confirmado or x.flag_acima_teto_pacote:
        t.append("estimativa do órgão acima do teto CMED: não usar como referência nem como critério de aceitabilidade")
    if x.flag_teto_suspeito:
        t.append("teto CMED suspeito de erro de conversão: validar fator antes de usar")
    if x.n_vinc_alerta and x.n_vinc_alerta > 0:
        t.append(f"{int(x.n_vinc_alerta)} vínculo(s) CMED COM ALERTA excluído(s) do teto: validar")
    if x.q * x.p_ref <= LIM_EPP:
        t.append("exclusivo ME/EPP (LC 123, art. 48, I), salvo exceção motivada do art. 49")
    if not pd.isna(x.p_ata):
        t.append(f"contingência: ata SRP no PNCP a R$ {x.p_ata:.4f}/un. (avaliar adesão, art. 86, se o item fracassar)")
    return "; ".join(t)

def obs(x):
    o = []
    if x.flag_ref_fraca and x.fonte_ref.startswith("praticado"):
        o.append(f"referência fraca (n={int(x.prat_n)})")
    if x.flag_a_conferir and not pd.isna(x.p_se_conferir_compativel):
        o.append(f"se 'a conferir' for compatível: R$ {x.p_se_conferir_compativel:.4f} (n={int(x.conf_n)})")
    if x.flag_a_conferir and pd.isna(x.p_se_conferir_compativel):
        o.append("'a conferir' sem registros de preço utilizáveis no pacote")
    if not pd.isna(x.p_org) and x.p_ref > 0:
        o.append(f"estimativa do órgão = {x.p_org / x.p_ref:.2f}× a referência adotada")
    if x.inconsistencia_unidade:
        o.append("inconsistência de unidade no TR")
    if not pd.isna(x.e2_pref):
        o.append(f"preço no modelo desconto CMED (E2) = R$ {x.e2_pref:.4f}")
    return "; ".join(o)

plano = pd.DataFrame({
    "item": r.item, "descricao": r.descricao, "unidade": r.unidade, "quantidade_etp": r.q,
    "tratamento_estrategia_recomendada": r.apply(tratamento, axis=1),
    "preco_ref_unitario": r.p_ref.round(4), "fonte_preco_ref": r.fonte_ref, "categoria_valor": r.categoria_valor_ref,
    "teto_cmed_unitario_aplicavel_max": r.teto_max.round(4), "teto_cmed_unitario_aplicavel_min": r.teto_min.round(4),
    "teto_cmed_tipo_aliquota": np.where(r.teto_max.isna(), "sem teto utilizável (" + r.status_teto_cmed + ")", r.teto_tipos + " ICMS " + r.teto_aliq),
    "categoria_valor_teto": np.where(r.teto_max.isna(), "", "limite_regulatorio_por_embalagem convertido por unidade do item (não é preço praticado)"),
    "faixa_preco_baixo": r.p_low.round(4), "faixa_preco_alto": r.p_high.round(4),
    "valor_ref_total": (r.q * r.p_ref).round(2), "valor_faixa_baixo": (r.q * r.p_low).round(2), "valor_faixa_alto": (r.q * r.p_high).round(2),
    "preco_estimado_orgao": r.p_org, "valor_estimado_orgao": r.v_org,
    "flag_a_conferir": r.flag_a_conferir, "flag_acima_teto_pacote": r.flag_acima_teto_pacote, "flag_acima_teto_confirmado": r.flag_acima_teto_confirmado,
    "flag_sem_referencia_externa": r.flag_sem_referencia_externa, "flag_sem_teto_utilizavel": r.flag_sem_teto_utilizavel,
    "flag_referencia_fraca": r.flag_ref_fraca, "flag_teto_suspeito": r.flag_teto_suspeito.fillna(False),
    "observacao": r.apply(obs, axis=1),
})
assert len(plano) == 334 and plano.item.is_unique and plano.preco_ref_unitario.notna().all()
plano.to_csv("saida/plano_por_item.csv", index=False, encoding="utf-8")

# ---------------- 03_comparacao.csv ----------------
c = pd.read_csv("trabalho/custos_estrategias.csv")
d = pd.read_csv("trabalho/demanda.csv").pivot(index="estrategia", columns="demanda_vs_ETP", values="gasto_central")
ids = ["R0", "R1", "E1", "E2", "E3", "E4"]
c.insert(0, "id", ids)
c["gasto_demanda_75pct"] = c.id.map(d[0.75]); c["gasto_demanda_125pct"] = c.id.map(d[1.25])
qual = {
 "E1": dict(cobertura="334 itens (100%); 63 com referência provisória até pesquisa direta", viab_juridica="alta", viab_operacional="média-alta (sem estoque central: entregas parceladas; muitos fornecedores)",
            viab_orcamentaria="alta (ata não obriga a contratar; dotação por pedido)", viab_mercado="média (risco de deserto em itens com referência no teto, p.ex. canetas de insulina)",
            risco_continuidade="médio (prazo até a ata; itens desertos)", posicao="1ª — recomendada"),
 "E2": dict(cobertura="225 itens pelo desconto; 109 dependem de processo complementar", viab_juridica="média-baixa (referência = teto regulatório, não mercado; preço depende do registro entregue)",
            viab_operacional="alta (1 fornecedor, 1 processo)", viab_orcamentaria="alta (SRP)", viab_mercado="alta (precedente 2024)",
            risco_continuidade="médio (concentração em 1 fornecedor)", posicao="4ª — custo ~2,2× E1"),
 "E3": dict(cobertura="111 itens (26% do valor E1) com ata identificada; restante via E1", viab_juridica="média (art. 86: aceite do gerenciador e do fornecedor, limites de 50%; adesão a ata municipal depende da redação vigente do art. 86, §3º)",
            viab_operacional="baixa (dezenas de adesões a atas de outras UFs; entrega remota de pequenos volumes)", viab_orcamentaria="alta", viab_mercado="baixa-média (aceite incerto; amostra PNCP não é censo de atas)",
            risco_continuidade="alto se usada como via principal", posicao="2ª como complemento/contingência de E1; inviável como via principal"),
 "E4": dict(cobertura="334 itens", viab_juridica="média (quantidade fixa sem dado de consumo e sem estoque conhecido)", viab_operacional="baixa (sem local de armazenagem: entrega integral inviável)",
            viab_orcamentaria="baixa (exige dotação para o total na assinatura; saldo desconhecido)", viab_mercado="média", risco_continuidade="médio", posicao="3ª — dominada por E1"),
}
for k in ["cobertura", "viab_juridica", "viab_operacional", "viab_orcamentaria", "viab_mercado", "risco_continuidade", "posicao"]:
    c[k] = c.id.map(lambda i: qual.get(i, {}).get(k, "referência de valor, não é estratégia"))
c["criterio_eficiencia"] = "custo esperado de cobertura integral (334 itens, 12 meses, demanda do ETP) entre estratégias viáveis; desempate por risco de descontinuidade e flexibilidade orçamentária"
c = c.rename(columns={"central": "custo_central", "baixo": "custo_baixo", "alto": "custo_alto"})
for col in ["custo_central", "custo_baixo", "custo_alto", "gasto_demanda_75pct", "gasto_demanda_125pct"]:
    c[col] = c[col].round(2)
c.to_csv("saida/03_comparacao.csv", index=False, encoding="utf-8")

# ---------------- itens críticos ----------------
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 70); pd.set_option("display.float_format", "{:,.4f}".format)
with open("trabalho/30_itens_criticos.txt", "w", encoding="utf-8") as f:
    w = lambda *a: print(*a, file=f)
    a = r[r.flag_acima_teto_pacote | r.flag_acima_teto_confirmado].copy()
    a["v_lim"] = a.q * a.p_org_limitado_teto; a["v_ref"] = a.q * a.p_ref; a["razao_org_teto"] = a.p_org / a.teto_max
    w("== ACIMA DO TETO: n pacote", int(r.flag_acima_teto_pacote.sum()), "n confirmado", int(r.flag_acima_teto_confirmado.sum()), "uniao", len(a))
    w(f"valor órgão={a.v_org.sum():,.2f} | limitado ao teto={a.v_lim.sum():,.2f} | excesso={a.v_org.sum()-a.v_lim.sum():,.2f} | referência E1={a.v_ref.sum():,.2f}")
    w("somente no confirmado (vínculo com alerta excluído):", a.loc[~a.flag_acima_teto_pacote, "item"].tolist())
    w("razão estimativa/teto_max:", a.razao_org_teto.describe(percentiles=[.25, .5, .75]).round(3).to_dict())
    w(a.sort_values("v_org", ascending=False)[["item", "descricao", "q", "p_org", "teto_min", "teto_max", "teto_tipos", "razao_org_teto", "p_ref", "v_org", "v_lim", "v_ref"]].to_string(index=False))
    b = r[r.flag_a_conferir].copy(); b["v_ref"] = b.q * b.p_ref
    b["v_se_compat"] = b.q * b.p_se_conferir_compativel.fillna(b.p_ref)
    w("\n== A CONFERIR:", len(b), f"valor órgão={b.v_org.sum():,.2f} | ref E1={b.v_ref.sum():,.2f} | se compatível={b.v_se_compat.sum():,.2f}")
    w(b.sort_values("v_org", ascending=False)[["item", "descricao", "q", "p_org", "fonte_ref", "p_ref", "conf_n", "conf_med", "p_se_conferir_compativel", "conf_motivos", "teto_max", "v_org", "v_ref", "v_se_compat"]].to_string(index=False))
    s = r[r.flag_sem_referencia_externa]
    w("\n== SEM REFERÊNCIA EXTERNA:", len(s), f"valor órgão={s.v_org.sum():,.2f} | ref provisória={(s.q*s.p_ref).sum():,.2f} | faixa {(s.q*s.p_low).sum():,.2f}–{(s.q*s.p_high).sum():,.2f}")
    w("ref fraca (praticado n<5):", int((r.flag_ref_fraca & r.fonte_ref.str.startswith("praticado")).sum()))
    w("sem teto utilizável:", int(r.flag_sem_teto_utilizavel.sum()), f"valor E1={(r.q*r.p_ref)[r.flag_sem_teto_utilizavel].sum():,.2f}")
    w("itens exclusivos ME/EPP (valor ref ≤ 80 mil):", int((r.q * r.p_ref <= LIM_EPP).sum()), "| acima:", r.loc[r.q * r.p_ref > LIM_EPP, "item"].tolist())
    w("itens com mercado (P25 praticado) acima do teto máximo:", r.loc[r.prat_p25 > r.teto_max, "item"].tolist())
    w("itens com mediana praticada acima do menor teto:", int((r.prat_med > r.teto_min).sum()))
print(open("trabalho/30_itens_criticos.txt", encoding="utf-8").read())
