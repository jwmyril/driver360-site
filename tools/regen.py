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
NL = chr(10)
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(os.path.dirname(RACINE), "Atmart_website")

# Quelle page source devient quelle page de la suite, et de quel côté du
# marché elle se range. Le côté décide de l'en-tête : on ne montre pas les
# outils du chauffeur à un employeur.
# L ORDRE COMPTE, et il n est pas alphabetique : c est celui des produits dans
# la suite, decide le 20/08/2026.
#   1. Driver Pool     — le vivier. L ACTIF : sans chauffeurs inscrits, rien
#                        d autre n a de valeur.
#   2. Driver Employer — la demande, et donc le revenu.
#   3. Driver Coach    — la preparation (test de route, 7D). C est le canal qui
#                        ALIMENTE le vivier, pas la finalite.
#
# NOMS : la SUITE s appelle Driver360 ; le coach s appelle DRIVER COACH. Les
# confondre — ce que faisait la premiere version — rendait la suite illisible :
# on ne sait plus si « Driver360 » designe le tout ou une de ses parties.
# Cet ordre se lit dans la navigation, sur l accueil et dans le sitemap.
PAGES = [
    ("rejistre.html",    "vivye.html",    "chauffeur", "Driver Pool",     "Le vivier de chauffeurs"),
    ("anplwaye360.html", "anplwaye.html", "employeur", "Driver Employer", "Recruter des chauffeurs"),
    ("chofe360.html",    "wout.html",     "chauffeur", "Driver Coach",    "Coach du test de route"),
    ("setd360.html",     "setdi.html",    "chauffeur", "Driver Coach 7D", "Permis 7D"),
]


# Le bloc pose EN TETE de la page employeur.
#
# POURQUOI. La page parcourt des viviers — « Ouvrir le pool », Class D, 7D.
# Au 20/08/2026 ces viviers sont VIDES : zero chauffeur inscrit, verifie dans
# le KV. Un employeur qui clique sur « Ouvrir le pool » ne trouve rien, et ne
# revient jamais. Plutot que de le laisser decouvrir le vide, on le dit avant,
# et on recueille sa demande — ce qui a deux vertus : on apprend qui cherche
# quoi et ou, et les chauffeurs gagnent une raison concrete de s inscrire.
#
# A RETIRER le jour ou le vivier compte de vrais chauffeurs. Pas avant.
APPEL_EMPLOYEUR = """
<section style="padding:1.6rem 0 .4rem">
  <div class="container">
    <div style="background:rgba(244,162,97,.1);border:1px solid rgba(244,162,97,.45);
      border-radius:16px;padding:1.5rem 1.7rem;max-width:820px">
      <h2 data-d3="b_titre" style="margin:0 0 .6rem;font-family:'Space Grotesk',sans-serif;color:#fff;font-size:1.24rem">The pool is still being built</h2>
      <p data-d3="b_texte" style="margin:0 0 1rem;font-size:.96rem;line-height:1.68;color:#e4dbcf;max-width:64ch">
        We have no drivers to show you yet, and we are not going to pretend otherwise: the pools
        below are empty today. Tell us instead <strong>what you are looking for</strong> — we will
        let you know as soon as a profile matches, and it tells us where to concentrate our recruiting.
      </p>
      <a class="btn btn-primary" data-d3="b_bouton" href="mailto:sales@atmart.ltd?subject=Driver360%20-%20je%20recherche%20des%20chauffeurs&amp;body=Entreprise%20%3A%0AVille%20ou%20zone%20%3A%0AType%20de%20permis%20(Class%20D%20%2F%207D)%20%3A%0ACombien%20de%20chauffeurs%20%3A%0AQuand%20%3A%0ALangues%20souhaitees%20%3A%0A%0AMerci.">Tell us what we should look for</a>
      <p data-d3="b_note" style="margin:.9rem 0 0;font-size:.84rem;color:#c9b79c">
        No commitment, and we never pass on a driver's name without their agreement.
      </p>
    </div>
  </div>
</section>
"""

# LA NAVIGATION EST EN ANGLAIS, et « Jobs » vient en premier apres l'accueil.
#
# POURQUOI L'ANGLAIS. Driver360 s'adresse a tous les residents du Massachusetts,
# pas a une communaute. Le kreyol, le francais et l'espagnol restent disponibles
# d'un clic sur chaque page — mais ils sont un AVANTAGE du produit, pas son
# identite. Une barre de navigation en francais disait le contraire.
#
# POURQUOI « JOBS » EN PREMIER. C'est ce que le visiteur est venu chercher.
# Le vivier, le coach et le portail employeur sont les moyens ; l'emploi est
# la fin. La navigation doit lire dans cet ordre-la.
# LA NAVIGATION EST UNIQUE ET LA MEME SUR LES SIX PAGES (decide le 30/08/2026).
#
# Elle etait auparavant SEPAREE par cote du marche : un chauffeur ne voyait pas
# le portail employeur, et reciproquement. L'idee se defendait, mais elle avait
# un cout : Driver Employer n'apparaissait nulle part pour qui n'etait pas deja
# du bon cote, et le produit qui RAPPORTE restait invisible. L'utilisateur a
# tranche : les trois portes se voient depuis n'importe quelle page.
#
# Chaque entree : (page, libelle anglais, cle de traduction).
# Une cle VIDE = un NOM DE PRODUIT, qui ne se traduit pas. Driver Pool reste
# Driver Pool dans les quatre langues : traduire un nom propre ferait croire a
# des produits differents selon la langue.
#
# Driver Coach ferme la marche : l'utilisateur a nomme les trois premieres, et
# on garde la quatrieme parce qu'un produit PAYANT qui n'est dans aucun menu ne
# se vend pas. Le coach 7D reste accessible depuis la page du coach.
NAV = [
    ("vivye.html",    "Driver Pool",     ""),
    ("anplwaye.html", "Driver Employer", ""),
    ("jobs.html",     "Job Postings",    "n_jobs"),
    ("wout.html",     "Driver Coach",    ""),
]

# Les pages qui appartiennent a CETTE suite : leurs liens restent relatifs.
# jobs.html n'est derivee d'aucune page d'atmart.ltd (elle est fabriquee par
# tools/gen_emplois.py), donc elle n'apparait pas dans PAGES — sans cette
# liste, `absolu()` l'enverrait sur atmart.ltd/jobs.html, qui n'existe pas.
PAGES_SUITE = {b for _, b, _, _, _ in PAGES} | {"index.html", "jobs.html"}


def entete(actif, cote=None):
    """L'en-tete de la suite.

    `cote` ne sert plus a rien depuis que la navigation est unique ; il reste
    accepte pour ne pas casser les appels existants.

    Le MENU DE LANGUE n'est pas construit ici : assets/suite.js l'ajoute dans
    cette meme <ul>. Une seule mecanique, un seul menu, sur les six pages.
    """
    lis = []
    for href, libelle, cle in NAV:
        style = ("color:var(--accent);font-weight:600" if href == actif else "color:var(--ink)")
        d3 = ' data-d3="%s"' % cle if cle else ""
        lis.append('        <li><a href="%s"%s style="%s;text-decoration:none;font-size:.9rem">%s</a></li>'
                   % (href, d3, style, libelle))
    return ('<header>' + NL + '  <nav class="nav" style="display:flex;align-items:center;'
            'justify-content:space-between;flex-wrap:wrap;gap:.6rem">' + NL
            + '    <a href="index.html" class="logo"><img src="assets/brand/logo-dark-96.png" '
              'alt="Driver360" class="logo-img" />Driver<span>360</span><small>by Atmart</small></a>' + NL
            + '    <ul class="nav-links" style="display:flex;gap:1.1rem;list-style:none;'
              'margin:0;padding:0;align-items:center">' + NL
            + NL.join(lis) + NL + '    </ul>' + NL + '  </nav>' + NL + '</header>')


PIED = """<footer>
  <div class="container">
    <p style="font-size:.85rem;color:var(--muted)"><span data-d3="f_service">Driver360 — a service by <a href="https://atmart.ltd" style="color:var(--accent)">Atmart LLC</a>. Massachusetts.</span><br />
    <span data-d3="f_question">A question</span> : <a href="mailto:sales@atmart.ltd" style="color:var(--accent)">sales@atmart.ltd</a></p>
    <p class="footer-note">© Atmart LLC — <span data-d3="f_rights">All rights reserved.</span></p>
  </div>
</footer>"""

# Les scripts propres a atmart.ltd n'ont rien a faire ici : ils chargent un
# service worker et un lanceur qui pointent vers l'autre site.
A_RETIRER = [
    re.compile(r'<script src="assets/launcher\.js[^"]*"></script>\s*'),
    re.compile(r'<script src="assets/share\.js[^"]*"></script>\s*'),
    re.compile(r'<script>if\("serviceWorker" in navigator\)\{navigator\.serviceWorker\.register\("/sw\.js"\);\}</script>\s*'),
    # i18n.js ne traduit RIEN ici : ses attributs `data-i18n` etaient TOUS dans
    # la navigation et le pied d'atmart.ltd, que cette moulinette remplace. Il
    # ne posait donc plus qu'un SECOND selecteur de langue, different de celui
    # de l'accueil — d'ou deux menus de langue selon la page. Verifie le
    # 30/08/2026 : zero `data-i18n` survit dans les quatre pages derivees.
    re.compile(r'<script src="assets/i18n\.js[^"]*"></script>\s*'),
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
    # suite.js traduit l'enveloppe (navigation, pied, bandeau) ; il doit
    # etre charge sur TOUTES les pages, sinon la page reste dans la langue
    # ecrite en dur pendant que son corps change — le melange exact que
    # l'utilisateur a signale le 30/08/2026.
    s = s.replace("</body>", '<script src="assets/suite.js?v=2"></script>\n'
                  '<script>if("serviceWorker" in navigator){navigator.serviceWorker.register("/sw.js");}</script>\n</body>')

    # 3. les liens internes : ceux de la suite deviennent relatifs, les autres
    #    partent en absolu vers atmart.ltd — sinon ils tombent dans le vide.
    interne = {a: b for a, b, _, _, _ in PAGES}
    for a, b in interne.items():
        s = re.sub(r'href="%s([#?][^"]*)?"' % re.escape(a),
                   lambda m: 'href="%s%s"' % (b, m.group(1) or ""), s)
    def absolu(m):
        cible = m.group(1)
        if cible in PAGES_SUITE:
            return m.group(0)
        return 'href="https://atmart.ltd/%s"' % cible
    s = re.sub(r'href="([a-z0-9\-]+\.html)"', absolu, s)

    # 4. la porte employeur dit la verite avant de montrer des viviers vides
    if cote == "employeur":
        s = s.replace("</header>", "</header>" + chr(10) + APPEL_EMPLOYEUR, 1)

    # 5. le manifeste de la suite
    s = s.replace('<link rel="manifest" href="manifest.webmanifest" />',
                  '<link rel="manifest" href="manifest.webmanifest" />')
    io.open(os.path.join(RACINE, dst_nom), "w", encoding="utf-8", newline="\n").write(s)
    return len(s)


if __name__ == "__main__":
    for src, dst, cote, nom, _ in PAGES:
        n = transformer(src, dst, cote)
        print("%-20s -> %-16s %-10s %7d octets" % (src, dst, "(" + cote + ")", n))
