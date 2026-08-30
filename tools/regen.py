# -*- coding: utf-8 -*-
"""
Régénère les pages de driver360.atmart.ltd depuis atmart.ltd.

À relancer APRÈS toute modification des pages sources :
    python tools/regen.py
puis commit + push de ce dépôt.

POURQUOI CETTE PLATEFORME. Driver360 et le portail employeur vivaient comme
deux pages parmi vingt sur atmart.ltd. Réunis sous une adresse à eux, ils
deviennent une offre lisible — comme Suite360 l'a fait pour Interview360 et
Career360.

MAIS AVEC UNE DIFFÉRENCE QUI COMMANDE TOUT LE RESTE. Suite360 sert UNE
personne : le chercheur d'emploi passe d'un outil à l'autre. Ici, un chauffeur
et un employeur ne veulent pas la même chose et n'arrivent pas par la même
porte. L'accueil BIFURQUE donc immédiatement — « je conduis » / « je recrute »
— et aucune page n'essaie de parler aux deux à la fois.

TRANSFORMATIONS APPLIQUÉES
  · en-tête et pied neutres « Driver360 pa Atmart », propres à la suite ;
  · les scripts du site Atmart (launcher, share, sw d'atmart.ltd) retirés ;
  · les liens internes vers atmart.ltd deviennent absolus, ceux de la suite
    deviennent relatifs ;
  · le service worker et le manifeste de la suite branchés.

Les pages sources ne sont JAMAIS modifiées : atmart.ltd garde les siennes, et
les redirections y sont posées à la main.
"""
import io, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(os.path.dirname(RACINE), "Atmart_website")

# Quelle page source devient quelle page de la suite, et de quel côté du
# marché elle se range. Le côté décide de l'en-tête : on ne montre pas les
# outils du chauffeur à un employeur.
PAGES = [
    ("chofe360.html",    "wout.html",     "chauffeur", "Wout",       "Coach du test de route"),
    ("setd360.html",     "setdi.html",    "chauffeur", "7D",         "Permis 7D"),
    ("rejistre.html",    "vivye.html",    "chauffeur", "Vivier",     "S'inscrire au vivier"),
    ("anplwaye360.html", "anplwaye.html", "employeur", "Employeurs", "Recruter des chauffeurs"),
]

NAV_CHAUFFEUR = [
    ("index.html", "Accueil"), ("wout.html", "Test de route"),
    ("setdi.html", "Permis 7D"), ("vivye.html", "Le vivier"),
]
NAV_EMPLOYEUR = [
    ("index.html", "Accueil"), ("anplwaye.html", "Recruter"),
]


def entete(actif, cote):
    liens = NAV_CHAUFFEUR if cote == "chauffeur" else NAV_EMPLOYEUR
    lis = []
    for href, libelle in liens:
        style = ("color:var(--accent);font-weight:600" if href == actif else "color:var(--ink)")
        lis.append(f'        <li><a href="{href}" style="{style};text-decoration:none;font-size:.9rem">{libelle}</a></li>')
    autre = ('<a href="anplwaye.html" style="font-size:.82rem;color:var(--muted);text-decoration:none">Je recrute →</a>'
             if cote == "chauffeur" else
             '<a href="index.html" style="font-size:.82rem;color:var(--muted);text-decoration:none">← Je conduis</a>')
    return ('<header>\n  <nav class="nav" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.6rem">\n'
            '    <a href="index.html" class="logo"><img src="assets/brand/logo-dark-96.png" alt="Driver360" class="logo-img" />'
            'Driver<span>360</span><small>pa Atmart</small></a>\n'
            '    <ul class="nav-links" style="display:flex;gap:1.1rem;list-style:none;margin:0;padding:0;align-items:center">\n'
            + "\n".join(lis) + f'\n        <li>{autre}</li>\n'
            '    </ul>\n  </nav>\n</header>')


PIED = ('<footer>\n  <div class="container">\n'
        '    <p style="font-size:.85rem;color:var(--muted)">Driver360 — un service <a href="https://atmart.ltd" '
        'style="color:var(--accent)">Atmart LLC</a>. Massachusetts.<br />\n'
        '    Une question : <a href="mailto:sales@atmart.ltd" style="color:var(--accent)">sales@atmart.ltd</a></p>\n'
        '    <p class="footer-note">© Atmart LLC — Tous droits réservés.</p>\n'
        '  </div>\n</footer>')

# Les scripts propres a atmart.ltd n'ont rien a faire ici : ils chargent un
# service worker et un lanceur qui pointent vers l'autre site.
A_RETIRER = [
    re.compile(r'<script src="assets/launcher\.js[^"]*"></script>\s*'),
    re.compile(r'<script src="assets/share\.js[^"]*"></script>\s*'),
    re.compile(r'<script>if\("serviceWorker" in navigator\)\{navigator\.serviceWorker\.register\("/sw\.js"\);\}</script>\s*'),
]


def transformer(src_nom, dst_nom, cote):
    s = io.open(os.path.join(SOURCE, src_nom), encoding="utf-8").read()

    # 1. en-tete et pied
    s = re.sub(r"<header>.*?</header>", lambda _: entete(dst_nom, cote), s, count=1, flags=re.S)
    s = re.sub(r"<footer>.*?</footer>", lambda _: PIED, s, count=1, flags=re.S)

    # 2. les scripts de l'autre site
    for rx in A_RETIRER:
        s = rx.sub("", s)
    # le service worker de CETTE suite
    s = s.replace("</body>", '<script>if("serviceWorker" in navigator){navigator.serviceWorker.register("/sw.js");}</script>\n</body>')

    # 3. les liens internes : ceux de la suite deviennent relatifs, les autres
    #    partent en absolu vers atmart.ltd — sinon ils tombent dans le vide.
    interne = {a: b for a, b, _, _, _ in PAGES}
    for a, b in interne.items():
        s = re.sub(r'href="%s([#?][^"]*)?"' % re.escape(a),
                   lambda m: 'href="%s%s"' % (b, m.group(1) or ""), s)
    def absolu(m):
        cible = m.group(1)
        if cible in interne.values() or cible in ("index.html",):
            return m.group(0)
        return 'href="https://atmart.ltd/%s"' % cible
    s = re.sub(r'href="([a-z0-9\-]+\.html)"', absolu, s)

    # 4. le manifeste de la suite
    s = s.replace('<link rel="manifest" href="manifest.webmanifest" />',
                  '<link rel="manifest" href="manifest.webmanifest" />')
    io.open(os.path.join(RACINE, dst_nom), "w", encoding="utf-8", newline="\n").write(s)
    return len(s)


if __name__ == "__main__":
    for src, dst, cote, nom, _ in PAGES:
        n = transformer(src, dst, cote)
        print("%-20s -> %-16s %-10s %7d octets" % (src, dst, "(" + cote + ")", n))
