# -*- coding: utf-8 -*-
"""
Reconstruit le site entier, dans le bon ordre, et refuse de finir s'il est cassé.

    python tools/build.py            reconstruit et contrôle
    python tools/build.py --liens    contrôle en plus les 20 liens employeurs

POURQUOI UN SEUL POINT D'ENTRÉE
-------------------------------
Il y a six étapes, et l'ORDRE compte : le thème s'applique aux pages générées,
donc il passe en dernier ; les contrôles lisent le résultat, donc après tout le
reste. Les lancer à la main, c'est en oublier un — et chacun des oublis déjà
commis (fichier de données absent, page à moitié traduite, couleur écrite en
dur) était une panne SILENCIEUSE : rien ne casse, la page s'affiche, elle
affiche juste faux.

Le code de sortie est non nul dès qu'un contrôle échoue : rien ne se publie
sur un site cassé.
"""
import io
import os
import subprocess
import sys

# ⚠️ La console Windows est en cp1252 : imprimer la sortie d'un controle qui
# contient un accent — ou le caractere de remplacement U+FFFD — y leve une
# UnicodeEncodeError. Le 31/08/2026 build.py a plante EN AFFICHANT un echec,
# et a donc rendu le code 0 : l'outil cense refuser de publier un site casse
# se cassait lui-meme au moment de le dire. On force UTF-8 en sortie.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)

# (script, arguments, description, bloquant)
ETAPES = [
    ("gen_logo.py", [], "logo et icones", True),
    ("regen.py", [], "pages derivees d'atmart.ltd + fichiers de donnees", True),
    ("gen_emplois.py", [], "page des offres", True),
    ("gen_legal.py", [], "conditions et confidentialite", True),
    ("appliquer_theme.py", [], "jetons de couleur, theme, CSP", True),
    # Le nom du cache se calcule APRES que tout est ecrit : il est l'empreinte
    # de ce qui sera reellement servi. Oublier de le changer, c'est publier
    # pour personne — les visiteurs deja venus gardent l'ancienne page. Ce
    # garde-fou reposait sur ma memoire, et ma memoire a rate deux fois.
    ("gen_sitemap.py", [], "sitemap et dates de derniere modification", True),
    ("version_cache.py", [], "nom du cache du service worker", True),
    # --- a partir d'ici, on ne fabrique plus : on verifie ---
    ("version_cache.py", ["--verifier"], "le cache correspond au contenu", True),
    ("gen_sitemap.py", ["--verifier"], "le sitemap suit le contenu", True),
    ("verif_versions.py", [], "une seule cle de cache par ressource", True),
    ("appliquer_theme.py", ["--verifier"], "aucune couleur ecrite en dur", True),
    ("verif_actifs.py", [], "aucune reference locale sans fichier", True),
    ("verif_langue.py", [], "8 pages x 4 langues coherentes", True),
    ("verif_ids_traduits.py", [], "aucun texte fige que rien ne traduit", True),
    ("verif_contraste.py", [], "contrastes AA dans les deux fonds", True),
]


def lancer(script, args, quoi):
    r = subprocess.run([sys.executable, os.path.join(ICI, script)] + args,
                       cwd=RACINE, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    sortie = (r.stdout or "").strip()
    if sortie:
        for ligne in sortie.split("\n"):
            print("     " + ligne)
    if r.returncode != 0:
        # ⚠️ LA TRACE ENTIERE, PAS SA DERNIERE LIGNE. On n'imprimait que
        # `err.split("\n")[-1]` : sur une trace Python, c'est le message
        # (« KeyError: 'ex' ») et rien d'autre. Le fichier et le numero de
        # ligne, qui sont au-dessus, etaient jetes — un build rouge ne disait
        # donc pas ou regarder, et il fallait relancer l'etape a la main pour
        # apprendre ce que le build savait deja.
        err = (r.stderr or "").rstrip()
        if err:
            for ligne in err.split("\n"):
                print("     | " + ligne)
    return r.returncode


def main():
    echecs = []
    for i, (script, args, quoi, _) in enumerate(ETAPES, 1):
        print("[%d/%d] %s" % (i, len(ETAPES) + (1 if "--liens" in sys.argv else 0), quoi))
        # Le 4e champ du tableau ne sert plus a rien : toutes les etapes
        # sont bloquantes depuis longtemps. On le garde dans le tableau
        # pour ne pas reecrire onze lignes, mais on ne le lit plus — un
        # drapeau qu'on lit sans jamais le voir varier ment sur ce que le
        # build peut faire.
        if lancer(script, args, quoi) != 0:
            echecs.append(quoi)

    if "--liens" in sys.argv:
        print("[%d] liens employeurs" % (len(ETAPES) + 1))
        if lancer("gen_emplois.py", ["--verifier"], "liens") != 0:
            echecs.append("liens employeurs")

    print("")
    if echecs:
        print("BUILD EN ECHEC : " + " | ".join(echecs))
        print("Ne rien publier tant que ce n'est pas vert.")
        return 1
    print("Build vert. Publier : git add -A && git commit && git push")
    return 0


if __name__ == "__main__":
    sys.exit(main())
