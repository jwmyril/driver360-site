# -*- coding: utf-8 -*-
"""Fabrique un code d'accès employeur, au hasard, et l'écrit dans le KV.

    python tools/code_employeur.py --org "ABC Student Transportation" \\
        --contact "Marie Joseph" --phone "+1 508 555 0142" --jours 90

    python tools/code_employeur.py --org "..." --montrer   (n'écrit rien)

POURQUOI CE FICHIER EXISTE (ligne C17)
--------------------------------------
Les codes employeur étaient posés **à la main** dans le KV. Un code vaut 15 $
la sélection, et il ouvre un vivier de personnes qui ont confié leur nom et
leur téléphone.

LE CALCUL, D'ABORD, parce qu'il décide du reste. Le format `EMP-XXXX-XXXX`
donne 8 caractères ; avec le frein posé en C10 — 30 échecs par IP et par
heure — épuiser l'espace demanderait des millénaires, même à mille adresses.
**La longueur n'est donc pas le problème.**

LE PROBLÈME EST QU'AUCUNE RÈGLE N'OBLIGEAIT LE CODE À ÊTRE ALÉATOIRE. Le jour
où l'on tape `EMP-ABCD-1234`, ou le nom du client, ou une suite qu'on retient
facilement, l'espace s'effondre — et rien, nulle part, ne s'en apercevait. La
sécurité dépendait de l'humeur du moment.

Ce script retire la décision : il tire le code avec `secrets`, jamais avec
`random` ni avec l'horloge.

⚠️ L'ALPHABET EXCLUT CE QUI SE CONFOND : 0/O, 1/I/L, 5/S, 8/B. Il reste 28
signes, soit 3,8 × 10¹¹ combinaisons — toujours des millénaires derrière le
frein de C10 — et on gagne ce qui compte vraiment ici : un code se dicte au
téléphone et se recopie depuis WhatsApp, et « 0 ou O » est la faute qui fait
revenir le client.

⚠️ LA FICHE PASSE PAR UN FICHIER, pas par la ligne de commande. Elle contient
le nom de l'organisation, donc des guillemets, des accents et parfois une
apostrophe : la passer en argument la ferait casser sur le shell Windows, ou
pire, la tronquerait silencieusement au premier espace mal cité.
"""
import argparse
import io
import json
import os
import secrets
import subprocess
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                            # noqa: BLE001
    pass

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKER = os.path.join(os.path.dirname(RACINE), "Atmart_chat_worker")

# Sans les signes qui se confondent à l'oral ou à la lecture.
ALPHABET = "ACDEFGHJKMNPQRTUVWXYZ2346789"


def tirer():
    """EMP-XXXX-XXXX, tiré avec `secrets` — jamais `random`, jamais l'heure."""
    bloc = lambda: "".join(secrets.choice(ALPHABET) for _ in range(4))  # noqa: E731
    return "EMP-%s-%s" % (bloc(), bloc())


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--org", required=True, help="nom de l'organisation")
    ap.add_argument("--contact", default="", help="personne à contacter")
    ap.add_argument("--phone", default="", help="téléphone")
    ap.add_argument("--kind", default="company", choices=["company", "district"])
    ap.add_argument("--jours", type=int, default=90, help="durée d'accès")
    ap.add_argument("--quota", type=int, default=4, help="sélections incluses")
    ap.add_argument("--montrer", action="store_true",
                    help="affiche la commande sans rien écrire")
    a = ap.parse_args()

    code = tirer()
    exp = time.strftime("%Y-%m-%d", time.localtime(time.time() + a.jours * 86400))
    fiche = {
        "exp": exp, "org": a.org, "contact": a.contact, "phone": a.phone,
        "kind": a.kind, "credits": a.quota, "selected": [], "pend": [],
        "cree": time.strftime("%Y-%m-%d"),
    }
    ttl = a.jours * 86400 + 7 * 86400          # une semaine de marge après l'expiration
    fic = os.path.join(WORKER, ".emp-%s.json" % code)
    cmd = ('npx wrangler kv key put --binding=RATE_LIMIT --remote '
           '"emp:%s" --path "%s" --ttl %d' % (code, fic, ttl))

    print("  Code      : %s" % code)
    print("  Alphabet  : %d signes, sans 0/O ni 1/I/L — il se dicte au telephone"
          % len(ALPHABET))
    print("  Espace    : %.1e combinaisons" % (len(ALPHABET) ** 8))
    print("  Org       : %s" % a.org)
    print("  Expire le : %s (%d jours, %d selection(s))" % (exp, a.jours, a.quota))

    if a.montrer:
        print("\n  Rien n'a ete ecrit. La commande serait :")
        print("    " + cmd)
        return 0

    io.open(fic, "w", encoding="utf-8", newline="\n").write(
        json.dumps(fiche, ensure_ascii=False))
    try:
        r = subprocess.run(cmd, cwd=WORKER, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", shell=True)
    finally:
        # ⚠️ La fiche porte le nom et le telephone d'un client : elle ne reste
        # pas sur le disque, meme si wrangler echoue.
        try:
            os.remove(fic)
        except OSError:
            pass
    if r.returncode != 0:
        print("\n  ECHEC de l'ecriture dans le KV :")
        print((r.stderr or r.stdout or "").strip()[-800:])
        return 1
    print("\n  Ecrit dans le KV. A transmettre au client :")
    print("    %s" % code)
    return 0


if __name__ == "__main__":
    sys.exit(main())
