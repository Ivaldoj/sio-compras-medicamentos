"""Etapa 2 — separa os dados do caso Santa Luzia/PB em (a) informação disponível na data de decisão e
(b) resultados posteriores reservados à avaliação, para evitar vazamento de informação futura.
Uso: python -I -X utf8 22_caso_pacotes_decisao.py <raiz_projeto> [data_decisao=2025-01-29]
Requer as saídas dos scripts 20 e 21. Grava em data/processed/caso_santa_luzia/{pre_decisao,reservado_avaliacao}/."""
import os, re, sys, unicodedata
import pandas as pd

ROOT = sys.argv[1]
DEC = sys.argv[2] if len(sys.argv) > 2 else "2025-01-29"
R = lambda f: os.path.join(ROOT, "reports", f)
OUT = os.path.join(ROOT, "data", "processed", "caso_santa_luzia")
PRE, POS = os.path.join(OUT, "pre_decisao"), os.path.join(OUT, "reservado_avaliacao")
os.makedirs(PRE, exist_ok=True); os.makedirs(POS, exist_ok=True)
norm = lambda s: re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower())

a = pd.read_csv(R("caso_sl_itens_pe04_2025.csv"), dtype={"catmat": str})
ev = pd.read_csv(R("caso_sl_evolucao_itens.csv"))
q24 = ev.set_index("chave")["PE 01/2024"] if "PE 01/2024" in ev else pd.Series(dtype=float)
a["chave"] = a.descricao.map(norm)

# (a) necessidade e referências conhecidas na data de decisão
pre = pd.DataFrame({
    "item": a.numeroItem, "descricao": a.descricao, "unidade": a.unidadeMedida, "quantidade_estimada_TR": a.quantidade,
    "preco_unitario_estimado_orgao": a.valorUnitarioEstimado, "valor_total_estimado_orgao": a.valorTotal,
    "catmat_identificado": a.catmat,
    "bps_n_precos_ate_decisao": a.n_ref, "bps_n_precos_PB_ate_decisao": a.n_ref_pb,
    "bps_mediana_preco_ate_decisao": a.mediana_ref, "bps_unidades_fornecimento": a.unidades_ref,
    "quantidade_no_PE01_2024_mesma_descricao": a.chave.map(q24),
})
pre.to_csv(os.path.join(PRE, "itens_necessidade_e_referencias.csv"), index=False)
an = pd.read_csv(R("caso_sl_farmaco_anual.csv"), dtype={"ano": str})
an[an.ano == "2024"].to_csv(os.path.join(PRE, "execucao_farmaco_2024_tcepb.csv"), index=False)
lic = pd.read_csv(R("caso_sl_farmaco_por_licitacao.csv"), dtype={"ano": str})
lic[lic.ano == "2024"].to_csv(os.path.join(PRE, "execucao_farmaco_2024_por_licitacao.csv"), index=False)
mes = pd.read_csv(R("caso_sl_farmaco_mensal.csv"), dtype={"ano": str})
mes[mes.ano == "2024"].to_csv(os.path.join(PRE, "execucao_farmaco_2024_mensal.csv"), index=False)

# (b) resultados posteriores: NÃO entregar ao agente decisor
pd.DataFrame({"item": a.numeroItem, "descricao": a.descricao, "quantidade_homologada": a.qtd_homologada,
              "preco_unitario_homologado": a.preco_homologado, "cnpj_fornecedor": a.fornecedor, "data_resultado": a.data_resultado}
             ).to_csv(os.path.join(POS, "resultado_homologado_PE04_2025.csv"), index=False)
for f in ("caso_sl_execucao_contratos.csv", "caso_sl_evolucao_itens.csv"):
    pd.read_csv(R(f)).to_csv(os.path.join(POS, f.replace("caso_sl_", "")), index=False)
for f in ("caso_sl_farmaco_anual.csv", "caso_sl_farmaco_por_licitacao.csv", "caso_sl_farmaco_mensal.csv"):
    x = pd.read_csv(R(f), dtype={"ano": str}); x[x.ano != "2024"].to_csv(os.path.join(POS, f.replace("caso_sl_", "").replace(".csv", "_2025_2026.csv")), index=False)

# autoverificação: nenhuma coluna de resultado no pacote pré-decisão
proib = {"preco_homologado", "qtd_homologada", "fornecedor", "data_resultado", "valor_homologado"}
assert not (proib & set(pre.columns)), "vazamento de coluna de resultado"
assert pre.quantidade_estimada_TR.notna().all() and len(pre) == 334
print("pré-decisão:", sorted(os.listdir(PRE)))
print("reservado:", sorted(os.listdir(POS)))
print("itens:", len(pre), "| com CATMAT: %d | com preço BPS até a decisão: %d | com quantidade 2024: %d" % (
    pre.catmat_identificado.notna().sum(), pre.bps_n_precos_ate_decisao.notna().sum(), pre.quantidade_no_PE01_2024_mesma_descricao.notna().sum()))
print("execução farmacológica 2024:", an[an.ano == "2024"].to_dict("records"))
