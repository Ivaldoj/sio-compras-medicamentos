"""Etapa 3 — contratações comparáveis no PNCP anteriores ao corte (amostra dirigida, não censo).
Uso:
  python -I -X utf8 26_pncp_comparaveis.py <raiz> selecionar [max=120]   # usa o MT só como índice; sem chamadas à API
  python -I -X utf8 26_pncp_comparaveis.py <raiz> selecionar_texto [max=40]  # pré-etapa 4: MT por DESCRIÇÃO, alvo = itens sem preço praticado
  python -I -X utf8 26_pncp_comparaveis.py <raiz> baixar [selecao_texto]  # PNCP: compra, itens e resultados dos itens casados (cache)
  python -I -X utf8 26_pncp_comparaveis.py <raiz> consolidar              # tabelas com classe temporal (todas as seleções)
Seleção: contratações com início de propostas <= corte, objeto com "medicament" e >= 1 item (dos até 10 que o MT expõe)
com CATMAT entre os candidatos pré-corte dos itens de Santa Luzia; escolha gulosa pela cobertura de itens do caso
ainda não cobertos, preferindo início até 30/11/2024. Disponibilidade é verificada nas datas do próprio PNCP:
compra (dataPublicacaoPncp), item (dataInclusao) e resultado (dataInclusao)."""
import glob, json, os, re, sys, time, urllib.request, urllib.error, zipfile
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from padroniza import principio, concentracoes, forma, forma_compativel, conteudo_item, norm, mesmo_medicamento

ROOT, MODO = sys.argv[1], sys.argv[2]
CUT = pd.Timestamp("2025-01-29T23:59:59")
D = lambda *p: os.path.join(ROOT, "data", *p)
RAW = D("raw", "pncp", "etapa3"); os.makedirs(RAW, exist_ok=True)
SEL = os.path.join(RAW, "selecao.csv")
SEL_TXT = os.path.join(RAW, "selecao_texto.csv")
API = "https://pncp.gov.br/api"


def get(url, dest, tries=5):
    if os.path.exists(dest):
        b = open(dest, "rb").read()
        try:
            return json.loads(b) if b else None
        except ValueError:
            pass  # arquivo parcial (download interrompido ou concorrente): baixa de novo
    for t in range(1, tries + 1):
        time.sleep(3)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "sio-auditoria-academica/1.0"}), timeout=120) as h:
                b = h.read()
            open(dest + ".tmp", "wb").write(b); os.replace(dest + ".tmp", dest)  # gravação atômica
            return json.loads(b) if b else None
        except urllib.error.HTTPError as e:
            if e.code in (404, 422):
                open(dest, "wb").write(b""); return None
            if e.code not in (429, 500, 502, 503, 504) or t == tries:
                print("ERRO", e.code, url, flush=True); return None
            ra = e.headers.get("Retry-After", ""); time.sleep(int(ra) if ra.isdigit() else 20 * t)
        except Exception as e:
            if t == tries:
                print("ERRO", e, url, flush=True); return None
            time.sleep(10 * t)


def ler(p):
    """JSON do cache; arquivo vazio (204/404) ou cortado por interrupção do download -> None (contado em 'ilegíveis')."""
    try:
        b = open(p, "rb").read()
        return json.loads(b) if b else None
    except (ValueError, OSError):
        ILEG.append(p); return None


ILEG = []


if MODO == "selecionar":
    mx = int(sys.argv[3]) if len(sys.argv) > 3 else 120
    cand = pd.read_parquet(D("decision_input", "padronizacao", "item_catmat_candidatos.parquet"))
    cand = cand[cand.nivel == "atributos_compativeis"]
    cat2item = cand.groupby("catmat")["item"].agg(set).to_dict()
    R, T = [], []
    for zp in sorted(glob.glob(D("raw", "transparencia", "*", "*-csv.zip"))):
        with zipfile.ZipFile(zp) as z:
            for m in z.namelist():
                if m.endswith("-releases.csv"):
                    R.append(pd.read_csv(z.open(m), dtype=str, usecols=lambda c: c in ("ocid", "id", "buyer/id", "tender/tenderPeriod/startDate", "tender/description")).assign(uf=os.path.basename(zp)[:2].upper()))
                elif m.endswith("-ten_items.csv"):
                    T.append(pd.read_csv(z.open(m), dtype=str, usecols=lambda c: c in ("ocid", "tender/items/0/classification/id")))
    r = pd.concat(R).drop_duplicates("ocid")
    r["inicio"] = pd.to_datetime(r["tender/tenderPeriod/startDate"], errors="coerce", utc=True).dt.tz_localize(None)
    r = r[(r.inicio <= CUT) & r["tender/description"].fillna("").str.contains("medicament", case=False)]
    n_pre = len(r)
    t = pd.concat(T).drop_duplicates()
    t = t[t.ocid.isin(r.ocid) & t["tender/items/0/classification/id"].isin(cat2item)]
    cov = t.groupby("ocid")["tender/items/0/classification/id"].agg(lambda s: set().union(*(cat2item[c] for c in s)))
    r = r[r.ocid.isin(cov.index)].set_index("ocid"); r["itens_caso"] = cov
    print("pré-corte com medicamento:", n_pre, "| com CATMAT do caso nos itens indexados pelo MT:", len(r))
    escolhidos, coberto = [], set()
    pref = r.inicio <= pd.Timestamp("2024-11-30")
    while len(escolhidos) < mx:
        ganho = r.itens_caso.map(lambda s: len(s - coberto)) + pref.astype(int) * 0.5
        ganho = ganho.drop(escolhidos, errors="ignore")
        if ganho.empty or ganho.max() < 1:
            break
        o = ganho.idxmax(); escolhidos.append(o); coberto |= r.loc[o, "itens_caso"]
    s = r.loc[escolhidos].reset_index()
    s["itens_caso"] = s.itens_caso.map(lambda x: "|".join(map(str, sorted(x))))
    s[["ocid", "id", "buyer/id", "uf", "inicio", "itens_caso", "tender/description"]].to_csv(SEL, index=False)
    print("selecionadas:", len(s), "| itens do caso cobertos (via CATMAT indexado):", len(coberto), "| UFs:", s.uf.nunique(),
          "| início:", s.inicio.min().date(), "..", s.inicio.max().date())

elif MODO == "selecionar_texto":
    # Seleção 2 (pré-Etapa 4): o índice CATMAT não alcança itens sem CATMAT pré-corte (ex.: insulinas em caneta). Aqui o MT
    # (só índice) é varrido pela DESCRIÇÃO dos itens; alvo = itens do caso sem preço praticado compatível, pesados pelo valor.
    mx = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    I = pd.read_parquet(D("processed", "etapa3", "itens_atributos.parquet"))
    st = pd.read_parquet(D("decision_input", "organizacional", "itens_santa_luzia.parquet"))[["item", "status_preco_praticado"]]
    A = I.merge(st, on="item"); A = A[A.status_preco_praticado != "disponível"]
    peso = A.set_index("item").valor_total_estimado_orgao
    R, T = [], []
    for zp in sorted(glob.glob(D("raw", "transparencia", "*", "*-csv.zip"))):
        with zipfile.ZipFile(zp) as z:
            for m in z.namelist():
                if m.endswith("-releases.csv"):
                    R.append(pd.read_csv(z.open(m), dtype=str, usecols=lambda c: c in ("ocid", "id", "tender/tenderPeriod/startDate")).assign(uf=os.path.basename(zp)[:2].upper()))
                elif m.endswith("-ten_items.csv"):
                    T.append(pd.read_csv(z.open(m), dtype=str, usecols=lambda c: c in ("ocid", "tender/items/0/description", "tender/items/0/unit/name")))
    r = pd.concat(R).drop_duplicates("ocid")
    r["inicio"] = pd.to_datetime(r["tender/tenderPeriod/startDate"], errors="coerce", utc=True).dt.tz_localize(None)
    r = r[r.inicio <= CUT]
    t = pd.concat(T); t = t[t.ocid.isin(r.ocid)].drop_duplicates()
    t["p"] = t["tender/items/0/description"].fillna("").map(principio)
    alvo_p = {}
    for a in A.itertuples():
        alvo_p.setdefault(principio(a.descricao), []).append(a)
    cov = {}
    for x in t[t.p.isin(alvo_p)].itertuples():
        for a in alvo_p[x.p]:
            if mesmo_medicamento(x._2, x._3 or "", a.descricao, a.unidade):
                cov.setdefault(x.ocid, set()).add(a.item)
    print("MT pré-corte:", len(r), "contratações |", len(t), "itens indexados | contratações com item-alvo por descrição:", len(cov))
    ja = set(pd.read_csv(SEL, dtype=str).ocid)
    escolhidos, coberto = [], set()
    while len(escolhidos) < mx:
        g = {o: sum(peso[i] for i in s_ - coberto) for o, s_ in cov.items() if o not in ja and o not in escolhidos}
        if not g or max(g.values()) <= 0:
            break
        o = max(g, key=g.get); escolhidos.append(o); coberto |= cov[o]
    s = r.set_index("ocid").loc[escolhidos].reset_index()
    s["itens_caso"] = [ "|".join(map(str, sorted(cov[o]))) for o in s.ocid]
    s["criterio"] = "descrição do item (MT) comparável a item sem preço praticado"
    s[["ocid", "id", "uf", "inicio", "itens_caso", "criterio"]].to_csv(SEL_TXT, index=False)
    print("selecionadas:", len(s), "| itens-alvo cobertos:", len(coberto), "de", len(A), "| % do valor dos itens-alvo:",
          round(100 * peso[list(coberto)].sum() / peso.sum(), 1), "| alvo cobertos:", sorted(coberto))

elif MODO == "baixar":
    I = pd.read_parquet(D("processed", "etapa3", "itens_atributos.parquet"))
    s = pd.read_csv(SEL_TXT if len(sys.argv) > 3 and sys.argv[3] == "selecao_texto" else SEL, dtype=str)
    if "reverso" in sys.argv[3:]:
        s = s.iloc[::-1]   # 2º processo em paralelo, do fim para o início (cache compartilhado)
    if len(sys.argv) > 3 and sys.argv[3] == "selecao_texto":
        # resultados só dos itens-alvo (sem preço): reduz as chamadas item a item, que dominam o tempo
        I = I[I["item"].isin({int(i) for v in s.itens_caso for i in v.split("|")})]
    for k, x in s.iterrows():
        cnpj, seq, ano = re.match(r"(\d{14})-\d-(\d+)/(\d{4})", x["id"]).groups(); seq = int(seq)
        d = os.path.join(RAW, f"{cnpj}_{ano}_{seq}"); os.makedirs(d, exist_ok=True)
        get(f"{API}/consulta/v1/orgaos/{cnpj}/compras/{ano}/{seq}", os.path.join(d, "compra.json"))
        its, p = [], 1
        while True:
            pg = get(f"{API}/pncp/v1/orgaos/{cnpj}/compras/{ano}/{seq}/itens?pagina={p}&tamanhoPagina=500", os.path.join(d, f"itens_p{p}.json")) or []
            its += pg
            if len(pg) < 500:
                break
            p += 1
        n = 0
        for i in its:
            if not i.get("temResultado"):
                continue
            if any(mesmo_medicamento(i["descricao"], i.get("unidadeMedida", ""), c.descricao, c.unidade) for c in I.itertuples()):
                get(f"{API}/pncp/v1/orgaos/{cnpj}/compras/{ano}/{seq}/itens/{i['numeroItem']}/resultados", os.path.join(d, f"resultado_item_{i['numeroItem']}.json")); n += 1
        print(f"[{k + 1}/{len(s)}] {x['id']} itens={len(its)} resultados_consultados={n}", flush=True)

elif MODO == "consolidar":
    I = pd.read_parquet(D("processed", "etapa3", "itens_atributos.parquet"))
    s = pd.read_csv(SEL, dtype=str).assign(criterio="CATMAT indexado (MT)")
    if os.path.exists(SEL_TXT):
        s = pd.concat([s, pd.read_csv(SEL_TXT, dtype=str)]).drop_duplicates("id")
    C, IT, RS, falta = [], [], [], []
    for x in s.itertuples():
        cnpj, seq, ano = re.match(r"(\d{14})-\d-(\d+)/(\d{4})", x.id).groups(); seq = int(seq)
        d = os.path.join(RAW, f"{cnpj}_{ano}_{seq}")
        if not os.path.exists(os.path.join(d, "compra.json")) or not glob.glob(os.path.join(d, "itens_p*.json")):
            falta.append(x.id); continue  # download não concluído: fica fora (registrado)
        c = ler(os.path.join(d, "compra.json")) or {}
        uo = c.get("unidadeOrgao", {})
        C.append(dict(numero_controle_pncp=x.id, ocid_mt=x.ocid, criterio_selecao=x.criterio, comprador_cnpj=cnpj, comprador_nome=c.get("orgaoEntidade", {}).get("razaoSocial"),
                      unidade=uo.get("nomeUnidade"), municipio=uo.get("municipioNome"), uf=uo.get("ufSigla"), codigo_ibge=uo.get("codigoIbge"),
                      esfera=c.get("orgaoEntidade", {}).get("esferaId"), modalidade=c.get("modalidadeNome"), srp=c.get("srp"),
                      objeto=(c.get("objetoCompra") or "")[:300], data_publicacao_pncp=c.get("dataPublicacaoPncp"),
                      data_abertura=c.get("dataAberturaProposta"), valor_total_estimado=c.get("valorTotalEstimado"),
                      orcamento_sigiloso=c.get("orcamentoSigilosoDescricao"), arquivo_origem=os.path.relpath(os.path.join(d, "compra.json"), ROOT)))
        for f in sorted(glob.glob(os.path.join(d, "itens_p*.json"))):
            for i in ler(f) or []:
                casa = [c_.item for c_ in I.itertuples() if mesmo_medicamento(i["descricao"], i.get("unidadeMedida", ""), c_.descricao, c_.unidade)]
                IT.append(dict(numero_controle_pncp=x.id, numero_item=i["numeroItem"], descricao=i["descricao"], unidade=i.get("unidadeMedida"),
                               quantidade=i.get("quantidade"), preco_unitario_estimado=i.get("valorUnitarioEstimado"), valor_total_estimado=i.get("valorTotal"),
                               orcamento_sigiloso=i.get("orcamentoSigiloso"), situacao=i.get("situacaoCompraItemNome"), data_inclusao=i.get("dataInclusao"),
                               itens_caso_comparaveis="|".join(map(str, casa)) or None, arquivo_origem=os.path.relpath(f, ROOT)))
        for f in glob.glob(os.path.join(d, "resultado_item_*.json")):
            for r_ in ler(f) or []:
                RS.append(dict(numero_controle_pncp=x.id, numero_item=r_["numeroItem"], fornecedor_cnpj=r_.get("niFornecedor"),
                               quantidade_homologada=r_.get("quantidadeHomologada"), preco_unitario_homologado=r_.get("valorUnitarioHomologado"),
                               valor_total_homologado=r_.get("valorTotalHomologado"), data_resultado=r_.get("dataResultado"),
                               data_inclusao=r_.get("dataInclusao"), data_cancelamento=r_.get("dataCancelamento"), arquivo_origem=os.path.relpath(f, ROOT)))
    C, IT, RS = pd.DataFrame(C), pd.DataFrame(IT), pd.DataFrame(RS)
    for df, col in ((C, "data_publicacao_pncp"), (IT, "data_inclusao"), (RS, "data_inclusao")):
        dt = pd.to_datetime(df[col], errors="coerce")
        df["data_disponibilidade"] = dt
        df["classe_temporal"] = ["indeterminado" if pd.isna(v) else ("disponivel" if v <= CUT else "posterior") for v in dt]
        df["base_disponibilidade"] = f"PNCP {col}"
    # um item só é disponível se a contratação também for; um resultado, se o item também for
    IT = IT.merge(C[["numero_controle_pncp", "classe_temporal"]].rename(columns={"classe_temporal": "ct_compra"}), on="numero_controle_pncp")
    IT.loc[IT.ct_compra != "disponivel", "classe_temporal"] = IT.ct_compra.where(IT.ct_compra != "disponivel", IT.classe_temporal)
    IT = IT.drop(columns="ct_compra")
    IT["categoria_valor"] = "preco_unitario_estimado_por_outro_orgao (por unidade do item)"
    # cancelamento só conta se ocorreu até o corte; data posterior não entra no pacote (seria informação futura)
    dc = pd.to_datetime(RS.get("data_cancelamento"), errors="coerce") if len(RS) else pd.Series(dtype="datetime64[ns]")
    RS["cancelado"] = dc <= CUT
    RS["data_cancelamento"] = dc.where(dc <= CUT)
    # 'situacao' do item é a situação ATUAL no PNCP (ex.: "Homologado" depois do corte): fica só na auditoria, fora do pacote
    os.makedirs(D("processed", "pre4"), exist_ok=True)
    IT.to_parquet(D("processed", "pre4", "pncp_itens_situacao_atual.parquet"), index=False)
    IT = IT.drop(columns=["situacao"])
    RS["categoria_valor"] = "preco_unitario_homologado (por unidade do item)"
    os.makedirs(D("decision_input", "nacional"), exist_ok=True); os.makedirs(D("evaluation_only", "nacional"), exist_ok=True); os.makedirs(D("quarentena_temporal"), exist_ok=True)
    for nome, df in (("pncp_comparaveis_contratacoes", C), ("pncp_comparaveis_itens", IT), ("pncp_comparaveis_resultados", RS)):
        for cls, alvo in (("disponivel", D("decision_input", "nacional")), ("posterior", D("evaluation_only", "nacional")), ("indeterminado", D("quarentena_temporal"))):
            df[df.classe_temporal == cls].to_parquet(os.path.join(alvo, f"{nome}.parquet"), index=False)
        print(nome, len(df), df.classe_temporal.value_counts().to_dict())
    print("arquivos ilegíveis ignorados:", len(ILEG), ILEG[:3])
    print("contratações selecionadas:", len(s), "| consolidadas:", len(C), "| sem download concluído:", len(falta))
    pd.Series(falta, name="numero_controle_pncp").to_csv(os.path.join(RAW, "nao_baixadas.csv"), index=False)
    print("itens comparáveis a itens do caso (disponíveis):", int(IT[(IT.classe_temporal == "disponivel")].itens_caso_comparaveis.notna().sum()),
          "| itens do caso com ≥1 comparável PNCP disponível:", len(set("|".join(IT[(IT.classe_temporal == "disponivel")].itens_caso_comparaveis.dropna()).split("|")) - {""}))
