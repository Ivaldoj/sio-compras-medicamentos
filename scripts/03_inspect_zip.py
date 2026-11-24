"""Lista o conteúdo de ZIPs e detecta codificação/delimitador das primeiras linhas de cada membro.
Uso: python -I 03_inspect_zip.py arquivo.zip [n_linhas]"""
import sys, zipfile, csv

n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
with zipfile.ZipFile(sys.argv[1]) as z:
    for i in z.infolist():
        print(f"== {i.filename} | comprimido={i.compress_size} | descomprimido={i.file_size}")
        head = z.open(i).read(200_000)
        enc = None
        for e in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
            try:
                txt = head.decode(e); enc = e; break
            except UnicodeDecodeError as ex:
                # corte no meio de um caractere multibyte no fim do bloco não invalida utf-8
                if e.startswith("utf-8") and ex.start > len(head) - 4:
                    txt = head[:ex.start].decode(e); enc = e; break
        try:
            delim = csv.Sniffer().sniff(txt.splitlines()[0]).delimiter
        except Exception:
            delim = "?"
        print("codificação provável:", enc, "| delimitador:", repr(delim), "| BOM:", head[:3] == b"\xef\xbb\xbf")
        for line in txt.splitlines()[:n]:
            print("  ", line[:1500])
