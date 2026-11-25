"""Experimento nacional — seleciona a cesta (50 apresentações CEAF) e monta:
  nacional/dados/decision_input_nacional/   (só informação disponível até 29/01/2025)
  nacional/dados/evaluation_only_nacional/  (posterior ao corte; NÃO entregar ao decisor)
e roda as verificações de integridade temporal e de separação.

Uso: python -I -X utf8 nacional/scripts/n03_pacote_nacional.py <raiz_projeto>
"""
import glob, hashlib, json, os, re, shutil, sys, zipfile
import numpy as np, pandas as pd

ROOT = os.path.abspath(sys.argv[1])
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from padroniza import norm  # noqa: E402
CUT = pd.Timestamp("2025-01-29T23:59:59")
N_CESTA, MIN_REG = 50, 5
PR = os.path.join(ROOT, "nacional", "dados", "processados")
DI = os.path.join(ROOT, "nacional", "dados", "decision_input_nacional")
EV = os.path.join(ROOT, "nacional", "dados", "evaluation_only_nacional")
for d in (DI, EV):
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)

A = pd.read_parquet(os.path.join(PR, "apresentacoes.parquet"))
K = pd.read_parquet(os.path.join(PR, "apresentacao_catmat.parquet"))
V = pd.read_parquet(os.path.join(PR, "cmed_vinculos_sia.parquet"))

# ---------------- preços Compras.gov.br (cache) ----------------
rows = []
for c in K.catmat.unique():
    for f in glob.glob(os.path.join(ROOT, "data", "raw", "comprasgov", "precos", f"catmat_{c}_p*.json")):
        rows += json.load(open(f, encoding="utf-8")).get("resultado") or []
Q = pd.DataFrame(rows).drop_duplicates("idItemCompra")
Q["catmat"] = Q.codigoItemCatalogo.astype(str)
dres, dcom = pd.to_datetime(Q.dataResultado, errors="coerce"), pd.to_datetime(Q.dataCompra, errors="coerce")
Q["classe_temporal"] = np.where(dres.isna() | dcom.isna() | (dcom > dres), "indeterminado", np.where(dres <= CUT, "disponivel", "posterior"))
UN_SOLIDA = {"COMPRIMIDO", "CÁPSULA", "CAPSULA", "DRÁGEA", "DRAGEA", "UNIDADE", "COMPRIMIDO REVESTIDO", "SUPOSITÓRIO", "ADESIVO"}
UN_REC = {"FRASCO-AMPOLA", "FRASCO", "AMPOLA", "SERINGA", "SERINGA PREENCHIDA", "CANETA", "UNIDADE", "BOLSA", "TUBETE", "CARPULE", "SACHÊ", "ENVELOPE"}
ap_forma = A.set_index("ap_id").forma.to_dict(); ap_un = A.set_index("ap_id").unidade_sia.to_dict()
def compat(ap, unidade):
    u = str(unidade or "").upper().strip()
    solido = ap_forma.get(ap) in ("comprimido", "capsula") or str(ap_un.get(ap, "")).startswith(("comprim", "capsul", "drag", "supos", "adesiv"))
    if u in (UN_SOLIDA if solido else UN_REC):
        return "compativel"
    return "a_conferir: unidade de fornecimento " + (u.lower() or "não informada")
QK = K[["ap_id", "catmat"]].merge(Q, on="catmat")
QK["compatibilidade"] = [compat(a, u) for a, u in zip(QK.ap_id, QK.nomeUnidadeFornecimento)]
med = QK[(QK.classe_temporal == "disponivel") & (QK.compatibilidade == "compativel")].groupby("ap_id").precoUnitario.median()
QK["flag_preco_extremo"] = (QK.precoUnitario / QK.ap_id.map(med)).pipe(lambda r: (r > 10) | (r < 0.1)).fillna(False)

# ---------------- seleção da cesta: relevância econômica nacional (qtd. dispensada pré-corte × preço praticado mediano pré-corte) ----------------
ok = QK[(QK.classe_temporal == "disponivel") & (QK.compatibilidade == "compativel") & ~QK.flag_preco_extremo]
st = ok.groupby("ap_id").agg(precos_pre_n=("precoUnitario", "size"), preco_pre_mediana=("precoUnitario", "median"),
                             preco_pre_p25=("precoUnitario", lambda s: s.quantile(.25)), preco_pre_p75=("precoUnitario", lambda s: s.quantile(.75)),
                             precos_pre_ufs=("estado", "nunique"), precos_pre_esferas=("esfera", lambda s: "".join(sorted(set(s.dropna())))))
A = A.merge(st, left_on="ap_id", right_index=True, how="left")
A["qualidade_dados"] = np.select([A.teto0_unit_mediana.isna(), A.precos_pre_n.fillna(0) < MIN_REG, A.grupo_financiamento.isna(), A.qtd_pre <= 0],
                                 ["sem teto CMED vinculado", f"menos de {MIN_REG} preços compatíveis pré-corte", "grupo de financiamento não identificado", "sem dispensação pré-corte"], "ok")
A["relevancia_economica_pre"] = A.qtd_pre * A.preco_pre_mediana
cand = A[A.ap_id.isin(K.ap_id.unique()) | A.index.isin(range(90))]
C = cand[cand.qualidade_dados == "ok"].sort_values("relevancia_economica_pre", ascending=False).head(N_CESTA).copy()
assert len(C) == N_CESTA, len(C)
C["posicao_relevancia"] = range(1, N_CESTA + 1)
sel = set(C.ap_id)
A.assign(na_cesta=A.ap_id.isin(sel)).to_parquet(os.path.join(PR, "selecao_cesta.parquet"), index=False)

# ---------------- pacote de decisão ----------------
os.makedirs(os.path.join(DI, "problema")); os.makedirs(os.path.join(DI, "mercado"))
cols_cesta = ["ap_id", "nome", "unidade_sia", "principio", "concentracao", "forma", "grupo_financiamento", "grupo_metodo", "procs",
              "qtd_pre", "qtd_pre_ano_anterior", "valor_aprovado_pre", "valor_unit_financiado_pre", "cmed_apresentacoes", "cmed_laboratorios",
              "teto0_unit_min", "teto0_unit_mediana", "teto0_unit_max", "teto18_unit_mediana", "algum_cap", "algum_convenio_87", "todos_convenio_87",
              "precos_pre_n", "preco_pre_p25", "preco_pre_mediana", "preco_pre_p75", "precos_pre_ufs", "precos_pre_esferas", "posicao_relevancia"]
cesta = C[cols_cesta].rename(columns={"unidade_sia": "unidade_dispensacao", "procs": "procedimentos_sigtap", "qtd_pre": "dispensacao_12m_pre_corte",
                                      "qtd_pre_ano_anterior": "dispensacao_12m_ano_anterior", "valor_aprovado_pre": "valor_aprovado_sia_12m",
                                      "valor_unit_financiado_pre": "valor_unitario_financiado_sia"})
cesta["data_disponibilidade"] = pd.Timestamp("2024-12-31")
cesta["base_disponibilidade"] = "SIA/SUS: processamentos nov/2023–out/2024 (publicados antes do corte; base atual com reprocessamentos)"
cesta.to_parquet(os.path.join(DI, "problema", "cesta.parquet"), index=False)
proc2ap = {p: a for a, ps in zip(C.ap_id, C.procs) for p in ps.split("|")}
du = pd.read_parquet(os.path.join(PR, "sia_pre_uf.parquet")); du["ap_id"] = du.proc.map(proc2ap)
du[du.ap_id.notna()].groupby(["ap_id", "uf"], as_index=False).qtd.sum().rename(columns={"qtd": "dispensacao_12m_pre_corte"}).to_parquet(os.path.join(DI, "problema", "demanda_uf.parquet"), index=False)
dm = pd.read_parquet(os.path.join(PR, "sia_pre_mes.parquet")); dm["ap_id"] = dm.proc.map(proc2ap)
dm[dm.ap_id.notna()].groupby(["ap_id", "mes_processamento"], as_index=False).qtd.sum().rename(columns={"qtd": "dispensacao"}).to_parquet(os.path.join(DI, "problema", "demanda_mes.parquet"), index=False)
keep = ["ap_id", "catmat", "descricaoItem", "nomeUnidadeFornecimento", "compatibilidade", "flag_preco_extremo", "quantidade", "precoUnitario",
        "esfera", "estado", "municipio", "codigoUasg", "nomeUasg", "niFornecedor", "nomeFornecedor", "marca", "modalidade", "forma",
        "criterioJulgamento", "objetoCompra", "dataCompra", "dataResultado", "idItemCompra"]
pre = QK[QK.ap_id.isin(sel) & (QK.classe_temporal == "disponivel")][keep].rename(columns={"precoUnitario": "preco_unitario", "estado": "uf", "forma": "forma_compra"})
pre["categoria_valor"] = "preço unitário homologado/praticado em compra pública (não é pagamento)"
pre.to_parquet(os.path.join(DI, "mercado", "precos_comprasgov.parquet"), index=False)
QK[QK.ap_id.isin(sel) & (QK.classe_temporal == "indeterminado")][keep].to_parquet(os.path.join(PR, "comprasgov_quarentena.parquet"), index=False)
b = pd.read_parquet(os.path.join(ROOT, "data", "decision_input", "nacional", "bps_precos_praticados.parquet"))  # BPS nacional (script 24), inserção ≤ corte
bk = K[K.ap_id.isin(sel)][["ap_id", "catmat"]].merge(b, on="catmat")
bk = bk[["ap_id", "catmat", "descricao_catmat", "unidade_fornecimento", "uf", "esfera", "comprador_cnpj", "comprador_nome", "fornecedor_cnpj", "modalidade",
         "data_compra", "data_insercao", "quantidade", "preco_unitario_praticado", "flag_preco_extremo", "flag_duplicata_negocio", "id_origem"]]
bk["observacao"] = "fonte complementar; pode repetir compras também registradas no Compras.gov.br (não somar as duas bases)"
bk.to_parquet(os.path.join(DI, "mercado", "precos_bps.parquet"), index=False)
cm = V[V.proc.isin(proc2ap)].assign(ap_id=lambda x: x.proc.map(proc2ap)).drop(columns=["proc"]).drop_duplicates(["ap_id", "registro"])
cm["categoria_valor"] = "teto regulatório CMED por unidade dispensada (lista de 06/01/2025); não é preço praticado"
cm.to_parquet(os.path.join(DI, "mercado", "cmed_teto.parquet"), index=False)

# recursos: execução federal das ações de assistência farmacêutica (Portal da Transparência), exercícios encerrados antes do corte
R = []
for y in (2023, 2024):
    z = zipfile.ZipFile(os.path.join(ROOT, "data", "raw", "nacional", "orcamento", f"orcamento_despesa_{y}.zip"))
    d = pd.read_csv(z.open(z.namelist()[0]), sep=";", encoding="latin-1", dtype=str)
    d = d[d["CÓDIGO AÇÃO"].isin(["4705", "20AE", "4368"]) & d["NOME ÓRGÃO SUPERIOR"].str.contains("SA[UÚ]DE", case=False, regex=True, na=False)]
    cols = [c for c in d.columns if c.startswith("ORÇAMENTO") and "(R$)" in c]
    for c in cols:
        d[c] = pd.to_numeric(d[c].str.replace(".", "", regex=False).str.replace(",", ".", regex=False), errors="coerce")
    g = d.groupby(["EXERCÍCIO", "CÓDIGO AÇÃO", "NOME AÇÃO"], as_index=False)[cols].sum()
    R.append(g)
R = pd.concat(R).rename(columns={"ORÇAMENTO INICIAL (R$)": "orcamento_inicial", "ORÇAMENTO ATUALIZADO (R$)": "dotacao_final_exercicio",
                                 "ORÇAMENTO EMPENHADO (R$)": "empenhado", "ORÇAMENTO REALIZADO (R$)": "realizado_pago"})
R["fonte"] = "Portal da Transparência — Orçamento da Despesa (download por exercício)"
R["observacao"] = np.where(R["EXERCÍCIO"] == "2024", "exercício encerrado em 31/12/2024; arquivo baixado em 2026 (valores finais)", "exercício encerrado")
R.to_csv(os.path.join(DI, "problema", "recursos_federais.csv"), index=False)

# ---------------- dados reservados para avaliação ----------------
qp = pd.read_parquet(os.path.join(PR, "sia_pos_uf.parquet")); qp["ap_id"] = qp.proc.map(proc2ap)
qp[qp.ap_id.notna()].groupby(["ap_id", "uf"], as_index=False).qtd.sum().rename(columns={"qtd": "dispensacao_fev2025_jan2026"}).to_parquet(os.path.join(EV, "sia_dispensacao_pos_uf.parquet"), index=False)
C[["ap_id", "qtd_pos", "valor_aprovado_pos"]].rename(columns={"qtd_pos": "dispensacao_fev2025_jan2026", "valor_aprovado_pos": "valor_aprovado_sia_pos"}).to_parquet(os.path.join(EV, "sia_dispensacao_pos_total.parquet"), index=False)
QK[QK.ap_id.isin(sel) & (QK.classe_temporal == "posterior")][keep].rename(columns={"precoUnitario": "preco_unitario", "estado": "uf", "forma": "forma_compra"}).to_parquet(os.path.join(EV, "precos_comprasgov_pos.parquet"), index=False)
bp = pd.read_parquet(os.path.join(ROOT, "data", "processed", "bps_2025_2026.parquet")).rename(columns={"co_catmat": "catmat"})
bp["catmat"] = bp.catmat.astype(str)
bp = K[K.ap_id.isin(sel)][["ap_id", "catmat"]].merge(bp, on="catmat")
bp[["ap_id", "catmat", "ds_item", "un_fornecimento", "sg_uf", "ds_esfera", "cnpj_instituicao", "no_instituicao", "cnpj_fornecedor", "dt_compra", "dt_insercao",
    "qt_medicamento_num", "vl_preco_unitario_num", "co_seq_bps"]].to_parquet(os.path.join(EV, "precos_bps_2025_2026.parquet"), index=False)
for y in (2025, 2026):
    z = zipfile.ZipFile(os.path.join(ROOT, "data", "raw", "nacional", "orcamento", f"orcamento_despesa_{y}.zip"))
    d = pd.read_csv(z.open(z.namelist()[0]), sep=";", encoding="latin-1", dtype=str)
    d[d["CÓDIGO AÇÃO"].isin(["4705", "20AE", "4368"])].to_csv(os.path.join(EV, f"orcamento_acoes_af_{y}.csv"), index=False)
open(os.path.join(EV, "LEIA-ME.md"), "w", encoding="utf-8").write(
    "# evaluation_only_nacional — NÃO FORNECER AO AGENTE DECISOR\n\nDados posteriores a 29/01/2025 para avaliar a decisão nacional: dispensação SIA fev/2025–jan/2026 "
    "(demanda atendida observada), preços Compras.gov.br com resultado após o corte, BPS 2025–2026 e execução orçamentária federal 2025–2026.\n")

# ---------------- verificações ----------------
falhas = []
def chk(nome, cond):
    print(("OK   " if cond else "FALHA"), nome); (None if cond else falhas.append(nome))
for p in glob.glob(os.path.join(DI, "**", "*.*"), recursive=True):
    if not p.endswith((".parquet", ".csv")):
        continue
    df = pd.read_parquet(p) if p.endswith(".parquet") else pd.read_csv(p, dtype=str)
    for c in df.columns:
        lc = c.lower()
        chk(f"sem coluna de situação/atualização atual: {os.path.basename(p)}.{c}", not re.search(r"atualiza|situacao|status", lc))
        if "data" in lc and lc not in ("data_disponibilidade",):
            s = pd.to_datetime(df[c], errors="coerce")
            chk(f"datas ≤ corte: {os.path.basename(p)}.{c}", not (s > CUT).any())
chk("cesta com 50 apresentações", len(cesta) == 50 and cesta.ap_id.is_unique)
chk("toda apresentação da cesta tem dispensação, teto e preço pré-corte", cesta[["dispensacao_12m_pre_corte", "teto0_unit_mediana", "preco_pre_mediana"]].notna().all().all())
chk("cesta inclui aquisição centralizada (1A)", (cesta.grupo_financiamento == "1A").any())
a_, b_ = set(pre.idItemCompra), set(pd.read_parquet(os.path.join(EV, "precos_comprasgov_pos.parquet")).idItemCompra)
chk("separação: nenhum preço Compras.gov.br no pacote e na avaliação", not (a_ & b_))
chk("separação: BPS do pacote só com inserção ≤ corte", (pd.to_datetime(bk.data_insercao) <= CUT).all())
for f in glob.glob(os.path.join(ROOT, "nacional", "pacote_docs", "*")):  # LEIA-ME, restrições e consulta (redigidos à parte)
    shutil.copy(f, os.path.join(DI, os.path.basename(f)) if not f.endswith("restricoes.csv") else os.path.join(DI, "problema", "restricoes.csv"))
mf = [(os.path.relpath(p, DI).replace("\\", "/"), hashlib.sha256(open(p, "rb").read()).hexdigest()) for p in sorted(glob.glob(os.path.join(DI, "**", "*.*"), recursive=True))]
pd.DataFrame(mf, columns=["arquivo", "sha256"]).to_csv(os.path.join(DI, "MANIFESTO.csv"), index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 60)
print(cesta[["posicao_relevancia", "ap_id", "nome", "grupo_financiamento", "dispensacao_12m_pre_corte", "preco_pre_mediana", "teto0_unit_mediana", "precos_pre_n"]].round(2).to_string(index=False))
print("grupos:", cesta.grupo_financiamento.value_counts().to_dict(), "| relevância total (R$):", round(float((cesta.dispensacao_12m_pre_corte * cesta.preco_pre_mediana).sum()), 0))
print("excluídos por qualidade entre os 90 candidatos:", cand.qualidade_dados.value_counts().to_dict())
assert not falhas, falhas
