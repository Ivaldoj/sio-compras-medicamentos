"""Carrega todas as tabelas OCDS achatadas (CSV) dos ZIPs do Medicamentos Transparentes de uma ou mais UFs.
Uso: python -I 06_profile_transparencia.py <raiz_projeto> <UF>[,<UF>...] [--perfil]
Grava data/processed/mt_<tabela>_<UFs>.parquet e, com --perfil, reports/perfil_colunas_transparencia.csv"""
import glob, os, re, sys, zipfile
import pandas as pd

ROOT, ufs = sys.argv[1], sys.argv[2].upper().split(",")
tables = {}
for uf in ufs:
    for zp in sorted(glob.glob(os.path.join(ROOT, "data", "raw", "transparencia", uf, "*-csv.zip"))):
        arq = os.path.basename(zp)
        uf_, mes, ano = re.match(r"(\w+)-(\d+)-(\d+)-csv", arq).groups()
        with zipfile.ZipFile(zp) as z:
            for m in z.namelist():
                if not m.endswith(".csv"):
                    continue
                # UFs grandes vêm em partes: "sp-1-2025-1/sp-1-2025-1-awards.csv"
                t = re.sub(r"^[a-z]{2}-\d+-\d+(?:-\d+)?-", "", os.path.basename(m))[:-4]
                df = pd.read_csv(z.open(m), dtype=str, encoding="utf-8", keep_default_na=False, na_values=[""])
                df.insert(0, "arquivo", arq); df.insert(1, "uf_arquivo", uf_.upper())
                df.insert(2, "coleta", f"{ano}-{int(mes):02d}")
                tables.setdefault(t, []).append(df)
tag = "_".join(ufs) if len(ufs) < 4 else f"{len(ufs)}ufs"
prof = []
for t, fr in tables.items():
    df = pd.concat(fr, ignore_index=True)
    # nomes de coluna "x/0/y" -> "x/y" (o índice 0 é artefato do achatamento OCDS)
    df.columns = [c.replace("/0/", "/") for c in df.columns]
    df.to_parquet(os.path.join(ROOT, "data", "processed", f"mt_{t}_{tag}.parquet"), index=False)
    print(f"{t}: {len(df)} linhas, {df.shape[1]} colunas, ocid distintos={df.ocid.nunique()}")
    for c in df.columns[3:]:
        s = df[c]; ex = s.dropna()
        prof.append(dict(base="Medicamentos Transparentes", tabela=t, escopo=tag, coluna=c, registros=len(s),
                         pct_preenchido=round(100 * s.notna().mean(), 2), distintos=int(s.nunique()),
                         exemplo=str(ex.iloc[0])[:120] if len(ex) else ""))
if "--perfil" in sys.argv:
    pd.DataFrame(prof).to_csv(os.path.join(ROOT, "reports", "perfil_colunas_transparencia.csv"), index=False)
