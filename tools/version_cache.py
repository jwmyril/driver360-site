# -*- coding: utf-8 -*-
"""Nomme le cache du service worker d'apres le contenu publie.

    python tools/version_cache.py            met a jour sw.js
    python tools/version_cache.py --verifier  echoue si sw.js est en retard

POURQUOI CE FICHIER EXISTE
--------------------------
Le service worker sert ce qu'il a en cache tant que le NOM du cache ne change
pas. Oublier de le changer apres une modification, c'est publier pour personne :
les visiteurs deja venus gardent l'ancienne page, parfois des jours.

Le README appelait cet oubli fatal, et le seul garde-fou etait un humain qui
se souvient. Ca a rate au moins deux fois. Le nom est donc calcule.

CE QU'ON HACHE : ce que le visiteur telecharge vraiment — les pages, la
feuille de style, les scripts, les donnees du coach. Pas les outils du build :
changer un commentaire dans un script Python ne doit purger le cache de
personne.
"""
import hashlib
import io
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SERVIS = [
    "index.html", "jobs.html", "vivye.html", "anplwaye.html", "wout.html",
    "setdi.html", "terms.html", "privacy.html", "404.html",
    "assets/style.css", "assets/theme.css", "assets/suite.js",
    "assets/script.js", "assets/komand.json", "assets/pemi-questions.json",
    "manifest.webmanifest",
]


def empreinte():
    """Huit caracteres qui changent si et seulement si le contenu change."""
    h = hashlib.sha256()
    for nom in sorted(SERVIS):
        p = os.path.join(RACINE, nom)
        if not os.path.exists(p):
            continue
        h.update(nom.encode("utf-8"))
        with io.open(p, "rb") as f:
            h.update(f.read())
    return h.hexdigest()[:8]


def main():
    verifier = "--verifier" in sys.argv
    p = os.path.join(RACINE, "sw.js")
    s = io.open(p, encoding="utf-8").read()
    m = re.search(r'const CACHE = "([^"]+)"', s)
    if not m:
        print("     sw.js : ligne CACHE introuvable")
        return 1

    voulu = "driver360-" + empreinte()
    if m.group(1) == voulu:
        print("     Cache : %s — a jour" % voulu)
        return 0
    if verifier:
        print("     Cache : sw.js dit %s, le contenu vaut %s" % (m.group(1), voulu))
        print("     Les visiteurs deja venus garderaient l'ancienne version.")
        return 1

    s = s[:m.start(1)] + voulu + s[m.end(1):]
    tmp = p + ".tmp"
    io.open(tmp, "w", encoding="utf-8", newline="\n").write(s)
    os.replace(tmp, p)
    print("     Cache : %s -> %s" % (m.group(1), voulu))
    return 0


if __name__ == "__main__":
    sys.exit(main())
