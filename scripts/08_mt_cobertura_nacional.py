"""Cobertura do Medicamentos Transparentes por UF e coleta, lida direto dos ZIPs CSV (só releases e ten_items, colunas mínimas).
Uso: python -I -X utf8 08_mt_cobertura_nacional.py <raiz_projeto>
Saídas: reports/mt_cobertura_uf.csv (período completo), reports/mt_cobertura_uf_mes.csv (contratações únicas por UF x coleta),
        reports/mt_cobertura_uf_2025T1.csv (coletas 2025-01..03, para comparação com a 1ª rodada)."""
import glob, os, re, sys, zipfile
import pandas as pd

ROOT = sys.argv[1]
REL = ["ocid", "date", "buyer/id", "tender/value/amount"]
rels, items = [], []
for zp in sorted(glob.glob(os.path.join(ROOT, "data", "raw", "transparencia", "*", "*-csv.zip"))):
    uf, mes, ano = re.match(r"(\w+)-(\d+)-(\d+)-csv", os.path.basename(zp)).groups()
    coleta = f"{ano}-{int(mes):02d}"
    with zipfile.ZipFile(zp) as z:
        for m in z.namelist():
            t = re.sub(r"^[a-z]{2}-\d+-\d+(?:-\d+)?-", "", os.path.basename(m))[:-4]
            if t == "releases":
                d = pd.read_csv(z.open(m), dtype=str, usecols=lambda c: c in REL, keep_default_na=False, na_values=[""])
                rels.append(d.assign(uf=uf.upper(), coleta=coleta))
            elif t == "ten_items":
                d = pd.read_csv(z.open(m), dtype=str, usecols=lambda c: c in ("ocid", "tender/items/0/id"), keep_default_na=False, na_values=[""])
                items.append(d.assign(uf=uf.upper(), coleta=coleta))
rel, it = pd.concat(rels, ignore_index=True), pd.concat(items, ignore_index=True)
print("linhas releases:", len(rel), "| ocids únicos:", rel.ocid.nunique(), "| linhas ten_items:", len(it))
print("coletas:", rel.coleta.min(), "->", rel.coleta.max(), "| UFs:", rel.uf.nunique())
rep = rel.groupby("ocid").coleta.nunique()
print("ocids em >1 coleta: %d (%.1f%%) | máx coletas por ocid: %d" % ((rep > 1).sum(), 100 * (rep > 1).mean(), rep.max()))
multi_uf = rel.groupby("ocid").uf.nunique()
print("ocids presentes em arquivos de >1 UF:", int((multi_uf > 1).sum()))


def cobertura(r, i):
    c = r.drop_duplicates("ocid").groupby("uf").agg(contratacoes=("ocid", "size"), compradores=("buyer/id", "nunique"))
    c["itens"] = i.drop_duplicates(["ocid", "tender/items/0/id"]).groupby("uf").size()
    c["coletas"] = r.groupby("uf").coleta.nunique()
    c["linhas_release"] = r.groupby("uf").size()
    return c.sort_values("contratacoes", ascending=False)


full = cobertura(rel, it)
full["pct_contratacoes"] = (100 * full.contratacoes / full.contratacoes.sum()).round(2)
full.to_csv(os.path.join(ROOT, "reports", "mt_cobertura_uf.csv"))
print("\nPeríodo completo:\n", full.to_string())
print("total:", full[["contratacoes", "compradores", "itens", "linhas_release"]].sum().to_dict())
print("posição da PB:", list(full.index).index("PB") + 1, "de", len(full))
cobertura(rel[rel.coleta <= "2025-03"], it[it.coleta <= "2025-03"]).to_csv(os.path.join(ROOT, "reports", "mt_cobertura_uf_2025T1.csv"))
mx = rel.drop_duplicates(["ocid", "coleta"]).pivot_table(index="uf", columns="coleta", values="ocid", aggfunc="count", fill_value=0)
mx.to_csv(os.path.join(ROOT, "reports", "mt_cobertura_uf_mes.csv"))
tot = mx.sum()
print("\ncontratações por coleta (Brasil):\n", tot.to_string())
print("coletas com menos da metade da mediana nacional:", list(tot[tot < tot.median() / 2].index))
zeros = (mx == 0)
print("UF x coleta sem nenhuma contratação:", [(u, c) for u in mx.index for c in mx.columns if zeros.loc[u, c]][:40])
