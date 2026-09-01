# -*- coding: utf-8 -*-
"""Fabrique sitemap.xml, avec des dates qui disent la verite.

    python tools/gen_sitemap.py             ecrit sitemap.xml
    python tools/gen_sitemap.py --verifier   echoue s'il est en retard

POURQUOI CE FICHIER EXISTE
--------------------------
Le sitemap etait ecrit a la main. Consequences mesurees le 30/08/2026 : six
`lastmod` perimes, et une neuvieme page n'y serait jamais entree parce que
personne n'aurait pense a l'ajouter.

Un `lastmod` faux est pire qu'absent. Un moteur qui revient sur une date
inchangee ne relit pas la page ; une date avancee sans raison lui fait
gaspiller son passage et lui apprend a ne plus vous croire.

COMMENT LA DATE EST DECIDEE
---------------------------
On garde l'empreinte de chaque page dans `tools/sitemap_dates.json`. Tant que
l'empreinte ne bouge pas, la date ne bouge pas. Elle passe a aujourd'hui le
jour ou le contenu change reellement — pas a chaque build, sinon on
reannoncerait neuf pages modifiees chaque fois qu'on corrige une virgule dans
un script Python.

⚠️ ON HACHE LA PAGE SANS SA CSP. `appliquer_theme.py` recalcule les empreintes
SHA-256 des scripts a chaque passage ; si la CSP entrait dans le hachage, la
moindre reconstruction ferait « changer » les neuf pages.

⚠️ 404.html N'EST PAS DANS LE SITEMAP. On n'invite pas un moteur a indexer une
page d'erreur.
"""
import datetime
import hashlib
import io
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ETAT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sitemap_dates.json")
SITE = "https://driver360.atmart.ltd"

# (fichier, priorite). L'ordre est celui du sitemap.
PAGES = [
    ("index.html", "1.0"),
    ("jobs.html", "0.9"),
    ("vivye.html", "0.9"),
    ("anplwaye.html", "0.9"),
    ("wout.html", "0.8"),
    ("setdi.html", "0.8"),
    ("terms.html", "0.3"),
    ("privacy.html", "0.3"),
]

CSP = re.compile(r'<meta http-equiv="Content-Security-Policy"[^>]*>')


def empreinte(nom):
    p = os.path.join(RACINE, nom)
    if not os.path.exists(p):
        return None
    t = io.open(p, encoding="utf-8").read()
    return hashlib.sha256(CSP.sub("", t).encode("utf-8")).hexdigest()[:16]


def xml(dates):
    l = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for nom, prio in PAGES:
        if empreinte(nom) is None:
            continue
        url = SITE + ("/" if nom == "index.html" else "/" + nom)
        l.append('  <url><loc>%s</loc><lastmod>%s</lastmod>'
                 '<priority>%s</priority></url>' % (url, dates[nom], prio))
    l.append("</urlset>")
    return "\n".join(l) + "\n"


def main():
    verifier = "--verifier" in sys.argv
    aujourdhui = datetime.date.today().isoformat()

    etat = {}
    if os.path.exists(ETAT):
        try:
            etat = json.load(io.open(ETAT, encoding="utf-8"))
        except ValueError:
            etat = {}

    dates, changees = {}, []
    for nom, _ in PAGES:
        e = empreinte(nom)
        if e is None:
            continue
        vu = etat.get(nom) or {}
        if vu.get("h") == e and vu.get("d"):
            dates[nom] = vu["d"]
        else:
            dates[nom] = aujourdhui
            changees.append(nom)
            etat[nom] = {"h": e, "d": aujourdhui}

    voulu = xml(dates)
    p = os.path.join(RACINE, "sitemap.xml")
    actuel = io.open(p, encoding="utf-8").read() if os.path.exists(p) else ""

    if verifier:
        if actuel == voulu:
            print("     Sitemap : %d page(s), a jour" % len(dates))
            return 0
        print("     Sitemap : en retard sur le contenu publie")
        return 1

    for f, s in ((p, voulu), (ETAT, json.dumps(etat, indent=1, sort_keys=True) + "\n")):
        io.open(f + ".tmp", "w", encoding="utf-8", newline="\n").write(s)
        os.replace(f + ".tmp", f)

    print("     Sitemap : %d page(s)%s" % (
        len(dates),
        (" — date avancee pour %s" % " ".join(changees)) if changees else ", aucune date changee"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
