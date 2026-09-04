# -*- coding: utf-8 -*-
"""L'exemple du portail employeur doit décrire le tableau qui existe.

    python tools/verif_exemple.py      échoue si l'exemple a dérivé

POURQUOI CE FICHIER EXISTE
--------------------------
Le bloc « ce que vous voyez avant de payer » est du HTML écrit à la main qui
reproduit un tableau que le code rend ailleurs. Deux vérités pour une seule
chose : elles divergent dès qu'on touche à l'une.

Elles ont divergé. Le 04/09/2026, après l'ajout du bassin DSP et de la colonne
d'ancienneté, le vrai tableau comptait **huit** colonnes et l'exemple en
montrait **six** — sans badge DSP-ready, sans colonne DSP. Un propriétaire de
DSP le regardait et n'y voyait rien de ce qui le concerne : exactement
l'argument qu'on veut lui faire. C'est l'utilisateur qui l'a vu, pas le build.

⚠️ CE CONTRÔLE NE VÉRIFIE PAS QUE L'EXEMPLE EST JOLI. Il vérifie qu'il ne MENT
pas : même nombre de colonnes que le tableau réel, et les deux nouveautés
citées. Un exemple qui décrit un produit qu'on n'a plus est pire qu'aucun
exemple — il promet une chose et en livre une autre.
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
PAGE = os.path.join(RACINE, "anplwaye.html")


def colonnes_du_vrai_tableau(t):
    """Les <th> du bassin licencié — la référence."""
    m = re.search(r'<table class="ep-t" id="ep-t-lic">\s*<thead>(.*?)</thead>', t, re.S)
    if not m:
        return None
    return len(re.findall(r"<th\b", m.group(1)))


def colonnes_de_l_exemple(t):
    m = re.search(r'id="ep-demo"[^>]*>(.*?)</table>', t, re.S)
    if not m:
        return None
    return len(re.findall(r"<th\b", m.group(1)))


def main():
    if not os.path.exists(PAGE):
        print("     anplwaye.html absente — rien a verifier")
        return 0
    t = io.open(PAGE, encoding="utf-8").read()

    vrai = colonnes_du_vrai_tableau(t)
    ex = colonnes_de_l_exemple(t)
    if vrai is None or ex is None:
        print("     !! tableau introuvable (vrai=%s, exemple=%s)" % (vrai, ex))
        return 1

    ennuis = []
    if vrai != ex:
        ennuis.append("l'exemple montre %d colonne(s), le tableau reel en a %d"
                      % (ex, vrai))

    bloc = re.search(r'id="ep-demo"[^>]*>(.*?)</table>', t, re.S).group(1)
    if "DSP-ready" not in bloc:
        ennuis.append("aucun badge « DSP-ready » dans l'exemple, alors que le "
                      "produit en pose un")
    if not re.search(r"<th\b[^>]*>\s*DSP\s*</th>", bloc):
        ennuis.append("aucune colonne « DSP » dans l'exemple, alors que le "
                      "tableau en a une")

    # ⚠️ L'exemple doit rester UN EXEMPLE, et le dire.
    if "EXEMPLE" not in bloc.upper() and "EGZANP" not in bloc.upper() \
            and "EJEMPLO" not in bloc.upper() and "EXAMPLE" not in bloc.upper():
        ennuis.append("l'exemple ne se declare plus comme un exemple : sans ce "
                      "mot, ce sont deux faux profils presentes comme vrais")

    if ennuis:
        print("     L'exemple du portail employeur a derive :")
        for e in ennuis:
            print("       - " + e)
        print("     Un exemple qui decrit un produit qu'on n'a plus promet une")
        print("     chose et en livre une autre.")
        return 1

    print("     Exemple employeur : %d colonnes, comme le tableau reel ; "
          "badge et colonne DSP presents." % ex)
    return 0


if __name__ == "__main__":
    sys.exit(main())
