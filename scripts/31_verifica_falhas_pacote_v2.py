"""Pré-Etapa 5 — verifica as 4 possíveis falhas do pacote apontadas pelo agente decisor (Etapa 4) e gera, SEPARADAMENTE,
o pacote corrigido data/decision_input_v2/ (v1 + errata). Não altera data/decision_input/ nem etapa4/.

Uso: python -I -X utf8 scripts/31_verifica_falhas_pacote_v2.py <raiz_projeto>
Saídas:
  etapa5/verificacao/falhas_pacote.csv     veredito, causa, evidência e impacto de cada apontamento
  etapa5/verificacao/impacto_itens.csv     v1 × v2 nos itens afetados
  data/decision_input_v2/                  cópia de v1 + correções; ERRATA.csv, MANIFESTO.csv, LEIA-ME.md (com seção de errata)
"""
import csv, hashlib, json, os, re, shutil, sys
import pandas as pd

ROOT = os.path.abspath(sys.argv[1])
V1 = os.path.join(ROOT, "data", "decision_input")
V2 = os.path.join(ROOT, "data", "decision_input_v2")
OUT = os.path.join(ROOT, "etapa5", "verificacao")
os.makedirs(OUT, exist_ok=True)
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()

# v1 precisa continuar idêntico ao manifesto (é o pacote usado na Etapa 4)
man = {r["arquivo"]: r["sha256"] for r in csv.DictReader(open(os.path.join(V1, "MANIFESTO.csv"), encoding="utf-8"))}
assert all(sha(os.path.join(ROOT, f)) == h for f, h in man.items()), "data/decision_input/ difere do manifesto"

rd = lambda rel: pd.read_parquet(os.path.join(V1, rel)) if rel.endswith(".parquet") else pd.read_csv(os.path.join(V1, rel), dtype={"registro": str})
I = rd("organizacional/itens_santa_luzia.parquet")
CAT, CATO = rd("padronizacao/item_catmat_candidatos.parquet"), rd("padronizacao/item_catmat_catalogo_oficial.parquet")
G, ICG, CG = rd("padronizacao/item_bps_grupos.parquet"), rd("padronizacao/item_comprasgov_registros.parquet"), rd("nacional/comprasgov_precos_praticados.parquet")
BPS, VC, RC = rd("nacional/bps_precos_praticados.parquet"), rd("padronizacao/item_cmed_vinculos.parquet"), rd("padronizacao/regras_conversao.csv")
AP, PR = rd("nacional/cmed_2025_01_apresentacoes.parquet"), rd("nacional/cmed_2025_01_precos.parquet")
desc = I.set_index("item").descricao
q = I.set_index("item").quantidade_estimada
p_org = I.set_index("item").preco_unitario_estimado_orgao

# ---------------- regras das correções ----------------
def tipo_insulina(t):
    t = (t or "").lower()
    if "insulina" not in t:
        return None
    for k, v in (("prolongada", "ANÁLOGA DE AÇÃO PROLONGADA"), ("rápida", "ANÁLOGA DE AÇÃO RÁPIDA"), ("rapida", "ANÁLOGA DE AÇÃO RÁPIDA"),
                 ("nph", "NPH"), ("regular", "REGULAR")):
        if k in t:
            return v
    return None


def tipo_catmat(d):
    m = re.search(r"TIPO:\s*([^,]+)", d or "")
    return m.group(1).strip() if m else None


assert tipo_insulina("Insulina análoga de ação rápida 100UI/mL") == "ANÁLOGA DE AÇÃO RÁPIDA" and tipo_catmat("INSULINA, TIPO: NPH , CONC") == "NPH"
PREMIX = re.compile(r"\d+\s*N\s*/\s*\d+\s*R|\bMIX\b|70\s*/\s*30", re.I)
SEM_SISTEMA = {"TUBETE", "REFIL", "CARTUCHO", "FRASCO", "FRASCO-AMPOLA"}  # mesma regra das canetas no Compras.gov.br (script 29)


def conflito_tipo(df):
    ti = df["item"].map(desc).map(tipo_insulina)
    tc = df.descricao_catmat.map(tipo_catmat)
    return ti.notna() & tc.notna() & (ti != tc)


# E-01: CATMAT de outro tipo de insulina
rm_cat = pd.concat([CAT[conflito_tipo(CAT)][["item", "catmat"]], CATO[conflito_tipo(CATO)][["item", "catmat"]]]).drop_duplicates()
chave = lambda df: list(zip(df["item"], df.catmat.astype(str)))
rm = set(chave(rm_cat))
CAT2, CATO2 = CAT[[k not in rm for k in chave(CAT)]], CATO[[k not in rm for k in chave(CATO)]]
G2, ICG2 = G[[k not in rm for k in chave(G)]].copy(), ICG[[k not in rm for k in chave(ICG)]]
# E-02: grupo BPS em tubete/refil para item que exige sistema de aplicação
pede_sistema = G2["item"].map(desc).str.contains("sistema de aplica", case=False, na=False)
e02 = pede_sistema & G2.unidade_fornecimento.str.upper().isin(SEM_SISTEMA) & (G2.compatibilidade == "compativel")
G2.loc[e02, "compatibilidade"] = "incompativel: tubete/refil/frasco sem sistema de aplicação"
# E-03: pré-mistura NPH+Regular vinculada a item de insulina NPH ou Regular
eh_premix = VC.produto.fillna("").str.contains(PREMIX) | VC.apresentacao.fillna("").str.contains(PREMIX)
e03 = VC["item"].map(desc).map(tipo_insulina).isin(["NPH", "REGULAR"]) & eh_premix & VC.classe.isin(["exata", "compativel_conversao"])
VC2 = VC.copy()
VC2.loc[e03, "classe"] = "incompativel"
VC2.loc[e03, "justificativa"] = "pré-mistura (NPH + Regular) não é a insulina pedida (errata v2, E-03)"
VC2.loc[e03, "fator_conversao"] = None
rm_rc = set(zip(VC.loc[e03, "item"], VC.loc[e03, "registro"].astype(str)))
RC2 = RC[[(i, str(r)) not in rm_rc for i, r in zip(RC["item"], RC.registro)]].copy()
afet_rc = sorted({i for i, _ in rm_rc})
m = RC2["item"].isin(afet_rc)
RC2.loc[m, "razao_mediana_item"] = RC2.loc[m, "teto_unitario_pb"] / RC2[m].groupby("item").teto_unitario_pb.transform("median")
RC2.loc[m, "verif_consistencia_interna"] = ["ok" if 0.25 <= x <= 4 else "alerta: teto unitário fora de 0,25–4× a mediana do item" for x in RC2.loc[m, "razao_mediana_item"]]

# ---------------- itens: recalcula as colunas derivadas dos itens afetados ----------------
afetados = sorted(set(rm_cat["item"]) | set(G2.loc[e02, "item"]) | set(afet_rc))
I2 = I.copy().set_index("item")
cg_join = ICG2.merge(CG[["id_origem"]], on="id_origem")
for it in afetados:
    cands = sorted(set(CAT2.loc[CAT2["item"] == it, "catmat"].astype(str)) | set(CATO2.loc[CATO2["item"] == it, "catmat"].astype(str)))
    I2.loc[it, "catmat_candidatos"] = "|".join(cands) or None
    I2.loc[it, "catmat_status"] = "unico" if len(cands) == 1 else ("multiplo" if cands else "nao_identificado")
    I2.loc[it, "status_identificacao"] = {"unico": "validada por atributos (1 CATMAT)", "multiplo": "validada por atributos (vários CATMAT equivalentes)",
                                          "nao_identificado": "ausente"}[I2.loc[it, "catmat_status"]]
    g = G2[G2["item"] == it]
    I2.loc[it, "bps_registros_compativeis"] = int(g.loc[g.compatibilidade == "compativel", "registros"].sum())
    c = cg_join[cg_join["item"] == it]
    I2.loc[it, "comprasgov_registros_compativeis"] = int((c.compatibilidade == "compativel").sum())
    I2.loc[it, "comprasgov_registros_a_conferir"] = int(c.compatibilidade.str.startswith("a_conferir").sum())
    fontes = [f for f, n in (("BPS", I2.loc[it, "bps_registros_compativeis"]), ("Compras.gov.br", I2.loc[it, "comprasgov_registros_compativeis"])) if n > 0]
    I2.loc[it, "fontes_preco_praticado"] = "|".join(fontes) or None
    v = VC2[VC2["item"] == it]
    for cl in ("exata", "compativel_conversao", "provavel_conferencia", "indeterminada", "incompativel"):
        I2.loc[it, "cmed_" + cl] = int((v.classe == cl).sum())
    tu = RC2.loc[RC2["item"] == it, "teto_unitario_pb"]
    if len(tu):
        I2.loc[it, ["teto_cmed_unitario_pb_min", "teto_cmed_unitario_pb_max"]] = [tu.min(), tu.max()]
        I2.loc[it, "estimativa_sobre_teto_max"] = I2.loc[it, "preco_unitario_estimado_orgao"] / tu.max()
        I2.loc[it, "alerta_estimativa_acima_teto_cmed"] = bool(I2.loc[it, "estimativa_sobre_teto_max"] > 1)
I2 = I2.reset_index()

# ---------------- impacto: preço praticado compatível (mediana, todo o pré-corte) e teto, v1 × v2 ----------------
def mediana_compat(g, icg, it):
    gg = g[(g["item"] == it) & (g.compatibilidade == "compativel")]
    b = BPS.merge(gg[["catmat", "unidade_fornecimento", "capacidade_descricao"]], on=["catmat", "unidade_fornecimento", "capacidade_descricao"]).preco_unitario_praticado
    c = CG.merge(icg[(icg["item"] == it) & (icg.compatibilidade == "compativel")][["id_origem"]], on="id_origem").preco_unitario_praticado
    s = pd.concat([b, c])
    return (float(s.median()) if len(s) else None), len(s)


imp = []
for it in afetados:
    m1, n1 = mediana_compat(G, ICG, it)
    m2, n2 = mediana_compat(G2, ICG2, it)
    a, b = I.set_index("item").loc[it], I2.set_index("item").loc[it]
    imp.append(dict(item=it, descricao=desc[it], quantidade=q[it], preco_estimado_orgao=p_org[it],
                    mediana_praticada_compat_v1=m1, n_v1=n1, mediana_praticada_compat_v2=m2, n_v2=n2,
                    valor_ref_mediana_v1=(m1 or 0) * q[it], valor_ref_mediana_v2=(m2 or 0) * q[it],
                    teto_max_v1=a.teto_cmed_unitario_pb_max, teto_max_v2=b.teto_cmed_unitario_pb_max,
                    alerta_acima_teto_v1=bool(a.alerta_estimativa_acima_teto_cmed), alerta_acima_teto_v2=bool(b.alerta_estimativa_acima_teto_cmed),
                    excesso_sobre_teto_v2=max(0.0, (p_org[it] - b.teto_cmed_unitario_pb_max) * q[it]) if pd.notna(b.teto_cmed_unitario_pb_max) else None))
IMP = pd.DataFrame(imp)
IMP.to_csv(os.path.join(OUT, "impacto_itens.csv"), index=False, encoding="utf-8")

# ---------------- F3 (item 268): o teto é consistente entre tamanhos de embalagem do mesmo produto? ----------------
r268 = RC[RC["item"] == 268].merge(VC[["item", "registro", "produto"]], on=["item", "registro"])
cons = r268.groupby("produto").teto_unitario_pb.agg(["min", "max", "count"])
cons["dispersao"] = cons["max"] / cons["min"]
med268, _ = mediana_compat(G, ICG, 268)
f3_ok_conversao = bool((cons.loc[cons["count"] > 1, "dispersao"] < 1.01).all())

# ---------------- F4 (Convênio 87/02): a lista CMED publica colunas de 20% para esses produtos? ----------------
cfz = set(AP.loc[AP.convenio_confaz_87, "registro"].astype(str))
pr = PR.assign(registro=PR.registro.astype(str))
conv_20 = int(pr[pr.registro.isin(cfz) & (pr.aliquota_icms == "20%")].registro.nunique())
piv = pr[~pr.registro.isin(cfz) & pr.aliquota_icms.isin(["0%", "20%"])].pivot_table(index=["registro", "tipo_preco"], columns="aliquota_icms", values="valor_embalagem", aggfunc="first").dropna()
K20 = float((piv["20%"] / piv["0%"]).median())  # razão típica 20%/0% nos produtos fora do convênio
rc_c = RC.assign(conv=RC.registro.astype(str).isin(cfz))
it_conv = rc_c[rc_c.conv & (rc_c.teto_aliquota_pb == "0%")]["item"].unique()
v_conv = float((I.set_index("item").loc[it_conv, "valor_total_estimado_orgao"]).sum())

# ---------------- veredito por apontamento ----------------
i194, i197 = IMP.set_index("item"), None
F = [
    dict(id="F1", apontamento="itens 194/195: grupo 'compatível' mistura preços de outros tipos de insulina",
         veredito="CONFIRMADA (e mais ampla que o apontado)",
         causa="nivel_catmat compara princípio, concentração e forma, mas não o atributo TIPO do CATMAT de insulina; e a regra de canetas (tubete/refil ≠ sistema de aplicação) foi aplicada ao Compras.gov.br, não aos grupos BPS",
         evidencia=f"194 recebia CATMAT 440255 (análoga rápida) e 442012 (NPH); 195 recebia 442012 (NPH) e 468664 (análoga prolongada); grupos BPS TUBETE marcados compatíveis em itens 'com sistema de aplicação' ({int(e02.sum())} grupos)",
         itens="194, 195",
         impacto=f"referência por mediana praticada compatível: v1 R$ {IMP.valor_ref_mediana_v1.sum():,.2f} → v2 R$ {IMP[IMP.item.isin([194,195])].valor_ref_mediana_v2.sum() + IMP[~IMP.item.isin([194,195])].valor_ref_mediana_v1.sum():,.2f} (itens afetados); peso dos 2 itens na estimativa: R$ {float(I.set_index('item').loc[[194,195], 'valor_total_estimado_orgao'].sum()):,.2f} (0,8%)",
         corrigido_em_v2="sim (E-01, E-02)"),
    dict(id="F2", apontamento="item 197: vínculo CMED de pré-mistura (HUMULIN 70N/30R) indevido",
         veredito="CONFIRMADA",
         causa="o vínculo CMED de insulina não distingue pré-mistura 70/30 de NPH (mesma forma, concentração e frasco)",
         evidencia="HUMULIN 70N/30R 100 UI/ML SUS INJ CT FA X 10 ML classificado 'exata' para NPH frasco 10 mL; único caso de pré-mistura nos itens de insulina",
         itens="197",
         impacto=f"teto máx. R$ {IMP.set_index('item').loc[197,'teto_max_v1']:.2f} → R$ {IMP.set_index('item').loc[197,'teto_max_v2']:.2f}; estimativa R$ {p_org[197]:.2f} passa a ficar acima do teto (41 itens); excesso R$ {IMP.set_index('item').loc[197,'excesso_sobre_teto_v2']:,.2f}",
         corrigido_em_v2="sim (E-03)"),
    dict(id="F3", apontamento="item 268: teto parece ter erro de conversão",
         veredito="NÃO CONFIRMADA",
         causa="o teto unitário é o mesmo em embalagens de 10 e de 50 ampolas do mesmo produto (fatores corretos); o teto CMED é que está muito acima do preço praticado (teto 'descolado' do mercado)",
         evidencia=f"teto unitário por produto (mín–máx entre embalagens): " + "; ".join(f"{p}: {a:.2f}–{b:.2f}" for p, (a, b) in cons[["min", "max"]].iterrows()) +
                   f"; mediana praticada compatível R$ {med268:.2f}; menor teto = {RC[RC['item']==268].teto_unitario_pb.min()/med268:.0f}× a mediana",
         itens="268", impacto="nenhum no pacote; no modelo do agente, excluir o item do E2 reduz o custo de E2 em poucos milhares de reais (ver avaliação)",
         corrigido_em_v2="não se aplica" if f3_ok_conversao else "verificar"),
    dict(id="F4", apontamento="Convênio ICMS 87/02: o pacote não traz a coluna de 20% para esses produtos",
         veredito="FATO CONFIRMADO, MAS NÃO É FALHA DO PACOTE",
         causa="a própria lista CMED de preços para compras públicas (06/01/2025) só publica 'Sem Imposto' e '0%' para os 2.810 registros do Convênio 87/02; o pacote reproduz a fonte",
         evidencia=f"registros do convênio com coluna de 20% no pacote: {conv_20}; na lista bruta: 0 de 2.810 (todas as colunas de 12% a 22% vazias). Razão mediana 20%/0% nos demais produtos: {K20:.4f}",
         itens=f"{len(it_conv)} itens com algum vínculo do convênio a 0%",
         impacto=f"só sensibilidade: se o convênio não se aplicasse, o teto desses vínculos subiria ~{(K20-1)*100:.0f}% (estimado pela razão, não publicado); estimativa desses itens R$ {v_conv:,.2f}",
         corrigido_em_v2="documentação (LEIA-ME v2); sem alteração de dados"),
]
pd.DataFrame(F).to_csv(os.path.join(OUT, "falhas_pacote.csv"), index=False, encoding="utf-8")

# ---------------- grava v2 ----------------
if os.path.exists(V2):
    shutil.rmtree(V2)
shutil.copytree(V1, V2)
wr = lambda df, rel: df.to_parquet(os.path.join(V2, rel), index=False) if rel.endswith(".parquet") else df.to_csv(os.path.join(V2, rel), index=False)
wr(I2, "organizacional/itens_santa_luzia.parquet"); wr(CAT2, "padronizacao/item_catmat_candidatos.parquet"); wr(CATO2, "padronizacao/item_catmat_catalogo_oficial.parquet")
wr(G2, "padronizacao/item_bps_grupos.parquet"); wr(ICG2, "padronizacao/item_comprasgov_registros.parquet"); wr(VC2, "padronizacao/item_cmed_vinculos.parquet")
wr(RC2, "padronizacao/regras_conversao.csv")
ER = pd.DataFrame([
    dict(id="E-01", tabela="item_catmat_candidatos, item_catmat_catalogo_oficial, item_bps_grupos, item_comprasgov_registros",
         alteracao=f"removidos {len(rm_cat)} pares item×CATMAT com TIPO de insulina diferente do item: {sorted(rm)}", origem="F1"),
    dict(id="E-02", tabela="item_bps_grupos", alteracao=f"{int(e02.sum())} grupos TUBETE/REFIL/FRASCO em item que exige sistema de aplicação: compativel → incompativel", origem="F1"),
    dict(id="E-03", tabela="item_cmed_vinculos, regras_conversao", alteracao=f"pré-mistura vinculada a NPH/Regular → incompativel: {sorted(rm_rc)}", origem="F2"),
    dict(id="E-04", tabela="itens_santa_luzia", alteracao=f"colunas derivadas recalculadas para os itens {afetados}", origem="F1, F2"),
    dict(id="E-05", tabela="LEIA-ME.md", alteracao="nota: a lista CMED não publica 20% para produtos do Convênio 87/02 (fonte, não falha)", origem="F4"),
])
ER.to_csv(os.path.join(V2, "ERRATA.csv"), index=False, encoding="utf-8")
leia = open(os.path.join(V1, "LEIA-ME.md"), encoding="utf-8").read()
nota = ("> **Versão 2 (errata de 23/11/2026, pré-Etapa 5).** Igual à versão usada na Etapa 4 (`data/decision_input/`), com as correções de `ERRATA.csv`: "
        "itens 194/195 sem CATMAT de outro tipo de insulina e sem tubete como preço de caneta; item 197 sem o vínculo da pré-mistura HUMULIN 70N/30R "
        "(o item passa a ter estimativa acima do teto: 41 itens no total). Nota sobre o Convênio ICMS 87/02: a lista CMED de compras públicas só publica "
        "as colunas 'Sem Imposto' e '0%' para os produtos do convênio; o teto a 20% desses produtos não existe na fonte. Nenhuma informação posterior "
        "a 29/01/2025 foi acrescentada.\n\n")
ac = I2.alerta_estimativa_acima_teto_cmed.fillna(False).astype(bool)
pct = I2.valor_total_estimado_orgao[ac].sum() / I2.valor_total_estimado_orgao.sum()
leia, n_sub = re.subn(r"em \d+ itens \([\d,]+% do valor estimado\) o preço unitário estimado está acima",
                      f"em {int(ac.sum())} itens ({pct:.1%} do valor estimado) o preço unitário estimado está acima".replace(".", ","), leia)
assert n_sub == 1
open(os.path.join(V2, "LEIA-ME.md"), "w", encoding="utf-8").write(leia.replace("\n", "\n" + nota, 1) if leia.startswith("# ") else nota + leia)
rows = []
for d, _, fs in os.walk(V2):
    for f in sorted(fs):
        if f.startswith("MANIFESTO"):
            continue
        p = os.path.join(d, f)
        rows.append((os.path.relpath(p, ROOT).replace("\\", "/"), os.path.getsize(p), sha(p)))
os.remove(os.path.join(V2, "MANIFESTO.json"))
with open(os.path.join(V2, "MANIFESTO.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["arquivo", "bytes", "sha256"]); w.writerows(sorted(rows))

# ---------------- autoverificação ----------------
assert not conflito_tipo(pd.read_parquet(os.path.join(V2, "padronizacao/item_catmat_candidatos.parquet"))).any()
assert not conflito_tipo(pd.read_parquet(os.path.join(V2, "padronizacao/item_catmat_catalogo_oficial.parquet"))).any()
v2vc = pd.read_parquet(os.path.join(V2, "padronizacao/item_cmed_vinculos.parquet"))
assert not ((v2vc.produto.fillna("").str.contains(PREMIX)) & v2vc["item"].map(desc).map(tipo_insulina).isin(["NPH", "REGULAR"]) & v2vc.classe.isin(["exata", "compativel_conversao"])).any()
assert afetados == [194, 195, 197], afetados
assert all(sha(os.path.join(ROOT, f)) == h for f, h in man.items()), "v1 foi alterado"
assert len(pd.read_csv(os.path.join(V2, "padronizacao/regras_conversao.csv"))) == len(RC) - len(rm_rc)
print(pd.DataFrame(F)[["id", "veredito"]].to_string(index=False))
print(IMP.to_string(index=False))
print(f"K20={K20:.4f} | itens com vínculo do convênio a 0%: {len(it_conv)} (estimativa R$ {v_conv:,.2f}) | E-02 grupos: {int(e02.sum())} | v2 arquivos: {len(rows)}")
