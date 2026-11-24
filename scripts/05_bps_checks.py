"""Verificações pontuais no BPS processado: maiores valores, instituições PB, distribuição por UF/mês.
Uso: python -I 05_bps_checks.py <raiz_projeto>"""
import os, sys
import pandas as pd
ROOT = sys.argv[1]
b = pd.read_parquet(os.path.join(ROOT, "data", "processed", "bps_2025_2026.parquet"))
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 60)
print("10 maiores vl_preco_total:")
print(b.nlargest(10, "vl_preco_total_num")[["sg_uf", "no_instituicao", "dt_compra", "co_catmat", "no_pdm", "un_fornecimento", "qt_medicamento_num", "vl_preco_unitario_num", "vl_preco_total_num"]].to_string())
top = b.nlargest(100, "vl_preco_total_num").vl_preco_total_num.sum()
print("\nparticipação dos 100 maiores no valor total: %.1f%%" % (100 * top / b.vl_preco_total_num.sum()))
print("mediana vl_preco_total: %.2f" % b.vl_preco_total_num.median())
print("\nUFs presentes:", b.sg_uf.nunique(), sorted(b.sg_uf.unique()))
print("\nRegistros por UF:\n", b.sg_uf.value_counts().to_string())
print("\nRegistros por mes_compra:\n", b.mes_compra.value_counts().sort_index().to_string())
print("\nInstituições por esfera:", b.groupby("ds_esfera").cnpj_instituicao.nunique().to_dict())
print("\nCNPJ com >1 nome:", int((b.groupby("cnpj_instituicao").no_instituicao.nunique() > 1).sum()),
      "| nomes com >1 CNPJ:", int((b.groupby("no_instituicao").cnpj_instituicao.nunique() > 1).sum()))
print(b.groupby("no_instituicao").cnpj_instituicao.nunique().sort_values(ascending=False).head(5).to_string())
pb = b[b.sg_uf == "PB"]
print("\nPB por instituição:\n", pb.groupby(["no_instituicao", "no_municipio", "ds_esfera"]).agg(n=("co_seq_bps", "size"), catmat=("co_catmat", "nunique"), meses=("mes_compra", "nunique"), valor=("vl_preco_total_num", "sum")).sort_values("n", ascending=False).round(0).to_string())
print("\nPB por mês:\n", pb.mes_compra.value_counts().sort_index().to_string())
print("\nPB % medicamentos (classe 6505):", round(100 * (pb.co_classe == "6505").mean(), 1))
# ds_observacao menciona PNCP?
obs = b.ds_observacao.fillna("")
print("\nds_observacao preenchido:", int((obs != "").sum()), "| contém 'PNCP':", int(obs.str.contains("PNCP", case=False).sum()))
print("nu_processo_compra preenchido %:", round(100 * b.nu_processo_compra.notna().mean(), 1), "| nu_ata %:", round(100 * b.nu_ata.notna().mean(), 1))
print("registro_anvisa preenchido %:", round(100 * b.registro_anvisa.notna().mean(), 1))
# exemplo de ambiguidade: mesmo CATMAT, várias unidades
amb = b.groupby("co_catmat").un_fornecimento.unique()
amb = amb[amb.map(len) > 1].head(5)
print("\nexemplos CATMAT com >1 un_fornecimento:\n", amb.to_string())
# medicamentos: dispersão em um CATMAT comum
cat = b[b.co_classe == "6505"].co_catmat.value_counts().index[0]
s = b[(b.co_catmat == cat)]
print("\nCATMAT mais frequente:", cat, s.ds_item.iloc[0][:80])
print(s.groupby("un_fornecimento").vl_preco_unitario_num.describe(percentiles=[.25, .5, .75]).round(4).to_string())
print("JUDICIAL por UF (top5):", b[b.tp_compra == "JUDICIAL"].sg_uf.value_counts().head().to_dict())
