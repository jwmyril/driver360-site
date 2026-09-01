# -*- coding: utf-8 -*-
"""Une ressource, une seule cle de cache.

    python tools/verif_versions.py

POURQUOI CE FICHIER EXISTE
--------------------------
Le `?v=` d'une ressource decide de ce que le navigateur ressert. Il est ecrit
a la main, a plusieurs endroits : dans les pages, dans `regen.py`, dans
`gen_emplois.py`, dans `gen_legal.py`, dans `appliquer_theme.py`. Rien ne
garantissait qu'ils disent tous la meme chose.

CE QUI S'EST PASSE, DEUX FOIS :

  · le 31/08/2026 au matin, `suite.js` avait gagne des cles de traduction et
    gardait `?v=4`. J'ai cru dix minutes que le menu de langue etait casse ;
    le navigateur servait simplement l'ancien fichier ;

  · le meme jour, `style.css` etait appele SANS `?v=` sur cinq pages et avec
    `?v=32` sur quatre. Apres une modification du CSS, l'accueil et la page
    des offres servaient l'ancienne feuille depuis le cache du navigateur,
    pendant que les autres pages servaient la nouvelle. Le site n'etait pas
    seulement perime : il etait perime a moitie, ce qui est plus difficile a
    voir et beaucoup plus difficile a croire.

Ce controle refuse les deux : chaque ressource doit etre appelee partout avec
la MEME cle, et aucune ne doit etre appelee sans cle.

⚠️ CE N'EST PAS LE CACHE DU SERVICE WORKER. Celui-la est nomme par
`tools/version_cache.py`, et son nom est calcule. Ici on parle du cache du
NAVIGATEUR, qui obeit a l'URL — donc au `?v=`.
"""
import io
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGES = ["index.html", "jobs.html", "vivye.html", "anplwaye.html", "wout.html",
         "setdi.html", "terms.html", "privacy.html", "404.html"]

# Les ressources qui DOIVENT porter une cle : leur contenu change avec le site.
VERSIONNEES = ("style.css", "theme.css", "suite.js", "script.js")

APPEL = re.compile(r'(?:href|src)="/?assets/([A-Za-z0-9_.-]+)(\?v=([0-9]+))?"')


def main():
    vues = {}       # fichier -> {cle: [pages]}
    sans = {}       # fichier -> [pages]

    for page in PAGES:
        p = os.path.join(RACINE, page)
        if not os.path.exists(p):
            continue
        t = io.open(p, encoding="utf-8").read()
        for m in APPEL.finditer(t):
            nom, cle = m.group(1), m.group(3)
            if nom not in VERSIONNEES:
                continue
            if cle is None:
                sans.setdefault(nom, []).append(page)
            else:
                vues.setdefault(nom, {}).setdefault(cle, []).append(page)

    fautes = []
    for nom, cles in sorted(vues.items()):
        if len(cles) > 1:
            fautes.append("%s : %d cles concurrentes — %s" % (
                nom, len(cles),
                " · ".join("?v=%s sur %d page(s)" % (k, len(v))
                           for k, v in sorted(cles.items()))))
    for nom, pages in sorted(sans.items()):
        fautes.append("%s : appele SANS cle sur %d page(s) — %s" % (
            nom, len(pages), " ".join(pages)))

    if fautes:
        print("     Versions : %d probleme(s)" % len(fautes))
        for f in fautes:
            print("       !! " + f)
        print("     Une ressource appelee avec deux cles rend le site perime")
        print("     A MOITIE — plus dur a voir qu'une panne franche.")
        return 1

    resume = " · ".join("%s ?v=%s" % (n, list(c)[0]) for n, c in sorted(vues.items()))
    print("     Versions : une seule cle par ressource — %s" % resume)
    return 0


if __name__ == "__main__":
    sys.exit(main())
