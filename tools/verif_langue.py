# -*- coding: utf-8 -*-
"""
Contrôle qu'aucune page ne peut se retrouver à moitié traduite.

    python tools/verif_langue.py        (code de sortie 1 si un défaut)

POURQUOI CE CONTRÔLE EXISTE. Le 30/08/2026 l'utilisateur a signalé que les
pages mélangeaient les langues. La cause n'était pas une faute de traduction :
c'était que TROIS couches de langue se superposaient sans se connaître —
le corps de la page, la navigation écrite en dur en anglais, et le pied écrit
en dur en français. Chaque couche était juste ; leur somme ne l'était pas.

La panne est SILENCIEUSE par nature : rien ne casse, la page s'affiche, et
seul un lecteur de la langue concernée s'en aperçoit. D'où ce script.

CE QU'IL VÉRIFIE
  1. Chaque page charge assets/suite.js — sinon son enveloppe reste figée dans
     la langue du HTML pendant que son corps change.
  2. Toute clé `data-d3` posée dans une page existe dans LES QUATRE langues de
     suite.js. Une clé présente en anglais seulement produirait exactement le
     mélange d'origine.
  3. Les dictionnaires de l'accueil et de jobs.html (mécanisme `data-t`)
     couvrent chacun toutes les clés de leur page, dans les trois langues
     qu'ils portent — l'anglais étant celui écrit dans le HTML.
  4. Aucune page ne garde de titre d'onglet figé : le titre doit être traduit
     par le script de la page.

CE QU'IL NE VÉRIFIE PAS. La qualité des traductions, et le kreyòl en
particulier : l'autorité sur cette langue est l'utilisateur, pas ce script.
"""
import io
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGUES = ["en", "fr", "ht", "es"]
PAGES = ["index.html", "jobs.html", "vivye.html", "anplwaye.html", "wout.html", "setdi.html"]

defauts = []


def lire(nom):
    with io.open(os.path.join(RACINE, nom), encoding="utf-8") as f:
        return f.read()


def cles_suite():
    """Les clés déclarées par assets/suite.js, langue par langue."""
    s = lire(os.path.join("assets", "suite.js"))
    out = {}
    for lg in LANGUES:
        m = re.search(r"\n    %s: \{(.*?)\n    \}" % lg, s, re.S)
        if not m:
            defauts.append("suite.js : la langue « %s » est absente" % lg)
            out[lg] = set()
            continue
        out[lg] = set(re.findall(r"(\w+):", m.group(1)))
    return out


def main():
    suite = cles_suite()

    # --- 1 et 2 : l'enveloppe -------------------------------------------
    for page in PAGES:
        s = lire(page)
        if "assets/suite.js" not in s:
            defauts.append("%s : ne charge pas assets/suite.js" % page)
        for cle in sorted(set(re.findall(r'data-d3="(\w+)"', s))):
            manquantes = [lg for lg in LANGUES if cle not in suite.get(lg, set())]
            if manquantes:
                defauts.append("%s : la clé d'enveloppe « %s » manque en %s"
                               % (page, cle, ", ".join(manquantes)))

    # --- 3 : les dictionnaires inline de l'accueil et de jobs ------------
    for page in ("index.html", "jobs.html"):
        s = lire(page)
        posees = set(re.findall(r'data-t="(\w+)"', s))
        for lg in ("fr", "ht", "es"):
            m = re.search(r'\n ["\']?%s["\']?: \{(.*?)\n \}' % lg, s, re.S)
            if not m:
                defauts.append("%s : le dictionnaire « %s » est introuvable" % (page, lg))
                continue
            dispo = set(re.findall(r'"(\w+)":', m.group(1)))
            for cle in sorted(posees - dispo):
                defauts.append("%s : « %s » n'est pas traduit en %s" % (page, cle, lg))

    # --- 4 : le titre de l'onglet ----------------------------------------
    # Une page dont le titre n'est jamais reecrit garde celui du HTML : l'onglet
    # reste alors en anglais (ou en francais) quelle que soit la langue lue.
    for page in PAGES:
        s = lire(page)
        if "document.title" not in s:
            defauts.append("%s : le titre de l'onglet n'est jamais traduit" % page)

    if defauts:
        print("%d defaut(s) :\n" % len(defauts))
        for d in defauts:
            print("  - " + d)
        return 1
    print("Langues : %d pages x %d langues, enveloppe et corps coherents." % (len(PAGES), len(LANGUES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
