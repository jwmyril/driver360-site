# -*- coding: utf-8 -*-
"""
Les alertes WhatsApp : préparer, envoyer, tracer, arrêter.

    python tools/alertes_whatsapp.py --liste
    python tools/alertes_whatsapp.py --preparer --ville Fitchburg \\
        --employeur "NRT Bus" --poste "chauffeur de van 7D" \\
        --lien https://nrtbus.com/careers/
    python tools/alertes_whatsapp.py --marquer DRV-XXXX-XXXX
    python tools/alertes_whatsapp.py --stop DRV-XXXX-XXXX

POURQUOI CE FICHIER EXISTE
--------------------------
Le site PROMET trois choses au chauffeur qui coche la case :

  1. on le prévient quand une offre s'ouvre près de chez lui ;
  2. **deux messages par semaine au maximum** ;
  3. **STOP** met fin à tout.

Or il n'existait rien pour tenir la deuxième ni la troisième. Une promesse
sans mécanisme n'est pas une promesse, c'est une phrase — et sur un produit
dont l'argument central est le respect des données, c'est la phrase qui coûte
le plus cher. Cet outil est le mécanisme.

CE QU'IL N'EST PAS. Ce n'est pas un automate d'envoi. Le compte WhatsApp
Business n'est pas ouvert (numéro dédié, compte vérifié, gabarits approuvés par
Meta, facturation par message livré). L'envoi reste donc fait par une personne
— exactement ce que la page annonce. L'outil rend cet envoi FAISABLE : il dit
qui prévenir, dans quelle langue, et il refuse ceux qu'on a déjà sollicités.

POURQUOI EN LOCAL PLUTÔT QU'UNE ROUTE DU WORKER. Une route de plus, c'est une
surface d'attaque de plus à protéger — pour un vivier qui compte zéro
chauffeur aujourd'hui. Les données restent dans le KV ; cet outil s'y branche
avec `wrangler`, qui exige déjà d'être authentifié sur le compte Cloudflare.

⚠️ CE QUE CET OUTIL NE DOIT JAMAIS FAIRE
  · écrire à quelqu'un dont `wa` n'est pas exactement `true` ;
  · dépasser deux messages sur sept jours glissants ;
  · réactiver un consentement retiré. `--stop` est définitif côté outil : seul
    le chauffeur peut se réabonner, depuis sa propre page, avec son code.
"""
import argparse
import io
import json
import os
import subprocess
import sys
from datetime import date, timedelta

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKER = os.path.join(os.path.dirname(RACINE), "Atmart_chat_worker")
BINDING = "RATE_LIMIT"

PLAFOND_7J = 2          # ce que la page promet, mot pour mot
REPOS_JOURS = 2         # jamais deux jours de suite


# --------------------------------------------------------------- le message
# Court : WhatsApp se lit sur un écran de téléphone, souvent en marchant.
# Il dit QUI recrute, OÙ, et il donne le lien de l'employeur — jamais le nôtre.
# Le rappel du STOP est dans chaque message : c'est ce qui rend le retrait
# possible sans avoir à chercher comment.
MESSAGES = {
    "en": ("Driver360 — a driving job just opened near {ville}.\n\n"
           "{employeur} is hiring: {poste}.\n"
           "Apply on their own page: {lien}\n\n"
           "You asked us to tell you. Reply STOP and we stop."),
    "es": ("Driver360 — se acaba de abrir un empleo de conductor cerca de {ville}.\n\n"
           "{employeur} contrata: {poste}.\n"
           "Postula en su propia página: {lien}\n\n"
           "Pediste que te avisáramos. Responde STOP y paramos."),
    "ht": ("Driver360 — gen yon travay chofè ki fèk louvri toupre {ville}.\n\n"
           "{employeur} ap chèche moun: {poste}.\n"
           "Aplike sou pwòp paj yo: {lien}\n\n"
           "Se ou menm ki te mande nou avèti w. Reponn STOP epi n ap kanpe."),
    "fr": ("Driver360 — une offre de chauffeur vient de s'ouvrir près de {ville}.\n\n"
           "{employeur} recrute : {poste}.\n"
           "Postulez sur leur propre page : {lien}\n\n"
           "Vous nous aviez demandé de vous prévenir. Répondez STOP et nous arrêtons."),
}


# ----------------------------------------------------------------- le KV
def wrangler(*args):
    r = subprocess.run(["npx", "wrangler"] + list(args), cwd=WORKER,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", shell=(os.name == "nt"))
    if r.returncode != 0:
        raise SystemExit("wrangler a echoue : %s" % (r.stderr or "").strip()[:300])
    return r.stdout


def lire_vivier():
    """Toutes les fiches du vivier libre, avec leur code."""
    brut = wrangler("kv", "key", "list", "--binding=" + BINDING,
                    "--prefix=drv:", "--remote")
    cles = [k["name"] for k in json.loads(brut)]
    fiches = []
    for cle in cles:
        txt = wrangler("kv", "key", "get", cle, "--binding=" + BINDING, "--remote")
        try:
            f = json.loads(txt)
        except ValueError:
            continue
        f["_cle"] = cle
        f["_code"] = cle.split(":", 1)[1]
        fiches.append(f)
    return fiches


def ecrire_fiche(fiche):
    cle = fiche.pop("_cle")
    fiche.pop("_code", None)
    chemin = os.path.join(os.environ.get("TEMP", "."), "d360-fiche.json")
    with io.open(chemin, "w", encoding="utf-8", newline="\n") as f:
        json.dump(fiche, f, ensure_ascii=False)
    wrangler("kv", "key", "put", cle, "--path", chemin,
             "--binding=" + BINDING, "--remote")
    os.remove(chemin)


# ------------------------------------------------------------- les regles
def envois_recents(fiche):
    """Les dates d'envoi des sept derniers jours."""
    limite = date.today() - timedelta(days=7)
    out = []
    for d in fiche.get("waSent", []) or []:
        try:
            j = date.fromisoformat(d)
        except ValueError:
            continue
        if j > limite:
            out.append(j)
    return sorted(out)


def joignable(fiche):
    """Peut-on ecrire a cette personne aujourd'hui ? Sinon, pourquoi non."""
    if fiche.get("wa") is not True:
        return False, "n'a pas demande d'alertes"
    if not fiche.get("phone"):
        return False, "pas de telephone"
    if fiche.get("status") == "hired":
        return False, "a trouve un emploi"
    if fiche.get("status") == "paused":
        return False, "a mis son dossier en pause"
    recents = envois_recents(fiche)
    if len(recents) >= PLAFOND_7J:
        return False, "deja %d messages sur 7 jours (plafond promis : %d)" % (len(recents), PLAFOND_7J)
    if recents and (date.today() - recents[-1]).days < REPOS_JOURS:
        return False, "dernier message il y a %d jour(s)" % (date.today() - recents[-1]).days
    return True, ""


def langue(fiche):
    """La langue du message.

    On prend d'abord `lang` : la langue dans laquelle le chauffeur LISAIT le
    site en s'inscrivant. C'est le signal le plus sur, et il ne lui a rien
    coute a saisir.

    ⚠️ On garde la lecture de `langs` pour les fiches d'AVANT le 31/08/2026,
    quand un champ « langues parlees » existait encore. Sans ce repli, toutes
    ces fiches basculeraient en anglais du jour au lendemain — en silence.
    """
    direct = fiche.get("lang")
    if direct in MESSAGES:
        return direct
    t = (fiche.get("langs") or "").lower()
    if any(m in t for m in ("krey", "creol", "kreol", "haitian")):
        return "ht"
    if any(m in t for m in ("espa", "spanish", "castell")):
        return "es"
    if any(m in t for m in ("fran", "french")):
        return "fr"
    return "en"


def lien_wa(phone, texte):
    import urllib.parse
    chiffres = "".join(c for c in (phone or "") if c.isdigit())
    if not chiffres:
        return ""
    if len(chiffres) == 10:
        chiffres = "1" + chiffres
    return "https://wa.me/%s?text=%s" % (chiffres, urllib.parse.quote(texte))


# ------------------------------------------------------------- les actions
def action_liste(fiches):
    if not fiches:
        print("Le vivier est vide : personne a prevenir.")
        return 0
    print("%-16s %-22s %-13s %-4s %s" % ("CODE", "VILLE", "ALERTES", "LG", "ETAT"))
    for f in sorted(fiches, key=lambda x: x.get("city") or ""):
        ok, pourquoi = joignable(f)
        print("%-16s %-22s %-13s %-4s %s"
              % (f["_code"], (f.get("city") or "-")[:22],
                 "%d/7j" % len(envois_recents(f)), langue(f),
                 "pret" if ok else pourquoi))
    joignables = sum(1 for f in fiches if joignable(f)[0])
    print("\n%d fiche(s), %d joignable(s) aujourd'hui." % (len(fiches), joignables))
    return 0


def action_preparer(fiches, args):
    if not (args.employeur and args.poste and args.lien):
        raise SystemExit("--preparer demande --employeur, --poste et --lien.")
    if not args.lien.startswith(("http://", "https://")):
        raise SystemExit("--lien doit etre une adresse http(s) : on envoie les gens\n"
                         "sur la page de l'employeur, jamais ailleurs.")
    ville = args.ville
    prets = []
    for f in fiches:
        ok, pourquoi = joignable(f)
        if not ok:
            continue
        if ville and ville.lower() not in (f.get("city") or "").lower():
            continue
        lg = langue(f)
        texte = MESSAGES[lg].format(ville=f.get("city") or ville or "you",
                                    employeur=args.employeur, poste=args.poste,
                                    lien=args.lien)
        prets.append((f, lg, texte))

    if not prets:
        print("Personne a prevenir : aucun consentement, ou tous deja sollicites.")
        return 0

    print("=" * 72)
    print("%d message(s) a envoyer A LA MAIN. Ouvrez chaque lien, verifiez," % len(prets))
    print("envoyez, puis marquez l'envoi — sinon le plafond ne sert a rien.")
    print("=" * 72)
    for f, lg, texte in prets:
        print("\n--- %s  (%s, %s)" % (f["_code"], f.get("city") or "?", lg))
        print(texte)
        print("\n  ouvrir : %s" % lien_wa(f.get("phone"), texte))
        print("  marquer: python tools/alertes_whatsapp.py --marquer %s" % f["_code"])
    return 0


def action_marquer(fiches, code):
    f = next((x for x in fiches if x["_code"] == code.upper()), None)
    if not f:
        raise SystemExit("Code inconnu : %s" % code)
    ok, pourquoi = joignable(f)
    if not ok:
        raise SystemExit("Refus : %s. On ne marque pas un envoi qui n'aurait pas du partir." % pourquoi)
    envois = [d for d in (f.get("waSent") or []) if d]
    envois.append(date.today().isoformat())
    f["waSent"] = envois[-10:]
    f["waLast"] = date.today().isoformat()
    ecrire_fiche(f)
    print("Envoi enregistre pour %s (%d sur les 7 derniers jours)."
          % (code.upper(), len(envois_recents(f))))
    return 0


def action_stop(fiches, code):
    f = next((x for x in fiches if x["_code"] == code.upper()), None)
    if not f:
        raise SystemExit("Code inconnu : %s" % code)
    f["wa"] = False
    f.pop("waAt", None)
    f["waStopAt"] = date.today().isoformat()
    ecrire_fiche(f)
    print("Alertes coupees pour %s." % code.upper())
    print("Cet outil ne peut PAS les rallumer : seul le chauffeur le peut,")
    print("depuis sa page, avec son code. C'est voulu.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Alertes WhatsApp Driver360")
    ap.add_argument("--liste", action="store_true", help="qui est joignable aujourd'hui")
    ap.add_argument("--preparer", action="store_true", help="composer les messages")
    ap.add_argument("--ville", default="", help="ne prevenir que ce secteur")
    ap.add_argument("--employeur", default="")
    ap.add_argument("--poste", default="")
    ap.add_argument("--lien", default="", help="la page de candidature de l'employeur")
    ap.add_argument("--marquer", metavar="CODE", help="enregistrer un envoi effectue")
    ap.add_argument("--stop", metavar="CODE", help="couper les alertes (STOP recu)")
    args = ap.parse_args()

    if not any([args.liste, args.preparer, args.marquer, args.stop]):
        ap.print_help()
        return 1

    fiches = lire_vivier()
    if args.marquer:
        return action_marquer(fiches, args.marquer)
    if args.stop:
        return action_stop(fiches, args.stop)
    if args.preparer:
        return action_preparer(fiches, args)
    return action_liste(fiches)


if __name__ == "__main__":
    sys.exit(main())
