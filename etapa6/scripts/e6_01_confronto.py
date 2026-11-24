"""Etapa 6 / 01 — confronto entre a avaliação independente (Etapa 5, Fable) e a preparação anterior (pré-Etapa 5).

Somente leitura sobre etapa4/, etapa5/, etapa5_avaliacao_independente/ e data/. Não reexecuta o experimento nem os scripts
do agente: lê os resultados já gravados e vai às fontes primárias só para resolver as duas divergências.

    python -I -X utf8 etapa6/scripts/e6_01_confronto.py .

Saídas em etapa6/resultados/:
  divergencia_cmed_icms_celulas.csv     tipo e conteúdo das células 'PF 20%' da lista CMED bruta (jan/2025)
  divergencia_insulinas_2026.csv        produto declarado pelo vencedor de cada insulina no PE 09/2026, com página
  insulinas_quadro_corrigido.csv        quadro das insulinas sem usar o PE 09/2026 como preço de caneta
  confronto_numeros.csv                 números-chave: preparação anterior × avaliação independente
  integridade.csv                       sha256 dos arquivos congelados e dos resultados da Etapa 5
  confronto_numeros.json
"""
import csv
import glob
import hashlib
import json
import os
import re
import sys

import pandas as pd
import xlrd
from pypdf import PdfReader

RAIZ = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
P = lambda *a: os.path.join(RAIZ, *a)
RES = P("etapa6", "resultados")
os.makedirs(RES, exist_ok=True)
E5I = P("etapa5_avaliacao_independente", "resultados")
PRIM = P("etapa5_avaliacao_independente", "ambiente_avaliador", "evidencias_primarias")
N = {}


def sha(c):
    h = hashlib.sha256()
    with open(c, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ================================================================ 0. integridade (nada pode ter mudado)
integ = []
with open(P("etapa4", "registro", "hashes_ambiente_depois.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        c = P("etapa4", "ambiente_decisor", r["arquivo"])
        if os.path.exists(c):
            integ.append({"grupo": "etapa4/ambiente_decisor", "arquivo": r["arquivo"], "esperado": r["sha256"], "obtido": sha(c)})
log5 = open(P("LOG_ETAPA_5.md"), encoding="utf-8").read()
for h, nome in re.findall(r"^([0-9a-f]{64})\s+(\S+)$", log5, flags=re.M):
    c = P(nome) if nome.startswith("etapa5_avaliacao_independente/") else os.path.join(E5I, nome)
    if os.path.exists(c):
        integ.append({"grupo": "etapa 5 independente (LOG_ETAPA_5.md)", "arquivo": os.path.relpath(c, RAIZ).replace(os.sep, "/"), "esperado": h, "obtido": sha(c)})
logp = open(P("LOG_PRE_ETAPA_5.md"), encoding="utf-8").read()
for h, nome in re.findall(r"^([0-9a-f]{64})\s+(\S+)", logp, flags=re.M):
    if os.path.exists(P(nome)):
        integ.append({"grupo": "pré-etapa 5 (LOG_PRE_ETAPA_5.md)", "arquivo": nome, "esperado": h, "obtido": sha(P(nome))})
integ = pd.DataFrame(integ)
integ["confere"] = integ.esperado == integ.obtido
integ.to_csv(os.path.join(RES, "integridade.csv"), index=False, encoding="utf-8")
N["integridade_total"], N["integridade_conferem"] = int(len(integ)), int(integ.confere.sum())

# ================================================================ 1. divergência: ICMS na lista CMED bruta
xls = P("data", "raw", "complementares", "cmed_pmvg_20250107.xls")
sh = xlrd.open_workbook(xls).sheet_by_index(0)
hr = next(i for i in range(80) if any(str(v).strip().upper().startswith("SUBST") for v in sh.row_values(i)))
hdr = [str(v).strip() for v in sh.row_values(hr)]
ix = {k: hdr.index(k) for k in ("PF 0%", "PF 20%", "PMVG 20%", "CONFAZ 87", "ICMS 0%", "PRODUTO", "APRESENTAÇÃO")}
TIPO = {0: "vazia", 1: "texto", 2: "número", 6: "em branco"}
cel = []
for r in range(hr + 1, sh.nrows):
    conv = str(sh.cell_value(r, ix["CONFAZ 87"])).strip().lower() == "sim"
    c = sh.cell(r, ix["PF 20%"])
    v = str(c.value)
    cel.append({"linha_planilha": r + 1, "convenio_87": conv, "icms_0pct": str(sh.cell_value(r, ix["ICMS 0%"])).strip(),
                "tipo_celula_pf20": TIPO.get(c.ctype, str(c.ctype)), "tem_asterisco": "*" in v,
                "numero_puro": c.ctype == 2 or bool(re.fullmatch(r"\d+([.,]\d+)?", v.strip())),
                "pf0": str(sh.cell_value(r, ix["PF 0%"])), "pf20": v, "produto": str(sh.cell_value(r, ix["PRODUTO"])),
                "apresentacao": str(sh.cell_value(r, ix["APRESENTAÇÃO"]))})
cel = pd.DataFrame(cel)
cv = cel[cel.convenio_87]
num = lambda s: pd.to_numeric(s.str.replace("*", "", regex=False).str.replace(",", ".", regex=False), errors="coerce")
razao = (num(cv.pf20) / num(cv.pf0)).median()
resumo_c = (cel.groupby(["convenio_87", "tipo_celula_pf20", "tem_asterisco", "numero_puro"]).size().rename("registros").reset_index())
resumo_c.to_csv(os.path.join(RES, "divergencia_cmed_icms_celulas.csv"), index=False, encoding="utf-8")
cv[cv.apresentacao.str.contains("FLEXPEN") & cv.produto.str.contains("NOVOLIN")][["linha_planilha", "produto", "apresentacao", "pf0", "pf20", "icms_0pct"]].to_csv(
    os.path.join(RES, "divergencia_cmed_icms_exemplos.csv"), index=False, encoding="utf-8")
N.update({"cmed_sha256": sha(xls), "cmed_conv87_registros": int(len(cv)), "cmed_conv87_pf20_texto_com_asterisco": int((cv.tem_asterisco & (cv.tipo_celula_pf20 == "texto")).sum()),
          "cmed_conv87_pf20_vazias": int(cv.tipo_celula_pf20.isin(["vazia", "em branco"]).sum()), "cmed_conv87_pf20_numero_puro": int(cv.numero_puro.sum()),
          "cmed_asterisco_fora_do_convenio": int((cel.tem_asterisco & ~cel.convenio_87).sum()),
          "cmed_conv87_razao_mediana_pf20_pf0": float(razao)})
pre = json.load(open(P("etapa5", "avaliacao", "resumo.json"), encoding="utf-8"))
N["preparacao_fator_estimado_20_sobre_0"] = pre["K20"]

# ================================================================ 2. divergência: insulinas no PE 09/2026
ata = glob.glob(os.path.join(PRIM, "pncp", "09090689000167_2026_26", "docs", "09_extraido", "**", "*.pdf"), recursive=True)[0]
pg = [(p.extract_text() or "") for p in PdfReader(ata).pages[:60]]
MAPA = {189: 194, 190: 195, 191: 196, 192: 197, 193: 198, 194: 199}
EQUIV = {189: ("indeterminada", "marca 'BIOM', sem apresentação; não se sabe se é caneta"),
         190: ("indeterminada", "'5 CAN 3ML HUMALOG': caneta, mas não se sabe se o preço é por caneta ou por caixa com 5"),
         191: ("NÃO equivalente", "refil sem caneta ('S/CANETA', Penfill); o item exige sistema de aplicação"),
         192: ("equivalente", "frasco, Novo Nordisk"), 193: ("equivalente", "frasco, Novo Nordisk"),
         194: ("NÃO equivalente", "refil sem caneta ('S/CANETA'); o item exige sistema de aplicação")}
linhas = []
for i, t in enumerate(pg):
    u = re.sub(r"\s+", " ", t)
    for it26 in MAPA:
        m = re.search(rf"0{it26} Insulina (.*?)(\d+,\d\d) ([\d.]+) ([\d.]+,\d\d) (?=0{it26 + 1} )", u)
        if m and not any(l["item_pe09_2026"] == it26 for l in linhas):
            corpo = m.group(1)
            forn = re.search(r"(ALMEIDA FARMACEUTICA LTDA|GIULLITE B MEDEIROS|ALLFAMED[A-Z ]*LTDA)", corpo)
            prod = corpo[forn.end():].strip() if forn else ""
            linhas.append({"item_pe09_2026": it26, "item_pe04_2025": MAPA[it26], "pagina_ata_final": i + 1, "descricao_do_item": "Insulina " + corpo[:forn.start()].strip() if forn else corpo,
                           "vencedor": forn.group(1) if forn else "", "modelo_marca_declarados": prod, "preco_unitario": m.group(2), "quantidade": m.group(3),
                           "equivalencia_com_o_item_de_2025": EQUIV[it26][0], "motivo": EQUIV[it26][1]})
d26 = pd.DataFrame(linhas).sort_values("item_pe09_2026")
d26["sha256_ata"] = sha(ata)[:16]
d26.to_csv(os.path.join(RES, "divergencia_insulinas_2026.csv"), index=False, encoding="utf-8")
N["pe09_2026_insulinas_localizadas"] = int(len(d26))
N["pe09_2026_canetas_humanas_equivalentes"] = int((d26[d26.item_pe04_2025.isin([196, 199])].equivalencia_com_o_item_de_2025 == "equivalente").sum())

# quadro corrigido: o preço de 2026 só entra onde o produto é equivalente
ax = pd.read_csv(os.path.join(E5I, "insulinas_agente_x_evidencia.csv"))
ax = ax.merge(d26[["item_pe04_2025", "modelo_marca_declarados", "equivalencia_com_o_item_de_2025"]], left_on="item", right_on="item_pe04_2025", how="left")
ok = ax.equivalencia_com_o_item_de_2025 == "equivalente"
ax["homologado_2026_utilizavel"] = ax.homologado_2026_mesmo_comprador.where(ok)
ax["hom2026_sobre_ref_corrigido"] = (ax.homologado_2026_mesmo_comprador / ax.ref_agente).where(ok)
ax[["item", "descricao", "quantidade", "estimativa_orgao", "ref_agente", "teto_agente", "homologado_2025", "proponentes_2025", "homologado_2026_mesmo_comprador",
    "modelo_marca_declarados", "equivalencia_com_o_item_de_2025", "homologado_2026_utilizavel", "hom2026_sobre_ref_corrigido", "valor_2025_contratado",
    "valor_ref_agente"]].to_csv(os.path.join(RES, "insulinas_quadro_corrigido.csv"), index=False, encoding="utf-8")
N["etapa5_valor_insulinas_a_preco_2026_RETIRADO"] = float(ax.valor_a_preco_2026.sum())
N["etapa5_parte_desse_valor_vinda_de_refil"] = float(ax.loc[ax.item.isin([196, 199]), "valor_a_preco_2026"].sum())

# ================================================================ 3. confronto de números
X = json.load(open(os.path.join(E5I, "resumo.json"), encoding="utf-8"))
ex, ins, ec = X["expost"], X["insulinas"], X["economia"]
sp = pd.read_csv(P("etapa5", "avaliacao", "sensibilidade.csv"))
si = pd.read_csv(os.path.join(E5I, "sensibilidade_recomendacao.csv")).set_index("id")
cr = pd.read_csv(P("etapa5", "avaliacao", "comparacao_resumo.csv")).set_index("grupo")
c4 = pd.read_csv(P("etapa5", "avaliacao_canetas", "correcao_C4.csv")).iloc[0]
en = pd.read_csv(P("etapa5", "avaliacao", "economia_niveis.csv"))
vp = pd.read_csv(P("etapa5", "avaliacao", "verificacao_calculos.csv"))
spv = lambda p: float(sp[sp.cenario.str.startswith(p)].E1.iloc[0])
C = []
def cf(tema, indicador, prep, indep, situacao, obs=""):
    C.append({"tema": tema, "indicador": indicador, "preparacao_pre_etapa5": prep, "avaliacao_independente_etapa5": indep, "situacao": situacao, "observacao": obs})

cf("Cálculos", "verificações que conferem", f"{pre['verificacoes_ok']}/{pre['verificacoes']}", f"{X['verificacao_calculos']['conferem']}/{X['verificacao_calculos']['total']}",
   "convergem", "listas diferentes de verificações; nenhuma falhou em nenhuma das duas")
cf("Cálculos", "reprodução dos scripts do agente (v1)", "13 saídas numéricas idênticas byte a byte", f"{X['reproducao']['v1_csv_identicos_em_bytes']} CSVs idênticos byte a byte",
   "convergem", "ambientes diferentes (Python 3.13 × 3.10)")
cf("Preço", "homologado total (R$)", pre["H_tot"], ex["homologado_total"], "idênticos")
cf("Preço", "razão mediana homologado/referência, todos os itens", round(float(cr.loc["todos", "razao_mediana"]), 4), round(ex["hom_sobre_ref_mediana"], 4), "idênticos")
cf("Preço", "itens homologados acima da faixa do agente", round(334 * float(cr.loc["todos", "pct_acima_faixa"])), ex["itens_hom_acima_faixa"], "idênticos")
cf("Preço", "itens com mediana nacional posterior", int(cr.loc["todos", "itens_com_mercado_2025"]), ex["itens_com_mediana_nacional"], "compatíveis",
   "preparação: ano civil de 2025; independente: 30/01/2025 a 29/01/2026 e mínimo de 5 registros")
cf("Preço", "referência do agente ÷ mediana nacional posterior", round(1 / float(cr.loc["todos", "razao_mediana_mercado25_ref"]), 3), round(ex["ref_sobre_nac_mediana"], 3),
   "convergem", "as duas indicam referência ~10% acima do mercado posterior")
cf("Preço", "homologado ÷ mediana nacional posterior", round(float(cr.loc["todos", "razao_mediana_hom_mercado25"]), 3), round(ex["hom_sobre_nac_mediana"], 3), "convergem")
cf("Teto", "itens homologados acima do teto (pacote)", int(c4.avaliacao_original), ex["itens_hom_acima_teto_agente"], "idênticos")
cf("Teto", "excesso sobre o teto (R$)", round(float(c4.excesso_original), 2), round(ex["excesso_hom_sobre_teto"], 2), "idênticos")
cf("Teto", "idem, com as análogas 194/195", f"{int(c4.corrigido)} itens; {float(c4.excesso_corrigido):.2f}",
   f"17 itens; {ex['excesso_hom_sobre_teto'] + ins['analogas_excesso_sobre_o_maior_teto_pb']:.2f}", "idênticos", "obtidos por caminhos independentes")
cf("Execução", "pago no PE 04/2025 (R$)", pre["pago"], ex["pe04_pago_total"], "idênticos")
cf("Execução", "fração empenhada do contratado", round(pre["d_obs"], 4), round(ex["pe04_pct_empenhado"] / 100, 4), "idênticos")
cf("Sensibilidade", "cenários que alteram a recomendação", f"{len(pre['cenarios_que_alteram'])} de {len(sp)}", f"{len(ec['cenarios_que_alteram'])} de {ec['cenarios']}",
   "compatíveis", "os 2 que alteram na independente cruzam o pior caso do E1 com o melhor do E2; a preparação não testou cruzamentos")
cf("Sensibilidade", "E1 com teto a 20% no Convênio 87/02 (R$)", round(spv("S2"), 0), round(float(si.loc["S2", "E1"]), 0), "convergem",
   "preparação: fator estimado de 1,25; independente: coluna de 20% lida da lista bruta")
cf("Sensibilidade", "E1 à mediana nacional posterior (R$)", round(spv("S5"), 0), round(float(si.loc["S5", "E1"]), 0), "compatíveis", "janelas e regra de preenchimento diferentes")
cf("Economia", "potencial E2 − E1 (R$)", round(float(en.valor.iloc[0]), 0), round(ec["potencial_E2_menos_E1"], 0), "idênticos")
cf("Economia", "contratada R0 − homologado (R$)", round(float(en.valor.iloc[2]), 0), round(ec["contratada_R0_menos_hom"], 0), "idênticos")
cf("Economia", "realizada estimada frente a R0, mix proporcional (R$)", round(float(en.valor.iloc[4]), 0), round(ec["realizada_estimativa_economia_vs_R0_mix_proporcional"], 0), "idênticos")
cf("Falhas do pacote", "F1 (194/195) e F2 (197)", "confirmadas", "confirmadas", "convergem")
cf("Falhas do pacote", "F3 (item 268)", "não confirmada", "não confirmada", "convergem")
cf("Falhas do pacote", "F4 (coluna de 20% no Convênio 87/02)", "fato da fonte: 0 de 2.810 na lista bruta",
   f"a fonte publica: {N['cmed_conv87_pf20_texto_com_asterisco']} de {N['cmed_conv87_registros']} células como texto com asterisco",
   "DIVERGEM — resolvida a favor da avaliação independente", "ver divergencia_cmed_icms_celulas.csv")
cf("Insulinas", "unidade contratada das canetas", "caneta (7 documentos)", "caneta (ETP, TR, contrato, aditivo)", "convergem")
cf("Insulinas", "contratado ÷ teto, canetas 196 e 199", "9,58 e 9,32", "9,58 e 9,32", "idênticos")
cf("Insulinas", "preço de R$ 29,00 no PE 09/2026 como preço de caneta", "não usado: o vencedor ofertou refil sem caneta",
   "usado como preço da 'mesma caneta' e como confirmação do risco de deserto", "DIVERGEM — resolvida a favor da preparação",
   "ver divergencia_insulinas_2026.csv; três afirmações da Etapa 5 ficam retiradas")
pd.DataFrame(C).to_csv(os.path.join(RES, "confronto_numeros.csv"), index=False, encoding="utf-8")
N["confronto_linhas"] = len(C)
N["confronto_divergencias"] = int(sum("DIVERGEM" in c["situacao"] for c in C))
json.dump(N, open(os.path.join(RES, "confronto_numeros.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 70); pd.set_option("display.max_columns", 20)
print(resumo_c.to_string(index=False))
print(d26[["item_pe09_2026", "item_pe04_2025", "pagina_ata_final", "vencedor", "modelo_marca_declarados", "preco_unitario", "equivalencia_com_o_item_de_2025"]].to_string(index=False))
print(pd.DataFrame(C)[["indicador", "preparacao_pre_etapa5", "avaliacao_independente_etapa5", "situacao"]].to_string(index=False))
for k, v in N.items():
    print(k, ":", v)
