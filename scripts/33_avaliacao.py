"""Pré-Etapa 5 — preparação da avaliação independente da decisão da Etapa 4, segundo etapa5/PROTOCOLO_AVALIACAO.md.
Lê os arquivos congelados do agente (sem alterá-los), o pacote v1/v2 e os dados reservados (data/evaluation_only/).
Não atribui nota: produz as evidências para a Etapa 5.

Uso: python -I -X utf8 scripts/33_avaliacao.py <raiz_projeto>   (depois de 31 e 32)
Saídas em etapa5/avaliacao/: verificacao_calculos.csv, comparacao_itens.csv, comparacao_resumo.csv, execucao.csv,
  sensibilidade.csv, economia_niveis.csv, viabilidade.csv, resumo.json
"""
import json, os, re, sys
import numpy as np, pandas as pd

ROOT = os.path.abspath(sys.argv[1])
CONG = os.path.join(ROOT, "etapa4", "ambiente_decisor")
EV = os.path.join(ROOT, "data", "evaluation_only")
V1, V2 = os.path.join(CONG, "data", "decision_input"), os.path.join(ROOT, "data", "decision_input_v2")
OUT = os.path.join(ROOT, "etapa5", "avaliacao")
os.makedirs(OUT, exist_ok=True)
CNPJ_SL = "09090689000167"
PE04 = "09090689000167-1-000006/2025"
rs = lambda v: f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

P = pd.read_csv(os.path.join(CONG, "saida", "plano_por_item.csv"))
R = pd.read_csv(os.path.join(CONG, "trabalho", "ref_itens.csv"))
R = R.merge(pd.read_csv(os.path.join(CONG, "trabalho", "e2_e3_por_item.csv"))[["item", "p_ata"]], on="item")
CMP = pd.read_csv(os.path.join(CONG, "saida", "03_comparacao.csv")).set_index("id")
H = pd.read_parquet(os.path.join(EV, "organizacional", "resultado_homologado_PE04_2025.parquet"))
X = pd.read_parquet(os.path.join(EV, "organizacional", "execucao_contratos.parquet"))
FL = pd.read_parquet(os.path.join(EV, "organizacional", "farmaco_por_licitacao_2025_2026.parquet"))
FA = pd.read_parquet(os.path.join(EV, "organizacional", "farmaco_anual_2025_2026.parquet"))
P25 = pd.read_parquet(os.path.join(EV, "organizacional", "pregao_25_2025_itens_resultados.parquet"))
EVO = pd.read_parquet(os.path.join(EV, "organizacional", "evolucao_itens.parquet"))
RC1 = pd.read_csv(os.path.join(V1, "padronizacao", "regras_conversao.csv"), dtype={"registro": str})
AP1 = pd.read_parquet(os.path.join(V1, "nacional", "cmed_2025_01_apresentacoes.parquet"))
assert (P.item.values == R.item.values).all() and len(P) == 334

# =============== B. verificação dos cálculos ===============
q, pref, plo, phi = P.quantidade_etp, P.preco_ref_unitario, P.faixa_preco_baixo, P.faixa_preco_alto
E1 = {k: float(P[c].sum()) for k, c in (("central", "valor_ref_total"), ("baixo", "valor_faixa_baixo"), ("alto", "valor_faixa_alto"))}
arred = float(E1["central"] - (q * pref).sum())  # preços unitários do plano arredondados a 4 casas
dec = {k: CMP.loc[k, ["custo_central", "custo_baixo", "custo_alto"]].astype(float).tolist() for k in ("R1", "E1", "E2", "E3")}
R1 = dec["R1"][0]
B = []
def chk(id_, desc, declarado, recalculado, ok, obs=""):
    B.append(dict(id=id_, verificacao=desc, declarado_pelo_agente=declarado, recalculado=recalculado, confere=bool(ok), observacao=obs))
chk("B1", "E1 central = Σ valor de referência do plano por item", rs(dec["E1"][0]), rs(E1["central"]), abs(E1["central"] - dec["E1"][0]) < 1,
    f"Σ quantidade × preço unitário do plano difere em {rs(arred)} (preços unitários arredondados a 4 casas no CSV)")
chk("B1", "E1 faixa (baixo–alto)", f"{rs(dec['E1'][1])} – {rs(dec['E1'][2])}", f"{rs(E1['baixo'])} – {rs(E1['alto'])}",
    abs(E1["baixo"] - dec["E1"][1]) < 1 and abs(E1["alto"] - dec["E1"][2]) < 1)
e2c, e2b, e2a = dec["E2"]
for desc, decl, val in (("economia potencial central E2 − E1", 2.22e6, e2c - E1["central"]),
                        ("faixa plausível: E2 baixo − E1 baixo", 0.80e6, e2b - E1["baixo"]), ("faixa plausível: E2 alto − E1 alto", 2.03e6, e2a - E1["alto"]),
                        ("extremo cruzado: E2 baixo − E1 alto", -0.21e6, e2b - E1["alto"]), ("extremo cruzado: E2 alto − E1 baixo", 3.04e6, e2a - E1["baixo"]),
                        ("economia vs R1 (estimativa limitada ao teto): R1 − E1", 1.74e6, R1 - E1["central"]),
                        ("faixa vs R1: R1 − E1 alto", 1.05e6, R1 - E1["alto"]), ("faixa vs R1: R1 − E1 baixo", 2.06e6, R1 - E1["baixo"])):
    chk("B2", desc, rs(decl), rs(val), abs(val - decl) < 0.006e6)
tm = P.teto_cmed_unitario_aplicavel_max
acima = (pref > tm * (1 + 1e-6)) & tm.notna()
chk("B3", "referência central ≤ teto máximo aplicável (itens com teto)", "sempre", f"{int(acima.sum())} itens acima", acima.sum() == 0,
    "; ".join(f"item {i}: {a:.4f} > {b:.4f}" for i, a, b in zip(P.item[acima], pref[acima], tm[acima])))
conf = P.fonte_preco_ref.fillna("").str.contains("conferir", case=False)
chk("B4", "nenhum preço 'a conferir' como referência central", "0", str(int(conf.sum())), conf.sum() == 0)
tetos = RC1.groupby("item").teto_unitario_pb.apply(lambda s: set(np.round(s.dropna(), 3)))
fora = [i for i, t in zip(P.item, tm) if pd.notna(t) and not any(abs(t - x) < 1e-3 for x in tetos.get(i, set()))]
chk("B5", "teto máximo usado é teto de vínculo aceito (exata/compatível) na alíquota da PB", "sempre", f"{len(fora)} itens fora", not fora, str(fora[:20]))
cats = P.categoria_valor.value_counts()
chk("B6", "uma categoria de valor por referência", "sim", f"{cats.size} categorias; nulos {int(P.categoria_valor.isna().sum())}",
    P.categoria_valor.notna().all() and not P.categoria_valor.str.contains(r"\|").any(), "; ".join(f"{k}: {v}" for k, v in cats.items()))
exc = ((P.preco_estimado_orgao - tm) * q).where(P.flag_acima_teto_confirmado)
for desc, decl, val in (("itens com estimativa acima do teto (confirmados)", 41, int(P.flag_acima_teto_confirmado.sum())),
                        ("itens sem referência externa", 63, int(P.flag_sem_referencia_externa.sum())),
                        ("itens a conferir", 25, int(P.flag_a_conferir.sum()))):
    chk("B7", desc, str(decl), str(val), decl == val)
chk("B7", "excesso das estimativas sobre o teto", rs(1.396e6), rs(float(exc.sum())), abs(exc.sum() - 1.396e6) < 0.006e6)
sh = float(exc[P.item.isin([196, 199])].sum() / exc.sum())
chk("B7", "parte do excesso nas canetas 196 e 199", "85,6%", f"{sh:.1%}", abs(sh - 0.856) < 0.001)
me = P.tratamento_estrategia_recomendada.str.contains("exclusivo ME/EPP", na=False)
chk("B8", "exclusivos ME/EPP pelo critério declarado (valor de referência do agente ≤ R$ 80.000)", "332 itens",
    f"{int(me.sum())} marcados; {int((me & (P.valor_ref_total > 80000)).sum())} acima de R$ 80 mil", int(me.sum()) == 332 and (me & (P.valor_ref_total > 80000)).sum() == 0,
    "pela estimativa ORIGINAL do órgão o resultado muda: marcados com estimativa > R$ 80 mil = " + str(P.item[me & (P.valor_estimado_orgao > 80000)].tolist())
    + "; não marcados com estimativa ≤ R$ 80 mil = " + str(P.item[~me & (P.valor_estimado_orgao <= 80000)].tolist())
    + ". O critério do agente só vale se a referência saneada virar o valor estimado do edital (o que ele recomenda)")
BV = pd.DataFrame(B)
BV.to_csv(os.path.join(OUT, "verificacao_calculos.csv"), index=False, encoding="utf-8")

# =============== C. comparação com os dados reservados ===============
M = P.merge(H[["item", "quantidade_homologada", "preco_unitario_homologado", "cnpj_fornecedor", "data_resultado"]], on="item", how="left")
assert M.preco_unitario_homologado.notna().all()
M["qtd_igual_etp"] = M.quantidade_homologada == M.quantidade_etp
M["v_hom"] = M.quantidade_homologada * M.preco_unitario_homologado
M["razao_hom_ref"] = M.preco_unitario_homologado / M.preco_ref_unitario
M["na_faixa"] = M.preco_unitario_homologado.between(M.faixa_preco_baixo, M.faixa_preco_alto)
M["acima_faixa"] = M.preco_unitario_homologado > M.faixa_preco_alto
M["abaixo_faixa"] = M.preco_unitario_homologado < M.faixa_preco_baixo
M["hom_acima_teto"] = M.preco_unitario_homologado > M.teto_cmed_unitario_aplicavel_max * (1 + 1e-6)
M["fonte_ref"] = M.fonte_preco_ref.fillna("").str.split("(").str[0].str.strip().str.replace(r"\s+", " ", regex=True)

# C3: mercado nacional em 2025 (registros compatíveis; exclui o próprio município)
g2 = pd.read_parquet(os.path.join(V2, "padronizacao", "item_bps_grupos.parquet"))
g2 = g2[g2.compatibilidade == "compativel"][["item", "catmat", "unidade_fornecimento", "capacidade_descricao"]]
bp = pd.read_parquet(os.path.join(EV, "nacional", "bps_pos_corte.parquet"),
                     columns=["catmat", "unidade_fornecimento", "capacidade_descricao", "comprador_cnpj", "data_compra", "preco_unitario_praticado", "flag_preco_extremo"])
bp = bp[(pd.to_datetime(bp.data_compra).dt.year == 2025) & ~bp.flag_preco_extremo.fillna(False) & (bp.comprador_cnpj.astype(str) != CNPJ_SL)]
mb = g2.merge(bp, on=["catmat", "unidade_fornecimento", "capacidade_descricao"])[["item", "preco_unitario_praticado"]]
icg2 = pd.read_parquet(os.path.join(V2, "padronizacao", "item_comprasgov_registros.parquet"))
cg1 = pd.read_parquet(os.path.join(V2, "nacional", "comprasgov_precos_praticados.parquet"), columns=["id_origem", "catmat", "unidade_fornecimento", "capacidade_valor", "capacidade_unidade"])
kc = ["catmat", "unidade_fornecimento", "capacidade_valor", "capacidade_unidade"]
chaves = icg2[icg2.compatibilidade == "compativel"].merge(cg1, on=["id_origem"], suffixes=("_x", ""))[["item"] + kc].drop_duplicates()
cp = pd.read_parquet(os.path.join(EV, "nacional", "comprasgov_pos_corte.parquet"), columns=kc + ["data_resultado", "preco_unitario_praticado"])
cp = cp[pd.to_datetime(cp.data_resultado, errors="coerce").dt.year == 2025]
mc = chaves.merge(cp, on=kc)[["item", "preco_unitario_praticado"]]
m25 = pd.concat([mb, mc]).groupby("item").preco_unitario_praticado.agg(mercado_2025_mediana="median", mercado_2025_n="size")
M = M.merge(m25, on="item", how="left")
M["razao_mercado25_ref"] = M.mercado_2025_mediana / M.preco_ref_unitario
M["razao_hom_mercado25"] = M.preco_unitario_homologado / M.mercado_2025_mediana

col = ["item", "descricao", "quantidade_etp", "preco_estimado_orgao", "preco_ref_unitario", "faixa_preco_baixo", "faixa_preco_alto", "fonte_ref",
       "teto_cmed_unitario_aplicavel_max", "preco_unitario_homologado", "quantidade_homologada", "qtd_igual_etp", "razao_hom_ref", "na_faixa",
       "acima_faixa", "abaixo_faixa", "hom_acima_teto", "mercado_2025_mediana", "mercado_2025_n", "razao_mercado25_ref", "razao_hom_mercado25",
       "flag_a_conferir", "flag_sem_referencia_externa", "flag_acima_teto_confirmado", "flag_referencia_fraca", "cnpj_fornecedor"]
M[col].to_csv(os.path.join(OUT, "comparacao_itens.csv"), index=False, encoding="utf-8")

def resumo(df, grupo):
    v_ref, v_h = float((df.quantidade_etp * df.preco_ref_unitario).sum()), float(df.v_hom.sum())
    return dict(grupo=grupo, itens=len(df), valor_E1_agente=v_ref, valor_homologado=v_h, razao_ponderada=v_h / v_ref if v_ref else np.nan,
                razao_mediana=float(df.razao_hom_ref.median()), pct_na_faixa=float(df.na_faixa.mean()), pct_acima_faixa=float(df.acima_faixa.mean()),
                pct_abaixo_faixa=float(df.abaixo_faixa.mean()), valor_hom_itens_acima_faixa=float(df.v_hom[df.acima_faixa].sum()),
                itens_hom_acima_teto=int(df.hom_acima_teto.sum()), itens_com_mercado_2025=int(df.mercado_2025_mediana.notna().sum()),
                razao_mediana_mercado25_ref=float(df.razao_mercado25_ref.median()), razao_mediana_hom_mercado25=float(df.razao_hom_mercado25.median()))
grupos = [("todos", M), ("insulinas 194–199", M[M.item.between(194, 199)]), ("canetas 196 e 199", M[M.item.isin([196, 199])]),
          ("sem insulinas", M[~M.item.between(194, 199)]), ("a conferir", M[M.flag_a_conferir]), ("sem referência externa", M[M.flag_sem_referencia_externa]),
          ("estimativa acima do teto", M[M.flag_acima_teto_confirmado]), ("referência fraca", M[M.flag_referencia_fraca])]
grupos += [(f"fonte: {f}", d) for f, d in M.groupby("fonte_ref")]
CR = pd.DataFrame([resumo(d, n) for n, d in grupos])
CR.to_csv(os.path.join(OUT, "comparacao_resumo.csv"), index=False, encoding="utf-8")
H_tot = float(M.v_hom.sum())

# C6: execução e gasto
x4 = X[X.compra == PE04].copy()
x4["empenhado"] = x4.empenhado_2025 + x4.empenhado_2026
hc = M.groupby(M.cnpj_fornecedor.astype(str)).agg(v_hom=("v_hom", "sum"), v_org=("valor_estimado_orgao", "sum"),
                                                     v_e1=("valor_ref_total", "sum"), itens=("item", "size"))
v_r1_item = (q * np.minimum(P.preco_estimado_orgao, P.teto_cmed_unitario_aplicavel_max.fillna(np.inf)))
hc = hc.join(pd.Series(v_r1_item.values, index=M.cnpj_fornecedor.astype(str)).groupby(level=0).sum().rename("v_r1"))
x4 = x4.merge(hc, left_on=x4.forn.astype(str), right_index=True, how="left").drop(columns="key_0", errors="ignore")
x4["valor_contrato_confere_homologado"] = (x4.valor - x4.v_hom).abs() < 1
fl = FL.assign(pe=FL.licitacao.str.split("|").str[0].str.strip()).pivot_table(index="pe", columns="ano", values="valor_empenhado", aggfunc="sum").fillna(0)
EXE = x4[["contrato", "forn", "itens", "valor", "v_hom", "valor_contrato_confere_homologado", "empenhado", "pago_total", "pct_empenhado", "v_org", "v_r1", "v_e1"]]
EXE.to_csv(os.path.join(OUT, "execucao.csv"), index=False, encoding="utf-8")
contratado, empenhado, pago = float(x4.valor.sum()), float(x4.empenhado.sum()), float(x4.pago_total.sum())
d_obs = empenhado / contratado

# =============== E. sensibilidade (fórmulas do agente, trabalho/20_estrategias.py) ===============
def custos(r, p, mask=None, e2=None):
    mask = np.ones(len(r), bool) if mask is None else np.asarray(mask)
    p, qq = np.asarray(p, float), np.asarray(r.q, float) * mask
    e2_ok = (r.e2_med.notna() & ~r.flag_teto_suspeito.fillna(False)).values
    e2p = np.asarray(r.e2_pref if e2 is None else e2, float)
    e1 = float((qq * p).sum())
    return dict(E1=e1, E2=float((qq * np.where(e2_ok, e2p, p)).sum()), E3=float((qq * np.where(r.p_ata.notna(), r.p_ata, p)).sum()), E4=e1)

# fator do teto a 20% para vínculos do Convênio 87/02 (S2)
cfz = set(AP1.loc[AP1.convenio_confaz_87, "registro"].astype(str))
pr = pd.read_parquet(os.path.join(V1, "nacional", "cmed_2025_01_precos.parquet"))
pr = pr[~pr.registro.astype(str).isin(cfz) & pr.aliquota_icms.isin(["0%", "20%"])]
piv = pr.pivot_table(index=["registro", "tipo_preco"], columns="aliquota_icms", values="valor_embalagem", aggfunc="first").dropna()
K20 = float((piv["20%"] / piv["0%"]).median())
rc = RC1.assign(t20=np.where(RC1.registro.isin(cfz) & (RC1.teto_aliquota_pb == "0%"), RC1.teto_unitario_pb * K20, RC1.teto_unitario_pb))
ri = (rc.groupby("item").t20.max() / rc.groupby("item").teto_unitario_pb.max()).reindex(R.item).fillna(1.0).values
nao_cap = np.where(R.prat_med.notna(), R.prat_med, R.p_org)
p_s2 = np.where(R.ref_limitada_teto.fillna(False), np.minimum(nao_cap, R.p_ref * ri), R.p_ref)
sem_ins = ~R.item.between(196, 199).values
p_hom = M.preco_unitario_homologado.values
p_m25 = np.where(M.mercado_2025_mediana.notna(), M.mercado_2025_mediana, R.p_ref)
p_s6 = np.where(R.flag_sem_referencia_externa, R.p_org_limitado_teto, R.p_ref)
R2 = pd.read_csv(os.path.join(ROOT, "etapa5", "reproducao", "v2", "trabalho", "ref_itens.csv"))
R2 = R2.merge(pd.read_csv(os.path.join(ROOT, "etapa5", "reproducao", "v2", "trabalho", "e2_e3_por_item.csv"))[["item", "p_ata"]], on="item")
cen = [("S0 base (modelo do agente)", custos(R, R.p_ref), "reproduz os números do agente"),
       ("S1 pacote v2 (errata)", custos(R2, R2.p_ref), "scripts do agente rodados sobre data/decision_input_v2"),
       ("S2 teto a 20% nos produtos do Convênio 87/02", custos(R, p_s2, e2=R.e2_pref * ri), f"tetos do convênio × {K20:.3f}; E2 escalado pela mesma razão do teto máximo do item (aproximação)"),
       ("S3 sem insulinas humanas 196–199 (fornecimento centralizado do MS)", custos(R, R.p_ref, sem_ins), "limite superior do efeito: supõe que a cota federal cobre toda a necessidade"),
       ("S4 E1 aos preços homologados reais", custos(R, p_hom), "E2 e E3 seguem o modelo do agente (assimetria: só E1 tem preço observado)"),
       ("S5 E1 à mediana nacional de 2025", custos(R, p_m25), f"mediana 2025 disponível para {int(M.mercado_2025_mediana.notna().sum())} itens; demais com a referência do agente"),
       ("S6 itens sem referência externa pela estimativa limitada ao teto", custos(R, p_s6), "em vez da estimativa ÷ 2,04"),
       ("S8 S2 + S3 + S4 combinados", custos(R, p_hom, sem_ins, e2=R.e2_pref * ri), "E1 a preços homologados, sem insulinas humanas, E2 com teto a 20% no convênio")]
S = []
for nome, c, obs in cen:
    viaveis = {k: c[k] for k in ("E1", "E2", "E4")}
    menor = min(viaveis, key=lambda k: (viaveis[k], k != "E1"))
    S.append(dict(cenario=nome, **c, E2_menos_E1=c["E2"] - c["E1"], menor_custo_viavel=menor, altera_decisao=menor != "E1", obs=obs))
c0 = custos(R, R.p_ref)
S.append(dict(cenario=f"S7 demanda = fração empenhada observada no PE 04/2025 ({d_obs:.1%})", E1=d_obs * c0["E1"], E2=d_obs * c0["E2"], E3=d_obs * c0["E3"],
              E4=c0["E4"], E2_menos_E1=d_obs * (c0["E2"] - c0["E1"]), menor_custo_viavel="E1", altera_decisao=False,
              obs=f"SRP paga d×C; regra do agente para E4 = compromisso C. Ex post, os contratos fixos reais foram executados em {d_obs:.1%}, isto é, o compromisso não virou gasto"))
SEN = pd.DataFrame(S)
assert abs(SEN.iloc[0].E1 - dec["E1"][0]) < 1 and abs(SEN.iloc[0].E2 - dec["E2"][0]) < 1
SEN.to_csv(os.path.join(OUT, "sensibilidade.csv"), index=False, encoding="utf-8")

# =============== F. economia em três níveis ===============
R0 = float(P.valor_estimado_orgao.sum())
real_r0 = float((x4.pago_total * (x4.v_org / x4.v_hom - 1)).sum())
real_r1 = float((x4.pago_total * (x4.v_r1 / x4.v_hom - 1)).sum())
ECO = pd.DataFrame([
    dict(nivel="1. projetada (ex ante)", objeto="estratégia do agente (E1)", referencia="E2 (desconto sobre CMED, modelo do agente)", valor=e2c - E1["central"],
         observabilidade="contrafactual: estimativa do agente; nunca observável", fonte="saida/03_comparacao.csv"),
    dict(nivel="1. projetada (ex ante)", objeto="estratégia do agente (E1)", referencia="R1 (estimativa do órgão limitada ao teto)", valor=R1 - E1["central"],
         observabilidade="contrafactual", fonte="saida/03_comparacao.csv"),
    dict(nivel="2. contratada (ex post)", objeto="decisão real (PE 04/2025)", referencia="R0 (estimativa do órgão)", valor=R0 - H_tot,
         observabilidade="observada no certame; NÃO é economia realizada (depende de execução)", fonte="resultado_homologado_PE04_2025"),
    dict(nivel="2. contratada (ex post)", objeto="decisão real (PE 04/2025)", referencia="R1 (estimativa limitada ao teto)", valor=R1 - H_tot,
         observabilidade="observada no certame; parte da diferença R0−homologado vem de estimativas acima do teto legal", fonte="idem + teto CMED"),
    dict(nivel="3. realizada (ex post)", objeto="decisão real (PE 04/2025)", referencia="R0, sobre o valor pago", valor=real_r0,
         observabilidade=f"ESTIMATIVA sob hipótese de mix proporcional por contrato (pago {rs(pago)}; execução por item indisponível)", fonte="execucao_contratos"),
    dict(nivel="3. realizada (ex post)", objeto="decisão real (PE 04/2025)", referencia="R1, sobre o valor pago", valor=real_r1,
         observabilidade="ESTIMATIVA sob a mesma hipótese", fonte="execucao_contratos"),
    dict(nivel="3. realizada (ex post)", objeto="estratégia do agente", referencia="qualquer", valor=np.nan,
         observabilidade="não observável: a estratégia não foi executada", fonte="—"),
    dict(nivel="(não é economia)", objeto="projeção do agente × certame real", referencia="homologado − E1 central (mesmas quantidades)", valor=H_tot - E1["central"],
         observabilidade="erro de projeção de preço; não mede economia de nenhuma das decisões", fonte="comparacao_itens.csv"),
])
ECO.to_csv(os.path.join(OUT, "economia_niveis.csv"), index=False, encoding="utf-8")

# =============== D. viabilidade (evidências; sem nota) ===============
CRt = CR.set_index("grupo")
ins = M[M.item.isin([196, 199])].set_index("item")
fl_pe12 = fl.loc["000122024"] if "000122024" in fl.index else pd.Series(dtype=float)
tot_ano = FA.set_index("ano").valor_empenhado
p25_hom = float((P25.valorUnitarioHomologado * P25.quantidadeHomologada).sum())
n_comum_25 = int((EVO["PE 04/2025"].notna() & EVO["PE 25/2025"].notna()).sum())
VI = pd.DataFrame([
    dict(dimensao="jurídica", criterio="SRP por item (E1)", ex_ante="Lei 14.133/2021, arts. 82–86 (citados pelo agente); art. 86 conferido no Planalto",
         ex_post="decisão real usou pregão por item sem ata (7 contratos 'termo inicial', sem ata vinculada); nenhuma evidência contra a viabilidade jurídica do SRP"),
    dict(dimensao="jurídica", criterio="adesão a ata municipal (E3)", ex_ante="agente marcou 'a verificar'. VERIFICADO: art. 86, §3º, II (Lei 14.770/2023, vigente desde 22/12/2023) permite, se a ata vier de licitação; limites de 50% por aderente (§4º) e 2× no total (§5º)",
         ex_post="não usada na decisão real"),
    dict(dimensao="jurídica", criterio="dispensa por valor", ex_ante="agente citou ~R$ 62,7 mil. VERIFICADO: Decreto 12.343/2024, R$ 62.725,59 (art. 75, II), vigente de 01/01/2025 a 31/12/2025",
         ex_post="—"),
    dict(dimensao="jurídica", criterio="exclusividade ME/EPP (LC 123, art. 48, I)", ex_ante=BV[BV.id == "B8"].iloc[0].observacao, ex_post="—"),
    dict(dimensao="regulatória", criterio="teto CMED", ex_ante=f"referências do agente ≤ teto: {BV[BV.id == 'B3'].iloc[0].recalculado}",
         ex_post=f"{int(M.hom_acima_teto.sum())} itens homologados acima do teto de jan/2025 (valor homologado desses itens {rs(float(M.v_hom[M.hom_acima_teto].sum()))})"),
    dict(dimensao="operacional", criterio="sem local de armazenamento", ex_ante="E1 com entregas parceladas sob demanda",
         ex_post="contratos reais também previam 'fornecimento parcelado'; sem dado de ruptura ou de entrega"),
    dict(dimensao="orçamentária", criterio="compromisso × uso", ex_ante=f"E1 central {rs(E1['central'])}; gasto 2024 R$ 1.953.288,72; saldo de dotação desconhecido",
         ex_post=f"PE 04/2025: contratado {rs(contratado)}, empenhado {rs(empenhado)} ({d_obs:.1%}) até 08/2026; gasto total com medicamentos 2025 {rs(float(tot_ano.get(2025, np.nan)))}"),
    dict(dimensao="mercado", criterio="risco de deserto com a referência saneada",
         ex_ante="agente: risco 'médio', concentrado nos itens com referência no teto (canetas)",
         ex_post=f"real: 334/334 itens homologados (estimativa como preço máximo). Em {int(M.acima_faixa.sum())} itens ({CRt.loc['todos','pct_acima_faixa']:.0%}) o homologado ficou acima do limite alto do agente ({rs(CRt.loc['todos','valor_hom_itens_acima_faixa'])} homologados); canetas: 196 a {rs(ins.loc[196,'preco_unitario_homologado'])} (ref. {rs(ins.loc[196,'preco_ref_unitario'])}), 199 a {rs(ins.loc[199,'preco_unitario_homologado'])} (ref. {rs(ins.loc[199,'preco_ref_unitario'])})"),
    dict(dimensao="mercado/assistência", criterio="insulinas humanas NPH e Regular (196–199)",
         ex_ante="agente: confirmar cota MS/SES antes de licitar (conhecimento prévio 'a verificar'). VERIFICADO: aquisição centralizada pelo MS (PRC nº 2/2017, Anexo XXVIII, art. 35; NT 169/2022 e NT 164/2023), frascos e canetas/tubetes, 70% da demanda SUS em canetas",
         ex_post=f"decisão real comprou as canetas: {rs(float(M.v_hom[M.item.isin([196,199])].sum()))} homologados; execução por item desconhecida"),
    dict(dimensao="transição", criterio="contrato de desconto sobre a CMED (PE 12/2024)",
         ex_ante="agente: vigência desconhecida (incerteza declarada)",
         ex_post=f"seguiu em uso: empenhado {rs(float(fl_pe12.get(2025, 0)))} em 2025 e {rs(float(fl_pe12.get(2026, 0)))} em 2026 (jan–ago), mais que o PE 04/2025 ({rs(float(fl.loc['000042025'].get(2025, 0)))} e {rs(float(fl.loc['000042025'].get(2026, 0)))})"),
    dict(dimensao="escopo", criterio="necessidades fora do plano", ex_ante="não previsíveis com o pacote",
         ex_post=f"PE 25/2025: {len(P25)} itens, {n_comum_25} em comum com o PE 04/2025; homologado {rs(p25_hom)}"),
])
VI.to_csv(os.path.join(OUT, "viabilidade.csv"), index=False, encoding="utf-8")

res = dict(H_tot=H_tot, E1=E1, R0=R0, R1=R1, E2=dec["E2"], d_obs=d_obs, contratado=contratado, empenhado=empenhado, pago=pago, K20=K20,
           verificacoes_ok=int(BV.confere.sum()), verificacoes=len(BV), qtd_igual_etp=int(M.qtd_igual_etp.sum()),
           cenarios_que_alteram=SEN[SEN.altera_decisao].cenario.tolist())
json.dump(res, open(os.path.join(OUT, "resumo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 90)
print(BV[["id", "verificacao", "declarado_pelo_agente", "recalculado", "confere"]].to_string(index=False))
print(CR[["grupo", "itens", "valor_E1_agente", "valor_homologado", "razao_ponderada", "razao_mediana", "pct_na_faixa", "pct_acima_faixa", "itens_hom_acima_teto", "itens_com_mercado_2025", "razao_mediana_mercado25_ref", "razao_mediana_hom_mercado25"]].round(3).to_string(index=False))
print(SEN.drop(columns="obs").round(0).to_string(index=False))
print(ECO[["nivel", "objeto", "referencia", "valor"]].round(0).to_string(index=False))
print(EXE.round(1).to_string(index=False)); print(fl.round(0).to_string())
print(json.dumps(res, ensure_ascii=False, default=float))
