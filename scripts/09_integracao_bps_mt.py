"""Testes reais de integração BPS x Medicamentos Transparentes (PB, 2025-2026).
Uso: python -I -X utf8 09_integracao_bps_mt.py <raiz_projeto>
Níveis de correspondência testados:
  N1 órgão: CNPJ normalizado (14 dígitos)
  N2 produto: CNPJ + CATMAT
  N3 transação provável: CNPJ + CATMAT + CNPJ fornecedor + preço unitário igual (±0,5%)
  N4 transação confirmada: N3 + número do processo idêntico (normalizado)"""
import os, re, sys
import pandas as pd
ROOT = sys.argv[1]
P = lambda f: pd.read_parquet(os.path.join(ROOT, "data", "processed", f))
cnpj = lambda s: s.fillna("").str.replace(r"\D", "", regex=True).str.zfill(14)
norm = lambda s: s.fillna("").str.upper().str.replace(r"[^0-9A-Z]", "", regex=True).str.lstrip("0")

bps = P("bps_2025_2026.parquet"); bps = bps[bps.sg_uf == "PB"].copy()
bps["cnpj"] = cnpj(bps.cnpj_instituicao); bps["forn"] = cnpj(bps.cnpj_fornecedor); bps["proc"] = norm(bps.nu_processo_compra)
rel = P("mt_releases_PB.parquet").drop_duplicates("ocid")
it = P("mt_itens_unicos_PB.parquet")
ai = P("mt_awa_items_PB.parquet").drop_duplicates(["ocid", "awards/id", "awards/items/id"])
sup = P("mt_awa_suppliers_PB.parquet").drop_duplicates(["ocid", "awards/id"])
rel["cnpj"] = cnpj(rel["buyer/id"].str.replace("BR-CNPJ-", "")); rel["proc"] = norm(rel["tender/id"])
print("formato buyer/id exemplo:", rel["buyer/id"].iloc[0], "-> normalizado", rel.cnpj.iloc[0])

# N1 órgãos
ob, om = set(bps.cnpj), set(rel.cnpj)
print(f"\nN1 órgãos PB: BPS={len(ob)} MT={len(om)} em ambos={len(ob & om)}")
both = sorted(ob & om)
tab = pd.DataFrame({"cnpj": both})
tab["nome_bps"] = tab.cnpj.map(bps.groupby("cnpj").no_instituicao.first())
tab["nome_mt"] = tab.cnpj.map(rel.groupby("cnpj")["buyer/name"].first())
tab["reg_bps"] = tab.cnpj.map(bps.groupby("cnpj").size())
tab["contratacoes_mt"] = tab.cnpj.map(rel.groupby("cnpj").size())
print(tab.to_string())
print("%% registros BPS-PB cujo órgão aparece no MT-PB: %.1f%%" % (100 * bps.cnpj.isin(om).mean()))

# itens adjudicados do MT com comprador, fornecedor e CATMAT
a = ai.merge(sup[["ocid", "awards/id", "awards/suppliers/id"]], on=["ocid", "awards/id"], how="left")
a = a.merge(it[["ocid", "tender/items/id", "tender/items/classification/id"]], left_on=["ocid", "awards/items/id"], right_on=["ocid", "tender/items/id"], how="left")
a = a.merge(rel[["ocid", "cnpj", "proc"]], on="ocid", how="left")
a["forn"] = cnpj(a["awards/suppliers/id"].str.replace("BR-CNPJ-", ""))
a["preco"] = pd.to_numeric(a["awards/items/unit/value/amount"], errors="coerce")
a["catmat"] = a["tender/items/classification/id"]
print("\nitens adjudicados MT-PB com CATMAT:", int(a.catmat.notna().sum()), "de", len(a))

# N2 produto
k2 = bps.merge(a[["cnpj", "catmat"]].drop_duplicates(), left_on=["cnpj", "co_catmat"], right_on=["cnpj", "catmat"], how="inner")
print("N2 (CNPJ+CATMAT): registros BPS-PB com par em MT: %d (%.1f%%)" % (len(k2.co_seq_bps.unique()), 100 * len(k2.co_seq_bps.unique()) / len(bps)))

# N3/N4 transação
m = bps.merge(a, left_on=["cnpj", "co_catmat", "forn"], right_on=["cnpj", "catmat", "forn"], how="inner", suffixes=("_bps", "_mt"))
m = m[(m.vl_preco_unitario_num - m.preco).abs() <= 0.005 * m.preco]
n3 = m.co_seq_bps.nunique()
print("N3 (CNPJ+CATMAT+fornecedor+preço±0,5%%): %d registros BPS (%.1f%%), pares=%d" % (n3, 100 * n3 / len(bps), len(m)))
m["mesmo_proc"] = (m.proc_bps == m.proc_mt) | m.apply(lambda r: r.proc_bps != "" and (r.proc_bps in r.proc_mt or r.proc_mt in r.proc_bps), axis=1)
n4 = m[m.mesmo_proc].co_seq_bps.nunique()
print("N4 (N3 + processo compatível): %d registros BPS (%.1f%%)" % (n4, 100 * n4 / len(bps)))
amb = m.groupby("co_seq_bps").ocid.nunique()
print("registros BPS N3 associados a >1 contratação MT (ambíguos):", int((amb > 1).sum()))
qeq = (m.qt_medicamento_num == pd.to_numeric(m["awards/items/quantity"], errors="coerce")).mean()
print("N3 com mesma quantidade: %.1f%%" % (100 * qeq))
cols = ["co_seq_bps", "no_instituicao", "dt_compra", "co_catmat", "vl_preco_unitario_num", "qt_medicamento_num", "nu_processo_compra", "ocid", "id", "proc_mt", "awards/items/quantity", "mesmo_proc"]
m[cols].head(15).to_csv(os.path.join(ROOT, "reports", "integracao_exemplos_bps_mt_pb.csv"), index=False)
print(m[cols].head(8).to_string())
# N1b: município (o BPS usa muito o CNPJ do Fundo Municipal de Saúde; o PNCP/MT, o do Município/Prefeitura)
import unicodedata
nm = lambda s: s.fillna("").map(lambda x: unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode().upper().strip())
par = P("mt_parties_PB.parquet")
par = par[par["parties/roles"].fillna("").str.contains("buyer")].drop_duplicates("ocid")
mun_mt = set(nm(par["parties/address/locality"])); mun_b = set(nm(bps.no_municipio))
print("\nN1b municípios PB: BPS=%d MT=%d em ambos=%d" % (len(mun_b), len(mun_mt), len(mun_b & mun_mt)))
print("%% registros BPS-PB cujo município tem comprador no MT-PB: %.1f%%" % (100 * nm(bps.no_municipio).isin(mun_mt).mean()))
print("municípios BPS ausentes no MT:", sorted(mun_b - mun_mt))
a["mun"] = a.ocid.map(dict(zip(par.ocid, nm(par["parties/address/locality"]))))
bps["mun"] = nm(bps.no_municipio)
m3b = bps.merge(a, left_on=["mun", "co_catmat", "forn"], right_on=["mun", "catmat", "forn"], how="inner", suffixes=("_bps", "_mt"))
m3b = m3b[(m3b.vl_preco_unitario_num - m3b.preco).abs() <= 0.005 * m3b.preco]
n3b = m3b.co_seq_bps.nunique()
print("N3b (município+CATMAT+fornecedor+preço±0,5%%): %d registros BPS (%.1f%%) | ambíguos (>1 ocid): %d" % (
    n3b, 100 * n3b / len(bps), int((m3b.groupby("co_seq_bps").ocid.nunique() > 1).sum())))
print("N3b por órgão BPS:", m3b.drop_duplicates("co_seq_bps").no_instituicao.value_counts().to_dict())
pd.DataFrame([dict(nivel="N1 órgão (CNPJ)", registros_bps_pb=len(bps), correspondentes=int(bps.cnpj.isin(om).sum())),
              dict(nivel="N2 CNPJ+CATMAT", registros_bps_pb=len(bps), correspondentes=len(k2.co_seq_bps.unique())),
              dict(nivel="N3 +fornecedor+preço", registros_bps_pb=len(bps), correspondentes=n3),
              dict(nivel="N3b município+CATMAT+fornecedor+preço", registros_bps_pb=len(bps), correspondentes=n3b),
              dict(nivel="N4 +processo", registros_bps_pb=len(bps), correspondentes=n4)]).to_csv(
    os.path.join(ROOT, "reports", "integracao_bps_mt_pb.csv"), index=False)
