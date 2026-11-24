"""Consulta a posição de estoque de medicamentos (BNAFAR/Hórus) na API de Dados Abertos do Ministério da Saúde.
Uso: python -I -X utf8 16_bnafar_estoque.py <raiz_projeto> <codigo_municipio_ibge6> [anomes_posicao=] [max_paginas=20]
Endpoint: https://apidadosabertos.saude.gov.br/daf/estoque-medicamentos-bnafar-horus (limit/offset)
Grava o bruto em data/raw/ms_api/ e imprime um resumo. Campos de contato do estabelecimento (telefone, e-mail)
não são usados na análise."""
import json, os, sys, time, urllib.request, urllib.error, hashlib, datetime, csv
import pandas as pd
ROOT, mun = sys.argv[1], sys.argv[2]
anomes = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else ""
maxp = int(sys.argv[4]) if len(sys.argv) > 4 else 20
base = "https://apidadosabertos.saude.gov.br/daf/estoque-medicamentos-bnafar-horus"
out = os.path.join(ROOT, "data", "raw", "ms_api", f"bnafar_{mun}_{anomes or 'atual'}.json")
if os.path.exists(out):
    rows = json.load(open(out, encoding="utf8"))
else:
    # offset>=1000 devolve lista vazia (testado em 22/11/2026); por isso usa um limit alto numa única página
    rows, lim = [], 50000
    for p in range(maxp):
        q = f"{base}?codigo_municipio={mun}&limit={lim}&offset={p * lim}" + (f"&anomes_posicao_estoque={anomes}" if anomes else "")
        try:
            with urllib.request.urlopen(urllib.request.Request(q, headers={"User-Agent": "sio-auditoria-academica/1.0"}), timeout=180) as h:
                data = json.loads(h.read()).get("parametros", [])
        except urllib.error.HTTPError as e:
            print("HTTP", e.code, q); break
        rows += data
        if len(data) < lim:
            break
        time.sleep(1)
    json.dump(rows, open(out, "w", encoding="utf8"), ensure_ascii=False)
    with open(os.path.join(ROOT, "reports", "manifest_fontes.csv"), "a", newline="", encoding="utf8") as fh:
        csv.writer(fh).writerow(["MS API BNAFAR/Hórus", f"{base}?codigo_municipio={mun}" + (f"&anomes_posicao_estoque={anomes}" if anomes else ""),
                                 os.path.relpath(out, ROOT), datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                                 os.path.getsize(out), hashlib.sha256(open(out, "rb").read()).hexdigest(),
                                 f"ok; {len(rows)} linhas" + ("; truncado em max_paginas" if len(rows) >= lim else "")])
df = pd.DataFrame(rows)
print(f"município {mun} posição {anomes or 'atual'}: linhas={len(df)}" + (" (TRUNCADO)" if len(df) >= 50000 else ""))
if df.empty:
    sys.exit()
print("datas de posição:", df.data_posicao_estoque.value_counts().head(5).to_dict())
print("estabelecimentos (CNES):", df.codigo_cnes.nunique(), "| razões sociais:", df.razao_social.nunique())
print("sistema de origem:", df.sigla_sistema_origem.value_counts().to_dict())
print("programa:", df.descricao_programa_saude.value_counts().head(6).to_dict())
print("tipo_produto:", df.tipo_produto.value_counts().to_dict())
df["catmat7"] = df.codigo_catmat.str.extract(r"BR0*(\d+)")[0]
print("códigos CATMAT (formato BR...):", df.codigo_catmat.nunique(), "| CATMAT numérico distinto:", df.catmat7.nunique(), "| exemplo:", df.codigo_catmat.iloc[0])
print("quantidade_estoque: soma por produto não é comparável entre unidades; quantis:", df.quantidade_estoque.quantile([.5, .9]).to_dict())
print("lotes vencidos na data de posição: %d" % (pd.to_datetime(df.data_validade.str[:10], errors="coerce") < pd.to_datetime(df.data_posicao_estoque, errors="coerce")).sum())
b = pd.read_parquet(os.path.join(ROOT, "data", "processed", "bps_2025_2026.parquet"))
print("CATMAT do estoque presentes no BPS nacional: %.1f%%" % (100 * df.catmat7.drop_duplicates().isin(set(b.co_catmat)).mean()))
