"""Baixa arquivos públicos, sem sobrescrever, e registra URL, data, tamanho e SHA-256 em reports/manifest_fontes.csv.
Uso:
  python -I 02_download.py url <URL> <destino> <fonte>
  python -I 02_download.py transparencia <listing_merged.json> <UF> <tipo csv|json> [ano]
"""
import csv, datetime, hashlib, json, os, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "reports", "manifest_fontes.csv")
FIELDS = ["fonte", "url", "arquivo_local", "data_download_utc", "bytes", "sha256", "status"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def log(row):
    new = not os.path.exists(MANIFEST)
    with open(MANIFEST, "a", newline="", encoding="utf8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)


def get(url, dest, fonte):
    public_url = url.split("?X-Amz")[0]  # não grava a assinatura temporária
    if os.path.exists(dest):
        print("já existe, não baixado de novo:", dest)
        return
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "sio-auditoria-academica/1.0"})
        with urllib.request.urlopen(req, timeout=300) as r, open(dest + ".part", "wb") as f:
            while b := r.read(1 << 20):
                f.write(b)
        os.replace(dest + ".part", dest)
        log(dict(fonte=fonte, url=public_url, arquivo_local=os.path.relpath(dest, ROOT), data_download_utc=now,
                 bytes=os.path.getsize(dest), sha256=sha256(dest), status="ok"))
        print("ok", dest, os.path.getsize(dest))
    except Exception as e:  # registra a falha e segue
        log(dict(fonte=fonte, url=public_url, arquivo_local="", data_download_utc=now, bytes="", sha256="", status=f"erro: {e}"))
        print("ERRO", public_url, e)


if sys.argv[1] == "url":
    get(sys.argv[2], sys.argv[3], sys.argv[4])
else:
    listing, uf, tipo = sys.argv[2], sys.argv[3].lower(), sys.argv[4]
    ano = int(sys.argv[5]) if len(sys.argv) > 5 else None
    mes_max = int(sys.argv[6]) if len(sys.argv) > 6 else 12
    for r in json.load(open(listing, encoding="utf8"))["response"]["records"]:
        if (uf != "all" and r["uf"] != uf) or (ano and r["ano_coleta"] != ano) or r["mes_coleta"] > mes_max:
            continue
        for f in r["files"]:
            if f["type"] == tipo:
                name = f["url"].split("?")[0].rsplit("/", 1)[1]
                get(f["url"], os.path.join(ROOT, "data", "raw", "transparencia", r["uf"].upper(), name), "Medicamentos Transparentes")
