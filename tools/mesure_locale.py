# -*- coding: utf-8 -*-
"""Pose le compteur d'audience sur les pages de Driver360 — et SEULEMENT d'ici.

    python tools/mesure_locale.py             pose ou corrige la balise
    python tools/mesure_locale.py --verifier  échoue si une page compte mal

POURQUOI (relecture critique du 15/09/2026, J4)
-----------------------------------------------
Le compteur commun `assets/mesure360.js` a été posé le 09/09 par
Atmart_chat_worker/tools/poser_mesure.py, avec la consigne « à relancer après
chaque build ». Personne ne l'a relancé, et le build l'a défait EN SILENCE :

  · vivye, anplwaye et setdi sont dérivées des pages d'atmart.ltd, qui portent
    `data-app="atmart"` — les visites du vivier et du portail allaient gonfler
    les chiffres d'atmart.ltd ;
  · jobs, wout, terms et privacy sont fabriquées par un générateur qui ne
    connaissait pas la balise — elles ne comptaient plus du tout.

Seul l'accueil comptait pour Driver360. Une consigne qui repose sur la mémoire
n'est pas une consigne ; c'est donc une étape du build.

⚠️ POURQUOI PAS poser_mesure.py DIRECTEMENT : il écrit sur QUATRE sites à la
fois (Driver360, Lojik360, atmart.ltd, art). Le lancer depuis le build de
Driver360 modifierait des dépôts que ce build ne publie pas. Et il ne corrige
pas une balise présente avec le mauvais nom (« déjà là », dit-il) — or c'est
exactement le défaut des pages dérivées.
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
SLUG = "driver360"
# 404.html ne se compte pas : une page d'erreur n'est pas une visite.
PAGES = ["index.html", "jobs.html", "vivye.html", "anplwaye.html", "wout.html",
         "setdi.html", "terms.html", "privacy.html"]
BALISE = '<script src="/assets/mesure360.js" data-app="%s" defer></script>' % SLUG
EXISTANTE = re.compile(r'<script src="/assets/mesure360\.js" data-app="([a-z0-9]+)" defer></script>')


def main():
    verifier = "--verifier" in sys.argv
    if not os.path.exists(os.path.join(RACINE, "assets", "mesure360.js")):
        print("     Mesure : assets/mesure360.js absent — relancer poser_mesure.py --poser une fois")
        return 1
    fautes, faits = [], []
    for page in PAGES:
        p = os.path.join(RACINE, page)
        if not os.path.exists(p):
            continue
        s = io.open(p, encoding="utf-8").read()
        m = EXISTANTE.findall(s)
        if m == [SLUG]:
            continue
        if verifier:
            fautes.append("%s (%s)" % (page, ", ".join(m) if m else "aucune balise"))
            continue
        s = EXISTANTE.sub("", s)
        s = s.replace("</body>", "  " + BALISE + "\n</body>", 1)
        io.open(p + ".tmp", "w", encoding="utf-8", newline="\n").write(s)
        os.replace(p + ".tmp", p)
        faits.append(page)
    if fautes:
        print("     Mesure : %d page(s) comptent mal : %s" % (len(fautes), " · ".join(fautes)))
        return 1
    print("     Mesure : %d page(s) comptent pour « %s »%s"
          % (len(PAGES), SLUG, (" — corrigees : " + " ".join(faits)) if faits else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
