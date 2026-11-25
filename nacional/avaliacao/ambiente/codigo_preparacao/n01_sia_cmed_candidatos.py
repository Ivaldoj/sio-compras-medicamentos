"""Experimento nacional — candidatos à cesta CEAF: dispensação nacional (SIA/SUS, TabNet) × teto CMED (jan/2025).

Uso: python -I -X utf8 nacional/scripts/n01_sia_cmed_candidatos.py <raiz_projeto>
Lê data/raw/nacional/datasus_sia/*.html (respostas TabNet, formato prn) e data/processed/cmed_pmvg_20250107.parquet.
Grava nacional/dados/processados/: sia_procedimentos.parquet (quantidades por janela), sia_pre_uf.parquet, sia_pre_mes.parquet,
sia_pos_uf.parquet, cmed_vinculos_sia.parquet, candidatos.parquet (ranking por qtd pré-corte × teto unitário mediano).
"""
import html, os, re, sys
import numpy as np, pandas as pd

ROOT = os.path.abspath(sys.argv[1])
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from padroniza import INJ, concentracoes, conteudo_item, embalagem_cmed, forma, norm, principio  # noqa: E402

SIA = os.path.join(ROOT, "data", "raw", "nacional", "datasus_sia")
OUT = os.path.join(ROOT, "nacional", "dados", "processados")
os.makedirs(OUT, exist_ok=True)


def tabnet(nome):
    """Tabela TabNet (prn) -> DataFrame largo: proc, nome, <colunas>."""
    t = open(os.path.join(SIA, nome + ".html"), encoding="latin-1").read()
    body = html.unescape(re.search(r"(?is)<pre>(.*?)</pre>", t).group(1))
    linhas = [l for l in body.splitlines() if l.strip()]
    cab = [c.strip('"') for c in linhas[0].split(";")]
    rows = []
    for l in linhas[1:]:
        p = l.split(";")
        if not p[0].startswith('"0'):
            continue
        rot = p[0].strip('"')
        vals = [float(x.replace(".", "").replace(",", ".")) if x.strip() not in ("-", "") else 0.0 for x in p[1:]]
        rows.append([rot[:10], rot[11:].strip()] + vals)
    return pd.DataFrame(rows, columns=["proc", "nome"] + cab[1:])


assert tabnet("pre0_qtd_proc").shape[0] > 250
pre = tabnet("sia_grupo06_proc_Qtd_aprovada_proc202311_202410").rename(columns={"Qtd.aprovada": "qtd_pre"})
val = tabnet("sia_grupo06_proc_Valor_aprovado_proc202311_202410").rename(columns={"Valor aprovado": "valor_aprovado_pre"})
pre0 = tabnet("pre0_qtd_proc").rename(columns={"Qtd.aprovada": "qtd_pre_ano_anterior"})
pos = tabnet("pos_qtd_proc_uf"); posv = tabnet("pos_valor_proc").rename(columns={"Valor aprovado": "valor_aprovado_pos"})
P = (pre.merge(val[["proc", "valor_aprovado_pre"]], on="proc", how="left").merge(pre0[["proc", "qtd_pre_ano_anterior"]], on="proc", how="left")
     .fillna({"valor_aprovado_pre": 0.0}))
P = P[P.proc.str.startswith("0604")].copy()  # subgrupo 06.04: medicamentos do Componente Especializado
P["unidade_sia"] = P.nome.str.extract(r"\(\s*(?:POR\s+)?([^)]*)\)\s*$", flags=re.I)[0].str.strip().str.lower().fillna("")
P["valor_unit_financiado_pre"] = np.where(P.qtd_pre > 0, P.valor_aprovado_pre / P.qtd_pre, np.nan)

uf = tabnet("pre_qtd_proc_uf"); ufs = [c for c in uf.columns if c not in ("proc", "nome", "Total")]
PU = uf.melt(id_vars=["proc"], value_vars=ufs, var_name="uf", value_name="qtd").query("qtd > 0")
mes = tabnet("pre_qtd_proc_mes"); meses = [c for c in mes.columns if c not in ("proc", "nome", "Total")]
PM = mes.melt(id_vars=["proc"], value_vars=meses, var_name="mes_processamento", value_name="qtd")
QU = pos.melt(id_vars=["proc"], value_vars=[c for c in pos.columns if c not in ("proc", "nome", "Total")], var_name="uf", value_name="qtd").query("qtd > 0")
P = P.merge(pos[["proc", "Total"]].rename(columns={"Total": "qtd_pos"}), on="proc", how="left").merge(posv[["proc", "valor_aprovado_pos"]], on="proc", how="left")

# ---------------- vínculo SIA × CMED (princípio, concentração, forma; unidade = unidade sólida ou recipiente) ----------------
c = pd.read_parquet(os.path.join(ROOT, "data", "processed", "cmed_pmvg_20250107.parquet"))
c = c[~c["LABORATÓRIO"].fillna("").str.contains("EMPRESA DE TESTE", case=False)]
c["pc"] = c["SUBSTÂNCIA"].map(principio)
sn = lambda s: s.fillna("").str.strip()
cap, cfz, ic0 = sn(c.CAP).eq("Sim"), sn(c["CONFAZ 87"]).eq("Sim"), sn(c["ICMS 0%"]).eq("Sim")
c["teto_gov_0"] = np.where(cap, c["PMVG 0%"], c["PF 0%"])  # teto em compra pública sem ICMS (convênio/isenção)
c["teto_gov_18"] = np.where(cap, c["PMVG 18%"], c["PF 18%"])  # referência com ICMS (alíquota interna mais comum; UF varia)
idx = {}
for i, p in zip(c.index, c.pc):
    for tok in p:
        idx.setdefault(tok, []).append(i)
def principio_sia(nome):
    """União dos princípios de cada parte de uma associação ('FORMOTEROL 12 MCG + BUDESONIDA 400 MCG')."""
    partes = [p for p in re.split(r"\+|/(?=\s*[A-Za-z])", re.sub(r"\([^)]*\)", " ", nome)) if re.search(r"[A-Za-z]{4,}", p)]
    return frozenset().union(*[principio(p) for p in partes]) if partes else frozenset()


def mesma_concentracao(ci, cc, vol, vol_sia=None):
    """Igual; ou massa/UI de um lado = concentração do outro × volume do recipiente; ou a CMED traz a mesma quantidade em duas notações."""
    if ci == cc:
        return True
    if len(ci) == 1 and len(cc) == 1:
        (vi, ui), (vc, uc) = next(iter(ci)), next(iter(cc))
        if vol and vol[1] == "ml" and uc == ui + "/ml" and abs(vc * vol[0] - vi) <= 0.01 * vi:
            return True
        if vol_sia and vol_sia[1] == "ml" and ui == uc + "/ml" and abs(vi * vol_sia[0] - vc) <= 0.01 * vc:
            return True
    return len(cc) == 2 and ci < cc and len({u.split("/")[0] for _, u in cc}) == 2  # "12 UI (4 MG)"


assert principio_sia("FORMOTEROL 12 MCG + BUDESONIDA 400 MCG (POR CAPSULA INALANTE)") >= {"formoterol", "budesonida"}
assert mesma_concentracao(frozenset({(40.0, "mg")}), frozenset({(50.0, "mg/ml")}), (0.8, "ml"))
V = []
for r in P.itertuples():
    pi, ci = principio_sia(r.nome), concentracoes(re.sub(r"\(\s*(?:BIOSSIMILAR|ORIGINADOR)[^)]*\)", " ", r.nome))
    fi, mi = forma(r.nome + " " + (r.unidade_sia or ""))
    cand = set.union(*[set(idx.get(t, [])) for t in pi]) if pi else set()
    for i in cand:
        x = c.loc[i]
        # mesmo princípio; a CMED pode ter um termo de sal a mais ("BISSULFATO DE CLOPIDOGREL")
        if not (x.pc == pi or (pi < x.pc and len(x.pc - pi) == 1 and len(ci) == 1)):
            continue
        ap = str(x["APRESENTAÇÃO"])
        cc = concentracoes(ap.split(" CT ")[0] if " CT " in ap else ap)
        e = embalagem_cmed(ap)
        if not ci or not mesma_concentracao(ci, cc, e["volume"], conteudo_item(r.nome)):
            continue
        fc, mc = forma(ap)
        inj_generico = fi == "injetavel" and fc in INJ  # SIA diz só "INJETÁVEL"; a CMED especifica solução/pó/suspensão
        if fi and fc and (fi != fc or mi != mc) and not ({fi, fc} <= {"comprimido", "capsula"}) and not inj_generico:
            continue
        # unidade dispensada = unidade sólida (comprimido, cápsula, supositório, adesivo: "X n" sem volume) ou recipiente (frasco, seringa)
        un = e["unidades_solidas"] or e["recipientes"]
        if not un or e["composta"] and not e["unidades_solidas"]:
            continue
        V.append(dict(proc=r.proc, registro=x.reg, substancia=x["SUBSTÂNCIA"], laboratorio=x["LABORATÓRIO"], produto=x.PRODUTO, apresentacao=ap,
                      tipo_produto=x["TIPO DE PRODUTO (STATUS DO PRODUTO)"], cap=bool(cap[i]), convenio_87=bool(cfz[i]), icms_isento=bool(ic0[i]),
                      unidades_por_embalagem=un, teto_gov_0_unit=x.teto_gov_0 / un if pd.notna(x.teto_gov_0) else np.nan,
                      teto_gov_18_unit=x.teto_gov_18 / un if pd.notna(x.teto_gov_18) else np.nan,
                      pf_sem_imposto_unit=x["PF Sem Impostos"] / un if pd.notna(x["PF Sem Impostos"]) else np.nan))
V = pd.DataFrame(V)
agg = V.groupby("proc").agg(cmed_apresentacoes=("registro", "size"), cmed_laboratorios=("laboratorio", "nunique"),
                            teto0_unit_min=("teto_gov_0_unit", "min"), teto0_unit_mediana=("teto_gov_0_unit", "median"),
                            teto0_unit_max=("teto_gov_0_unit", "max"), algum_cap=("cap", "any"), algum_convenio_87=("convenio_87", "any"))
P = P.merge(agg, on="proc", how="left")
P["relevancia_teto_pre"] = P.qtd_pre * P.teto0_unit_mediana  # proxy de relevância: quantidade dispensada × teto mediano (não é gasto)
P = P.sort_values("relevancia_teto_pre", ascending=False)
P.to_parquet(os.path.join(OUT, "sia_procedimentos.parquet"), index=False)
PU.to_parquet(os.path.join(OUT, "sia_pre_uf.parquet"), index=False); PM.to_parquet(os.path.join(OUT, "sia_pre_mes.parquet"), index=False)
QU.to_parquet(os.path.join(OUT, "sia_pos_uf.parquet"), index=False); V.to_parquet(os.path.join(OUT, "cmed_vinculos_sia.parquet"), index=False)
assert P.proc.is_unique and (P.qtd_pre >= 0).all()
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 70)
print("procedimentos CEAF (06.04):", len(P), "| com vínculo CMED:", int(P.cmed_apresentacoes.notna().sum()), "| UFs:", PU.uf.nunique(), "| meses:", len(meses))
print(P.head(70)[["proc", "nome", "qtd_pre", "teto0_unit_mediana", "relevancia_teto_pre", "valor_unit_financiado_pre", "cmed_laboratorios"]].round(2).to_string(index=False))
print("sem vínculo entre os 100 primeiros por quantidade:", P.sort_values("qtd_pre", ascending=False).head(100).cmed_apresentacoes.isna().sum())
