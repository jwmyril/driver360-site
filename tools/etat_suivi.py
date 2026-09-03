# -*- coding: utf-8 -*-
"""L'état réel des recommandations Driver360, recalculé — pas relu.

    python tools/etat_suivi.py          l'état de tout le registre
    python tools/etat_suivi.py --ouvert seulement ce qui reste à faire

POURQUOI CE FICHIER EXISTE
--------------------------
Un registre tenu à la main dit ce qu'on croyait le jour où on l'a écrit.
Suite 360 en a fait la démonstration : le sien annonçait 82 corrections « à
faire » alors qu'une bonne partie était faite depuis des semaines. Personne ne
ment — c'est la mémoire qui dérive, et un registre qu'on ne mesure pas devient
en quelques jours un document de fiction que plus personne n'ose ouvrir.

Un état déclaré dérive. Un état MESURÉ ne dérive pas.

Ce script relance donc les contrôles qui peuvent trancher, et compare leur
verdict à ce que `docs/SUIVI_RECOMMANDATIONS.md` déclare. Si les deux
divergent, **c'est le registre qui a tort**, et il sort en erreur pour le dire.

CE QU'IL NE FAIT PAS. Il ne juge pas les lignes marquées « humain » — une
relecture en kreyòl, un avis d'avocat, un arbitrage éditorial. Il les compte
et les nomme, pour qu'elles ne se perdent pas dans le tas de ce qui est fait.
Il ne corrige rien non plus : il mesure.

LA LEÇON QUI L'A FAIT NAÎTRE. La relecture du 30/08/2026 a trouvé quatre
contrôles verts qui mesuraient moins que ce qu'ils annonçaient :
`verif_ids_traduits.py` lisait un autre dépôt, `appliquer_theme.py --verifier`
comptait une page sans thème parmi ses « 9 pages », `verif_contraste.py` ne
pouvait pas voir un jeton inexistant, et `regen.py` sortait en 0 quand la copie
échouait. Un contrôle qui passe au vert sur un périmètre plus étroit que ce
qu'il annonce est plus dangereux qu'un contrôle absent : il autorise à ne pas
regarder. Les mesures ci-dessous nomment donc toujours CE QU'ELLES ONT
REGARDÉ, pas seulement leur verdict.
"""
import io
import json
import os
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                            # noqa: BLE001
    pass

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
REGISTRE = os.path.join(RACINE, "docs", "SUIVI_RECOMMANDATIONS.md")

PAGES = ["index.html", "jobs.html", "vivye.html", "anplwaye.html",
         "wout.html", "setdi.html", "terms.html", "privacy.html"]
TOUTES = PAGES + ["404.html"]


# ------------------------------------------------------------- les outils
def lire(rel):
    """Le contenu d'un fichier du dépôt, ou None s'il n'existe pas."""
    p = os.path.join(RACINE, rel)
    if not os.path.exists(p):
        return None
    return io.open(p, encoding="utf-8", errors="replace").read()


def compter(motif, fichiers, drapeaux=0, filtre=None):
    """(nombre total, pages touchées) pour un motif d'expression régulière.

    `filtre` retire du texte ce qui ne doit pas compter — un commentaire, une
    clé de stockage. C'est ce qui sépare une sentinelle utile d'une sentinelle
    qui hurle sur du code correct jusqu'à ce qu'on cesse de l'écouter.
    """
    rx = re.compile(motif, drapeaux)
    n, ou = 0, []
    for f in fichiers:
        t = lire(f)
        if t is None:
            continue
        if filtre:
            t = filtre(t)
        k = len(rx.findall(t))
        if k:
            n += k
            ou.append("%s×%d" % (f, k))
    return n, ou


def zero(motif, fichiers, quoi, drapeaux=0, filtre=None):
    """Vrai quand le motif a disparu partout. Rend (verdict, détail)."""
    n, ou = compter(motif, fichiers, drapeaux, filtre)
    if n == 0:
        return True, "aucune occurrence de %s" % quoi
    return False, "%d %s : %s" % (n, quoi, " ".join(ou[:6]))


def partout(motif, fichiers, quoi, drapeaux=0):
    """Vrai quand CHAQUE fichier porte le motif au moins une fois."""
    rx = re.compile(motif, drapeaux)
    absents = []
    for f in fichiers:
        t = lire(f)
        if t is None:
            absents.append(f + " (absent)")
        elif not rx.search(t):
            absents.append(f)
    if not absents:
        return True, "%s sur les %d pages" % (quoi, len(fichiers))
    return False, "%s manque sur %d page(s) : %s" % (quoi, len(absents),
                                                     " ".join(absents))


# ------------------------------------------------------- A · doctrine
def m_a2():
    """Les 8 pages en anglais, et le repli de langue à l'anglais."""
    mauvais = [f for f in PAGES
               if not re.search(r'<html lang="en"', lire(f) or "")]
    repli, _ = compter(r'__atmLang=l=l\|\|"(?!en")', PAGES)
    if mauvais or repli:
        return False, ("%d page(s) hors anglais (%s) · %d repli(s) non anglais"
                       % (len(mauvais), " ".join(mauvais) or "—", repli))
    return True, "8 pages en <html lang=\"en\">, repli anglais"


def m_a3():
    """rejistre.html n'existe pas : la page du vivier s'appelle vivye.html.

    /!\\ ON NE COMPTE QUE LES RENVOIS, PAS LA PROSE. Le nom `rejistre.html`
    reste JUSTE dans un commentaire : sur atmart.ltd la page s'appelle vraiment
    ainsi, et c'est de la que ces pages sont derivees. Comptez la mention et la
    sentinelle accuse une page correcte — puis on apprend a ne plus la lire.
    """
    return zero(r'(?:href|action|src)="[^"]*rejistre\.html|location\.(?:href|assign|replace)\s*[=(]\s*["\'][^"\']*rejistre\.html|window\.open\(\s*["\'][^"\']*rejistre\.html',
                TOUTES, "renvoi(s) vers rejistre.html")


def m_a4():
    """setdi.html atteignable depuis une autre page.

    /!\\ « 7D PRO » NE SE COMPTE PLUS. La recommandation demandait de le
    renommer ; l'utilisateur a tranché l'inverse — c'est un nom de produit
    qu'il a choisi, au même titre que Driver Pool ou Career360. La sentinelle
    portait donc une décision abandonnée et accusait 35 fois un site correct.
    Reste la moitié qui vaut : setdi.html n'était liée de nulle part.
    """
    lie, _ = compter(r"setdi\.html", [f for f in TOUTES if f != "setdi.html"])
    return bool(lie), ("setdi.html liée depuis %d page(s)" % lie if lie
                       else "setdi.html n'est liée depuis aucune page")


def m_a5():
    """Les anciens noms de produits, visibles jusque dans les sujets de mail.

    /!\\ LES CLES DE STOCKAGE NE SE RENOMMENT PAS. `chofe360_code` et
    `chofe360_weakcmds` vivent dans le navigateur des gens : les rebaptiser
    deconnecterait tout le monde et effacerait les progres deja enregistres.
    C'est la regle posee avec les noms de produits — les URL, les codes d'acces
    et les cles de stockage restent. La sentinelle les comptait pourtant, et
    exigeait donc une correction qu'il ne faut surtout pas faire.
    """
    def sans_cles(t):
        return re.sub(r'(?:local|session)Storage\.\w+\(\s*"[^"]*"', "", t)

    return zero(r"Chof[eè]360|Chof%C3%A8360|coach Wout|pool Driver360",
                TOUTES, "ancien(s) nom(s) de produit", re.I, filtre=sans_cles)


def m_a7():
    """Le nombre d'employeurs annoncé au visiteur contre celui du fichier."""
    src = lire("tools/emplois.py")
    if src is None:
        return None, "tools/emplois.py introuvable"
    reel = len(re.findall(r"\bgenre\s*=", src))
    jobs = lire("jobs.html") or ""
    dits = set(re.findall(r"[Cc]hecking (\w+) pages", jobs))
    if not dits:
        return None, "la page n'annonce plus de nombre de pages vérifiées"
    mots = {"eight": 8, "twenty": 20, "huit": 8, "vingt": 20}
    valeurs = {mots.get(d.lower(), d) for d in dits}
    bon = valeurs == {reel}
    return bon, "la page dit %s, le fichier en compte %d" % (
        "/".join(str(v) for v in sorted(valeurs, key=str)), reel)


# ------------------------------------------------------- B · langue
def m_b1():
    """Le voile qui cache la page à tout visiteur non francophone."""
    n, ou = compter(r'if\(l!=="fr"\)\{d\.className\+=" i18n-wait"', PAGES)
    if n:
        return False, "%d page(s) voilées pour les non-francophones : %s" % (
            n, " ".join(ou))
    reste, _ = compter(r"i18n-wait", PAGES)
    return True, ("aucun voile inversé (%d mention(s) de i18n-wait restante(s))"
                  % reste)


def m_b3():
    """La description de partage suit-elle la langue choisie ?"""
    manque = []
    for f in ["vivye.html", "wout.html", "setdi.html", "anplwaye.html"]:
        t = lire(f) or ""
        if not re.search(r'name="description"[^>]*\][^>]*|querySelector\(\s*[\'"]meta\[name="?description', t):
            manque.append(f)
    if manque:
        return False, "description figée sur %d page(s) : %s" % (
            len(manque), " ".join(manque))
    return True, "les 4 pages produit retraduisent leur description"


def m_b4():
    """Le contrôle des textes non traduits lit-il CE dépôt ?"""
    src = lire("tools/verif_ids_traduits.py")
    if src is None:
        return None, "tools/verif_ids_traduits.py introuvable"
    # /!\ REGARDER L'AFFECTATION, PAS LA PROSE. Le contrôle a bien été corrigé
    # (`SOURCE = RACINE`), mais il EXPLIQUE la correction en nommant
    # `Atmart_website` dans son commentaire — et la sentinelle, qui cherchait
    # le mot n'importe où, accusait le fichier de son propre correctif.
    code = re.sub(r"#[^\n]*", "", src)
    code = re.sub(r'"""(?:.|\n)*?"""', "", code)
    mauvais = re.search(r"SOURCE\s*=\s*[^\n]*Atmart_website", code)
    return not mauvais, ("il lit Atmart_website, pas les pages publiées ici"
                         if mauvais else "il lit les pages de ce dépôt")


def m_b6():
    """404.html entre-t-elle dans le contrôle des langues ?"""
    src = lire("tools/verif_langue.py")
    if src is None:
        return None, "tools/verif_langue.py introuvable"
    bloc = re.search(r"PAGES\s*=\s*\[(.*?)\]", src, re.S)
    dedans = bool(bloc and "404.html" in bloc.group(1))
    return dedans, ("404.html est dans PAGES" if dedans
                    else "404.html reste hors du contrôle des langues")


def m_b13():
    """Les clés mortes du pied de page de jobs.html."""
    return zero(r'"(?:contact|droits)"\s*:', ["jobs.html"], "clé(s) morte(s)")


# ------------------------------------------------------- C · sécurité
def m_c1():
    """La ville du chauffeur, échappée ou non, avant d'atteindre l'employeur."""
    t = lire("anplwaye.html")
    if t is None:
        return None, "anplwaye.html introuvable"
    # /!\ LA SENTINELLE ETAIT AVEUGLE. Le motif cherchait `(e.city` non
    # precede de `esc(` — or dans `esc(e.city ...)` la parenthese EST celle de
    # `esc(`, si bien que chaque insertion correctement echappee etait comptee
    # comme brute. Le controle censes detecter une regression XSS ne pouvait
    # donc jamais passer, et son alarme permanente valait silence.
    code = re.sub(r"//[^\n]*", "", t)
    brut = len(re.findall(r"(?<!esc\()e\.city", code))
    total = len(re.findall(r"e\.city", code))
    return brut == 0, "%d insertion(s) de e.city sans esc(), sur %d" % (
        brut, total)


def m_c3():
    """Le nom de l'organisation, échappé avant d'atteindre le chauffeur."""
    t = lire("vivye.html")
    if t is None:
        return None, "vivye.html introuvable"
    code = re.sub(r"//[^\n]*", "", t)          # meme correction qu'en C1
    brut = len(re.findall(r"(?<!esc\()d\.org", code))
    a_esc = bool(re.search(r"function esc\b", t))
    return (brut == 0 and a_esc), (
        "%d insertion(s) de d.org sans esc() · esc() %s dans la page"
        % (brut, "défini" if a_esc else "ABSENT"))


def m_c4():
    """Le bouton « Sélectionner » lève-t-il encore une ReferenceError ?"""
    t = lire("anplwaye.html")
    if t is None:
        return None, "anplwaye.html introuvable"
    # /!\ NE PAS COMPTER LA DECLARATION. `function enAttente(id)` contient
    # evidemment « enAttente(id) » : la sentinelle accusait donc la definition
    # de la fonction, jamais ses appels, et criait au loup en permanence.
    appels = re.findall(r"(?<!function )enAttente\(([^)]*)\)", t)
    casse = [a for a in appels if a.strip() == "id"]
    return not casse, ("%d appel(s) enAttente(id) — identifiant non déclaré"
                       % len(casse) if casse
                       else "enAttente() reçoit un identifiant déclaré (%d appel(s))"
                       % len(appels))


def m_c11():
    """Le fichier vide servi publiquement."""
    existe = os.path.exists(os.path.join(RACINE, "code.txt"))
    return not existe, ("code.txt est toujours publié" if existe
                        else "code.txt supprimé")


# ------------------------------------------------------- D · légal
def m_d1():
    """Les pages légales sont-elles atteignables d'où l'on collecte ?"""
    sans = [f for f in PAGES
            if not re.search(r'href="(?:\./)?(?:terms|privacy)\.html"',
                             lire(f) or "")]
    if sans:
        return False, "%d page(s) sans lien vers les pages légales : %s" % (
            len(sans), " ".join(sans))
    return True, "les 8 pages renvoient aux conditions et à la confidentialité"


def m_d4():
    """Un éditeur qui se déclare d'un État où il n'est pas immatriculé."""
    return zero(r"Atmart LLC(?:</a>)?\.\s*Massachusetts", TOUTES,
                "mention(s) « Atmart LLC. Massachusetts. »")


# ------------------------------------------------------- E · métier
def m_e1():
    """L'argument de vente du 7D, démenti par le RMV depuis avril 2026."""
    return zero(r"men many[eè]l la se an angle s[eè]lman|mais pas le manuel"
                r"|but not the manual|pero no el manual",
                ["setdi.html"], "affirmation(s) « le manuel n'existe pas »",
                re.I)


def m_e3():
    """Le dérapage : le manuel dit « dans la direction du dérapage »."""
    p = os.path.join(RACINE, "assets", "pemi-questions.json")
    if not os.path.exists(p):
        return None, "pemi-questions.json introuvable"
    t = io.open(p, encoding="utf-8").read()
    faux = "Steer in the direction you WANT to go" in t
    return not faux, ("q15 contredit encore le manuel" if faux
                      else "q15 ne porte plus la réponse contredite")


def m_e13():
    """La banque de questions : taille, tirage, doublons LITTÉRAUX.

    ⚠️ Cette mesure ne juge PAS la ligne E13. Les quatre doublons relevés à la
    relecture (q03≡q24, q04≡q23, q05≡q22, q11⊂q26) sont des doublons de SENS,
    formulés différemment : aucune comparaison de chaînes ne les voit. Elle est
    ici pour donner les nombres — 28 questions pour 25 tirées, donc presque
    toute la banque à chaque passage — et elle est volontairement absente de
    MESURES. Fermer E13 reste un geste humain.
    """
    p = os.path.join(RACINE, "assets", "pemi-questions.json")
    if not os.path.exists(p):
        return None, "pemi-questions.json introuvable"
    d = json.load(io.open(p, encoding="utf-8"))
    qs = d.get("questions", d if isinstance(d, list) else [])
    vus, doubles = {}, []
    for q in qs:
        cle = (q.get("q") or {}).get("en", "")
        cle = re.sub(r"[^a-z0-9]+", "", cle.lower())
        if cle and cle in vus:
            doubles.append("%s≡%s" % (vus[cle], q.get("id")))
        elif cle:
            vus[cle] = q.get("id")
    total = len(qs)
    tire = d.get("total", 25)
    return (not doubles), "%d question(s) pour %d tirées · %d doublon(s) %s" % (
        total, tire, len(doubles), " ".join(doubles))


# ------------------------------------------------------- F · rendu
def m_f2():
    """Un var() dont le nom n'est défini nulle part vaut « rien »."""
    definis = set()
    for f in ["assets/style.css", "assets/theme.css"] + TOUTES:
        t = lire(f) or ""
        definis |= set(re.findall(r"(--[a-z0-9-]+)\s*:", t, re.I))
    utilises = {}
    for f in TOUTES + ["assets/style.css", "assets/theme.css",
                       "assets/suite.js", "assets/script.js"]:
        t = lire(f) or ""
        for nom in re.findall(r"var\(\s*(--[a-z0-9-]+)", t, re.I):
            utilises[nom] = utilises.get(nom, 0) + 1
    orphelins = {n: k for n, k in utilises.items() if n not in definis}
    if orphelins:
        return False, "%d jeton(s) jamais défini(s) : %s" % (
            len(orphelins),
            " ".join("%s×%d" % (n, k) for n, k in sorted(orphelins.items())))
    return True, "les %d jetons employés sont tous définis" % len(utilises)


def m_f3():
    """La page 404 a-t-elle reçu la feuille de thème ?"""
    return partout(r"theme\.css", TOUTES, "theme.css")


def m_f4():
    """Un champ sous 16 px fait zoomer iOS tout seul."""
    petits = []
    for f in PAGES:
        t = lire(f) or ""
        for regle in re.findall(r"[^\n{]*(?:input|textarea|select)[^\n{]*\{[^}]*\}", t):
            m = re.search(r"font-size:\s*([\d.]+)(rem|px|em)", regle)
            if not m:
                continue
            v = float(m.group(1))
            px = v * 16 if m.group(2) in ("rem", "em") else v
            if px < 16:
                petits.append("%s(%.2fpx)" % (f, px))
    if petits:
        return False, "%d règle(s) de champ sous 16 px : %s" % (
            len(petits), " ".join(petits))
    return True, "aucune règle de champ sous 16 px"


# ------------------------------------------------------- G · fabrication
def m_g1():
    """Une copie de données qui échoue doit faire échouer le build."""
    src = lire("tools/regen.py")
    if src is None:
        return None, "tools/regen.py introuvable"
    sort = bool(re.search(r"sys\.exit\(", src))
    return sort, ("regen.py se termine par un code de sortie" if sort
                  else "regen.py sort toujours en 0, même sans les données")


def m_g2():
    """Un lien partagé sur WhatsApp sans vignette est un lien nu."""
    return partout(r'property="og:(?:title|image)"', TOUTES,
                   "les balises Open Graph")


def m_g3():
    """Deux URL pour un même contenu, sans canonical pour arbitrer."""
    return partout(r'rel="canonical"', PAGES, "le lien canonique")


def m_g4():
    """828 Ko publiés que plus rien ne charge."""
    reste = [p for p in ("assets/i18n", "assets/i18n.js")
             if os.path.exists(os.path.join(RACINE, p))]
    return not reste, ("encore publié : " + " ".join(reste) if reste
                       else "le dictionnaire mort est supprimé")


# ------------------------------------------------------- H · parcours reel
def m_h1():
    """Le lien de CV, refuse cote page avant meme d'atteindre le Worker.

    Mesure au navigateur du 30/08 : `javascript:alert(1)` passe checkValidity().
    Un <input type="url"> accepte n'importe quel schema absolu — le refus doit
    donc etre ecrit dans le code, pas delegue au navigateur.
    """
    t = lire("vivye.html")
    if t is None:
        return None, "vivye.html introuvable"
    lit = bool(re.search(r'getElementById\("rj-cv"\)', t))
    if not lit:
        return None, "le champ rj-cv n'est plus lu par la page"
    # /!\ LE MOTIF CHERCHAIT UN LITTERAL QUI N'EXISTE PAS. Dans une expression
    # reguliere JavaScript les barres obliques sont echappees — `^https?:\/\//`
    # — si bien que la sentinelle ne trouvait jamais le filtre POURTANT PRESENT
    # et declarait la page ouverte a `javascript:`. Une alarme qui ne peut pas
    # s'eteindre ne protege rien.
    passe = bool(re.search(r'lienSur\(\s*document\.getElementById\("rj-cv"\)', t))
    garde = bool(re.search(r"function lienSur\b", t)
                 and re.search(r"\^https\?:\\?/\\?/", t))
    ok = passe and garde
    return ok, ("le lien de CV passe par lienSur(), ancre sur ^https?://" if ok
                else "filtre absent ou contourne : passe=%s garde=%s"
                     % (passe, garde))


def m_h3():
    """Une seule cle de cache pour la feuille de style."""
    formes = {}
    for f in TOUTES:
        for m in re.findall(r"assets/style\.css[^\"']*", lire(f) or ""):
            formes.setdefault(m, []).append(f)
    if len(formes) <= 1:
        return True, "une seule forme d'appel : %s" % (
            " ".join(formes) or "aucune")
    return False, "%d formes concurrentes : %s" % (
        len(formes),
        " · ".join("%s (%d pages)" % (k, len(v)) for k, v in formes.items()))


def m_h4():
    """L'index de la bonne reponse, laisse dans le DOM."""
    # /!\ L'ATTRIBUT, PAS LA PROSE. Le motif nu comptait aussi le commentaire
    # qui EXPLIQUE pourquoi l'attribut a ete retire — la sentinelle accusait
    # donc la page de son propre correctif. Meme defaut qu'en A3 et B4.
    def sans_commentaires(t):
        return re.sub(r"//[^\n]*", "", t)

    return zero(r'data-oi\s*=', ["wout.html", "setdi.html"],
                "attribut(s) data-oi revelant la bonne reponse",
                filtre=sans_commentaires)


def m_h7():
    """Le formulaire employeur, envoyable a vide."""
    t = lire("anplwaye.html")
    if t is None:
        return None, "anplwaye.html introuvable"
    # /!\ CE MOTIF NE POUVAIT RIEN TROUVER. Il contenait deux caracteres
    # RETOUR ARRIERE (0x08) la ou quelqu'un voulait ecrire \b : un `\b` tape
    # dans une chaine NON brute vaut le caractere backspace, et il a ete
    # enregistre tel quel. Invisible a la relecture, invisible dans un diff,
    # et la sentinelle accusait un formulaire correct — ce qu'elle a fait ce
    # 31/08/2026, apres que les quatre `required` ont ete poses.
    n = len(re.findall(r"\brequired\b", t))
    return n > 0, "%d champ(s) obligatoire(s) dans le formulaire employeur" % n



# ------------------------------------------------------- I · DSP-ready
WORKER = os.path.join(os.path.dirname(RACINE), "Atmart_chat_worker")


def m_i1():
    """Les champs DSP-ready dans la page publiee, et dans les 4 langues."""
    t = lire("vivye.html")
    if t is None:
        return None, "vivye.html introuvable"
    cases = len(re.findall(r'value="(?:age21|licUS|recordClean|screenOk|lift50)"', t))
    slots = len(re.findall(r'id="rj-slot[123]"', t))
    envoie = bool(re.search(r'dsp:checked\("#rj-dsp"\)', t)) and "slots:[1,2,3]" in t
    dicos = len(re.findall(r"\bdAge21:", t))
    bon = cases == 5 and slots == 3 and envoie and dicos == 4
    return bon, "%d/5 attestations · %d/3 creneaux · profile() %s · %d/4 dictionnaires" % (
        cases, slots, "envoie dsp+slots" if envoie else "N'ENVOIE PAS", dicos)


def m_i2():
    """Le test comportemental du Worker, rejoue tel quel."""
    test = os.path.join(WORKER, "tests", "dsp-ready.js")
    if not os.path.exists(test):
        return None, "tests/dsp-ready.js introuvable dans Atmart_chat_worker"
    r = subprocess.run(["node", test], cwd=WORKER, capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    out = (r.stdout or "") + (r.stderr or "")
    ok_n = out.count("\u2705")
    ko_n = out.count("\u274c")
    return r.returncode == 0, "%d assertion(s) vertes, %d rouge(s)" % (ok_n, ko_n)


def m_i3():
    """La seule voie qui pose phoneOk."""
    src = lire("tools/alertes_whatsapp.py")
    if src is None:
        return None, "alertes_whatsapp.py introuvable"
    a = "def action_tel_ok(" in src
    b = '"--tel-ok"' in src
    c = "action_tel_ok(fiches, args.tel_ok)" in src
    return a and b and c, "fonction %s · option %s · dispatch %s" % (
        "ok" if a else "ABSENTE", "ok" if b else "ABSENTE", "ok" if c else "ABSENT")



def m_i4():
    """Le chauffeur voit son verdict, dans les 4 langues."""
    t = lire("vivye.html")
    if t is None:
        return None, "vivye.html introuvable"
    boite = 'id="rj-dspbox"' in t
    fn = "function showDsp(" in t
    branches = t.count("showDsp(res.body")
    cles = len(re.findall(r"\bmPhone:", t))
    bon = boite and fn and branches >= 3 and cles == 4
    return bon, "boite %s · showDsp %s · %d branchement(s) · %d/4 dictionnaires" % (
        "ok" if boite else "ABSENTE", "ok" if fn else "ABSENT", branches, cles)


def m_i5():
    """L'employeur filtre sur le badge, et ne voit que le badge."""
    t = lire("anplwaye.html")
    if t is None:
        return None, "anplwaye.html introuvable"
    case = 'id="ep-dsp"' in t
    envoi = bool(re.search(r'dsp:\s*document\.getElementById\("ep-dsp"\)\.checked', t))
    badge = "function dspBadge(" in t and "dspBadge(e)" in t
    cles = len(re.findall(r"\bdspFilter:", t))
    # le badge remplace les colonnes : aucune colonne « attestation » ne doit
    # apparaitre dans l'en-tete du vivier libre
    colonne = bool(re.search(r"<th[^>]*>[^<]*(?:21|MVR|50 lb|dépistage|drug)", t, re.I))
    bon = case and envoi and badge and cles == 4 and not colonne
    return bon, "case %s · requete %s · badge %s · %d/4 dictionnaires · colonne critere %s" % (
        "ok" if case else "ABSENTE", "ok" if envoi else "ABSENTE", "ok" if badge else "ABSENT",
        cles, "AJOUTEE" if colonne else "aucune")


# --------------------------------------------------------------- le tableau
MESURES = {
    "A2": m_a2, "A3": m_a3, "A4": m_a4, "A5": m_a5, "A7": m_a7,
    "B1": m_b1, "B3": m_b3, "B4": m_b4, "B6": m_b6, "B13": m_b13,
    "C1": m_c1, "C3": m_c3, "C4": m_c4, "C11": m_c11,
    "D1": m_d1, "D4": m_d4,
    "E1": m_e1, "E3": m_e3,
    "F2": m_f2, "F3": m_f3, "F4": m_f4,
    "G1": m_g1, "G2": m_g2, "G3": m_g3, "G4": m_g4,
    "H1": m_h1, "H3": m_h3, "H4": m_h4, "H7": m_h7,
    "I1": m_i1, "I2": m_i2, "I3": m_i3, "I4": m_i4, "I5": m_i5,
}

# « fait » déclaré = le contrôle DOIT passer. Toute autre valeur n'engage
# rien : on mesure quand même, et on le dit.
FERME = ("fait", "résolu", "tranché", "vérifié")


def declares():
    """Ce que le registre affirme, ligne par ligne."""
    if not os.path.exists(REGISTRE):
        raise SystemExit("registre introuvable : %s" % REGISTRE)
    out = {}
    for ligne in io.open(REGISTRE, encoding="utf-8"):
        m = re.match(r"\|\s*([A-I]\d{1,2})\s*\|([^|]*)\|([^|]*)\|([^|]*)\|",
                     ligne)
        if m:
            out[m.group(1)] = (m.group(2).strip(),
                               m.group(3).strip(),
                               m.group(4).strip().replace("*", "").lower())
    return out


def principal():
    seulement_ouvert = "--ouvert" in sys.argv
    dit = declares()
    if not dit:
        raise SystemExit("aucune ligne lue dans le registre — le format "
                         "du tableau a-t-il changé ?")

    print("ÉTAT DES RECOMMANDATIONS DRIVER360 — mesuré, pas relu\n")
    print("%-5s %-40s %-10s %s" % ("", "recommandation", "registre", "mesure"))
    print("-" * 100)

    desaccords, humains, ouverts, fermes = [], [], [], []
    bloquants_ouverts = []
    ordre = sorted(dit, key=lambda k: (k[0], int(k[1:])))

    for ident in ordre:
        titre, gravite, etat = dit[ident]
        ferme = any(f in etat for f in FERME)
        if "humain" in etat:
            humains.append(ident)
        elif ferme:
            fermes.append(ident)
        else:
            ouverts.append(ident)
            if "🔴" in gravite:
                bloquants_ouverts.append(ident)

        if seulement_ouvert and ferme:
            continue

        court = titre if len(titre) <= 40 else titre[:37] + "..."
        if ident in MESURES:
            try:
                bon, detail = MESURES[ident]()
            except Exception as e:                            # noqa: BLE001
                bon, detail = None, "mesure impossible : %s" % e
            marque = "  " if bon is None else ("ok" if bon else "!!")
            print("%-5s %-40s %-10s %s %s"
                  % (ident, court, etat[:10], marque, detail))
            if bon is not None and ferme != bon:
                desaccords.append((ident, etat, detail))
        else:
            print("%-5s %-40s %-10s %s"
                  % (ident, court, etat[:10], "— non mesurable"))

    print("-" * 100)
    print("%d ligne(s) · %d close(s) · %d ouverte(s) · %d en attente d'un humain"
          % (len(dit), len(fermes), len(ouverts), len(humains)))
    print("%d ligne(s) mesurée(s) automatiquement, %d ne le sont pas"
          % (len(MESURES), len(dit) - len(MESURES)))
    if bloquants_ouverts:
        print("   BLOQUANTS ouverts   : " + " ".join(bloquants_ouverts))
    if humains:
        print("   attendent un humain : " + " ".join(humains))

    if desaccords:
        print("\nLE REGISTRE MENT — c'est lui qu'il faut corriger, pas la mesure :")
        for ident, etat, detail in desaccords:
            print("   %s déclare « %s », la mesure dit : %s"
                  % (ident, etat, detail))
        return 1

    print("\nChaque ligne mesurable est conforme à ce que le registre déclare.")
    return 0


if __name__ == "__main__":
    sys.exit(principal())
