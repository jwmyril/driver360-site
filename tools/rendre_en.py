# -*- coding: utf-8 -*-
"""Rend le balisage des pages produit EN ANGLAIS, au moment du build.

Le probleme, tel qu'il se voit vraiment :

  Les quatre pages produit naissent en francais. Le balisage porte le
  francais, un voile cache la page, `applyLang()` la traduit, le voile se
  leve. Un visiteur avec JavaScript ne voit jamais le francais.

  Mais `<html lang="fr">` restait ecrit, et le corps aussi. Un moteur
  d'indexation lit du francais. Un lecteur d'ecran annonce du francais et le
  prononce a la francaise. Et quiconque perd le script — reseau coupe en
  cours de chargement, extension trop zelee, navigateur ancien — reste devant
  un voile qui ne se levera pas.

CE QUE FAIT CE MODULE. Il execute le script DE LA PAGE (voir rendre_en.mjs)
avec un DOM d'enregistrement, note quel element recoit quel texte anglais,
puis pose ces textes dans le balisage. La traduction n'est donc pas devinee :
elle vient de la page elle-meme, par le meme chemin qu'au navigateur.

⚠️ ON NE REANALYSE PAS LE DOCUMENT. Les remplacements sont chirurgicaux, sur
la chaine. Une reserialisation par un analyseur HTML toucherait aux scripts en
ligne — et leurs empreintes SHA-256 sont ce sur quoi repose la CSP.
"""
import io
import json
import os
import re
import subprocess
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDES = {"input", "img", "br", "hr", "meta", "link", "source", "area", "col"}


def zones_script(html):
    """Les intervalles occupes par du script : on n'y cherche aucun id."""
    return [(m.start(), m.end())
            for m in re.finditer(r"<script\b[^>]*>.*?</script>", html, re.S | re.I)]


def dans_script(zones, i):
    return any(a <= i < b for a, b in zones)


def echapper(v):
    return v.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def interieur(html, ident, zones):
    """(debut, fin, nom_de_balise) du contenu de l'element portant cet id."""
    motif = re.compile(r'<([a-zA-Z][\w-]*)\b[^>]*?\sid="%s"' % re.escape(ident))
    for m in motif.finditer(html):
        if dans_script(zones, m.start()):
            continue
        nom = m.group(1).lower()
        if nom in VIDES:
            return None
        i = html.find(">", m.end())
        if i < 0 or html[i - 1] == "/":
            return None
        debut, prof, j = i + 1, 1, i + 1
        bal = re.compile(r"<(/?)%s\b" % re.escape(nom), re.I)
        while prof:
            k = bal.search(html, j)
            if not k:
                return None
            if k.group(1):
                prof -= 1
                if prof == 0:
                    return debut, k.start(), nom
            else:
                f = html.find(">", k.end())
                if f < 0:
                    return None
                if html[f - 1] != "/":
                    prof += 1
            j = k.end()
    return None


def poser(html, ident, mode, valeur):
    zones = zones_script(html)
    p = interieur(html, ident, zones)
    if not p:
        return html, False
    debut, fin, _ = p
    v = valeur if mode == "innerHTML" else echapper(valeur)
    return html[:debut] + v + html[fin:], True


def poser_options(html, ident, rangs):
    zones = zones_script(html)
    p = interieur(html, ident, zones)
    if not p:
        return html, 0
    debut, fin, _ = p
    bloc = html[debut:fin]
    n = 0

    compteur = {"i": -1}

    def une(m):
        compteur["i"] += 1
        t = rangs.get(str(compteur["i"]))
        if t is None:
            return m.group(0)
        return m.group(1) + echapper(t) + m.group(3)

    bloc2, _c = re.subn(r"(<option\b[^>]*>)(.*?)(</option>)", une, bloc, flags=re.S | re.I)
    n = sum(1 for k in rangs if int(k) <= compteur["i"])
    return html[:debut] + bloc2 + html[fin:], n


def poser_titre(html, titre, descr):
    faits = 0
    if titre:
        h, ok = re.subn(r"(<title\b[^>]*>).*?(</title>)",
                        lambda m: m.group(1) + echapper(titre) + m.group(2),
                        html, count=1, flags=re.S | re.I)
        html, faits = h, faits + ok
    if descr:
        def rempl(m):
            return re.sub(r'content="[^"]*"', 'content="%s"' % descr.replace('"', "&quot;"),
                          m.group(0))
        h, ok = re.subn(r'<meta\s+name="description"[^>]*>', rempl, html, count=1, flags=re.I)
        html, faits = h, faits + ok
    return html, faits


def poser_langue(html):
    """`lang="en"`, replis anglais, et le voile qui change de camp."""
    n = 0
    html, k = re.subn(r'<html lang="[a-z-]+"', '<html lang="en"', html, count=1)
    n += k
    # Le repli de `lang()` : il restait au francais DANS LE CORPS de la page,
    # alors que l'entete avait deja bascule a l'anglais. Une langue absente du
    # dictionnaire — de l'allemand, du portugais — retombait donc en francais.
    html, k = re.subn(r'(document\.documentElement\.lang\|\|localStorage\.getItem\("atmart_lang"\)\|\|)"fr"',
                      r'\1"en"', html)
    n += k
    html, k = re.subn(r'(return L\[l\]\?l:)"fr";', r'\1"en";', html)
    n += k
    # ⚠️ LE VOILE CHANGEAIT DE CAMP AVEC LE BALISAGE. Il cachait la page tant
    # qu'on n'etait PAS en francais, parce que le francais etait ecrit dans le
    # HTML. Le balisage est desormais anglais : c'est l'anglais qui n'a plus
    # besoin d'attendre, et tout le reste qui attend.
    html, k = re.subn(r'if\(l!=="fr"\)\{d\.className\+=" i18n-wait"',
                      'if(l!=="en"){d.className+=" i18n-wait"', html)
    n += k
    return html, n


def rendre(chemin, langue="en", bavard=True):
    mjs = os.path.join(RACINE, "tools", "rendre_en.mjs")
    r = subprocess.run(["node", mjs, chemin, langue],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise SystemExit("rendre_en.mjs a echoue sur %s :\n%s" % (chemin, r.stderr[-2000:]))
    d = json.loads(r.stdout)
    if d["soucis"]:
        # Un script qui meurt en route, c'est une page a moitie traduite. On
        # refuse de publier plutot que de livrer un melange de langues.
        raise SystemExit("%s : le script de la page a echoue — %s"
                         % (os.path.basename(chemin), " · ".join(d["soucis"])))

    html = io.open(chemin, encoding="utf-8").read()

    def presents(t):
        z = zones_script(t)
        return {m.group(1) for m in re.finditer(r'\sid="([^"]+)"', t)
                if not dans_script(z, m.start())}

    avant = presents(html)

    poses = ratees = 0
    for ident, e in d["ecrits"].items():
        html, ok = poser(html, ident, e["mode"], e["v"])
        poses += ok
        ratees += not ok

    # ⚠️ UN PARENT PEUT AVALER SON ENFANT. Si applyLang() ecrit l'innerHTML
    # d'un element QUI EN CONTIENT un autre qu'elle traduit aussi, poser le
    # parent efface l'identifiant de l'enfant — le texte reste juste en
    # anglais, mais la page ne sait plus le retraduire, et passer en kreyol
    # laisse cette ligne-la en anglais. Le defaut serait invisible au build et
    # ne se verrait qu'en changeant de langue, sur une ligne parmi cinquante.
    disparus = sorted(avant - presents(html))
    if disparus:
        raise SystemExit(
            "%s : %d identifiant(s) efface(s) en posant l'anglais — %s.\n"
            "Un element traduit en contient un autre : la page ne pourra plus "
            "retraduire l'enfant quand le visiteur changera de langue."
            % (os.path.basename(chemin), len(disparus), " ".join(disparus)))
    opts = 0
    for ident, rangs in d["options"].items():
        html, k = poser_options(html, ident, rangs)
        opts += k
    html, t = poser_titre(html, d["titre"], d["description"])
    html, lg = poser_langue(html)

    tmp = chemin + ".tmp"
    io.open(tmp, "w", encoding="utf-8", newline="\n").write(html)
    os.replace(tmp, chemin)
    if bavard:
        print("     %-14s %3d pose(s) · %2d option(s) · %d titre/descr · %d langue"
              % (os.path.basename(chemin), poses, opts, t, lg)
              + ("  !! %d id(s) introuvable(s) dans le balisage" % ratees if ratees else ""))
    return poses, ratees


if __name__ == "__main__":
    cibles = sys.argv[1:] or ["wout.html", "setdi.html", "vivye.html", "anplwaye.html"]
    total = 0
    for c in cibles:
        _, r = rendre(os.path.join(RACINE, c))
        total += r
    sys.exit(0)
