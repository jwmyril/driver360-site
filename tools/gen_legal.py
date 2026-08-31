# -*- coding: utf-8 -*-
"""
Fabrique `terms.html` et `privacy.html` depuis `legal_specs.py`.

    python tools/gen_legal.py

Les deux pages suivent le même dispositif que le reste de la suite : l'anglais
est écrit dans le HTML, les trois autres langues vivent dans un dictionnaire
inline, et le tout observe `<html lang>`. `tools/verif_langue.py` les contrôle
comme les autres.
"""
import io
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

from legal_specs import TERMS, PRIVACY, MANQUE, MAJ, MAJ_LBL
from regen import entete, PIED

CSS = """
    .lg{max-width:74ch}
    .lg h2{font-family:'Space Grotesk',sans-serif;color:#fff;font-size:1.2rem;margin:2.1rem 0 .6rem}
    .lg p{font-size:.95rem;line-height:1.72;color:#c9d8e6;margin:0 0 .9rem}
    .lg .maj{font-size:.82rem;color:#7f93a7;margin-top:.4rem}
    .lg .manque{background:rgba(244,162,97,.1);border:1px solid rgba(244,162,97,.42);
      border-radius:12px;padding:1rem 1.2rem;margin-top:2.4rem;font-size:.88rem;color:#e4dbcf;line-height:1.65}
"""

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="icon" href="assets/brand/favicon.ico" sizes="any" />
  <link rel="icon" type="image/png" href="assets/brand/logo-32.png" />
  <link rel="apple-touch-icon" href="assets/brand/apple-touch-icon.png" />
  <title>%(titre)s — Driver360</title>
  <meta name="description" content="%(intro_court)s" />
  <link rel="canonical" href="https://driver360.atmart.ltd/%(fichier)s" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet" />
  <link rel="manifest" href="manifest.webmanifest" />
  <meta name="theme-color" content="#0e2240" />
  <link rel="stylesheet" href="assets/style.css" />
<script>/* langue automatique, avant le premier affichage */
(function(){var S={ht:1,fr:1,en:1,es:1},d=document.documentElement,s=null;
try{s=localStorage.getItem("atmart_lang")}catch(e){}
var l=s&&S[s]?s:null;
if(!l){var n=navigator.languages||[navigator.language||""];
for(var i=0;i<n.length;i++){var c=String(n[i]).toLowerCase().split("-")[0];
if(c==="ht"||c==="hat"){l="ht";break}if(S[c]){l=c;break}}}
d.lang=l||"en";})();
</script>
  <style>%(css)s</style>
</head>
<body>

%(entete)s

<section class="hero" style="padding-bottom:.4rem">
  <div class="container">
    <h1 data-t="titre">%(titre)s</h1>
    <p class="lead" data-t="intro">%(intro)s</p>
    <p class="maj"><span data-t="majl">%(majl)s</span>: %(maj)s</p>
  </div>
</section>

<section style="padding-top:.4rem;padding-bottom:2.8rem">
  <div class="container">
    <div class="lg">
%(corps)s
      <div class="manque" data-t="manque">%(manque)s</div>
    </div>
  </div>
</section>

%(pied)s

<script>
var T = %(dico)s;
var TITRE0 = document.title;
function appliquer(){
  var l = document.documentElement.lang;
  var d = T[l];                      /* en = ce qui est ecrit dans le HTML */
  document.title = (d && d.ti) ? d.ti : TITRE0;
  document.querySelectorAll("[data-t]").forEach(function(e){
    if(!e.dataset.original) e.dataset.original = e.innerHTML;
    e.innerHTML = d ? (d[e.dataset.t] || e.dataset.original) : e.dataset.original;
  });
}
appliquer();
new MutationObserver(appliquer).observe(document.documentElement,
  {attributes:true, attributeFilter:["lang"]});
</script>
<script src="assets/suite.js?v=5"></script>
<script>if("serviceWorker" in navigator){navigator.serviceWorker.register("/sw.js");}</script>
</body>
</html>
"""


def corps(doc):
    out = []
    for i, sec in enumerate(doc["sections"]):
        out.append('      <h2 data-t="s%d_t">%s</h2>' % (i, sec["t"]["en"]))
        for j, para in enumerate(sec["p"]["en"]):
            out.append('      <p data-t="s%d_%d">%s</p>' % (i, j, para))
    return "\n".join(out)


def dictionnaire(doc, titre_page):
    out = {}
    for lg in ("fr", "ht", "es"):
        d = {
            "ti": "%s — Driver360" % doc["titre"][lg],
            "titre": doc["titre"][lg],
            "intro": doc["intro"][lg],
            "majl": MAJ_LBL[lg],
            "manque": MANQUE[lg],
        }
        for i, sec in enumerate(doc["sections"]):
            d["s%d_t" % i] = sec["t"][lg]
            for j, para in enumerate(sec["p"][lg]):
                d["s%d_%d" % (i, j)] = para
        out[lg] = d
    return out


def ecrire(doc, fichier):
    html = PAGE % {
        "titre": doc["titre"]["en"],
        "intro": doc["intro"]["en"],
        "intro_court": doc["intro"]["en"][:150],
        "majl": MAJ_LBL["en"],
        "maj": MAJ,
        "manque": MANQUE["en"],
        "css": CSS,
        "entete": entete(fichier),
        "pied": PIED,
        "corps": corps(doc),
        "fichier": fichier,
        "dico": json.dumps(dictionnaire(doc, fichier), ensure_ascii=False, indent=1),
    }
    chemin = os.path.join(RACINE, fichier)
    with io.open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    return len(html)


if __name__ == "__main__":
    for doc, nom in ((TERMS, "terms.html"), (PRIVACY, "privacy.html")):
        n = ecrire(doc, nom)
        print("%-14s %d sections, %d octets" % (nom, len(doc["sections"]), n))
