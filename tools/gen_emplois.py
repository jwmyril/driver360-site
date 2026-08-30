# -*- coding: utf-8 -*-
"""
Fabrique `jobs.html` — la page des offres de chauffeur au Massachusetts.

    python tools/gen_emplois.py              regenere la page
    python tools/gen_emplois.py --verifier   ouvre chaque lien et dit lesquels sont morts

POURQUOI CETTE PAGE EXISTE, ET POURQUOI ELLE EST LA PREMIERE
------------------------------------------------------------
Un chauffeur ne s'inscrit pas dans un vivier pour figurer dans une base de
donnees. Il s'inscrit parce qu'il y a un poste. Tant que Driver360 n'offrait
que « inscrivez-vous, on vous trouvera peut-etre », il demandait un service au
chauffeur au lieu de lui en rendre un. Cette page renverse la relation : elle
donne quelque chose d'utile AVANT de demander quoi que ce soit — la liste des
employeurs qui recrutent vraiment, verifiee, sans compte a creer.

L'inscription devient alors la suite naturelle : « et si vous voulez, on vous
previent quand il y en a une nouvelle. »

CE QUE LA PAGE NE FAIT PAS. Elle ne recopie aucune annonce (voir emplois.py).
Elle ne promet pas d'alertes automatiques : au 29/08/2026 elles partent a la
main, et la page le dit.
"""
import io, os, sys, re

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

from emplois import EMPLOYEURS, SECTIONS, VERIFIE_LE
from regen import entete, PIED  # regen re-enveloppe sys.stdout : ne pas le refaire ici

LANGUES = ["en", "fr", "ht", "es"]

# Les phrases de la page. La cle est courte, la valeur est le texte dans les
# quatre langues. `en` est la langue ECRITE DANS LE HTML : les autres sont
# appliquees par le petit script de bascule en bas de page.
#
# NOTE KREYOL. Traduit a partir du SENS, jamais mot a mot. A relire par
# l'utilisateur, qui est l'autorite sur cette langue.
TX = {
    "ti": {
        "en": "Driving jobs in Massachusetts — Driver360",
        "fr": "Emplois de chauffeur au Massachusetts — Driver360",
        "ht": "Travay chofè nan Massachusetts — Driver360",
        "es": "Empleos de conductor en Massachusetts — Driver360",
    },
    "titre": {
        "en": "Driving jobs in Massachusetts",
        "fr": "Emplois de chauffeur au Massachusetts",
        "ht": "Travay chofè nan Massachusetts",
        "es": "Empleos de conductor en Massachusetts",
    },
    "fil": {
        "en": "Massachusetts is short of drivers. For most of these jobs, the licence is the only thing in the way.",
        "fr": "Le Massachusetts manque de chauffeurs. Pour la plupart de ces postes, le permis est le seul obstacle.",
        "ht": "Massachusetts manke chofè. Pou pifò nan travay sa yo, se pèmi a ki sèl bagay k ap bare wout la.",
        "es": "A Massachusetts le faltan conductores. Para la mayoría de estos puestos, la licencia es el único obstáculo.",
    },
    "lead": {
        "en": "We do not host job adverts and we do not copy them. Below is the list of employers who actually hire drivers here, with a link straight to their own openings — so you apply in the right place, and nothing on this page goes stale.",
        "fr": "Nous n'hébergeons pas d'annonces et nous n'en recopions aucune. Voici la liste des employeurs qui recrutent réellement des chauffeurs ici, avec un lien direct vers leurs propres offres — vous postulez donc au bon endroit, et rien sur cette page ne périme.",
        "ht": "Nou pa gen anons lakay nou epi nou pa kopye okenn. Men lis anplwayè ki tout bon ap chèche chofè isit la, ak yon lyen dirèk sou òf pa yo — konsa ou aplike nan bon kote a, epi anyen sou paj sa a pa vin vye.",
        "es": "No alojamos anuncios ni los copiamos. Esta es la lista de empleadores que de verdad contratan conductores aquí, con un enlace directo a sus propias vacantes — así postulas en el sitio correcto y nada de esta página caduca.",
    },
    "verifie": {
        "en": "Every link below was opened and checked on %s." % VERIFIE_LE,
        "fr": "Chaque lien ci-dessous a été ouvert et vérifié le %s." % VERIFIE_LE,
        "ht": "Chak lyen anba a te louvri epi verifye nan dat %s." % VERIFIE_LE,
        "es": "Cada enlace de abajo fue abierto y verificado el %s." % VERIFIE_LE,
    },
    "voir": {
        "en": "See their openings →", "fr": "Voir leurs offres →",
        "ht": "Gade òf yo →", "es": "Ver sus vacantes →",
    },
    "paye_t": {
        "en": "What these jobs pay", "fr": "Ce que ces postes paient",
        "ht": "Konbyen travay sa yo peye", "es": "Cuánto pagan estos puestos",
    },
    "paye_d": {
        "en": "School bus driver posts in Massachusetts were advertised at roughly $27 to $32 an hour in August 2026, and CDL routes often carry a sign-on bonus. Those are figures read on job boards, not a promise from anyone: the only number that binds an employer is the one on the employer's own page. Many of these posts are split shifts — morning and afternoon — which suits people who need the middle of the day free.",
        "fr": "Les postes de chauffeur de bus scolaire étaient affichés autour de 27 à 32 dollars de l'heure au Massachusetts en août 2026, et les circuits CDL s'accompagnent souvent d'une prime à l'embauche. Ce sont des chiffres lus sur des sites d'emploi, pas une promesse : le seul chiffre qui engage un employeur est celui de sa propre page. Beaucoup de ces postes sont en horaires coupés — matin et après-midi — ce qui convient à qui a besoin de son milieu de journée.",
        "ht": "Pòs chofè bis lekòl yo te afiche ant 27 ak 32 dola lè a nan Massachusetts nan mwa out 2026, epi wout CDL yo souvan vini ak yon prim lè ou siyen. Se chif nou li sou sit travay, se pa yon pwomès: sèl chif ki angaje yon anplwayè se sa ki sou paj pa l. Anpil nan pòs sa yo se orè koupe — maten ak apremidi — sa bon pou moun ki bezwen mitan jounen an lib.",
        "es": "Los puestos de conductor de autobús escolar se anunciaban entre 27 y 32 dólares la hora en Massachusetts en agosto de 2026, y las rutas con CDL suelen incluir un bono de contratación. Son cifras leídas en portales de empleo, no una promesa: el único número que compromete a un empleador es el de su propia página. Muchos de estos puestos son de jornada partida — mañana y tarde — lo que le conviene a quien necesita libre el mediodía.",
    },
    "alerte_t": {
        "en": "Get told when a new one opens", "fr": "Être prévenu quand une offre s'ouvre",
        "ht": "Konnen lè yon nouvo òf louvri", "es": "Que te avisen cuando se abra una",
    },
    "alerte_d": {
        "en": "Checking eight pages every week is work. Tick one box when you join the driver pool and we will send you a WhatsApp message when something opens near you — two a week at most, and STOP ends it. Right now those messages are written and sent by hand, by a person, from a Massachusetts number. We would rather say that than pretend we have an automated system we do not yet have.",
        "fr": "Vérifier huit pages chaque semaine, c'est du travail. Cochez une case en vous inscrivant au vivier et nous vous enverrons un message WhatsApp quand une offre s'ouvre près de chez vous — deux par semaine au maximum, et STOP y met fin. Aujourd'hui ces messages sont écrits et envoyés à la main, par une personne, depuis un numéro du Massachusetts. Nous préférons le dire plutôt que de faire croire à un système automatique que nous n'avons pas encore.",
        "ht": "Tcheke uit paj chak semèn se travay. Koche yon sèl kaz lè w ap enskri nan vivye a epi n ap voye yon mesaj WhatsApp ba ou lè yon òf louvri toupre lakay ou — de pa semèn, pa plis, epi STOP fè sa kanpe. Kounye a se yon moun ki ekri epi voye mesaj sa yo alamen, depi yon nimewo Massachusetts. Nou pito di sa pase pou nou fè kwè nou gen yon sistèm otomatik nou poko genyen.",
        "es": "Revisar ocho páginas cada semana es trabajo. Marca una casilla al inscribirte en el registro y te enviaremos un mensaje de WhatsApp cuando se abra algo cerca de ti — dos por semana como máximo, y STOP lo termina. Hoy esos mensajes los escribe y los envía una persona, a mano, desde un número de Massachusetts. Preferimos decirlo antes que fingir un sistema automático que todavía no tenemos.",
    },
    "alerte_b": {
        "en": "Join the pool and turn on alerts", "fr": "M'inscrire et activer les alertes",
        "ht": "Enskri m epi limen alèt yo", "es": "Inscribirme y activar los avisos",
    },
    "gratuit": {
        "en": "Free. No account, no payment, and we sell nobody's name.",
        "fr": "Gratuit. Pas de compte, pas de paiement, et nous ne vendons le nom de personne.",
        "ht": "Gratis. Pa gen kont, pa gen peman, epi nou pa vann non pèsonn.",
        "es": "Gratis. Sin cuenta, sin pago, y no vendemos el nombre de nadie.",
    },
    "permis_t": {
        "en": "Missing the licence?", "fr": "Il vous manque le permis ?",
        "ht": "Se pèmi a ki manke w?", "es": "¿Te falta la licencia?",
    },
    "permis_d": {
        "en": "Most of these employers will train you, but they all need you to hold — or be able to get — a Class D or a 7D. Driver Coach drills the road test and the 7D written test, in English, Haitian Creole, French and Spanish.",
        "fr": "La plupart de ces employeurs vous formeront, mais tous ont besoin que vous ayez — ou puissiez obtenir — un Class D ou un 7D. Driver Coach fait travailler le test de route et l'examen écrit 7D, en anglais, kreyòl, français et espagnol.",
        "ht": "Pifò nan anplwayè sa yo ap fòme w, men yo tout bezwen ou genyen — oswa ou ka jwenn — yon Class D oswa yon 7D. Driver Coach fè w travay tès wout la ak egzamen ekri 7D a, an anglè, kreyòl, franse ak panyòl.",
        "es": "La mayoría de estos empleadores te formarán, pero todos necesitan que tengas — o puedas obtener — una Class D o una 7D. Driver Coach practica el examen de manejo y el examen escrito 7D, en inglés, criollo haitiano, francés y español.",
    },
    "permis_b": {
        "en": "Prepare with Driver Coach →", "fr": "Me préparer avec Driver Coach →",
        "ht": "Prepare m ak Driver Coach →", "es": "Prepararme con Driver Coach →",
    },
    "manque_t": {
        "en": "An employer we have missed?", "fr": "Un employeur qui manque ?",
        "ht": "Yon anplwayè ki manke?", "es": "¿Falta un empleador?",
    },
    "manque_d": {
        "en": "If you know a company or a district hiring drivers in Massachusetts, tell us and we will check it and add it.",
        "fr": "Si vous connaissez une entreprise ou un district qui recrute des chauffeurs au Massachusetts, dites-le-nous : nous le vérifions et nous l'ajoutons.",
        "ht": "Si w konnen yon konpayi oswa yon distri k ap chèche chofè nan Massachusetts, di nou l: n ap verifye l epi n ap mete l.",
        "es": "Si conoces una empresa o un distrito que contrate conductores en Massachusetts, dínoslo: lo verificamos y lo añadimos.",
    },
    "manque_b": {
        "en": "Tell us about an employer", "fr": "Signaler un employeur",
        "ht": "Siyale yon anplwayè", "es": "Avisar de un empleador",
    },
    "contact": {"en": "A question", "fr": "Une question", "ht": "Yon kesyon", "es": "Una pregunta"},
    "droits": {"en": "All rights reserved.", "fr": "Tous droits réservés.",
               "ht": "Tout dwa rezève.", "es": "Todos los derechos reservados."},
}

MAILTO = ("mailto:sales@atmart.ltd?subject=Driver360%20-%20un%20employeur%20qui%20recrute"
          "%20des%20chauffeurs&amp;body=Nom%20de%20l%27employeur%20%3A%0AVille%20%3A%0A"
          "Adresse%20de%20leur%20page%20d%27emploi%20%3A%0A%0AMerci.")

CSS = """
    .jb-sec{margin-top:2.4rem}
    .jb-sec>h2{font-family:'Space Grotesk',sans-serif;color:#fff;font-size:1.28rem;margin:0 0 .2rem}
    .jb-sec>p.n{margin:0 0 1.1rem;font-size:.85rem;color:#7f93a7}
    .jb-liste{display:grid;grid-template-columns:1fr;gap:.85rem}
    @media(min-width:800px){.jb-liste{grid-template-columns:1fr 1fr}}
    .jb{display:block;text-decoration:none;background:rgba(255,255,255,.035);
      border:1px solid rgba(255,255,255,.1);border-radius:14px;padding:1.15rem 1.3rem;
      transition:border-color .2s,transform .2s}
    .jb:hover{border-color:rgba(46,196,182,.6);transform:translateY(-2px)}
    .jb .n{display:flex;align-items:baseline;justify-content:space-between;gap:.7rem;flex-wrap:wrap}
    .jb h3{margin:0;font-family:'Space Grotesk',sans-serif;color:#fff;font-size:1.06rem}
    .jb .z{font-size:.75rem;color:#2ec4b6;font-weight:600}
    .jb p{margin:.5rem 0 .8rem;font-size:.88rem;line-height:1.6;color:#9db2c7}
    .jb .v{font-size:.83rem;color:#2ec4b6;font-weight:600}
    .jb-note{background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.1);
      border-radius:14px;padding:1.3rem 1.5rem;margin-top:1.6rem;max-width:74ch}
    .jb-note h2{margin:0 0 .5rem;font-family:'Space Grotesk',sans-serif;color:#fff;font-size:1.14rem}
    .jb-note p{margin:0;font-size:.92rem;line-height:1.7;color:#c9d8e6}
    .jb-wa{background:rgba(37,211,102,.08);border-color:rgba(37,211,102,.4)}
    .d3-lang{display:flex;gap:.4rem;flex-wrap:wrap}
    .d3-lang button{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.14);
      color:#c9d8e6;border-radius:99px;padding:.3rem .8rem;font-size:.8rem;cursor:pointer;font-family:inherit}
    .d3-lang button.actif{border-color:#2ec4b6;color:#2ec4b6;font-weight:600}
"""


def t(cle, lg="en"):
    return TX[cle][lg]


def carte(e):
    return (
        '      <a class="jb" href="%s" target="_blank" rel="noopener">\n'
        '        <span class="n"><h3>%s</h3><span class="z" data-t="z_%s">%s</span></span>\n'
        '        <p data-t="q_%s">%s</p>\n'
        '        <span class="v" data-t="voir">%s</span>\n'
        '      </a>' % (e["url"], e["nom"], cle(e), e["zone"]["en"],
                        cle(e), e["quoi"]["en"], t("voir"))
    )


def cle(e):
    return re.sub(r"[^a-z0-9]+", "", e["nom"].lower())


def dictionnaire():
    """Le dictionnaire des trois autres langues, employeurs compris."""
    out = {}
    for lg in ("fr", "ht", "es"):
        d = {k: v[lg] for k, v in TX.items()}
        for e in EMPLOYEURS:
            d["z_" + cle(e)] = e["zone"][lg]
            d["q_" + cle(e)] = e["quoi"][lg]
        for genre, titres in SECTIONS:
            d["s_" + genre] = titres[lg]
        out[lg] = d
    return out


def construire():
    corps = []
    for genre, titres in SECTIONS:
        gens = [e for e in EMPLOYEURS if e["genre"] == genre]
        if not gens:
            continue
        corps.append('    <div class="jb-sec">\n      <h2 data-t="s_%s">%s</h2>\n'
                     '      <div class="jb-liste">\n%s\n      </div>\n    </div>'
                     % (genre, titres["en"], "\n".join(carte(e) for e in gens)))
    return "\n".join(corps)


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="icon" href="assets/brand/favicon.ico" sizes="any" />
  <link rel="icon" type="image/png" href="assets/brand/logo-32.png" />
  <link rel="apple-touch-icon" href="assets/brand/apple-touch-icon.png" />
  <title>Driving jobs in Massachusetts — Driver360</title>
  <meta name="description" content="Who actually hires drivers in Massachusetts: school transport, regional transit authorities and the state job board. Checked links, straight to each employer's own openings. Free WhatsApp alerts when a new one opens." />
  <link rel="canonical" href="https://driver360.atmart.ltd/jobs.html" />
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

<section class="hero" style="padding-bottom:.6rem">
  <div class="container">
    <p class="kreyol" data-t="fil">%(fil)s</p>
    <h1 data-t="titre">%(titre)s</h1>
    <p class="lead" data-t="lead">%(lead)s</p>
    <p style="font-size:.83rem;color:#7f93a7;margin-top:.6rem" data-t="verifie">%(verifie)s</p>
  </div>
</section>

<section style="padding-top:.4rem;padding-bottom:2.6rem">
  <div class="container">
%(corps)s

    <div class="jb-note">
      <h2 data-t="paye_t">%(paye_t)s</h2>
      <p data-t="paye_d">%(paye_d)s</p>
    </div>

    <div class="jb-note jb-wa">
      <h2 data-t="alerte_t">%(alerte_t)s</h2>
      <p data-t="alerte_d">%(alerte_d)s</p>
      <p style="margin-top:1.1rem">
        <a class="btn btn-primary" href="vivye.html" data-t="alerte_b">%(alerte_b)s</a>
      </p>
      <p style="margin-top:.7rem;font-size:.84rem;color:#9db2c7" data-t="gratuit">%(gratuit)s</p>
    </div>

    <div class="jb-note">
      <h2 data-t="permis_t">%(permis_t)s</h2>
      <p data-t="permis_d">%(permis_d)s</p>
      <p style="margin-top:1.1rem">
        <a class="btn btn-outline" href="wout.html" data-t="permis_b">%(permis_b)s</a>
      </p>
    </div>

    <div class="jb-note">
      <h2 data-t="manque_t">%(manque_t)s</h2>
      <p data-t="manque_d">%(manque_d)s</p>
      <p style="margin-top:1.1rem">
        <a class="btn btn-outline" href="%(mailto)s" data-t="manque_b">%(manque_b)s</a>
      </p>
    </div>
  </div>
</section>

%(pied)s

<script>
var T = %(dico)s;
var LANGUES = {en:"English", ht:"Kreyòl", fr:"Français", es:"Español"};
var TITRE0 = document.title;   /* le titre anglais, ecrit dans le <title> */
function appliquer(l){
  var d = T[l];                      /* en = ce qui est ecrit dans le HTML */
  document.title = (d && d.ti) ? d.ti : TITRE0;
  document.querySelectorAll("[data-t]").forEach(function(e){
    if(!e.dataset.original) e.dataset.original = e.innerHTML;
    e.innerHTML = d ? (d[e.dataset.t] || e.dataset.original) : e.dataset.original;
  });
  document.documentElement.lang = l;
  try{localStorage.setItem("atmart_lang", l)}catch(e){}
  document.querySelectorAll("#lang button").forEach(function(b){
    b.classList.toggle("actif", b.dataset.l === l);
  });
}
(function(){
  var bar = document.getElementById("lang");
  if(!bar) return;
  Object.keys(LANGUES).forEach(function(code){
    var b = document.createElement("button");
    b.type = "button"; b.dataset.l = code; b.textContent = LANGUES[code];
    b.addEventListener("click", function(){ appliquer(code); });
    bar.appendChild(b);
  });
  appliquer(document.documentElement.lang || "en");
})();
</script>
<script src="assets/suite.js?v=1"></script>
<script>if("serviceWorker" in navigator){navigator.serviceWorker.register("/sw.js");}</script>
</body>
</html>
"""


def ecrire():
    import json
    champs = {k: t(k) for k in TX}
    champs.update(css=CSS, entete=entete("jobs.html", "chauffeur", selecteur=True), pied=PIED,
                  corps=construire(), mailto=MAILTO,
                  dico=json.dumps(dictionnaire(), ensure_ascii=False, indent=1))
    html = PAGE % champs
    chemin = os.path.join(RACINE, "jobs.html")
    io.open(chemin, "w", encoding="utf-8", newline="\n").write(html)
    return chemin, len(html)


def verifier():
    """Ouvre chaque lien. Un 404 ici vaut mieux qu un 404 chez un chauffeur.

    DEUX PIEGES APPRIS LE 29/08/2026, quand ce controle a declare morts trois
    liens qui repondaient parfaitement dans un navigateur :

      · un User-Agent seul ne suffit pas. Plusieurs de ces sites sont derriere
        un pare-feu qui repond 403 a une requete sans en-tetes Accept — la page
        est vivante, c est le CLIENT qui est refuse. On envoie donc la meme
        panoplie qu un navigateur.
      · 200 n est pas le seul succes. MART repond 202. Tout code en dessous de
        400 veut dire que la page existe et se sert.

    Un controle qui crie au loup rend le controle inutile : on finit par ne
    plus le lancer.
    """
    import urllib.request, urllib.error, ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    tetes = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    mauvais = 0
    for e in EMPLOYEURS:
        req = urllib.request.Request(e["url"], headers=tetes)
        try:
            with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
                code = r.getcode()
        except urllib.error.HTTPError as ex:
            code = ex.code
        except Exception as ex:
            code = "ERR %s" % type(ex).__name__
        ok = isinstance(code, int) and code < 400
        mauvais += 0 if ok else 1
        print("%s  %-22s %s" % ("OK  " if ok else "MORT", e["nom"], code))
    print("")
    print("%d lien(s) a corriger" % mauvais)
    return mauvais


if __name__ == "__main__":
    if "--verifier" in sys.argv:
        sys.exit(1 if verifier() else 0)
    chemin, n = ecrire()
    print("jobs.html ecrit : %d employeurs, %d octets" % (len(EMPLOYEURS), n))
