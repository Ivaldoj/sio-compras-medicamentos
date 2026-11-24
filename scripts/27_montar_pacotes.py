"""Etapa 3 (+ pré-Etapa 4) — monta data/decision_input (só pré-corte) e data/evaluation_only (reservado), mais o manifesto.
Uso: python -I -X utf8 27_montar_pacotes.py <raiz_projeto>
Requer as saídas dos scripts 24, 25 e (opcionais) 26 e 29. Regras CMED citadas da própria lista (06/01/2025); alíquota de ICMS
da PB pela Lei 6.379/96 art. 11, I (20% desde 01/01/2024) e isenção do Convênio ICMS 87/02 (doc 18)."""
import glob, hashlib, io, json, os, re, sys, datetime, zipfile
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from padroniza import embalagem_cmed, conteudo_item, forma, norm, mesmo_medicamento

ROOT = sys.argv[1]
CUT = "2025-01-29"
D = lambda *p: os.path.join(ROOT, "data", *p)
DI, EV = D("decision_input"), D("evaluation_only")
for p in ("organizacional", "nacional", "padronizacao"):
    os.makedirs(os.path.join(DI, p), exist_ok=True)
for p in ("organizacional", "nacional", "auditoria"):
    os.makedirs(os.path.join(EV, p), exist_ok=True)
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")

# ---------- CMED jan/2025: apresentações e preços (formato longo) ----------
c = pd.read_parquet(D("processed", "cmed_pmvg_20250107.parquet"))
sn = lambda s: s.fillna("").str.strip()
cap, icms0, cfz = sn(c.CAP).eq("Sim"), sn(c["ICMS 0%"]).eq("Sim"), sn(c["CONFAZ 87"]).eq("Sim")
emb = c["APRESENTAÇÃO"].map(embalagem_cmed)
A = pd.DataFrame({"registro": c.reg, "codigo_ggrem": c["CÓDIGO GGREM"], "ean1": c["EAN 1"], "substancia": c["SUBSTÂNCIA"],
                  "laboratorio_cnpj": c.CNPJ.str.replace(r"\D", "", regex=True), "laboratorio": c["LABORATÓRIO"], "produto": c.PRODUTO,
                  "apresentacao": c["APRESENTAÇÃO"].str.strip(), "classe_terapeutica": c["CLASSE TERAPÊUTICA"],
                  "tipo_produto": c["TIPO DE PRODUTO (STATUS DO PRODUTO)"], "regime_preco": c["REGIME DE PREÇO"],
                  "restricao_hospitalar": sn(c["RESTRIÇÃO HOSPITALAR"]), "cap": cap, "icms_isento_so_0pct": icms0, "convenio_confaz_87": cfz,
                  "lista_pis_cofins": sn(c["LISTA DE CONCESSÃO DE CRÉDITO TRIBUTÁRIO (PIS/COFINS)"]),
                  "tarja": c.TARJA, "recipientes_por_embalagem": emb.map(lambda e: e["recipientes"]),
                  "volume_por_recipiente": emb.map(lambda e: f"{e['volume'][0]:g} {e['volume'][1]}" if e["volume"] else None),
                  "unidades_solidas_por_embalagem": emb.map(lambda e: e["unidades_solidas"]), "embalagem_composta": emb.map(lambda e: e["composta"])})
A["teto_compras_administrativas"] = A.cap.map({True: "PMVG", False: "PF"})
# alíquota de ICMS aplicável a uma compra do município de Santa Luzia/PB (destino PB; comprador = administração pública municipal)
BASE_ISENTO = "isento de ICMS (coluna 'ICMS 0%' = Sim na lista CMED)"
BASE_C87 = ("Convênio ICMS 87/02, cl. 1ª: isenção nas operações destinadas à administração pública municipal (prorrogado até 30/04/2026 "
            "pelo Conv. ICMS 226/23); CMED/Acórdão TCU 140/2012: preço com desoneração; condições do §1º, I–II, não verificadas por produto")
BASE_20 = "Lei 6.379/96 (PB), art. 11, I: 20% nas operações internas desde 01/01/2024 (Lei 12.788/23); CMED: usar a alíquota da UF de destino"
A["aliquota_icms_pb"] = ["0%" if i0 or cf else "20%" for i0, cf in zip(icms0, cfz)]
A["base_aliquota_pb"] = [BASE_ISENTO if i0 else (BASE_C87 if cf else BASE_20) for i0, cf in zip(icms0, cfz)]
A["fonte"] = "CMED/Anvisa — Lista PF/PMVG publicada em 06/01/2025 14h00 (arquivo xls_conformidade_gov_20250107)"
A["data_disponibilidade"] = pd.Timestamp("2025-01-06")
A.to_parquet(os.path.join(DI, "nacional", "cmed_2025_01_apresentacoes.parquet"), index=False)
L = []
for col in [x for x in c.columns if x.startswith(("PF ", "PMVG "))]:
    tipo, aliq = col.split(" ", 1)
    aliq = aliq.replace("Impostos", "Imposto").replace("%2", "%").strip()
    v = pd.DataFrame({"registro": c.reg, "tipo_preco": tipo, "aliquota_icms": aliq, "valor_embalagem": c[col], "cap": cap, "icms0": icms0, "cfz": cfz})
    L.append(v[v.valor_embalagem.notna()])
P = pd.concat(L, ignore_index=True)
P["aplicabilidade"] = [("teto obrigatório (produto com CAP)" if cp else "somente compras por força de decisão judicial") if t == "PMVG"
                       else ("não é o teto para governo: produto com CAP usa PMVG" if cp else "teto para compras administrativas")
                       for t, cp in zip(P.tipo_preco, P.cap)]
P["aliquota_aplicavel_pb"] = [a == ("0%" if (i0 or cf) else "20%") for a, i0, cf in zip(P.aliquota_icms, P.icms0, P.cfz)]
P["aliquota_status"] = ["sem tributos — referência, não teto por alíquota" if a == "Sem Imposto" else
                        ("aplicável na PB: " + (BASE_ISENTO if i0 else (BASE_C87 if cf else BASE_20))) if ok else
                        ("não aplicável: compra pública isenta (Conv. ICMS 87/02)" if cf else "não aplicável na PB (alíquota de outra UF ou de área de livre comércio)")
                        for a, ok, i0, cf in zip(P.aliquota_icms, P.aliquota_aplicavel_pb, P.icms0, P.cfz)]
P["categoria_valor"] = "limite_regulatorio_por_embalagem (não é preço praticado)"
P["data_disponibilidade"] = pd.Timestamp("2025-01-06"); P["base_disponibilidade"] = "publicação da lista CMED (06/01/2025)"
P = P.drop(columns=["icms0", "cfz"])
P.to_parquet(os.path.join(DI, "nacional", "cmed_2025_01_precos.parquet"), index=False)
print("CMED: apresentações", len(A), "| linhas de preço", len(P), "| alíquota PB:", A.aliquota_icms_pb.value_counts().to_dict())

# ---------- organizacional: itens e histórico próprio ----------
I = pd.read_parquet(D("processed", "etapa3", "itens_atributos.parquet"))
V = pd.read_parquet(os.path.join(DI, "padronizacao", "item_cmed_vinculos.parquet"))
f_desc = I.descricao.map(lambda s: forma(s)[0]); f_unid = I.unidade.map(lambda s: forma(s)[0])
I["inconsistencia_unidade"] = (f_desc.notna() & f_unid.notna() & (f_desc != f_unid) & ~I.descricao.map(lambda s: "caps" in norm(s) and "comp" in norm(s)))
# compatibilidade BPS por grupo (CATMAT × unidade × capacidade)
bps = pd.read_parquet(os.path.join(DI, "nacional", "bps_precos_praticados.parquet"),
                      columns=["catmat", "unidade_fornecimento", "capacidade_descricao", "data_compra", "uf", "preco_unitario_praticado", "flag_preco_extremo"])
g = bps.groupby(["catmat", "unidade_fornecimento", "capacidade_descricao"], dropna=False).agg(
    registros=("uf", "size"), ufs=("uf", "nunique"), compra_min=("data_compra", "min"), compra_max=("data_compra", "max")).reset_index()
cand = pd.read_parquet(os.path.join(DI, "padronizacao", "item_catmat_candidatos.parquet"))
cand = cand[cand.nivel == "atributos_compativeis"][["item", "catmat"]]
G = cand.merge(g, on="catmat").merge(I[["item", "descricao", "unidade", "forma"]], on="item")
SOL = {"COMPRIMIDO", "CÁPSULA", "DRÁGEA", "COMPRIMIDO REVESTIDO", "CAPSULA", "DRAGEA"}
def comp_bps(r):
    if r.forma in ("comprimido", "capsula"):
        return "compativel" if str(r.unidade_fornecimento).upper() in SOL else "incompativel_unidade"
    vi = conteudo_item(r.descricao)
    m = re.search(r"(\d+(?:,\d+)?)\s*(ML|G)\b", str(r.capacidade_descricao or "").upper())
    if not vi:
        return "conteudo_item_nao_extraido"
    if not m:
        return "capacidade_nao_informada"
    return "compativel" if (float(m.group(1).replace(",", ".")), m.group(2).lower()) == vi else "incompativel_capacidade"
G["compatibilidade"] = G.apply(comp_bps, axis=1)
G.drop(columns=["descricao", "unidade", "forma"]).to_parquet(os.path.join(DI, "padronizacao", "item_bps_grupos.parquet"), index=False)
ok = G[G.compatibilidade == "compativel"]
I["bps_registros_compativeis"] = I["item"].map(ok.groupby("item").registros.sum()).fillna(0).astype(int)
I["bps_registros_a_conferir"] = I["item"].map(G[G.compatibilidade.isin(["capacidade_nao_informada", "conteudo_item_nao_extraido"])].groupby("item").registros.sum()).fillna(0).astype(int)
bmed = ok[["item", "catmat", "unidade_fornecimento", "capacidade_descricao"]].merge(bps[~bps.flag_preco_extremo], on=["catmat", "unidade_fornecimento", "capacidade_descricao"]) \
    .groupby("item").preco_unitario_praticado.median()
# Compras.gov.br (script 29): registros pré-corte por item, com compatibilidade por registro
cgp = os.path.join(DI, "padronizacao", "item_comprasgov_registros.parquet")
CG = pd.read_parquet(cgp) if os.path.exists(cgp) else pd.DataFrame(columns=["item", "compatibilidade"])
I["comprasgov_registros_compativeis"] = I["item"].map(CG[CG.compatibilidade == "compativel"].groupby("item").size()).fillna(0).astype(int)
I["comprasgov_registros_a_conferir"] = I["item"].map(CG[CG.compatibilidade.str.startswith("a_conferir")].groupby("item").size()).fillna(0).astype(int)
for k in ("exata", "compativel_conversao", "provavel_conferencia", "indeterminada", "incompativel"):
    I[f"cmed_{k}"] = I["item"].map(V[V.classe == k].groupby("item").size()).fillna(0).astype(int)
cv = V[V.classe.isin(["exata", "compativel_conversao"])].merge(A[["registro", "cap"]], on="registro")
I["cmed_alguma_com_cap"] = I["item"].isin(cv[cv.cap]["item"])
pi_path = os.path.join(DI, "nacional", "pncp_comparaveis_itens.parquet")
if os.path.exists(pi_path):
    pit = pd.read_parquet(pi_path).dropna(subset=["itens_caso_comparaveis"])
    pit = pit.assign(item=pit.itens_caso_comparaveis.str.split("|")).explode("item"); pit["item"] = pit["item"].astype(int)
    I["pncp_itens_comparaveis"] = I["item"].map(pit.groupby("item").size()).fillna(0).astype(int)
    I["pncp_itens_com_preco_estimado"] = I["item"].map(pit[pit.preco_unitario_estimado > 0].groupby("item").size()).fillna(0).astype(int)
    prs = os.path.join(DI, "nacional", "pncp_comparaveis_resultados.parquet")
    rs = pd.read_parquet(prs) if os.path.exists(prs) else pd.DataFrame(columns=["numero_controle_pncp", "numero_item"])
    j = pit.merge(rs, on=["numero_controle_pncp", "numero_item"])
    I["pncp_resultados_disponiveis"] = I["item"].map(j.groupby("item").size()).fillna(0).astype(int)
else:
    I["pncp_itens_comparaveis"] = 0; I["pncp_itens_com_preco_estimado"] = 0; I["pncp_resultados_disponiveis"] = 0
I["status_necessidade"] = "documentada (TR) — consumo que a sustenta ausente"
I["status_identificacao"] = I.catmat_status.map({"unico": "validada por atributos (1 CATMAT)", "multiplo": "validada por atributos (vários CATMAT equivalentes)",
                                                 "parcial": "incompleta (forma não confirmada)", "nao_identificado": "ausente"})
I["status_preco_praticado"] = ["disponível" if b > 0 or p > 0 or cg > 0 else ("a conferir" if a > 0 or cga > 0 else "ausente")
                               for b, p, cg, a, cga in zip(I.bps_registros_compativeis, I.pncp_resultados_disponiveis, I.comprasgov_registros_compativeis,
                                                           I.bps_registros_a_conferir, I.comprasgov_registros_a_conferir)]
I["fontes_preco_praticado"] = ["|".join(f for f, n in (("BPS", b), ("Compras.gov.br", cg), ("PNCP", p)) if n > 0) or None
                               for b, cg, p in zip(I.bps_registros_compativeis, I.comprasgov_registros_compativeis, I.pncp_resultados_disponiveis)]
I["status_teto_cmed"] = ["disponível (conversão por regra)" if e + cc > 0 else ("a conferir" if p + d > 0 else ("bloqueado/incompatível" if inc > 0 else "ausente"))
                         for e, cc, p, d, inc in zip(I.cmed_exata, I.cmed_compativel_conversao, I.cmed_provavel_conferencia, I.cmed_indeterminada, I.cmed_incompativel)]

# ---------- padronização: regras de conversão aceitas + verificação (pré-Etapa 4) ----------
R = V[V.classe.isin(["exata", "compativel_conversao"])][["item", "registro", "apresentacao", "classe", "unidade_origem", "unidade_destino", "fator_conversao", "justificativa"]].copy()
R["regra"] = R.classe.map({"exata": "R0: embalagem contém exatamente 1 unidade do item (mesmo princípio, concentração, forma e conteúdo)",
                           "compativel_conversao": "R1 (sólidos): unidades = n de 'X n' [× n de 'CT n BL'] | R2 (recipientes): unidades = n de 'CT n FA/AMP/FR…' com mesmo volume/massa por recipiente"})
teto = P[P.aliquota_aplicavel_pb & ((P.tipo_preco == "PMVG") == P.cap)].drop_duplicates("registro").set_index("registro")
R["teto_tipo"] = R.registro.map(teto.tipo_preco); R["teto_aliquota_pb"] = R.registro.map(teto.aliquota_icms)
R["teto_unitario_pb"] = R.registro.map(teto.valor_embalagem) / R.fator_conversao
R["razao_mediana_item"] = R.teto_unitario_pb / R.groupby("item").teto_unitario_pb.transform("median")
R["verif_consistencia_interna"] = ["sem teto na alíquota aplicável" if pd.isna(x) else ("ok" if 0.25 <= x <= 4 else "alerta: teto unitário fora de 0,25–4× a mediana do item")
                                   for x in R.razao_mediana_item]
rb = R["item"].map(bmed) / R.teto_unitario_pb
R["verif_preco_praticado"] = ["sem preço praticado BPS para comparar" if pd.isna(x) else ("alerta: preço praticado mediano > 2× o teto unitário" if x > 2 else
                              ("alerta: teto unitário > 50× o preço praticado mediano" if x < 0.02 else "ok")) for x in rb]
nd, na = R["item"].map(I.set_index("item").descricao).map(norm), R.apresentacao.map(norm)
fa_item = nd.str.contains(r"frasco.?ampola")
R["ressalva_recipiente"] = [("item pede ampola; apresentação em frasco-ampola" if (re.search(r"\bampola\b", d) and not f and re.search(r"\bfa\b", a)) else
                             ("item pede frasco-ampola; apresentação em ampola" if f and re.search(r"\bamp\b", a) else None)) for d, a, f in zip(nd, na, fa_item)]
insp = pd.read_csv(os.path.join(ROOT, "reports", "pre4_inspecao_conversoes_amostra.csv"), dtype={"registro": str})
R = R.merge(insp[["item", "registro", "veredito"]].rename(columns={"veredito": "inspecao_amostral_ia"}), on=["item", "registro"], how="left")
alerta = R.verif_consistencia_interna.str.startswith("alerta") | R.verif_preco_praticado.str.startswith("alerta") | R.ressalva_recipiente.notna()
R["status"] = ["aceita por regra; verificação automática COM ALERTA (conferir); validação humana pendente" if a_ else
               "aceita por regra; verificação automática sem alerta; validação humana pendente" for a_ in alerta]
R.to_csv(os.path.join(DI, "padronizacao", "regras_conversao.csv"), index=False)
print("conversões aceitas:", len(R), "| com alerta:", int(alerta.sum()), "| inspecionadas (amostra IA):", int(R.inspecao_amostral_ia.notna().sum()))
# teto unitário por item (faixa entre vínculos aceitos, alíquota PB) e posição da estimativa do órgão
tu = R.groupby("item").teto_unitario_pb.agg(["min", "max"])
I["teto_cmed_unitario_pb_min"] = I["item"].map(tu["min"]); I["teto_cmed_unitario_pb_max"] = I["item"].map(tu["max"])
I["estimativa_sobre_teto_max"] = I.preco_unitario_estimado_orgao / I.teto_cmed_unitario_pb_max
I["alerta_estimativa_acima_teto_cmed"] = I.estimativa_sobre_teto_max > 1

# histórico próprio: pregões 01/2024 e 12/2024 (PNCP) — informação interna anterior ao corte
H = []
for pasta, pe in (("09090689000167_2024_1", "PE 01/2024"), ("09090689000167_2024_14", "PE 12/2024")):
    d = D("raw", "pncp", "etapa2", pasta)
    comp = json.load(open(os.path.join(d, "compra.json"), encoding="utf8"))
    res = {}
    for f in glob.glob(os.path.join(d, "resultado_item_*.json")):
        for r_ in json.load(open(f, encoding="utf8")) or []:
            res[r_["numeroItem"]] = r_
    for i in json.load(open(os.path.join(d, "itens_p1.json"), encoding="utf8")):
        r_ = res.get(i["numeroItem"], {})
        H.append(dict(pregao=pe, numero_controle_pncp=comp["numeroControlePNCP"], data_publicacao_pncp=comp["dataPublicacaoPncp"], numero_item=i["numeroItem"],
                      descricao=i["descricao"], unidade=i.get("unidadeMedida"), quantidade=i.get("quantidade"), criterio=i.get("criterioJulgamentoNome"),
                      preco_unitario_homologado=r_.get("valorUnitarioHomologado"), percentual_desconto=r_.get("percentualDesconto"),
                      fornecedor_cnpj=r_.get("niFornecedor"), data_resultado=r_.get("dataResultado"), data_inclusao_resultado_pncp=r_.get("dataInclusao"),
                      arquivo_origem=rel(d)))
H = pd.DataFrame(H)
H["classe_temporal"] = "disponivel"
H["base_disponibilidade"] = ["PNCP: publicação " + str(p)[:10] + ("" if not isinstance(r, str) else
                             (f"; resultado incluído {r[:10]}" if r[:10] <= CUT else f"; resultado incluído no PNCP só em {r[:10]} — disponível como informação interna (contrato próprio; resultado de {d_})"))
                             for p, r, d_ in zip(H.data_publicacao_pncp, H.data_inclusao_resultado_pncp, H.data_resultado)]
H.to_parquet(os.path.join(DI, "organizacional", "historico_proprio_pregoes_2024.parquet"), index=False)
# item de 2025 × itens comparáveis dos pregões próprios de 2024 (quantidade licitada em 2024: sinal de demanda planejada, não consumo)
mp = {r.item: [h for h in H.itertuples() if mesmo_medicamento(h.descricao, h.unidade or "", r.descricao, r.unidade)] for r in I.itertuples()}
I["qtd_licitada_pregoes_proprios_2024"] = [sum(h.quantidade or 0 for h in mp[i]) if mp[i] else None for i in I["item"]]
I["pregoes_proprios_2024_itens"] = ["|".join(f"{h.pregao}#{h.numero_item}" for h in mp[i]) or None for i in I["item"]]
I["data_disponibilidade"] = pd.Timestamp(CUT)
I["base_disponibilidade"] = "documento interno: edital/ETP/TR assinado em 29/01/2025 (publicado no PNCP em 30/01/2025 07:34)"
I["classe_temporal"] = "disponivel"
I.to_parquet(os.path.join(DI, "organizacional", "itens_santa_luzia.parquet"), index=False)
print("itens:", len(I), "| identificação:", I.status_identificacao.value_counts().to_dict())
print("preço praticado:", I.status_preco_praticado.value_counts().to_dict(), "| teto CMED:", I.status_teto_cmed.value_counts().to_dict())
print("itens com qtd licitada em 2024:", int(I.qtd_licitada_pregoes_proprios_2024.notna().sum()), "| estimativa acima do teto CMED (alíquota PB):",
      int(I.alerta_estimativa_acima_teto_cmed.sum()))

E = [("Lei 14.133/2021 (modalidades, dispensa, registro de preços, garantias, contratos, sanções)", "legal", "E-01/E-02"),
     ("Registro na Anvisa, salvo isenção legal", "legal/sanitária", "E-02 ETP III"),
     ("Validade mínima ≥ 75% da vida útil ou > 365 dias na entrega (orientação TCE-PB)", "regulatória", "E-02 ETP III / TR"),
     ("A administração não possui local adequado para armazenamento de medicamentos", "operacional", "E-02 TR 8.4"),
     ("Entrega no endereço da Secretaria Municipal de Saúde", "operacional", "E-02 TR"),
     ("Teto CMED nas vendas ao governo: PMVG para produtos com CAP; PF nos demais (PMVG também em compras judiciais)", "regulatória", "CMED lista 06/01/2025"),
     ("Alíquota de ICMS do teto CMED para Santa Luzia/PB: 0% para isentos e para produtos do Convênio ICMS 87/02 (compra pública municipal); 20% nos demais (Lei 6.379/96, art. 11, I)",
      "tributária", "CONFAZ Conv. ICMS 87/02; Lei PB 6.379/96 consolidada (SEFAZ-PB, 02/10/2023); cabeçalho da lista CMED"),
     ("Necessidade inclui itens fora da RENAME", "escopo", "E-02 objeto")]
pd.DataFrame(E, columns=["restricao", "tipo", "evidencia"]).assign(data_disponibilidade=CUT, classe_temporal="disponivel").to_csv(
    os.path.join(DI, "organizacional", "restricoes.csv"), index=False)

# receitas SUS de 2024 do próprio município (TCE-PB/SAGRES) — informação interna anterior ao corte
zr = os.path.join(ROOT, "data", "raw", "complementares", "tcepb", "170_santa_luzia_receitas-2024.zip")
rc = pd.read_csv(io.BytesIO(zipfile.ZipFile(zr).read("receitas-2024.csv")), sep=None, engine="python", dtype=str)
rc["valor"] = rc.valor.str.replace(".", "", regex=False).str.replace(",", ".").astype(float)
rc = rc[rc.codigo_fonte_recurso.isin(["600", "605"]) & (rc.tipo_atualizacao_receita == "Lançamento de Receita")]
RS = rc.groupby(["ano", "mes_ano", "codigo_receita", "descricao_receita", "codigo_fonte_recurso", "descricao_fonte_recurso"]).valor.sum().reset_index()
RS = RS.assign(fonte="TCE-PB/SAGRES — receitas 2024 do município (download.tce.pb.gov.br)", arquivo_origem=rel(zr),
               base_disponibilidade="interna: receitas de 2024 do próprio órgão", classe_temporal="disponivel")
RS.to_csv(os.path.join(DI, "organizacional", "receitas_sus_2024.csv"), index=False)
af = RS[RS.codigo_receita == "17135041"].valor.sum()
pop = json.load(open(os.path.join(ROOT, "data", "raw", "complementares", "ibge_pop_santa_luzia.json"), encoding="utf8"))[0]["resultados"][0]["series"][0]["serie"]["2024"]
REC = [("valor estimado da necessidade (soma dos 334 itens)", 4952438.00, "R$", "E-02/E-03"),
       ("dotações: 02.030 SMS 10.301.2016.2018; 02.090 FMS 10.301.1006.2061, 10.301.1006.2067, 10.302.1008.2069; elementos 3390.30 e 3390.32; fontes 1.500.1002, 1.500.0000, 1.600.0000", None, "texto", "E-02"),
       ("saldo disponível nas dotações", None, "desconhecido", "ausente: não publicado no edital nem nos dados abertos do TCE-PB consultados"),
       ("repasse federal fundo a fundo — Bloco de Manutenção — Assistência Farmacêutica (receita 1713.50.4.1), recebido em 2024", round(af, 2), "R$", "TCE-PB/SAGRES receitas 2024"),
       ("repasses federais SUS fundo a fundo (fontes 600 e 605), total recebido em 2024", round(RS.valor.sum(), 2), "R$", "TCE-PB/SAGRES receitas 2024"),
       ("população residente estimada 2024 (IBGE, estimativa publicada em 2024)", float(pop), "pessoas", "IBGE/SIDRA tabela 6579 (agregado 9324)"),
       ("estoque inicial de medicamentos na data de decisão", None, "desconhecido", "ausente: BNAFAR sem posição histórica (consultas 12/2024 e 01/2025 vazias em 23/11/2026)")]
pd.DataFrame(REC, columns=["recurso", "valor", "unidade", "evidencia"]).assign(data_disponibilidade=CUT, classe_temporal="disponivel").to_csv(
    os.path.join(DI, "organizacional", "recursos.csv"), index=False)
for f, nome in (("caso_sl_farmaco_mensal.csv", "execucao_farmaco_2024_mensal.csv"), ("caso_sl_farmaco_por_licitacao.csv", "execucao_farmaco_2024_por_licitacao.csv")):
    x = pd.read_csv(os.path.join(ROOT, "reports", f), dtype={"ano": str}); x = x[x.ano == "2024"]
    x.assign(fonte="TCE-PB/SAGRES (despesa do próprio município)", base_disponibilidade="interna: empenhos de 2024 do próprio órgão",
             classe_temporal="disponivel").to_csv(os.path.join(DI, "organizacional", nome), index=False)

# ---------- evaluation_only ----------
S2 = D("processed", "caso_santa_luzia", "reservado_avaliacao")
for f in glob.glob(os.path.join(S2, "*.csv")):
    pd.read_csv(f).to_parquet(os.path.join(EV, "organizacional", os.path.basename(f).replace(".csv", ".parquet")), index=False)
for pasta, nome in (("09090689000167_2025_99", "pregao_25_2025"), ("09090689000167_2026_26", "pregao_09_2026")):
    d = D("raw", "pncp", "etapa2", pasta)
    its = pd.DataFrame([x for f in glob.glob(os.path.join(d, "itens_p*.json")) for x in json.load(open(f, encoding="utf8"))])
    rs = pd.DataFrame([x for f in glob.glob(os.path.join(d, "resultado_item_*.json")) for x in (json.load(open(f, encoding="utf8")) or [])])
    its.merge(rs[["numeroItem", "niFornecedor", "valorUnitarioHomologado", "quantidadeHomologada", "dataResultado"]], on="numeroItem", how="left").to_parquet(
        os.path.join(EV, "organizacional", f"{nome}_itens_resultados.parquet"), index=False)
pd.DataFrame(json.load(open(D("raw", "pncp", "etapa2", "contratos_santa_luzia", "contratos_pregoes_medicamentos.json"), encoding="utf8"))).astype(str).to_parquet(
    os.path.join(EV, "organizacional", "contratos_pregoes_medicamentos.parquet"), index=False)
open(os.path.join(EV, "LEIA-ME.md"), "w", encoding="utf8").write(f"""# evaluation_only — NÃO FORNECER AO AGENTE DECISOR

Dados posteriores ao corte de {CUT} (ou derivados deles), reservados para avaliar a decisão. O módulo
`scripts/consulta_agente.py` recusa caminhos fora de `data/decision_input/`.

- organizacional/: resultado homologado do PE 04/2025, execução por contrato, despesa 2025–2026, pregões 25/2025 e 09/2026,
  contratos; cópia em parquet de `data/processed/caso_santa_luzia/reservado_avaliacao/` (Etapa 2) e de `data/raw/pncp/etapa2/`.
- nacional/: BPS inserido após o corte; resultados/itens/contratações PNCP publicados após o corte; preços Compras.gov.br
  com resultado após o corte (`comprasgov_pos_corte.parquet`, pré-Etapa 4).
- auditoria/: comparação do CATMAT da Etapa 2 (obtido com dados pós-corte) com a identificação pré-corte.
- Fontes brutas pós-corte ainda fora daqui: `data/raw/complementares/cmed_lista_pmvg_20261109.xlsx` (CMED nov/2026),
  `data/raw/ms_api/` (estoque BNAFAR de nov/2026), `data/raw/complementares/tcepb/*2025*|*2026*`.
""")

# ---------- manifesto ----------
def nreg(p):
    try:
        return len(pd.read_parquet(p)) if p.endswith(".parquet") else (len(pd.read_csv(p)) if p.endswith(".csv") else None)
    except Exception:
        return None
META = {"bps_precos_praticados.parquet": ("BPS/MS 2020–2024 (registros inseridos até o corte), classe 6505", "compras 2020-01-01..2024-10-30; inserção até 2024-12-13", "cobertura parcial dos compradores do SUS; sem esfera federal; outliers marcados, não removidos"),
        "cmed_2025_01_apresentacoes.parquet": ("CMED/Anvisa lista PF/PMVG de 06/01/2025", "vigente em 29/01/2025", "preço por embalagem; alíquota PB: 0% (isentos/Conv. 87/02) ou 20%"),
        "cmed_2025_01_precos.parquet": ("CMED/Anvisa lista PF/PMVG de 06/01/2025", "vigente em 29/01/2025", "limites regulatórios, não preços praticados; aliquota_aplicavel_pb marca a coluna válida"),
        "pncp_comparaveis_contratacoes.parquet": ("PNCP API (amostra dirigida; índice MT por CATMAT e por descrição)", "publicação até o corte", "amostra, não censo"),
        "pncp_comparaveis_itens.parquet": ("PNCP API", "itens incluídos até o corte", "amostra; CATMAT ausente no PNCP"),
        "pncp_comparaveis_resultados.parquet": ("PNCP API", "resultados incluídos até o corte", "amostra"),
        "comprasgov_precos_praticados.parquet": ("Compras.gov.br — dados abertos, módulo Pesquisa de Preço", "resultado (dataResultado) até o corte", "registros de órgãos que usam o Compras.gov.br; possível sobreposição com BPS marcada"),
        "item_comprasgov_registros.parquet": ("padronização: item × registro Compras.gov.br", "pré-corte", "compatibilidade por unidade de fornecimento/capacidade"),
        "item_catmat_catalogo_oficial.parquet": ("Catálogo CATMAT oficial (Compras.gov.br) + catálogo BPS pré-corte", "catálogo atual; existência no corte indicada", "código sem registro pré-corte = existência não comprovada"),
        "itens_santa_luzia.parquet": ("Edital/ETP/TR PE 04/2025 (assinado 29/01/2025) + padronização", "necessidade de 12 meses", "sem consumo por item"),
        "historico_proprio_pregoes_2024.parquet": ("PNCP (pregões 01/2024 e 12/2024 do próprio órgão)", "2024", "PE 01/2024 com 4 resultados apenas"),
        "receitas_sus_2024.csv": ("TCE-PB/SAGRES receitas 2024 do município", "2024", "repasses federais SUS; sem saldo de dotação"),
        }
M = []
for p in sorted(glob.glob(os.path.join(DI, "**", "*"), recursive=True)):
    if os.path.isfile(p) and not os.path.basename(p).startswith("MANIFESTO"):
        m = META.get(os.path.basename(p), ("", "", ""))
        M.append(dict(arquivo=rel(p), bytes=os.path.getsize(p), sha256=hashlib.sha256(open(p, "rb").read()).hexdigest(), registros=nreg(p),
                      fonte=m[0], periodo=m[1], limitacoes=m[2]))
M = pd.DataFrame(M)
M.to_csv(os.path.join(DI, "MANIFESTO.csv"), index=False)
json.dump({"pacote": "decision_input", "data_corte": CUT, "gerado_em_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "gerado_por": "scripts/24_bps_historico_temporal.py, 25_padronizacao_vinculos.py, 26_pncp_comparaveis.py, 29_comprasgov_precos.py, 27_montar_pacotes.py",
           "arquivos": M.to_dict("records")}, open(os.path.join(DI, "MANIFESTO.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1, default=str)
print("manifesto:", len(M), "arquivos,", int(M.bytes.sum()), "bytes")
