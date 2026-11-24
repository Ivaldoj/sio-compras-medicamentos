"""Etapa 5 / 04 — insulinas: evidências documentais, teto CMED (lista bruta), mercado posterior e erratas.

Fontes primárias (somente leitura), em etapa5_avaliacao_independente/ambiente_avaliador/evidencias_primarias/:
  pncp/09090689000167_2025_6/docs/   edital (ETP/TR), Contrato 00054/2025, Aditivo 01, Ata Final do PE 04/2025
  pncp/09090689000167_2025_6/*.json  itens e resultados no PNCP
  cmed/cmed_pmvg_20250107.xls        lista CMED vigente em 29/01/2025 (arquivo bruto, não o pacote)
  cmed/cmed_lista_pmvg_20261109.xlsx lista CMED de nov/2026 (só contexto)
  normas/ms_nota_tecnica_*.pdf       notas técnicas do MS anteriores ao corte
Saídas em resultados/:
  insulinas_evidencias_documentais.csv   unidade, quantidade, preço e marca, com página e trecho
  insulinas_cmed_bruta.csv               apresentações de insulina humana 3 mL na CMED de jan/2025, teto por caneta
  insulinas_impacto.csv                  contratado × teto, em três hipóteses, e limites do que pode ter sido pago
  insulinas_mercado_posterior.csv        mesmo comprador em 2026 (PE 09/2026) e registros nacionais do horizonte
  insulinas_normas_ms.csv                trechos das notas técnicas do MS (aquisição centralizada)
  insulinas_agente_x_evidencia.csv       por insulina: referência do agente × homologado 2025 × homologado 2026 × teto
  falhas_pacote_verificacao_independente.csv  as 4 falhas apontadas pelo agente × errata × verificação própria
  insulinas_numeros.json
"""
import json
import os
import pickle
import re
import sys
import tempfile
import warnings

import numpy as np
import pandas as pd
from pypdf import PdfReader

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e5_comum import EVAL, HORIZ_FIM, HORIZ_INI, PRIM, RES, SAIDA, V1, V2, sha256

D6 = os.path.join(PRIM, "pncp", "09090689000167_2025_6")
N = {}
# a extração de PDF traz caracteres de controle e substitutos isolados, que o escritor de CSV recusa
limpa = lambda s: re.sub(r"\s+", " ", re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff]", " ", s)).strip()


def paginas_pdf(caminho):
    cache = os.path.join(tempfile.gettempdir(), f"e5_pdf_{sha256(caminho)[:16]}.pkl")
    if os.path.exists(cache):
        return pickle.load(open(cache, "rb"))
    pg = [(p.extract_text() or "") for p in PdfReader(caminho).pages]
    pickle.dump(pg, open(cache, "wb"))
    return pg


# ============================================================ 1. evidências documentais
DOCS = [("Edital PE 04/2025 — ETP (anexo)", "docs/01_edital.pdf", "antes da licitação"),
        ("Contrato 00054/2025 (ALLFAMED)", "docs/05_arquivo.pdf", "contratação (12/03/2025)"),
        ("Termo Aditivo 01 ao Contrato 00054/2025", "docs/12_aditivo.pdf", "prorrogação (até 12/03/2027)"),
        ("Ata Final do PE 04/2025", "docs/16_extraido/Ata Final.pdf", "sessão (12–13/02/2025)")]
# a extração de PDFs digitalizados troca letras por dígitos (I OOUl/mL); o padrão tolera isso
PAD = {196: r"Insulina\s+Humana\s+NPH[^\n]{0,40}\n?[^\n]{0,60}?3\s*mL\s+com[\s\S]{0,60}?sistema\s+de\s+aplica[çc][ãa]o[^\n]{0,60}",
       199: r"Insulina\s+Humana\s+Regular[\s\S]{0,60}?3\s*\n?\s*(?:\d\.\d{3}\s+caneta\s+[\d,]+\s*\n?\s*)?mL\s+com[\s\S]{0,40}?sistema\s+de[\s\S]{0,12}?aplica[çc][ãa]o[^\n]{0,60}"}
ev = []
for nome, rel, fase in DOCS:
    caminho = os.path.join(D6, rel)
    pg = paginas_pdf(caminho)
    for it, pad in PAD.items():
        achou = 0
        for i, t in enumerate(pg):
            for m_ in re.finditer(pad, t, flags=re.I):
                trecho = limpa(t[max(0, m_.start() - 10): m_.end() + 90])
                un = "caneta" if re.search(r"caneta", trecho, re.I) else ("caixa" if re.search(r"\bcaixa\b|\bcx\b", trecho, re.I) else "não consta no trecho")
                pr = re.search(r"(193[,.]02|147[,.]?36)", trecho)
                qt = re.search(r"\b(6\.000|1\.200)\b", trecho)
                ev.append({"documento": nome, "arquivo": rel, "sha256": sha256(caminho)[:16], "fase": fase, "pagina": i + 1, "item": it,
                           "unidade_no_trecho": un, "quantidade_no_trecho": qt.group(1) if qt else "", "preco_no_trecho": pr.group(1) if pr else "",
                           "menciona_caixa": bool(re.search(r"\bcaixa\b|\bcx\b", trecho, re.I)), "trecho": trecho[:330]})
                achou += 1
                if achou >= 3:
                    break
            if achou >= 3:
                break
# PNCP (JSON)
ji = json.load(open(os.path.join(D6, "itens_p1.json"), encoding="utf-8"))
ji = ji if isinstance(ji, list) else ji.get("data", ji)
for x in ji:
    if x["numeroItem"] in (196, 199):
        r_ = json.load(open(os.path.join(D6, f"resultado_item_{x['numeroItem']}.json"), encoding="utf-8"))
        r_ = r_[0] if isinstance(r_, list) else r_
        ev.append({"documento": "PNCP — item e resultado (API)", "arquivo": f"itens_p1.json; resultado_item_{x['numeroItem']}.json", "sha256": "", "fase": "homologação (11/03/2025)",
                   "pagina": "", "item": x["numeroItem"], "unidade_no_trecho": x["unidadeMedida"], "quantidade_no_trecho": x["quantidade"],
                   "preco_no_trecho": r_["valorUnitarioHomologado"], "menciona_caixa": False,
                   "trecho": limpa(f"{x['descricao']} | unidadeMedida={x['unidadeMedida']} | estimado={x['valorUnitarioEstimado']} | "
                                   f"homologado={r_['valorUnitarioHomologado']} × {r_['quantidadeHomologada']} = {r_['valorTotalHomologado']} | "
                                   f"{r_['nomeRazaoSocialFornecedor']} | desconto={r_['percentualDesconto']}%")})
ev = pd.DataFrame(ev)
ev.to_csv(os.path.join(RES, "insulinas_evidencias_documentais.csv"), index=False, encoding="utf-8")
N["evidencias_trechos"] = int(len(ev))
N["evidencias_documentos"] = int(ev.documento.nunique())
N["evidencias_trechos_com_caneta"] = int((ev.unidade_no_trecho.astype(str).str.lower() == "caneta").sum())
N["evidencias_trechos_com_caixa"] = int(ev.menciona_caixa.sum())

# propostas e marca na Ata Final
ata = "\n".join(paginas_pdf(os.path.join(D6, "docs", "16_extraido", "Ata Final.pdf")))
prop = {}
for it in (194, 195, 196, 199):
    b = re.search(rf"0{it} - Insulina[\s\S]*?(?=\n0{it + 1} - )", ata)
    bloco = b.group(0) if b else ""
    cnpjs = set(re.findall(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\s*\d{2}", bloco))
    marca = re.search(r"\d{2}:\d{2}:\d{2}\s+(\S+)\s+(\S+)\s+[\d.]+\s+R\$", bloco)
    prop[it] = {"proponentes": len({re.sub(r"\s", "", c) for c in cnpjs}), "marca_fabricante": f"{marca.group(1)} / {marca.group(2)}" if marca else ""}
N["propostas_ata_final"] = prop

# ============================================================ 2. CMED bruta (jan/2025)
xls = os.path.join(PRIM, "cmed", "cmed_pmvg_20250107.xls")
bruto = pd.read_excel(xls, header=None, nrows=80)
hr = next(i for i in range(80) if bruto.iloc[i].astype(str).str.contains("SUBST").any())
nota_viii = next((limpa(str(v)) for i in range(hr) for v in bruto.iloc[i].dropna().tolist() if str(v).startswith("(viii)")), "")
cm = pd.read_excel(xls, header=hr, dtype=str)
cm.columns = [c.strip() for c in cm.columns]
numf = lambda s: pd.to_numeric(s.astype(str).str.replace("*", "", regex=False).str.replace(",", ".", regex=False).str.strip(), errors="coerce")
conv = cm[cm["CONFAZ 87"].astype(str).str.strip().str.lower() == "sim"]
N["cmed_registros_convenio_87"] = int(len(conv))
N["cmed_conv87_pf20_numerico_puro"] = int(pd.to_numeric(conv["PF 20%"], errors="coerce").notna().sum())
N["cmed_conv87_pf20_com_asterisco"] = int(conv["PF 20%"].astype(str).str.contains(r"\*").sum())
N["cmed_nota_viii"] = nota_viii[:600]
ins = cm[cm["SUBSTÂNCIA"].astype(str).str.upper().eq("INSULINA HUMANA") & cm["APRESENTAÇÃO"].astype(str).str.contains("3 ML")].copy()
ap = ins["APRESENTAÇÃO"].astype(str)
ins["tem_sistema_aplicacao"] = ap.str.contains("SIST APLIC")
ins["tipo"] = np.where(ins["PRODUTO"].str.contains("70"), "pré-mistura 70/30", np.where(ap.str.contains("SUS INJ"), "NPH", "Regular"))
ins["n_unidades"] = ap.str.extract(r"(?:CT|CX)\s+(\d+)\s+CARP?")[0].astype(float).fillna(1)
for c in ("PF 0%", "PF 20%", "PMVG 0%", "PMVG 20%"):
    ins[c + " (num)"] = numf(ins[c])
ins["cap"] = ins["CAP"].str.strip().str.lower().eq("sim")
ins["teto_aplicavel_0pct_por_unidade"] = np.where(ins.cap, ins["PMVG 0% (num)"], ins["PF 0% (num)"]) / ins.n_unidades
ins["teto_aplicavel_20pct_por_unidade"] = np.where(ins.cap, ins["PMVG 20% (num)"], ins["PF 20% (num)"]) / ins.n_unidades
ins["tipo_teto"] = np.where(ins.cap, "PMVG (CAP)", "PF")
cols = ["LABORATÓRIO", "REGISTRO", "PRODUTO", "APRESENTAÇÃO", "tipo", "tem_sistema_aplicacao", "n_unidades", "CAP", "CONFAZ 87", "ICMS 0%",
        "PF 0%", "PF 20%", "PMVG 0%", "PMVG 20%", "tipo_teto", "teto_aplicavel_0pct_por_unidade", "teto_aplicavel_20pct_por_unidade"]
ins[cols].to_csv(os.path.join(RES, "insulinas_cmed_bruta.csv"), index=False, encoding="utf-8")
can = ins[ins.tem_sistema_aplicacao & ins.tipo.isin(["NPH", "Regular"])]
N["cmed_canetas_apresentacoes"] = int(len(can))
N["cmed_canetas_laboratorios"] = sorted(can["LABORATÓRIO"].str.strip().unique().tolist())
teto = {}
for tp, it in (("NPH", 196), ("Regular", 199)):
    c_ = can[can.tipo == tp]
    teto[it] = {"tipo": tp, "tipo_teto": c_.tipo_teto.iloc[0], "teto_0pct_min": float(c_.teto_aplicavel_0pct_por_unidade.min()),
                "teto_0pct_max": float(c_.teto_aplicavel_0pct_por_unidade.max()), "teto_20pct_max": float(c_.teto_aplicavel_20pct_por_unidade.max())}
N["teto_cmed_jan2025_por_caneta"] = teto
N["cmed_equiplex_apresentacoes"] = int(cm["LABORATÓRIO"].astype(str).str.contains("EQUIPLEX", case=False).sum())
N["cmed_equiplex_insulinas"] = int((cm["LABORATÓRIO"].astype(str).str.contains("EQUIPLEX", case=False) & cm["SUBSTÂNCIA"].astype(str).str.contains("INSULINA", case=False)).sum())

# análogas em caneta (itens 194 e 195): o pacote não tem vínculo CMED (o item não diz a substância). Teste: o MAIOR teto por caneta
# entre todas as análogas do tipo, na alíquota aplicável à PB (0% se Convênio 87/02 ou isento; 20% nos demais), PMVG se CAP.
sub = cm["SUBSTÂNCIA"].astype(str).str.upper().str.strip()
apr = cm["APRESENTAÇÃO"].astype(str)
TIPOS = {194: ("análoga de ação prolongada", ["INSULINA GLARGINA", "INSULINA DETEMIR", "INSULINA DEGLUDECA"]),
         195: ("análoga de ação rápida", ["INSULINA ASPARTE", "INSULINA LISPRO", "INSULINA GLULISINA"])}
ana, teto_ana = [], {}
for it_, (rotulo, subs) in TIPOS.items():
    z = cm[sub.isin(subs) & apr.str.contains(r"100 U") & apr.str.contains(r"3 ML") & apr.str.contains(r"APLIC") & apr.str.contains("SOL INJ")].copy()
    z = z[~z["PRODUTO"].astype(str).str.contains("MIX")]
    z["n"] = z["APRESENTAÇÃO"].str.extract(r"CT\s*X?\s*(\d+)\s+CARP?")[0].astype(float).fillna(1)
    z["cap"] = z["CAP"].str.strip().str.lower().eq("sim")
    z["isento"] = z["CONFAZ 87"].str.strip().str.lower().eq("sim") | z["ICMS 0%"].str.strip().str.lower().eq("sim")
    pf = np.where(z.isento, numf(z["PF 0%"]), numf(z["PF 20%"]))
    pm = np.where(z.isento, numf(z["PMVG 0%"]), numf(z["PMVG 20%"]))
    z["teto_pb_por_caneta"] = np.where(z.cap, pm, pf) / z.n
    z["teto_20pct_por_caneta"] = np.where(z.cap, numf(z["PMVG 20%"]), numf(z["PF 20%"])) / z.n
    z["item"], z["tipo_item"] = it_, rotulo
    ana.append(z[["item", "tipo_item", "SUBSTÂNCIA", "PRODUTO", "APRESENTAÇÃO", "n", "CAP", "CONFAZ 87", "PF 0%", "PF 20%", "PMVG 0%", "PMVG 20%",
                  "teto_pb_por_caneta", "teto_20pct_por_caneta"]])
    teto_ana[it_] = {"apresentacoes": int(len(z)), "teto_pb_max": float(z.teto_pb_por_caneta.max()), "teto_pb_min": float(z.teto_pb_por_caneta.min()),
                     "teto_20pct_max": float(z.teto_20pct_por_caneta.max()), "produto_do_maior_teto": str(z.loc[z.teto_pb_por_caneta.idxmax(), "PRODUTO"])}
pd.concat(ana).to_csv(os.path.join(RES, "insulinas_cmed_analogas.csv"), index=False, encoding="utf-8")
N["teto_cmed_jan2025_analogas_por_caneta"] = teto_ana

# CMED nov/2026 (contexto: teto na época do PE 09/2026)
teto26 = {}
try:
    x26 = os.path.join(PRIM, "cmed", "cmed_lista_pmvg_20261109.xlsx")
    xl = pd.ExcelFile(x26)
    for aba in xl.sheet_names:
        b26 = xl.parse(aba, header=None, nrows=80)
        h26 = [i for i in range(len(b26)) if b26.iloc[i].astype(str).str.contains("SUBST").any()]
        if not h26:
            continue
        c26 = xl.parse(aba, header=h26[0], dtype=str)
        c26.columns = [re.sub(r"\s+%", "%", re.sub(r"\s+", " ", str(c)).strip()) for c in c26.columns]  # "PMVG 0 %" -> "PMVG 0%"
        i26 = c26[c26["SUBSTÂNCIA"].astype(str).str.upper().eq("INSULINA HUMANA") & c26["APRESENTAÇÃO"].astype(str).str.contains("3 ML")
                  & c26["APRESENTAÇÃO"].astype(str).str.contains("SIST APLIC") & ~c26["PRODUTO"].astype(str).str.contains("70")].copy()
        i26["n"] = i26["APRESENTAÇÃO"].str.extract(r"(?:CT|CX)\s+(\d+)\s+CARP?")[0].astype(float).fillna(1)
        i26["tipo"] = np.where(i26["APRESENTAÇÃO"].str.contains("SUS INJ"), "NPH", "Regular")
        i26["cap"] = i26["CAP"].str.strip().str.lower().eq("sim")
        for tp, it in (("NPH", 196), ("Regular", 199)):
            z = i26[i26.tipo == tp]
            if not len(z):
                continue
            pf0 = numf(z["PF 0%"]) / z.n
            pmvg0 = numf(z["PMVG 0%"]) / z.n if "PMVG 0%" in z.columns else pf0 * np.nan
            aplic = np.where(z.cap & pmvg0.notna(), pmvg0, pf0)
            teto26[it] = {"pf_0pct_por_caneta_max": float(pf0.max()), "pmvg_0pct_por_caneta_max": None if pmvg0.isna().all() else float(pmvg0.max()),
                          "teto_aplicavel_0pct_max": float(np.nanmax(aplic)), "apresentacoes": int(len(z)),
                          "pf_20pct_publicado": bool("PF 20%" in z.columns and z["PF 20%"].notna().any()),
                          "pf_20pct_por_caneta_max": float((numf(z["PF 20%"]) / z.n).max()) if "PF 20%" in z.columns and z["PF 20%"].notna().any() else None,
                          "laboratorios": sorted(z["LABORATÓRIO"].str.strip().unique().tolist())}
except Exception as e:  # contexto opcional
    teto26 = {"erro": str(e)[:200]}
N["teto_cmed_nov2026_por_caneta"] = teto26

# ============================================================ 3. impacto: contratado × teto
hom = pd.read_parquet(os.path.join(EVAL, "organizacional", "resultado_homologado_PE04_2025.parquet")).set_index("item")
exe = pd.read_parquet(os.path.join(EVAL, "organizacional", "execucao_contratos.parquet"))
c54 = exe[(exe.compra == "09090689000167-1-000006/2025") & (exe.forn == 31187918000115)].iloc[0]
pago54 = float(c54.pago_total)
imp = []
for it in (196, 199):
    p, q_ = float(hom.loc[it, "preco_unitario_homologado"]), float(hom.loc[it, "quantidade_homologada"])
    for hip, t_, doc in (("unidade = caneta; ICMS 0% (Convênio 87/02) — hipótese do agente e documentada", teto[it]["teto_0pct_max"], "documentada"),
                         ("unidade = caneta; coluna de ICMS 20% da lista bruta (se o Convênio não se aplicasse)", teto[it]["teto_20pct_max"], "teste de robustez"),
                         ("teste: preço seria de caixa com 5 canetas; ICMS 0% (hipótese NÃO documentada)", 5 * teto[it]["teto_0pct_max"], "não documentada"),
                         ("teste: caixa com 5 canetas; ICMS 20% (hipótese NÃO documentada, a mais favorável ao contrato)", 5 * teto[it]["teto_20pct_max"], "não documentada")):
        imp.append({"item": it, "hipotese": hip, "status_da_hipotese": doc, "preco_contratado": p, "quantidade_contratada": q_, "teto": t_,
                    "contratado_sobre_teto": p / t_, "acima_do_teto": p > t_ + 0.005, "valor_contratado": p * q_, "valor_no_teto": min(p, t_) * q_,
                    "excesso_contratado_sobre_teto": max(p - t_, 0) * q_})
for it in (194, 195):  # análogas: comparadas ao MAIOR teto possível do tipo (teste mais favorável ao contrato)
    p, q_ = float(hom.loc[it, "preco_unitario_homologado"]), float(hom.loc[it, "quantidade_homologada"])
    for hip, t_ in ((f"maior teto por caneta entre as análogas do tipo, alíquota da PB ({teto_ana[it]['produto_do_maior_teto']})", teto_ana[it]["teto_pb_max"]),
                    ("maior teto por caneta entre as análogas do tipo, coluna de 20% para todas", teto_ana[it]["teto_20pct_max"])):
        imp.append({"item": it, "hipotese": hip, "status_da_hipotese": "teste (substância não especificada no item)", "preco_contratado": p,
                    "quantidade_contratada": q_, "teto": t_, "contratado_sobre_teto": p / t_, "acima_do_teto": p > t_ + 0.005, "valor_contratado": p * q_,
                    "valor_no_teto": min(p, t_) * q_, "excesso_contratado_sobre_teto": max(p - t_, 0) * q_})
imp = pd.DataFrame(imp)
N["analogas_acima_do_maior_teto_do_tipo"] = bool(imp[imp.item.isin([194, 195])].acima_do_teto.all())
N["analogas_excesso_sobre_o_maior_teto_pb"] = float(imp[imp.item.isin([194, 195]) & imp.hipotese.str.contains("alíquota da PB")].excesso_contratado_sobre_teto.sum())
imp.to_csv(os.path.join(RES, "insulinas_impacto.csv"), index=False, encoding="utf-8")
v_can = float(sum(hom.loc[i, "preco_unitario_homologado"] * hom.loc[i, "quantidade_homologada"] for i in (196, 199)))
exc_doc = float(imp[imp.status_da_hipotese == "documentada"].excesso_contratado_sobre_teto.sum())
N.update({"canetas_valor_contratado": v_can, "canetas_excesso_contratado_sobre_teto_0pct": exc_doc,
          "canetas_excesso_contratado_sobre_teto_20pct": float(imp[imp.status_da_hipotese == "teste de robustez"].excesso_contratado_sobre_teto.sum()),
          "canetas_acima_do_teto_em_todas_as_hipoteses": bool(imp[imp.item.isin([196, 199])].acima_do_teto.all()),
          "canetas_menor_multiplo_sobre_teto": float(imp[imp.item.isin([196, 199])].contratado_sobre_teto.min()),
          "contrato54_valor": float(c54.valor), "contrato54_pago_total": pago54,
          "contrato54_pago_sobre_valor_das_canetas_pct": 100 * pago54 / v_can,
          # limite superior: se TODO o valor pago no contrato 54 fosse de canetas NPH
          "canetas_nph_maximo_possivelmente_pago_unidades": pago54 / float(hom.loc[196, "preco_unitario_homologado"]),
          "canetas_excesso_pago_limite_superior": pago54 * (1 - teto[196]["teto_0pct_max"] / float(hom.loc[196, "preco_unitario_homologado"]))})

# ============================================================ 4. mercado posterior
p26 = pd.read_parquet(os.path.join(EVAL, "organizacional", "pregao_09_2026_itens_resultados.parquet"))
i26b = p26[p26.descricao.str.contains("nsulina")][["numeroItem", "descricao", "unidadeMedida", "quantidade", "valorUnitarioEstimado", "situacaoCompraItemNome",
                                                    "niFornecedor", "valorUnitarioHomologado", "dataResultado"]].copy()
i26b.insert(0, "fonte", "PE 09/2026 — Santa Luzia/PB (mesmo comprador)")
merc = [i26b.rename(columns={"valorUnitarioHomologado": "preco", "descricao": "descricao"})]
bps = pd.read_parquet(os.path.join(EVAL, "nacional", "bps_pos_corte.parquet"))
bps = bps[(bps.data_compra >= HORIZ_INI) & (bps.data_compra <= HORIZ_FIM) & bps.descricao_catmat.str.contains("INSULINA", na=False)
          & bps.descricao_catmat.str.contains("NPH|REGULAR", na=False) & ~bps.flag_preco_extremo]
bp = bps[bps.unidade_fornecimento.fillna("").str.contains("CANETA|SERINGA|SISTEMA|CARPULE|TUBETE|CARTUCHO") | bps.capacidade_descricao.fillna("").str.contains("3,00")]
nb = (bp.groupby(["catmat", "descricao_catmat", "unidade_fornecimento", "capacidade_descricao"], dropna=False).preco_unitario_praticado
      .agg(registros="size", mediana="median", minimo="min", maximo="max").reset_index())
nb.insert(0, "fonte", f"BPS {HORIZ_INI}..{HORIZ_FIM} (unidade com 3 mL/caneta/seringa/tubete — apresentação NÃO confirmada como caneta)")
cg = pd.read_parquet(os.path.join(EVAL, "nacional", "comprasgov_pos_corte.parquet"))
cg = cg[(cg.data_compra >= HORIZ_INI) & (cg.data_compra <= HORIZ_FIM) & cg.descricao_catmat.str.contains("INSULINA", na=False)
        & cg.descricao_catmat.str.contains("NPH|REGULAR", na=False)]
cgp = cg[cg.descricao_catmat.str.contains("SISTEMA DE APLICA", na=False) | cg.descricao_detalhada.fillna("").str.contains("caneta|sistema de aplica", case=False)]
nc = (cgp.groupby(["catmat", "descricao_catmat", "unidade_fornecimento"], dropna=False).preco_unitario_praticado
      .agg(registros="size", mediana="median", minimo="min", maximo="max").reset_index())
nc.insert(0, "fonte", f"Compras.gov.br {HORIZ_INI}..{HORIZ_FIM} (descrição com 'sistema de aplicação' ou 'caneta')")
pd.concat(merc + [nb, nc]).to_csv(os.path.join(RES, "insulinas_mercado_posterior.csv"), index=False, encoding="utf-8")
N["nacional_registros_caneta_comprasgov"] = int(len(cgp))
if len(cgp):
    N["nacional_caneta_comprasgov_mediana"] = float(cgp.preco_unitario_praticado.median())
    for it in (196, 199):
        tp = "NPH" if it == 196 else "REGULAR"
        z = cgp[cgp.descricao_catmat.str.contains(tp)]
        if len(z):
            N[f"nacional_caneta_{tp}_n"] = int(len(z))
            N[f"nacional_caneta_{tp}_mediana"] = float(z.preco_unitario_praticado.median())
            N[f"nacional_caneta_{tp}_frac_ate_teto_0pct"] = float((z.preco_unitario_praticado <= teto[it]["teto_0pct_max"] + 0.005).mean())
            N[f"nacional_caneta_{tp}_frac_ate_teto_20pct"] = float((z.preco_unitario_praticado <= teto[it]["teto_20pct_max"] + 0.005).mean())
            N[f"nacional_caneta_{tp}_maximo"] = float(z.preco_unitario_praticado.max())

# ============================================================ 5. normas do MS (anteriores ao corte)
nm = []
for arq, data in (("ms_nota_tecnica_169_2022_canetas_insulina.pdf", "29/04/2022"), ("ms_nota_tecnica_164_2023_logistica_insulina.pdf", "31/05/2023")):
    cam = os.path.join(PRIM, "normas", arq)
    for i, t in enumerate(paginas_pdf(cam)):
        tt = limpa(t)
        for m_ in re.finditer(r"[^.]{0,200}(aquisi[çc][ãa]o[^.]{0,80}centralizada|centralizada da|70% da demanda total|percentual de 70%)[^.]{0,260}\.", tt, flags=re.I):
            nm.append({"documento": arq, "data": data, "sha256": sha256(cam)[:16], "pagina": i + 1, "trecho": m_.group(0).strip()[:520]})
nm = pd.DataFrame(nm).drop_duplicates("trecho")
nm.to_csv(os.path.join(RES, "insulinas_normas_ms.csv"), index=False, encoding="utf-8")
N["normas_ms_trechos"] = int(len(nm))

# ============================================================ 6. agente × evidência, por insulina
plano = pd.read_csv(os.path.join(SAIDA, "plano_por_item.csv")).set_index("item")
desc26 = {194: "nsulina análoga de ação prolongada", 195: "nsulina análoga de ação rápida", 196: "NPH 100UI/mL- suspensão injetável  3 mL", 197: "NPH 100UI/mL- suspensão injetável (frasco", 198: "Regular 100UI/mL - solução injetável (frasco",
          199: "Regular 100UI/mL - solução injetável 3 mL"}
ax = []
for it in range(194, 200):
    r26 = p26[p26.descricao.str.contains(desc26[it], regex=False)]
    p26h = float(r26.valorUnitarioHomologado.iloc[0]) if len(r26) else np.nan
    pl = plano.loc[it]
    ax.append({"item": it, "descricao": pl.descricao, "quantidade": pl.quantidade_etp, "estimativa_orgao": pl.preco_estimado_orgao,
               "ref_agente": pl.preco_ref_unitario, "faixa_baixo": pl.faixa_preco_baixo, "faixa_alto": pl.faixa_preco_alto, "fonte_ref_agente": pl.fonte_preco_ref,
               "teto_agente": pl.teto_cmed_unitario_aplicavel_max, "homologado_2025": float(hom.loc[it, "preco_unitario_homologado"]),
               "proponentes_2025": prop.get(it, {}).get("proponentes", ""), "homologado_2026_mesmo_comprador": p26h,
               "hom2025_sobre_ref": float(hom.loc[it, "preco_unitario_homologado"]) / pl.preco_ref_unitario,
               "hom2026_sobre_ref": p26h / pl.preco_ref_unitario, "hom2025_sobre_hom2026": float(hom.loc[it, "preco_unitario_homologado"]) / p26h,
               "valor_2025_contratado": float(hom.loc[it, "preco_unitario_homologado"]) * pl.quantidade_etp, "valor_ref_agente": pl.valor_ref_total,
               "valor_a_preco_2026": p26h * pl.quantidade_etp})
ax = pd.DataFrame(ax)
ax.to_csv(os.path.join(RES, "insulinas_agente_x_evidencia.csv"), index=False, encoding="utf-8")
N["insulinas_valor_contratado_2025"] = float(ax.valor_2025_contratado.sum())
N["insulinas_valor_ref_agente"] = float(ax.valor_ref_agente.sum())
N["insulinas_valor_a_preco_2026_mesmo_comprador"] = float(ax.valor_a_preco_2026.sum())

# ============================================================ 7. falhas do pacote apontadas pelo agente
err = pd.read_csv(os.path.join(V2, "ERRATA.csv"))
f = []
# F1: 194/195 — CATMAT de outro tipo de insulina no grupo "compatível"
g1 = pd.read_parquet(os.path.join(V1, "padronizacao", "item_catmat_catalogo_oficial.parquet"))
g1v2 = pd.read_parquet(os.path.join(V2, "padronizacao", "item_catmat_catalogo_oficial.parquet"))
par = lambda t: {(int(a), str(b)) for a, b in zip(t.item, t.catmat) if a in (194, 195)}
removidos = sorted(par(g1) - par(g1v2))
f.append({"falha": "F1", "apontada_pelo_agente": "itens 194/195: o grupo 'compatível' mistura CATMAT de outros tipos de insulina (194 ← 440255, 442012; 195 ← 442012, 468664)",
          "verificacao_independente": f"pares item×CATMAT presentes no v1 e removidos no v2: {removidos}; cada CATMAT removido descreve outro TIPO de insulina",
          "errata": "E-01, E-02", "resultado": "CONFIRMADA — os 4 pares apontados pelo agente são exatamente os 4 removidos pela errata",
          "tratamento_do_agente": "usou só o CATMAT específico (D04) — equivalente à correção", "impacto_na_decisao": "nenhum na ordenação; referências de 194/195 já isoladas"})
# F2: 197 — pré-mistura vinculada como NPH
v1c = pd.read_parquet(os.path.join(V1, "padronizacao", "item_cmed_vinculos.parquet"))
v2c = pd.read_parquet(os.path.join(V2, "padronizacao", "item_cmed_vinculos.parquet"))
a197 = v1c[(v1c.item == 197) & v1c.produto.str.contains("70")][["registro", "produto", "classe"]]
b197 = v2c[(v2c.item == 197) & v2c.produto.str.contains("70")][["registro", "produto", "classe"]]
f.append({"falha": "F2", "apontada_pelo_agente": "item 197 (NPH frasco): vínculo CMED 'exata' com HUMULIN 70N/30R, que é pré-mistura",
          "verificacao_independente": f"v1: {a197[a197.classe.isin(['exata', 'compativel_conversao'])].to_dict('records')}; v2: {b197[b197.registro.isin(a197[a197.classe.isin(['exata', 'compativel_conversao'])].registro)].to_dict('records')}",
          "errata": "E-03, E-04", "resultado": "CONFIRMADA",
          "tratamento_do_agente": "manteve o teto do pacote no plano (R$ 63,46), mas declarou que sem o vínculo o teto é R$ 50,77 e a estimativa do órgão passa a superá-lo",
          "impacto_na_decisao": "nenhum na referência (R$ 26,88); muda a contagem de itens acima do teto (41 → 42)"})
# F3: 268 — teto suspeito
con_sql = None
it268 = pd.read_parquet(os.path.join(V1, "organizacional", "itens_santa_luzia.parquet")).set_index("item").loc[268]
vinc = v1c[(v1c.item == 268) & v1c.classe.isin(["exata", "compativel_conversao"])]
pre = pd.read_parquet(os.path.join(V1, "nacional", "cmed_2025_01_precos.parquet"))
pr268 = pre[pre.registro.isin(vinc.registro) & pre.aliquota_aplicavel_pb & (pre.tipo_preco == "PF")].merge(vinc[["registro", "produto", "apresentacao", "fator_conversao"]], on="registro")
pr268["teto_por_unidade"] = pr268.valor_embalagem / pr268.fator_conversao
ex268 = pr268.sort_values("teto_por_unidade").head(3)[["produto", "apresentacao", "fator_conversao", "valor_embalagem", "teto_por_unidade"]].to_dict("records")
f.append({"falha": "F3", "apontada_pelo_agente": "item 268 (ondansetrona ampola): menor teto 31× a mediana praticada — 'sugere erro de fator de conversão'",
          "verificacao_independente": f"item: {it268.descricao}; {len(pr268)} vínculos PF na alíquota da PB; menores tetos por unidade: {ex268}; "
                                      f"mediana praticada usada pelo agente: {float(plano.loc[268, 'preco_ref_unitario']):.2f}",
          "errata": "nenhuma", "resultado": "NÃO CONFIRMADA como erro de conversão: o fator bate com a apresentação; o PF da CMED é que fica dezenas de vezes acima do preço praticado",
          "tratamento_do_agente": "marcou o teto como suspeito e tirou o item do modelo de desconto (E2), que passou a precificá-lo pelo E1",
          "impacto_na_decisao": "conservador para o E2 (reduz o custo modelado do E2); não altera a ordenação"})
# F4: Convênio 87/02 — coluna de 20%
f.append({"falha": "F4", "apontada_pelo_agente": "produtos do Convênio ICMS 87/02: o pacote não publica o teto a 20% (2.810 registros)",
          "verificacao_independente": f"na lista CMED BRUTA de 06/01/2025, os {N['cmed_registros_convenio_87']} registros do Convênio trazem a coluna 'PF 20%' preenchida com asterisco "
                                      f"em {N['cmed_conv87_pf20_com_asterisco']} casos (ex.: NOVOLIN N FlexPen '25,18*'); como número puro, em {N['cmed_conv87_pf20_numerico_puro']}. "
                                      f"O valor existe na fonte, marcado com '*'; o pacote o descartou na leitura. Nota (viii) da lista: {nota_viii[:260]}",
          "errata": "E-05 (nota no LEIA-ME: 'fonte, não falha')",
          "resultado": "CONFIRMADA como lacuna do PACOTE; a fonte bruta publica o valor a 20% com asterisco (divergência em relação à nota E-05)",
          "tratamento_do_agente": "declarou a lacuna e usou a alíquota 0% (mais restritiva) como teto",
          "impacto_na_decisao": f"com a coluna de 20%, o teto das canetas iria a R$ {teto[196]['teto_20pct_max']:.2f} (NPH) e R$ {teto[199]['teto_20pct_max']:.2f} (Regular); "
                                f"o contratado continua {float(hom.loc[196, 'preco_unitario_homologado']) / teto[196]['teto_20pct_max']:.1f}× e "
                                f"{float(hom.loc[199, 'preco_unitario_homologado']) / teto[199]['teto_20pct_max']:.1f}× acima"})
pd.DataFrame(f).to_csv(os.path.join(RES, "falhas_pacote_verificacao_independente.csv"), index=False, encoding="utf-8")
json.dump(N, open(os.path.join(RES, "insulinas_numeros.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30); pd.set_option("display.max_colwidth", 110)
print(ev.groupby(["documento", "item", "unidade_no_trecho"]).size().to_string())
print(ins[["PRODUTO", "APRESENTAÇÃO", "tipo", "tem_sistema_aplicacao", "n_unidades", "CAP", "PF 0%", "PF 20%", "PMVG 0%", "tipo_teto",
           "teto_aplicavel_0pct_por_unidade", "teto_aplicavel_20pct_por_unidade"]].to_string(index=False))
print(imp[["item", "hipotese", "teto", "contratado_sobre_teto", "acima_do_teto", "excesso_contratado_sobre_teto"]].round(2).to_string(index=False))
print(ax[["item", "estimativa_orgao", "ref_agente", "faixa_alto", "teto_agente", "homologado_2025", "proponentes_2025", "homologado_2026_mesmo_comprador",
          "hom2025_sobre_ref", "hom2026_sobre_ref"]].round(2).to_string(index=False))
print(nc.to_string(index=False) if len(nc) else "sem registros Compras.gov.br de caneta")
print(nm[["documento", "pagina", "trecho"]].to_string(index=False, max_colwidth=230))
for k, v_ in N.items():
    print(k, ":", v_)
for r_ in f:
    print(r_["falha"], "|", r_["resultado"], "|", r_["verificacao_independente"][:600])
