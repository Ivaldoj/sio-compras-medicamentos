"""Pré-Etapa 4 — Compras.gov.br (dados abertos oficiais): catálogo CATMAT e pesquisa de preços praticados.
Uso:
  python -I -X utf8 29_comprasgov_precos.py <raiz> catalogo     # PDMs da classe 6505 e itens CATMAT dos PDMs dos itens do caso (cache)
  python -I -X utf8 29_comprasgov_precos.py <raiz> precos       # preços por CATMAT (cache), alvo = itens sem preço praticado
  python -I -X utf8 29_comprasgov_precos.py <raiz> consolidar   # tabelas com classe temporal + compatibilidade por registro
Identificação: catálogo oficial atual (a API não expõe a data de criação do item); a existência do código no corte só é dada
como comprovada quando há registro de preço com resultado <= corte ou registro BPS inserido <= corte.
Disponibilidade de cada preço: dataResultado (resultado publicado no Compras.gov.br) e dataCompra <= 29/01/2025."""
import glob, json, os, re, sys, time, urllib.request, urllib.error
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from padroniza import principio, principio_catmat, concentracoes, forma, forma_compativel, conteudo_item, norm, nivel_catmat

ROOT, MODO = sys.argv[1], sys.argv[2]
CUT = pd.Timestamp("2025-01-29T23:59:59")
D = lambda *p: os.path.join(ROOT, "data", *p)
RAW = D("raw", "comprasgov")
API = "https://dadosabertos.compras.gov.br"
for p in ("catalogo", "precos"):
    os.makedirs(os.path.join(RAW, p), exist_ok=True)


def get(url, dest, tries=5):
    """GET com cache em disco; 429/5xx com espera crescente (respeita Retry-After)."""
    if os.path.exists(dest):
        try:
            return json.load(open(dest, encoding="utf-8"))
        except ValueError:
            pass  # arquivo parcial (download interrompido ou concorrente): baixa de novo
    for t in range(1, tries + 1):
        time.sleep(1)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "sio-auditoria-academica/1.0"}), timeout=180) as h:
                b = h.read()
            d = json.loads(b)
            open(dest + ".tmp", "wb").write(b); os.replace(dest + ".tmp", dest)  # gravação atômica
            return d
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {"resultado": [], "totalPaginas": 0}
            if e.code not in (429, 500, 502, 503, 504) or t == tries:
                print("ERRO", e.code, url, flush=True); return None
            ra = e.headers.get("Retry-After", ""); time.sleep(int(ra) if ra.isdigit() else 15 * t)
        except Exception as e:
            if t == tries:
                print("ERRO", e, url, flush=True); return None
            time.sleep(10 * t)


def paginas(url, prefixo):
    out, p = [], 1
    while True:
        d = get(f"{url}&pagina={p}&tamanhoPagina=500", f"{prefixo}_p{p}.json")
        if not d:
            break
        out += d.get("resultado") or []
        if p >= (d.get("totalPaginas") or 0):
            break
        p += 1
    return out


I = pd.read_parquet(D("processed", "etapa3", "itens_atributos.parquet"))
ST = pd.read_parquet(D("decision_input", "organizacional", "itens_santa_luzia.parquet"))[["item", "status_preco_praticado", "catmat_status"]]
I = I.merge(ST, on="item")
ALVO = I   # os 334 itens: 2ª fonte de preço praticado para todos (estável entre execuções); downloads em ordem de valor
CAT_P = os.path.join(D("processed", "pre4"), "catalogo_oficial_candidatos.parquet")
os.makedirs(D("processed", "pre4"), exist_ok=True)


def cat_forma(desc):
    f, m = forma(desc)
    return f, m


if MODO == "catalogo":
    pdm = paginas(f"{API}/modulo-material/3_consultarPdmMaterial?codigoClasse=6505", os.path.join(RAW, "catalogo", "pdm_6505"))
    pdm = pd.DataFrame(pdm)
    print("PDMs classe 6505:", len(pdm))
    # tokens do nome antes do 1º número, inclusive sinônimos entre parênteses ("(Vitamina D3)" -> PDM "VITAMINA D")
    toks = {w for d_ in ALVO.descricao for w in re.findall(r"[a-z]{4,}", re.split(r"\d", norm(d_), maxsplit=1)[0])}
    pdm["tk"] = pdm.nomePdm.map(lambda s: set(re.findall(r"[a-z]{4,}", norm(s))))
    alvo_pdm = pdm[pdm.tk.map(lambda s: bool(s & toks))]
    print("PDMs com token de princípio dos itens-alvo:", len(alvo_pdm))
    rows = []
    for x in alvo_pdm.itertuples():
        for it in paginas(f"{API}/modulo-material/4_consultarItemMaterial?codigoPdm={x.codigoPdm}", os.path.join(RAW, "catalogo", f"itens_pdm_{x.codigoPdm}")):
            rows.append(it)
    C = pd.DataFrame(rows).drop_duplicates("codigoItem")
    C["p"] = [principio_catmat(a, b) for a, b in zip(C.nomePdm, C.descricaoItem)]
    C["c"] = C.descricaoItem.map(concentracoes); C["f"] = C.descricaoItem.map(cat_forma)
    idx = C.groupby("p").groups
    L = []
    for r in ALVO.itertuples():
        for k in idx.get(principio(r.descricao), []):
            x = C.loc[k]
            nivel = nivel_catmat(r.descricao, r.unidade, x.c, x.f)
            fi, mi = forma(r.descricao + " " + r.unidade)
            # CATMAT genérico ("injetável") cuja apresentação (caneta, frasco, refil) só aparece na unidade de fornecimento
            if not nivel and x.c == concentracoes(r.descricao) and x.f[0] == "injetavel" and fi and "injet" in fi and x.f[1] < mi and mi - x.f[1] <= {"sist_aplic"}:
                nivel = "generico_apresentacao_na_unidade"
            if nivel:
                L.append(dict(item=r.item, catmat=str(x.codigoItem), descricao_catmat=x.descricaoItem, codigo_pdm=str(x.codigoPdm), nome_pdm=x.nomePdm,
                              status_catalogo=bool(x.statusItem), data_atualizacao_catalogo=x.dataHoraAtualizacao, nivel=nivel,
                              fonte="Catálogo CATMAT oficial (dadosabertos.compras.gov.br, módulo material; consulta em 23/11/2026)"))
    L = pd.DataFrame(L)
    L.to_parquet(CAT_P, index=False)
    print("itens-alvo com CATMAT no catálogo oficial:", L["item"].nunique(), "de", len(ALVO), "| pares:", len(L), "| níveis:", L.nivel.value_counts().to_dict())

elif MODO == "precos":
    L = pd.read_parquet(CAT_P)
    bpsc = pd.read_parquet(D("decision_input", "padronizacao", "item_catmat_candidatos.parquet"))
    bpsc = bpsc[bpsc["item"].isin(ALVO["item"])]
    cods = list(dict.fromkeys(list(L.catmat) + list(bpsc.catmat)))
    peso = I.set_index("item").valor_total_estimado_orgao
    ordem = pd.concat([L[["item", "catmat"]], bpsc[["item", "catmat"]]]).assign(v=lambda d: d["item"].map(peso)).groupby("catmat").v.max()
    cods = sorted(cods, key=lambda c: -ordem.get(c, 0))   # maior valor primeiro
    if len(sys.argv) > 3 and sys.argv[3] == "reverso":
        cods = cods[::-1]   # 2º processo em paralelo, do fim para o início (cache compartilhado)
    elif len(sys.argv) > 3 and sys.argv[3] == "meio":
        cods = cods[len(cods) // 2:]   # 3º processo em paralelo, do meio para o fim
    for n, c in enumerate(cods, 1):
        r = paginas(f"{API}/modulo-pesquisa-preco/1_consultarMaterial?tipo=codigoItemCatalogo&codigo={c}", os.path.join(RAW, "precos", f"catmat_{c}"))
        print(f"[{n}/{len(cods)}] CATMAT {c}: {len(r)} registros", flush=True)

elif MODO == "consolidar":
    L = pd.read_parquet(CAT_P)
    bpsc = pd.read_parquet(D("decision_input", "padronizacao", "item_catmat_candidatos.parquet"))
    bpsc = bpsc[bpsc["item"].isin(ALVO["item"])].assign(nivel=lambda d: d.nivel, fonte="BPS inserido até 29/01/2025 (catálogo observado)")
    P = []
    for f in glob.glob(os.path.join(RAW, "precos", "catmat_*_p*.json")):
        for x in json.load(open(f, encoding="utf-8")).get("resultado") or []:
            x["arquivo_origem"] = os.path.relpath(f, ROOT); P.append(x)
    P = pd.DataFrame(P).drop_duplicates("idCompraItem")
    P["catmat"] = P.codigoItemCatalogo.astype(str)
    dres, dcom = pd.to_datetime(P.dataResultado, errors="coerce"), pd.to_datetime(P.dataCompra, errors="coerce")
    P["classe_temporal"] = ["indeterminado" if pd.isna(r) or pd.isna(c) or r < c else ("disponivel" if r <= CUT else "posterior") for r, c in zip(dres, dcom)]
    P["data_disponibilidade"] = dres; P["base_disponibilidade"] = "Compras.gov.br dataResultado (com dataCompra <= dataResultado)"
    T = pd.DataFrame(dict(
        fonte="Compras.gov.br — Pesquisa de Preço (dadosabertos.compras.gov.br, módulo pesquisa-preco)", id_origem=P.idCompraItem, arquivo_origem=P.arquivo_origem,
        catmat=P.catmat, descricao_catmat=P.descricaoItem, descricao_detalhada=P.descricaoDetalhadaItem, unidade_fornecimento=P.nomeUnidadeFornecimento,
        capacidade_valor=P.capacidadeUnidadeFornecimento, capacidade_unidade=P.siglaUnidadeMedida, marca=P.marca,
        comprador_uasg=P.codigoUasg, comprador_nome=P.nomeUasg, comprador_orgao=P.nomeOrgao, uf=P.estado, municipio=P.municipio, esfera=P.esfera, poder=P.poder,
        fornecedor_ni=P.niFornecedor, forma_compra=P.forma, modalidade=P.modalidade, data_compra=dcom, data_resultado=dres,
        data_atualizacao_item=pd.to_datetime(P.dataHoraAtualizacaoItem, errors="coerce"), quantidade=P.quantidade, preco_unitario_praticado=P.precoUnitario,
        categoria_valor="preco_unitario_praticado (homologado no Compras.gov.br, por unidade de fornecimento)",
        data_disponibilidade=P.data_disponibilidade, base_disponibilidade=P.base_disponibilidade, classe_temporal=P.classe_temporal))
    # possível duplicata com o BPS (mesmo fornecedor, CATMAT, data e preço): marcada, não removida
    bps = pd.read_parquet(D("decision_input", "nacional", "bps_precos_praticados.parquet"), columns=["catmat", "fornecedor_cnpj", "data_compra", "preco_unitario_praticado"])
    k = lambda c, f, d, v: list(zip(c.astype(str), f.astype(str), pd.to_datetime(d).dt.date, v.round(2)))
    kb = set(k(bps.catmat, bps.fornecedor_cnpj, bps.data_compra, bps.preco_unitario_praticado))
    T["flag_possivel_duplicata_bps"] = [x in kb for x in k(T.catmat, T.fornecedor_ni, T.data_compra, T.preco_unitario_praticado)]
    # CATMAT por item: catálogo oficial + catálogo BPS pré-corte; existência no corte comprovada por registro pré-corte
    pre = set(T[T.classe_temporal == "disponivel"].catmat) | set(bps.catmat.astype(str))
    L["existencia_no_corte"] = L.catmat.map(lambda c: "comprovada (registro de preço/BPS anterior ao corte)" if c in pre else "não comprovada")
    K = pd.concat([L, bpsc[["item", "catmat", "descricao_catmat", "nivel", "fonte"]].assign(existencia_no_corte="comprovada (BPS anterior ao corte)")]).drop_duplicates(["item", "catmat"])
    # compatibilidade de cada registro com o item (unidade de fornecimento e conteúdo)
    SOL = {"COMPRIMIDO", "CÁPSULA", "CAPSULA", "DRÁGEA", "DRAGEA", "COMPRIMIDO REVESTIDO"}
    REFIL = {"TUBETE", "CARTUCHO", "REFIL", "CARPULE", "FRASCO", "FRASCO-AMPOLA"}
    It = I.set_index("item")

    def comp(r):
        d = It.loc[r["item"]]
        fi, mi = forma(d.descricao + " " + d.unidade)
        u = str(r.unidade_fornecimento or "").upper()
        if r.nivel == "parcial_forma_indeterminada":
            # mesma regra do catálogo BPS: forma sólida confirmada pela unidade de fornecimento do registro
            uf_ = "capsula" if "PSULA" in u else ("comprimido" if u in SOL else None)
            amb = "caps" in norm(d.descricao) and "comp" in norm(d.descricao)
            if fi in ("comprimido", "capsula") and uf_ and forma_compativel(fi, uf_, amb):
                return "compativel"
            return "a_conferir: forma do CATMAT não confirmada"
        if fi in ("comprimido", "capsula", "solido"):
            return "compativel" if u in SOL else "incompativel_unidade"
        vi = conteudo_item(d.descricao)
        cap = (float(r.capacidade_valor), str(r.capacidade_unidade or "").lower()) if r.capacidade_valor and float(r.capacidade_valor) > 0 else None
        if "sist_aplic" in mi:
            if not u:
                return "a_conferir: unidade de fornecimento não informada"
            if u in REFIL:
                return "incompativel: refil/frasco sem sistema de aplicação"
            if cap and vi and cap != vi:
                return "incompativel_capacidade"
            txt = norm(f"{r.descricao_detalhada} {r.marca}")
            if re.search(r"caneta|sistema de aplica|flexpen|kwikpen|descartavel", txt) and cap == vi:
                return "compativel"
            return "a_conferir: sistema de aplicação não explícito no registro"
        if not vi:
            return "a_conferir: conteúdo do item não extraído"
        if not cap:
            return "a_conferir: capacidade não informada"
        return "compativel" if cap == vi else "incompativel_capacidade"
    R = K[["item", "catmat", "nivel", "existencia_no_corte"]].merge(T, on="catmat")
    R["compatibilidade"] = R.apply(comp, axis=1)
    os.makedirs(D("decision_input", "nacional"), exist_ok=True); os.makedirs(D("evaluation_only", "nacional"), exist_ok=True)
    # data de atualização do registro na fonte é metadado atual (muitas vezes > corte): fica na auditoria, fora do pacote
    os.makedirs(D("processed", "pre4"), exist_ok=True)
    T[["id_origem", "classe_temporal", "data_resultado", "data_atualizacao_item"]].to_parquet(D("processed", "pre4", "comprasgov_datas_atualizacao.parquet"), index=False)
    print("registros disponíveis atualizados na fonte após o corte:", int(((T.classe_temporal == "disponivel") & (T.data_atualizacao_item > CUT)).sum()))
    T = T.drop(columns=["data_atualizacao_item"])
    for cls, alvo in (("disponivel", D("decision_input", "nacional", "comprasgov_precos_praticados.parquet")),
                      ("posterior", D("evaluation_only", "nacional", "comprasgov_pos_corte.parquet")),
                      ("indeterminado", D("quarentena_temporal", "comprasgov_disponibilidade_indeterminada.parquet"))):
        T[T.classe_temporal == cls].to_parquet(alvo, index=False)
    Rd = R[R.classe_temporal == "disponivel"][["item", "catmat", "nivel", "id_origem", "compatibilidade"]]
    Rd.to_parquet(D("decision_input", "padronizacao", "item_comprasgov_registros.parquet"), index=False)
    # status e data de atualização do catálogo são do estado ATUAL (2026): ficam em data/processed/pre4, fora do pacote
    K.drop(columns=["status_catalogo", "data_atualizacao_catalogo"], errors="ignore").to_parquet(
        D("decision_input", "padronizacao", "item_catmat_catalogo_oficial.parquet"), index=False)
    print("registros:", len(T), T.classe_temporal.value_counts().to_dict(), "| possíveis duplicatas BPS (disponíveis):", int(T[T.classe_temporal == "disponivel"].flag_possivel_duplicata_bps.sum()))
    print("pares item×registro disponíveis por compatibilidade:", Rd.compatibilidade.value_counts().to_dict())
    ok = Rd[Rd.compatibilidade == "compativel"]
    print("itens-alvo com ≥1 preço compatível (Compras.gov.br, pré-corte):", ok["item"].nunique(), "| itens com só 'a conferir':",
          Rd[Rd.compatibilidade.str.startswith("a_conferir") & ~Rd["item"].isin(ok["item"])]["item"].nunique())
    for it_ in (196, 199):
        print(f"item {it_}:", Rd[Rd["item"] == it_].compatibilidade.value_counts().to_dict())
