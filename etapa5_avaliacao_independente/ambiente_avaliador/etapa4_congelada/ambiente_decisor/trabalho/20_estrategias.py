"""Custos por estratégia (faixas), sensibilidades e cobertura. Lê trabalho/ref_itens.csv (de 10_referencias.py).

Saídas: trabalho/20_estrategias.txt, trabalho/custos_estrategias.csv, trabalho/sensibilidades.csv
Estratégias (ver saida/02_alternativas.md):
 E1 pregão eletrônico SRP, menor preço por item, referência saneada (mediana praticada ≤ teto CMED)
 E2 pregão eletrônico SRP por maior desconto sobre a tabela CMED (modelo PE 12/2024); itens sem teto utilizável -> E1
 E3 adesão a atas (carona) onde houver ata SRP homologada no PNCP com quantidade suficiente; restante -> E1
 E4 pregão com contrato de quantidade fixa (sem SRP), entrega integral/escalonada; preço unitário = E1 (hipótese otimista p/ E4)
"""
import sys; sys.path.insert(0, "scripts"); import consulta_agente as q
import pandas as pd, numpy as np

r = pd.read_csv("trabalho/ref_itens.csv")
con = q.conectar()
tot = lambda v: float((v * r.q).sum())
out = []

# ---------------- referências de valor ----------------
R0 = float(r.v_org.sum())
R1 = tot(r.p_org_limitado_teto)
E1 = {k: tot(r[c]) for k, c in [("central", "p_ref"), ("baixo", "p_low"), ("alto", "p_high")]}

# ---------------- E2: desconto sobre CMED ----------------
e2_ok = r.e2_med.notna() & ~r.flag_teto_suspeito.fillna(False)
# central: gestão ativa (categoria mais barata disponível); baixo: registro de menor preço; alto: mediana de todos os registros
# (fornecedor escolhe livremente); e2_max (registro de maior preço) só como extremo
E2C = [("central", "e2_pref", "p_ref"), ("baixo", "e2_min", "p_low"), ("alto", "e2_med", "p_high")]
E2 = {k: tot(np.where(e2_ok, r[c], r[d])) for k, c, d in E2C}
e2_itens, e2_valor_e1 = int(e2_ok.sum()), tot(np.where(e2_ok, r.p_ref, 0))
e2_parte = {k: tot(np.where(e2_ok, r[c], 0)) for k, c, _ in E2C}
E2_EXTREMO = tot(np.where(e2_ok, r.e2_max, r.p_high))
# multiplicador sobre o preço E2 que empataria com E1 nos itens cobertos pelo desconto
m_empate = e2_valor_e1 / e2_parte["central"]
# desconto adicional uniforme (p.p. sobre o PF) equivalente: e2 = pf*(1-d) -> aproximação via multiplicador
# por tipo de produto: comparação E2 x E1 item a item
r["e2_sobre_e1"] = np.where(e2_ok, r.e2_pref / r.p_ref, np.nan)

# ---------------- E3: carona (atas SRP no PNCP) ----------------
atas = con.execute("""SELECT v.item, v.preco_unitario_homologado p_ata, v.quantidade_homologada q_ata, v.data_resultado, c.esfera, c.uf, c.srp
  FROM v_pncp_comparavel v JOIN pncp_contratacoes c USING (numero_controle_pncp)
  WHERE v.preco_unitario_homologado IS NOT NULL AND c.srp AND v.data_resultado >= '2024-01-29'""").df()
atas = atas.merge(r[["item", "q", "teto_max"]], on="item")
atas = atas[(0.5 * atas.q_ata >= atas.q) & (atas.teto_max.isna() | (atas.p_ata <= atas.teto_max))]  # limite de 50% por aderente (art. 86 §4)
melhor = atas.sort_values("p_ata").drop_duplicates("item").set_index("item")
r["p_ata"] = r.item.map(melhor.p_ata)
e3_ok = r.p_ata.notna()
E3 = {k: tot(np.where(e3_ok, np.minimum(r.p_ata, r[c]) if k == "baixo" else r.p_ata, r[c])) for k, c in
      [("central", "p_ref"), ("baixo", "p_low"), ("alto", "p_high")]}

# ---------------- E4: contrato de quantidade fixa ----------------
E4 = dict(E1)

res = pd.DataFrame([
    {"estrategia": "R0 estimativa do órgão (referência, não estratégia)", **{k: R0 for k in ("central", "baixo", "alto")}},
    {"estrategia": "R1 estimativa do órgão limitada ao teto CMED (referência)", **{k: R1 for k in ("central", "baixo", "alto")}},
    {"estrategia": "E1 SRP por item, menor preço, referência saneada", **E1},
    {"estrategia": "E2 SRP maior desconto sobre CMED (itens sem teto via E1)", **E2},
    {"estrategia": "E3 adesão a atas (carona) + E1 no restante", **E3},
    {"estrategia": "E4 contrato quantidade fixa (preço E1; demanda comprometida)", **E4},
])

# ---------------- demanda: SRP paga d*C; contrato fixo paga max(d,1)*C (d<=1,25 via art. 125) ----------------
dem = []
for d in (0.75, 1.0, 1.25):
    for nome, C in (("E1", E1), ("E2", E2), ("E3", E3), ("E4", E4)):
        f = max(d, 1.0) if nome == "E4" else d
        dem.append({"demanda_vs_ETP": d, "estrategia": nome, "gasto_central": f * C["central"], "gasto_baixo": f * C["baixo"], "gasto_alto": f * C["alto"]})
dem = pd.DataFrame(dem)

# ---------------- sensibilidades de E1 e da comparação E1 x E2 ----------------
sens = []
def add(nome, e1, e2=None, obs=""):
    sens.append({"cenario": nome, "E1_central": e1, "E2_central": e2 if e2 is not None else np.nan,
                 "E2_menos_E1": (e2 - e1) if e2 is not None else np.nan, "obs": obs})
add("base", E1["central"], E2["central"])
# a conferir compatível: usa mediana a conferir (≤ teto) nos 25 itens a conferir
pc = np.where(r.flag_a_conferir & r.p_se_conferir_compativel.notna(), r.p_se_conferir_compativel, r.p_ref)
add("a conferir = compatível", tot(pc), tot(np.where(e2_ok, r.e2_pref, pc)), "usa mediana dos registros a conferir (limitada ao teto) nos itens a conferir que os têm")
# a conferir incompatível: base (já não usa a conferir) -> idêntico ao base
add("a conferir = incompatível", E1["central"], E2["central"], "idêntico ao base: o central nunca usa preço a conferir")
# mediana só de compradores municipais
pm = np.where(r.prat_med_municipal.notna() & r.fonte_ref.str.startswith("praticado"),
              np.minimum(r.prat_med_municipal, r.teto_max.fillna(np.inf)), r.p_ref)
add("mediana só municipal", tot(pm), tot(np.where(e2_ok, r.e2_pref, pm)))
# insulinas em caneta sem fornecimento até o teto: comprar frasco 10 mL equivalente (300 UI/caneta -> 0,3 frasco)
pi = r.p_ref.copy()
for it_caneta, it_frasco in ((196, 197), (199, 198)):
    pf = float(r.loc[r.item == it_frasco, "p_ref"].iloc[0])
    pi[r.item == it_caneta] = 0.3 * pf
add("canetas 196/199 substituídas por frasco (custo por UI)", tot(pi), None, "só medicamento; sem seringas/agulhas; decisão clínica, não de compra")
# sem saneamento: referência = estimativa do órgão limitada ao teto
add("referência = estimativa do órgão limitada ao teto (R1)", R1, None, "pior caso de E1 se o pregão aceitasse lances até a referência inflada")
# E2 com preço = teto (fornecedor entrega o produto de maior PF e o desconto vale sobre PF)
add("E2 fornecedor escolhe livremente (mediana dos registros)", E1["central"], E2["alto"])
add("E2 extremo: fornecedor entrega o registro de maior preço", E1["central"], E2_EXTREMO)
add("E2 fornecedor escolhe o registro de menor preço", E1["central"], E2["baixo"])
sens = pd.DataFrame(sens)

# ---------------- E2 x E1 por tipo de produto e item ----------------
cmp_tipo = (r[e2_ok].assign(v_e1=lambda x: x.q * x.p_ref, v_e2=lambda x: x.q * x.e2_pref)
            .groupby(r.tipos_produto.fillna("-").str.contains("Genérico").map({True: "tem registro Genérico", False: "sem Genérico"}))
            [["v_e1", "v_e2"]].sum())
cmp_tipo["n"] = r[e2_ok].groupby(r.tipos_produto.fillna("-").str.contains("Genérico").map({True: "tem registro Genérico", False: "sem Genérico"})).size()

res.to_csv("trabalho/custos_estrategias.csv", index=False, encoding="utf-8")
sens.to_csv("trabalho/sensibilidades.csv", index=False, encoding="utf-8")
dem.to_csv("trabalho/demanda.csv", index=False, encoding="utf-8")
r[["item", "e2_sobre_e1", "p_ata"]].to_csv("trabalho/e2_e3_por_item.csv", index=False, encoding="utf-8")

# auto-verificação
assert E1["baixo"] <= E1["central"] <= E1["alto"] and E2["baixo"] <= E2["central"] <= E2["alto"]
assert R1 <= R0 and E3["central"] <= E1["central"] + 1e-6

with open("trabalho/20_estrategias.txt", "w", encoding="utf-8") as f:
    w = lambda *a: print(*a, file=f)
    pd.set_option("display.width", 250); pd.set_option("display.float_format", "{:,.2f}".format)
    w(res.to_string(index=False)); w()
    w(f"E2: itens cobertos pelo desconto={e2_itens} | valor desses itens em E1={e2_valor_e1:,.2f} | em E2 central={e2_parte['central']:,.2f} "
      f"baixo={e2_parte['baixo']:,.2f} alto={e2_parte['alto']:,.2f} | multiplicador de empate sobre preços E2={m_empate:.4f}")
    w("E2/E1 por item (itens cobertos): ", r.e2_sobre_e1.describe(percentiles=[.1, .25, .5, .75, .9]).round(3).to_dict())
    w("itens em que E2 central < E1 central:", int((r.e2_sobre_e1 < 1).sum()), "valor E1 desses itens:", round(tot(np.where(r.e2_sobre_e1 < 1, r.p_ref, 0)), 2),
      "valor E2:", round(tot(np.where(r.e2_sobre_e1 < 1, r.e2_pref, 0)), 2))
    w(f"E2 extremo (registro de maior preço) = {E2_EXTREMO:,.2f}")
    # combinado E1 com o menor de (E1, E2) item a item: limite inferior teórico de um híbrido
    w(f"híbrido teórico min(E1,E2 central) item a item = {tot(np.where(e2_ok, np.minimum(r.p_ref, r.e2_pref), r.p_ref)):,.2f}")
    sv = (r.q * (r.p_ref - r.p_ata)).where(e3_ok)
    w(f"E3 economia vs E1 concentrada: top10 itens = {sv.nlargest(10).sum():,.2f} de {sv.sum():,.2f}; itens:", r.loc[sv.nlargest(10).index, 'item'].tolist())
    w(cmp_tipo.to_string()); w()
    w(f"E3: itens com ata SRP (PNCP, resultado >= 29/01/2024, 50% da qtd. registrada >= necessidade, <= teto) = {int(e3_ok.sum())}; "
      f"valor E1 desses itens = {tot(np.where(e3_ok, r.p_ref, 0)):,.2f}; valor pela ata = {tot(np.where(e3_ok, r.p_ata, 0)):,.2f}; "
      f"participação no valor E1 = {tot(np.where(e3_ok, r.p_ref, 0)) / E1['central']:.2%}")
    w(melhor.reset_index().to_string()); w()
    w(sens.to_string(index=False)); w()
    w(dem.pivot(index="estrategia", columns="demanda_vs_ETP", values="gasto_central").to_string()); w()
    ins = r[r.item.between(194, 199)].assign(v_e1=lambda x: x.q * x.p_ref, v_e1_lo=lambda x: x.q * x.p_low, v_e1_hi=lambda x: x.q * x.p_high,
                                              v_e2=lambda x: x.q * x.e2_pref, v_r1=lambda x: x.q * x.p_org_limitado_teto)
    ins["pct_R0"] = ins.v_org / R0; ins["pct_E1"] = ins.v_e1 / E1["central"]
    w(ins[["item", "q", "p_org", "v_org", "pct_R0", "teto_min", "teto_max", "p_ref", "p_low", "p_high", "v_e1", "v_e1_lo", "v_e1_hi", "pct_E1", "v_e2", "v_r1"]].to_string(index=False))
    w(f"insulinas: v_org={ins.v_org.sum():,.2f} ({ins.v_org.sum()/R0:.2%}) | E1 central={ins.v_e1.sum():,.2f} ({ins.v_e1.sum()/E1['central']:.2%})")
print(open("trabalho/20_estrategias.txt", encoding="utf-8").read())
