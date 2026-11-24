"""Pré-Etapa 5 — unidade de fornecimento das insulinas em caneta (itens 194, 195, 196 e 199 do PE 04/2025):
evidências documentais conferidas por trecho e página, compatibilidade com a CMED (jan/2025) e impacto na avaliação.
Não altera etapa4/ nem as saídas de etapa5/avaliacao/; grava em etapa5/avaliacao_canetas/.

Uso: python -I -X utf8 scripts/34_canetas_insulina.py <raiz_projeto>
Requer os documentos baixados do PNCP em data/raw/pncp/etapa2/09090689000167_2025_6/docs/ (edital, contratos, aditivo, atas)
e data/raw/pncp/etapa2/09090689000167_2026_26/docs/09_extraido/ (ata do PE 09/2026, só contexto).
"""
import json, os, re, sys
import numpy as np, pandas as pd
from pypdf import PdfReader

ROOT = os.path.abspath(sys.argv[1])
P25 = os.path.join(ROOT, "data", "raw", "pncp", "etapa2", "09090689000167_2025_6")
P26 = os.path.join(ROOT, "data", "raw", "pncp", "etapa2", "09090689000167_2026_26")
OUT = os.path.join(ROOT, "etapa5", "avaliacao_canetas")
os.makedirs(OUT, exist_ok=True)
CANETAS = {194: "ANÁLOGA DE AÇÃO PROLONGADA", 195: "ANÁLOGA DE AÇÃO RÁPIDA", 196: "NPH", 199: "REGULAR"}
_cache = {}


def paginas(rel):
    if rel not in _cache:
        _cache[rel] = [re.sub(r"\s+", " ", p.extract_text() or "") for p in PdfReader(os.path.join(ROOT, rel)).pages]
    return _cache[rel]


def achar(rel, padrao, faixa):
    """primeira página (1-based) da faixa cujo texto contém o padrão; o trecho encontrado é devolvido como evidência"""
    for pg in faixa:
        m = re.search(padrao, paginas(rel)[pg - 1], re.I)
        if m:
            return pg, m.group(0)
    raise AssertionError(f"evidência não encontrada: {rel} {padrao}")


D25 = os.path.relpath(os.path.join(P25, "docs"), ROOT).replace("\\", "/")
EDITAL, CONTRATO, ADITIVO = f"{D25}/01_edital.pdf", f"{D25}/05_arquivo.pdf", f"{D25}/12_aditivo.pdf"
ATA = f"{D25}/16_extraido/Ata Final.pdf"
ATA26 = os.path.relpath(os.path.join(P26, "docs", "09_extraido", "Ata Final.pdf"), ROOT).replace("\\", "/")

E = []
def ev(id_, documento, arq, faixa, itens_pad, unidade, obs=""):
    for it, pad in itens_pad:
        pg, trecho = achar(arq, pad, faixa)
        E.append(dict(id=id_, documento=documento, arquivo=arq, pagina=pg, item=it, trecho_verificado=trecho, unidade_no_documento=unidade, observacao=obs))

linhas_edital = [(194, r"prolongada 100UI/mL Solução Injetável com sistema de aplicação 3ml Caneta 100"),
                 (195, r"rápida 100UI/mL Solução Injetável com sistema de aplicação 3ml Caneta 100"),
                 (196, r"NPH 100UI/mL - suspensão injetável 3 mL com sistema de aplicação caneta 6\.000"),
                 (199, r"Regular 100UI/mL - solução injetável 3 mL com sistema de aplicação caneta 1\.200")]
ev("D1", "Edital PE 04/2025 — Anexo I, Estudo Técnico Preliminar (tabela ITEM/DESCRIÇÃO/UNID./QUANT.)", EDITAL, range(19, 30), linhas_edital, "Caneta",
   "documento assinado em 29/01/2025 e publicado no PNCP em 30/01/2025")
ev("D2", "Edital PE 04/2025 — Anexo II, Termo de Referência (mesma tabela)", EDITAL, range(30, 47), linhas_edital, "Caneta")
ev("D3", "Ata Final do pregão (Portal de Compras Públicas) — quadro de itens homologados", ATA, range(1, 20),
   [(194, r"R\$ 195,68 100 UN"), (195, r"R\$ 194,76 100 UN"), (196, r"R\$ 193,02 6\.000 UN"), (199, r"R\$ 147,36 1\.200 UN")], "UN")
ev("D4", "Ata Final — resultado por fornecedor (modelo e marca/fabricante)", ATA, range(20, 40),
   [(194, r"EQUIPLEX EQUIPLEX 195,68 100 19\.568,00"), (195, r"EQUIPLEX EQUIPLEX 194,76 100 19\.476,00"),
    (196, r"EQUIPLEX EQUIPLEX 193,02 6\.000 1\.158\.120,00"), (199, r"EQUIPLEX EQUIPLEX 147,36 1\.200 176\.832,00")], "—",
   "proposta da ALLFAMED (CNPJ 31.187.918/0001-15); 'Modelo' e 'Marca/Fabricante' = EQUIPLEX")
ev("D5", "Ata Final — propostas e lances por item", ATA, range(100, 130),
   [(196, r"EQUIPLEX EQUIPLEX 6\.000 R\$193,02"), (199, r"EQUIPLEX EQUIPLEX 1\.200 R\$147,36")], "—")
ev("D6", "Contrato Administrativo nº 00054/2025 (ALLFAMED) — quadro de itens", CONTRATO, range(1, 21),
   [(194, r"100 Caneta 195,68"), (195, r"100 Caneta 194,76"), (196, r"6\.000 caneta 193,02"), (199, r"1\.200 caneta 147,36")], "Caneta")
ev("D7", "Termo Aditivo nº 01 ao Contrato nº 00054/2025 — quadro de itens", ADITIVO, range(1, 7),
   [(194, r"100 Caneta 195\.68 19\.568,00"), (195, r"100 Caneta 194,76 19\.476,00"), (196, r"6\.000 caneta 193,02 1\.158\.120,00"),
    (199, r"1\.200 caneta 147?,?36 176\.832")], "Caneta", "texto obtido por OCR do PDF ('14736' = 147,36)")

# quantas propostas houve para cada caneta (seção de propostas da ata: blocos entre '0NNN -' consecutivos)
txt = " ".join(paginas(ATA)[260:290])
n_prop = {}
for it in CANETAS:
    m = re.search(rf"0{it} - .*?(?= 0{it + 1} - )", txt)
    n_prop[it] = len(re.findall(r"\(proposta\)", m.group(0))) if m else None
# registro do item no PNCP e resultado
itens = {x["numeroItem"]: x for x in json.load(open(os.path.join(P25, "itens_p1.json"), encoding="utf-8"))}
for it in CANETAS:
    r_ = json.load(open(os.path.join(P25, f"resultado_item_{it}.json"), encoding="utf-8"))[0]
    E.append(dict(id="D8", documento="PNCP — cadastro do item e resultado (API)", arquivo=os.path.relpath(os.path.join(P25, "itens_p1.json"), ROOT).replace("\\", "/"),
                  pagina=None, item=it, trecho_verificado=f"unidadeMedida={itens[it]['unidadeMedida']}; quantidade={itens[it]['quantidade']:g}; "
                  f"homologado={r_['valorUnitarioHomologado']} × {r_['quantidadeHomologada']:g}; percentualDesconto={r_['percentualDesconto']}",
                  unidade_no_documento=itens[it]["unidadeMedida"], observacao=f"propostas registradas na ata para o item: {n_prop[it]}"))
EV = pd.DataFrame(E)
EV.to_csv(os.path.join(OUT, "evidencias_documentais.csv"), index=False, encoding="utf-8")

# ---------------- CMED jan/2025: canetas compatíveis por tipo ----------------
DI = os.path.join(ROOT, "data", "decision_input", "nacional")
A = pd.read_parquet(os.path.join(DI, "cmed_2025_01_apresentacoes.parquet"))
PR = pd.read_parquet(os.path.join(DI, "cmed_2025_01_precos.parquet"))
eq = A[A.laboratorio.str.contains("EQUIPLEX", case=False, na=False)]
eq_insulina = int(eq.substancia.str.contains("INSULINA", case=False, na=False).sum())
ins = A[A.substancia.str.contains("INSULINA", case=False, na=False) & ~A.substancia.str.contains(";", na=False)].copy()
ins = ins[ins.apresentacao.str.contains(r"SIST\s*APLIC|CAN APLIC", case=False, na=False)]           # só com sistema/caneta de aplicação
ins = ins[ins.apresentacao.str.contains(r"\b100 U", case=False) & ins.apresentacao.str.contains(r"3\s*ML", case=False)]
ins = ins[~ins.produto.str.contains(r"MIX|70|30", case=False, na=False)]                            # exclui pré-misturas
def tipo(r):
    s, a = r.substancia.upper(), r.apresentacao.upper()
    if "HUMANA" in s:
        return "NPH" if " SUS " in f" {a} " else "REGULAR"
    if any(k in s for k in ("GLARGINA", "DETEMIR", "DEGLUDECA")):
        return "ANÁLOGA DE AÇÃO PROLONGADA"
    if any(k in s for k in ("ASPARTE", "LISPRO", "GLULISINA")):
        return "ANÁLOGA DE AÇÃO RÁPIDA"
ins["tipo"] = ins.apply(tipo, axis=1)
ins["canetas"] = ins.apresentacao.str.extract(r"CT\s+(\d+)\s+CARP?\b", flags=re.I)[0].astype(float).fillna(1.0)
teto = PR[PR.aliquota_aplicavel_pb & ((PR.tipo_preco == "PMVG") == PR.cap)][["registro", "tipo_preco", "aliquota_icms", "valor_embalagem"]]
C = ins.merge(teto, on="registro")
C["teto_por_caneta"] = C.valor_embalagem / C.canetas
C = C[["tipo", "registro", "laboratorio", "produto", "apresentacao", "canetas", "cap", "tipo_preco", "aliquota_icms", "valor_embalagem", "teto_por_caneta"]].sort_values(["tipo", "teto_por_caneta"])
C.to_csv(os.path.join(OUT, "cmed_canetas_compativeis.csv"), index=False, encoding="utf-8")

# ---------------- impacto na avaliação ----------------
CI = pd.read_csv(os.path.join(ROOT, "etapa5", "avaliacao", "comparacao_itens.csv")).set_index("item")
I = []
for it, tp in CANETAS.items():
    c = C[C.tipo == tp]
    hom, q = CI.loc[it, "preco_unitario_homologado"], CI.loc[it, "quantidade_homologada"]
    tmin, tmax = c.teto_por_caneta.min(), c.teto_por_caneta.max()
    cx5 = c[c.canetas == 5].valor_embalagem
    I.append(dict(item=it, tipo=tp, unidade_documentada="caneta (D1, D2, D6, D7) / UN (D3)", quantidade=q, preco_homologado=hom,
                  propostas_no_certame=n_prop[it], marca_declarada="EQUIPLEX (sem insulina na CMED)", referencia_agente=CI.loc[it, "preco_ref_unitario"],
                  canetas_cmed_compativeis=len(c), teto_por_caneta_min=tmin, teto_por_caneta_max=tmax,
                  razao_hom_sobre_teto_max=hom / tmax, excesso_sobre_teto_max=max(0.0, (hom - tmax) * q),
                  hipotese_nao_documentada_caixa5_teto_max=cx5.max() if len(cx5) else np.nan,
                  hipotese_caixa5_razao=hom / cx5.max() if len(cx5) else np.nan,
                  teto_usado_na_avaliacao=CI.loc[it, "teto_cmed_unitario_aplicavel_max"]))
IM = pd.DataFrame(I)
IM.to_csv(os.path.join(OUT, "impacto_canetas.csv"), index=False, encoding="utf-8")

# correção do indicador C4 (homologado acima do teto): 194 e 195 não tinham teto no pacote; agora comparados ao MAIOR teto
# por caneta entre as apresentações CMED compatíveis com o tipo (critério mais favorável à decisão real)
ant = CI[CI.hom_acima_teto]
novos = IM[(IM.item.isin([194, 195])) & (IM.razao_hom_sobre_teto_max > 1)]
exc_ant = float(((ant.preco_unitario_homologado - ant.teto_cmed_unitario_aplicavel_max) * ant.quantidade_homologada).sum())
C4 = pd.DataFrame([dict(indicador="itens homologados acima do teto CMED (jan/2025)", avaliacao_original=len(ant), corrigido=len(ant) + len(novos),
                        itens_acrescentados=str(novos.item.tolist()), excesso_original=exc_ant, excesso_corrigido=exc_ant + float(novos.excesso_sobre_teto_max.sum()),
                        criterio="194/195 sem teto no pacote (item não especifica a substância): comparados ao maior teto por caneta entre as apresentações compatíveis do tipo")])
C4.to_csv(os.path.join(OUT, "correcao_C4.csv"), index=False, encoding="utf-8")

# contexto pós-PE 04/2025 (não usado em cálculo): propostas do PE 09/2026 para os mesmos itens
ctx = []
if os.path.exists(os.path.join(ROOT, ATA26)):
    t26 = " ".join(paginas(ATA26)[110:130])
    for it26, it25 in ((191, 196), (194, 199), (189, 194), (190, 195)):
        m = re.search(rf"0{it26} - .*?(?= 0{it26 + 1} - )", t26)
        if m:
            ctx.append(dict(item_pe_09_2026=it26, item_pe_04_2025=it25, bloco_de_propostas=m.group(0)[:900]))
pd.DataFrame(ctx).to_csv(os.path.join(OUT, "contexto_pe_09_2026.csv"), index=False, encoding="utf-8")

# ---------------- autoverificação ----------------
assert set(EV[EV.unidade_no_documento.isin(["Caneta", "UN"])].item) == set(CANETAS)          # todo documento com unidade diz caneta/UN
assert not EV.trecho_verificado.str.contains(r"\bcaixa\b|\bcx\b", case=False).any()
assert eq_insulina == 0 and len(eq) > 0
assert all(n == 1 for n in n_prop.values()), n_prop
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 90)
print(EV[["id", "pagina", "item", "unidade_no_documento", "trecho_verificado"]].to_string(index=False))
print("propostas por item:", n_prop, "| EQUIPLEX na CMED:", len(eq), "registros, insulina:", eq_insulina)
print(C.groupby("tipo").teto_por_caneta.agg(["count", "min", "max"]).round(2).to_string())
print(IM.drop(columns=["unidade_documentada", "marca_declarada"]).round(2).to_string(index=False))
print(C4.to_string(index=False))
print("contexto 2026:", len(ctx), "blocos")
