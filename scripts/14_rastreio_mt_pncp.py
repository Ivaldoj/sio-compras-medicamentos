"""Teste de rastreabilidade Medicamentos Transparentes -> PNCP em amostra aleatória (semente fixa).
Uso: python -I -X utf8 14_rastreio_mt_pncp.py <raiz_projeto> [n=20]
O campo `id` do MT tem o formato do numeroControlePNCP: <cnpj>-1-<sequencial>/<ano>.
Consulta https://pncp.gov.br/api/consulta/v1/orgaos/{cnpj}/compras/{ano}/{seq} e compara órgão e valor estimado."""
import json, os, re, sys, time, urllib.request, urllib.error
import pandas as pd


def fetch(url, tries=5):
    """GET com espera progressiva em HTTP 429 (respeita Retry-After quando numérico). Devolve (corpo, tentativas)."""
    for t in range(1, tries + 1):
        time.sleep(3)  # a API devolve HTTP 429 com chamadas rápidas
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "sio-auditoria-academica/1.0"}), timeout=60) as h:
                return h.read(), t
        except urllib.error.HTTPError as e:
            if e.code != 429 or t == tries:
                raise
            ra = e.headers.get("Retry-After", "")
            wait = int(ra) if ra.isdigit() else 20 * t
            print(f"429 em {url} — tentativa {t}, aguardando {wait}s", flush=True)
            time.sleep(wait)
ROOT = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
rel = pd.read_parquet(os.path.join(ROOT, "data", "processed", "mt_releases_PB.parquet"))
# usa a coleta mais recente de cada ocid (o valor pode mudar entre coletas)
rel = rel.sort_values("coleta").drop_duplicates("ocid", keep="last").sample(n, random_state=42)
out, res = os.path.join(ROOT, "data", "raw", "pncp", "rastreio"), []
os.makedirs(out, exist_ok=True)
for _, r in rel.iterrows():
    cnpj, seq, ano = re.match(r"(\d{14})-\d-(\d+)/(\d{4})", r["id"]).groups()
    url = f"https://pncp.gov.br/api/consulta/v1/orgaos/{cnpj}/compras/{ano}/{int(seq)}"
    cache = os.path.join(out, f"{cnpj}_{ano}_{int(seq)}.json")
    try:
        if os.path.exists(cache):
            p, st = json.loads(open(cache, "rb").read()), "ok (cache)"
        else:
            body, t = fetch(url)
            open(cache, "wb").write(body)
            p, st = json.loads(body), f"ok ({t} tentativa(s))"
    except Exception as e:
        p, st = {}, f"erro: {e}"
    est_mt = float(r["tender/value/amount"]) if pd.notna(r["tender/value/amount"]) else None
    est_p = p.get("valorTotalEstimado")
    res.append(dict(ocid=r.ocid, numeroControlePNCP=r["id"], coleta=r.coleta, status=st,
                    orgao_igual=p.get("orgaoEntidade", {}).get("cnpj") == cnpj if p else None,
                    valor_estimado_mt=est_mt, valor_estimado_pncp=est_p, valor_homologado_pncp=p.get("valorTotalHomologado"),
                    valor_igual=(est_mt is not None and est_p is not None and abs(est_mt - est_p) < 0.01),
                    situacao_pncp=p.get("situacaoCompraNome"), data_publicacao_pncp=p.get("dataPublicacaoPncp"),
                    data_atualizacao_pncp=p.get("dataAtualizacaoGlobal") or p.get("dataAtualizacao")))
    time.sleep(0.3)
df = pd.DataFrame(res)
df.to_csv(os.path.join(ROOT, "reports", "rastreio_mt_pncp_amostra.csv"), index=False)
print(df[["numeroControlePNCP", "status", "orgao_igual", "valor_estimado_mt", "valor_estimado_pncp", "valor_igual", "situacao_pncp"]].to_string())
print("\nencontrados:", int(df.status.str.startswith("ok").sum()), "de", len(df), "| órgão igual:", int((df.orgao_igual == True).sum()), "| valor estimado igual:", int(df.valor_igual.sum()))

