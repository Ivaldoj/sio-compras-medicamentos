"""Etapa 5 / 03 — comparação ex post da decisão do agente com os dados reservados.

Entradas (somente leitura):
  etapa4/ambiente_decisor/saida/plano_por_item.csv   decisão congelada
  data/evaluation_only/                              resultados reais (pós-corte)
  data/decision_input_v2/padronizacao/               regras de compatibilidade com a errata (só para casar
                                                     registros nacionais pós-corte com os itens)
  evidencias_primarias/pncp/.../Ata Final.pdf        propostas e lances do PE 04/2025

Saídas em resultados/:
  expost_itens.csv            uma linha por item: referência do agente × homologado × mercado nacional 2025 × PE 09/2026 × competição
  expost_resumo_grupos.csv    indicadores por grupo de itens
  expost_totais.csv           totais (R0, R1, E1, homologado, contrafactuais de preço)
  expost_competicao.csv       propostas por item (Ata Final)
  expost_execucao_contratos.csv, expost_gasto_por_licitacao.csv, expost_gasto_mensal.csv
  expost_escopo.csv           necessidades fora do plano (PE 25/2025) e recorrência (PE 09/2026)
  expost_numeros.json         números-chave
"""
import json
import os
import pickle
import re
import sys
import tempfile
import unicodedata

import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e5_comum import EVAL, HORIZ_FIM, HORIZ_INI, PRIM, RES, SAIDA, V1, V2, sha256

N = {}  # números-chave
plano = pd.read_csv(os.path.join(SAIDA, "plano_por_item.csv"))
hom = pd.read_parquet(os.path.join(EVAL, "organizacional", "resultado_homologado_PE04_2025.parquet"))
itens_v1 = pd.read_parquet(os.path.join(V1, "organizacional", "itens_santa_luzia.parquet"))

d = plano.merge(hom[["item", "quantidade_homologada", "preco_unitario_homologado", "cnpj_fornecedor", "data_resultado"]], on="item", how="left")
assert len(d) == 334 and d.preco_unitario_homologado.notna().all() and (d.quantidade_etp == d.quantidade_homologada).all()
d = d.rename(columns={"quantidade_etp": "q", "preco_ref_unitario": "p_ref", "faixa_preco_baixo": "p_lo", "faixa_preco_alto": "p_hi",
                      "preco_estimado_orgao": "p_org", "preco_unitario_homologado": "p_hom", "teto_cmed_unitario_aplicavel_max": "teto"})
d["grupo_fonte"] = d.fonte_preco_ref.str.split(r" \(| —", regex=True).str[0]
d["v_hom"] = d.q * d.p_hom
d["v_ref"] = d.q * d.p_ref
d["hom_sobre_ref"] = d.p_hom / d.p_ref
d["hom_sobre_org"] = d.p_hom / d.p_org
d["hom_igual_estimativa"] = np.isclose(d.p_hom, d.p_org, atol=0.005)
d["hom_dentro_faixa"] = (d.p_hom >= d.p_lo - 1e-9) & (d.p_hom <= d.p_hi + 1e-9)
d["hom_abaixo_faixa"] = d.p_hom < d.p_lo - 1e-9
d["hom_acima_faixa"] = d.p_hom > d.p_hi + 1e-9
d["hom_acima_teto_agente"] = d.teto.notna() & (d.p_hom > d.teto + 0.005)
d = d.merge(itens_v1[["item", "teto_cmed_unitario_pb_max"]].rename(columns={"teto_cmed_unitario_pb_max": "teto_pacote_todos_vinculos"}), on="item")
caneta = d.item.isin([196, 199])

# ------------------------------------------------------------------ mercado nacional no horizonte da necessidade
g2 = pd.read_parquet(os.path.join(V2, "padronizacao", "item_bps_grupos.parquet"))
g2 = g2[g2.compatibilidade == "compativel"]
bps = pd.read_parquet(os.path.join(EVAL, "nacional", "bps_pos_corte.parquet"))
bps = bps[(bps.data_compra >= HORIZ_INI) & (bps.data_compra <= HORIZ_FIM) & ~bps.flag_preco_extremo & ~bps.flag_duplicata_negocio
          & (bps.preco_unitario_praticado > 0)]
chave = ["catmat", "unidade_fornecimento", "capacidade_descricao"]
for c in chave:
    g2[c] = g2[c].fillna("∅")
    bps[c] = bps[c].fillna("∅")
nb = g2[["item"] + chave].merge(bps[chave + ["preco_unitario_praticado", "uf", "esfera", "data_compra"]], on=chave)
nb["fonte"] = "BPS"

# Compras.gov.br pós-corte: não há vínculo registro×item; uso a mesma regra do pacote, inferida dos registros pré-corte:
# combinações (item, CATMAT, unidade de fornecimento, capacidade) em que TODOS os registros pré-corte são 'compativel'.
ic = pd.read_parquet(os.path.join(V2, "padronizacao", "item_comprasgov_registros.parquet"))
cg_pre = pd.read_parquet(os.path.join(V2, "nacional", "comprasgov_precos_praticados.parquet"),
                         columns=["id_origem", "unidade_fornecimento", "capacidade_valor", "capacidade_unidade"])
kc = ["catmat", "unidade_fornecimento", "capacidade_valor", "capacidade_unidade"]
m = ic.merge(cg_pre, on="id_origem")
for c in kc[1:]:
    m[c] = m[c].astype(object).where(m[c].notna(), "∅").astype(str)
regra = m.groupby(["item"] + kc).compatibilidade.agg(n="size", comp=lambda s: (s == "compativel").mean()).reset_index()
regra_ok = regra[regra.comp == 1.0]
N["comprasgov_regra_combinacoes_compat"] = int(len(regra_ok))
N["comprasgov_regra_combinacoes_mistas"] = int(((regra.comp > 0) & (regra.comp < 1)).sum())
cg = pd.read_parquet(os.path.join(EVAL, "nacional", "comprasgov_pos_corte.parquet"))
cg = cg[(cg.data_compra >= HORIZ_INI) & (cg.data_compra <= HORIZ_FIM) & ~cg.flag_possivel_duplicata_bps & (cg.preco_unitario_praticado > 0)]
for c in kc[1:]:
    cg[c] = cg[c].astype(object).where(cg[c].notna(), "∅").astype(str)
nc = regra_ok[["item"] + kc].merge(cg[kc + ["preco_unitario_praticado", "uf", "esfera", "data_compra"]], on=kc)
nc["fonte"] = "Compras.gov.br"
nac = pd.concat([nb[["item", "fonte", "preco_unitario_praticado", "uf", "esfera"]], nc[["item", "fonte", "preco_unitario_praticado", "uf", "esfera"]]])
nac = nac.merge(d[["item", "p_ref", "p_hi", "p_hom", "p_org"]], on="item")
ag = nac.groupby("item").agg(nac_n=("preco_unitario_praticado", "size"), nac_ufs=("uf", "nunique"),
                             nac_p25=("preco_unitario_praticado", lambda s: s.quantile(.25)),
                             nac_med=("preco_unitario_praticado", "median"),
                             nac_p75=("preco_unitario_praticado", lambda s: s.quantile(.75))).reset_index()
ag["nac_frac_ate_ref"] = nac.assign(x=nac.preco_unitario_praticado <= nac.p_ref + 1e-9).groupby("item").x.mean().values
ag["nac_frac_ate_alto"] = nac.assign(x=nac.preco_unitario_praticado <= nac.p_hi + 1e-9).groupby("item").x.mean().values
ag["nac_frac_ate_hom"] = nac.assign(x=nac.preco_unitario_praticado <= nac.p_hom + 1e-9).groupby("item").x.mean().values
ne = nac[nac.uf.isin(["PB", "PE", "RN", "CE", "AL", "SE", "BA", "PI", "MA"])].groupby("item").preco_unitario_praticado.agg(ne_n="size", ne_med="median").reset_index()
d = d.merge(ag, on="item", how="left").merge(ne, on="item", how="left")
MIN_N = 5
d["nac_ok"] = d.nac_n >= MIN_N
d.loc[~d.nac_ok, ["nac_p25", "nac_med", "nac_p75", "nac_frac_ate_ref", "nac_frac_ate_alto", "nac_frac_ate_hom"]] = np.nan
d["ref_sobre_nac"] = d.p_ref / d.nac_med
d["org_sobre_nac"] = d.p_org / d.nac_med
d["hom_sobre_nac"] = d.p_hom / d.nac_med

# ------------------------------------------------------------------ mesmo comprador, um ano depois: PE 09/2026
norm = lambda s: re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower())
p26 = pd.read_parquet(os.path.join(EVAL, "organizacional", "pregao_09_2026_itens_resultados.parquet"))
p26["chave"] = p26.descricao.map(norm)
p26u = p26.drop_duplicates("chave")
d["chave"] = d.descricao.map(norm)
d = d.merge(p26u[["chave", "valorUnitarioEstimado", "valorUnitarioHomologado", "quantidade", "situacaoCompraItemNome"]]
            .rename(columns={"valorUnitarioEstimado": "p_est_2026", "valorUnitarioHomologado": "p_hom_2026", "quantidade": "q_2026",
                             "situacaoCompraItemNome": "situacao_2026"}), on="chave", how="left")
d["hom2026_sobre_ref"] = d.p_hom_2026 / d.p_ref
d["hom2026_sobre_hom2025"] = d.p_hom_2026 / d.p_hom

# ------------------------------------------------------------------ competição: propostas por item (Ata Final)
ata = os.path.join(PRIM, "pncp", "09090689000167_2025_6", "docs", "16_extraido", "Ata Final.pdf")
cache = os.path.join(tempfile.gettempdir(), f"e5_ata_final_{sha256(ata)[:16]}.pkl")
if os.path.exists(cache):
    paginas = pickle.load(open(cache, "rb"))
else:
    from pypdf import PdfReader
    paginas = [(p.extract_text() or "") for p in PdfReader(ata).pages]
    pickle.dump(paginas, open(cache, "wb"))
ini = next(i for i, t in enumerate(paginas) if "Lances Enviados" in t)
texto = "\n".join(paginas[ini:])
texto = texto[texto.index("Lances Enviados"):]
texto = re.sub(r"A autenticidade do documento.*?\nP[áa]gina \d+ de \d+\n", "", texto, flags=re.S)
blocos = re.split(r"(?m)^(\d{4}) - ", texto)
comp_rows = []
pad = re.compile(r"(\d{2}/\d{2}/\d{4}) - (\d{2}:\d{2}:\d{2}) ([\d.]+,\d+) \((proposta|lance)\) (\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})")
for k in range(1, len(blocos) - 1, 2):
    it = int(blocos[k])
    if not (1 <= it <= 334) or "Data Valor CNPJ" not in blocos[k + 1][:400]:
        continue
    ev = pad.findall(blocos[k + 1])
    if not ev:
        continue
    vals = [float(v.replace(".", "").replace(",", ".")) for _, _, v, _, _ in ev]
    comp_rows.append({"item": it, "n_proponentes": len({c for *_, c in ev}), "n_propostas": sum(t == "proposta" for *_, t, _ in ev),
                      "n_lances": sum(t == "lance" for *_, t, _ in ev), "menor_valor_ofertado": min(vals), "maior_valor_ofertado": max(vals)})
comp = pd.DataFrame(comp_rows).drop_duplicates("item")
comp.to_csv(os.path.join(RES, "expost_competicao.csv"), index=False, encoding="utf-8")
d = d.merge(comp, on="item", how="left")
N["competicao_itens_extraidos"] = int(d.n_proponentes.notna().sum())

# ------------------------------------------------------------------ resumos por grupo
def resumo(nome, m_):
    g = d[m_]
    if not len(g):
        return None
    r = {"grupo": nome, "itens": len(g), "v_org": g.valor_estimado_orgao.sum(), "v_ref_agente": g.v_ref.sum(), "v_ref_baixo": g.valor_faixa_baixo.sum(),
         "v_ref_alto": g.valor_faixa_alto.sum(), "v_homologado": g.v_hom.sum(),
         "hom_sobre_ref_mediana": g.hom_sobre_ref.median(), "hom_sobre_ref_ponderada": g.v_hom.sum() / g.v_ref.sum(),
         "pct_hom_dentro_faixa": 100 * g.hom_dentro_faixa.mean(), "pct_hom_abaixo_faixa": 100 * g.hom_abaixo_faixa.mean(),
         "pct_hom_acima_faixa": 100 * g.hom_acima_faixa.mean(), "valor_hom_itens_acima_faixa": g.loc[g.hom_acima_faixa, "v_hom"].sum(),
         "itens_hom_igual_estimativa": int(g.hom_igual_estimativa.sum()), "itens_hom_acima_teto": int(g.hom_acima_teto_agente.sum()),
         "itens_com_mediana_nacional": int(g.nac_ok.sum()),
         "ref_sobre_nac_mediana": g.ref_sobre_nac.median(), "org_sobre_nac_mediana": g.org_sobre_nac.median(), "hom_sobre_nac_mediana": g.hom_sobre_nac.median(),
         "erro_abs_mediano_ref_vs_nac_pct": 100 * (g.ref_sobre_nac - 1).abs().median(),
         "erro_abs_mediano_org_vs_nac_pct": 100 * (g.org_sobre_nac - 1).abs().median(),
         "proponentes_mediana": g.n_proponentes.median(), "itens_1_proponente": int((g.n_proponentes == 1).sum())}
    return r


grupos = [("TODOS", np.ones(len(d), bool)), ("todos exceto canetas 196/199", ~caneta), ("canetas de insulina humana (196, 199)", caneta),
          ("insulinas (194–199)", d.item.between(194, 199)), ("análogas (194, 195)", d.item.isin([194, 195])),
          ("frascos (197, 198)", d.item.isin([197, 198]))]
grupos += [("fonte: " + f, d.grupo_fonte == f) for f in d.grupo_fonte.unique()]
grupos += [("flag: a conferir", d.flag_a_conferir), ("flag: sem referência externa", d.flag_sem_referencia_externa),
           ("flag: referência fraca", d.flag_referencia_fraca), ("flag: estimativa acima do teto (agente)", d.flag_acima_teto_confirmado),
           ("flag: sem teto utilizável", d.flag_sem_teto_utilizavel),
           ("competição: 1 proponente", d.n_proponentes == 1), ("competição: 2–3 proponentes", d.n_proponentes.between(2, 3)),
           ("competição: 4+ proponentes", d.n_proponentes >= 4)]
rg = pd.DataFrame([r for r in (resumo(n, m_) for n, m_ in grupos) if r])
rg.to_csv(os.path.join(RES, "expost_resumo_grupos.csv"), index=False, encoding="utf-8")

# ------------------------------------------------------------------ totais e contrafactuais de PREÇO (quantidade = ETP)
T = []
tot = lambda s: float((d.q * s).sum())
R0, E1c, E1b, E1a, HOM = float(d.valor_estimado_orgao.sum()), float(d.v_ref.sum()), float(d.valor_faixa_baixo.sum()), float(d.valor_faixa_alto.sum()), float(d.v_hom.sum())
R1 = tot(np.where(d.teto.notna(), np.minimum(d.p_org, d.teto), d.p_org))
T += [("R0 estimativa do órgão", R0, "ex ante, do órgão"), ("R1 estimativa limitada ao teto (agente)", R1, "ex ante, do agente"),
      ("E1 central (agente)", E1c, "ex ante, potencial"), ("E1 baixo (agente)", E1b, "ex ante, potencial"), ("E1 alto (agente)", E1a, "ex ante, potencial"),
      ("Homologado PE 04/2025 (decisão real)", HOM, "ex post, contratado"),
      ("Homologado — canetas 196/199", float(d.loc[caneta, "v_hom"].sum()), "ex post, contratado"),
      ("Homologado — demais 332 itens", float(d.loc[~caneta, "v_hom"].sum()), "ex post, contratado"),
      ("E1 central — canetas 196/199", float(d.loc[caneta, "v_ref"].sum()), "ex ante, potencial"),
      ("E1 central — demais 332 itens", float(d.loc[~caneta, "v_ref"].sum()), "ex ante, potencial"),
      ("E1 alto — demais 332 itens", float(d.loc[~caneta, "valor_faixa_alto"].sum()), "ex ante, potencial"),
      ("E1 baixo — demais 332 itens", float(d.loc[~caneta, "valor_faixa_baixo"].sum()), "ex ante, potencial")]
# contrafactual A: preços reais homologados, com o teto CMED do agente aplicado onde existe (regra de aceitabilidade do E1)
pA = np.where(d.teto.notna(), np.minimum(d.p_hom, d.teto), d.p_hom)
T.append(("Contrafactual A: homologado real limitado ao teto CMED (regra de aceitabilidade do E1)", tot(pA), "estimativa ex post (não observado)"))
# contrafactual B: menor entre homologado e limite alto do agente (o E1 não aceitaria acima da referência; se ninguém baixasse = deserto)
pB = np.minimum(d.p_hom, d.p_hi)
T.append(("Contrafactual B: min(homologado, limite alto do agente)", tot(pB), "estimativa ex post (não observado)"))
# contrafactual C: mediana nacional do horizonte (itens com ≥5 registros); demais = homologado limitado ao teto
pC = np.where(d.nac_ok, np.where(d.teto.notna(), np.minimum(d.nac_med, d.teto), d.nac_med), pA)
T.append((f"Contrafactual C: mediana nacional {HORIZ_INI}..{HORIZ_FIM} (≥{MIN_N} registros; {int(d.nac_ok.sum())} itens), demais = A", tot(pC),
          "estimativa ex post (não observado)"))
sub = d.nac_ok
T += [(f"Subconjunto com mediana nacional ({int(sub.sum())} itens): E1 central", float(d.loc[sub, 'v_ref'].sum()), "ex ante"),
      (f"Subconjunto com mediana nacional ({int(sub.sum())} itens): mediana nacional do horizonte", float((d.q * d.nac_med)[sub].sum()), "ex post, mercado"),
      (f"Subconjunto com mediana nacional ({int(sub.sum())} itens): homologado", float(d.loc[sub, 'v_hom'].sum()), "ex post, contratado"),
      (f"Subconjunto com mediana nacional ({int(sub.sum())} itens): estimativa do órgão", float(d.loc[sub, 'valor_estimado_orgao'].sum()), "ex ante, do órgão")]
s26 = d.p_hom_2026.notna()
T += [(f"Itens repetidos e homologados no PE 09/2026 ({int(s26.sum())} itens), quantidade do ETP 2025: E1 central", float(d.loc[s26, 'v_ref'].sum()), "ex ante"),
      (f"Idem: homologado PE 04/2025", float(d.loc[s26, 'v_hom'].sum()), "ex post"),
      (f"Idem: homologado PE 09/2026 × quantidade do ETP 2025", float((d.q * d.p_hom_2026)[s26].sum()), "ex post (mesmo comprador, +15 meses)")]
pd.DataFrame(T, columns=["indicador", "valor", "natureza"]).to_csv(os.path.join(RES, "expost_totais.csv"), index=False, encoding="utf-8")

# ------------------------------------------------------------------ teto CMED ex post
at = d[d.hom_acima_teto_agente].assign(excesso=lambda x: x.q * (x.p_hom - x.teto))
# mesma contagem com outros tetos, para medir a sensibilidade do indicador C4 à escolha do teto
itens_v2 = pd.read_parquet(os.path.join(V2, "organizacional", "itens_santa_luzia.parquet"))[["item", "teto_cmed_unitario_pb_max"]].rename(
    columns={"teto_cmed_unitario_pb_max": "teto_pacote_v2"})
d = d.merge(itens_v2, on="item", how="left")
for nome, col in (("pacote_v1_todos_vinculos", "teto_pacote_todos_vinculos"), ("pacote_v2_todos_vinculos", "teto_pacote_v2")):
    mm = d[col].notna() & (d.p_hom > d[col] + 0.005)
    N[f"itens_hom_acima_teto_{nome}"] = int(mm.sum())
    N[f"excesso_hom_sobre_teto_{nome}"] = float((d.q * (d.p_hom - d[col]))[mm].sum())
    N[f"itens_hom_acima_teto_{nome}_lista"] = d.loc[mm, "item"].tolist()
N["itens_com_teto_agente"] = int(d.teto.notna().sum())
N.update({"R0": R0, "R1": R1, "E1_central": E1c, "E1_baixo": E1b, "E1_alto": E1a, "homologado_total": HOM,
          "homologado_canetas": float(d.loc[caneta, "v_hom"].sum()), "homologado_sem_canetas": float(d.loc[~caneta, "v_hom"].sum()),
          "E1_central_sem_canetas": float(d.loc[~caneta, "v_ref"].sum()), "E1_baixo_sem_canetas": float(d.loc[~caneta, "valor_faixa_baixo"].sum()),
          "E1_alto_sem_canetas": float(d.loc[~caneta, "valor_faixa_alto"].sum()),
          "contrafactual_A": tot(pA), "contrafactual_B": tot(pB), "contrafactual_C": tot(pC),
          "itens_hom_acima_teto_agente": int(len(at)), "excesso_hom_sobre_teto": float(at.excesso.sum()),
          "excesso_hom_sobre_teto_canetas": float(at.loc[at.item.isin([196, 199]), "excesso"].sum()),
          "itens_hom_acima_teto_lista": at.item.tolist(),
          "itens_hom_igual_estimativa": int(d.hom_igual_estimativa.sum()), "valor_hom_igual_estimativa": float(d.loc[d.hom_igual_estimativa, "v_hom"].sum()),
          "itens_hom_dentro_faixa": int(d.hom_dentro_faixa.sum()), "itens_hom_abaixo_faixa": int(d.hom_abaixo_faixa.sum()),
          "itens_hom_acima_faixa": int(d.hom_acima_faixa.sum()), "valor_hom_acima_faixa": float(d.loc[d.hom_acima_faixa, "v_hom"].sum()),
          "valor_ref_alto_itens_acima_faixa": float(d.loc[d.hom_acima_faixa, "valor_faixa_alto"].sum()),
          "hom_sobre_ref_mediana": float(d.hom_sobre_ref.median()), "hom_sobre_ref_mediana_sem_canetas": float(d.loc[~caneta, "hom_sobre_ref"].median()),
          "hom_sobre_org_mediana": float(d.hom_sobre_org.median()),
          "itens_com_mediana_nacional": int(d.nac_ok.sum()), "ref_sobre_nac_mediana": float(d.ref_sobre_nac.median()),
          "org_sobre_nac_mediana": float(d.org_sobre_nac.median()), "hom_sobre_nac_mediana": float(d.hom_sobre_nac.median()),
          "pct_itens_ref_dentro_20pct_da_nac": float(100 * ((d.ref_sobre_nac - 1).abs() <= 0.2)[d.nac_ok].mean()),
          "pct_itens_org_dentro_20pct_da_nac": float(100 * ((d.org_sobre_nac - 1).abs() <= 0.2)[d.nac_ok].mean()),
          "pct_itens_nac_dentro_faixa_agente": float(100 * ((d.nac_med >= d.p_lo) & (d.nac_med <= d.p_hi))[d.nac_ok].mean()),
          "frac_mediana_registros_nac_ate_ref": float(d.nac_frac_ate_ref.median()), "frac_mediana_registros_nac_ate_alto": float(d.nac_frac_ate_alto.median()),
          "itens_nac_menos_de_10pct_ate_alto": int((d.nac_frac_ate_alto < 0.10).sum()),
          "itens_pe09_2026_casados": int(d.p_est_2026.notna().sum()), "itens_pe09_2026_homologados": int(s26.sum()),
          "hom2026_sobre_ref_mediana": float(d.hom2026_sobre_ref.median()), "hom2026_sobre_hom2025_mediana": float(d.hom2026_sobre_hom2025.median()),
          "proponentes_mediana": float(d.n_proponentes.median()), "itens_1_proponente": int((d.n_proponentes == 1).sum()),
          "valor_hom_itens_1_proponente": float(d.loc[d.n_proponentes == 1, "v_hom"].sum()),
          "hom_sobre_ref_mediana_1_proponente": float(d.loc[d.n_proponentes == 1, "hom_sobre_ref"].median()),
          "hom_sobre_ref_mediana_4mais_proponentes": float(d.loc[d.n_proponentes >= 4, "hom_sobre_ref"].median())})
# correlação competição × preço
cc = d[d.n_proponentes.notna()]
N["spearman_proponentes_vs_hom_sobre_ref"] = float(cc.n_proponentes.corr(cc.hom_sobre_ref, method="spearman"))

# ------------------------------------------------------------------ execução
ex = pd.read_parquet(os.path.join(EVAL, "organizacional", "execucao_contratos.parquet"))
ct = pd.read_parquet(os.path.join(EVAL, "organizacional", "contratos_pregoes_medicamentos.parquet"))
ex["pregao"] = ex.compra.map({"09090689000167-1-000006/2025": "PE 04/2025", "09090689000167-1-000099/2025": "PE 25/2025",
                              "09090689000167-1-000026/2026": "PE 09/2026"})
ex = ex.merge(ct[["numeroControlePNCP", "nomeRazaoSocialFornecedor", "numeroContratoEmpenho"]].rename(columns={"numeroControlePNCP": "contrato"}), on="contrato", how="left")
ex["empenhado_total"] = ex.empenhado_2025 + ex.empenhado_2026
ex["pct_empenhado_calc"] = np.where(ex.valor > 0, 100 * ex.empenhado_total / ex.valor, np.nan)
ex["pct_pago_calc"] = np.where(ex.valor > 0, 100 * ex.pago_total / ex.valor, np.nan)
ex.to_csv(os.path.join(RES, "expost_execucao_contratos.csv"), index=False, encoding="utf-8")
e4 = ex[ex.pregao == "PE 04/2025"]
c54 = e4[e4.forn == 31187918000115].iloc[0]
v54 = d[d.cnpj_fornecedor == 31187918000115]
N.update({"pe04_contratado": float(e4.valor.sum()), "pe04_empenhado_2025": float(e4.empenhado_2025.sum()), "pe04_empenhado_2026": float(e4.empenhado_2026.sum()),
          "pe04_empenhado_total": float(e4.empenhado_total.sum()), "pe04_pago_total": float(e4.pago_total.sum()),
          "pe04_pct_empenhado": float(100 * e4.empenhado_total.sum() / e4.valor.sum()), "pe04_pct_pago": float(100 * e4.pago_total.sum() / e4.valor.sum()),
          "contrato54_valor": float(c54.valor), "contrato54_empenhado": float(c54.empenhado_total), "contrato54_pago": float(c54.pago_total),
          "contrato54_itens": int(len(v54)), "contrato54_valor_canetas": float(v54.loc[v54.item.isin([196, 199]), "v_hom"].sum()),
          "contrato54_valor_sem_canetas": float(v54.loc[~v54.item.isin([196, 199]), "v_hom"].sum()),
          "pe04_sem_contrato54_contratado": float(e4[e4.forn != 31187918000115].valor.sum()),
          "pe04_sem_contrato54_empenhado": float(e4[e4.forn != 31187918000115].empenhado_total.sum())})
gl = pd.read_parquet(os.path.join(EVAL, "organizacional", "farmaco_por_licitacao_2025_2026.parquet"))
gl.to_csv(os.path.join(RES, "expost_gasto_por_licitacao.csv"), index=False, encoding="utf-8")
gm = pd.read_parquet(os.path.join(EVAL, "organizacional", "farmaco_mensal_2025_2026.parquet"))
gm.to_csv(os.path.join(RES, "expost_gasto_mensal.csv"), index=False, encoding="utf-8")
ga = pd.read_parquet(os.path.join(EVAL, "organizacional", "farmaco_anual_2025_2026.parquet"))
pe12 = gl[gl.licitacao.str.startswith("000122024")]
pe04 = gl[gl.licitacao.str.startswith("000042025")]
for ano in (2025, 2026):
    tot_ano = float(ga.loc[ga.ano == ano, "valor_empenhado"].iloc[0])
    N[f"gasto_{ano}_empenhado"] = tot_ano
    N[f"gasto_{ano}_pe12_2024_desconto_cmed"] = float(pe12.loc[pe12.ano == ano, "valor_empenhado"].sum())
    N[f"gasto_{ano}_pe04_2025"] = float(pe04.loc[pe04.ano == ano, "valor_empenhado"].sum())
    N[f"gasto_{ano}_pct_pe12"] = 100 * N[f"gasto_{ano}_pe12_2024_desconto_cmed"] / tot_ano
    N[f"gasto_{ano}_pct_pe04"] = 100 * N[f"gasto_{ano}_pe04_2025"] / tot_ano
N["gasto_2025_jan_abr"] = float(gm[(gm.ano == 2025) & gm.mes.str[:2].isin(["01", "02", "03", "04"])].valor_empenhado.sum())
N["gasto_2025_mai_dez_media_mensal"] = float(gm[(gm.ano == 2025) & ~gm.mes.str[:2].isin(["01", "02", "03", "04"])].valor_empenhado.mean())
N["gasto_12m_mar2025_fev2026"] = float(gm[((gm.ano == 2025) & (gm.mes.str[:2] >= "03")) | ((gm.ano == 2026) & (gm.mes.str[:2] <= "02"))].valor_empenhado.sum())

# ------------------------------------------------------------------ escopo
p25 = pd.read_parquet(os.path.join(EVAL, "organizacional", "pregao_25_2025_itens_resultados.parquet"))
p25["chave"] = p25.descricao.map(norm)
esc = [{"indicador": "PE 25/2025: itens", "valor": len(p25)},
       {"indicador": "PE 25/2025: itens que já estavam nos 334 do plano (mesma descrição normalizada)", "valor": int(p25.chave.isin(d.chave).sum())},
       {"indicador": "PE 25/2025: valor estimado", "valor": float(p25.valorTotal.sum())},
       {"indicador": "PE 25/2025: valor homologado", "valor": float((p25.valorUnitarioHomologado * p25.quantidadeHomologada).sum())},
       {"indicador": "PE 25/2025: data de inclusão", "valor": str(p25.dataInclusao.min())[:10]},
       {"indicador": "PE 09/2026: itens", "valor": len(p26)},
       {"indicador": "PE 09/2026: itens iguais aos do plano de 2025", "valor": int(p26.chave.isin(d.chave).sum())},
       {"indicador": "PE 09/2026: valor estimado", "valor": float(p26.valorTotal.sum())},
       {"indicador": "PE 09/2026: valor homologado", "valor": float((p26.valorUnitarioHomologado * p26.quantidadeHomologada).sum())},
       {"indicador": "PE 09/2026: itens homologados", "valor": int(p26.valorUnitarioHomologado.notna().sum())},
       {"indicador": "PE 09/2026: situação dos itens", "valor": json.dumps(p26.situacaoCompraItemNome.value_counts().to_dict(), ensure_ascii=False)},
       {"indicador": "PE 09/2026: data de inclusão", "valor": str(p26.dataInclusao.min())[:10]},
       {"indicador": "PE 09/2026: razão mediana quantidade 2026 / quantidade ETP 2025 (itens iguais)", "valor": float((d.q_2026 / d.q).median())},
       {"indicador": "PE 09/2026: razão mediana estimativa unitária 2026 / estimativa 2025 (itens iguais)", "valor": float((d.p_est_2026 / d.p_org).median())},
       {"indicador": "PE 09/2026: razão mediana estimativa unitária 2026 / referência do agente", "valor": float((d.p_est_2026 / d.p_ref).median())}]
pd.DataFrame(esc).to_csv(os.path.join(RES, "expost_escopo.csv"), index=False, encoding="utf-8")
N["pe25_itens"], N["pe25_valor_homologado"] = len(p25), esc[3]["valor"]

cols = ["item", "descricao", "unidade", "q", "grupo_fonte", "p_org", "p_ref", "p_lo", "p_hi", "teto", "teto_pacote_todos_vinculos", "p_hom", "cnpj_fornecedor",
        "v_ref", "v_hom", "hom_sobre_ref", "hom_sobre_org", "hom_igual_estimativa", "hom_dentro_faixa", "hom_abaixo_faixa", "hom_acima_faixa", "hom_acima_teto_agente",
        "n_proponentes", "n_propostas", "n_lances", "menor_valor_ofertado", "nac_n", "nac_ufs", "nac_p25", "nac_med", "nac_p75", "ne_n", "ne_med",
        "ref_sobre_nac", "org_sobre_nac", "hom_sobre_nac", "nac_frac_ate_ref", "nac_frac_ate_alto", "nac_frac_ate_hom",
        "p_est_2026", "p_hom_2026", "q_2026", "situacao_2026", "hom2026_sobre_ref", "hom2026_sobre_hom2025",
        "flag_a_conferir", "flag_acima_teto_confirmado", "flag_sem_referencia_externa", "flag_sem_teto_utilizavel", "flag_referencia_fraca"]
d[cols].to_csv(os.path.join(RES, "expost_itens.csv"), index=False, encoding="utf-8")
json.dump(N, open(os.path.join(RES, "expost_numeros.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30); pd.set_option("display.float_format", "{:,.2f}".format)
print(pd.DataFrame(T, columns=["indicador", "valor", "natureza"]).to_string(index=False, max_colwidth=95))
print(rg[["grupo", "itens", "v_ref_agente", "v_homologado", "hom_sobre_ref_mediana", "pct_hom_dentro_faixa", "pct_hom_acima_faixa",
          "itens_hom_igual_estimativa", "itens_com_mediana_nacional", "ref_sobre_nac_mediana", "org_sobre_nac_mediana", "hom_sobre_nac_mediana",
          "proponentes_mediana"]].to_string(index=False, max_colwidth=45))
for k, v_ in N.items():
    print(f"{k}: {v_:,.2f}" if isinstance(v_, float) else f"{k}: {v_}")
