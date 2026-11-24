"""Etapa 5 / 02 — verificação independente dos cálculos do agente (pacote v1, ex ante).

Não reutiliza os scripts do agente: recalcula, com código próprio e a partir do pacote v1, os números
que sustentam a decisão, e compara com os valores DECLARADOS nos entregáveis congelados
(saida/plano_por_item.csv, saida/03_comparacao.csv e textos .md).

Saída: resultados/verificacao_calculos.csv  (id, o que foi verificado, declarado, recalculado, confere, observação)
       resultados/verificacao_referencias_item.csv (recomputo da referência e do teto, item a item)
"""
import os
import re
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e5_comum import RAIZ, RES, SAIDA, V1

sys.path.insert(0, os.path.join(RAIZ, "scripts"))
import consulta_agente as q  # módulo de consulta do pacote (não é código do agente); lê só data/decision_input

con = q.conectar()
sql = lambda s: con.execute(s).df()
plano = pd.read_csv(os.path.join(SAIDA, "plano_por_item.csv"))
comp = pd.read_csv(os.path.join(SAIDA, "03_comparacao.csv"))
txt = {f: open(os.path.join(SAIDA, f), encoding="utf-8").read() for f in os.listdir(SAIDA) if f.endswith(".md")}
itens = sql("SELECT * FROM itens ORDER BY item")
L = []


def reg(i, o_que, declarado, recalculado, tol=0.5, obs=""):
    if isinstance(declarado, (int, float, np.floating, np.integer)) and isinstance(recalculado, (int, float, np.floating, np.integer)):
        ok = abs(float(declarado) - float(recalculado)) <= tol
    else:
        ok = declarado == recalculado
    L.append({"id": i, "verificacao": o_que, "declarado": declarado, "recalculado": recalculado, "confere": bool(ok), "observacao": obs})


def num_br(s):
    return float(s.replace(".", "").replace(",", "."))


def linha_comp(prefixo):
    return comp[comp.iloc[:, 0].astype(str).str.startswith(prefixo)].iloc[0]


# ---------- V01–V02: totais ----------
qtd = plano.quantidade_etp
reg("V01", "R0 = Σ valor estimado do órgão (334 itens)", 4952438.0, float(itens.valor_total_estimado_orgao.sum()))
reg("V01b", "plano: 334 itens, quantidades = ETP", 334, int((plano.merge(itens[["item", "quantidade_estimada"]], on="item")
                                                              .eval("quantidade_etp == quantidade_estimada")).sum()), tol=0)
cols_num = [c for c in comp.columns if comp[c].dtype != object]
e1 = linha_comp("E1")
c_central = [c for c in comp.columns if "central" in c.lower()][0]
c_baixo = [c for c in comp.columns if "baixo" in c.lower()][0]
c_alto = [c for c in comp.columns if "alto" in c.lower()][0]
E1c, E1b, E1a = float(e1[c_central]), float(e1[c_baixo]), float(e1[c_alto])
# o plano arredonda o preço unitário a 4 casas; a soma exata usa valor_ref_total
reg("V02a", "E1 central = Σ valor_ref_total do plano", E1c, float(plano.valor_ref_total.sum()), tol=1)
reg("V02b", "E1 central = Σ quantidade × preco_ref_unitario (preço arredondado a 4 casas)", E1c, float((qtd * plano.preco_ref_unitario).sum()), tol=5,
    obs="diferença só de arredondamento do preço unitário no CSV")
reg("V02c", "E1 baixo = Σ valor_faixa_baixo", E1b, float(plano.valor_faixa_baixo.sum()), tol=1)
reg("V02d", "E1 alto = Σ valor_faixa_alto", E1a, float(plano.valor_faixa_alto.sum()), tol=1)
reg("V02e", "faixa coerente em todos os itens (baixo ≤ ref ≤ alto)", 334,
    int(((plano.faixa_preco_baixo <= plano.preco_ref_unitario + 1e-9) & (plano.preco_ref_unitario <= plano.faixa_preco_alto + 1e-9)).sum()), tol=0)

# ---------- V03: recomputo independente da mediana praticada ----------
prat = sql("""
SELECT item, catmat, data_compra, preco_unitario_praticado p FROM v_bps_comparavel
 WHERE NOT coalesce(flag_preco_extremo,false) AND NOT coalesce(flag_duplicata_negocio,false) AND preco_unitario_praticado > 0
UNION ALL
SELECT item, catmat, data_compra, preco_unitario_praticado FROM v_comprasgov_comparavel
 WHERE NOT coalesce(flag_possivel_duplicata_bps,false) AND preco_unitario_praticado > 0""")
# regra declarada pelo agente (D04) para as análogas: só o CATMAT específico
prat = prat[~((prat.item == 194) & (prat.catmat != "468664")) & ~((prat.item == 195) & (prat.catmat != "440255"))]
prat["rec"] = pd.to_datetime(prat.data_compra) >= pd.Timestamp("2023-01-29")
rows = []
for it, g in prat.groupby("item"):
    u = g[g.rec] if g.rec.sum() >= 5 else g
    rows.append({"item": it, "n": len(u), "med": u.p.median(), "p25": u.p.quantile(.25), "p75": u.p.quantile(.75)})
med = pd.DataFrame(rows)

# ---------- V04: recomputo independente do teto CMED "confirmado" ----------
teto = sql("""
SELECT t.item, t.registro, t.tipo_preco, t.aliquota_icms, t.valor_por_unidade_item teto_u, a.tipo_produto, a.cap,
       r.status, coalesce(r.inspecao_amostral_ia,'') insp
FROM v_cmed_teto_unitario t
JOIN regras_conversao r ON r.item = t.item AND CAST(r.registro AS VARCHAR) = t.registro
JOIN cmed_apresentacoes a ON a.registro = t.registro
WHERE t.aliquota_aplicavel_pb AND t.aplicabilidade IN ('teto para compras administrativas','teto obrigatório (produto com CAP)')""")
teto["ok"] = ~teto.status.str.contains("COM ALERTA") & ~teto.insp.str.startswith("ERRO")
tmax = teto[teto.ok].groupby("item").teto_u.agg(teto_max="max", teto_min="min").reset_index()
tmax_todos = teto.groupby("item").teto_u.max().rename("teto_max_todos_vinculos").reset_index()

v = (plano[["item", "descricao", "quantidade_etp", "preco_ref_unitario", "fonte_preco_ref", "categoria_valor", "teto_cmed_unitario_aplicavel_max",
            "preco_estimado_orgao", "valor_estimado_orgao", "valor_ref_total", "flag_a_conferir", "flag_acima_teto_confirmado",
            "flag_sem_referencia_externa"]]
     .merge(med, on="item", how="left").merge(tmax, on="item", how="left").merge(tmax_todos, on="item", how="left"))
v["ref_recalc"] = np.where(v.teto_max.notna(), np.minimum(v.med, v.teto_max), v.med)
e_prat = v.fonte_preco_ref.str.startswith("praticado")
v["ref_confere"] = np.where(e_prat, np.abs(v.ref_recalc - v.preco_ref_unitario) <= 5e-4, np.nan)
v["teto_confere"] = (np.abs(v.teto_max - v.teto_cmed_unitario_aplicavel_max) <= 5e-4) | (v.teto_max.isna() & v.teto_cmed_unitario_aplicavel_max.isna())
v.to_csv(os.path.join(RES, "verificacao_referencias_item.csv"), index=False, encoding="utf-8")

reg("V03a", "itens cuja referência é 'praticado compatível'", 247, int(e_prat.sum()), tol=0, obs="declarado em 01_diagnostico.md §3.2")
reg("V03b", "referência (mediana praticada 24 m, limitada ao teto) recalculada item a item — itens que conferem", int(e_prat.sum()),
    int(v.loc[e_prat, "ref_confere"].sum()), tol=0, obs="recomputo próprio em pandas, tolerância R$ 0,0005")
reg("V03c", "itens com praticado compatível no pacote mas referência de outra fonte", 0, int((~e_prat & v.med.notna()).sum()), tol=0)
reg("V04", "teto CMED máximo 'confirmado' recalculado item a item — itens que conferem", 334, int(v.teto_confere.sum()), tol=0,
    obs="PF (PMVG se CAP), alíquota aplicável à PB, sem vínculos COM ALERTA/ERRO")
reg("V05", "itens com referência acima do teto aplicável (B3)", 0,
    int((v.teto_max.notna() & (v.preco_ref_unitario > v.teto_max + 5e-4)).sum()), tol=0)

# ---------- V06–V07: R1 e itens acima do teto ----------
p_lim = np.where(v.teto_max.notna(), np.minimum(v.preco_estimado_orgao, v.teto_max), v.preco_estimado_orgao)
R1 = float((v.quantidade_etp * p_lim).sum())
reg("V06", "R1 = Σ q × min(estimativa do órgão, teto)", float(linha_comp("R1")[c_central]), R1, tol=1)
ac = v.teto_max.notna() & (v.preco_estimado_orgao > v.teto_max + 1e-9)
reg("V07a", "itens com estimativa do órgão acima do teto (confirmado)", 41, int(ac.sum()), tol=0)
reg("V07b", "valor (R0) desses itens", 1932504.0, float(v.loc[ac, "valor_estimado_orgao"].sum()), tol=1)
exc = float((v.quantidade_etp * (v.preco_estimado_orgao - v.teto_max))[ac].sum())
reg("V07c", "excesso sobre o teto (R0 − R1)", 1396287.0, exc, tol=1)
exc_can = float((v.quantidade_etp * (v.preco_estimado_orgao - v.teto_max))[ac & v.item.isin([196, 199])].sum())
reg("V07d", "parte das canetas 196/199 no excesso (%)", 85.6, round(100 * exc_can / exc, 1), tol=0.05)
reg("V07e", "flag_acima_teto_confirmado do plano = recomputo", 334, int((plano.flag_acima_teto_confirmado.values == ac.values).sum()), tol=0)
reg("V07f", "itens marcados pelo pacote (alerta_estimativa_acima_teto_cmed)", 40, int(itens.alerta_estimativa_acima_teto_cmed.fillna(False).sum()), tol=0)

# ---------- V08: 'a conferir' nunca como preço central ----------
ac_items = itens.loc[itens.status_preco_praticado.eq("a conferir"), "item"]
reg("V08a", "itens com preço praticado só 'a conferir'", 25, int(len(ac_items)), tol=0)
fontes_ac = plano[plano.item.isin(ac_items)].fonte_preco_ref.str.split(r" \(| —", regex=True).str[0].value_counts().to_dict()
reg("V08b", "desses 25, quantos têm referência central vinda de registro 'a conferir' (B4)", 0,
    int(plano[plano.item.isin(ac_items)].fonte_preco_ref.str.contains("conferir", case=False).sum()), tol=0, obs=str(fontes_ac))
reg("V08c", "valor R0 dos 25 itens a conferir", 1470360.0, float(itens.loc[itens.item.isin(ac_items), "valor_total_estimado_orgao"].sum()), tol=1)

# ---------- V09: sem referência externa ----------
sr = plano.flag_sem_referencia_externa
reg("V09a", "itens sem referência externa", 63, int(sr.sum()), tol=0)
reg("V09b", "valor R0 desses itens", 444019.0, float(plano.loc[sr, "valor_estimado_orgao"].sum()), tol=1)
reg("V09c", "referência provisória desses itens (≈ R$ 217 mil)", 217000.0, float(plano.loc[sr, "valor_ref_total"].sum()), tol=1000)
base = v[(v.n >= 5) & (v.med > 0)]
# a razão de sobre-estimação do agente usa a mediana praticada sem o limite do teto e todos os itens com n>=5
rmed = float((base.preco_estimado_orgao / base.med).median())
reg("V09d", "sobre-estimação mediana estimativa do órgão / mediana praticada", 2.044, round(rmed, 3), tol=0.0006, obs=f"n={len(base)} itens com ≥5 preços")
reg("V09e", "referência dos sem-referência = estimativa ÷ 2,044 (itens que conferem)", int(sr.sum()),
    int((np.abs(plano.loc[sr, "preco_ref_unitario"] - np.where(v.loc[sr, "teto_max"].notna(),
         np.minimum(plano.loc[sr, "preco_estimado_orgao"] / rmed, v.loc[sr, "teto_max"]), plano.loc[sr, "preco_estimado_orgao"] / rmed)) <= 5e-4).sum()), tol=0)

# ---------- V10: E2 recalculado de forma independente ----------
DESC = {"Genérico": 0.6011, "Similar": 0.5101}
pf = sql("SELECT item, registro, valor_por_unidade_item pf_u FROM v_cmed_teto_unitario WHERE aliquota_aplicavel_pb AND tipo_preco = 'PF'")
t2 = teto[teto.ok].merge(pf, on=["item", "registro"])
t2["d"] = t2.tipo_produto.map(DESC).fillna(0.1801)
t2["e2_u"] = np.minimum(t2.pf_u * (1 - t2.d), t2.teto_u)
t2["pref"] = t2.tipo_produto.map({"Genérico": 0, "Similar": 1}).fillna(2)
pref = t2[t2.pref == t2.groupby("item").pref.transform("min")].groupby("item").e2_u.median().rename("e2_pref")
e2 = t2.groupby("item").e2_u.agg(e2_min="min", e2_med="median", e2_max="max").join(pref).reset_index()
v2 = v.merge(e2, on="item", how="left")
suspeito = (v2.teto_min / v2.med) > 20
cob = v2.e2_pref.notna() & ~suspeito
E2c = float((v2.quantidade_etp * np.where(cob, v2.e2_pref, v2.preco_ref_unitario)).sum())
E2b = float((v2.quantidade_etp * np.where(cob, v2.e2_min, plano.faixa_preco_baixo)).sum())
E2a = float((v2.quantidade_etp * np.where(cob, v2.e2_med, plano.faixa_preco_alto)).sum())
e2l = linha_comp("E2")
reg("V10a", "E2 central (desconto 2024 sobre PF, categoria mais barata; restante via E1)", float(e2l[c_central]), E2c, tol=5)
reg("V10b", "E2 baixo (registro de menor preço)", float(e2l[c_baixo]), E2b, tol=5)
reg("V10c", "E2 alto (mediana de todos os registros)", float(e2l[c_alto]), E2a, tol=5)
reg("V10d", "itens cobertos pelo desconto no E2", 225, int(cob.sum()), tol=0)
# ---------- V11–V12: economias e ponto de empate ----------
reg("V11a", "economia potencial principal E2 − E1 (central)", 2223619.0, E2c - float(plano.valor_ref_total.sum()), tol=5)
reg("V11b", "economia potencial secundária R1 − E1 (central)", 1744021.0, R1 - float(plano.valor_ref_total.sum()), tol=5,
    obs="texto: 'R$ 1,74 mi'")
reg("V11c", "faixa plausível E2−E1: baixo×baixo", 800988.0, E2b - E1b, tol=5)
reg("V11d", "faixa plausível E2−E1: alto×alto", 2034872.0, E2a - E1a, tol=5)
reg("V11e", "extremo cruzado E2 baixo − E1 alto", -208718.0, E2b - E1a, tol=5)
reg("V11f", "faixa R1 − E1: [R1 − alto, R1 − baixo] ≈ 1,05 a 2,06 mi", "1.05–2.06", f"{(R1 - E1a) / 1e6:.2f}–{(R1 - E1b) / 1e6:.2f}")
e1_cob = float((v2.quantidade_etp * v2.preco_ref_unitario)[cob].sum())
e2_cob = float((v2.quantidade_etp * v2.e2_pref)[cob].sum())
m = e1_cob / e2_cob
reg("V12a", "multiplicador de empate sobre os preços do E2 (≈ 0,36)", 0.36, round(m, 2), tol=0.005)
reg("V12b", "descontos de empate genérico/similar/ético (%)", "85.6/82.4/70.5",
    "/".join(f"{100 * (1 - m * (1 - d)):.1f}" for d in (0.6011, 0.5101, 0.1801)))

# ---------- V13: ME/EPP ----------
reg("V13a", "itens ≤ R$ 80 mil pela referência do agente (texto: 332)", 332, int((plano.valor_ref_total <= 80000).sum()), tol=0)
n80_org = int((plano.valor_estimado_orgao <= 80000).sum())
reg("V13b", "itens ≤ R$ 80 mil pela estimativa do órgão (contexto; o agente não declarou este número)", n80_org, n80_org, tol=0,
    obs="informativo: a base do benefício é o valor estimado do item no edital; pelas duas bases a regra alcança quase todos os itens")

# ---------- V14: insulinas ----------
ins = plano[plano.item.between(194, 199)]
reg("V14a", "insulinas: valor R0 (R$ 1.407.331; 28,4%)", 1407331.0, float(ins.valor_estimado_orgao.sum()), tol=1)
reg("V14b", "insulinas: peso em R0 (%)", 28.4, round(100 * ins.valor_estimado_orgao.sum() / 4952438, 1), tol=0.05)
reg("V14c", "insulinas: referência E1 (R$ 172.639; 9,5%)", 172639.0, float(ins.valor_ref_total.sum()), tol=1)
for it, mult in ((196, 9.6), (199, 9.3)):
    r_ = plano[plano.item == it].iloc[0]
    reg(f"V14d{it}", f"item {it}: estimativa do órgão ÷ teto CMED", mult, round(r_.preco_estimado_orgao / r_.teto_cmed_unitario_aplicavel_max, 1), tol=0.05)

# ---------- V15: categoria de valor única (B6) ----------
reg("V15", "itens com mais de uma categoria_valor na referência (B6)", 0, int(plano.categoria_valor.str.contains(r"\|").sum()), tol=0,
    obs=str(plano.categoria_valor.str.split(r" \(", regex=True).str[0].value_counts().to_dict()))

# ---------- V16: histórico 2024 ----------
ex = sql("SELECT * FROM execucao_2024_licitacao")
cval = [c for c in ex.columns if "empenh" in c.lower()][0]
clic = [c for c in ex.columns if "licit" in c.lower()][0]
tot24 = float(ex[cval].sum())
pe12 = float(ex.loc[ex[clic].astype(str).str.contains("000122024"), cval].sum())
reg("V16a", "despesa com medicamentos em 2024 (empenhado)", 1953288.72, tot24, tol=0.01)
reg("V16b", "parte do PE 12/2024 (desconto sobre CMED) em 2024 (%)", 62.6, round(100 * pe12 / tot24, 1), tol=0.05)
reg("V16c", "E1 central ÷ gasto de 2024 (texto: 0,93)", 0.93, round(float(plano.valor_ref_total.sum()) / tot24, 2), tol=0.005)

# ---------- V17: números do resumo executivo × CSV ----------
res = txt["00_resumo_executivo.md"]
achados = {"E1 central 1,81 mi": ("1,81 mi", E1c / 1e6, 1.81), "E1 faixa 1,50": ("1,50", E1b / 1e6, 1.50), "E1 faixa 2,51": ("2,51 mi", E1a / 1e6, 2.51),
           "E2 central 4,04 mi": ("4,04 mi", E2c / 1e6, 4.04), "economia 2,22 mi": ("2,22 mi", (E2c - E1c) / 1e6, 2.22),
           "R1 3,56 mi": ("3,56 mi", R1 / 1e6, 3.56), "economia vs R1 1,74 mi": ("1,74 mi", (R1 - E1c) / 1e6, 1.74)}
for nome, (padrao, valor, esperado) in achados.items():
    reg("V17", f"resumo executivo cita '{padrao}' e o valor recalculado arredonda para isso ({nome})", True,
        bool(padrao in res and abs(round(valor, 2) - esperado) < 1e-9), obs=f"recalculado = {valor:.4f} mi")

# ---------- V18: demanda (SRP × contrato fixo) ----------
reg("V18a", "E1 com demanda de 75% (SRP paga d × C)", 1359098.0, 0.75 * E1c, tol=1)
reg("V18b", "E4 com demanda de 75% (contrato fixo compromete C)", 1812130.0, E1c, tol=1)

df = pd.DataFrame(L)
df.to_csv(os.path.join(RES, "verificacao_calculos.csv"), index=False, encoding="utf-8")
print(df[["id", "verificacao", "declarado", "recalculado", "confere"]].to_string(index=False, max_colwidth=70))
print(f"\nCONFEREM: {int(df.confere.sum())}/{len(df)}")
