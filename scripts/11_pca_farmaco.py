"""Mostra os itens de PCA classificados como MATERIAL FARMACOLOGICO (ou medicamento) a partir dos JSON brutos já baixados.
Uso: python -I -X utf8 11_pca_farmaco.py <raiz_projeto> <cnpj> <ano>"""
import glob, json, os, sys
import pandas as pd
ROOT, cnpj, ano = sys.argv[1:4]
fs = glob.glob(os.path.join(ROOT, "data", "raw", "pncp", "pca", f"pca_{cnpj}_{ano}_*.json"))
df = pd.DataFrame([x for f in fs for x in json.load(open(f, encoding="utf8"))])
df["classe"] = df.classificacaoSuperiorNome.fillna("").str.strip()
m = df[df.classe.str.contains("FARMACOL|MEDICAMENT|DROGAS", case=False) | df.descricao.fillna("").str.contains("MEDICAMENT", case=False)].copy()
m["descricao"] = m.descricao.str.strip().str[:90]
pd.set_option("display.width", 300); pd.set_option("display.max_colwidth", 90)
print("itens:", len(m), "| valor total: %.2f" % pd.to_numeric(m.valorTotal).sum(), "| valorOrcamentoExercicio: %.2f" % pd.to_numeric(m.valorOrcamentoExercicio).sum())
print(m[["nomeUnidade", "classe", "codigoItem", "descricao", "unidadeFornecimento", "quantidade", "valorUnitario", "valorTotal", "dataDesejada"]].to_string())
m.to_csv(os.path.join(ROOT, "data", "samples", f"pncp_pca_{cnpj}_{ano}_farmacologico.csv"), index=False)
