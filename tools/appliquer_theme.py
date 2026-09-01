# -*- coding: utf-8 -*-
"""
Remplace les couleurs écrites en dur des pages publiées par des jetons.

    python tools/appliquer_theme.py            applique
    python tools/appliquer_theme.py --verifier  échoue s'il en reste

À LANCER APRÈS toute génération de page. `tools/build.py` s'en charge.

POURQUOI
--------
Les pages de la suite portaient leurs couleurs en clair, dans des attributs
`style` et des blocs `<style>` : `#fff` pour un titre, `#9db2c7` pour un texte
courant, `rgba(255,255,255,.04)` pour une carte. C'est parfaitement lisible sur
le fond sombre d'origine — et parfaitement illisible sur un fond clair, où
cela donne du blanc sur du blanc.

Aucun réglage global ne peut rattraper une couleur écrite en dur. Ce script
fait donc la seule chose qui marche : il les remplace toutes par des jetons,
dont `assets/theme.css` donne deux jeux de valeurs.

CE QUI EST DÉLIBÉRÉMENT LAISSÉ TEL QUEL
  · les couleurs à l'intérieur de `assets/` (style.css, theme.css) — c'est là
    que les jetons sont définis ;
  · `#0e2240` dans `<meta name="theme-color">`, que le script de bascule met à
    jour lui-même : une variable CSS n'a pas cours dans une balise meta.

⚠️ CE SCRIPT EST IDEMPOTENT et doit le rester : il tourne à chaque
régénération, donc repasser sur une page déjà traitée ne doit rien changer.
"""
import io
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGES = ["index.html", "jobs.html", "vivye.html", "anplwaye.html", "wout.html",
         "setdi.html", "terms.html", "privacy.html", "404.html"]

# L'ordre compte : les formes longues d'abord (#ffffff avant #fff).
REMPLACEMENTS = [
    # --- textes ---
    ("#ffffff", "var(--d-fort)"), ("#FFFFFF", "var(--d-fort)"),
    ("#fff", "var(--d-fort)"), ("#FFF", "var(--d-fort)"),
    ("#eaf2fb", "var(--d-fort)"),
    ("#d7e3f0", "var(--d-texte)"), ("#c9d8e6", "var(--d-texte)"),
    ("#9db2c7", "var(--d-doux)"),
    ("#7f93a7", "var(--d-faible)"), ("#6f8296", "var(--d-faible)"),
    ("#5a6f83", "var(--d-faible)"),
    # --- fonds ---
    ("#0e2240", "var(--d-fond)"), ("#0a1a2f", "var(--d-fond-2)"),
    ("#12233d", "var(--d-surface-2)"), ("#12406b", "var(--d-surface-2)"),
    # --- accents ---
    ("#2ec4b6", "var(--d-accent)"), ("#06232b", "var(--d-accent-encre)"),
    ("#5d9cec", "var(--d-bleu)"),
    ("#f4a261", "var(--d-alerte)"),
    ("#e4dbcf", "var(--d-alerte-texte)"), ("#c9b79c", "var(--d-alerte-doux)"),
    ("#e63946", "var(--d-danger)"), ("#ff8a94", "var(--d-danger)"),
    # teintes propres a style.css, trouvees en l'y appliquant a son tour
    ("#0b1f3d", "var(--d-fond-2)"), ("#0b1a30", "var(--d-fond-2)"),
    ("#081426", "var(--d-fond-2)"), ("#0f2540", "var(--d-fond-2)"),
    ("#16365c", "var(--d-surface-2)"), ("#1e3a5f", "var(--d-ligne)"),
    ("#bfe9e3", "var(--d-texte)"), ("#dbe9f5", "var(--d-fort)"),
    ("#8fa6bd", "var(--d-doux)"), ("#e8d5c4", "var(--d-alerte-texte)"),
    ("#06251f", "var(--d-accent-encre)"),
    # pastilles de resultat (reussi / echoue) du coach
    ("#123f2c", "var(--d-vert-fond)"), ("#5c1a22", "var(--d-alerte-fond)"),
    ("#2fd573", "var(--d-vert)"),
]

# Les couleurs translucides, écrites de vingt façons (espaces, .04 ou 0.04…).
# On les attrape par expression régulière plutôt que d'énumérer les variantes.
TRANSLUCIDES = [
    (re.compile(r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0?\.0[1-6]\d*\s*\)"), "var(--d-surface)"),
    (re.compile(r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0?\.0[7-9]\d*\s*\)"), "var(--d-surface-2)"),
    (re.compile(r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0?\.(1\d*|2[0-5]\d*)\s*\)"), "var(--d-ligne)"),
    (re.compile(r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0?\.[3-9]\d*\s*\)"), "var(--d-ligne-forte)"),
    (re.compile(r"rgba\(\s*46\s*,\s*196\s*,\s*182\s*,\s*0?\.[01]\d*\s*\)"), "var(--d-accent-fond)"),
    (re.compile(r"rgba\(\s*46\s*,\s*196\s*,\s*182\s*,\s*0?\.[2-9]\d*\s*\)"), "var(--d-accent-bord)"),
    (re.compile(r"rgba\(\s*93\s*,\s*156\s*,\s*236\s*,\s*0?\.[01]\d*\s*\)"), "var(--d-bleu-fond)"),
    (re.compile(r"rgba\(\s*93\s*,\s*156\s*,\s*236\s*,\s*0?\.[2-9]\d*\s*\)"), "var(--d-bleu-bord)"),
    (re.compile(r"rgba\(\s*244\s*,\s*162\s*,\s*97\s*,\s*0?\.[01]\d*\s*\)"), "var(--d-alerte-fond)"),
    (re.compile(r"rgba\(\s*244\s*,\s*162\s*,\s*97\s*,\s*0?\.[2-9]\d*\s*\)"), "var(--d-alerte-bord)"),
    (re.compile(r"rgba\(\s*37\s*,\s*211\s*,\s*102\s*,\s*0?\.[01]\d*\s*\)"), "var(--d-vert-fond)"),
    (re.compile(r"rgba\(\s*37\s*,\s*211\s*,\s*102\s*,\s*0?\.[2-9]\d*\s*\)"), "var(--d-vert-bord)"),
    (re.compile(r"rgba\(\s*230\s*,\s*57\s*,\s*70\s*,\s*0?\.[0-9]\d*\s*\)"), "var(--d-alerte-fond)"),
    (re.compile(r"rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0?\.[0-9]\d*\s*\)"), "var(--d-ombre)"),
]

# CE QUI DOIT RESTER LITTÉRAL.
#
#  · `<meta name="theme-color">` — une balise meta ne comprend pas var().
#
#  · ⚠️ TOUT BLOC `@media print`. Piège rencontré le 30/08/2026 : la première
#    passe y a transformé `background:#fff` en `background:var(--d-fort)`.
#    Sur fond clair ce jeton vaut presque noir — la page se serait imprimée
#    en noir plein, et le guide de l'accompagnateur est fait pour être
#    imprimé. Le papier est toujours blanc : ses couleurs ne se thématisent
#    pas.
GARDE = re.compile(
    r'<meta name="theme-color"[^>]*>'
    r'|@media\s+print\s*\{(?:[^{}]|\{[^{}]*\})*\}')


LIEN = '<link rel="stylesheet" href="assets/theme.css?v=5" />'

# ⚠️ CE SCRIPT DOIT S'EXÉCUTER AVANT LE PREMIER AFFICHAGE.
# Poser la classe depuis suite.js, chargé en bas de page, ferait apparaître la
# page en sombre puis basculer en clair sous les yeux du visiteur — le fameux
# « flash ». Désagréable partout, et sur un téléphone en plein soleil, il fait
# rater la première seconde de lecture. Il est donc inline, dans le <head>.
BASCULE = """<script>/* fond clair/sombre — avant le premier affichage */
(function(){var c=null;try{c=localStorage.getItem("atmart_theme")}catch(e){}
var clair = c==="clair" || (c!=="sombre" && window.matchMedia
  && window.matchMedia("(prefers-color-scheme: light)").matches);
if(clair) document.documentElement.className += " clair";
var m=document.querySelector('meta[name="theme-color"]');
if(m) m.setAttribute("content", clair ? "#f4f8fb" : "#0e2240");})();
</script>"""


# LA POLITIQUE DE SÉCURITÉ DU CONTENU.
#
# Elle limite d'où la page a le droit de charger et d'appeler. Sans elle, une
# injection réussie quelque part peut faire venir un script de n'importe où et
# expédier les données ailleurs ; avec elle, l'injection ne mène nulle part.
#
# ⚠️ `'unsafe-inline'` A ÉTÉ LEVÉ SUR LES SCRIPTS, le 31/08/2026, par
# EMPREINTES. C'était le filet sous les deux XSS stockés (C1, C3) — et il
# n'existait pas : une charge injectée se serait exécutée sans obstacle.
#
# Pourquoi des empreintes plutôt qu'un refactor. Sortir la trentaine de blocs
# `<script>` en fichiers séparés casserait ce qui fait tenir ce site : le thème
# et la langue sont posés AVANT le premier affichage précisément PARCE QU'ILS
# SONT EN LIGNE. Externalisés, ils s'exécuteraient plus tard et la page
# clignoterait du sombre au clair à chaque chargement. On aurait échangé une
# faille théorique contre un défaut visible par tous.
#
# Un `nonce` est l'autre solution propre, mais il doit changer à chaque
# réponse : impossible sur GitHub Pages, qui sert des fichiers figés.
#
# ⚠️ CONSÉQUENCE : toute modification d'un bloc en ligne change son empreinte.
# Le calcul se fait donc À LA POSE, page par page, après toutes les autres
# étapes du build. Écrire ces empreintes à la main condamnerait la page au
# premier caractère changé.
#
# ⚠️ `style-src` GARDE `'unsafe-inline'`. Les empreintes ne couvrent pas les
# attributs `style=`, et le site en pose des dizaines. Les retirer est un
# chantier de mise en page, pas de sécurité : un `style=` injecté ne peut pas
# exécuter de code.
#
# ⚠️ `frame-ancestors` NE PEUT PAS être posé dans une balise meta (la
# spécification l'ignore). La protection contre l'encadrement doit venir d'un
# EN-TÊTE, donc de Cloudflare — c'est noté dans le README, avec la règle à
# créer. GitHub Pages, lui, ne pose aucun en-tête.
# La directive contient des apostrophes ET des guillemets d'attribut : on la
# construit a partir d'une liste, ce qui evite toute imbrication de quotes.
DIRECTIVES = [
    "default-src 'self'",
    # script-src est complete PAR PAGE avec les empreintes de ses blocs en
    # ligne : voir empreintes_scripts() et poser_securite().
    "script-src 'self'",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com",
    "img-src 'self' data:",
    # Le seul interlocuteur reseau autorise : notre Worker.
    "connect-src 'self' https://atmart-chat.atmartllc.workers.dev",
    "form-action 'self'",
    "base-uri 'self'",
    "object-src 'none'",
    "frame-src 'none'",
    # Sans ces deux lignes, le service worker et le manifeste
    # dependent d'un repli implicite sur default-src : on prefere le
    # dire, la PWA en depend.
    "worker-src 'self'",
    "manifest-src 'self'",
]
CSP = ('<meta http-equiv="Content-Security-Policy" content="'
       + "; ".join(DIRECTIVES) + '" />')

# L'adresse d'une page ne doit pas fuir vers les sites vers lesquels on renvoie.
AUTRES = '<meta name="referrer" content="strict-origin-when-cross-origin" />'


def empreintes_scripts(s):
    """Le SHA-256 de chaque bloc <script> SANS `src`, encode en base64.

    Le navigateur n'executera que les blocs dont l'empreinte figure dans la
    politique — au caractere pres. Un script injecte n'a pas la bonne
    empreinte : il ne demarre pas.
    """
    import base64
    import hashlib
    out = []
    for m in re.finditer(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", s, re.S):
        h = hashlib.sha256(m.group(1).encode("utf-8")).digest()
        e = "'sha256-%s'" % base64.b64encode(h).decode("ascii")
        if e not in out:
            out.append(e)
    return out


def poser_securite(s):
    # ⚠️ ON REMPLACE, ON N'IGNORE PAS. La version d'origine sortait des qu'une
    # CSP existait : une page deja generee gardait donc la sienne pour
    # toujours. Le passage aux empreintes n'aurait jamais pris effet — et
    # surtout, une empreinte perimee bloquerait la page en silence.
    s = re.sub(r'\s*<meta http-equiv="Content-Security-Policy"[^>]*/>', "", s)
    s = re.sub(r'\s*<meta name="referrer"[^>]*/>', "", s)
    # ⚠️ LES EMPREINTES SE CALCULENT ICI, sur la page finie. Les figer ailleurs
    # les perimerait au premier caractere change dans un bloc en ligne.
    directives = list(DIRECTIVES)
    emp = empreintes_scripts(s)
    if emp:
        for i, d in enumerate(directives):
            if d.startswith("script-src"):
                directives[i] = d + " " + " ".join(emp)
                break
    csp = ('<meta http-equiv="Content-Security-Policy" content="'
           + "; ".join(directives) + '" />')
    ancre = '<meta charset="UTF-8" />'
    if ancre in s:
        s = s.replace(ancre, ancre + chr(10) + "  " + csp + chr(10) + "  " + AUTRES, 1)
    return s


def poser_theme(s):
    """Ajoute la feuille du thème et le script anti-clignotement, une seule fois."""
    # ⚠️ ON CHERCHE LA FEUILLE, PAS UNE CHAINE EXACTE. 404.html l'appelle en
    # `/assets/theme.css` : compare a `LIEN` — qui est relatif — elle passait
    # pour depourvue de theme, et on lui en aurait ajoute un SECOND, relatif,
    # donc introuvable depuis /une/adresse/profonde.
    if not re.search(r'<link rel="stylesheet" href="/?assets/theme\.css', s):
        # Les pages derivees portent un `?v=` sur style.css : on repere le
        # lien par expression reguliere plutot que par egalite exacte.
        #
        # ⚠️ LA BARRE OBLIQUE DE TETE EST FACULTATIVE. 404.html doit appeler
        # ses fichiers en chemin ABSOLU — elle est servie a n'importe quelle
        # adresse, et un chemin relatif irait chercher la feuille de style dans
        # /un/dossier/qui/n/existe/pas/assets/. Le motif, lui, n'acceptait que
        # la forme relative : il ne voyait donc pas le lien de 404.html et n'y
        # posait jamais le theme. La page restait en sombre, sans focus
        # visible, sans reduced-motion — et le controle disait « vert », parce
        # qu'il ne regardait pas cette page-la non plus.
        m = re.search(r'<link rel="stylesheet" href="/?assets/style\.css[^"]*"\s*/?>', s)
        if m:
            # Le lien pose EPOUSE la forme de celui qu'il suit : absolu sur une
            # page servie a n'importe quelle adresse, relatif ailleurs.
            lien = (LIEN.replace('href="assets/', 'href="/assets/')
                    if '"/assets/style.css' in m.group(0) else LIEN)
            s = s[:m.end()] + "\n  " + lien + s[m.end():]
    if 'localStorage.getItem("atmart_theme")' not in s:
        s = s.replace(LIEN, LIEN + "\n" + BASCULE, 1)
    return s


def traiter(s):
    protege = []

    def mettre_de_cote(m):
        protege.append(m.group(0))
        return "\x00%d\x00" % (len(protege) - 1)

    s = GARDE.sub(mettre_de_cote, s)
    for avant, apres in REMPLACEMENTS:
        s = s.replace(avant, apres)
    for motif, apres in TRANSLUCIDES:
        s = motif.sub(apres, s)
    for i, brut in enumerate(protege):
        s = s.replace("\x00%d\x00" % i, brut)
    return poser_securite(poser_theme(s))


RESTE = re.compile(r"#[0-9a-fA-F]{3,6}\b|rgba?\([0-9]")


def main():
    verifier = "--verifier" in sys.argv
    restants, touchees = {}, 0
    for page in PAGES:
        chemin = os.path.join(RACINE, page)
        if not os.path.exists(chemin):
            continue
        with io.open(chemin, encoding="utf-8") as f:
            avant = f.read()
        apres = traiter(avant)
        if apres != avant and not verifier:
            with io.open(chemin, "w", encoding="utf-8", newline="\n") as f:
                f.write(apres)
            touchees += 1
        cible = avant if verifier else apres
        sans_meta = GARDE.sub("", cible)
        # Le script anti-clignotement porte deux couleurs litterales : ce
        # sont les valeurs de <meta name="theme-color">, ou var() n'a pas
        # cours. Le controle ne doit pas se signaler lui-meme.
        sans_meta = re.sub(r"<script>/\* fond clair/sombre.*?</script>",
                           "", sans_meta, flags=re.S)
        trouves = RESTE.findall(sans_meta)
        if trouves:
            restants[page] = len(trouves)

    if verifier:
        if restants:
            print("Couleurs encore ecrites en dur :")
            for p, n in sorted(restants.items()):
                print("  - %-16s %d" % (p, n))
            print("\nAjouter la correspondance dans REMPLACEMENTS, puis relancer le build.")
            return 1
        print("Theme : aucune couleur ecrite en dur dans les %d pages." % len(PAGES))
        return 0

    print("Theme : %d page(s) converties en jetons." % touchees)
    if restants:
        print("  restent a traiter : %s" % ", ".join("%s (%d)" % kv for kv in sorted(restants.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
