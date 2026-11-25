"""Leitor mínimo das respostas TabNet (HTML com bloco CSV ';' dentro de <PRE>)."""
import html, re
import pandas as pd


def ler(caminho):
    t = open(caminho, encoding="latin-1").read()
    t = html.unescape(re.sub(r"<[^>]+>", "\n", t))
    linhas = [l.strip() for l in t.splitlines() if l.strip().startswith('"')]
    cab = [c.strip('"') for c in linhas[0].split(";")]
    reg = []
    for l in linhas[1:]:
        p = l.split(";")
        if len(p) != len(cab):
            continue
        reg.append(p)
    d = pd.DataFrame(reg, columns=cab)
    d["proc"] = d[cab[0]].str.strip('"').str[:10]
    for c in cab[1:]:
        d[c] = pd.to_numeric(d[c].str.replace(".", "", regex=False).str.replace(",", ".", regex=False).replace("-", "0"), errors="coerce")
    return d


def por_ap(d, cesta, col):
    m = {p: a for a, ps in zip(cesta.ap_id, cesta.procedimentos_sigtap) for p in ps.split("|")}
    d = d.assign(ap_id=d.proc.map(m))
    return d[d.ap_id.notna()].groupby("ap_id")[col].sum()
