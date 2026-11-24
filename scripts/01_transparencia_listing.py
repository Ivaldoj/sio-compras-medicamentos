"""Inventário dos arquivos do Medicamentos Transparentes a partir do JSON da API /dados-abertos.
Uso: python -I 01_transparencia_listing.py <listing_all.json> <saida_csv>
Gera um CSV (uf, ano, mes, data_publicacao, tipo, url_sem_assinatura) e imprime a matriz de cobertura.
As URLs S3 são pré-assinadas (expiram em 24h); a assinatura é removida antes de gravar."""
import json, sys, csv, collections
recs = json.load(open(sys.argv[1], encoding="utf8"))["response"]
print("count informado pela API:", recs.get("count"), "| registros recebidos:", len(recs["records"]))
rows = []
for r in recs["records"]:
    for f in r["files"]:
        rows.append(dict(id=r["id"], uf=r["uf"].upper(), ano_coleta=r["ano_coleta"], mes_coleta=r["mes_coleta"],
                         data_coleta=r["data_coleta"], data_publicacao=r["data_publicacao"], data_insercao=r["data_insercao"],
                         tipo=f["type"], url=f["url"].split("?")[0]))
with open(sys.argv[2], "w", newline="", encoding="utf8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)
cov = collections.defaultdict(set)
for r in recs["records"]:
    cov[r["uf"].upper()].add((r["ano_coleta"], r["mes_coleta"]))
periods = sorted({p for s in cov.values() for p in s})
print("períodos distintos:", len(periods), periods[0], "->", periods[-1])
print("UFs:", len(cov))
for uf in sorted(cov):
    miss = [f"{a}-{m:02d}" for a, m in periods if (a, m) not in cov[uf]]
    print(uf, len(cov[uf]), "faltando:", miss)
dup = collections.Counter((r["uf"], r["ano_coleta"], r["mes_coleta"]) for r in recs["records"])
print("UF/mês repetidos na listagem:", [k for k, v in dup.items() if v > 1])
