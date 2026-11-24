"""Referências de preço por item (334) para a decisão de 29/01/2025.

Saída: trabalho/ref_itens.csv (uma linha por item) e trabalho/10_referencias.txt (resumo).
Regras (ver saida/registro_decisoes.csv):
- Preço praticado: v_bps_comparavel (sem flag_preco_extremo/flag_duplicata_negocio) + v_comprasgov_comparavel
  (sem flag_possivel_duplicata_bps); janela 29/01/2023..29/01/2025; se n<5, todo o histórico (2020+).
  Itens 194/195: só o CATMAT específico (468664 = análoga prolongada; 440255 = análoga rápida), pois o pacote
  mistura no grupo "compatível" CATMATs de outros tipos de insulina (D04).
- Teto CMED: v_cmed_teto_unitario na alíquota aplicável à PB e no tipo de preço aplicável (PF; PMVG se CAP),
  só vínculos exata/compatível_conversao; "teto confirmado" exclui vínculos COM ALERTA e o vínculo com ERRO da inspeção.
- "A conferir" (v_bps_a_conferir, v_comprasgov_a_conferir) nunca é preço central; só cenário de sensibilidade.
- Bloqueados (incompativel/indeterminada/provavel_conferencia; grupos BPS não compatíveis) nunca entram (as visões já excluem).
- Desconto PE 12/2024 sobre CMED: Genérico 60,11%; Similar 51,01%; demais (éticos) 18,01% (historico_proprio).
"""
import sys; sys.path.insert(0, "scripts"); import consulta_agente as q
import pandas as pd, numpy as np

con = q.conectar()
df = lambda sql: con.execute(sql).df()
JANELA = "2023-01-29"
CATMAT_ESPECIFICO = {194: "468664", 195: "440255"}
DESC = {"Genérico": 0.6011, "Similar": 0.5101}  # demais tipos: 0.1801 (éticos)
D_ETICO = 0.1801

itens = df("SELECT * FROM itens ORDER BY item")

# ---------- preços praticados compatíveis ----------
prat = df(f"""
SELECT item, 'BPS' fonte, catmat, uf, esfera, data_compra, preco_unitario_praticado p FROM v_bps_comparavel
 WHERE NOT coalesce(flag_preco_extremo,false) AND NOT coalesce(flag_duplicata_negocio,false) AND preco_unitario_praticado > 0
UNION ALL
SELECT item, 'Compras.gov.br', catmat, uf, esfera, data_compra, preco_unitario_praticado FROM v_comprasgov_comparavel
 WHERE NOT coalesce(flag_possivel_duplicata_bps,false) AND preco_unitario_praticado > 0""")
for it, cm in CATMAT_ESPECIFICO.items():
    prat = prat[(prat.item != it) | (prat.catmat == cm)]
prat["recente"] = prat.data_compra >= pd.Timestamp(JANELA)

def resumo(g, pref):
    rec = g[g.recente]
    use, jan = (rec, "24m") if len(rec) >= 5 else (g, "total")
    p = use.p
    return pd.Series({f"{pref}_n": len(use), f"{pref}_n_total": len(g), f"{pref}_janela": jan, f"{pref}_ufs": use.uf.nunique(),
                      f"{pref}_p25": p.quantile(.25), f"{pref}_med": p.median(), f"{pref}_p75": p.quantile(.75),
                      f"{pref}_fontes": "|".join(sorted(use.fonte.unique())),
                      f"{pref}_med_municipal": use.loc[use.esfera.isin(["M", "MUNICIPAL"]), "p"].median()})

rp = prat.groupby("item").apply(lambda g: resumo(g, "prat"), include_groups=False).reset_index()

# ---------- preços "a conferir" (só sensibilidade) ----------
conf = df("""
SELECT item, 'BPS' fonte, uf, esfera, data_compra, preco_unitario_praticado p, compatibilidade FROM v_bps_a_conferir
 WHERE NOT coalesce(flag_preco_extremo,false) AND NOT coalesce(flag_duplicata_negocio,false) AND preco_unitario_praticado > 0
UNION ALL
SELECT item, 'Compras.gov.br', uf, esfera, data_compra, preco_unitario_praticado, compatibilidade FROM v_comprasgov_a_conferir
 WHERE NOT coalesce(flag_possivel_duplicata_bps,false) AND preco_unitario_praticado > 0""")
conf["recente"] = conf.data_compra >= pd.Timestamp(JANELA)
rc = conf.groupby("item").apply(lambda g: resumo(g, "conf"), include_groups=False).reset_index()
rc = rc[["item", "conf_n", "conf_janela", "conf_p25", "conf_med", "conf_p75"]]
rc_tipo = conf.groupby("item").compatibilidade.agg(lambda s: "|".join(sorted(set(s)))).rename("conf_motivos").reset_index()

# ---------- PNCP (contratações comparáveis do pacote) ----------
pn = df("""SELECT item,
  count(preco_unitario_homologado) pncp_n_hom, median(preco_unitario_homologado) pncp_med_hom,
  count(*) FILTER (WHERE preco_unitario_estimado > 0) pncp_n_est, median(preco_unitario_estimado) FILTER (WHERE preco_unitario_estimado > 0) pncp_med_est
  FROM v_pncp_comparavel GROUP BY item""")

# ---------- teto CMED (PB) + preço do modelo "desconto sobre CMED" ----------
teto = df("""
WITH t AS (
 SELECT t.item, t.registro, t.tipo_preco, t.aliquota_icms, t.valor_por_unidade_item teto_u, t.fator_conversao, a.tipo_produto, a.cap,
        r.status, coalesce(r.inspecao_amostral_ia,'') insp
 FROM v_cmed_teto_unitario t
 JOIN regras_conversao r ON r.item = t.item AND CAST(r.registro AS VARCHAR) = t.registro
 JOIN cmed_apresentacoes a ON a.registro = t.registro
 WHERE t.aliquota_aplicavel_pb AND t.aplicabilidade IN ('teto para compras administrativas','teto obrigatório (produto com CAP)')),
pf AS (SELECT item, registro, valor_por_unidade_item pf_u FROM v_cmed_teto_unitario WHERE aliquota_aplicavel_pb AND tipo_preco = 'PF'),
a20 AS (SELECT item, registro, tipo_preco, valor_por_unidade_item teto20_u FROM v_cmed_teto_unitario WHERE aliquota_icms = '20%')
SELECT t.*, pf.pf_u, a20.teto20_u,
       (t.status NOT LIKE '%COM ALERTA%' AND t.insp NOT LIKE 'ERRO%') ok
FROM t JOIN pf USING (item, registro) LEFT JOIN a20 USING (item, registro, tipo_preco)""")
teto["desc"] = teto.tipo_produto.map(DESC).fillna(D_ETICO)
teto["e2_u"] = np.minimum(teto.pf_u * (1 - teto.desc), teto.teto_u)  # desconto sobre PF, limitado ao teto (PMVG se CAP)
ok = teto[teto.ok]
rt = ok.groupby("item").agg(teto_min=("teto_u", "min"), teto_max=("teto_u", "max"), teto_n=("registro", "nunique"),
                            teto_tipos=("tipo_preco", lambda s: "|".join(sorted(set(s)))),
                            teto_aliq=("aliquota_icms", lambda s: "|".join(sorted(set(s)))),
                            teto_max_aliq20=("teto20_u", "max"), cap_algum=("cap", "max"),
                            e2_min=("e2_u", "min"), e2_med=("e2_u", "median"), e2_max=("e2_u", "max"),
                            tipos_produto=("tipo_produto", lambda s: "|".join(sorted(set(s))))).reset_index()
# gestão ativa do modelo de desconto: a SMS pede a categoria mais barata disponível (Genérico > Similar > demais)
ok = ok.assign(pref=ok.tipo_produto.map({"Genérico": 0, "Similar": 1}).fillna(2))
pref = ok[ok.pref == ok.groupby("item").pref.transform("min")]
rt = rt.merge(pref.groupby("item").e2_u.median().rename("e2_pref").reset_index(), on="item", how="left")
rt_all = teto.groupby("item").agg(teto_max_todos=("teto_u", "max"), n_vinc_alerta=("ok", lambda s: int((~s).sum()))).reset_index()

r = (itens[["item", "descricao", "unidade", "quantidade_estimada", "preco_unitario_estimado_orgao", "valor_total_estimado_orgao",
            "status_identificacao", "status_preco_praticado", "status_teto_cmed", "cmed_melhor_classe", "teto_cmed_unitario_pb_min",
            "teto_cmed_unitario_pb_max", "alerta_estimativa_acima_teto_cmed", "inconsistencia_unidade", "qtd_licitada_pregoes_proprios_2024"]]
     .merge(rp, on="item", how="left").merge(rc, on="item", how="left").merge(rc_tipo, on="item", how="left")
     .merge(pn, on="item", how="left").merge(rt, on="item", how="left").merge(rt_all, on="item", how="left"))
r = r.rename(columns={"quantidade_estimada": "q", "preco_unitario_estimado_orgao": "p_org", "valor_total_estimado_orgao": "v_org"})

# dispersão empírica (para referências pontuais): mediana entre itens com >=5 preços de p25/med e p75/med
base = r[(r.prat_n >= 5) & (r.prat_med > 0)]
K_LOW = float((base.prat_p25 / base.prat_med).median())
K_HIGH = float((base.prat_p75 / base.prat_med).median())
# sobre-estimação típica da estimativa do órgão: razão p_org / mediana praticada nos itens com >=5 preços
R_MED = float((base.p_org / base.prat_med).median())
R_P75 = float((base.p_org / base.prat_med).quantile(.75))
# teto suspeito de erro de conversão: menor teto > 20x a mediana praticada (não usado no modelo de desconto CMED)
r["flag_teto_suspeito"] = (r.teto_min / r.prat_med) > 20
# preço homologado no próprio PE 01/2024 (contratação similar da própria Administração)
prop = df("""SELECT i.item, h.preco_unitario_homologado p_proprio FROM itens i JOIN historico_proprio h
  ON list_contains(string_split(i.pregoes_proprios_2024_itens,'|'), h.pregao || '#' || h.numero_item) WHERE h.preco_unitario_homologado IS NOT NULL""")
r = r.merge(prop, on="item", how="left")

cap = lambda v, t: v if pd.isna(t) else min(v, t)

def referencia(x):
    """Preço de referência E1 (central, baixo, alto), fonte e categoria_valor."""
    t = x.teto_max
    tem = lambda v: (not pd.isna(v)) and v >= 1
    teto_ou = lambda v: v if pd.isna(t) else min(v, t)
    if tem(x.prat_n):
        c, lo, hi = x.prat_med, x.prat_p25, x.prat_p75
        if x.prat_n < 5:  # referência fraca: amplia com a dispersão empírica
            lo, hi = min(lo, c * K_LOW), max(hi, c * K_HIGH)
        fonte = f"praticado compatível ({x.prat_fontes}; janela {x.prat_janela}; n={int(x.prat_n)})"
        cat = "preco_unitario_praticado_por_unidade_fornecimento (mediana)"
    elif not pd.isna(x.p_proprio):
        c = x.p_proprio; lo, hi = c * K_LOW, max(c * K_HIGH, teto_ou(x.p_org / R_MED))
        fonte = "homologado no próprio PE 01/2024 (resultado 02/09/2024)"; cat = "preco_unitario_homologado (próprio órgão)"
    elif tem(x.pncp_n_hom):
        c = x.pncp_med_hom; lo, hi = c * K_LOW, max(c * K_HIGH, teto_ou(x.p_org / R_MED))
        fonte = f"PNCP homologado por outro órgão (n={int(x.pncp_n_hom)})"; cat = "preco_unitario_homologado (por unidade do item)"
    elif tem(x.pncp_n_est):
        c = x.pncp_med_est; lo, hi = c * K_LOW, max(c * K_HIGH, teto_ou(x.p_org / R_MED))
        fonte = f"PNCP estimado por outro órgão (n={int(x.pncp_n_est)})"; cat = "preco_unitario_estimado_por_outro_orgao (por unidade do item)"
    elif not pd.isna(x.e2_med) and not x.flag_teto_suspeito:
        c, lo, hi = x.e2_med, x.e2_min, x.e2_max
        fonte = "teto CMED PB × (1 − desconto PE 12/2024 por tipo de produto)"; cat = "derivado: limite_regulatorio × (1 − desconto obtido em 2024)"
    else:
        c, lo, hi = x.p_org / R_MED, x.p_org / R_P75, x.p_org
        fonte = "estimativa do órgão ÷ sobre-estimação mediana (sem referência externa utilizável)"; cat = "derivado: preco_estimado_pelo_orgao ÷ razão mediana estimativa/praticado"
    teto_bind = (not pd.isna(t)) and c > t
    if teto_bind:  # referência limitada ao teto: o lance pode ficar abaixo do teto (dispersão empírica)
        lo = min(lo, t * K_LOW)
    return pd.Series({"p_ref": cap(c, t), "p_low": min(cap(lo, t), cap(c, t)), "p_high": max(cap(hi, t), cap(c, t)),
                      "fonte_ref": fonte + (" — limitado ao teto CMED" if teto_bind else ""), "categoria_valor_ref": cat,
                      "ref_limitada_teto": teto_bind})

r = pd.concat([r, r.apply(referencia, axis=1)], axis=1)

# cenário "a conferir compatível": usa mediana a conferir (limitada ao teto) no lugar do central
r["p_se_conferir_compativel"] = [cap(m, t) if not pd.isna(m) else np.nan for m, t in zip(r.conf_med, r.teto_max)]
r["flag_a_conferir"] = r.status_preco_praticado.eq("a conferir")
r["flag_acima_teto_pacote"] = r.alerta_estimativa_acima_teto_cmed.fillna(False)
r["flag_acima_teto_confirmado"] = (~r.teto_max.isna()) & (r.p_org > r.teto_max + 1e-9)
r["flag_sem_referencia_externa"] = r.fonte_ref.str.startswith("estimativa do órgão")
r["flag_sem_teto_utilizavel"] = r.teto_max.isna()
r["flag_ref_fraca"] = ~(r.prat_n >= 5)
r["p_org_limitado_teto"] = [cap(p, t) for p, t in zip(r.p_org, r.teto_max)]

r.to_csv("trabalho/ref_itens.csv", index=False, encoding="utf-8")

# ---------- auto-verificação ----------
assert len(r) == 334 and r.item.is_unique
assert abs(r.v_org.sum() - 4952438.0) < 0.5
assert (r.p_low <= r.p_ref + 1e-9).all() and (r.p_ref <= r.p_high + 1e-9).all()
assert (r.teto_max.isna() | (r.p_ref <= r.teto_max + 1e-9)).all()
assert not r.p_ref.isna().any()

with open("trabalho/10_referencias.txt", "w", encoding="utf-8") as f:
    w = lambda *a: print(*a, file=f)
    w(f"K_LOW={K_LOW:.4f} K_HIGH={K_HIGH:.4f} R_MED={R_MED:.4f} R_P75={R_P75:.4f} (n itens base={len(base)})")
    w("teto suspeito:", r.loc[r.flag_teto_suspeito, "item"].tolist(), "| preço próprio usado:", r.loc[r.fonte_ref.str.startswith("homologado no próprio"), "item"].tolist())
    w(r.groupby(r.fonte_ref.str.split(" \\(| —").str[0]).agg(n=("item", "size"), v_org=("v_org", "sum"),
      v_ref=("p_ref", lambda s: (s * r.loc[s.index, "q"]).sum())).to_string())
    w("itens com teto confirmado:", int((~r.teto_max.isna()).sum()), "| com teto (todos os vínculos) no pacote:", int((~r.teto_cmed_unitario_pb_max.isna()).sum()))
    w("ref limitada ao teto:", int(r.ref_limitada_teto.sum()))
    w("acima teto pacote:", int(r.flag_acima_teto_pacote.sum()), round(r.loc[r.flag_acima_teto_pacote, "v_org"].sum(), 2),
      "| acima teto confirmado:", int(r.flag_acima_teto_confirmado.sum()), round(r.loc[r.flag_acima_teto_confirmado, "v_org"].sum(), 2))
    w("a conferir:", int(r.flag_a_conferir.sum()), round(r.loc[r.flag_a_conferir, "v_org"].sum(), 2))
    w("sem referência externa:", int(r.flag_sem_referencia_externa.sum()), round(r.loc[r.flag_sem_referencia_externa, "v_org"].sum(), 2))
    tot = lambda c: (r[c] * r.q).sum()
    w(f"R0 org={r.v_org.sum():,.2f}  R1 org_lim_teto={tot('p_org_limitado_teto'):,.2f}  E1 central={tot('p_ref'):,.2f} low={tot('p_low'):,.2f} high={tot('p_high'):,.2f}")
    m = r.prat_med_municipal.notna() & r.prat_med.gt(0)
    w(f"razão mediana municipal/mediana geral (itens com ambos): mediana={float((r.prat_med_municipal[m]/r.prat_med[m]).median()):.4f} "
      f"p25={float((r.prat_med_municipal[m]/r.prat_med[m]).quantile(.25)):.4f} p75={float((r.prat_med_municipal[m]/r.prat_med[m]).quantile(.75)):.4f}")
print(open("trabalho/10_referencias.txt", encoding="utf-8").read())
