# -*- coding: utf-8 -*-
"""Fabrique la doctrine des deux coachs LLM depuis les fichiers du dépôt.

    python tools/gen_doctrine.py             écrit src/doctrine.js du Worker
    python tools/gen_doctrine.py --verifier  échoue si le Worker est en retard

POURQUOI CE FICHIER EXISTE (ligne E19)
--------------------------------------
Les deux coachs répondent depuis un texte — leur « prompt système » — qui
vivait dans le Worker, **recopié à la main** depuis les données du site. Rien
ne reliait les deux. Résultat, mesuré le 31/08/2026, juste après avoir corrigé
les pages :

  · le Worker connaissait 12 manœuvres et 20 commandes. Le site en avait 13 et
    21 depuis E9 — le coach ne pouvait donc PAS faire travailler le démarrage
    en côte, la manœuvre officielle qui manquait et qu'on venait d'ajouter ;

  · le prompt disait de nommer si une faute serait « a minor point or an
    AUTOMATIC FAIL ». E7 avait fait retirer cette formule de toutes les pages,
    parce que **le RMV ne publie aucun barème** ;

  · le prompt affirmait « they have the RIGHT to bring an interpreter to the
    road test ». C'est faux. Le manuel écrit : « If the examiner so authorizes,
    a language interpreter may also be allowed. » E10 venait de l'écrire
    correctement sur la page — et le coach enseignait le contraire, à des gens
    dont c'est justement la question ;

  · le prompt s'ouvrait sur « for Creole- and Spanish-speaking learners »,
    alors que Driver360 s'adresse à TOUS les résidents du Massachusetts.

Un prompt que personne ne mesure dérive en silence, et il dérive vers ce qui
était vrai le jour où on l'a écrit.

CE QUE FAIT CE MODULE. Il lit `assets/komand.json`, la grille de manœuvres de
`wout.html` et `assets/pemi-questions.json`, et il écrit `src/doctrine.js`
dans le dépôt du Worker. Le Worker n'a plus de liste à lui : il importe
celle-ci. Le build échoue si les deux divergent.

⚠️ IL ÉCRIT DANS UN AUTRE DÉPÔT. C'est délibéré, et c'est le prix d'une source
unique : le Worker doit être redéployé après un changement de doctrine, et le
contrôle du build est là pour qu'on ne l'oublie pas.
"""
import io
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                            # noqa: BLE001
    pass

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKER = os.path.join(os.path.dirname(RACINE), "Atmart_chat_worker", "src",
                      "doctrine.js")

# La doctrine en toutes lettres. ELLE VIT ICI, à côté des données qu'elle
# commente — pas dans le Worker, où personne ne la relit en corrigeant une
# page.
DOCTRINE = """WHAT YOU MAY AND MAY NOT CLAIM — these rules override anything else in this prompt.

- AUDIENCE. Driver360 is for EVERY Massachusetts resident who wants driving work. You answer in the learner's language, and speaking Haitian Creole, Spanish or French is an advantage of the product, not a description of who it is for. Never address the learner as a member of a community.

- THE RMV PUBLISHES NO SCORING SHEET. Never say a mistake is an "automatic fail" or worth "points" ON THE REAL TEST. Our fault grid is OURS: say "in our grid this is disqualifying" or "in our grid this is a minor error". If a learner asks what the examiner scores, say plainly that the RMV does not publish a grid.

- THE INTERPRETER IS NOT A RIGHT. The manual says an interpreter "may also be allowed" IF THE EXAMINER SO AUTHORIZES. Never tell a learner they have the right to one. Tell them to ask when they book, and to drill the English commands so they do not depend on it.

- THE SPONSOR CANNOT HOLD A FOREIGN LICENCE. "Holders of foreign driver's licenses are not eligible to be sponsors." A sponsor is 21+, has one year of driving experience, and holds a valid licence from their own US state. No sponsor, no Class D test.

- NEVER STATE A NUMBER YOU WERE NOT GIVEN. Ages, fees, durations, deadlines, passing scores, curfew hours: only the figures that appear in this prompt or in the learner's file. If you do not have it, say so and send them to mass.gov. An invented figure costs someone a day of work and a $35 fee.

- CURFEWS DIFFER, AND THE DIFFERENCE MATTERS. Learner's permit under 18: no driving from MIDNIGHT to 5 a.m. Junior operator (JOL): 12:30 a.m. to 5 a.m. Both only with a parent or legal guardian. Driving on a permit at 12:15 a.m. is a criminal violation, not a ticket.

- YOU ARE NOT AFFILIATED WITH THE RMV. Preparation is independent, and passing is never guaranteed."""


def commandes():
    p = os.path.join(RACINE, "assets", "komand.json")
    d = json.load(io.open(p, encoding="utf-8"))
    return {c["id"]: c["en"] for c in d["commands"]}


def manoeuvres():
    """(ordre, libellés) lus dans la grille de wout.html, pas recopiés."""
    t = io.open(os.path.join(RACINE, "wout.html"), encoding="utf-8").read()
    trouve = re.findall(r'\{\s*id:"(\w+)",\s*ph:"(\w+)",\s*en:"([^"]*)"', t)
    if not trouve:
        raise SystemExit("gen_doctrine : la grille de manœuvres de wout.html "
                         "est introuvable — le format a-t-il changé ?")
    return [i for i, _, _ in trouve], {i: e for i, _, e in trouve}


def nb_questions():
    p = os.path.join(RACINE, "assets", "pemi-questions.json")
    d = json.load(io.open(p, encoding="utf-8"))
    return len(d["questions"]), d.get("total", 25), d.get("pass", 18)


def js():
    cmds = commandes()
    ids, libelles = manoeuvres()
    n, tire, seuil = nb_questions()

    def bloc(d):
        return "\n".join('  %s: %s,' % (k, json.dumps(v, ensure_ascii=False))
                         for k, v in d.items())

    return """// ⚠️ FICHIER GÉNÉRÉ — NE PAS MODIFIER À LA MAIN.
//
// Écrit par Driver360_site/tools/gen_doctrine.py depuis assets/komand.json,
// la grille de manœuvres de wout.html et assets/pemi-questions.json.
//
// POURQUOI. Ces listes vivaient en double : ici, et dans les fichiers du
// site. Le 31/08/2026 le Worker connaissait 12 manœuvres et 20 commandes
// quand le site en avait 13 et 21 — le coach ne pouvait donc pas faire
// travailler le démarrage en côte, qu'on venait justement d'ajouter parce
// que le manuel du RMV le liste. Un prompt recopié à la main dérive vers ce
// qui était vrai le jour où on l'a écrit.
//
// Pour changer une commande ou une manœuvre : modifier le SITE, relancer son
// build, puis redéployer ce Worker. Le build du site échoue si ce fichier
// est en retard.

export const WOUT_MANEUVERS = %s;

export const WOUT_MANEUVER_LABELS = {
%s
};

export const WOUT_COMMANDS = {
%s
};

export const WOUT_COMMAND_IDS = Object.keys(WOUT_COMMANDS);

// La banque du test écrit, telle qu'elle est publiée.
export const QUIZ = { total: %d, drawn: %d, pass: %d };

export const DOCTRINE = %s;
""" % (json.dumps(ids), bloc(libelles), bloc(cmds), n, tire, seuil,
       json.dumps(DOCTRINE, ensure_ascii=False))


def main():
    verifier = "--verifier" in sys.argv
    voulu = js()
    actuel = io.open(WORKER, encoding="utf-8").read() if os.path.exists(WORKER) else ""

    ids, _ = manoeuvres()
    cmds = commandes()
    resume = "%d manœuvre(s), %d commande(s)" % (len(ids), len(cmds))

    if actuel == voulu:
        print("     Doctrine : %s — le Worker est à jour" % resume)
        return 0
    if verifier:
        print("     Doctrine : le Worker est EN RETARD sur le site (%s)" % resume)
        print("     Les deux coachs répondraient depuis d'anciennes listes.")
        print("     Lancer tools/gen_doctrine.py, puis redéployer le Worker.")
        return 1

    os.makedirs(os.path.dirname(WORKER), exist_ok=True)
    io.open(WORKER + ".tmp", "w", encoding="utf-8", newline="\n").write(voulu)
    os.replace(WORKER + ".tmp", WORKER)
    print("     Doctrine : src/doctrine.js réécrit — %s" % resume)
    print("     ⚠️ le Worker doit être redéployé (npx wrangler deploy)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
