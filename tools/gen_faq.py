# -*- coding: utf-8 -*-
"""Déduit `FAQPage` et `Course` de ce que la page AFFICHE (ligne G12).

    python tools/gen_faq.py            pose le balisage
    python tools/gen_faq.py --verifier échoue s'il ne correspond plus

POURQUOI CE FICHIER EXISTE
--------------------------
Google demande que le contenu d'un `FAQPage` soit **visible par le visiteur**.
Un balisage qui décrit des questions absentes de la page est un faux, et c'est
la première chose qu'un moteur sanctionne.

On ne l'écrit donc pas à côté de la page : **on le lit dans la page**. Les
questions et les réponses sont extraites des `<details class="faq-q">` de la
page déjà construite — donc déjà passée en anglais par `rendre_en`. Si
quelqu'un corrige une réponse, le balisage suit au build suivant, sans que
personne ait à y penser. Les deux ne peuvent pas diverger : il n'y a qu'une
source.

CE QUE `Course` DIT, ET CE QU'IL NE DIT PAS
-------------------------------------------
Il dit : le nom, ce que ça enseigne, qui le fournit, en quelles langues, et
que **c'est gratuit** — parce que la page dit « Gratuit (WOUT-XXXX-XXXX) ».

⚠️ IL NE DIT PAS `educationalCredentialAwarded`. Ces coachs ne délivrent aucun
titre : c'est le RMV qui délivre le permis et le certificat. Le déclarer ferait
du balisage exactement la chose que le site refuse d'être partout ailleurs —
un organisme de formation qui laisse croire qu'il certifie.

⚠️ IL N'Y A PAS DE `JobPosting` sur jobs.html, et il ne doit pas y en avoir :
la page ne republie aucune annonce.
"""
import html
import io
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                            # noqa: BLE001
    pass

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://driver360.atmart.ltd"

# Ce que chaque coach enseigne. Factuel, et repris de la page elle-même.
COURS = {
    "wout.html": {
        "nom": "Driver Coach — Massachusetts Class D road test",
        "enseigne": ["Massachusetts Class D road test",
                     "the examiner's English commands",
                     "the written permit exam"],
    },
    "setdi.html": {
        "nom": "7D Pro — Massachusetts school pupil transport (7D) written exam",
        "enseigne": ["Massachusetts 7D certificate rules",
                     "school pupil transport vehicle rules",
                     "the 7D written exam"],
    },
}

# Les guillemets sont SIMPLES ou DOUBLES selon le chemin : le balisage ecrit a
# la main en porte des doubles, celui que la page injecte depuis son
# dictionnaire en porte des simples (une chaine JavaScript ne peut pas
# contenir ses propres guillemets). Le motif accepte les deux, sinon il ne
# trouve rien sur la page CONSTRUITE — c'est-a-dire sur la seule qui compte.
FAQ = re.compile(
    r"""<details class=['"]faq-q['"]><summary>(.*?)</summary>"""
    r"""<div class=['"]faq-r['"]>(.*?)</div></details>""", re.S)

MARQUE = "<!-- donnees structurees : gen_faq.py -->"
BLOC = re.compile(re.escape(MARQUE) + r".*?" + re.escape(MARQUE), re.S)


def texte(h):
    """Le texte que le visiteur lit, sans les balises."""
    return html.unescape(re.sub(r"<[^>]+>", "", h)).strip()


def descr(t):
    m = re.search(r'<meta name="description"[^>]*content="([^"]*)"', t)
    return html.unescape(m.group(1)) if m else ""


def titre(t):
    m = re.search(r"<title[^>]*>(.*?)</title>", t, re.S)
    return html.unescape(m.group(1)).strip() if m else ""


SCRIPT = re.compile(r"<script\b.*?</script>", re.S | re.I)
CONTENEUR = re.compile(r'<div id="(?:cf|sd)-faq"[^>]*>(.*?)</div></div></section>', re.S)


def visible(t):
    """Le seul endroit qui compte : le bloc FAQ que le visiteur voit.

    ⚠️ ON RETIRE D'ABORD LES <script>. La page porte ses quatre traductions
    dans un dictionnaire JavaScript, et chacune contient les mêmes
    `<details class='faq-q'>`. Sans ce filtre, le balisage annonçait
    **50 questions** au lieu de 10 — les mêmes cinq, répétées en quatre
    langues, décrites comme si elles étaient toutes affichées. C'est
    exactement le faux que ce fichier existe pour empêcher, et il l'a produit
    à sa première exécution.
    """
    sans = SCRIPT.sub("", t)
    m = CONTENEUR.search(sans)
    return m.group(1) if m else ""


def balisage(page, t):
    qr = FAQ.findall(visible(t))
    if not qr:
        return None, 0

    url = SITE + "/" + page
    blocs = [{
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{
            "@type": "Question",
            "name": texte(q),
            "acceptedAnswer": {"@type": "Answer", "text": texte(r)},
        } for q, r in qr],
    }]

    c = COURS.get(page)
    if c:
        blocs.append({
            "@context": "https://schema.org",
            "@type": "Course",
            "name": c["nom"],
            "description": descr(t) or titre(t),
            "url": url,
            "provider": {"@type": "Organization", "name": "Atmart LLC",
                         "url": SITE + "/"},
            "teaches": c["enseigne"],
            "inLanguage": ["en", "es", "ht", "fr"],
            "isAccessibleForFree": True,
            "hasCourseInstance": {
                "@type": "CourseInstance",
                "courseMode": "online",
                "courseWorkload": "PT30M",
            },
        })

    out = [MARQUE]
    for b in blocs:
        out.append('<script type="application/ld+json">%s</script>'
                   % json.dumps(b, ensure_ascii=False, indent=1))
    out.append(MARQUE)
    return "\n  ".join(out), len(qr)


def main():
    verifier = "--verifier" in sys.argv
    total, retard = 0, []

    for page in ("wout.html", "setdi.html"):
        p = os.path.join(RACINE, page)
        if not os.path.exists(p):
            continue
        t = io.open(p, encoding="utf-8").read()
        bloc, n = balisage(page, t)
        if bloc is None:
            print("     !! %s : aucune question trouvee dans la page" % page)
            return 1
        total += n

        if BLOC.search(t):
            neuf = BLOC.sub(lambda _m: bloc, t, count=1)
        else:
            i = t.lower().find("</head>")
            if i < 0:
                print("     !! %s : pas de </head>" % page)
                return 1
            neuf = t[:i] + "  " + bloc + "\n" + t[i:]

        if neuf == t:
            continue
        if verifier:
            retard.append(page)
            continue
        io.open(p + ".tmp", "w", encoding="utf-8", newline="\n").write(neuf)
        os.replace(p + ".tmp", p)

    if verifier and retard:
        print("     FAQ : le balisage ne correspond plus a la page (%s)"
              % " ".join(retard))
        print("     Un FAQPage qui decrit des questions absentes est un faux.")
        return 1
    print("     FAQ : %d question(s) balisees, sur 2 pages, deduites du visible"
          % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
