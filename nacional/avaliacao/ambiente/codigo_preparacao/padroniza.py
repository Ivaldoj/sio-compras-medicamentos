"""Etapa 3 — funções de padronização de medicamentos (texto do edital/PNCP, CATMAT do BPS, apresentação CMED)
e regras de comparação/conversão. Módulo importado pelos scripts 25+ (inclua scripts/ no sys.path).
Rodar `python -I -X utf8 padroniza.py` executa os autotestes.

Regras (documentadas em docs/13):
- princípio ativo: tokens alfabéticos (>=4 letras) normalizados, sem sais/radicais e palavras de forma/uso;
- concentração: pares (valor, unidade normalizada) — mg, g, mcg, ui, meq, %, com denominador opcional (/ml, /g);
- forma: categoria canônica + modificadores (lib_prol, orodisp, mast, subl, vag, efev, oft);
- conteúdo do recipiente: último volume/massa (ml, g) para itens de frasco/ampola/bisnaga/seringa/unidade;
- embalagem CMED: nº de recipientes/unidades por embalagem e volume/massa por recipiente.
Nenhuma conversão é feita quando qualquer atributo é desconhecido ou diverge."""
import re, unicodedata

SAIS = set("""cloridrato dicloridrato sodico sodica potassico potassica calcico calcica magnesico maleato acetato acetonato succinato
hemitartarato hemifumarato tartarato bitartarato besilato mesilato fumarato citrato fosfato dissodico dissodica monoidratado monoidratada
diidratado diidratada dihidratado hidratado hidratada trihidratado trihidratada sesqui sesquiidratado oxalato bromidrato
hidrobrometo potassio valerato propionato dipropionato furoato sulfato carbonato cloreto gluconato lactato nitrato estearato palmitato
decanoato enantato cipionato hiclato monoidrato hemi hemiidratado anidro anidra base equivalente""".split())
OUTRAS = set("""adulto adultos pediatrico pediatrica infantil mastigavel comprimido comprimidos capsula capsulas drageas dragea
solucao suspensao injetavel injetaveis oral orais xarope creme pomada gotas frasco ampola ampolas bisnaga liberacao prolongada
retard revestido revestida orodispersivel sublingual vaginal uso topico dermatologico dermatologica intravenosa intramuscular
subcutanea sistema aplicacao com sem para dose doses unidade unidades envelope sache seringa preenchida colirio oftalmica
oftalmico spray nasal aerossol efervescente diluente frascoampola equivalente composto composta associado associada acao rapida
lenta ultra analoga analogo humana humano tubo fechado bolsa""".split())
OUTRAS -= {"humana"}  # "insulina humana" é princípio ativo na CMED

FORMAS = [  # (regex no texto normalizado, categoria) — ordem importa
    (r"po (liof|para|p/)?.{0,12}(sus|suspensao) or|po para suspensao oral|po p sus or|po sus or", "po_suspensao_oral"),
    (r"po (liof )?(inj|para solucao inj|p/ sol inj|p/ solucao inj)|po liof|po injet|po para solucao injetavel|liofilizado", "po_injetavel"),
    (r"sus inj|suspensao injet", "suspensao_injetavel"),
    (r"sol inj|solucao injet|emul inj|emulsao injet", "solucao_injetavel"),
    (r"injetavel|\binj\b", "injetavel"),  # genérico (catálogo): compatível com solução, suspensão ou pó injetável
    (r"sol oft|colirio|oftalm", "colirio"),
    (r"sus or|suspensao oral|susp\.? oral|susp or", "suspensao_oral"),
    (r"\bxpe\b|xarope", "xarope"),
    (r"sol or|solucao oral|gotas|\bgot\b|elixir|\belx\b", "solucao_oral"),
    (r"crem|creme", "creme"), (r"\bpom\b|pomada", "pomada"), (r"\bgel\b", "gel"), (r"locao|\bloc\b", "locao"),
    (r"\bsup\b|supositorio", "supositorio"), (r"aer|spray|\bspr\b", "spray"),
    (r"cap dura|cap mole|\bcap\b|capsula|caps\b", "capsula"),
    (r"\bcom\b|\bcm\b|comprimido|\bcomp\b|\bdrg\b|dragea", "comprimido"),  # "CM" aparece em algumas apresentações CMED
]
MODIF = [(r"70\s*n?\s*/\s*30|bifasic|mistura|\bmix\b", "mistura"),
         (r"sistema de aplica|sist aplic|caneta|flexpen|kwikpen|solostar|\bcan\b", "sist_aplic"),
         (r"lib prol|lib retard|lib mod|lib contr|liberacao prolongada|liberacao modificada|liberacao controlada|retard|\bxr\b|\bcr\b|\bsr\b", "lib_prol"), (r"orodisp", "orodisp"),
         (r"mast", "mast"), (r"subl", "subl"), (r"vag", "vag"), (r"efev|efervesc", "efev")]
UNID_SOLIDA = {"comprimido", "capsula", "drageas", "dragea", "cps/comp", "cápsula"}


INJ = {"solucao_injetavel", "suspensao_injetavel", "po_injetavel", "injetavel"}


def forma_compativel(a, b, ambos_solidos=False):
    """Mesma categoria; 'injetavel' genérico casa com qualquer injetável; sólidos casam entre si se o texto aceitar os dois
    ('cáps./comp.') ou se um lado for 'solido' (catálogo comprado como comprimido e cápsula)."""
    if a == b:
        return True
    if "injetavel" in (a, b) and {a, b} <= INJ:
        return True
    if {a, b} == {"suspensao_oral", "po_suspensao_oral"}:
        return True  # concentração do catálogo se refere à suspensão reconstituída
    sol = {"comprimido", "capsula"}
    return ({a, b} <= sol and ambos_solidos) or ("solido" in (a, b) and {a, b} - {"solido"} <= sol)


def norm(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", s).strip()


def num(t):
    """'25.000' -> 25000 ; '0,5' -> 0.5 ; '1.250' -> 1250 ; '2.5' -> 2.5"""
    t = t.strip()
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", t):
        return float(t.replace(".", ""))
    return float(t.replace(".", "").replace(",", ".")) if "," in t else float(t)


SINONIMOS = {"benzerazida": "benserazida"}  # grafia do edital × grafia do catálogo/CMED


def principio(texto):
    """Conjunto de tokens do(s) princípio(s) ativo(s). Para texto de item, usa o trecho antes do 1º número."""
    t = re.sub(r"\([^)]*\)", " ", norm(texto))  # sinônimos entre parênteses: "(vitamina d3)", "(noradrenalina)"
    t = re.split(r"\d", t, maxsplit=1)[0]
    toks = {w for w in re.findall(r"[a-z]{4,}", t)} - OUTRAS
    toks = {SINONIMOS.get(w, w) for w in toks}
    sem_sal = toks - SAIS
    return frozenset(sem_sal or toks)


def principio_catmat(pdm, descricao):
    """Princípio do catálogo: nome do item (1º segmento da descrição; o PDM às vezes é genérico, ex.: PDM "VITAMINA D" e
    item "COLECALCIFEROL, ...") + valores de 'ORIGEM:'/'TIPO:' + associações ('COMPOSIÇÃO:'/'PRINCÍPIO ATIVO: ASSOCIADA COM ...')."""
    d = norm(descricao)
    nome = re.split(r",|\s[a-z]+\s*:", d)[0].strip() or norm(pdm)
    extra = " ".join(re.findall(r"(?:origem|tipo)\s*:\s*([a-z ]+)", d))
    extra += " " + " ".join(re.findall(r"(?:composicao|principio ativo)\s*:\s*associad[oa]s?\s*(?:a|ao|as|com)?\s*([a-z +]+)", d))
    return principio(f"{nome} {extra}")


RX_CONC = re.compile(r"(\d+(?:[.,]\d+)*)\s*(mg|mcg|ug|g|ui|u\b|meq|%)\s*(?:/\s*(ml|g|dose|gota))?", re.I)


def concentracoes(texto):
    """Conjunto de (valor, unidade[/denominador]); massas normalizadas para mg (1 g = 1000 mg; 1 mcg = 0,001 mg).
    Massa em 'g' sem denominador só conta como concentração se não houver outra (ex.: 'ceftriaxona 1 g');
    caso contrário é conteúdo do recipiente (ex.: 'creme 50 mg/g ... 10 g')."""
    out, gramas = set(), set()
    t = norm(texto)
    # "100+25mg" -> "100mg+25mg" (o 1º valor herda a unidade do 2º)
    t = re.sub(r"(\d+(?:[.,]\d+)?)\s*\+\s*(\d+(?:[.,]\d+)?)\s*(mg|mcg|g|ui)\b", r"\1\3+\2\3", t)
    # "50 mg + 12,5 mg/ml" -> "50 mg/ml + 12,5 mg/ml" (o denominador vale para a soma, notação usual de associações líquidas)
    t = re.sub(r"(\d+(?:[.,]\d+)?)\s*(mg|mcg|ui)\s*\+\s*(\d+(?:[.,]\d+)?)\s*\2\s*/\s*(ml|g)\b", r"\1\2/\4 + \3\2/\4", t)
    t = re.sub(r"(\d+(?:[.,]\d+)*)\s*(mg|ui|mcg)\s*/\s*(\d+(?:[.,]\d+)?)\s*ml\b",
               lambda m: f"{num(m.group(1)) / num(m.group(3)):g}{m.group(2)}/ml", t)
    for v, u, d in RX_CONC.findall(t):
        u = {"ug": "mcg", "u": "ui"}.get(u.lower(), u.lower())
        x = num(v)
        if u == "g" and not d:
            gramas.add((x * 1000, "mg")); continue
        if u == "g":
            x, u = x * 1000, "mg"
        elif u == "mcg":
            x, u = round(x / 1000, 6), "mg"
        out.add((x, u + ("/" + d.lower() if d else "")))
    return frozenset(out or gramas)


def forma(texto):
    t = norm(texto)
    cat = next((c for rx, c in FORMAS if re.search(rx, t)), None)
    mods = frozenset(m for rx, m in MODIF if re.search(rx, t))
    return cat, mods


def conteudo_item(texto):
    """Último volume (ml) ou massa (g) do texto do item, ex.: '(frasco 120ml)' -> (120,'ml'); '10g' -> (10,'g')."""
    ach = re.findall(r"(\d+(?:[.,]\d+)?)\s*(ml|g)\b(?!\s*/)", norm(texto))
    ach = [(num(v), u) for v, u in ach]
    return ach[-1] if ach else None


RX_REC = r"(fa|amp|fr|bg|ser|car|tb|env|sach|bl|blt|str|est|bisn|bolsa|fle|cpr)"


def embalagem_cmed(apres):
    """Da APRESENTAÇÃO CMED extrai: recipientes por embalagem, volume/massa por recipiente, unidades sólidas por embalagem
    e se a embalagem é composta (kit com diluente, '+' etc.). Valores None quando não determináveis."""
    t = norm(apres)
    # composta = outro recipiente/medicamento no kit (diluente, 2º frasco); acessórios (copo, seringa dosadora, aplicador) não contam
    comp = bool(re.search(r"\+\s*(\d+\s*)?(dil|fa|amp|fr|bolsa)\b", t)) or "kit" in t
    # parte após a forma: tudo depois do primeiro 'ct'/'cx'/'fr'/'bl'
    m = re.search(r"\b(ct|cx|emb|fr|bl|fa|amp|bg)\b.*", t)
    pac = m.group(0) if m else ""
    q = r"(?:(?:c/|est|disp|envol|envolt|cama)\s*)?"  # "CT EST 50 AMP", "CX C/ 25 AMP", "CT DISP 10 BL"
    rec = re.search(r"\b(ct|cx)\s+" + q + r"(\d+)\s+" + RX_REC, pac)
    n_rec = int(rec.group(2)) if rec else (1 if re.search(r"\b" + RX_REC + r"\b", pac) else None)
    vol = re.search(r"\bx\s*(\d+(?:[.,]\d+)?)\s*(ml|g|l)\b", pac)
    vol = (num(vol.group(1)) * (1000 if vol.group(2) == "l" else 1), "ml" if vol.group(2) == "l" else vol.group(2)) if vol else None
    sol = None
    if not vol:
        xs = re.findall(r"\bx\s*(\d+)\b(?!\s*(ml|g|mg))", pac)
        bl = re.search(r"\b(ct|cx)\s+" + q + r"(\d+)\s+(bl|blt|str|env)\b", pac)
        # >100 unidades "por blister" com multiplicador de blisters é fisicamente implausível ("CX 50 BL X 350"): ambíguo
        if xs and not (bl and int(xs[-1][0]) > 100):
            sol = int(xs[-1][0]) * (int(bl.group(2)) if bl else 1)
    return {"recipientes": n_rec, "volume": vol, "unidades_solidas": sol, "composta": comp}


def nivel_catmat(item_desc, item_unid, cat_c, cat_fm):
    """Item × CATMAT com o mesmo princípio: 'atributos_compativeis' (concentração, forma e modificadores iguais),
    'parcial_forma_indeterminada' (forma não extraída de um dos lados) ou None (incompatível)."""
    c = concentracoes(item_desc)
    if not c or not cat_c or c != cat_c:
        return None
    f, m = forma(item_desc + " " + item_unid)
    fx, mx = cat_fm
    if f and fx and forma_compativel(f, fx, "caps" in norm(item_desc) and "comp" in norm(item_desc)) and m == mx:
        return "atributos_compativeis"
    if not f or not fx:
        return "parcial_forma_indeterminada"
    return None


def mesmo_medicamento(da, ua, db, ub):
    """Item comparável no nível da unidade: princípio, concentração, forma/modificadores iguais e, para líquidos/semissólidos,
    mesmo conteúdo do recipiente. Sólidos 'cáps./comp.' aceitam as duas formas."""
    if principio(da) != principio(db) or not concentracoes(da) or concentracoes(da) != concentracoes(db):
        return False
    (fa, ma), (fb, mb) = forma(da), forma(db)
    fa = fa or forma(ua)[0]; fb = fb or forma(ub)[0]
    amb = any("caps" in norm(x) and "comp" in norm(x) for x in (da, db))
    if not fa or not fb or ma != mb or not forma_compativel(fa, fb, amb):
        return False
    if fa in ("comprimido", "capsula"):
        return True
    ca, cb = conteudo_item(da), conteudo_item(db)
    return ca is not None and ca == cb


ORDEM = ["exata", "compativel_conversao", "provavel_conferencia", "indeterminada", "incompativel"]


def compara(item_desc, item_unid, cmed_subst, cmed_apres):
    """Classifica o par item × apresentação CMED. Devolve dict com classe, fator, unidade_destino e motivos."""
    mot = []
    pi, pc = principio(item_desc), principio(cmed_subst)
    # a CMED não grava o tipo "regular" no nome da substância (insulina regular = solução; NPH = suspensão): a forma decide
    if not pi or (pi != pc and not (pc < pi and pi - pc <= {"regular"})):
        return {"classe": "incompativel", "fator": None, "motivos": ["princípio ativo difere"]}
    ci, cc = concentracoes(item_desc), concentracoes(cmed_apres.split(" ct ")[0] if " ct " in norm(cmed_apres) else cmed_apres)
    st = "ok"
    if not ci or not cc:
        st = "indet"; mot.append("concentração não extraída")
    elif ci != cc:
        vi, vc = {v for v, _ in ci}, {v for v, _ in cc}
        if vi == vc:
            st = "prov"; mot.append("mesmos valores de concentração com unidades/denominadores diferentes")
        else:
            return {"classe": "incompativel", "fator": None, "motivos": ["concentração difere"]}
    # forma do item: descrição primeiro; a unidade do PNCP só supre ausência (há itens "Cápsula" com unidade "Comprimido")
    fi, mi = forma(item_desc)
    if not fi:
        fi, mi2 = forma(item_unid); mi = mi | mi2
    fc, mc = forma(cmed_apres)
    nd = norm(item_desc)
    ambos = "caps" in nd and "comp" in nd  # itens "cáps./comprimido" aceitam as duas formas sólidas
    if not fi or not fc:
        st = "indet" if st != "indet" else st; mot.append("forma farmacêutica não extraída")
    elif (fi != fc and not (ambos and {fi, fc} <= {"comprimido", "capsula"})) or mi != mc:
        return {"classe": "incompativel", "fator": None, "motivos": [f"forma difere ({fi}{sorted(mi)} × {fc}{sorted(mc)})"]}
    e = embalagem_cmed(cmed_apres)
    u = norm(item_unid)
    fator, ok_emb = None, "indet"
    if fi in ("comprimido", "capsula") or u in UNID_SOLIDA:
        if e["unidades_solidas"]:
            fator, ok_emb = e["unidades_solidas"], "ok"
        else:
            mot.append("nº de unidades por embalagem não extraído")
    else:
        vi = conteudo_item(item_desc)
        if not vi or not e["volume"]:
            mot.append("volume/massa do recipiente não extraído")
        elif vi != e["volume"]:
            return {"classe": "incompativel", "fator": None, "motivos": [f"conteúdo do recipiente difere ({vi[0]:g} {vi[1]} × {e['volume'][0]:g} {e['volume'][1]})"]}
        elif e["recipientes"]:
            fator, ok_emb = e["recipientes"], "ok"
        else:
            mot.append("nº de recipientes por embalagem não extraído")
    if fc == "comprimido" and re.search(r"\bcom rev\b", norm(cmed_apres)) and "revest" not in nd:
        mot.append("revestimento não especificado no item (regra: revestimento não impede compatibilidade)")
    if e["composta"] and ok_emb == "ok":
        mot.append("embalagem composta (kit com diluente/outro recipiente)"); ok_emb = "prov"
    if st == "indet" or ok_emb == "indet" and not mot:
        classe = "indeterminada"
    elif st == "ok" and ok_emb == "ok" and not any(m.startswith("embalagem composta") for m in mot):
        classe = "exata" if fator == 1 else "compativel_conversao"
    elif st == "indet":
        classe = "indeterminada"
    else:
        classe = "provavel_conferencia"
    return {"classe": classe, "fator": fator, "motivos": mot}


if __name__ == "__main__":  # autotestes com casos reais do caso Santa Luzia e da CMED jan/2025
    assert principio("Insulina Humana NPH 100UI/mL- suspensão injetável") == principio("INSULINA HUMANA")
    assert principio("Magnésio, Sulfato - solução injetável 50%") == principio("SULFATO DE MAGNÉSIO")
    assert principio("Sulfametoxazol+trimetoprima 40mg+8mg/ml") == principio("SULFAMETOXAZOL;TRIMETOPRIMA")
    assert concentracoes("Nistatina 25.000ui creme vaginal 50g") == {(25000.0, "ui")}
    assert concentracoes("Aciclovir 50mg/g (5%) 10g Creme") == {(50.0, "mg/g"), (5.0, "%")}
    assert concentracoes("CEFTRIAXONA 1g pó liofílico para solução injetável") == concentracoes("CEFTRIAXONA, CONCENTRAÇÃO: 1000 MG") == {(1000.0, "mg")}
    assert concentracoes("Cianocobalamina 500 mcg") == {(0.5, "mg")}
    assert conteudo_item("Acetilcisteina pediatrico 20mg/ml xarope (frasco 120ml)") == (120.0, "ml")
    assert embalagem_cmed("5 MG COM CT BL AL PLAS TRANS X 30")["unidades_solidas"] == 30
    assert embalagem_cmed("10 MG COM CT 3 BL AL PLAS TRANS X 10")["unidades_solidas"] == 30
    assert embalagem_cmed("100 MG/ML SOL INJ/DIL INFUS IV CT 10 FA VD TRANS X 2 ML") == {"recipientes": 10, "volume": (2.0, "ml"), "unidades_solidas": None, "composta": False}
    # bloqueios exigidos: volumes diferentes nunca convertem
    r = compara("Insulina Humana NPH 100UI/mL- suspensão injetável  3 mL com sistema de aplicação", "Unidade", "INSULINA HUMANA", "100 UI/ML SUS INJ CT FA VD TRANS X 10 ML")
    assert r["classe"] == "incompativel", r
    r = compara("Amoxicilina 50 mg/ml - Pó para suspensão Oral 60mL", "Frasco", "AMOXICILINA TRI-HIDRATADA", "50 MG/ML PO SUS OR CT FR PLAS OPC X 150 ML  + COP")
    assert r["classe"] == "incompativel", r
    r = compara("Amoxicilina 50 mg/ml - Pó para suspensão Oral 60mL", "Frasco", "AMOXICILINA TRI-HIDRATADA", "50 MG/ML PO SUS OR CT FR PLAS OPC X 60 ML")
    assert r["classe"] == "exata", r
    r = compara("Ramipril 5mg - comprimido", "Comprimido", "RAMIPRIL", "5 MG COM CT BL AL AL X 30")
    assert r["classe"] == "compativel_conversao" and r["fator"] == 30, r
    r = compara("Bupropiona 150mg comprimido de liberação prolongada - comprimido", "Comprimido", "CLORIDRATO DE BUPROPIONA", "150 MG COM REV CT BL AL PLAS X 30")
    assert r["classe"] == "incompativel", r  # liberação prolongada × comum
    assert principio_catmat("INSULINA", "INSULINA, ORIGEM: HUMANA, TIPO: REGULAR, DOSAGEM: 100U/ML") == principio("Insulina Humana Regular 100UI/mL")
    assert principio_catmat("INSULINA", "INSULINA, ORIGEM: HUMANA, TIPO: NPH, DOSAGEM: 100U/ML") == principio("Insulina Humana NPH 100UI/mL")
    assert principio("Colecalciferol (Vitamina D3) 1000 Ui") == principio("COLECALCIFEROL")
    assert concentracoes("Levodopa + benzerazida BD 100+25mg") == {(100.0, "mg"), (25.0, "mg")}
    assert forma_compativel("injetavel", "po_injetavel") and not forma_compativel("comprimido", "capsula")
    assert compara("Insulina Humana Regular 100UI/mL - solução injetável 3 mL com sistema de aplicação", "Unidade", "INSULINA HUMANA", "100 UI/ML SOL INJ CT 1 CAR VD TRANS X 3 ML X 1 SIST APLIC PLAS (FLEXPEN)")["classe"] == "exata"
    assert compara("Insulina Humana Regular 100UI/mL - solução injetável 3 mL com sistema de aplicação", "Unidade", "INSULINA HUMANA", "100 UI/ML SUS INJ CT 1 CAR VD TRANS X 3 ML X 1 SIST APLIC PLAS (FLEXPEN)")["classe"] == "incompativel"
    assert principio_catmat("LEVODOPA", "LEVODOPA, COMPOSIÇÃO: ASSOCIADO À BENSERAZIDA, DOSAGEM: 100MG + 25MG") == principio("Levodopa + benzerazida BD 100+25mg")
    assert concentracoes("Enoxaparina Sódica 60 mg/0,6 mL solução injetável") == concentracoes("ENOXAPARINA, CONCENTRAÇÃO: 100 MG/ML") == {(100.0, "mg/ml")}
    assert forma("CEFTRIAXONA SÓDICA, CONCENTRAÇÃO: 1 G, FORMA FARMACEUTICA: PÓ P/ SOLUÇÃO INJETÁVEL")[0] == "po_injetavel"
    i196 = "Insulina Humana NPH 100UI/mL- suspensão injetável  3 mL com sistema de aplicação"
    assert compara(i196, "Unidade", "INSULINA HUMANA", "100 UI/ML SUS INJ CT 2 CARP VD INC X 3 ML")["classe"] == "incompativel"  # refil sem caneta
    assert compara(i196, "Unidade", "INSULINA HUMANA", "100 UI/ML SUS INJ CT 1 CAR VD TRANS X 3 ML X 1 SIST APLIC PLAS (FLEXPEN)")["classe"] == "exata"
    assert compara(i196.replace("NPH", "NPH 70/30"), "Unidade", "INSULINA HUMANA", "100 UI/ML SUS INJ CT 1 CAR VD TRANS X 3 ML X 1 SIST APLIC PLAS (FLEXPEN)")["classe"] == "incompativel"
    assert compara("Acido Valproico 250mg caps./comprimido.", "Cáps/comp", "ÁCIDO VALPROICO", "250 MG CAP MOLE CT BL AL PLAS X 25")["classe"] == "compativel_conversao"
    r = compara("Ramipril 5mg - comprimido", "Comprimido", "RAMIPRIL", "10 MG COM CT BL AL AL X 30")
    assert r["classe"] == "incompativel", r
    # pré-Etapa 4: defeitos achados na verificação das conversões e na identificação pelo catálogo
    assert embalagem_cmed("500 MG/ML SOL INJ CT EST 50 AMP VD AMB X 2 ML")["recipientes"] == 50
    assert embalagem_cmed("2 MG/ML SOL INJ CX C/ 25 AMP VD TRANS X 10 ML")["recipientes"] == 25
    assert embalagem_cmed("500MG COM CT DISP 10 BL AL PLAS TRANS X 10")["unidades_solidas"] == 100
    assert embalagem_cmed("500 MG CAP DURA CX 50 BL AL PLAS TRANS X 350")["unidades_solidas"] is None
    assert embalagem_cmed("40 MG COM CX 25 BL AL PLAS LAR X 20")["unidades_solidas"] == 500
    assert principio("Hemifumarato de Quetiapina 25mg - comprimido") == principio_catmat("QUETIAPINA", "QUETIAPINA, DOSAGEM: 25 MG")
    assert principio_catmat("VITAMINA D", "COLECALCIFEROL, CONCENTRAÇÃO: 2.000 UI") == principio("Colecalciferol (Vitamina D3) 2000 Ui")
    assert principio_catmat("AMOXICILINA", "AMOXICILINA, PRINCÍPIO ATIVO: ASSOCIADA COM CLAVULANATO DE POTÁSSIO, CONCENTRAÇÃO: 500MG + 125MG") == principio("Amoxicilina + clavulanato de potássio 500 mg + 125 mg")
    assert principio_catmat("ESTRADIOL", "ESTRADIOL APRESENTAÇÃO: TRATAMENTO HORMONAL") == principio("ESTRADIOL")
    assert nivel_catmat("Ramipril 5mg - comprimido", "Comprimido", concentracoes("RAMIPRIL, DOSAGEM: 5 MG"), (None, frozenset())) == "parcial_forma_indeterminada"
    assert nivel_catmat("Ramipril 5mg - comprimido", "Comprimido", concentracoes("RAMIPRIL, DOSAGEM: 10 MG"), (None, frozenset())) is None
    assert mesmo_medicamento("INSULINA HUMANA NPH 100 UI/ML INJETAVEL CANETA 3ML", "UNIDADE", i196, "Unidade")
    assert not mesmo_medicamento("INSULINA HUMANA NPH 100UI/ML REFIL 3ML", "UNIDADE", i196, "Unidade")
    assert embalagem_cmed("2 MG/ML SOL INJ CX C/5 AMP VD TRANS X 10 ML")["recipientes"] == 5
    assert compara("Paroxetina 12,5mg comprimido", "Comprimido", "CLORIDRATO DE PAROXETINA", "12,5 MG COM LIB MOD CT BL AL PLAS X 30")["classe"] == "incompativel"
    assert concentracoes("Amoxicilina + clavulanato de potássio 50 mg + 12,5 mg/ml - Susp. Oral 75mL") == concentracoes("CONCENTRAÇÃO: 50 MG/ML + 12,5 MG/ML") == {(50.0, "mg/ml"), (12.5, "mg/ml")}
    print("autotestes ok")
