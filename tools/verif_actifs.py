# -*- coding: utf-8 -*-
"""
Refuse toute référence locale qui ne correspond à aucun fichier.

    python tools/verif_actifs.py        (code de sortie 1 si un manque)

POURQUOI CE CONTRÔLE EXISTE
---------------------------
Le 30/08/2026, l'utilisateur signale une section restée en français sur la
page anglaise du coach. La traduction n'était pas en cause : la section se
traduit toute seule dans `paint()`, mais cette fonction commence par
`if(!DATA) return;` — et `DATA` vient d'un `fetch("assets/komand.json")`.

Ce fichier n'avait jamais été copié depuis le dépôt d'atmart.ltd. La panne
était donc DOUBLE, et la seconde moitié était la plus grave :

  1. le module gardait le français écrit en dur dans le HTML, quelle que soit
     la langue — c'est ce qui se voyait ;
  2. et LES EXERCICES NE FONCTIONNAIENT PAS DU TOUT. Ce n'était pas un défaut
     de traduction, c'était une fonctionnalité absente. Personne ne l'avait vu
     parce qu'une page qui ne charge pas ses données ne casse pas : elle se
     contente d'afficher moins.

LA LEÇON, ET LA RAISON DE CE FICHIER. Une ressource manquante est une panne
SILENCIEUSE : rien ne rougit, la page s'affiche, et seul quelqu'un qui connaît
la fonctionnalité s'aperçoit qu'elle a disparu. Un contrôle automatique est le
seul moyen fiable de l'attraper.

CE QU'IL VÉRIFIE
  · chaque `src=` et `href=` relatif d'une page publiée pointe sur un fichier
    qui existe (les pages .html incluses) ;
  · chaque `fetch("assets/…")` d'une page publiée aussi.

CE QU'IL NE VÉRIFIE PAS. Les liens externes — c'est le travail de
`gen_emplois.py --verifier`, qui les ouvre vraiment.
"""
import io
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGES = ["index.html", "jobs.html", "vivye.html", "anplwaye.html", "wout.html",
         "setdi.html", "terms.html", "privacy.html", "404.html"]

# `src`/`href` relatifs, puis les chargements de données faits en JavaScript.
MOTIFS = [
    re.compile(r'(?:src|href)="((?!https?:|mailto:|tel:|data:|javascript:|#|/)[^"]+)"'),
    re.compile(r'fetch\("((?!https?:)assets/[^"]+)"'),
]

# Une chaîne construite en JavaScript (`' + s.cv + '`) ressemble à un chemin
# sans en être un. On écarte tout ce qui contient un signe de concaténation.
BRUIT = re.compile(r"[+'{}<>]|\s")


def main():
    manques = {}
    for page in PAGES:
        chemin = os.path.join(RACINE, page)
        if not os.path.exists(chemin):
            manques.setdefault(page, []).append("(la page elle-même)")
            continue
        with io.open(chemin, encoding="utf-8") as f:
            s = f.read()
        for motif in MOTIFS:
            for brut in motif.findall(s):
                cible = brut.split("?")[0].split("#")[0]
                if not cible or BRUIT.search(cible):
                    continue
                if not os.path.exists(os.path.join(RACINE, cible)):
                    manques.setdefault(cible, []).append(page)

    if manques:
        print("%d reference(s) sans fichier :\n" % len(manques))
        for cible, pages in sorted(manques.items()):
            print("  - %-28s reclame par %s" % (cible, ", ".join(sorted(set(pages)))))
        print("\nSi c'est un fichier de donnees d'atmart.ltd, l'ajouter a DONNEES")
        print("dans tools/regen.py, puis relancer `python tools/regen.py`.")
        return 1

    print("Actifs : toutes les references locales des %d pages existent." % len(PAGES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
