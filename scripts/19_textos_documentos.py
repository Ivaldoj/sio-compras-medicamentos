"""Etapa 2 — extrai texto de PDFs (soltos ou dentro de ZIP, lidos em memória) e procura termos-chave com contexto.
Uso: python -I -X utf8 19_textos_documentos.py <raiz_projeto> <arquivo.pdf|arquivo.zip> [...]
Grava o texto em data/processed/etapa2_textos/<pasta>__<nome>.txt (uma marca '=== página N' por página)."""
import io, os, re, sys, zipfile
from pypdf import PdfReader

ROOT = sys.argv[1]
OUT = os.path.join(ROOT, "data", "processed", "etapa2_textos"); os.makedirs(OUT, exist_ok=True)
TERMOS = r"dota[çc][ãa]o|elemento de despesa|consumo|m[ée]dia|prazo de entrega|entrega|vig[êe]ncia|validade|reajust|garantia|estimad|recursos? or[çc]ament|fonte de recurso|quantitativ|justificativ|parcelad|amostra|registro na anvisa|desabastec|penalidade|multa"


def pdf_text(b):
    r = PdfReader(io.BytesIO(b))
    return "\n".join(f"=== página {i + 1}\n" + (p.extract_text() or "") for i, p in enumerate(r.pages)), len(r.pages)


for f in sys.argv[2:]:
    pasta = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(f))))
    srcs = []
    if f.lower().endswith(".zip"):
        with zipfile.ZipFile(f) as z:
            srcs = [(n, z.read(n)) for n in z.namelist() if n.lower().endswith(".pdf")]
    else:
        srcs = [(os.path.basename(f), open(f, "rb").read())]
    for nome, b in srcs:
        txt, np_ = pdf_text(b)
        dest = os.path.join(OUT, f"{pasta}__{re.sub(r'[^A-Za-z0-9._-]', '_', nome)}.txt")
        open(dest, "w", encoding="utf8").write(txt)
        chars = len(re.sub(r"\s|=== página \d+", "", txt))
        print(f"\n##### {pasta} | {nome} | páginas={np_} | caracteres úteis={chars} -> {os.path.relpath(dest, ROOT)}")
        if chars < 200 * np_:
            print("   AVISO: pouco texto extraível (provável PDF digitalizado).")
        hits = {}
        for m in re.finditer(TERMOS, txt, flags=re.I):
            hits[m.group(0).lower()] = hits.get(m.group(0).lower(), 0) + 1
        print("   ocorrências:", dict(sorted(hits.items(), key=lambda x: -x[1])[:20]))
