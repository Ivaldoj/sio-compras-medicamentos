"""Preços de referência e efeito volume-preço.

Entrada: precos_comprasgov (base principal), precos_bps (só conferência, NUNCA somada), cmed_teto/cesta (teto),
         trabalho/demanda_projecao.csv, trabalho/demanda_uf_projecao.csv.
Saídas:  trabalho/elasticidade.csv      coeficiente volume-preço por segmento de mercado, IC bootstrap por item
         trabalho/precos_referencia.csv uma linha por apresentação

Filtro da amostra de preços (Compras.gov): compatibilidade='compativel', flag_preco_extremo=False,
dataResultado em [2022-02-01, 2025-01-29]. categoria_valor = preço homologado/praticado (não é pagamento).
Modelo: log(preço) = efeito_item + beta_segmento*log(quantidade) + efeito_ano  (MQO, efeitos fixos por item).
Segmento: 'concorrencial' se cesta.cmed_laboratorios >= 3; senão 'concentrado'.
Previsões de preço por volume são feitas com log(q) limitado à faixa observada do próprio item (sem extrapolar).
"""
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.join("data", "decision_input_nacional"))
import consulta as q

con = q.conectar()
REGIAO = {**dict.fromkeys(["AC", "AM", "AP", "PA", "RO", "RR", "TO"], "N"),
          **dict.fromkeys(["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"], "NE"),
          **dict.fromkeys(["DF", "GO", "MS", "MT"], "CO"),
          **dict.fromkeys(["ES", "MG", "RJ", "SP"], "SE"),
          **dict.fromkeys(["PR", "RS", "SC"], "S")}  # IBGE (conhecimento prévio)

cesta = con.sql("SELECT * FROM cesta").df()
dem = pd.read_csv("trabalho/demanda_projecao.csv")
duf = pd.read_csv("trabalho/demanda_uf_projecao.csv")
assert set(duf.uf) <= set(REGIAO)

cg = con.sql("""SELECT ap_id, esfera, uf, nomeUasg, niFornecedor, quantidade q, preco_unitario p, dataResultado
                FROM precos_comprasgov
                WHERE compatibilidade='compativel' AND NOT flag_preco_extremo
                  AND dataResultado >= '2022-02-01' AND dataResultado <= '2025-01-29'
                  AND quantidade > 0 AND preco_unitario > 0""").df()
cg["ano"] = cg.dataResultado.str[:4].astype(int)
seg = cesta.set_index("ap_id").cmed_laboratorios.ge(3).map({True: "concorrencial", False: "concentrado"})
cg["seg"] = cg.ap_id.map(seg)
cg["lq"], cg["lp"] = np.log(cg.q), np.log(cg.p)


def ajusta(df):
    """MQO com efeitos fixos de item e ano; retorna betas por segmento, efeitos de item e de ano."""
    X = pd.concat([pd.get_dummies(df.ap_id, dtype=float),
                   pd.get_dummies(df.ano, prefix="a", dtype=float).drop(columns="a_2024", errors="ignore"),
                   pd.DataFrame({f"b_{s}": df.lq * (df.seg == s) for s in ["concorrencial", "concentrado"]})], axis=1)
    coef, *_ = np.linalg.lstsq(X.values, df.lp.values, rcond=None)
    return pd.Series(coef, index=X.columns)


coef = ajusta(cg)
rng = np.random.default_rng(20250129)
itens = cg.ap_id.unique()
boot = []
for _ in range(400):  # bootstrap por item (cluster)
    amostra = rng.choice(itens, size=len(itens), replace=True)
    d = pd.concat([cg[cg.ap_id == a].assign(ap_id=f"{a}_{k}") for k, a in enumerate(amostra)])
    b = ajusta(d)
    boot.append([b["b_concorrencial"], b["b_concentrado"]])
boot = np.array(boot)
el = pd.DataFrame({"segmento": ["concorrencial", "concentrado"],
                   "beta": [coef["b_concorrencial"], coef["b_concentrado"]],
                   "ic90_inf": np.percentile(boot, 5, axis=0), "ic90_sup": np.percentile(boot, 95, axis=0),
                   "n_registros": [int((cg.seg == s).sum()) for s in ["concorrencial", "concentrado"]],
                   "n_itens": [cg[cg.seg == s].ap_id.nunique() for s in ["concorrencial", "concentrado"]]})
el.to_csv("trabalho/elasticidade.csv", index=False)
print(el.round(4).to_string())

# Volumes por arranjo de compra (quantidade central anual)
duf["regiao"] = duf.uf.map(REGIAO)
vol = pd.DataFrame({
    "v_uf_mediana": duf.groupby("ap_id").q_central_uf.median(),
    "v_regiao_mediana": duf.groupby(["ap_id", "regiao"]).q_central_uf.sum().groupby("ap_id").median(),
    "v_nacional": dem.set_index("ap_id").q_central})

lim = cg.groupby("ap_id").lq.agg(lq_min="min", lq_max="max")


def preco_vol(ap, v, beta):
    """Preço previsto (nível 2024) para compra de volume v; log(v) limitado à faixa observada do item."""
    lv = np.clip(np.log(v), lim.lq_min[ap], lim.lq_max[ap])
    return float(np.exp(coef[ap] + beta * lv))


rec = cg[cg.dataResultado >= "2023-02-01"]  # últimos 24 meses para estatísticas descritivas
bps = con.sql("""SELECT ap_id, preco_unitario_praticado p FROM precos_bps
                 WHERE NOT flag_preco_extremo AND NOT flag_duplicata_negocio AND data_compra >= '2023-02-01'""").df()
# DLOG/MS: inclui registros com flag_preco_extremo, pois a flag compara com mediana dominada por compras pequenas (decisão D08)
dl = con.sql("""SELECT ap_id, quantidade q, preco_unitario p, dataResultado, flag_preco_extremo fx FROM precos_comprasgov
                WHERE compatibilidade='compativel' AND nomeUasg LIKE 'DEPARTAMENTO DE LOG%'
                  AND dataResultado >= '2022-02-01' AND dataResultado <= '2025-01-29'""").df().merge(dem[["ap_id", "d12"]], on="ap_id")
dl = dl[dl.q >= 0.10 * dl.d12].sort_values("dataResultado")  # compra programática do MS: >=10% da dispensação anual (H09)

linhas = []
for _, c in cesta.iterrows():
    a = c.ap_id
    s = seg[a]
    b = coef[f"b_{s}"]
    r, e = rec[rec.ap_id == a], rec[(rec.ap_id == a) & (rec.esfera == "E")]
    d = dl[dl.ap_id == a]
    du = d[d.dataResultado == d.dataResultado.iloc[-1]] if len(d) else d
    linhas.append(dict(
        ap_id=a, segmento=s, cmed_laboratorios=c.cmed_laboratorios,
        n_24m=len(r), p25_24m=r.p.quantile(.25), mediana_24m=r.p.median(), p75_24m=r.p.quantile(.75),
        n_estadual_24m=len(e), mediana_estadual_24m=e.p.median() if len(e) else np.nan,
        p25_estadual_24m=e.p.quantile(.25) if len(e) else np.nan, p75_estadual_24m=e.p.quantile(.75) if len(e) else np.nan,
        n_fornecedores_24m=r.niFornecedor.nunique(),
        dlog_prog_preco=np.average(du.p, weights=du.q) if len(d) else np.nan,  # média ponderada da última compra
        dlog_prog_data=d.dataResultado.iloc[-1] if len(d) else "", dlog_prog_qtd=du.q.sum() if len(d) else np.nan,
        dlog_flag_extremo=bool(du.fx.any()) if len(d) else False,
        q_ref_mediana=(e if len(e) >= 3 else r).q.median(),
        bps_mediana_24m=bps[bps.ap_id == a].p.median(), bps_n_24m=int((bps.ap_id == a).sum()),
        p_mod_uf=preco_vol(a, vol.v_uf_mediana[a], b), p_mod_regiao=preco_vol(a, vol.v_regiao_mediana[a], b),
        p_mod_nacional=preco_vol(a, vol.v_nacional[a], b),
        v_uf_mediana=vol.v_uf_mediana[a], v_regiao_mediana=vol.v_regiao_mediana[a], v_nacional=vol.v_nacional[a],
        lq_max_obs=np.exp(lim.lq_max[a]),
        teto0_min=c.teto0_unit_min, teto0_mediana=c.teto0_unit_mediana, teto0_max=c.teto0_unit_max,
        teto18_mediana=c.teto18_unit_mediana, todos_convenio_87=c.todos_convenio_87, algum_cap=c.algum_cap,
        sia_unit_1b=c.valor_unitario_financiado_sia))
pr = pd.DataFrame(linhas)
# teto aplicável conservador: maior teto entre produtos (0% ICMS se todos Conv.87; senão 18% como aproximação, H10)
pr["teto_aplicavel"] = np.where(pr.todos_convenio_87, pr.teto0_max, pr[["teto0_max", "teto18_mediana"]].max(axis=1))
pr["flag_mediana_acima_teto"] = pr.mediana_24m > pr.teto_aplicavel
pr.to_csv("trabalho/precos_referencia.csv", index=False)
print(pr[["ap_id", "segmento", "mediana_24m", "mediana_estadual_24m", "dlog_prog_preco", "p_mod_uf", "p_mod_regiao",
          "p_mod_nacional", "bps_mediana_24m", "teto_aplicavel", "flag_mediana_acima_teto"]].round(2).to_string())
