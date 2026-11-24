"""Extrai links e texto de uma página HTML salva. Uso: python -I 00_inspect_html.py arquivo.html [n_chars]"""
import re, sys, html
t = open(sys.argv[1], encoding="utf8").read()
n = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
print("bytes", len(t))
for m in sorted(set(re.findall(r'(?:href|src)="([^"]+)"', t))):
    print("LINK", m)
s = re.sub(r"<script.*?</script>", "", t, flags=re.S)
s = re.sub(r"<[^>]+>", " ", s)
print(re.sub(r"\s+", " ", html.unescape(s))[:n])
