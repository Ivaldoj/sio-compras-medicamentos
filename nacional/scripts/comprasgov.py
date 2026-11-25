"""Acesso à API de dados abertos do Compras.gov.br com cache em disco (mesma lógica de scripts/29_comprasgov_precos.py).
shortcut: cópia das funções get/paginas do script 29, que executa código de módulo ao ser importado; unificar se o 29 for refatorado."""
import json, os, time, urllib.error, urllib.request

API = "https://dadosabertos.compras.gov.br"


def get(url, dest, tries=5):
    """GET com cache em disco; 429/5xx com espera crescente (respeita Retry-After); gravação atômica."""
    if os.path.exists(dest):
        try:
            return json.load(open(dest, encoding="utf-8"))
        except ValueError:
            pass
    for t in range(1, tries + 1):
        time.sleep(1)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "sio-pesquisa-academica/1.0"}), timeout=180) as h:
                b = h.read()
            d = json.loads(b)
            open(dest + ".tmp", "wb").write(b); os.replace(dest + ".tmp", dest)
            return d
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {"resultado": [], "totalPaginas": 0}
            if e.code not in (429, 500, 502, 503, 504) or t == tries:
                print("ERRO", e.code, url, flush=True); return None
            ra = e.headers.get("Retry-After", ""); time.sleep(int(ra) if ra.isdigit() else 15 * t)
        except Exception as e:
            if t == tries:
                print("ERRO", e, url, flush=True); return None
            time.sleep(10 * t)


def paginas(url, prefixo):
    out, p = [], 1
    while True:
        d = get(f"{url}&pagina={p}&tamanhoPagina=500", f"{prefixo}_p{p}.json")
        if not d:
            break
        out += d.get("resultado") or []
        if p >= (d.get("totalPaginas") or 0):
            break
        p += 1
    return out
