"""Baixa os itens dos Planos de Contratações Anuais (PCA) de um órgão no PNCP (sequenciais 1..N) e resume os de medicamentos.
Uso: python -I -X utf8 10_pncp_pca.py <raiz_projeto> <cnpj> <ano> [seq_max=30]
Endpoint: https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/pca/{ano}/{seq}/itens?pagina=N&tamanhoPagina=500
Cada órgão publica um PCA por unidade (sequencial). Para após 3 sequenciais vazios seguidos.
Grava data/raw/pncp/pca/pca_<cnpj>_<ano>_<seq>.json (bruto) e reports/pncp_pca_<cnpj>_<ano>_resumo.csv"""
import json, os, sys, time, urllib.request, urllib.error, hashlib, datetime, csv
import pandas as pd

ROOT, cnpj, ano = sys.argv[1], sys.argv[2], sys.argv[3]
seq_max = int(sys.argv[4]) if len(sys.argv) > 4 else 30
D = os.path.join(ROOT, "data", "raw", "pncp", "pca"); os.makedirs(D, exist_ok=True)


def fetch(seq):
    base = f"https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/pca/{ano}/{seq}/itens"
    out = os.path.join(D, f"pca_{cnpj}_{ano}_{seq}.json")
    if os.path.exists(out):
        return json.load(open(out, encoding="utf8"))
    items, page, status = [], 1, "ok"
    while True:
        req = urllib.request.Request(f"{base}?pagina={page}&tamanhoPagina=500", headers={"User-Agent": "sio-auditoria-academica/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                body = r.read()
        except urllib.error.HTTPError as e:
            status = f"HTTP {e.code}"; break
        data = json.loads(body) if body else []
        if not data:
            break
        items += data; page += 1; time.sleep(0.3)
    if items:
        json.dump(items, open(out, "w", encoding="utf8"), ensure_ascii=False)
    with open(os.path.join(ROOT, "reports", "manifest_fontes.csv"), "a", newline="", encoding="utf8") as fh:
        csv.writer(fh).writerow(["PNCP API (PCA)", base, os.path.relpath(out, ROOT) if items else "",
                                 datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                                 os.path.getsize(out) if items else 0,
                                 hashlib.sha256(open(out, "rb").read()).hexdigest() if items else "", f"{status}; {len(items)} itens"])
    return items


allit, empty = [], 0
for s in range(1, seq_max + 1):
    it = fetch(s)
    empty = 0 if it else empty + 1
    allit += it
    if empty >= 3:
        break
df = pd.DataFrame(allit)
print(f"PCA {cnpj} {ano}: itens={len(df)}")
if df.empty:
    sys.exit()
df["valorTotal"] = pd.to_numeric(df.valorTotal, errors="coerce")
df["classe"] = df.classificacaoSuperiorNome.fillna("").str.strip()
print("sequenciais/unidades:", df.sequencialPca.nunique(), "|", df.nomeUnidade.str.strip().unique()[:15])
print("categorias:", df.categoriaItemPcaNome.value_counts().to_dict())
print("catálogo:", df.nomeCatalogo.value_counts(dropna=False).to_dict())
med = df[df.classe.str.contains("MEDICAMENT|DROGAS", case=False)]
print("itens cuja classe superior cita medicamento/drogas:", len(med), "| valor: %.2f | valor total PCA: %.2f" % (med.valorTotal.sum(), df.valorTotal.sum()))
print("classes de material mais frequentes:", df[df.categoriaItemPcaNome == "Material"].classe.value_counts().head(8).to_dict())
if len(med):
    print("exemplos:\n", med[["nomeUnidade", "codigoItem", "descricao", "unidadeFornecimento", "quantidade", "valorUnitario", "valorTotal", "dataDesejada"]].head(8).to_string())
    print("codigoItem preenchido %.1f%% | quantidade>0 %.1f%%" % (100 * med.codigoItem.notna().mean(), 100 * (pd.to_numeric(med.quantidade, errors='coerce') > 0).mean()))
    med.to_csv(os.path.join(ROOT, "data", "samples", f"pncp_pca_{cnpj}_{ano}_medicamentos.csv"), index=False)
df.groupby(["categoriaItemPcaNome", "classe"]).valorTotal.agg(["size", "sum"]).sort_values("sum", ascending=False).to_csv(
    os.path.join(ROOT, "reports", f"pncp_pca_{cnpj}_{ano}_resumo.csv"))
