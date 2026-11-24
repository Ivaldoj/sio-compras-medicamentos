"""Etapa 2 — baixa do PNCP a contratação completa: cabeçalho, todos os itens, lista de documentos e atas.
Uso: python -I -X utf8 18_pncp_compra_completa.py <raiz_projeto> <numeroControlePNCP> [<numeroControlePNCP> ...] [--resultados]
Grava em data/raw/pncp/etapa2/<cnpj>_<ano>_<seq>/ (não sobrescreve) e imprime um resumo.
--resultados: baixa também /itens/{n}/resultados de cada item com resultado (1 chamada por item; pausa de 3 s)."""
import json, os, re, sys, time, urllib.request, urllib.error
from collections import Counter

ROOT = sys.argv[1]
ids = [a for a in sys.argv[2:] if not a.startswith("--")]
API = "https://pncp.gov.br/api"


def get(url, dest, tries=5):
    """GET com cache em disco e espera progressiva em HTTP 429. Devolve JSON (ou None em 204/404)."""
    if os.path.exists(dest):
        b = open(dest, "rb").read()
        return json.loads(b) if b else None
    for t in range(1, tries + 1):
        time.sleep(3)  # a API devolve 429 com chamadas rápidas
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "sio-auditoria-academica/1.0"}), timeout=120) as h:
                b = h.read()
            open(dest, "wb").write(b)
            return json.loads(b) if b else None
        except urllib.error.HTTPError as e:
            if e.code == 404:
                open(dest, "wb").write(b""); return None
            if e.code != 429 or t == tries:
                raise
            ra = e.headers.get("Retry-After", "")
            time.sleep(int(ra) if ra.isdigit() else 20 * t)


for nc in ids:
    cnpj, seq, ano = re.match(r"(\d{14})-\d-(\d+)/(\d{4})", nc).groups(); seq = int(seq)
    d = os.path.join(ROOT, "data", "raw", "pncp", "etapa2", f"{cnpj}_{ano}_{seq}"); os.makedirs(d, exist_ok=True)
    base = f"{API}/pncp/v1/orgaos/{cnpj}/compras/{ano}/{seq}"
    c = get(f"{API}/consulta/v1/orgaos/{cnpj}/compras/{ano}/{seq}", os.path.join(d, "compra.json"))
    itens, p = [], 1
    while True:
        pg = get(f"{base}/itens?pagina={p}&tamanhoPagina=500", os.path.join(d, f"itens_p{p}.json")) or []
        itens += pg
        if len(pg) < 500:
            break
        p += 1
    arq = get(f"{base}/arquivos", os.path.join(d, "arquivos.json")) or []
    atas = get(f"{base}/atas", os.path.join(d, "atas.json")) or []
    print(f"\n=== {nc} | {c.get('modalidadeNome')} | SRP={c.get('srp')} | {c.get('situacaoCompraNome')}")
    print("objeto:", (c.get("objetoCompra") or "")[:200].replace("\n", " "))
    print("unidade:", c.get("unidadeOrgao", {}).get("nomeUnidade"), "| processo:", c.get("processo"), "| amparo:", (c.get("amparoLegal") or {}).get("nome"))
    print("abertura:", c.get("dataAberturaProposta"), "| encerramento:", c.get("dataEncerramentoProposta"), "| publicação PNCP:", c.get("dataPublicacaoPncp"))
    print("valor estimado: %s | homologado: %s" % (c.get("valorTotalEstimado"), c.get("valorTotalHomologado")))
    print("itens:", len(itens), "| situação:", dict(Counter(i.get("situacaoCompraItemNome") for i in itens)),
          "| com resultado:", sum(1 for i in itens if i.get("temResultado")), "| material:", sum(1 for i in itens if i.get("materialOuServico") == "M"))
    ex = itens[0] if itens else {}
    print("campos de item:", sorted(ex.keys()))
    print("documentos:", [(a.get("tipoDocumentoNome"), a.get("titulo")) for a in arq])
    print("atas:", len(atas) if isinstance(atas, list) else atas)
    if "--resultados" in sys.argv:
        ok = 0
        for i in itens:
            if i.get("temResultado"):
                r = get(f"{base}/itens/{i['numeroItem']}/resultados", os.path.join(d, f"resultado_item_{i['numeroItem']}.json"))
                ok += bool(r)
        print("resultados baixados:", ok)
