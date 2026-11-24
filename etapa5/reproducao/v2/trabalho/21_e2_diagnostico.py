"""Diagnóstico de E2 (desconto sobre CMED): itens que mais contribuem para E2−E1 e robustez a vínculos suspeitos."""
import pandas as pd, numpy as np
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 55); pd.set_option("display.float_format", "{:,.3f}".format)
r = pd.read_csv("trabalho/ref_itens.csv")
ok = r.e2_pref.notna() & ~r.flag_teto_suspeito.fillna(False)
r["dif"] = np.where(ok, r.q * (r.e2_pref - r.p_ref), np.nan)
r["rt"] = r.teto_min / r.prat_med
print(r.loc[ok].nlargest(20, "dif")[["item", "descricao", "q", "prat_n", "prat_med", "teto_min", "teto_max", "e2_min", "e2_pref", "tipos_produto", "rt", "dif"]].to_string(index=False))
tot = r.dif.sum(); top10 = r.dif.nlargest(10).sum()
print(f"\nE2−E1 total (itens cobertos) = {tot:,.2f}; top10 = {top10:,.2f} ({top10/tot:.1%})")
# robustez: excluindo itens com razão teto_min/mediana > 10 (possível erro de conversão residual)
m = ok & ~(r.rt > 10)
print(f"excluindo itens com teto_min/mediana > 10: n={int((ok & (r.rt > 10)).sum())}; E2−E1 = {r.dif[m].sum():,.2f}; E1 dos cobertos = {(r.q*r.p_ref)[m].sum():,.2f}; E2 = {(r.q*r.e2_pref)[m].sum():,.2f}")
# E2 com registro de menor preço, só itens com genérico
g = ok & r.tipos_produto.fillna("").str.contains("Genérico")
print(f"genéricos: E1={(r.q*r.p_ref)[g].sum():,.2f} E2_pref={(r.q*r.e2_pref)[g].sum():,.2f} E2_min={(r.q*r.e2_min)[g].sum():,.2f}; mediana item E2_pref/E1={float((r.e2_pref/r.p_ref)[g].median()):.3f}")
