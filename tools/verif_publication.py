# -*- coding: utf-8 -*-
"""Ce que le site publie — et ce qu'il ne doit jamais publier.

    python tools/verif_publication.py     échoue si la règle n'est plus tenue

POURQUOI (15/09/2026)
---------------------
Le dépôt driver360-site est PUBLIC sur GitHub, et GitHub Pages servait le dépôt
ENTIER : `docs/` et `tools/` compris. On y a trouvé, lisibles à une adresse
directe, la citation mot pour mot du courriel privé d'un propriétaire de DSP,
avec son nom, sa société et sa station — alors que l'autorisation de le citer
était encore demandée.

Décision de l'utilisateur (option 2) :
  1. le site ne publie ni `docs/` ni `tools/` (`_config.yml`, `exclude`) ;
  2. les documents internes — argumentaires, spécifications, notes sur des
     personnes — vivent HORS du dépôt public, dans
     `Atmart_business/driver360/`, dossier local sans dépôt distant.

CE QUE CE CONTRÔLE VÉRIFIE
  · `_config.yml` existe et exclut `docs` et `tools` ;
  · aucun `.nojekyll` : sa présence désactiverait `_config.yml`, et donc
    l'exclusion, en silence ;
  · `docs/` ne contient QUE le registre (`SUIVI_RECOMMANDATIONS.md`), dont
    l'outil `tools/etat_suivi.py` a besoin dans le dépôt.

⚠️ CE CONTRÔLE NE LISTE AUCUN NOM DE PERSONNE. Une liste de noms « interdits »
écrite ici les republierait dans le dépôt public qu'elle prétend protéger.
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                            # noqa: BLE001
    pass

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTORISES_DOCS = {"SUIVI_RECOMMANDATIONS.md"}


def main():
    fautes = []
    cfg = os.path.join(RACINE, "_config.yml")
    if not os.path.exists(cfg):
        fautes.append("_config.yml absent : GitHub Pages publie tout le depot")
    else:
        t = io.open(cfg, encoding="utf-8").read()
        for dossier in ("docs", "tools"):
            if not re.search(r"^\s*-\s*%s\s*$" % dossier, t, re.M):
                fautes.append("_config.yml n'exclut pas %s/" % dossier)
    if os.path.exists(os.path.join(RACINE, ".nojekyll")):
        fautes.append(".nojekyll present : _config.yml est ignore, docs/ et tools/ repartent en ligne")
    d = os.path.join(RACINE, "docs")
    if os.path.isdir(d):
        intrus = sorted(set(os.listdir(d)) - AUTORISES_DOCS)
        if intrus:
            fautes.append("docs/ contient des documents internes : %s — leur place est "
                          "Atmart_business/driver360/" % ", ".join(intrus))
    if fautes:
        print("     Publication : %d manquement(s)" % len(fautes))
        for f in fautes:
            print("       - " + f)
        return 1
    print("     Publication : docs/ et tools/ exclus du site ; docs/ ne garde que le registre.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
