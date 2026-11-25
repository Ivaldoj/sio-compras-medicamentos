"""Experimento nacional — apresentações CEAF candidatas: agrega procedimentos SIA equivalentes (biossimilar/originador),
atribui o grupo de financiamento (RENAME 2024, Anexo III), vincula CATMAT (catálogo Compras.gov.br) e baixa a pesquisa de preço.

Uso: python -I -X utf8 nacional/scripts/n02_apresentacoes_catmat.py <raiz_projeto> [n_candidatos=90]
Grava nacional/dados/processados/apresentacoes.parquet, apresentacao_catmat.parquet e o cache bruto em data/raw/comprasgov/.
"""
import glob, json, os, re, sys
import numpy as np, pandas as pd
from pypdf import PdfReader

ROOT = os.path.abspath(sys.argv[1]); N = int(sys.argv[2]) if len(sys.argv) > 2 else 90
sys.path.insert(0, os.path.join(ROOT, "scripts")); sys.path.insert(0, os.path.join(ROOT, "nacional", "scripts"))
from padroniza import concentracoes, conteudo_item, forma, norm, principio, principio_catmat  # noqa: E402
from comprasgov import API, paginas  # noqa: E402
import importlib.util  # noqa: E402
spec = importlib.util.spec_from_file_location("n01", os.path.join(ROOT, "nacional", "scripts", "n01_sia_cmed_candidatos.py"))
PR = os.path.join(ROOT, "nacional", "dados", "processados")
RAW = os.path.join(ROOT, "data", "raw", "comprasgov")

# funções de vínculo do n01 (sem reexecutá-lo): copiadas por texto para não duplicar regra
src = open(os.path.join(ROOT, "nacional", "scripts", "n01_sia_cmed_candidatos.py"), encoding="utf-8").read()
exec(src[src.index("def principio_sia"):src.index("assert principio_sia")], globals())

P = pd.read_parquet(os.path.join(PR, "sia_procedimentos.parquet"))
V = pd.read_parquet(os.path.join(PR, "cmed_vinculos_sia.parquet"))
limpa = lambda s: re.sub(r"\(\s*(?:BIOSSIMILAR|ORIGINADOR|1B)[^)]*\)?|Ç¨", " ", s)
SIN = {"eltrombopag": "eltrombopague", "mofetil": "mofetila"}  # grafia do catálogo × grafia do SIA (equivalências registradas)
P["nome"] = P.nome.str.replace(r"(\d)O(\s*ML)", r"\g<1>0\2", regex=True)  # erro de digitação no SIA: "5O ML" = 50 mL
P["chave"] = [(tuple(sorted(principio_sia(n))), tuple(sorted(concentracoes(limpa(n)))), forma(limpa(n) + " " + u)[0] or "")
              for n, u in zip(P.nome, P.unidade_sia)]
A = (P.groupby("chave").agg(procs=("proc", lambda s: "|".join(sorted(s))), nome=("nome", lambda s: limpa(s.iloc[np.argmax(P.loc[s.index, "qtd_pre"].values)]).strip()),
                            unidade_sia=("unidade_sia", "first"), qtd_pre=("qtd_pre", "sum"), qtd_pre_ano_anterior=("qtd_pre_ano_anterior", "sum"),
                            qtd_pos=("qtd_pos", "sum"), valor_aprovado_pre=("valor_aprovado_pre", "sum"), valor_aprovado_pos=("valor_aprovado_pos", "sum"))
     .reset_index())
A["principio"] = A.chave.map(lambda k: "|".join(k[0])); A["concentracao"] = A.chave.map(lambda k: str(list(k[1]))); A["forma"] = A.chave.map(lambda k: k[2])
proc2ap = {p: i for i, ps in zip(A.index, A.procs) for p in ps.split("|")}
V["ap"] = V.proc.map(proc2ap)
t = V.drop_duplicates(["ap", "registro"]).groupby("ap").agg(cmed_apresentacoes=("registro", "size"), cmed_laboratorios=("laboratorio", "nunique"),
    teto0_unit_min=("teto_gov_0_unit", "min"), teto0_unit_mediana=("teto_gov_0_unit", "median"), teto0_unit_max=("teto_gov_0_unit", "max"),
    teto18_unit_mediana=("teto_gov_18_unit", "median"), algum_cap=("cap", "any"), algum_convenio_87=("convenio_87", "any"), todos_convenio_87=("convenio_87", "all"))
A = A.join(t)
A["valor_unit_financiado_pre"] = np.where(A.qtd_pre > 0, A.valor_aprovado_pre / A.qtd_pre, np.nan)
A["relevancia_teto_pre"] = A.qtd_pre * A.teto0_unit_mediana
A = A.sort_values("relevancia_teto_pre", ascending=False).reset_index(drop=True)
A.insert(0, "ap_id", [f"AP{i + 1:03d}" for i in range(len(A))])

# ---------------- grupo de financiamento (RENAME 2024, Anexo III) por correspondência textual ----------------
pg = [p.extract_text() or "" for p in PdfReader(os.path.join(ROOT, "data", "raw", "nacional", "rename", "relacao_nacional_medicamentos_2024_2ed.pdf")).pages]
ini = next(i for i, x in enumerate(pg) if "ANEXO III" in x and "Componente Especializado" in x and i > 100)
fim = next(i for i in range(ini + 1, len(pg)) if "ANEXO IV" in pg[i])
R3 = norm(" ".join(pg[ini:fim]))
R3 = re.sub(r"(\d)\.(\d{3})", r"\1\2", R3)
def grupo(princ, conc):
    """1º grupo após a concentração da apresentação no trecho da substância; senão, 1º grupo do trecho (com ressalva)."""
    toks = [t for t in princ.split("|") if t]
    if not toks:
        return None, "sem princípio"
    pos = [m.start() for m in re.finditer(r"\b" + re.escape(max(toks, key=len)) + r"\b", R3)]
    for p in pos:
        jan = R3[p:p + 250]  # só a entrada da própria substância (janela maior invade a substância seguinte)
        for v, u in conc:
            num = f"{v:g}".replace(".", ",")
            un = {"mg": "mg", "ui": "ui", "mg/ml": "mg/ml"}.get(u, u.split("/")[0])
            m = re.search(r"(?<![\d,])" + re.escape(num) + r"\s*" + re.escape(un.split("/")[0]), jan)
            if m:
                g = re.search(r"\b(1a|1b|2)\b", jan[m.end():m.end() + 120])
                if g:
                    return g.group(1).upper(), "concentração localizada"
        g = re.search(r"\b(1a|1b|2)\b", jan)
        if g:
            return g.group(1).upper(), "1º grupo do trecho da substância (concentração não localizada)"
    return None, "substância não localizada no Anexo III"
G = [grupo(p, k[1]) for p, k in zip(A.principio, A.chave)]
A["grupo_financiamento"] = [g for g, _ in G]; A["grupo_metodo"] = [m for _, m in G]
A["coerencia_sia"] = np.where(A.grupo_financiamento == "1B", np.where(A.valor_aprovado_pre > 0, "ok", "1B sem valor no SIA"),
                              np.where(A.valor_aprovado_pre > 0, "valor no SIA sem ser 1B", "ok"))

# ---------------- CATMAT: catálogo oficial (PDMs da classe 6505) ----------------
pdm = pd.DataFrame([x for f in sorted(glob.glob(os.path.join(RAW, "catalogo", "pdm_6505_p*.json"))) for x in json.load(open(f, encoding="utf-8"))["resultado"]])
pdm["tk"] = pdm.nomePdm.map(lambda s: {SIN.get(t, t) for t in re.findall(r"[a-z]{4,}", norm(s))})
C = A.head(N).copy()
rows = []
for r in C.itertuples():
    toks = set(r.principio.split("|"))
    for x in pdm[pdm.tk.map(lambda s: bool(s & toks))].itertuples():
        for it in paginas(f"{API}/modulo-material/4_consultarItemMaterial?codigoPdm={x.codigoPdm}", os.path.join(RAW, "catalogo", f"itens_pdm_{x.codigoPdm}")):
            pc = frozenset(SIN.get(t, t) for t in principio_catmat(it.get("nomePdm"), it.get("descricaoItem")))
            if not (pc == frozenset(toks) or (frozenset(toks) < pc and len(pc - frozenset(toks)) == 1)):
                continue
            cc = concentracoes(it.get("descricaoItem"))
            # massa total de um lado = concentração × volume do outro (catálogo "100 MG" × SIA "10 MG/ML ... 10 ML", e o inverso)
            if not cc or not mesma_concentracao(frozenset(r.chave[1]), cc, conteudo_item(it.get("descricaoItem")), conteudo_item(r.nome)):
                continue
            fc = forma(it.get("descricaoItem"))[0]
            if r.forma and fc and r.forma != fc and not ({r.forma, fc} <= {"comprimido", "capsula"}) and not (r.forma == "injetavel" or fc == "injetavel"):
                continue
            rows.append(dict(ap_id=r.ap_id, catmat=str(it["codigoItem"]), descricao_catmat=it.get("descricaoItem"), codigo_pdm=x.codigoPdm,
                             item_ativo=it.get("statusItem")))
K = pd.DataFrame(rows).drop_duplicates(["ap_id", "catmat"])
print("candidatos:", len(C), "| com CATMAT:", K.ap_id.nunique(), "| CATMATs:", K.catmat.nunique())

# ---------------- pesquisa de preço (todas as datas; o corte é aplicado depois, por dataResultado) ----------------
for i, c in enumerate(sorted(K.catmat.unique())):
    paginas(f"{API}/modulo-pesquisa-preco/1_consultarMaterial?tipo=codigoItemCatalogo&codigo={c}", os.path.join(RAW, "precos", f"catmat_{c}"))
    if i % 25 == 0:
        print("preços:", i, "de", K.catmat.nunique(), flush=True)
A.drop(columns=["chave"]).to_parquet(os.path.join(PR, "apresentacoes.parquet"), index=False)
K.to_parquet(os.path.join(PR, "apresentacao_catmat.parquet"), index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 70)
print(A.head(N)[["ap_id", "nome", "qtd_pre", "teto0_unit_mediana", "grupo_financiamento", "grupo_metodo", "coerencia_sia"]].to_string(index=False))
