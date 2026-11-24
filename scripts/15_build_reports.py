"""Consolida relatórios estruturados: inventário de arquivos brutos (com SHA-256), perfil de colunas unificado,
estatísticas por base e sobreposição de CATMAT entre bases.
Uso: python -I -X utf8 15_build_reports.py <raiz_projeto>"""
import glob, hashlib, os, sys, datetime
import pandas as pd
ROOT = sys.argv[1]
R = lambda *p: os.path.join(ROOT, *p)

# inventário de todos os arquivos em data/raw
rows = []
for f in sorted(glob.glob(R("data", "raw", "**", "*"), recursive=True)):
    if os.path.isfile(f):
        h = hashlib.sha256(open(f, "rb").read()).hexdigest()
        rel = os.path.relpath(f, ROOT).replace("\\", "/")
        fonte = ("BPS/MS" if "/bps/" in rel else "Medicamentos Transparentes" if "/transparencia/" in rel else
                 "PNCP" if "/pncp/" in rel else "TCE-PB" if "/tcepb/" in rel else "CMED/Anvisa" if "cmed" in rel else "Complementar")
        rows.append(dict(fonte=fonte, arquivo=rel, bytes=os.path.getsize(f), sha256=h,
                         modificado_local=datetime.datetime.fromtimestamp(os.path.getmtime(f)).isoformat(timespec="seconds")))
inv = pd.DataFrame(rows)
inv.to_csv(R("reports", "inventario_arquivos.csv"), index=False)
print("arquivos brutos:", len(inv), "| bytes:", inv.bytes.sum()); print(inv.groupby("fonte").agg(arquivos=("arquivo", "size"), bytes=("bytes", "sum")).to_string())

# perfil de colunas unificado
pb = pd.read_csv(R("reports", "perfil_colunas_bps.csv")); pm = pd.read_csv(R("reports", "perfil_colunas_transparencia.csv"))
pb["tabela"] = pb.pop("arquivo")
pd.concat([pb, pm], ignore_index=True).to_csv(R("reports", "perfil_colunas.csv"), index=False)

# estatísticas
b = pd.read_parquet(R("data", "processed", "bps_2025_2026.parquet"))
rel = pd.read_parquet(R("data", "processed", "mt_releases_PB.parquet")).drop_duplicates("ocid")
it = pd.read_parquet(R("data", "processed", "mt_itens_unicos_PB.parquet"))
ai = pd.read_parquet(R("data", "processed", "mt_awa_items_PB.parquet")).drop_duplicates(["ocid", "awards/id", "awards/items/id"])
st = []
add = lambda base, recorte, metrica, valor, obs="": st.append(dict(base=base, recorte=recorte, metrica=metrica, valor=valor, observacao=obs))
for arq, g in b.groupby("arquivo"):
    add("BPS", arq, "registros", len(g)); add("BPS", arq, "instituicoes_cnpj", g.cnpj_instituicao.nunique())
    add("BPS", arq, "ufs", g.sg_uf.nunique()); add("BPS", arq, "catmat_distintos", g.co_catmat.nunique())
    add("BPS", arq, "pct_classe_6505_medicamentos", round(100 * (g.co_classe == "6505").mean(), 2))
    add("BPS", arq, "soma_vl_preco_total_RS", round(g.vl_preco_total_num.sum(), 2), "dominada por outliers; ver docs/03")
    add("BPS", arq, "mediana_vl_preco_total_RS", round(g.vl_preco_total_num.median(), 2))
    add("BPS", arq, "dt_compra_min", str(pd.to_datetime(g.dt_compra, format="%d/%m/%Y").min().date()))
    add("BPS", arq, "dt_compra_max", str(pd.to_datetime(g.dt_compra, format="%d/%m/%Y").max().date()))
g = b[b.sg_uf == "PB"]
add("BPS", "PB 2025-2026", "registros", len(g)); add("BPS", "PB 2025-2026", "instituicoes_cnpj", g.cnpj_instituicao.nunique())
add("BPS", "PB 2025-2026", "catmat_distintos", g.co_catmat.nunique())
add("MT", "PB coletas 2025-01..2026-09", "linhas_releases", len(pd.read_parquet(R("data", "processed", "mt_releases_PB.parquet"))))
add("MT", "PB coletas 2025-01..2026-09", "contratacoes_ocid_unicas", len(rel))
add("MT", "PB coletas 2025-01..2026-09", "compradores", rel["buyer/id"].nunique())
add("MT", "PB coletas 2025-01..2026-09", "itens_licitacao_unicos", len(it))
add("MT", "PB coletas 2025-01..2026-09", "itens_adjudicados_unicos", len(ai))
add("MT", "PB coletas 2025-01..2026-09", "catmat_distintos", it["tender/items/classification/id"].nunique())
add("MT", "PB coletas 2025-01..2026-09", "fornecedores", pd.read_parquet(R("data", "processed", "mt_awa_suppliers_PB.parquet"))["awards/suppliers/id"].nunique())
# MT nacional (saída do script 08, coletas 2025-01..2026-09)
cov = pd.read_csv(R("reports", "mt_cobertura_uf.csv"), index_col=0)
add("MT", "Brasil coletas 2025-01..2026-09", "contratacoes_ocid_unicas", int(cov.contratacoes.sum()))
add("MT", "Brasil coletas 2025-01..2026-09", "itens_licitacao_unicos", int(cov.itens.sum()))
add("MT", "Brasil coletas 2025-01..2026-09", "compradores_soma_por_UF", int(cov.compradores.sum()), "um mesmo CNPJ pode contar em mais de uma UF")
add("MT", "Brasil coletas 2025-01..2026-09", "posicao_PB_em_contratacoes", list(cov.index).index("PB") + 1, f"de {len(cov)} códigos de UF (inclui EX)")
# sobreposição de CATMAT
cm, cb, cbp = set(it["tender/items/classification/id"]), set(b.co_catmat), set(g.co_catmat)
add("Integração", "MT-PB x BPS nacional", "catmat_MT_PB_presentes_no_BPS_pct", round(100 * len(cm & cb) / len(cm), 1), f"{len(cm & cb)} de {len(cm)}")
add("Integração", "MT-PB x BPS-PB", "catmat_MT_PB_presentes_no_BPS_PB_pct", round(100 * len(cm & cbp) / len(cm), 1), f"{len(cm & cbp)} de {len(cm)}")
it["v"] = pd.to_numeric(it["tender/items/unit/value/amount"], errors="coerce") * pd.to_numeric(it["tender/items/quantity"], errors="coerce")
add("Integração", "MT-PB x BPS nacional", "itens_MT_PB_com_catmat_no_BPS_pct", round(100 * it["tender/items/classification/id"].isin(cb).mean(), 1))
s = pd.DataFrame(st); s.to_csv(R("reports", "estatisticas_bases.csv"), index=False); print(s.to_string())
