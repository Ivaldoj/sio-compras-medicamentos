"""Confere o grupo de financiamento dos itens não-1A (e AP007) no Anexo III da RENAME 2024 (evidencias_primarias/rename).
Imprime o trecho e a página do PDF. Saída: trabalho/d01_rename_trechos.txt"""
import re, subprocess
subprocess.run(["pdftotext", "-layout", "evidencias_primarias/rename/relacao_nacional_medicamentos_2024_2ed.pdf", "trabalho/rename2024.txt"], check=True)
txt = open("trabalho/rename2024.txt", encoding="latin-1").read()
paginas = txt.split("\f")
ini = next(i for i, p in enumerate(paginas) if re.search(r"ANEXO III . Rela", p) and i > 100)  # início do Anexo III (lista)
alvo = ["imunoglobulina humana", "mepolizumabe", "eltrombopague", "omalizumabe", "leuprorrelina", "atorvastatina", "dapagliflozina",
        "mesalazina", "azatioprina", "calcitriol"]
out = []
for i, p in enumerate(paginas[ini:], start=ini + 1):
    for a in alvo:
        for m in re.finditer(a, p, re.I):
            ls = p[:m.start()].count("\n"); linhas = p.splitlines()
            trecho = "\n".join(l[:150] for l in linhas[max(0, ls - 4): ls + 8])
            out.append(f"=== {a} | página do PDF {i}\n{trecho}\n")
            break
open("trabalho/d01_rename_trechos.txt", "w", encoding="utf8").write("\n".join(out))
print("início do Anexo III (lista) na página", ini + 1); print("\n".join(o.splitlines()[0] for o in out))
