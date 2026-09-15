# -*- coding: utf-8 -*-
"""Chaque getElementById("…") d'une page vise un id qui existe dans cette page.

    python tools/verif_ids_js.py      échoue si un script cherche un élément absent

POURQUOI (15/09/2026, registre J28)
-----------------------------------
Le 31/08, le champ `rj-langs` a quitté le formulaire du vivier, mais `fill()`
continuait d'y écrire sans garde. L'exception tombait dans le `.catch` : « Petit
souci technique. Réessayez. » Pendant deux semaines, AUCUN chauffeur n'a pu
rouvrir sa fiche avec son code — ni la modifier, ni la mettre en pause, ni
proposer de nouveaux créneaux — sans qu'aucun contrôle ne bouge. Le build
était vert.

Ce contrôle ne comprend pas le JavaScript : il compare des chaînes. Un id
fabriqué à la volée (`"rj-slot" + i`) n'est pas une chaîne littérale et n'est
pas contrôlé ; un id littéral posé par un script (`innerHTML = '<p id="x">'`)
compte comme présent, puisqu'il figure dans le fichier.
"""
import glob
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                            # noqa: BLE001
    pass

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSE = re.compile(r"""(?<![\w-])id\s*=\s*\\?["']([A-Za-z0-9_-]+)""")
CHERCHE = re.compile(r"""getElementById\(\s*["']([A-Za-z0-9_-]+)["']\s*\)""")


FACULTATIFS = re.compile(r"ids-facultatifs:\s*([A-Za-z0-9_\- ]+)")


def manquants(texte):
    """Ids cherches mais absents. Un script qui teste lui-meme l'absence d'un element
    le declare dans un commentaire `ids-facultatifs: a b c` : c'est un choix ecrit,
    pas un oubli."""
    admis = set(POSE.findall(texte))
    for m in FACULTATIFS.findall(texte):
        admis |= set(m.split())
    return sorted(set(CHERCHE.findall(texte)) - admis)


def main():
    fautes = {}
    pages = sorted(glob.glob(os.path.join(RACINE, "*.html")))
    for f in pages:
        m = manquants(io.open(f, encoding="utf-8").read())
        if m:
            fautes[os.path.basename(f)] = m
    if fautes:
        print("     Ids : un script cherche un element absent de sa page")
        for page, ids in fautes.items():
            print("       - %s : %s" % (page, ", ".join(ids)))
        return 1
    print("     Ids : les %d pages ne cherchent que des elements presents." % len(pages))
    return 0


if __name__ == "__main__":
    sys.exit(main())
