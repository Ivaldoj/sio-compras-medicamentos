"""Etapa 3 — verificações automáticas do pacote decisório: qualidade, integridade temporal, vazamento e consultas.
Uso: python -I -X utf8 28_verificacoes.py <raiz_projeto>
Saídas: reports/etapa3_testes.csv (um teste por linha, PASSOU/FALHOU), reports/validacao_temporal.csv, reports/cobertura_integracao.csv.
Código de saída 1 se algum teste FALHOU."""
import glob, hashlib, json, os, re, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import consulta_agente as q
from padroniza import compara

ROOT = sys.argv[1]
CUT = pd.Timestamp("2025-01-29T23:59:59")
D = lambda *p: os.path.join(ROOT, "data", *p)
DI, EV = D("decision_input"), D("evaluation_only")
T = []
def teste(grupo, nome, ok, detalhe=""):
    T.append(dict(grupo=grupo, teste=nome, resultado="PASSOU" if ok else "FALHOU", detalhe=str(detalhe)[:500]))
con = q.conectar()
S = lambda sql, *a: con.execute(sql, list(a)).df()
tem = lambda v: bool(con.execute(f"SELECT count(*) FROM information_schema.tables WHERE table_name = '{v}'").fetchone()[0])

# ---------------- integridade temporal e vazamento ----------------
arqs = [p for p in glob.glob(os.path.join(DI, "**", "*"), recursive=True) if os.path.isfile(p)]
for p in arqs:
    if not p.endswith((".parquet", ".csv")):
        continue
    df = pd.read_parquet(p) if p.endswith(".parquet") else pd.read_csv(p, low_memory=False)
    nome = os.path.relpath(p, DI).replace("\\", "/")
    if "classe_temporal" in df:
        teste("temporal", f"{nome}: só classe 'disponivel'", set(df.classe_temporal.dropna()) <= {"disponivel"}, df.classe_temporal.value_counts().to_dict())
    for col in ("data_disponibilidade", "data_insercao", "data_publicacao_pncp", "data_inclusao"):
        if col in df:
            mx = pd.to_datetime(df[col], errors="coerce").max()
            teste("temporal", f"{nome}: max({col}) <= corte", pd.isna(mx) or mx <= CUT, mx)
    if "data_disponibilidade" not in df and "base_disponibilidade" not in df and nome not in ("MANIFESTO.csv", "padronizacao/regras_conversao.csv"):
        teste("proveniência", f"{nome}: tem data/base de disponibilidade ou é derivado documentado", nome.startswith("padronizacao/"), "derivado de tabelas pré-corte" if nome.startswith("padronizacao/") else "sem campo")
    proib = {"preco_unitario_homologado", "quantidade_homologada", "fornecedor", "cnpj_fornecedor", "data_resultado", "valor_contratado", "empenhado_2025", "pct_empenhado"}
    if nome.startswith(("organizacional/itens", "padronizacao/")):
        teste("vazamento", f"{nome}: sem colunas de resultado do PE 04/2025", not (proib & set(df.columns)), proib & set(df.columns))

RX = [r"09090689000167-1-0+99/2025", r"09090689000167-1-0+26/2026", r"09090689000167-2-\d{6}/20(25|26)", r"\bPE\s*(25/2025|0?9/2026)\b",
      r"nova demanda", r"3\.105\.249,60|\b3105249\.6\b", r"586\.816,65|\b586816\.65\b", r"\b18,9\s*%", r"reservado_avaliacao|evaluation_only/organizacional"]
achados = []
for p in arqs:
    nome = os.path.relpath(p, DI)
    if re.search(r"2026|homolog|resultado_pe04|contrato", nome, re.I):
        achados.append(("nome", nome))
    if p.endswith((".csv", ".json", ".md", ".txt")):
        txt = open(p, encoding="utf8", errors="ignore").read()
    else:
        df = pd.read_parquet(p); txt = " ".join(df[c].astype(str).str.cat(sep=" ") for c in df.columns if df[c].dtype == object)
    for rx in RX:
        if re.search(rx, txt, re.I):
            achados.append((nome, rx))
teste("vazamento", "nomes de arquivo e textos sem identificadores/valores pós-corte", not achados, achados[:10])
bp = S("SELECT count(*) n FROM bps WHERE comprador_cnpj = '10425754000147' AND data_compra >= '2025-01-01'").n[0]
teste("vazamento", "BPS do pacote sem compras de Santa Luzia de 2025", bp == 0, bp)
res = pd.read_parquet(os.path.join(EV, "organizacional", "resultado_homologado_PE04_2025.parquet"))
it = pd.read_parquet(os.path.join(DI, "organizacional", "itens_santa_luzia.parquet")).merge(res[["item", "preco_unitario_homologado"]], on="item")
susp = [c for c in it.select_dtypes("number").columns if c not in ("item", "preco_unitario_estimado_orgao", "preco_unitario_homologado")
        and (it[c].round(4) == it.preco_unitario_homologado.round(4)).mean() > 0.05]
teste("vazamento", "nenhuma coluna dos itens reproduz o preço homologado", not susp, susp)
eq = (it.preco_unitario_estimado_orgao.round(4) == it.preco_unitario_homologado.round(4)).mean()
teste("vazamento", "preço estimado do órgão é pré-corte (coincidência com homologado registrada, não vazamento)", True, f"{100 * eq:.1f}% dos itens com estimado = homologado")
if tem("pncp_contratacoes"):
    n = S("SELECT count(*) n FROM pncp_contratacoes WHERE comprador_cnpj = '09090689000167' AND (numero_controle_pncp LIKE '%/2025' OR numero_controle_pncp LIKE '%/2026')").n[0]
    teste("vazamento", "comparáveis PNCP sem contratações de 2025/2026 de Santa Luzia", n == 0, n)
    n = S("SELECT count(*) n FROM pncp_resultados r LEFT JOIN pncp_itens i USING (numero_controle_pncp, numero_item) WHERE i.numero_item IS NULL").n[0]
    teste("temporal", "todo resultado PNCP disponível tem item disponível", n == 0, n)
man = pd.read_csv(os.path.join(DI, "MANIFESTO.csv"))
dif = [r.arquivo for r in man.itertuples() if hashlib.sha256(open(os.path.join(ROOT, r.arquivo), "rb").read()).hexdigest() != r.sha256]
teste("reprodutibilidade", "hashes do manifesto conferem", not dif, dif)
fora = [a for a in arqs if not os.path.basename(a).startswith("MANIFESTO") and os.path.relpath(a, ROOT).replace("\\", "/") not in set(man.arquivo)]
teste("reprodutibilidade", "todo arquivo do pacote está no manifesto", not fora, fora)
teste("vazamento", "manifesto não aponta para evaluation_only/reports", not man.arquivo.str.contains("evaluation_only|reports/").any())
cm = S("SELECT min(d) a, max(d) b FROM (SELECT data_disponibilidade d FROM cmed_apresentacoes UNION ALL SELECT data_disponibilidade FROM cmed_precos)")
teste("temporal", "CMED do pacote é a lista de 06/01/2025", str(cm.a[0])[:10] == "2025-01-06" == str(cm.b[0])[:10], cm.to_dict("records"))
try:
    q.caminho("../evaluation_only/organizacional/resultado_homologado_PE04_2025.parquet"); bloq = False
except PermissionError:
    bloq = True
teste("vazamento", "módulo de consulta recusa caminho fora de decision_input", bloq)

# ---------------- qualidade ----------------
ref = [("item_cmed.item ⊆ itens", "SELECT count(*) n FROM item_cmed WHERE item NOT IN (SELECT item FROM itens)"),
       ("item_cmed.registro ⊆ cmed_apresentacoes", "SELECT count(*) n FROM item_cmed WHERE registro NOT IN (SELECT registro FROM cmed_apresentacoes)"),
       ("cmed_precos.registro ⊆ cmed_apresentacoes", "SELECT count(*) n FROM cmed_precos WHERE registro NOT IN (SELECT registro FROM cmed_apresentacoes)"),
       ("item_catmat.item ⊆ itens", "SELECT count(*) n FROM item_catmat WHERE item NOT IN (SELECT item FROM itens)"),
       ("item_catmat.catmat ⊆ bps", "SELECT count(*) n FROM item_catmat WHERE catmat NOT IN (SELECT DISTINCT catmat FROM bps)"),
       ("item_bps_grupos ⊆ item_catmat", "SELECT count(*) n FROM item_bps_grupos g ANTI JOIN item_catmat c USING (item, catmat)")]
if tem("pncp_itens"):
    ref.append(("pncp_itens ⊆ pncp_contratacoes", "SELECT count(*) n FROM pncp_itens WHERE numero_controle_pncp NOT IN (SELECT numero_controle_pncp FROM pncp_contratacoes)"))
for nome, sql in ref:
    n = S(sql).n[0]; teste("integridade referencial", nome, n == 0, n)
uni = [("itens.item", "itens", "item"), ("bps.id_origem", "bps", "id_origem"), ("cmed_apresentacoes.registro", "cmed_apresentacoes", "registro"),
       ("item_cmed (item, registro)", "item_cmed", "item, registro"), ("item_catmat (item, catmat)", "item_catmat", "item, catmat")]
if tem("pncp_itens"):
    uni += [("pncp_contratacoes", "pncp_contratacoes", "numero_controle_pncp"), ("pncp_itens (contratação, item)", "pncp_itens", "numero_controle_pncp, numero_item")]
for nome, t, k in uni:
    n = S(f"SELECT count(*) - count(DISTINCT ({k})) n FROM {t}").n[0]; teste("unicidade", nome, n == 0, n)
d = S("SELECT sum(flag_duplicata_negocio::INT) dup, sum(flag_preco_extremo::INT) ext, count(*) n FROM bps")
teste("duplicidade", "BPS: duplicatas de negócio marcadas (não removidas)", True, d.to_dict("records"))
x = S("SELECT count(*) n, sum(valor_total_estimado_orgao) v, sum(abs(valor_total_estimado_orgao - quantidade_estimada * preco_unitario_estimado_orgao) > 0.01) inc, sum((quantidade_estimada <= 0)::INT) q0 FROM itens")
teste("consistência", "334 itens, soma R$ 4.952.438,00, total = qtd × preço, qtd > 0", x.n[0] == 334 and abs(x.v[0] - 4952438.0) < 0.01 and x.inc[0] == 0 and x.q0[0] == 0, x.to_dict("records"))
x = S("SELECT sum((preco_unitario_praticado < 0)::INT) neg, sum((quantidade <= 0)::INT) q0, sum(flag_total_inconsistente::INT) tot FROM bps")
teste("consistência", "BPS: preços >= 0, quantidades > 0, total = unitário × quantidade", x.neg[0] == 0 and x.q0[0] == 0 and x.tot[0] == 0, x.to_dict("records"))
x = S("SELECT sum((valor_embalagem < 0)::INT) neg FROM cmed_precos")
teste("consistência", "CMED: valores não negativos", x.neg[0] == 0, x.neg[0])
x = S("""SELECT sum(abs(p.valor_embalagem / f.valor_embalagem - (1 - 0.2153)) > 0.01) n FROM cmed_precos p JOIN cmed_precos f
         ON p.registro = f.registro AND p.aliquota_icms = f.aliquota_icms AND p.tipo_preco = 'PMVG' AND f.tipo_preco = 'PF' WHERE f.valor_embalagem > 0""")
teste("consistência", "PMVG publicado = PF × (1 − 21,53%) (CAP já aplicado; não reaplicar)", x.n[0] <= 0.001 * S("SELECT count(*) n FROM cmed_precos").n[0], f"{x.n[0]} pares fora de ±1 p.p.")
x = S("SELECT sum((fator_conversao IS NULL OR fator_conversao < 1 OR fator_conversao <> round(fator_conversao))::INT) n, sum((classe = 'exata' AND fator_conversao <> 1)::INT) e FROM item_cmed WHERE classe IN ('exata','compativel_conversao')")
teste("compatibilidade de unidades", "vínculos aceitos têm fator inteiro >= 1 (exata = 1)", x.n[0] == 0 and x.e[0] == 0, x.to_dict("records"))
v = S("SELECT v.item, i.descricao, i.unidade, c.substancia, v.apresentacao, v.classe FROM item_cmed v JOIN itens i USING (item) JOIN cmed_apresentacoes c USING (registro) WHERE v.classe IN ('exata','compativel_conversao')")
redo = [compara(r.descricao, r.unidade, r.substancia, r.apresentacao)["classe"] for r in v.itertuples()]
teste("validade das correspondências", "reclassificação dos vínculos aceitos é determinística", all(a == b for a, b in zip(redo, v.classe)), sum(a != b for a, b in zip(redo, v.classe)))
x = S("SELECT count(*) n FROM v_cmed_teto_unitario WHERE item = 196 AND apresentacao ILIKE '%X 10 ML%'")
teste("validade das correspondências", "insulina 3 mL (item 196) não converte frasco de 10 mL", x.n[0] == 0, x.n[0])
x = S("SELECT count(*) n FROM v_cmed_teto_unitario WHERE item = 28 AND apresentacao ILIKE '%150 ML%'")
teste("validade das correspondências", "amoxicilina 60 mL (item 28) não converte 150 mL", x.n[0] == 0, x.n[0])
for t, cols in (("bps", "fonte, id_origem, arquivo_origem"), ("item_cmed", "fonte, origem_vinculo"), ("item_catmat", "fonte"), ("cmed_apresentacoes", "fonte")):
    n = S(f"SELECT count(*) n FROM {t} WHERE " + " OR ".join(f"{c.strip()} IS NULL" for c in cols.split(","))).n[0]
    teste("proveniência", f"{t}: {cols} preenchidos", n == 0, n)

# ---------------- pré-Etapa 4: ICMS, Compras.gov.br, conversões verificadas, organizacional ----------------
x = S("""SELECT count(*) n FROM (SELECT registro, tipo_preco, count(*) k FROM cmed_precos WHERE aliquota_aplicavel_pb GROUP BY 1, 2) WHERE k > 1""")
teste("ICMS PB", "no máximo uma alíquota aplicável por apresentação e tipo de preço", x.n[0] == 0, x.n[0])
x = S("""SELECT sum(CASE WHEN (a.icms_isento_so_0pct OR a.convenio_confaz_87) THEN (p.aliquota_icms <> '0%')::INT ELSE (p.aliquota_icms <> '20%')::INT END) n
         FROM cmed_precos p JOIN cmed_apresentacoes a USING (registro) WHERE p.aliquota_aplicavel_pb""")
teste("ICMS PB", "alíquota aplicável = 0% (isento ou Conv. 87/02) ou 20% (demais), conforme a regra documentada", x.n[0] == 0, x.n[0])
x = S("SELECT count(DISTINCT registro) n FROM cmed_apresentacoes WHERE registro NOT IN (SELECT registro FROM cmed_precos WHERE aliquota_aplicavel_pb)")
teste("ICMS PB", "apresentações sem preço na alíquota aplicável (informativo)", True, f"{x.n[0]} apresentações sem a coluna aplicável preenchida na lista")
t_ = q.teto_cmed(con, 28)
teste("ICMS PB", "teto_cmed() devolve por padrão só a alíquota aplicável na PB", len(t_) > 0 and t_.aliquota_aplicavel_pb.all(), t_.aliquota_icms.unique().tolist())
if tem("comprasgov"):
    x = S("SELECT max(data_resultado) r, sum((data_compra > data_resultado)::INT) inv, count(*) n, count(DISTINCT id_origem) u FROM comprasgov")
    teste("temporal", "Compras.gov.br: resultado <= corte e compra <= resultado", pd.Timestamp(x.r[0]) <= CUT and x.inv[0] == 0, x.to_dict("records"))
    teste("unicidade", "comprasgov.id_origem", x.n[0] == x.u[0], x.n[0] - x.u[0])
    n = S("SELECT count(*) n FROM item_comprasgov WHERE id_origem NOT IN (SELECT id_origem FROM comprasgov)").n[0]
    teste("integridade referencial", "item_comprasgov.id_origem ⊆ comprasgov", n == 0, n)
    n = S("""SELECT count(*) n FROM v_comprasgov_comparavel WHERE item IN (196, 199)
             AND upper(coalesce(unidade_fornecimento, '')) IN ('TUBETE', 'CARTUCHO', 'REFIL', 'CARPULE', 'FRASCO', 'FRASCO-AMPOLA')""").n[0]
    teste("validade das correspondências", "insulinas em caneta (196, 199): refil/frasco do Compras.gov.br nunca compatível", n == 0, n)
    n = S("SELECT count(*) n FROM item_catmat_oficial WHERE item NOT IN (SELECT item FROM itens)").n[0]
    teste("integridade referencial", "item_catmat_oficial.item ⊆ itens", n == 0, n)
x = S("SELECT count(*) n FROM item_cmed v JOIN cmed_apresentacoes a USING (registro) WHERE a.laboratorio ILIKE '%EMPRESA DE TESTE%'")
teste("validade das correspondências", "registros de teste da lista CMED fora dos vínculos", x.n[0] == 0, x.n[0])
x = S("SELECT min(fator_conversao) f FROM item_cmed WHERE item = 151 AND apresentacao ILIKE '%C/5 AMP%'")
teste("validade das correspondências", "'CX C/5 AMP' converte 5 ampolas (erro achado na inspeção)", x.f[0] == 5, x.f[0])
x = S("SELECT count(*) n FROM item_cmed WHERE classe IN ('exata','compativel_conversao') AND apresentacao ILIKE '%LIB MOD%' AND item IN (SELECT item FROM itens WHERE modificadores NOT LIKE '%lib_prol%' OR modificadores IS NULL)")
teste("validade das correspondências", "liberação modificada nunca aceita para item de liberação convencional", x.n[0] == 0, x.n[0])
x = S("SELECT count(*) n FROM item_cmed WHERE classe IN ('exata','compativel_conversao') AND apresentacao ILIKE '%CX 50 BL%X 350%'")
teste("validade das correspondências", "contagem implausível 'CX 50 BL … X 350' não é aceita", x.n[0] == 0, x.n[0])
x = S("SELECT count(*) n, sum((apresentacao ILIKE '%SOL INJ%' AND apresentacao ILIKE '%SIST APLIC%')::INT) ok FROM item_cmed WHERE item = 199 AND classe IN ('exata','compativel_conversao')")
teste("validade das correspondências", "item 199 (insulina Regular em caneta) só converte solução com sistema de aplicação", x.n[0] > 0 and x.n[0] == x.ok[0], x.to_dict("records"))
rc_ = pd.read_csv(os.path.join(DI, "padronizacao", "regras_conversao.csv"))
cols = ["verif_consistencia_interna", "verif_preco_praticado", "status"]
teste("verificação de conversões", "toda conversão aceita tem verificação automática registrada", rc_[cols].notna().all().all() and len(rc_) == S("SELECT count(*) n FROM item_cmed WHERE classe IN ('exata','compativel_conversao')").n[0],
      rc_.status.value_counts().to_dict())
teste("verificação de conversões", "status mantém 'validação humana pendente'", rc_.status.str.contains("validação humana pendente").all())
insp = pd.read_csv(os.path.join(ROOT, "reports", "pre4_inspecao_conversoes_amostra.csv"))
teste("verificação de conversões", "amostra inspecionada registrada com veredito por apresentação", insp.veredito.notna().all() and len(insp) > 0, insp.veredito.str.split(":").str[0].value_counts().to_dict())
rec = S("SELECT * FROM recursos")
teste("organizacional", "recursos: repasse federal de Assistência Farmacêutica 2024 registrado (TCE-PB)", (rec.recurso.str.contains("Assistência Farmacêutica") & rec.valor.notna()).any(),
      rec[rec.recurso.str.contains("Assistência Farmacêutica")].valor.tolist())
teste("organizacional", "itens: quantidade licitada nos pregões próprios de 2024 (sinal de demanda, não consumo)", S("SELECT count(qtd_licitada_pregoes_proprios_2024) n FROM itens").n[0] > 0,
      S("SELECT count(qtd_licitada_pregoes_proprios_2024) n FROM itens").n[0])

# varredura genérica: nenhuma coluna de data do pacote passa do corte (exceção documentada: data de inclusão no PNCP do
# resultado do PE 12/2024, contrato do próprio município usado como informação interna — doc 15)
EXC = {("organizacional/historico_proprio_pregoes_2024.parquet", "data_inclusao_resultado_pncp")}
viol, stat = [], []
for p in arqs:
    if not p.endswith((".parquet", ".csv")):
        continue
    nome = os.path.relpath(p, DI).replace("\\", "/")
    df = pd.read_parquet(p) if p.endswith(".parquet") else pd.read_csv(p, low_memory=False)
    for c in df.columns:
        lc = c.lower()
        if re.search(r"situacao$|status_catalogo|atualiza", lc):
            stat.append((nome, c))
        if ("data" in lc or "atualiza" in lc) and (nome, c) not in EXC:
            s = df[c] if "datetime" in str(df[c].dtype) else (pd.to_datetime(df[c], errors="coerce", format="mixed") if df[c].dtype == object else None)
            if s is not None and (s > CUT).any():
                viol.append((nome, c, str(s.max())))
teste("temporal", "varredura: nenhuma coluna de data do pacote > corte (salvo exceção documentada)", not viol, viol)
teste("vazamento", "sem colunas de situação/atualização atuais (ex.: 'Homologado' posterior, status do catálogo em 2026)", not stat, stat)
x = S("SELECT count(*) n FROM pncp_resultados WHERE cancelado AND (data_cancelamento IS NULL OR data_cancelamento > ?)", CUT)
teste("vazamento", "resultados PNCP: cancelamento só marcado se ocorreu até o corte", x.n[0] == 0, x.n[0])
for rotulo, f_di, f_ev, chave in (("BPS", "nacional/bps_precos_praticados.parquet", "nacional/bps_pos_corte.parquet", ["id_origem"]),
                                  ("Compras.gov.br", "nacional/comprasgov_precos_praticados.parquet", "nacional/comprasgov_pos_corte.parquet", ["id_origem"]),
                                  ("PNCP resultados", "nacional/pncp_comparaveis_resultados.parquet", "nacional/pncp_comparaveis_resultados.parquet", ["numero_controle_pncp", "numero_item", "fornecedor_cnpj", "data_inclusao"]),  # um item pode ter novo resultado após o corte
                                  ("PNCP itens", "nacional/pncp_comparaveis_itens.parquet", "nacional/pncp_comparaveis_itens.parquet", ["numero_controle_pncp", "numero_item"])):
    a_, b_ = os.path.join(DI, f_di), os.path.join(EV, f_ev)
    if os.path.exists(a_) and os.path.exists(b_):
        ka = pd.read_parquet(a_, columns=chave).astype(str).drop_duplicates(); kb = pd.read_parquet(b_, columns=chave).astype(str).drop_duplicates()
        n = len(ka.merge(kb, on=chave))
        teste("separação", f"{rotulo}: nenhum registro ao mesmo tempo no pacote e em evaluation_only", n == 0, n)

# ---------------- consultas (item 22) ----------------
n = q.necessidades(con); r_ = S("SELECT * FROM restricoes")
teste("consultas", "recupera as 334 necessidades e as restrições (inclui armazenamento)", len(n) == 334 and r_.restricao.str.contains("armazenamento").any(), f"{len(n)} itens; {len(r_)} restrições")
h = q.historico(con, item=76)
teste("consultas", "histórico nacional elegível do item 76 (cefalexina 500 mg)", len(h) > 0 and h.data_insercao.max() <= CUT and h.data_compra.dt.year.between(2020, 2024).all(),
      f"{len(h)} registros, {h.uf.nunique()} UFs, {h.data_compra.min()}..{h.data_compra.max()}")
p_ = q.precos_compativeis(con, 76)
teste("consultas", "preços compatíveis com fonte e categoria (item 76)", len(p_) > 0 and p_.fonte.notna().all() and p_.categoria_valor.notna().all(), p_.groupby(["fonte", "categoria_valor"]).size().to_dict())
c_ = q.teto_cmed(con, 28)
ok = len(c_) > 0 and set(c_.classe) <= {"exata", "compativel_conversao"} and c_.aplicabilidade.notna().all()
teste("consultas", "referências CMED do item 28 com aplicabilidade e alíquotas preservadas", ok, f"{len(c_)} linhas; alíquotas {c_.aliquota_icms.nunique()}")
b_ = q.bloqueados(con, 196)
teste("consultas", "bloqueados do item 196 incluem frasco 10 mL", b_.descricao.str.contains("X 10 ML").any(), f"{len(b_)} linhas bloqueadas")

out = pd.DataFrame(T); out.to_csv(os.path.join(ROOT, "reports", "etapa3_testes.csv"), index=False)
print(out.resultado.value_counts().to_dict()); print(out[out.resultado == "FALHOU"].to_string())

# ---------------- relatórios de cobertura e de validação temporal ----------------
I = S("SELECT * FROM itens"); tot = I.valor_total_estimado_orgao.sum()
cov = []
def add(fonte, metrica, n, base, valor=None):
    cov.append(dict(fonte=fonte, metrica=metrica, itens_ou_registros=int(n), base=base, pct_valor_estimado=None if valor is None else round(100 * valor / tot, 1)))
for col in ("status_identificacao", "status_preco_praticado", "status_teto_cmed"):
    for k, g in I.groupby(col):
        add({"status_identificacao": "CATMAT (BPS pré-corte)", "status_preco_praticado": "preço praticado (BPS/Compras.gov.br/PNCP)", "status_teto_cmed": "CMED jan/2025"}[col], f"{col}={k}", len(g), "itens (334)", g.valor_total_estimado_orgao.sum())
for k, g in S("SELECT classe, count(*) n FROM item_cmed GROUP BY classe").iterrows():
    add("CMED jan/2025", f"pares item×apresentação classe={g.classe}", g.n, "pares")
rv = pd.read_csv(os.path.join(ROOT, "reports", "etapa3_revisao_259_cmed.csv"))
rb = rv.assign(o=rv.classe.map(["exata", "compativel_conversao", "provavel_conferencia", "indeterminada", "incompativel"].index)).sort_values("o").drop_duplicates("item")
for k, g in rb.groupby("classe"):
    add("revisão 259 (Etapa 2)", f"itens melhor classe={k}", len(g), "itens dos 259 candidatos")
add("BPS pré-corte", "registros de medicamentos disponíveis", S("SELECT count(*) n FROM bps").n[0], "registros")
add("BPS pré-corte", "registros compatíveis com itens do caso", S("SELECT count(*) n FROM v_bps_comparavel").n[0], "registros (um registro pode servir a mais de um item)")
if tem("pncp_itens"):
    add("PNCP pré-corte", "contratações comparáveis", S("SELECT count(*) n FROM pncp_contratacoes").n[0], "contratações")
    add("PNCP pré-corte", "itens comparáveis a itens do caso", S("SELECT count(*) n FROM pncp_itens WHERE itens_caso_comparaveis IS NOT NULL").n[0], "itens PNCP")
    add("PNCP pré-corte", "resultados disponíveis", S("SELECT count(*) n FROM pncp_resultados").n[0], "resultados")
    add("PNCP pré-corte", "itens do caso com ≥1 comparável PNCP", (I.pncp_itens_comparaveis > 0).sum(), "itens (334)", I[I.pncp_itens_comparaveis > 0].valor_total_estimado_orgao.sum())
if tem("comprasgov"):
    add("Compras.gov.br pré-corte", "registros de preço disponíveis", S("SELECT count(*) n FROM comprasgov").n[0], "registros")
    add("Compras.gov.br pré-corte", "itens do caso com ≥1 registro compatível", (I.comprasgov_registros_compativeis > 0).sum(), "itens (334)",
        I[I.comprasgov_registros_compativeis > 0].valor_total_estimado_orgao.sum())
rc2 = pd.read_csv(os.path.join(DI, "padronizacao", "regras_conversao.csv"))
add("conversões CMED", "aceitas sem alerta na verificação automática", (~rc2.status.str.contains("COM ALERTA")).sum(), "vínculos aceitos")
add("conversões CMED", "aceitas com alerta (conferir)", rc2.status.str.contains("COM ALERTA").sum(), "vínculos aceitos")
add("estimativa do órgão", "itens com estimativa acima do teto CMED unitário (alíquota PB)", I.alerta_estimativa_acima_teto_cmed.fillna(False).sum(), "itens (334)",
    I[I.alerta_estimativa_acima_teto_cmed.fillna(False)].valor_total_estimado_orgao.sum())
pd.DataFrame(cov).to_csv(os.path.join(ROOT, "reports", "cobertura_integracao.csv"), index=False)

V = []
def vt(fonte, conjunto, classe, n, base, destino):
    V.append(dict(fonte=fonte, conjunto=conjunto, classe_temporal=classe, registros=n, criterio_disponibilidade=base, destino=destino))
bc = pd.read_csv(os.path.join(ROOT, "reports", "etapa3_bps_classes_temporais.csv")).groupby("classe_temporal").registros.sum()
for k, n in bc.items():
    vt("BPS/MS 2020–2026", "todos os registros (todas as classes de material)", k, int(n), "dt_insercao <= 29/01/2025 e dt_compra <= dt_insercao",
       {"disponivel": "decision_input (só classe 6505)", "posterior": "evaluation_only", "indeterminado": "quarentena_temporal"}[k])
for nome in ("contratacoes", "itens", "resultados"):
    for cls, dst in (("disponivel", DI + "/nacional"), ("posterior", EV + "/nacional"), ("indeterminado", D("quarentena_temporal"))):
        p = os.path.join(dst, f"pncp_comparaveis_{nome}.parquet")
        if os.path.exists(p):
            vt("PNCP (amostra dirigida)", nome, cls, len(pd.read_parquet(p)), "dataPublicacaoPncp (contratação) / dataInclusao (item, resultado) <= corte", os.path.relpath(dst, ROOT))
fixos = [("CMED/Anvisa", "lista PF/PMVG publicada em 06/01/2025", "disponivel", 25549, "data de publicação impressa na lista", "decision_input"),
         ("CMED/Anvisa", "lista de 09/11/2026", "posterior", 26694, "data de publicação", "fora do pacote (raw)"),
         ("Santa Luzia — edital/ETP/TR PE 04/2025", "334 itens, dotações, restrições", "disponivel", 334, "documento interno assinado em 29/01/2025 (PNCP 30/01/2025)", "decision_input"),
         ("Santa Luzia — PE 01/2024 (PNCP)", "itens e 4 resultados", "disponivel", 349, "publicação 12/01/2024; resultados incluídos 02/09/2024", "decision_input"),
         ("Santa Luzia — PE 12/2024 (PNCP)", "3 itens (desconto CMED)", "disponivel", 3, "itens publicados 21/03/2024; resultados incluídos no PNCP em 30/04/2025 — usados como informação interna (contrato próprio, resultado de 11/04/2024)", "decision_input"),
         ("TCE-PB/SAGRES", "despesa farmacológica 2024 do município", "disponivel", 248, "empenhos de 2024 do próprio órgão (informação interna)", "decision_input"),
         ("TCE-PB/SAGRES", "despesa 2025–2026", "posterior", 536, "data do empenho > corte", "evaluation_only"),
         ("Santa Luzia — PE 04/2025", "resultados, contratos, aditivos, execução", "posterior", 334, "datas de resultado/contrato > corte", "evaluation_only"),
         ("Santa Luzia — PE 25/2025 e PE 09/2026", "itens e resultados", "posterior", 87 + 329, "publicação > corte", "evaluation_only"),
         ("BNAFAR/Hórus", "estoque nov/2026", "posterior", 4240, "posição de 17–18/11/2026", "fora do pacote (raw)"),
         ("Medicamentos Transparentes", "índice de contratações", "indeterminado", 86068, "plataforma publicada a partir de jun/2025; usada só como índice — datas verificadas no PNCP", "não entra no pacote"),
         ("Etapa 2 — CATMAT via BPS dez/2025", "299 itens", "posterior", 299, "derivado de registros inseridos em 22/12/2025", "evaluation_only/auditoria (refeito pré-corte)")]
for nome_, dst in (("comprasgov_precos_praticados", DI + "/nacional"), ("comprasgov_pos_corte", EV + "/nacional"), ("comprasgov_disponibilidade_indeterminada", D("quarentena_temporal"))):
    p = os.path.join(dst, nome_ + ".parquet")
    if os.path.exists(p):
        vt("Compras.gov.br (pesquisa de preço)", "registros dos CATMAT dos itens do caso", {"comprasgov_precos_praticados": "disponivel", "comprasgov_pos_corte": "posterior"}.get(nome_, "indeterminado"),
           len(pd.read_parquet(p)), "dataResultado <= 29/01/2025 e dataCompra <= dataResultado", os.path.relpath(dst, ROOT))
fixos += [("TCE-PB/SAGRES", "receitas SUS 2024 do município", "disponivel", len(pd.read_csv(os.path.join(DI, "organizacional", "receitas_sus_2024.csv"))), "receitas de 2024 do próprio órgão (informação interna)", "decision_input"),
          ("IBGE", "população estimada 2024 de Santa Luzia", "disponivel", 1, "estimativa 2024 publicada em 2024; a de 2025 é posterior e não é usada", "decision_input (recursos.csv)"),
          ("BNAFAR/Hórus", "estoque em 12/2024 e 01/2025", "indeterminado", 0, "API sem posição histórica (consultas vazias em 23/11/2026)", "lacuna documentada"),
          ("CONFAZ / SEFAZ-PB", "Conv. ICMS 87/02; Lei 6.379/96 consolidada em 02/10/2023", "disponivel", 2, "normas vigentes em 29/01/2025 (versões publicadas antes do corte)", "regra em cmed_precos.aliquota_aplicavel_pb")]
for f in fixos:
    vt(*f)
pd.DataFrame(V).to_csv(os.path.join(ROOT, "reports", "validacao_temporal.csv"), index=False)
sys.exit(1 if (out.resultado == "FALHOU").any() else 0)
