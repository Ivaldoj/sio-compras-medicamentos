"""Etapa 3 — BPS nacional 2020–2026 padronizado, com classe temporal por registro.
Uso: python -I -X utf8 24_bps_historico_temporal.py <raiz_projeto> [corte=2025-01-29]

Classe temporal (data de disponibilidade = dt_insercao, momento em que o registro entra no BPS):
  disponivel     dt_insercao <= corte  e  dt_compra <= dt_insercao
  posterior      dt_insercao  > corte
  indeterminado  datas ausentes/inválidas ou dt_insercao < dt_compra (inserção anterior à compra é impossível)
Só a classe 'disponivel' da classe de material 6505 (medicamentos) vai para data/decision_input.
Nada é removido por qualidade: outliers e duplicatas recebem marcas (flag_*)."""
import glob, os, sys, zipfile
import pandas as pd

ROOT = sys.argv[1]
CUT = pd.Timestamp(sys.argv[2] if len(sys.argv) > 2 else "2025-01-29")
D = lambda *p: os.path.join(ROOT, "data", *p)
REG = {"N": "AC AM AP PA RO RR TO", "NE": "AL BA CE MA PB PE PI RN SE", "CO": "DF GO MS MT", "SE": "ES MG RJ SP", "S": "PR RS SC"}
REG = {uf: r for r, ufs in REG.items() for uf in ufs.split()}

fr = []
for zp in sorted(glob.glob(D("raw", "bps", "20??_csv.zip"))):
    with zipfile.ZipFile(zp) as z:
        x = pd.read_csv(z.open(z.namelist()[0]), sep=";", dtype=str, keep_default_na=False, na_values=[""])
    x["arquivo_origem"] = "data/raw/bps/" + os.path.basename(zp)
    fr.append(x); print(os.path.basename(zp), len(x), "registros,", x.shape[1], "colunas")
cols = [set(f.columns) for f in fr]
print("colunas comuns a todos os anos:", len(set.intersection(*cols)), "| diferenças:", sorted(set.union(*cols) - set.intersection(*cols)))
b = pd.concat(fr, ignore_index=True)

o = pd.DataFrame({
    "fonte": "BPS", "id_origem": b.co_seq_bps, "arquivo_origem": b.arquivo_origem,
    "catmat": b.co_catmat, "descricao_catmat": b.ds_item, "principio_ativo_pdm": b.no_pdm, "codigo_pdm": b.co_pdm,
    "classe_material": b.co_classe, "unidade_fornecimento": b.un_fornecimento,
    "capacidade_valor": pd.to_numeric(b.vl_capacidade, errors="coerce"), "capacidade_descricao": b.un_medida_capacidade,
    "capacidade_unidade": b.sg_unidade_medida, "registro_anvisa": b.registro_anvisa.str.replace(r"\D", "", regex=True),
    "generico": b.fg_generico,
    "comprador_cnpj": b.cnpj_instituicao.str.zfill(14), "comprador_nome": b.no_instituicao, "comprador_municipio": b.no_municipio,
    "uf": b.sg_uf, "regiao": b.sg_uf.map(REG), "esfera": b.ds_esfera,
    "fornecedor_cnpj": b.cnpj_fornecedor.str.zfill(14), "fabricante_cnpj": b.cnpj_fabricante.str.zfill(14),
    "modalidade": b.modalidade, "tipo_compra": b.tp_compra, "processo": b.nu_processo_compra, "ata": b.nu_ata,
    "data_compra": pd.to_datetime(b.dt_compra, format="%d/%m/%Y", errors="coerce"),
    "data_insercao": pd.to_datetime(b.dt_insercao, format="%d/%m/%Y", errors="coerce"),
    "quantidade": pd.to_numeric(b.qt_medicamento, errors="coerce"),
    "preco_unitario_praticado": pd.to_numeric(b.vl_preco_unitario, errors="coerce"),  # R$ por unidade de fornecimento
    "valor_total_praticado": pd.to_numeric(b.vl_preco_total, errors="coerce"),
})
o["categoria_valor"] = "preco_unitario_praticado_por_unidade_fornecimento"
o["data_disponibilidade"] = o.data_insercao
o["base_disponibilidade"] = "BPS dt_insercao (inserção no sistema de consulta pública)"
bad = o.data_compra.isna() | o.data_insercao.isna() | (o.data_insercao < o.data_compra)
o["classe_temporal"] = "posterior"
o.loc[o.data_insercao <= CUT, "classe_temporal"] = "disponivel"
o.loc[bad, "classe_temporal"] = "indeterminado"
o["motivo_temporal"] = ""
o.loc[o.data_insercao < o.data_compra, "motivo_temporal"] = "dt_insercao anterior a dt_compra"
o.loc[o.data_compra.isna() | o.data_insercao.isna(), "motivo_temporal"] = "data ausente ou inválida"

# marcas de qualidade (calculadas só com registros disponíveis, para não usar informação futura)
disp = o.classe_temporal == "disponivel"
med = o[disp].groupby(["catmat", "unidade_fornecimento"]).preco_unitario_praticado.median().rename("mediana_grupo")
o = o.join(med, on=["catmat", "unidade_fornecimento"])
r = o.preco_unitario_praticado / o.mediana_grupo
o["flag_preco_extremo"] = (r > 20) | (r < 0.05)  # regra fixa: >20x ou <1/20 da mediana do mesmo CATMAT+unidade (pré-corte)
o["flag_total_inconsistente"] = ((o.valor_total_praticado - o.preco_unitario_praticado * o.quantidade).abs() > 0.01 * o.valor_total_praticado.abs().clip(lower=1))
key = ["comprador_cnpj", "data_compra", "catmat", "fornecedor_cnpj", "quantidade", "preco_unitario_praticado", "processo"]
o["flag_duplicata_negocio"] = o.duplicated(key, keep=False)
o = o.drop(columns="mediana_grupo")
assert o.id_origem.is_unique, "co_seq_bps repetido entre arquivos"

print("\nclasse temporal:", o.classe_temporal.value_counts().to_dict())
print("motivos indeterminado:", o[o.classe_temporal == "indeterminado"].motivo_temporal.value_counts().to_dict())
s = o[disp]
print("disponíveis: compras %s..%s | inserção %s..%s | UFs %d | instituições %d | CATMAT %d" % (
    s.data_compra.min().date(), s.data_compra.max().date(), s.data_insercao.min().date(), s.data_insercao.max().date(),
    s.uf.nunique(), s.comprador_cnpj.nunique(), s.catmat.nunique()))
print("disponíveis por ano de compra:", s.data_compra.dt.year.value_counts().sort_index().to_dict())
print("disponíveis por região:", s.regiao.value_counts().to_dict())
print("disponíveis medicamentos (6505):", int((s.classe_material == "6505").sum()), "| flags:", {c: int(s[c].sum()) for c in o.columns if c.startswith("flag_")})

for p in ("decision_input/nacional", "evaluation_only/nacional", "quarentena_temporal"):
    os.makedirs(D(p), exist_ok=True)
o[disp & (o.classe_material == "6505")].to_parquet(D("decision_input", "nacional", "bps_precos_praticados.parquet"), index=False)
o[o.classe_temporal == "posterior"].to_parquet(D("evaluation_only", "nacional", "bps_pos_corte.parquet"), index=False)
o[o.classe_temporal == "indeterminado"].to_parquet(D("quarentena_temporal", "bps_disponibilidade_indeterminada.parquet"), index=False)
o.groupby(["classe_temporal", o.data_compra.dt.year.rename("ano_compra")], dropna=False).size().rename("registros").to_csv(
    os.path.join(ROOT, "reports", "etapa3_bps_classes_temporais.csv"))
print("excluídos do pacote por não serem medicamentos (classe != 6505) entre os disponíveis:", int((disp & (o.classe_material != "6505")).sum()))
