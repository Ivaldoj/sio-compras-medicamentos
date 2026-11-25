"""F: sensibilidade da recomendação aos valores observados.
1) beta volume-preço fora da amostra: mesma especificação do decisor (02_precos.py) estimada nos preços pós-corte.
2) economia determinística de E2/E3/E4 (fórmula do decisor, 04_sensibilidade.py) trocando Q e P por observados.
3) ponto de equilíbrio de fracasso do certame: fórmula do decisor x fórmula corrigida, sobre o Monte Carlo reproduzido.
Requer trabalho/repro (criado por b01_reproduz.py), e01 e e02. Saída: trabalho/f01_sensibilidade.csv, trabalho/f01_beta_pos.csv"""
import os
import numpy as np
import pandas as pd

PK = "decisao_congelada/ambiente/data/decision_input_nacional/"
cesta = pd.read_parquet(PK + "problema/cesta.parquet").set_index("ap_id")
seg = cesta.cmed_laboratorios.ge(3).map({True: "concorrencial", False: "concentrado"})

# ---------- 1) beta fora da amostra ----------
def prep(df):
    df = df[(df.compatibilidade == "compativel") & ~df.flag_preco_extremo & (df.quantidade > 0) & (df.preco_unitario > 0)].copy()
    sol = df.ap_id.map(cesta.forma).isin(["comprimido", "capsula"])
    ret = df.nomeUnidadeFornecimento.fillna("").str.upper().str.startswith("SUPOSIT") | df.descricaoItem.fillna("").str.upper().str.contains("USO RETAL")
    df = df[~(sol & ret)]
    df["ano"] = df.dataResultado.str[:4].astype(int); df["seg"] = df.ap_id.map(seg)
    df["lq"], df["lp"] = np.log(df.quantidade), np.log(df.preco_unitario)
    return df

def ajusta(df):  # idêntica à do decisor, com ano de referência = o primeiro ano da amostra
    anos = pd.get_dummies(df.ano, prefix="a", dtype=float); anos = anos.drop(columns=anos.columns[0])
    X = pd.concat([pd.get_dummies(df.ap_id, dtype=float), anos,
                   pd.DataFrame({f"b_{s}": df.lq * (df.seg == s) for s in ["concorrencial", "concentrado"]})], axis=1)
    coef, *_ = np.linalg.lstsq(X.values, df.lp.values, rcond=None)
    return pd.Series(coef, index=X.columns)

def beta_ic(df, nb=300, semente=1):
    c = ajusta(df); rng = np.random.default_rng(semente); itens = df.ap_id.unique(); bo = []
    for _ in range(nb):
        am = rng.choice(itens, size=len(itens), replace=True)
        d = pd.concat([df[df.ap_id == a].assign(ap_id=f"{a}_{k}") for k, a in enumerate(am)])
        b = ajusta(d); bo.append([b["b_concorrencial"], b["b_concentrado"]])
    bo = np.array(bo)
    return pd.DataFrame({"segmento": ["concorrencial", "concentrado"], "beta": [c.b_concorrencial, c.b_concentrado],
                         "ic90_inf": np.percentile(bo, 5, 0), "ic90_sup": np.percentile(bo, 95, 0),
                         "n": [int((df.seg == s).sum()) for s in ["concorrencial", "concentrado"]]})

pos = prep(pd.read_parquet("dados_reservados/precos_comprasgov_pos.parquet"))
B = []
for nome, df in [("pós-corte, horizonte (30/01/2025-31/01/2026)", pos[pos.dataResultado <= "2026-01-31"]), ("pós-corte, tudo (até nov/2026)", pos)]:
    b = beta_ic(df); b.insert(0, "amostra", nome); B.append(b)
pre = pd.read_csv("decisao_congelada/ambiente/trabalho/elasticidade.csv").rename(columns={"n_registros": "n"}); pre.insert(0, "amostra", "decisor (pré-corte 2022-2025)")
B = pd.concat([pre[["amostra", "segmento", "beta", "ic90_inf", "ic90_sup", "n"]], *B])
B.to_csv("trabalho/f01_beta_pos.csv", index=False)
print(B.round(4).to_string(index=False))

# ---------- 2) economia determinística com valores observados ----------
pr = pd.read_csv("decisao_congelada/ambiente/trabalho/precos_referencia.csv").set_index("ap_id")
dem = pd.read_csv("decisao_congelada/ambiente/trabalho/demanda_projecao.csv").set_index("ap_id")
e1 = pd.read_csv("trabalho/e01_demanda.csv").set_index("ap_id")
e2 = pd.read_csv("trabalho/e02_precos.csv").set_index("ap_id")
el = pd.read_csv("decisao_congelada/ambiente/trabalho/elasticidade.csv").set_index("segmento")
D = [a for a in cesta.index if cesta.grupo_financiamento[a] != "1A" and a != "AP007"]
d = pr.loc[D].copy()
usa = d.n_estadual_24m >= 3
p_dec = np.where(usa, d.mediana_estadual_24m, d.mediana_24m)
p_obs = e2.loc[D, "preco_obs"].values
IDX = 1.025

def f(v, beta, dd=d):
    return np.minimum(1, np.exp(beta * (np.minimum(np.log(v), np.log(dd.lq_max_obs)) - np.log(dd.q_ref_mediana))))

def eco(Q, p, s, beta, v):
    return float((Q * p * IDX * s * (1 - f(v, beta))).sum())

bc = d.segmento.map(el.beta).values
bpos = pd.read_csv("trabalho/f01_beta_pos.csv"); bpos = bpos[bpos.amostra.str.startswith("pós-corte, horizonte")].set_index("segmento").beta
bp = d.segmento.map(bpos).values
Qd, Qo = dem.loc[D, "q_central"].values, e1.loc[D, "obs"].values
# correção AP052 (mediana estadual 24m sem supositório/uso retal) calculada em p01_pacote.py
corr = pd.read_csv("trabalho/p01_ap052.csv").iloc[0]
p_dec_corr = p_dec.copy(); p_dec_corr[D.index("AP052")] = corr.mediana_estadual_24m_sem_retal
S = []
for nome, Q, p, b in [("decisor (Q e P projetados)", Qd, p_dec, bc),
                      ("Q observada", Qo, p_dec, bc),
                      ("P observado (mediana estadual H)", Qd, p_obs, bc),
                      ("Q e P observados", Qo, p_obs, bc),
                      ("P do decisor com AP052 corrigido", Qd, p_dec_corr, bc),
                      ("Q e P observados + beta pós-corte", Qo, p_obs, bp)]:
    base = float((Q * p * IDX).sum())
    r = dict(cenario=nome, custo_E1_descentralizados=base,
             eco_E2_s055=eco(Q, p, .55, b, d.v_nacional), eco_E3_s040=eco(Q, p, .40, b, d.v_regiao_mediana),
             eco_E3_s055_mesma_transicao=eco(Q, p, .55, b, d.v_regiao_mediana), eco_E4_s015=eco(Q, p, .15, b, d.v_nacional),
             eco_E2_pleno=eco(Q, p, 1, b, d.v_nacional), eco_E3_pleno=eco(Q, p, 1, b, d.v_regiao_mediana))
    r["eco_E2_pct"] = r["eco_E2_s055"] / base
    r["ordem"] = " > ".join(k for k, _ in sorted([("E2", r["eco_E2_s055"]), ("E3", r["eco_E3_s040"]), ("E4", r["eco_E4_s015"]), ("E1", 0.0)], key=lambda t: -t[1]))
    S.append(r)
S = pd.DataFrame(S)
# contribuição por item no cenário Q e P observados
it = pd.DataFrame({"ap_id": D, "eco_decisor": Qd * p_dec * IDX * .55 * (1 - f(d.v_nacional, bc)),
                   "eco_QP_obs": Qo * p_obs * IDX * .55 * (1 - f(d.v_nacional, bc)), "p_dec": p_dec, "p_obs": p_obs, "Qd": Qd, "Qo": Qo})
it.to_csv("trabalho/f01_eco_item.csv", index=False)

# ---------- 3) ponto de equilíbrio: reexecuta o Monte Carlo do decisor na cópia e aplica as duas fórmulas ----------
src = open("decisao_congelada/ambiente/trabalho/03_estrategias.py", encoding="utf8").read().split("# ---------------- Por item")[0]
cwd = os.getcwd(); os.chdir("trabalho/repro"); g = {"__name__": "mc"}
try:
    exec(compile(src, "03_estrategias.py", "exec"), g)
finally:
    os.chdir(cwd)
eco2, extra = g["eco2"], g["extra_falha"]
pf_dec, pf_cor = np.median(eco2 / (eco2 + extra)), np.median(eco2 / extra)
print(f"\nponto de equilíbrio (mediana MC): fórmula do decisor {pf_dec:.3f}; corrigida eco/extra {pf_cor:.3f}")
S = pd.concat([S, pd.DataFrame([dict(cenario="ponto de equilíbrio de fracasso (MC do decisor)", eco_E2_s055=np.nan,
                                     nota=f"decisor {pf_dec:.3f}; corrigido {pf_cor:.3f}")])])
S.to_csv("trabalho/f01_sensibilidade.csv", index=False)
pd.set_option("display.width", 300)
print(S.drop(columns=["nota"], errors="ignore").round(3).to_string(index=False))
print(it.round(2).to_string(index=False))
