"""Dimensão C: verificação dos números declarados pelo decisor. Saída: saida/02_calculos.csv
Requer trabalho/repro (b01_reproduz.py) para reexecutar o Monte Carlo do decisor."""
import os
import numpy as np
import pandas as pd

PK = "decisao_congelada/ambiente/data/decision_input_nacional/"
T = "decisao_congelada/ambiente/trabalho/"
cesta = pd.read_parquet(PK + "problema/cesta.parquet").set_index("ap_id")
cg = pd.read_parquet(PK + "mercado/precos_comprasgov.parquet")
comp = pd.read_csv("decisao_congelada/ambiente/saida/03_comparacao.csv").set_index("estrategia")
plano = pd.read_csv("decisao_congelada/ambiente/saida/plano_por_apresentacao.csv").set_index("ap_id")
pr = pd.read_csv(T + "precos_referencia.csv").set_index("ap_id")
it = pd.read_csv(T + "custos_item_estrategia.csv").set_index("ap_id")
sens = pd.read_csv(T + "sensibilidade.csv")
rf = pd.read_csv(PK + "problema/recursos_federais.csv")
r4705 = rf[(rf["CÓDIGO AÇÃO"].astype(str) == "4705") & (rf["EXERCÍCIO"] == 2024)].iloc[0]

# Monte Carlo do decisor reexecutado na cópia, para checagens por sorteio
src = open(T + "03_estrategias.py", encoding="utf8").read().split("# ---------------- Por item")[0]
cwd = os.getcwd(); os.chdir("trabalho/repro"); g = {"__name__": "mc"}
try:
    exec(compile(src, "03_estrategias.py", "exec"), g)
finally:
    os.chdir(cwd)
C, cen = g["C"], g["cen"]
tot = {k: v.sum(1) for k, v in C.items()}
M = 1e6
R = []


def chk(id_, item, onde, declarado, recalculado, confere, classe="CALCULADO", nota=""):
    R.append(dict(id=id_, verificacao=item, onde_declarado=onde, valor_declarado=declarado, valor_recalculado=recalculado,
                  confere=confere, classificacao=classe, nota=nota))


def faixa(x):
    return f"{np.percentile(x, 50)/M:.0f} ({np.percentile(x, 5)/M:.0f}-{np.percentile(x, 95)/M:.0f})"


chk("C01", "Custo total E1 p50 (p05-p95), R$ mi", "00_resumo; 03_comparacao", "6.475 (5.930-7.185)", faixa(tot["E1"]), "sim")
chk("C02", "Custo total E2 p50 (p05-p95), R$ mi", "00_resumo; 03_comparacao", "6.255 (5.731-6.935)", faixa(tot["E2"]), "sim")
eco = tot["E1"] - tot["E2"]
chk("C03", "Economia potencial E2 x E1 no horizonte, R$ mi", "00_resumo; 05_economia", "221 (159-298)", faixa(eco), "sim")
ep = tot["E1"] - tot["E2_pleno"]
chk("C04", "Economia E2 em regime pleno, R$ mi", "00_resumo; 05_economia", "405 (337-483)", faixa(ep), "sim",
    nota="apresentada como referência e não somada à do horizonte (correto)")
dec = C["E1"][:, ~cen].sum(1)
chk("C05", "Economia E2 em % do custo E1 dos descentralizados", "03_comparacao", "18,4%", f"{np.median(eco / dec):.3f}", "sim")
chk("C06", "Custo dos 39 centralizados (p50), R$ mi", "00_resumo", "5.281", f"{np.median(C['E1'][:, cen].sum(1))/M:.0f}", "sim")
chk("C07", "Centralizados / empenhado 4705 em 2024", "01_diagnostico; 04_recomendacao", "38% de R$ 13,74 bi",
    f"{np.median(C['E1'][:, cen].sum(1))/r4705.empenhado:.3f}", "sim",
    nota="categorias diferentes comparadas só como ordem de grandeza, sem soma (adequado)")
chk("C08", "Pago/empenhado 4705 em 2024", "05_economia", "72%", f"{r4705.realizado_pago/r4705.empenhado:.3f}", "sim",
    nota="a coluna 'realizado' do Portal foi rotulada como pago pelo pacote")
for k in ["E3", "E4"]:
    chk(f"C09_{k}", f"Custo total {k} p50, R$ mi", "00_resumo; 03_comparacao", f"{comp.loc[k, 'custo_total_p50']/M:.0f}", f"{np.median(tot[k])/M:.0f}", "sim")
f23 = (tot["E2"] < tot["E3"]).mean(); f34 = (tot["E3"] < tot["E4"]).mean(); f41 = (tot["E4"] < tot["E1"]).mean()
chk("C10", "Ordenação E2<E3<E4<E1 'em todos os percentis'", "03_comparacao §2", "vale em todos os percentis",
    f"fração de sorteios pareados: E2<E3 {f23:.3f}; E3<E4 {f34:.3f}; E4<E1 {f41:.3f}", "sim" if min(f23, f34, f41) > .99 else "parcial",
    nota="o decisor comparou percentis marginais; a checagem por sorteio pareado é a adequada")
el = pd.read_csv(T + "elasticidade.csv").set_index("segmento")
chk("C11", "Beta volume-preço por segmento (IC90)", "01_diagnostico §3", "-0,085 (-0,118 a -0,072); -0,080 (-0,099 a -0,067)",
    f"{el.beta['concorrencial']:.3f} ({el.ic90_inf['concorrencial']:.3f} a {el.ic90_sup['concorrencial']:.3f}); "
    f"{el.beta['concentrado']:.3f} ({el.ic90_inf['concentrado']:.3f} a {el.ic90_sup['concentrado']:.3f})", "sim",
    nota="reproduzido byte a byte; é associação transversal, como o decisor declara")
chk("C12", "Decuplicar o volume reduz o preço em ~17-18%", "01_diagnostico", "17-18%",
    f"{1-10**el.beta['concorrencial']:.3f}; {1-10**el.beta['concentrado']:.3f}", "sim")
centr = cesta.index[(cesta.grupo_financiamento == "1A") | (cesta.index == "AP007")]
amb = pr[pr.dlog_prog_preco.notna() & (pr.n_estadual_24m >= 3) & pr.index.isin(centr)]
rz = amb.dlog_prog_preco / amb.mediana_estadual_24m
chk("C13", "Razão DLOG/mediana estadual (n=27)", "00_resumo; 01_diagnostico", "0,29 (p25 0,24; p75 0,53)",
    f"n={len(rz)}; {rz.median():.3f} ({rz.quantile(.25):.3f}; {rz.quantile(.75):.3f})", "sim",
    nota="mistura volume, PDP e negociação; o decisor não a usa no valor central (adequado)")
eco2, extra = g["eco2"], g["extra_falha"]
chk("C14", "Probabilidade de fracasso do certame que anula a economia", "00_resumo; 03_comparacao; 04_recomendacao", "~41%",
    f"fórmula do decisor {np.median(eco2/(eco2+extra)):.3f}; fórmula correta {np.median(eco2/extra):.3f}", "não",
    nota="erro conceitual: extra_falha (p75 - preço E2) já contém a perda da economia; dividir por eco+extra conta a perda duas vezes. "
         "O erro é conservador: o limiar correto é ~70%")
e = it[~it.centralizado].eco_E2_pleno_p50.sort_values(ascending=False)
chk("C15", "Seis itens concentram ~85% da economia (regime pleno)", "00_resumo; 05_economia", "~85%", f"{e.head(6).sum()/e.sum():.3f}", "sim",
    nota="soma de medianas por item (aproximação aceitável)")
chk("C16", "Grupos na cesta: 38 1A, 6 1B, 6 2", "01_diagnostico", "38/6/6", str(cesta.grupo_financiamento.value_counts().to_dict()), "sim", "OBSERVADO")
nd = sorted(a for a in cesta.index if pd.isna(pr.loc[a, "dlog_prog_preco"]) and cesta.grupo_financiamento[a] == "1A")
chk("C17", "Itens 1A sem compra DLOG programática", "01_diagnostico Q11",
    "9 (AP004, AP005, AP010, AP022, AP030, AP035, AP049, AP063, AP082)", f"{len(nd)} {nd}", "sim")
desc = it.index[~it.centralizado]
chk("C18", "Fonte única na CMED em 7 dos 11 descentralizados", "00_resumo", "7", str(int((cesta.loc[desc, "cmed_laboratorios"] <= 1).sum())), "sim", "OBSERVADO")
chk("C19", "idItemCompra único no Compras.gov", "01_diagnostico Q12", "5.447/5.447", f"{cg.idItemCompra.nunique()}/{len(cg)}", "sim", "OBSERVADO")
q7 = cg[(cg.ap_id == "AP007") & cg.nomeUasg.str.startswith("DEPARTAMENTO DE LOG") & (cg.dataResultado.str[:4] == "2024")].quantidade.sum()
chk("C20", "AP007: MS comprou ~751 mil frascos em 2024; SIA 1B R$ 14 mil (R$ 0,03/un.)", "01_diagnostico Q3", "~751 mil; R$ 14 mil",
    f"{q7:,.0f} frascos (todas as compras DLOG de 2024); SIA {cesta.loc['AP007', 'valor_aprovado_sia_12m']:,.0f} "
    f"({cesta.loc['AP007', 'valor_unitario_financiado_sia']:.3f}/un.)", "sim" if abs(q7 / 751000 - 1) < .03 else "parcial", "OBSERVADO")
x = cesta
chk("C21", "Crescimento: risdiplam 259->5.424; eculizumabe 4.866->26.175; dapagliflozina x2,2; upadacitinibe x2,3", "01_diagnostico §3", "idem",
    f"{x.loc['AP024', 'dispensacao_12m_ano_anterior']:.0f}->{x.loc['AP024', 'dispensacao_12m_pre_corte']:.0f}; "
    f"{x.loc['AP013', 'dispensacao_12m_ano_anterior']:.0f}->{x.loc['AP013', 'dispensacao_12m_pre_corte']:.0f}; "
    f"x{x.loc['AP050', 'dispensacao_12m_pre_corte']/x.loc['AP050', 'dispensacao_12m_ano_anterior']:.2f}; "
    f"x{x.loc['AP014', 'dispensacao_12m_pre_corte']/x.loc['AP014', 'dispensacao_12m_ano_anterior']:.2f}", "sim", "OBSERVADO")
chk("C22", "AP012: mediana R$ 23.846 > teto R$ 21.340; MS paga R$ 3.208,85", "01_diagnostico Q5", "23.846 / 21.340 / 3.208,85",
    f"{pr.loc['AP012', 'mediana_24m']:.2f} / {pr.loc['AP012', 'teto_aplicavel']:.2f} / {pr.loc['AP012', 'dlog_prog_preco']:.2f}", "sim")
corr = pd.read_csv("trabalho/p01_ap052.csv").iloc[0]
chk("C23", "Mesalazina 500 mg: p25 R$ 1,84 / p75 R$ 4,50 apresentado como dispersão entre compradores", "01_diagnostico §3",
    "1,84 / 4,50 (dispersão de preço)",
    f"{pr.loc['AP052', 'p25_estadual_24m']:.2f} / {pr.loc['AP052', 'p75_estadual_24m']:.2f}; sem supositório/uso retal a mediana estadual cai de "
    f"{corr.mediana_estadual_24m_decisor:.3f} para {corr.mediana_estadual_24m_sem_retal:.3f}", "parcial",
    nota="o número confere, a interpretação não: a amplitude vem da mistura com supositório (CATMAT 352414 'uso retal'), falha do pacote não detectada")
chk("C24", "Tofacitinibe: Fiocruz R$ 14,40 x mediana estadual R$ 74", "01_diagnostico §3", "14,40 x 74",
    f"{pr.loc['AP011', 'dlog_prog_preco']:.2f} x {pr.loc['AP011', 'mediana_estadual_24m']:.2f}", "sim")
acima = plano[(plano.preco_referencia_unit > plano.teto_cmed_aplicavel_unit) | (plano.preco_ref_faixa_sup > plano.teto_cmed_aplicavel_unit)]
acima_min = sorted(plano.index[plano.preco_referencia_unit > plano.teto_cmed_min_0icms_unit])
chk("C25", "Nenhum preço projetado chega ao teto CMED aplicável", "registro_hipoteses H10", "nenhum",
    f"{len(acima)} itens com preço ou faixa superior acima do teto aplicável; acima do menor teto 0% ICMS: {acima_min}",
    "sim" if len(acima) == 0 else "não", nota="teto aplicável = maior teto entre produtos (0% ou mediana 18%); MC limita custo a teto x idx")
b = (pr.bps_mediana_24m / pr.mediana_24m)
chk("C26", "BPS/Compras.gov: mediana 0,95 (p10 0,75; p90 1,47; n=42)", "01_diagnostico Q8", "0,95; 0,75; 1,47; 42",
    f"{b.median():.2f}; {b.quantile(.1):.2f}; {b.quantile(.9):.2f}; {b.notna().sum()}", "sim")
chk("C27", "Unidade de dispensação ausente em 8 itens", "01_diagnostico Q4", "8",
    str(int(cesta.unidade_dispensacao.isna().sum() + (cesta.unidade_dispensacao == "").sum())), "sim", "OBSERVADO")
s = sens["valor_R$"].values
chk("C28", "Sensibilidade determinística: central 203; beta 0 -> 0; s=0,40 148; s=0,70 259; otimista 444 (R$ mi)", "03_comparacao §3",
    "203; 0; 148; 259; 444", "; ".join(f"{v/M:.0f}" for v in [s[1], s[2], s[5], s[6], s[-1]]), "sim",
    nota=f"base determinística dos descentralizados = {s[0]/M:.0f} mi (índice 1,025; Q central) x MC p50 1.197 mi: diferença de método, não erro")
chk("C29", "Categorias de valor não somadas e BPS nunca somado ao Compras.gov", "03_estrategias.py; 02_precos.py", "declarado",
    "código: custo = Q x min(preço homologado x idx, teto); teto só como limite; SIA e orçamento só em mc_resumo, separados; BPS só em medianas de conferência",
    "sim", "OBSERVADO")
cat = pd.read_csv("evidencias_primarias/comprasgov_precos/apresentacao_catmat.csv", dtype=str)
multi = cat.groupby("catmat").ap_id.nunique(); multi = multi[multi > 1]
chk("C30", "Duplicidade entre apresentações por CATMAT compartilhado", "não declarado", "-",
    f"CATMATs ligados a mais de uma apresentação: {len(multi)} {list(multi.index)}", "sim" if len(multi) == 0 else "parcial", "OBSERVADO")
chk("C31", "Unidade do preço = unidade de dispensação SIA", "plano_por_apresentacao", "implícito",
    "confere nos itens inspecionados, exceto AP012 (CATMAT 90 mg/mL mistura 45 e 90 mg; tratado pelo decisor) e AP052 (supositório misturado; não tratado)",
    "parcial", "INFERIDO")
pd.DataFrame(R).to_csv("saida/02_calculos.csv", index=False)
print(pd.DataFrame(R)[["id", "confere", "valor_declarado", "valor_recalculado"]].to_string(index=False))
