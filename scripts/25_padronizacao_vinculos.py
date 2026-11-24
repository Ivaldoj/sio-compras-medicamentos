"""Etapa 3 — padronização dos 334 itens de Santa Luzia e vínculos SÓ com evidência anterior ao corte:
  (1) item -> CATMAT candidatos, por atributos (princípio ativo, concentração, forma) do catálogo presente no BPS disponível;
  (2) item -> apresentações CMED jan/2025, por atributos e embalagem (sem passar pelo CATMAT da Etapa 2, que usou dados pós-corte);
  (3) revisão das 259 correspondências candidatas da Etapa 2 (mesmo classificador; origem marcada como pós-corte);
  (4) auditoria (só em evaluation_only): concordância com o CATMAT da Etapa 2.
Uso: python -I -X utf8 25_padronizacao_vinculos.py <raiz_projeto>"""
import json, os, re, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from padroniza import principio, principio_catmat, concentracoes, forma, forma_compativel, conteudo_item, compara, norm, nivel_catmat, ORDEM

ROOT = sys.argv[1]
D = lambda *p: os.path.join(ROOT, "data", *p)
for p in ("processed/etapa3", "decision_input/padronizacao", "evaluation_only/auditoria"):
    os.makedirs(D(p), exist_ok=True)

# (0) itens: fonte = edital/TR assinado em 29/01/2025 (itens do PNCP, publicação 30/01/2025 07:34)
src = "data/raw/pncp/etapa2/09090689000167_2025_6/itens_p1.json"
it = pd.DataFrame(json.load(open(os.path.join(ROOT, src), encoding="utf8")))
assert len(it) == 334 and it.numeroItem.is_unique
I = pd.DataFrame({"item": it.numeroItem, "descricao": it.descricao, "unidade": it.unidadeMedida, "quantidade_estimada": it.quantidade,
                  "preco_unitario_estimado_orgao": it.valorUnitarioEstimado, "valor_total_estimado_orgao": it.valorTotal})
I["principio_tokens"] = I.descricao.map(lambda s: "|".join(sorted(principio(s))))
I["concentracoes"] = I.descricao.map(lambda s: "; ".join(f"{v:g} {u}" for v, u in sorted(concentracoes(s))))
fm = I.apply(lambda r: forma(r.descricao + " " + r.unidade), axis=1)
I["forma"] = [f for f, _ in fm]; I["modificadores"] = ["|".join(sorted(m)) for _, m in fm]
I["conteudo_recipiente"] = I.descricao.map(lambda s: (lambda c: f"{c[0]:g} {c[1]}" if c else None)(conteudo_item(s)))
I["fonte"] = "Edital PE 04/2025 (ETP/TR) assinado em 29/01/2025; itens PNCP 09090689000167-1-000006/2025"
I["arquivo_origem"] = src

# (1) CATMAT por atributos — catálogo = CATMATs presentes no BPS disponível (inserido até o corte)
bps = pd.read_parquet(D("decision_input", "nacional", "bps_precos_praticados.parquet"),
                      columns=["catmat", "descricao_catmat", "principio_ativo_pdm", "unidade_fornecimento"])
cat = bps.groupby("catmat").agg(descricao_catmat=("descricao_catmat", "first"), pdm=("principio_ativo_pdm", "first"),
                                unidades=("unidade_fornecimento", lambda s: "|".join(sorted(s.dropna().unique())))).reset_index()
cat["p"] = [principio_catmat(p_, d_) for p_, d_ in zip(cat.pdm, cat.descricao_catmat)]; cat["c"] = cat.descricao_catmat.map(concentracoes)
UF_FORMA = {"comprimido": "comprimido", "capsula": "capsula", "dragea": "comprimido"}
def forma_cat(r):
    f, m = forma(r.descricao_catmat)
    if not f:
        us = {UF_FORMA.get(norm(u)) for u in r.unidades.split("|")} - {None}
        # mesmo CATMAT comprado como comprimido, cápsula ou drágea: forma sólida não diferenciada no catálogo
        f = us.pop() if len(us) == 1 else ("solido" if us and us <= {"comprimido", "capsula"} else None)
    return f, m
cat["f"] = cat.apply(forma_cat, axis=1)
idx = {}
for k, r in cat.iterrows():
    idx.setdefault(r.p, []).append(k)
rows = []
for _, r in I.iterrows():
    for k in idx.get(principio(r.descricao), []):
        x = cat.loc[k]
        nivel = nivel_catmat(r.descricao, r.unidade, x.c, x.f)
        if not nivel:
            continue
        rows.append(dict(item=r["item"], catmat=x.catmat, descricao_catmat=x.descricao_catmat, unidades_fornecimento_bps=x.unidades,
                         nivel=nivel, criterio="princípio ativo + concentração" + (" + forma/modificadores" if nivel == "atributos_compativeis" else ""),
                         fonte="BPS inserido até 29/01/2025 (catálogo observado)"))
C = pd.DataFrame(rows)
st = C.groupby("item").nivel.agg(lambda s: "unico" if (s == "atributos_compativeis").sum() == 1 else
                                 "multiplo" if (s == "atributos_compativeis").sum() > 1 else "parcial")
I["catmat_status"] = I["item"].map(st).fillna("nao_identificado")
I["catmat_candidatos"] = I["item"].map(C[C.nivel == "atributos_compativeis"].groupby("item").catmat.agg("|".join))
C.to_parquet(D("decision_input", "padronizacao", "item_catmat_candidatos.parquet"), index=False)
print("CATMAT pré-corte:", I.catmat_status.value_counts().to_dict(), "| pares:", len(C))

# (2) CMED jan/2025 direto por atributos
cm = pd.read_parquet(D("processed", "cmed_pmvg_20250107.parquet"))
cm = cm[~cm["LABORATÓRIO"].str.contains("EMPRESA DE TESTE", case=False, na=False)]  # 2 registros de teste da própria lista CMED
cm["p"] = cm["SUBSTÂNCIA"].map(principio)
cidx = cm.groupby("p").groups
L = []
for _, r in I.iterrows():
    # o nome CMED da insulina não traz o tipo "regular" (a forma solução × suspensão decide em compara)
    pr = principio(r.descricao)
    for k in list(cidx.get(pr, [])) + (list(cidx.get(pr - {"regular"}, [])) if "regular" in pr else []):
        x = cm.loc[k]
        res = compara(r.descricao, r.unidade, x["SUBSTÂNCIA"], x["APRESENTAÇÃO"])
        L.append(dict(item=r["item"], registro=x.reg, substancia=x["SUBSTÂNCIA"], produto=x["PRODUTO"], laboratorio=x["LABORATÓRIO"],
                      apresentacao=x["APRESENTAÇÃO"].strip(), classe=res["classe"], fator_conversao=res["fator"],
                      unidade_origem="embalagem CMED (apresentação)", unidade_destino=r.unidade,
                      justificativa="; ".join(res["motivos"]) or ("1 embalagem = 1 unidade do item" if res["fator"] == 1 else
                                     f"embalagem contém {res['fator']} unidade(s) de {r.unidade.lower()} (padrão 'X n'/'CT n')" if res["fator"] else ""),
                      origem_vinculo="atributos (pré-corte)", fonte="CMED PF/PMVG publicada em 06/01/2025"))
V = pd.DataFrame(L)
V["validacao_humana"] = "pendente"
V.to_parquet(D("decision_input", "padronizacao", "item_cmed_vinculos.parquet"), index=False)
best = V.assign(o=V.classe.map(ORDEM.index)).sort_values("o").drop_duplicates("item").set_index("item").classe
I["cmed_melhor_classe"] = I["item"].map(best).fillna("sem_candidato")
print("CMED pré-corte: pares", len(V), "| por classe:", V.classe.value_counts().to_dict())
print("CMED pré-corte por item (melhor classe):", I.cmed_melhor_classe.value_counts().to_dict())

# (3) revisão das 259 correspondências da Etapa 2
e2 = pd.read_csv(D("processed", "caso_santa_luzia", "pre_decisao", "itens_cmed_jan2025.csv"), dtype={"reg": str})
rv = [dict(item=r["item"], registro=r.reg, apresentacao=str(r["APRESENTAÇÃO"]).strip(),
           **{k: v for k, v in compara(r.descricao, r.unidade, r["SUBSTÂNCIA"], r["APRESENTAÇÃO"]).items() if k != "motivos"},
           motivos="; ".join(compara(r.descricao, r.unidade, r["SUBSTÂNCIA"], r["APRESENTAÇÃO"])["motivos"]))
      for _, r in e2.iterrows()]
RV = pd.DataFrame(rv)
RV["origem"] = "Etapa 2 (descoberto via CATMAT obtido de dados pós-corte) — excluído do pacote decisório"
RV["tambem_encontrado_pre_corte"] = RV.set_index(["item", "registro"]).index.isin(V.set_index(["item", "registro"]).index)
RV.to_csv(os.path.join(ROOT, "reports", "etapa3_revisao_259_cmed.csv"), index=False)
rb = RV.assign(o=RV.classe.map(ORDEM.index)).sort_values("o").drop_duplicates("item")
print("\nRevisão Etapa 2: itens", RV["item"].nunique(), "| pares", len(RV), "| pares por classe:", RV.classe.value_counts().to_dict())
print("  por item (melhor classe):", rb.classe.value_counts().to_dict(), "| pares também achados pré-corte:", int(RV.tambem_encontrado_pre_corte.sum()))

# (4) auditoria — usa CATMAT da Etapa 2 (pós-corte): só em evaluation_only
e2c = pd.read_csv(os.path.join(ROOT, "reports", "caso_sl_itens_pe04_2025.csv"), dtype={"catmat": str})[["numeroItem", "catmat"]].rename(columns={"numeroItem": "item", "catmat": "catmat_etapa2"})
au = I[["item", "catmat_status", "catmat_candidatos"]].merge(e2c, on="item")
au["concorda"] = [bool(c2) and isinstance(cs, str) and c2 in cs.split("|") for c2, cs in zip(au.catmat_etapa2, au.catmat_candidatos)]
au.to_csv(D("evaluation_only", "auditoria", "catmat_etapa2_vs_pre_corte.csv"), index=False)
m = au.catmat_etapa2.notna() & au.catmat_candidatos.notna()
print("\nauditoria: itens com CATMAT nas duas abordagens:", int(m.sum()), "| concordância: %.1f%%" % (100 * au[m].concorda.mean()))

I.to_parquet(D("processed", "etapa3", "itens_atributos.parquet"), index=False)  # intermediário; o pacote usa itens_santa_luzia (script 27)
pend = V[V.classe.isin(["provavel_conferencia", "indeterminada"])].copy()
blq = V[(V.classe == "incompativel") & V.justificativa.str.contains("conteúdo do recipiente difere|forma difere")].copy()
blq["situacao"] = "bloqueado: apresentação distinta (não converter)"
pend["situacao"] = "exige conferência humana"
cols = ["situacao", "item", "registro", "produto", "apresentacao", "classe", "fator_conversao", "unidade_destino", "justificativa"]
P = pd.concat([pend, blq])[cols].merge(I[["item", "descricao", "valor_total_estimado_orgao"]], on="item")
P.to_csv(os.path.join(ROOT, "reports", "pendencias_conversao.csv"), index=False)
print("pendências de conversão:", P.situacao.value_counts().to_dict(), "| itens envolvidos:", P["item"].nunique())
for it_ in (196, 28):
    print(f"item {it_}:", V[V["item"] == it_].classe.value_counts().to_dict())
