"""Despesa municipal com material farmacológico (TCE-PB/SAGRES) e teste de vínculo com o BPS por CNPJ do fornecedor.
Uso: python -I -X utf8 12_tcepb_despesas.py <raiz_projeto> <zip_despesas> <nome_municipio_BPS>
Filtro de medicamentos: elemento de despesa 30 (Material de Consumo) e subelemento "MATERIAL FARMACOLÓGICO".
Observação: o subelemento agrega medicamentos e outros itens farmacológicos; não identifica o produto."""
import os, sys, zipfile
import pandas as pd
ROOT, zp, mun = sys.argv[1:4]
with zipfile.ZipFile(zp) as z:
    d = pd.read_csv(z.open(z.namelist()[0]), sep=";", dtype=str, encoding="utf-8-sig")
for c in ("valor_empenhado", "valor_liquidado", "valor_pago"):
    d[c] = pd.to_numeric(d[c].str.replace(".", "", regex=False).str.replace(",", ".", regex=False), errors="coerce")
print("empenhos:", len(d), "| período:", d.data_empenho.min(), "->", d.data_empenho.max())
print("unidades gestoras:", d.descricao_unidade_gestora.unique()[:6])
e30 = d[d.codigo_elemento_despesa == "30"]
print("\nsubelementos do elemento 30 (código exibição -> histórico mais comum):")
print(e30.groupby("codigo_subelemento_exibicao").agg(n=("numero_empenho", "size"), empenhado=("valor_empenhado", "sum")).round(2).to_string())
# o campo "codigo_subelemento_exibicao" traz o nome do subelemento; o código numérico fica em codigo_subelemento
farm = e30[e30.codigo_subelemento_exibicao.str.contains("FARMACOL", case=False, na=False)]
print("codigo_subelemento do material farmacológico:", farm.codigo_subelemento.unique())
print("\nhistóricos de exemplo do subelemento 09:", farm.historico.str[:100].head(3).tolist())
print("material farmacológico: empenhos=%d | empenhado=%.2f | liquidado=%.2f | pago=%.2f" % (len(farm), farm.valor_empenhado.sum(), farm.valor_liquidado.sum(), farm.valor_pago.sum()))
print("por função:", farm.funcao.value_counts().to_dict())
print("fontes de recurso:", farm.descricao_fonte_recurso.value_counts().head(6).to_dict())
farm.groupby("mes")[["valor_empenhado", "valor_liquidado", "valor_pago"]].sum().round(2).to_csv(os.path.join(ROOT, "reports", f"tcepb_farmaco_mensal_{mun.replace(' ', '_')}.csv"))
print(farm.groupby("mes")[["valor_empenhado", "valor_liquidado", "valor_pago"]].sum().round(0).to_string())
cred = farm.groupby(["cpf_cnpj", "nome_credor"]).valor_empenhado.sum().sort_values(ascending=False)
print("\ncredores (top 8):\n", cred.head(8).round(0).to_string())

b = pd.read_parquet(os.path.join(ROOT, "data", "processed", "bps_2025_2026.parquet"))
b = b[(b.sg_uf == "PB") & (b.no_municipio == mun.upper()) & (b.ano_compra == "2025")]
fb = set(b.cnpj_fornecedor.str.zfill(14)); ft = set(farm.cpf_cnpj.str.zfill(14))
print(f"\nBPS {mun} 2025: registros={len(b)}, valor=%.2f, fornecedores={len(fb)}" % b.vl_preco_total_num.sum())
print("fornecedores BPS também credores de material farmacológico no TCE-PB:", len(fb & ft), "de", len(fb))
lic_b = set(b.nu_processo_compra.str.replace(r"\D", "", regex=True).str.lstrip("0"))
lic_t = set(farm.numero_licitacao.str.replace(r"\D", "", regex=True).str.lstrip("0"))
print("números de processo BPS:", sorted(lic_b)[:8], "| números de licitação TCE (farmaco):", sorted(lic_t)[:8], "| em comum:", sorted(lic_b & lic_t))
