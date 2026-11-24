"""Lê a lista CMED de Preço Máximo de Venda ao Governo (PMVG) e testa o vínculo com o BPS pelo registro Anvisa.
Uso: python -I -X utf8 13_cmed_pmvg.py <raiz_projeto> <xlsx>
A primeira aba contém apenas notas; a aba de dados é a que tem uma célula iniciando por 'REGISTRO' nas primeiras linhas."""
import os, sys
import pandas as pd
ROOT, xp = sys.argv[1:3]
xl = pd.ExcelFile(xp)
print("abas:", xl.sheet_names)
for sh in xl.sheet_names:
    raw = pd.read_excel(xl, sheet_name=sh, header=None, dtype=str, nrows=300)
    hits = raw.index[raw.apply(lambda r: r.astype(str).str.strip().str.upper().str.startswith("REGISTRO").any(), axis=1)]
    if len(hits):
        break
else:
    sys.exit("cabeçalho não encontrado em nenhuma aba")
c = pd.read_excel(xl, sheet_name=sh, header=hits[0], dtype=str)
c.columns = [str(x).strip() for x in c.columns]
print("aba:", sh, "| linha de cabeçalho:", hits[0], "| linhas:", len(c), "| colunas:", len(c.columns))
print(list(c.columns))
print("exemplo:", {k: v for k, v in c.iloc[0].to_dict().items()})
reg_col = [x for x in c.columns if x.upper().startswith("REGISTRO")][0]
c["reg"] = c[reg_col].str.replace(r"\D", "", regex=True)
print("registros distintos:", c.reg.nunique(), "| tamanho típico do registro:", c.reg.str.len().value_counts().head(3).to_dict())
b = pd.read_parquet(os.path.join(ROOT, "data", "processed", "bps_2025_2026.parquet"))
b = b[b.co_classe == "6505"].copy()
b["reg"] = b.registro_anvisa.fillna("").str.replace(r"\D", "", regex=True)
print("\nBPS medicamentos (classe 6505):", len(b), "| registro_anvisa preenchido: %.1f%%" % (100 * (b.reg != "").mean()))
print("tamanho do registro no BPS:", b.reg.str.len().value_counts().head(4).to_dict())
# registro completo (13 dígitos = produto + apresentação) e registro do produto (9 primeiros dígitos)
full = set(c.reg) - {""}; prod = set(c.reg.str[:9]) - {""}
b = b[b.reg != ""]  # percentuais abaixo: sobre registros BPS com registro Anvisa informado
print("BPS com registro informado:", len(b))
print("BPS com registro de 13 dígitos encontrado na CMED (apresentação): %.1f%%" % (100 * b.reg.isin(full).mean()))
print("BPS com registro encontrado na CMED pelo produto (9 dígitos): %.1f%%" % (100 * b.reg.str[:9].isin(prod).mean()))
pd.DataFrame([dict(fonte="CMED PMVG 09/11/2026", linhas=len(c), registros_distintos=c.reg.nunique(),
                   bps_medicamentos_com_registro=len(b),
                   bps_match_13dig=int(b.reg.isin(full).sum()), bps_match_9dig=int(b.reg.str[:9].isin(prod).sum()))]).to_csv(
    os.path.join(ROOT, "reports", "integracao_bps_cmed.csv"), index=False)
