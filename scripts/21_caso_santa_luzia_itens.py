"""Etapa 2 — itens do caso Santa Luzia/PB: necessidade planejada (PNCP), evolução entre pregões, referências de preço
disponíveis na data de decisão (BPS inserido até a data) e compras registradas depois (BPS).
Uso: python -I -X utf8 21_caso_santa_luzia_itens.py <raiz_projeto> [data_decisao=2025-01-29]
Saídas: reports/caso_sl_itens_pe04_2025.csv, caso_sl_evolucao_itens.csv, caso_sl_bps_santa_luzia.csv"""
import glob, json, os, sys, zipfile
import pandas as pd

ROOT = sys.argv[1]
DEC = pd.Timestamp(sys.argv[2] if len(sys.argv) > 2 else "2025-01-29")
E2 = os.path.join(ROOT, "data", "raw", "pncp", "etapa2")
R = lambda f: os.path.join(ROOT, "reports", f)


def itens(pasta):
    L = [x for f in sorted(glob.glob(os.path.join(E2, pasta, "itens_p*.json"))) for x in json.load(open(f, encoding="utf8"))]
    d = pd.DataFrame(L)
    d["catmat"] = d.catalogoCodigoItem.astype(str).str.replace(r"\D", "", regex=True)
    res = {}
    for f in glob.glob(os.path.join(E2, pasta, "resultado_item_*.json")):
        r = json.load(open(f, encoding="utf8"))
        r = [x for x in (r or []) if not x.get("dataCancelamento")]
        if r:
            res[r[0]["numeroItem"]] = r[0]
    d["preco_homologado"] = d.numeroItem.map(lambda n: res.get(n, {}).get("valorUnitarioHomologado"))
    d["qtd_homologada"] = d.numeroItem.map(lambda n: res.get(n, {}).get("quantidadeHomologada"))
    d["fornecedor"] = d.numeroItem.map(lambda n: res.get(n, {}).get("niFornecedor"))
    d["data_resultado"] = d.numeroItem.map(lambda n: res.get(n, {}).get("dataResultado"))
    return d


a = itens("09090689000167_2025_6")
print("PE 04/2025 (PNCP 09090689000167-1-000006/2025): itens", len(a), "| com CATMAT:", int((a.catmat.str.len() > 0).sum()),
      "| CATMAT distintos:", a.catmat.nunique(), "| soma valorTotal estimado: %.2f" % a.valorTotal.sum())
print("unidades:", a.unidadeMedida.value_counts().head(10).to_dict(), "| distintas:", a.unidadeMedida.nunique())
print("concentração do valor estimado: 10 maiores itens = %.1f%%" % (100 * a.valorTotal.nlargest(10).sum() / a.valorTotal.sum()))
print("itens com resultado baixado:", int(a.preco_homologado.notna().sum()))
print(a.nlargest(10, "valorTotal")[["numeroItem", "descricao", "quantidade", "unidadeMedida", "valorUnitarioEstimado", "valorTotal"]].to_string(index=False, max_colwidth=60))

# referências de preço disponíveis na data de decisão: BPS (qualquer UF) inserido até DEC, mesmo CATMAT
fr = []
for ano in (2024, 2025, 2026):
    with zipfile.ZipFile(os.path.join(ROOT, "data", "raw", "bps", f"{ano}_csv.zip")) as z:
        fr.append(pd.read_csv(z.open(z.namelist()[0]), sep=";", dtype=str, keep_default_na=False, na_values=[""]))
b = pd.concat(fr, ignore_index=True)
b["ins"] = pd.to_datetime(b.dt_insercao, format="%d/%m/%Y"); b["comp"] = pd.to_datetime(b.dt_compra, format="%d/%m/%Y")
b["preco"] = pd.to_numeric(b.vl_preco_unitario); b["qtd"] = pd.to_numeric(b.qt_medicamento)
print("\nBPS 2024 registros:", (b.ano_compra == "2024").sum(), "| inserção 2024 mín/máx:", b[b.ano_compra == "2024"].ins.min().date(), b[b.ano_compra == "2024"].ins.max().date())
pre = b[b.ins <= DEC]
print(f"BPS inserido até {DEC.date()}: {len(pre)} registros, {pre.cnpj_instituicao.nunique()} instituições, compras {pre.comp.min().date()}..{pre.comp.max().date()}")
# o PNCP de Santa Luzia não traz CATMAT; o código é obtido do registro BPS do mesmo contrato
# (processo 004/2025) casando fornecedor + preço unitário + quantidade. Só a identidade do produto é usada.
sl = b[(b.sg_uf == "PB") & (b.no_municipio == "SANTA LUZIA")]
k = sl[sl.nu_processo_compra == "004/2025"].assign(p=lambda x: x.preco.round(4))
k = k.drop_duplicates(["cnpj_fornecedor", "p", "qtd"]).set_index(["cnpj_fornecedor", "p", "qtd"]).co_catmat
a["catmat"] = [k.get((f, round(p, 4) if pd.notna(p) else None, q)) for f, p, q in zip(a.fornecedor, a.preco_homologado, a.qtd_homologada)]
amb = sl[sl.nu_processo_compra == "004/2025"].assign(p=lambda x: x.preco.round(4)).duplicated(["cnpj_fornecedor", "p", "qtd"], keep=False).sum()
print("CATMAT obtido via BPS (fornecedor+preço+quantidade): %d de %d itens | chaves ambíguas no BPS: %d" % (a.catmat.notna().sum(), len(a), amb))
ref = pre.groupby("co_catmat").agg(n_ref=("preco", "size"), n_ref_pb=("sg_uf", lambda s: (s == "PB").sum()), mediana_ref=("preco", "median"),
                                   unidades_ref=("un_fornecimento", lambda s: "|".join(sorted(s.dropna().unique()))))
a = a.merge(ref, left_on="catmat", right_index=True, how="left")
cov = a.n_ref.notna()
print("itens do PE 04/2025 com ≥1 preço BPS anterior à decisão: %d de %d (%.1f%% do valor estimado)" % (cov.sum(), len(a), 100 * a.valorTotal[cov].sum() / a.valorTotal.sum()))
print("… com ≥5 preços: %d | com preço da PB: %d" % ((a.n_ref >= 5).sum(), (a.n_ref_pb > 0).sum()))
a.to_csv(R("caso_sl_itens_pe04_2025.csv"), index=False)

# BPS da própria Santa Luzia (FMS ou prefeitura)
g = sl.groupby("ano_compra").agg(registros=("preco", "size"), cnpjs=("cnpj_instituicao", lambda s: "|".join(sorted(s.unique()))),
                                 compra_min=("comp", "min"), compra_max=("comp", "max"), insercao_max=("ins", "max"),
                                 catmat=("co_catmat", "nunique"), valor=("vl_preco_total", lambda s: pd.to_numeric(s).sum()))
print("\nBPS Santa Luzia por ano:\n", g.to_string())
print("BPS Santa Luzia inserido até a decisão:", int((sl.ins <= DEC).sum()))
sl.to_csv(R("caso_sl_bps_santa_luzia.csv"), index=False)
print("BPS Santa Luzia por processo:", sl.groupby("nu_processo_compra").agg(n=("preco", "size"), valor=("vl_preco_total", lambda s: round(pd.to_numeric(s).sum(), 2)), data=("dt_compra", "first")).to_dict("index"))
print("valor homologado PE 04/2025 (soma dos resultados): %.2f" % (a.preco_homologado * a.qtd_homologada).sum())

# evolução da necessidade planejada: PE 04/2025 -> PE 25/2025 (nova demanda) -> PE 09/2026, pela descrição normalizada
import re, unicodedata
norm = lambda s: re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower())
ev = []
for nome, pasta in (("PE 01/2024", "09090689000167_2024_1"), ("PE 04/2025", "09090689000167_2025_6"), ("PE 25/2025", "09090689000167_2025_99"), ("PE 09/2026", "09090689000167_2026_26")):
    x = itens(pasta); x["pregao"] = nome; x["chave"] = x.descricao.map(norm); ev.append(x[["pregao", "chave", "descricao", "quantidade", "unidadeMedida", "valorUnitarioEstimado"]])
ev = pd.concat(ev, ignore_index=True)
pv = ev.pivot_table(index="chave", columns="pregao", values="quantidade", aggfunc="sum")
pv.insert(0, "descricao", ev.drop_duplicates("chave").set_index("chave").descricao)
pv.to_csv(R("caso_sl_evolucao_itens.csv"))
k25, kn, k26 = (set(ev[ev.pregao == p].chave) for p in ("PE 04/2025", "PE 25/2025", "PE 09/2026"))
print("\ndescrições: PE04/2025=%d | PE25/2025=%d (iguais a alguma do PE04: %d) | PE09/2026=%d (iguais a alguma do PE04: %d)" % (len(k25), len(kn), len(kn & k25), len(k26), len(k26 & k25)))
c = pv.dropna(subset=["PE 04/2025", "PE 09/2026"])
r = c["PE 09/2026"] / c["PE 04/2025"]
print("quantidade PE09/2026 ÷ PE04/2025 (mesma descrição): n=%d, iguais=%d, menores=%d, maiores=%d, mediana=%.2f" % (len(r), (r == 1).sum(), (r < 1).sum(), (r > 1).sum(), r.median()))
print("soma das quantidades × preço estimado: PE04/2025=%.2f | PE25/2025=%.2f | PE09/2026=%.2f" % tuple((ev[ev.pregao == p].quantidade * ev[ev.pregao == p].valorUnitarioEstimado).sum() for p in ("PE 04/2025", "PE 25/2025", "PE 09/2026")))
k24 = set(ev[ev.pregao == "PE 01/2024"].chave)
c = pv.dropna(subset=["PE 01/2024", "PE 04/2025"]); r = c["PE 04/2025"] / c["PE 01/2024"]
print("PE01/2024: %d descrições; iguais no PE04/2025: %d | quantidade 2025÷2024: iguais=%d, menores=%d, maiores=%d, mediana=%.2f" % (len(k24), len(k24 & k25), (r == 1).sum(), (r < 1).sum(), (r > 1).sum(), r.median()))
print("PE01/2024 valor estimado no PNCP:", ev[ev.pregao == "PE 01/2024"].valorUnitarioEstimado.describe()[["count", "mean", "max"]].to_dict())
