"""D/F: o efeito volume-preço vale para os 11 itens descentralizados? (informação disponível em 29/01/2025)
- uniformidade de preço entre SES (parcela das compras estaduais a +-2% da mediana, 24m pré-corte)
- inclinação log-log por item (mesma amostra do decisor: compativel, sem extremo, 2022-02-01 a 2025-01-29, com efeito de ano)
- economia determinística de E2 (fórmula do decisor, s=0,55) usando beta por item (limitado a [beta_IC90_inf, 0])
Saída: trabalho/d02_beta_por_item.csv"""
import numpy as np
import pandas as pd

PK = "decisao_congelada/ambiente/data/decision_input_nacional/"
cesta = pd.read_parquet(PK + "problema/cesta.parquet").set_index("ap_id")
cg = pd.read_parquet(PK + "mercado/precos_comprasgov.parquet")
cg = cg[(cg.compatibilidade == "compativel") & ~cg.flag_preco_extremo & (cg.dataResultado >= "2022-02-01") & (cg.dataResultado <= "2025-01-29")
        & (cg.quantidade > 0) & (cg.preco_unitario > 0)]
pr = pd.read_csv("decisao_congelada/ambiente/trabalho/precos_referencia.csv").set_index("ap_id")
dem = pd.read_csv("decisao_congelada/ambiente/trabalho/demanda_projecao.csv").set_index("ap_id")
el = pd.read_csv("decisao_congelada/ambiente/trabalho/elasticidade.csv").set_index("segmento")
D = [a for a in cesta.index if cesta.grupo_financiamento[a] != "1A" and a != "AP007"]
L = []
for a in D:
    x = cg[cg.ap_id == a]
    e = x[(x.esfera == "E") & (x.dataResultado >= "2023-02-01")]
    med = e.preco_unitario.median()
    X = np.column_stack([np.ones(len(x)), np.log(x.quantidade), pd.get_dummies(x.dataResultado.str[:4], drop_first=True, dtype=float).values])
    b = np.linalg.lstsq(X, np.log(x.preco_unitario), rcond=None)[0][1]
    L.append(dict(ap_id=a, nome=cesta.nome[a][:40], grupo=cesta.grupo_financiamento[a], cmed_laboratorios=cesta.cmed_laboratorios[a], n_registros=len(x),
                  n_estadual_24m=len(e), mediana_estadual_24m=med, parcela_estadual_a_2pct_mediana=((e.preco_unitario / med - 1).abs() <= .02).mean(),
                  cv_estadual=e.preco_unitario.std() / e.preco_unitario.mean(), beta_item=b, n_uf_estaduais=e.uf.nunique()))
t = pd.DataFrame(L).set_index("ap_id")
# economia de E2 com beta por item (limitado a [IC90 inferior do segmento, 0]) x beta do segmento (decisor)
d = pr.loc[D]
p = np.where(d.n_estadual_24m >= 3, d.mediana_estadual_24m, d.mediana_24m)
bseg = d.segmento.map(el.beta).values
bi = np.clip(t.beta_item.values, d.segmento.map(el.ic90_inf).values, 0)
f = lambda b: np.minimum(1, np.exp(b * (np.minimum(np.log(d.v_nacional), np.log(d.lq_max_obs)) - np.log(d.q_ref_mediana))))
t["eco_E2_beta_segmento"] = dem.loc[D, "q_central"].values * p * 1.025 * .55 * (1 - f(bseg))
t["eco_E2_beta_item"] = dem.loc[D, "q_central"].values * p * 1.025 * .55 * (1 - f(bi))
t.to_csv("trabalho/d02_beta_por_item.csv")
pd.set_option("display.width", 250)
print(t.round(3).to_string())
print(f"economia E2 (s=0,55): beta do segmento {t.eco_E2_beta_segmento.sum()/1e6:.1f} mi; beta por item {t.eco_E2_beta_item.sum()/1e6:.1f} mi")
