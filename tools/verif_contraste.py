# -*- coding: utf-8 -*-
"""
Mesure les contrastes de la palette, dans les deux fonds.

    python tools/verif_contraste.py     (code de sortie 1 si une paire echoue)

POURQUOI CE FICHIER EXISTE
--------------------------
`assets/theme.css` affirme dans ses commentaires que ses contrastes sont
« mesurés ». Ils l'étaient — mais au navigateur, à la main, un jour donné.
Une affirmation qu'aucun outil ne rejoue est une affirmation qui se périme au
premier ajustement de couleur, et le fichier renvoyait vers un script qui
n'existait pas encore. Le voici.

CE QU'IL VÉRIFIE. Les paires texte/fond que la maquette utilise réellement,
dans les deux thèmes, contre le seuil AA du WCAG : **4,5:1** pour le texte
courant, **3:1** pour les grands titres et les éléments non textuels utiles.

CE QU'IL NE REMPLACE PAS. La mesure dans le navigateur, qui seule voit les
superpositions réelles (une carte translucide sur un dégradé). Les deux se
complètent : celui-ci attrape une régression de palette en une seconde, sans
lancer quoi que ce soit.
"""
import io
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEME = os.path.join(RACINE, "assets", "theme.css")

AA_TEXTE = 4.5
AA_GRAND = 3.0

# (jeton du texte, jeton du fond, seuil, a quoi ca sert)
# Les fonds translucides sont donnes par leur RESULTAT sur le fond de page :
# comparer un texte a `rgba(255,255,255,.045)` n'aurait aucun sens.
PAIRES = [
    ("--d-fort", "--d-fond", AA_GRAND, "titres sur la page"),
    ("--d-texte", "--d-fond", AA_TEXTE, "texte courant sur la page"),
    ("--d-doux", "--d-fond", AA_TEXTE, "texte secondaire sur la page"),
    ("--d-faible", "--d-fond", AA_TEXTE, "mentions discretes sur la page"),
    ("--d-accent", "--d-fond", AA_TEXTE, "liens sur la page"),
    ("--d-bleu", "--d-fond", AA_TEXTE, "liens employeur sur la page"),
    ("--d-alerte", "--d-fond", AA_TEXTE, "avertissements sur la page"),
    ("--d-vert", "--d-fond", AA_TEXTE, "reussite sur la page"),
    ("--d-danger", "--d-fond", AA_TEXTE, "echec sur la page"),
    ("--d-accent-encre", "--d-accent", AA_TEXTE, "texte d'un bouton plein"),
    # Sur fond clair, les cartes sont d'un blanc franc : c'est la que vivent
    # la plupart des liens, et c'est le fond le plus exigeant.
    ("--d-accent", "--d-surface", AA_TEXTE, "liens dans une carte"),
    ("--d-texte", "--d-surface", AA_TEXTE, "texte dans une carte"),
    ("--d-faible", "--d-surface", AA_TEXTE, "mentions dans une carte"),
]


def hexa(v):
    v = v.strip().lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))


def couleurs(bloc, sur_fond):
    """Les jetons d'un bloc CSS, resolus en RVB.

    Les valeurs translucides sont aplaties SUR le fond de page : c'est ce que
    l'oeil voit, et donc ce qu'il faut mesurer.
    """
    out = {}
    for nom, val in re.findall(r"(--d-[\w-]+)\s*:\s*([^;]+);", bloc):
        val = val.split("/*")[0].strip()
        m = re.match(r"rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*(?:,\s*([\d.]+)\s*)?\)", val)
        if m:
            r, g, b = (float(m.group(i)) for i in (1, 2, 3))
            a = float(m.group(4)) if m.group(4) else 1.0
            out[nom] = tuple(c * a + f * (1 - a) for c, f in zip((r, g, b), sur_fond))
        elif val.startswith("#"):
            out[nom] = hexa(val)
    return out


def luminance(c):
    def canal(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (canal(x) for x in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def rapport(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def bloc(css, selecteur):
    m = re.search(re.escape(selecteur) + r"\s*\{(.*?)\n\}", css, re.S)
    return m.group(1) if m else ""


def main():
    with io.open(THEME, encoding="utf-8") as f:
        css = f.read()

    echecs = []
    for nom, selecteur in (("sombre", ":root"), ("clair", ".clair")):
        brut = bloc(css, selecteur)
        if not brut:
            print("Bloc %s introuvable dans theme.css" % selecteur)
            return 1
        # premiere passe pour connaitre le fond, seconde pour aplatir dessus
        fond = couleurs(brut, (0, 0, 0)).get("--d-fond", (0, 0, 0))
        jetons = couleurs(brut, fond)

        print("\n--- fond %s" % nom)
        for texte, dessous, seuil, quoi in PAIRES:
            if texte not in jetons or dessous not in jetons:
                continue
            r = rapport(jetons[texte], jetons[dessous])
            ok = r >= seuil
            if not ok:
                echecs.append("%s : %s sur %s = %.2f:1 (il faut %.1f) — %s"
                              % (nom, texte, dessous, r, seuil, quoi))
            print("  %s %-18s sur %-14s %5.2f:1  %s"
                  % ("ok  " if ok else "FAUX", texte, dessous, r, quoi))

    print("")
    if echecs:
        print("%d paire(s) sous le seuil :" % len(echecs))
        for e in echecs:
            print("  - " + e)
        print("\nCorriger le JETON dans assets/theme.css, pas la regle qui l'utilise :")
        print("sinon la correction ne vaut que pour un endroit.")
        return 1
    print("Contrastes : toutes les paires tiennent le seuil AA, dans les deux fonds.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
