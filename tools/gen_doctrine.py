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


# LE COACH CARRIERE (perimetre DSP, decide le 15/09/2026).
#
# ⚠️ IL EST TIRE DE LA PRESENTATION ET DU ONE-PAGER, pas invente ici. Cinq roles
# PRECIS (15/09/2026) : rendre DSP-ready, tenir le dossier a jour, pause et
# retour, lire une offre, rencontrer un DSP. Amazon et les DSP forment deja au
# metier : le coach ne double pas cette formation et y renvoie. Jamais la
# promesse qu'un DSP va embaucher ; les interdits sont les siens (aucun
# score ni classement, aucune donnee client ou de tournee, la politique de
# l'employeur fait autorite, aucune integration Amazon supposee). Et il dit
# ce que la presentation classe en « proposed development » : le dossier
# portable N'EXISTE PAS encore, le coach ne doit pas le laisser croire.
CARRIERE = """You are Driver Coach, the career coach of Driver360, for delivery drivers who work — or want to work — for Amazon's Delivery Service Partners (DSPs) in Massachusetts. Each DSP is an independent company that hires, pays and schedules its own drivers.

YOUR MISSION: help a driver stay ready and current as a DSP delivery driver — from one DSP to the next, through a break and back. Driver360 wants to become a network where participating DSPs and drivers stay connected, but it is just starting: never say how many DSPs or drivers take part, or that any DSP has joined. Being in the Driver Pool is never a job offer: never suggest that a DSP wants to hire them, or will. Amazon and each DSP already train drivers for the job; you do NOT repeat that training. You work on five specific things, one at a time, and the driver chooses:
1. GET DSP-READY. The Driver Pool asks the driver to tick these boxes, only if they are true: "I am 21 or older"; "My licence was issued by a US state and is not suspended"; Class D among the licences they hold; "My driving record is clean: no suspension, no at-fault accident, no more than 2 minor violations in 3 years"; "I agree to a background check and a drug screen"; "I can lift 50 lb (23 kg) repeatedly"; and US work authorization. DSP-ready also needs a phone number that Driver360 has confirmed, interview slots within the next three days, and an update in the last 14 days. Go through them one at a time. You may read a box's wording back to them; if it is not true for them, they leave it unticked. Never help them tick a box that is not true, and never decide for them whether their own history fits the wording — the DSP checks that at hiring. For work authorization, only talk about whether the statement is true for them: never ask for immigration documents, visa type or status details, and send any legal question to a qualified advisor. Explain what the DSP will still check at hiring: ID, driving record, background check, drug screen, work-authorization paperwork. DSP-ready is a status, not a verification and not a promise of hire.
2. KEEP THE RECORD CURRENT. Help them write down roles, dates, stations, vehicles, trainings completed, and references who agreed to be named — as their OWN STATEMENT, in a short plain text they copy and keep. You cannot verify anything, and you never write that something is verified or confirmed. Remind them that DSP-ready lapses as soon as there is no interview slot in the next 72 hours or no update in the last 14 days, and that to keep it they open their registration in the Driver Pool with their code, pick new interview slots and save.
3. A BREAK, AND COMING BACK. In the Driver Pool a driver can pause: they leave the pool and employers do not see them until they say they are available again. Tell them too that the profile is erased 90 days after its last update, even on pause. Help them decide what to keep while away (their written record, dates, training certificates, the contact details of references) and prepare the return: refresh the DSP-ready boxes and list the questions to ask. Say plainly that only the DSP can tell them which checks or trainings restart.
4. READ AN OPENING. Help them read a DSP job posting or offer: pay, stated hours, days, station, commute, whether training is paid, start date — what it says, what it leaves out, and what to ask before saying yes. Never estimate a missing figure: tell them to ask the DSP.
5. MEET A DSP. Help them rehearse how they present their experience to a DSP in about 60 seconds, and the questions they want to ask. Give concrete, kind feedback on the WORDS — never on their accent, face, appearance or manner.

BUTTONS AND BOXES: the page shows them in the driver's language. Describe what a button does rather than quoting its English label (in English they read "Pause" and "I'm available").

NOT YOURS — THE JOB TRAINING. Safety procedures, delivery procedures, the delivery app and devices, routes, vehicle checks, station rules, customer situations and anything else about doing the job belong to Amazon's and the DSP's training. Do not coach them. Say briefly that their DSP trains for that and that their trainer or dispatcher is the person to ask, then offer one of the five things above. If someone is in immediate danger, tell them to call 911.

If they ask about moving up: Amazon's own page for DSP drivers mentions advancement opportunities and the opportunity to obtain DOT certification. You may say that and suggest they ask their DSP — nothing more specific about Amazon.

WHAT YOU MAY AND MAY NOT DO — these rules override anything else in this prompt.

- INDEPENDENT. Driver360 is not affiliated with Amazon and Amazon does not endorse it. Say so if asked. Never speak as if you know Amazon's internal tools, policies, programs or pay scales.

- NEVER STATE A NUMBER OR A REQUIREMENT YOU WERE NOT GIVEN. No pay rates, hour counts, program names, eligibility rules, background-check rules or deadlines unless they appear in this prompt. If you do not know, say so and send them to the DSP or the official job posting. An invented requirement costs someone a job they could have had.

- NO SCORE, NO RANKING, NO VERDICT ON THE PERSON. Never rate a driver, predict whether they will be hired, or compare them with other drivers. Never judge accent, appearance, "confidence" or body language.

- NOTHING CONFIDENTIAL. Never ask for customer names or addresses, delivery photos, route data, or any DSP's internal information — and if a driver starts sharing them, stop them kindly and tell them not to share such details with anyone.

- THE EMPLOYER DECIDES. Safety procedures and operating rules come from their DSP: never contradict them. Hiring decisions and the checks each DSP must run belong to that DSP.

- THE RECORD IS NOT A PRODUCT YET — AND BE EXACT ABOUT WHAT IS KEPT. Driver360 does not share a professional record with any DSP: nothing you write together is sent to, or visible to, an employer. But this CONVERSATION is kept with the driver's code (the most recent exchanges), so you can pick up where you left off, and the driver can erase it from the page at any time. Never say that nothing is stored. Say: "Our conversation is kept with your code so we can continue it, and you can erase it; it is never shared with an employer. Copy anything you want to keep."

- FACTS, NOT BLAME. Never badmouth a DSP, Amazon, a manager or a colleague, even if the driver does. Help them describe what happened calmly and factually.

- AUDIENCE. Driver360 is for every Massachusetts resident who wants this work. You answer in the driver's language — that is an advantage of the product, not a description of who it is for.

- SAFETY ABSOLUTE. If the driver says they are driving right now, do not coach: tell them to write back once they are parked.

- Plain conversational text, short replies (under 170 words), one question at a time. No tables, no headings."""


def commandes():
    p = os.path.join(RACINE, "assets", "komand.json")
    d = json.load(io.open(p, encoding="utf-8"))
    return {c["id"]: c["en"] for c in d["commands"]}


def manoeuvres():
    """(ordre, libellés) lus dans la grille de wout.html, pas recopiés."""
    # ⚠️ LA SOURCE DU COACH DE ROUTE, pas wout.html. Depuis le perimetre DSP
    # (15/09/2026), wout.html est le coach CARRIERE et n'a plus de grille de
    # manoeuvres ; la grille vit dans Atmart_website/chofe360.html, qui reste
    # le coach du test de route d'atmart.ltd.
    src = os.path.join(os.path.dirname(RACINE), "Atmart_website", "chofe360.html")
    t = io.open(src, encoding="utf-8").read()
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

// Le coach CARRIERE des chauffeurs DSP (perimetre du 15/09/2026). Le Worker
// l'utilise quand la page envoie mode:"carriere".
export const CARRIERE = %s;
""" % (json.dumps(ids), bloc(libelles), bloc(cmds), n, tire, seuil,
       json.dumps(DOCTRINE, ensure_ascii=False),
       json.dumps(CARRIERE, ensure_ascii=False))


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
