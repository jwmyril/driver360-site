# -*- coding: utf-8 -*-
"""
Trouve les éléments qui portent un texte écrit en dur que personne ne traduit.

    python tools/verif_ids_traduits.py     (code de sortie 1 si un défaut)

POURQUOI CE FICHIER EXISTE
--------------------------
Le 30/08/2026, en exerçant vraiment le test écrit du coach, le bouton
« Suivant ⏭ » est resté en FRANÇAIS sur la page anglaise. La clé `qzNext`
existait pourtant dans les quatre dictionnaires — quelqu'un l'avait ajoutée et
avait oublié de la brancher. Le bouton ne recevait jamais sa traduction : le
code se contentait de le montrer et de le cacher.

AUCUN DES CONTRÔLES EXISTANTS NE POUVAIT LE VOIR :
  · `verif_langue.py` lit les fichiers, pas la page en cours d'exécution ;
  · l'audit au navigateur lit la page À L'ARRÊT — or ce bouton n'apparaît
    qu'APRÈS avoir répondu à une question.

C'est la signature d'une panne d'état : le défaut n'existe que dans une
situation qu'il faut provoquer. On ne peut pas provoquer toutes les
situations ; on peut en revanche vérifier la CAUSE, qui est statique — un
élément identifié, porteur de texte, que le traducteur de la page n'assigne
jamais.

⚠️ DEUX MÉCANISMES QU'UNE RECHERCHE NAÏVE PREND POUR DES DÉFAUTS. La première
version de ce script a signalé 37 éléments dont 36 allaient très bien :

  1. LES IDENTIFIANTS CONSTRUITS. `chofe360.html` traduit une douzaine
     d'éléments par `["bg1","f1t",…].forEach(k => setTxt("cf-"+k, t[k]))`.
     L'identifiant `cf-bg1` n'existe nulle part en toutes lettres.
  2. LES CONTENEURS. Un `<label id="L-consent">` dont le `<span>` intérieur est
     traduit n'a pas besoin de l'être : son texte vient de son enfant.
     Le signaler reviendrait à demander de traduire deux fois la même phrase.

Un contrôle qui crie au loup 36 fois sur 37 ne sera plus jamais lancé. Les deux
règles sont donc dans le détecteur, pas dans la tête de qui le lit.
"""
import io
import os
import re
import sys

# La console Windows est en cp1252 : sans cette ligne, un emoji dans un libellé
# fait planter l'affichage du rapport.
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(os.path.dirname(RACINE), "Atmart_website")

# Les pages d'où Driver360 dérive ses quatre pages produit.
PAGES = ["chofe360.html", "setd360.html", "rejistre.html", "anplwaye360.html"]

# Un texte sans langue n'a pas besoin d'être traduit.
SANS_LANGUE = re.compile(r"^[\s\d\W_]*$", re.U)

# Contenus légitimement figés, avec la raison — un nom propre reste un nom
# propre dans les quatre langues.
TOLERES = {
    "cf-code": "saisie de l'utilisateur",
    "sd-code": "saisie de l'utilisateur",
    "rj-code": "saisie de l'utilisateur",
    "ep-code": "saisie de l'utilisateur",
    "rj-h1": "nom de produit : Driver Pool",
    "rj-lic": "noms de classes de permis : Class D, 7D, CDL-A...",
}

BALISES = "button|span|h1|h2|h3|h4|p|label|a|small|div|option|th|td"


def texte_visible(html):
    t = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    return " ".join(t.split())


def analyser(page):
    chemin = os.path.join(SOURCE, page)
    if not os.path.exists(chemin):
        return ["%s : introuvable" % page]
    with io.open(chemin, encoding="utf-8") as f:
        s = f.read()
    scripts = "\n".join(re.findall(r"<script[^>]*>(.*?)</script>", s, re.S))

    prefixes = set(re.findall(r"""["']([\w-]+-)["']\s*\+""", scripts))
    chaines = set(re.findall(r"""["']([\w-]+)["']""", scripts))

    def assigne(ident):
        # 1. l'identifiant est passe a une fonction qui pose du texte, ou il
        #    figure dans un TABLEAU parcouru pour en poser — d'ou le crochet
        #    fermant accepte a cote de la virgule. Sans lui, `["thl7","thcv"]`
        #    passait pour non traduit alors qu'une boucle s'en occupe.
        #    ⚠️ On n'accepte PAS la parenthese fermante : `getElementById("x")`
        #    n'est qu'une lecture, et c'est ce laxisme qui laissait passer le
        #    bouton « Suivant » a l'origine de ce script.
        if re.search(r"""["']""" + re.escape(ident) + r"""["']\s*[,\]]""", scripts):
            return True
        # 2. l'element est recupere puis rempli, parfois via une variable :
        #    `var w = getElementById("x"); ... w.innerHTML = t.cle;`
        #    On accepte si une pose de texte suit de pres dans le meme flot.
        for m in re.finditer(r"""getElementById\(\s*["']""" + re.escape(ident)
                             + r"""["']\s*\)""", scripts):
            suite = scripts[m.end():m.end() + 200]
            if re.search(r"\.(?:textContent|innerHTML|innerText)\s*=", suite):
                return True
        # 3. l'identifiant est construit : `setTxt("cf-" + k, t[k])`
        for pre in prefixes:
            if ident.startswith(pre) and ident[len(pre):] in chaines:
                return True
        return False

    out = []
    for m in re.finditer(r'<(%s)\b[^>]*\bid="([\w-]+)"[^>]*>(.*?)</\1>' % BALISES, s, re.S):
        balise, ident, dedans = m.group(1), m.group(2), m.group(3)
        txt = texte_visible(dedans)
        if not txt or SANS_LANGUE.match(txt) or len(txt) < 3 or ident in TOLERES:
            continue
        if assigne(ident):
            continue
        # Un enfant identifié et traduit suffit : le texte vient de lui.
        if any(assigne(e) for e in re.findall(r'\bid="([\w-]+)"', dedans)):
            continue
        out.append("%-18s #%-16s <%s> « %s »" % (page, ident, balise, txt[:58]))
    return out


def main():
    defauts = []
    for page in PAGES:
        defauts.extend(analyser(page))

    if defauts:
        print("%d element(s) a texte fige que rien ne traduit :\n" % len(defauts))
        for d in defauts:
            print("  - " + d)
        print("\nBrancher la cle dans applyLang de la page, et la poser dans LES")
        print("QUATRE langues. Une cle presente dans les dictionnaires mais jamais")
        print("assignee ne traduit rien : c'est exactement le defaut d'origine.")
        return 1

    print("Traductions : chaque element identifie porteur de texte est assigne.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
