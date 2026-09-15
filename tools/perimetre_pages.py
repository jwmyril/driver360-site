# -*- coding: utf-8 -*-
"""Passe « périmètre DSP » sur les deux pages dérivées : le vivier et le portail.

Appelée par tools/regen.py APRÈS la dérivation et AVANT le rendu anglais
(rendre_en rejoue le dictionnaire de la page : c'est donc le dictionnaire
qu'on corrige, pas seulement le balisage).

POURQUOI (relecture critique du 15/09/2026, bloquant n° 2)
----------------------------------------------------------
L'accueil passait au périmètre DSP, mais les deux pages où mènent tous ses
boutons parlaient encore de transport scolaire, médical, MART, 7D et CDL. Un
DSP qui cliquait « I run or hire for a DSP » lisait, dès la page suivante,
« The portal for Massachusetts transport companies — school transport… ».
Convertir la moitié d'un système est pire que ne rien convertir.

Et deux affirmations du portail dépassaient la vérité :
  · « with results you can check » — l'accueil dit « We do not verify » ;
  · « nothing to check before you call » — le badge DSP-ready repose sur
    cinq attestations DÉCLARÉES, un permis et une autorisation de travail
    DÉCLARÉS ; seul le numéro est confirmé (phoneOk, posé par l'opérateur).
    La présentation à Ryan le dit : « required checks remain with each
    employer ».

⚠️ LES SOURCES D'ATMART.LTD NE SONT PAS TOUCHÉES. rejistre.html et
anplwaye360.html y restent des pages tous publics. La passe ne s'applique
qu'aux pages de Driver360, et seulement si portee.PORTEE == "dsp".

⚠️ Le kreyòl est à relire par l'utilisateur.
"""
import re

import portee

# Ordre des dictionnaires dans chaque source (relevé le 15/09/2026).
ORDRE = {"anplwaye.html": ("fr", "en", "ht", "es"),
         "vivye.html": ("fr", "ht", "en", "es")}

ANPLWAYE = {
 "ti": {"en": "Driver Employer — find DSP delivery drivers in Massachusetts | Driver360",
        "fr": "Driver Employer — trouver des chauffeurs livreurs DSP au Massachusetts | Driver360",
        "ht": "Driver Employer — jwenn chofè livrezon DSP nan Massachusetts | Driver360",
        "es": "Driver Employer — encuentra conductores de reparto DSP en Massachusetts | Driver360"},
 "kicker": {"en": "Find delivery drivers who asked to be found.",
            "fr": "Trouvez des chauffeurs livreurs qui ont demandé à être trouvés.",
            "ht": "Jwenn chofè livrezon ki mande pou yo jwenn yo.",
            "es": "Encuentra conductores de reparto que pidieron ser encontrados."},
 "lead": {"en": "The portal for Amazon Delivery Service Partners in Massachusetts: browse drivers who asked to be found, and reach them directly. Everything a driver tells us is declared, and your own required checks still apply. Driver360 is independent — not affiliated with Amazon.",
          "fr": "Le portail des partenaires de livraison d'Amazon au Massachusetts : parcourez des chauffeurs qui ont demandé à être trouvés, et joignez-les directement. Tout ce qu'un chauffeur nous dit est déclaré, et vos propres contrôles obligatoires s'appliquent toujours. Driver360 est indépendant — non affilié à Amazon.",
          "ht": "Pòtay patnè livrezon Amazon yo nan Massachusetts : gade chofè ki mande pou yo jwenn yo, epi kontakte yo dirèkteman. Tout sa yon chofè di nou se sa li deklare, epi pwòp kontwòl obligatwa pa w yo toujou aplike. Driver360 endepandan — li pa afilye ak Amazon.",
          "es": "El portal de los socios de entrega de Amazon en Massachusetts: revisa conductores que pidieron ser encontrados y contáctalos directamente. Todo lo que un conductor nos dice es declarado, y tus propias comprobaciones obligatorias siguen aplicándose. Driver360 es independiente — sin afiliación con Amazon."},
 "desc": {"en": "The Driver360 portal for Amazon DSPs in Massachusetts: browse delivery drivers who asked to be found, and reach them directly. Independent — not affiliated with Amazon.",
          "fr": "Le portail Driver360 des DSP d'Amazon au Massachusetts : parcourez des chauffeurs livreurs qui ont demandé à être trouvés, et joignez-les directement. Indépendant — non affilié à Amazon.",
          "ht": "Pòtay Driver360 pou DSP Amazon yo nan Massachusetts : gade chofè livrezon ki mande pou yo jwenn yo, epi kontakte yo dirèkteman. Endepandan — pa afilye ak Amazon.",
          "es": "El portal Driver360 para los DSP de Amazon en Massachusetts: revisa conductores de reparto que pidieron ser encontrados y contáctalos directamente. Independiente — sin afiliación con Amazon."},
 # ⚠️ PAS « Most DSPs use the pool » : le vivier est vide, on ne sait rien de
 # ce que font « la plupart des DSP ». On conseille, on ne raconte pas.
 "conseil": {"en": "Use the pool when you need drivers this week, and post an opening when you need volume. Both stay open to you.",
             "fr": "Passez par le vivier quand il vous faut des chauffeurs cette semaine, et publiez une offre quand il vous faut du volume. Les deux vous restent ouverts.",
             "ht": "Sèvi ak vivye a lè w bezwen chofè semèn sa a, epi pibliye yon òf lè w bezwen anpil moun. Tou de rete louvri pou ou.",
             "es": "Usa el registro cuando necesites conductores esta semana, y publica una oferta cuando necesites volumen. Ambas opciones siguen abiertas para ti."},
 "orgPh": {"en": "E.g.: ABC Delivery LLC", "fr": "Ex. : ABC Delivery LLC", "ht": "Egz. : ABC Delivery LLC", "es": "Ej.: ABC Delivery LLC"},
 "eoPOrg": {"en": "E.g.: ABC Delivery LLC", "fr": "Ex. : ABC Delivery LLC", "ht": "Egz. : ABC Delivery LLC", "es": "Ej.: ABC Delivery LLC"},
 "eoPPoste": {"en": "E.g.: Delivery driver, full time", "fr": "Ex. : Chauffeur livreur, temps plein",
              "ht": "Egz. : Chofè livrezon, tan plèn", "es": "Ej.: Conductor de reparto, jornada completa"},
 "eoPZone": {"en": "E.g.: Worcester station and around", "fr": "Ex. : Station de Worcester et alentours",
             "ht": "Egz. : Estasyon Worcester ak alantou", "es": "Ej.: Estación de Worcester y alrededores"},
 "eoPPlus": {"en": "Hours, advertised pay, paid training, station…", "fr": "Horaires, salaire affiché, formation payée, station…",
             "ht": "Orè, salè afiche, fòmasyon ki peye, estasyon…", "es": "Horario, salario anunciado, formación pagada, estación…"},
 "Lneeds": {"en": "What you need (optional) <small>E.g.: 5 delivery drivers for the Worcester station, starting Monday; profile sought…</small>",
            "fr": "Ce qu'il vous faut (facultatif) <small>Ex. : 5 chauffeurs livreurs pour la station de Worcester, dès lundi ; profil recherché…</small>",
            "ht": "Sa w bezwen (si w vle) <small>Egz. : 5 chofè livrezon pou estasyon Worcester, depi lendi ; ki pwofil w ap chèche…</small>",
            "es": "Lo que necesitas (opcional) <small>Ej.: 5 conductores de reparto para la estación de Worcester, desde el lunes; perfil buscado…</small>"},
 "hDsp": {"en": "\U0001F69A DSP-ready pool", "fr": "\U0001F69A Vivier DSP-ready", "ht": "\U0001F69A Vivye DSP-ready", "es": "\U0001F69A Registro DSP-ready"},
 "subDsp": {"en": "These drivers declared the five things a DSP asks about, a Class D licence and work authorization — declared, not verified by us. Their phone number was confirmed on WhatsApp, and they offered an interview slot within 72 hours. Your own required checks still apply.",
            "fr": "Ces chauffeurs ont déclaré les cinq points qu'un DSP demande, un permis Class D et une autorisation de travail — déclarés, non vérifiés par nous. Leur numéro a été confirmé sur WhatsApp, et ils ont proposé un créneau d'entretien sous 72 heures. Vos propres contrôles obligatoires s'appliquent toujours.",
            "ht": "Chofè sa yo te deklare senk bagay yon DSP mande, yon pèmi Class D ak yon otorizasyon travay — se yo ki deklare sa, nou pa verifye l. Nimewo yo te konfime sou WhatsApp, epi yo te pwopoze yon lè pou entèvyou nan 72 èdtan. Pwòp kontwòl obligatwa pa w yo toujou aplike.",
            "es": "Estos conductores declararon los cinco puntos que pide un DSP, una licencia Class D y autorización de trabajo — declarados, no verificados por nosotros. Su número se confirmó por WhatsApp y ofrecieron un horario de entrevista en menos de 72 horas. Tus propias comprobaciones obligatorias siguen aplicándose."},
 "dspFilter": {"en": "DSP-ready only", "fr": "DSP-ready seulement", "ht": "DSP-ready sèlman", "es": "Solo DSP-ready"},
 "dspTip": {"en": "Declared by the driver: 21+, US-state licence, authorized to work, clean record, agrees to a background check and drug screen, lifts 50 lb. Confirmed by us: phone number. Offered: an interview slot within 72 h. Updated less than 14 days ago.",
            "fr": "Déclaré par le chauffeur : 21 ans et plus, permis d'un État américain, autorisé à travailler, dossier propre, accepte une vérification d'antécédents et un dépistage, soulève 50 lb. Confirmé par nous : le numéro de téléphone. Proposé : un créneau d'entretien sous 72 h. Mis à jour il y a moins de 14 jours.",
            "ht": "Chofè a deklare : 21 an oswa plis, pèmi yon Eta ameriken, otorize pou travay, dosye pwòp, dakò pou yo verifye dosye l epi fè tès dwòg, ka leve 50 liv. Nou konfime : nimewo telefòn nan. Li pwopoze : yon lè pou entèvyou nan 72 èdtan. Mete ajou gen mwens pase 14 jou.",
            "es": "Declarado por el conductor: 21 años o más, licencia de un estado de EE. UU., autorizado para trabajar, historial limpio, acepta verificación de antecedentes y prueba de drogas, levanta 50 lb. Confirmado por nosotros: el número de teléfono. Ofrecido: un horario de entrevista en menos de 72 h. Actualizado hace menos de 14 días."},
}

VIVYE = {
 "ti": {"en": "Driver360 — Join the Driver Pool for DSP delivery drivers (free)",
        "fr": "Driver360 — Rejoindre le Driver Pool des chauffeurs livreurs DSP (gratuit)",
        "ht": "Driver360 — Antre nan Driver Pool chofè livrezon DSP yo (gratis)",
        "es": "Driver360 — Únete al Driver Pool de conductores de reparto DSP (gratis)"},
 "descr": {"en": "Deliver, or want to deliver, for an Amazon DSP in Massachusetts? Join the Driver Pool free. DSPs contact you only if you agree. Independent — not affiliated with Amazon.",
           "fr": "Vous livrez, ou voulez livrer, pour un DSP d'Amazon au Massachusetts ? Rejoignez gratuitement le Driver Pool. Les DSP ne vous contactent que si vous êtes d'accord. Indépendant — non affilié à Amazon.",
           "ht": "W ap livre, oswa ou vle livre, pou yon DSP Amazon nan Massachusetts ? Antre gratis nan Driver Pool la. DSP yo kontakte w sèlman si w dakò. Endepandan — pa afilye ak Amazon.",
           "es": "¿Repartes, o quieres repartir, para un DSP de Amazon en Massachusetts? Únete gratis al Driver Pool. Los DSP solo te contactan si estás de acuerdo. Independiente — sin afiliación con Amazon."},
 "lead": {"en": "Do you deliver, or want to deliver, for an Amazon DSP? Register for free: DSPs in Massachusetts can find you — and contact you only if you agree. Driver360 is independent and not affiliated with Amazon.",
          "fr": "Vous livrez, ou voulez livrer, pour un DSP d'Amazon ? Inscrivez-vous gratuitement : les DSP du Massachusetts peuvent vous trouver — et ne vous contactent que si vous êtes d'accord. Driver360 est indépendant et non affilié à Amazon.",
          "ht": "W ap livre, oswa ou vle livre, pou yon DSP Amazon ? Enskri gratis : DSP nan Massachusetts ka jwenn ou — epi yo kontakte w sèlman si w dakò. Driver360 endepandan epi li pa afilye ak Amazon.",
          "es": "¿Repartes, o quieres repartir, para un DSP de Amazon? Regístrate gratis: los DSP de Massachusetts pueden encontrarte — y solo te contactan si estás de acuerdo. Driver360 es independiente y no está afiliado a Amazon."},
 "dspOkS": {"en": "A delivery employer sees you with this badge, and none of your answers in detail. It needs an interview slot in the next 72 hours and an update in the last 14 days: to keep it, open your registration with your code, pick new interview slots and save.",
            "fr": "Un employeur de livraison vous voit avec ce badge, sans aucune de vos réponses en détail. Il demande un créneau d'entretien dans les 72 heures et une mise à jour dans les 14 derniers jours : pour le garder, rouvrez votre inscription avec votre code, choisissez de nouveaux créneaux et enregistrez.",
            "ht": "Yon anplwayè livrezon wè w ak badj sa a, san okenn nan repons ou yo an detay. Li mande yon lè pou entèvyou nan 72 èdtan ki vini yo ak yon mizajou nan 14 dènye jou yo : pou w kenbe l, louvri enskripsyon w ak kòd ou, chwazi lòt moman pou entèvyou epi anrejistre.",
            "es": "Un empleador de reparto te ve con esta insignia, sin ninguna de tus respuestas en detalle. Requiere un horario de entrevista en las próximas 72 horas y una actualización en los últimos 14 días: para mantenerla, abre tu inscripción con tu código, elige nuevos horarios de entrevista y guarda."},
}

# La valeur d'une cle JS entre guillemets doubles, echappements compris.
def _motif(cle):
    return re.compile(r'(\b%s\s*:\s*")((?:[^"\\]|\\.)*)(")' % re.escape(cle))


def _js(v):
    return v.replace("\\", "\\\\").replace('"', '\\"')


def _cles(s, page, table):
    ordre = ORDRE[page]
    for cle, trad in table.items():
        m = list(_motif(cle).finditer(s))
        if len(m) != 4:
            raise SystemExit("perimetre_pages : %s « %s » trouvee %d fois (4 attendues)" % (page, cle, len(m)))
        # de la fin vers le debut : les positions restent valables
        for lg, mm in reversed(list(zip(ordre, m))):
            s = s[:mm.start(2)] + _js(trad[lg]) + s[mm.end(2):]
    return s


def _un(s, avant, apres, n=None, page=""):
    c = s.count(avant)
    if c == 0 or (n is not None and c != n):
        raise SystemExit("perimetre_pages : %s — %r trouve %d fois" % (page, avant[:60], c))
    return s.replace(avant, apres)


CSS_ANPLWAYE = """<style>/* perimetre DSP (15/09/2026) : le vivier 7D est hors perimetre. On le
   masque au lieu de le retirer — le script de la page cherche ses elements
   par identifiant et casserait s'ils disparaissaient. */
#ep-h-7d,#ep-empty-7d,.ep-wrap:has(#ep-t-7d),
#ep-h-cd,#ep-empty-cd,.ep-wrap:has(#ep-t-cd){display:none!important}</style>
"""

CSS_VIVYE = """<style>/* perimetre DSP (15/09/2026) : ni 7D, ni transport scolaire, medical ou
   regional. Masques plutot que retires : le script traduit ces libelles par
   identifiant, et une case retiree casserait l'enregistrement du profil. */
.rj-chk:has(input[value="7d"]),.rj-chk:has(input[value="school"]),
.rj-chk:has(input[value="senior"]),.rj-chk:has(input[value="transit"]){display:none!important}</style>
"""


def appliquer(page, s):
    if not portee.dsp() or page not in ORDRE:
        return s
    if page == "anplwaye.html":
        s = _cles(s, page, ANPLWAYE)
        # les exemples du tableau de demonstration : plus de 7D ni d'ecole
        s = _un(s, "7D · Class D", "Class D", page=page)
        s = _un(s, "\U0001F4E6 \U0001F3EB", "\U0001F4E6", page=page)
        # la voie « publier une offre » citait la rentree scolaire comme exemple
        for av, ap in ((" Pour une rentrée scolaire, un recrutement saisonnier.", " Pour une nouvelle station ou un pic saisonnier."),
                       (" For a school year, a seasonal hire.", " For a new station or a seasonal peak."),
                       (" Pou yon rantre lekòl, yon rekritman sezonye.", " Pou yon nouvo estasyon oswa yon sezon kote gen anpil travay."),
                       (" Para un inicio de curso, una contratación de temporada.", " Para una nueva estación o un pico de temporada.")):
            s = _un(s, av, ap, page=page)
        # « Vous etes » : le DSP d'abord, et plus de scolaire, district, medical, regional
        sel = re.search(r'(<select id="ep-kind">)(.*?)(</select>)', s, re.S)
        if not sel:
            raise SystemExit("perimetre_pages : select ep-kind introuvable")
        options = ('\n          <option value="dsp" selected>\U0001F4E6 Amazon DSP</option>'
                   '\n          <option value="delivery">\U0001F4E6 Package delivery</option>'
                   '\n          <option value="other">\U0001F695 Other transport</option>\n        ')
        s = s[:sel.start(2)] + options + s[sel.end(2):]
        # le courriel « on cherche des chauffeurs » demandait « Class D / 7D / CDL »
        s = _un(s, "Company%3A%0ATown%20or%20area%3A%0ALicence%20needed%20%28Class%20D%20/%207D%20/%20CDL%29%3A%0A",
                "DSP%20name%3A%0AStation%20or%20area%3A%0A", page=page)
        s = s.replace("</head>", CSS_ANPLWAYE + "</head>", 1)
    elif page == "vivye.html":
        s = _cles(s, page, VIVYE)
        s = _un(s, '<label class="rj-chk"><input type="checkbox" value="delivery" />',
                '<label class="rj-chk on"><input type="checkbox" value="delivery" checked />', n=1, page=page)
        s = s.replace("</head>", CSS_VIVYE + "</head>", 1)
    return s
