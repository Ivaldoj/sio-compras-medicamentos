"""Números derivados citados nos entregáveis (economia, empates, insulinas, execução 2024). Saída: trabalho/40_numeros_texto.txt"""
import sys; sys.path.insert(0, "scripts"); import consulta_agente as q
import pandas as pd, numpy as np

con = q.conectar()
r = pd.read_csv("trabalho/ref_itens.csv")
c = pd.read_csv("trabalho/custos_estrategias.csv").set_index("estrategia")
g = lambda pref, col: float(c.loc[[i for i in c.index if i.startswith(pref)][0], col])
R0, R1 = g("R0", "central"), g("R1", "central")
E1 = {k: g("E1", k) for k in ("baixo", "central", "alto")}
E2 = {k: g("E2", k) for k in ("baixo", "central", "alto")}
E3 = {k: g("E3", k) for k in ("baixo", "central", "alto")}
L = []
p = lambda s: L.append(s)

ex = con.execute("SELECT sum(valor_empenhado) FROM execucao_2024_licitacao").fetchone()[0]
pe12 = con.execute("SELECT valor_empenhado FROM execucao_2024_licitacao WHERE licitacao LIKE '000122024%'").fetchone()[0]
af = con.execute("SELECT sum(valor) FROM receitas_sus_2024 WHERE descricao_receita LIKE '%Farmac%'").fetchone()[0]
p(f"execução 2024 = {ex:,.2f}; PE 12/2024 = {pe12:,.2f} ({pe12/ex:.1%}); repasse AF 2024 = {af:,.2f} ({af/ex:.1%} da execução)")
p(f"R0/execução 2024 = {R0/ex:.3f}; E1 central/execução 2024 = {E1['central']/ex:.3f}; E1 faixa/execução = {E1['baixo']/ex:.3f}–{E1['alto']/ex:.3f}")
p(f"R0−R1 (excesso acima do teto; não é economia) = {R0-R1:,.2f}")
p(f"Economia potencial E1 vs R1: central {R1-E1['central']:,.2f}; faixa {R1-E1['alto']:,.2f} a {R1-E1['baixo']:,.2f}; % de R1: {(R1-E1['central'])/R1:.1%}")
mat = {(a, b): E2[a] - E1[b] for a in E2 for b in E1}
p("Economia potencial E1 vs E2 (E2[cenário] − E1[cenário]):")
for (a, b), v in mat.items():
    p(f"   E2 {a:7s} − E1 {b:7s} = {v:,.2f}")
p(f"   central {E2['central']-E1['central']:,.2f} ({(E2['central']-E1['central'])/E2['central']:.1%} de E2); mesmos cenários: {E2['baixo']-E1['baixo']:,.2f} a {E2['alto']-E1['alto']:,.2f}; "
  f"extremos: {E2['baixo']-E1['alto']:,.2f} a {E2['alto']-E1['baixo']:,.2f}")
p(f"E3 vs E1 (central) = {E1['central']-E3['central']:,.2f}")
# empate de E2: multiplicador sobre preços E2 nos itens cobertos (de 20_estrategias.txt) -> desconto equivalente por categoria
txt = open("trabalho/20_estrategias.txt", encoding="utf-8").read()
m = float(txt.split("multiplicador de empate sobre preços E2=")[1].split()[0])
for nome, d in (("Genérico", .6011), ("Similar", .5101), ("éticos", .1801)):
    p(f"desconto de empate aproximado {nome}: {1 - m*(1-d):.1%} (hoje {d:.2%})")
p(f"E1 +5% (correção monetária não aplicada) = +{0.05*E1['central']:,.2f}")
# insulinas
ins = r[r.item.between(194, 199)].copy()
ins["v_e1"] = ins.q * ins.p_ref
p(f"insulinas: R0 {ins.v_org.sum():,.2f} ({ins.v_org.sum()/R0:.2%}); E1 {ins.v_e1.sum():,.2f} ({ins.v_e1.sum()/E1['central']:.2%}); faixa {(ins.q*ins.p_low).sum():,.2f}–{(ins.q*ins.p_high).sum():,.2f}")
for _, x in ins.iterrows():
    p(f"   item {x['item']}: R0 {x.v_org:,.2f} ({x.v_org/R0:.2%}) | E1 {x.v_e1:,.2f} ({x.v_e1/E1['central']:.2%}) | p_org/teto_max = {x.p_org/x.teto_max if x.teto_max==x.teto_max else float('nan'):.2f}")
# item 197: teto sem o vínculo HUMULIN 70N/30R (pré-mistura, não NPH)
t197 = con.execute("""SELECT t.registro, t.produto, t.tipo_preco, t.aliquota_icms, t.valor_por_unidade_item FROM v_cmed_teto_unitario t
   WHERE item=197 AND aliquota_aplicavel_pb AND aplicabilidade IN ('teto para compras administrativas','teto obrigatório (produto com CAP)') ORDER BY 5""").df()
p("item 197 tetos: " + "; ".join(f"{a.produto} {a.tipo_preco} {a.aliquota_icms} {a.valor_por_unidade_item:.2f}" for a in t197.itertuples()))
sem = t197[~t197.produto.str.contains("70N/30R")].valor_por_unidade_item.max()
p(f"item 197: teto máx. sem HUMULIN 70N/30R = {sem:.2f}; estimativa do órgão 55.49 {'>' if 55.49 > sem else '<='} esse teto")
# acima do teto: participação das insulinas no excesso
a = r[r.flag_acima_teto_pacote | r.flag_acima_teto_confirmado]
exc = (a.v_org - a.q * a.p_org_limitado_teto)
p(f"acima do teto: excesso {exc.sum():,.2f}; das canetas 196+199 = {exc[a.item.isin([196,199])].sum():,.2f} ({exc[a.item.isin([196,199])].sum()/exc.sum():.1%})")
p(f"sem teto utilizável: {int(r.flag_sem_teto_utilizavel.sum())} itens; R0 {r.loc[r.flag_sem_teto_utilizavel,'v_org'].sum():,.2f} ({r.loc[r.flag_sem_teto_utilizavel,'v_org'].sum()/R0:.1%})")
# demanda e orçamento
p(f"E1 alto / R0 = {E1['alto']/R0:.1%}; E1 alto × 1,25 = {E1['alto']*1.25:,.2f}")
# sobre-estimação: validação com o próprio PE 01/2024
own = con.execute("""SELECT i.item, i.preco_unitario_estimado_orgao p_org, h.preco_unitario_homologado p_h FROM itens i JOIN historico_proprio h
  ON list_contains(string_split(i.pregoes_proprios_2024_itens,'|'), h.pregao || '#' || h.numero_item) WHERE h.preco_unitario_homologado IS NOT NULL""").df()
p("estimativa 2025 / homologado próprio 2024: " + "; ".join(f"item {x.item}: {x.p_org/x.p_h:.2f}" for x in own.itertuples()))
cf = r[r.flag_a_conferir & r.conf_med.notna() & ~r.item.isin([196, 199])]
p(f"a conferir (exceto canetas): mediana de p_org/conf_med = {float((cf.p_org/cf.conf_med).median()):.2f} (n={len(cf)})")
open("trabalho/40_numeros_texto.txt", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
