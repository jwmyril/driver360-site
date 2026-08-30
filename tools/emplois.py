# -*- coding: utf-8 -*-
"""
Les employeurs qui recrutent des chauffeurs au Massachusetts.

CE FICHIER EST LA SEULE SOURCE DE LA PAGE D'OFFRES. `gen_emplois.py` le lit et
fabrique `jobs.html` ; personne n'ecrit d'employeur directement dans le HTML.

TROIS REGLES, ET ELLES NE SE NEGOCIENT PAS
-------------------------------------------
1. ON NE REPUBLIE AUCUNE ANNONCE. Driver360 n'heberge pas d'offres et n'en
   recopie aucune. Il envoie le chauffeur vers la page de l'employeur, ou vers
   le site de l'Etat. C'est ce qui rend la page durable : aucune annonce ne
   perime, aucune condition d'utilisation d'un agregateur n'est enfreinte, et
   le chauffeur postule au bon endroit du premier coup.

2. AUCUNE URL N'ENTRE ICI SANS AVOIR ETE OUVERTE. Le champ `verifie` porte la
   date a laquelle l'adresse a renvoye 200. Une URL inventee qui tombe sur un
   404 coute la confiance d'un chauffeur qu'on ne revoit jamais.

3. LES SALAIRES SONT CITES AVEC LEUR DATE ET RENVOIENT A L'EMPLOYEUR. Un
   chiffre lu sur un agregateur en aout 2026 n'engage personne ; seule la page
   de l'employeur engage l'employeur. La page le dit explicitement.

Verification de toute la liste :
    python tools/gen_emplois.py --verifier
"""

# Date de la derniere verification collective des liens (toutes les URL ci-dessous
# ont renvoye HTTP 200 ce jour-la).
VERIFIE_LE = "2026-08-29"

# `genre` decide de la section : "board" = on cherche soi-meme,
# "ecole" = transport scolaire, "transit" = regie publique.
EMPLOYEURS = [
    dict(
        genre="board", nom="MassHire JobQuest", url="https://jobquest.mass.gov/",
        zone={"en": "Statewide", "fr": "Tout l'État", "ht": "Tout eta a", "es": "Todo el estado"},
        quoi={
            "en": "The state of Massachusetts runs its own job board. Search “driver” and your town. It is free, it is official, and it lists employers who never appear on the big commercial sites.",
            "fr": "L'État du Massachusetts tient son propre site d'emploi. Cherchez « driver » et votre ville. C'est gratuit, c'est officiel, et on y trouve des employeurs qui n'apparaissent jamais sur les grands sites commerciaux.",
            "ht": "Eta Massachusetts la gen pwòp sit travay pa l. Chèche « driver » ak vil ou. Li gratis, li ofisyèl, epi gen anplwayè ladan l ki pa janm parèt sou gwo sit komèsyal yo.",
            "es": "El estado de Massachusetts tiene su propia bolsa de empleo. Busca «driver» y tu ciudad. Es gratis, es oficial, y aparecen empleadores que nunca salen en los grandes sitios comerciales.",
        },
    ),
    dict(
        genre="board", nom="SchoolSpring", url="https://www.schoolspring.com/",
        zone={"en": "School districts", "fr": "Districts scolaires", "ht": "Distri lekòl yo", "es": "Distritos escolares"},
        quoi={
            "en": "Where Massachusetts school districts post their own openings — including van and bus driver posts they never advertise elsewhere.",
            "fr": "C'est là que les districts scolaires du Massachusetts publient leurs postes — y compris des postes de chauffeur de van et de bus qu'ils n'affichent nulle part ailleurs.",
            "ht": "Se la distri lekòl Massachusetts yo mete pòs pa yo — ak pòs chofè van ak bis yo pa janm anonse lòt kote.",
            "es": "Aquí es donde los distritos escolares de Massachusetts publican sus vacantes — incluidos puestos de conductor de van y de autobús que no anuncian en ningún otro sitio.",
        },
    ),
    dict(
        genre="ecole", nom="NRT Bus", url="https://nrtbus.com/careers/",
        zone={"en": "Eastern & Central MA", "fr": "Est et centre du Massachusetts",
              "ht": "Lès ak sant Massachusetts", "es": "Este y centro de Massachusetts"},
        quoi={
            "en": "School bus and 7D van routes across dozens of towns. Trains people who do not yet have a CDL.",
            "fr": "Circuits de bus scolaires et de vans 7D dans des dizaines de villes. Forme ceux qui n'ont pas encore de CDL.",
            "ht": "Wout bis lekòl ak van 7D nan plizyè douzèn vil. Yo fòme moun ki poko gen CDL.",
            "es": "Rutas de autobús escolar y van 7D en decenas de ciudades. Forma a quienes aún no tienen CDL.",
        },
    ),
    dict(
        genre="ecole", nom="First Student", url="https://firststudentinc.com/careers/",
        zone={"en": "Depots across MA", "fr": "Dépôts partout au Massachusetts",
              "ht": "Depo toupatou nan Massachusetts", "es": "Bases en todo Massachusetts"},
        quoi={
            "en": "The largest school bus operator in North America, with depots in many Massachusetts towns. Paid licence training is part of the job.",
            "fr": "Le plus gros transporteur scolaire d'Amérique du Nord, avec des dépôts dans de nombreuses villes du Massachusetts. La formation au permis est payée et fait partie du poste.",
            "ht": "Pi gwo konpayi bis lekòl nan Amerik di Nò, ak depo nan anpil vil Massachusetts. Fòmasyon pou pèmi a peye epi li fè pati travay la.",
            "es": "El mayor operador de autobuses escolares de Norteamérica, con bases en muchas ciudades de Massachusetts. La formación para la licencia es pagada y forma parte del puesto.",
        },
    ),
    dict(
        genre="transit", nom="MBTA", url="https://www.mbta.com/careers",
        zone={"en": "Greater Boston", "fr": "Grand Boston", "ht": "Gran Boston", "es": "Gran Boston"},
        quoi={
            "en": "Buses, the RIDE and support roles. Public-sector pay, benefits and a union.",
            "fr": "Bus, service RIDE et postes de soutien. Salaire du secteur public, avantages sociaux et syndicat.",
            "ht": "Bis, sèvis RIDE la ak lòt pòs. Salè sektè piblik, avantaj sosyal ak sendika.",
            "es": "Autobuses, el servicio RIDE y puestos de apoyo. Salario del sector público, prestaciones y sindicato.",
        },
    ),
    dict(
        genre="transit", nom="MART", url="https://www.mrta.us/job-postings/",
        zone={"en": "Fitchburg, Leominster, Gardner", "fr": "Fitchburg, Leominster, Gardner",
              "ht": "Fitchburg, Leominster, Gardner", "es": "Fitchburg, Leominster, Gardner"},
        quoi={
            "en": "The Montachusett regional transit authority: fixed routes and door-to-door medical transport in north-central Massachusetts.",
            "fr": "La régie de transport du Montachusett : lignes régulières et transport médical porte-à-porte dans le centre-nord du Massachusetts.",
            "ht": "Rejyon transpò Montachusett la : liy regilye ak transpò medikal pòt an pòt nan nò-santral Massachusetts.",
            "es": "La autoridad de transporte de Montachusett: líneas regulares y transporte médico puerta a puerta en el centro-norte de Massachusetts.",
        },
    ),
    dict(
        genre="transit", nom="WRTA", url="https://therta.com/about-us/careers/",
        zone={"en": "Worcester area", "fr": "Région de Worcester", "ht": "Zòn Worcester", "es": "Zona de Worcester"},
        quoi={
            "en": "The Worcester regional transit authority. Bus operators and paratransit drivers.",
            "fr": "La régie de transport de Worcester. Conducteurs de bus et chauffeurs de transport adapté.",
            "ht": "Rejyon transpò Worcester la. Chofè bis ak chofè transpò adapte.",
            "es": "La autoridad de transporte de Worcester. Operadores de autobús y conductores de transporte adaptado.",
        },
    ),
    dict(
        genre="transit", nom="PVTA", url="https://www.pvta.us/site/business-opportunites/career-opportunities/",
        zone={"en": "Springfield & the Valley", "fr": "Springfield et la vallée",
              "ht": "Springfield ak vale a", "es": "Springfield y el valle"},
        quoi={
            "en": "The Pioneer Valley transit authority, in the west of the state.",
            "fr": "La régie de transport de Pioneer Valley, dans l'ouest de l'État.",
            "ht": "Rejyon transpò Pioneer Valley la, nan lwès eta a.",
            "es": "La autoridad de transporte de Pioneer Valley, en el oeste del estado.",
        },
    ),
]

SECTIONS = [
    ("board", {"en": "Start here — search every opening yourself",
               "fr": "Commencez ici — chercher vous-même dans toutes les offres",
               "ht": "Kòmanse la — chèche tèt ou nan tout òf yo",
               "es": "Empieza aquí — busca tú mismo en todas las ofertas"}),
    ("ecole", {"en": "School and student transport",
               "fr": "Transport scolaire",
               "ht": "Transpò lekòl",
               "es": "Transporte escolar"}),
    ("transit", {"en": "Public transit authorities",
                 "fr": "Régies de transport public",
                 "ht": "Konpayi transpò piblik",
                 "es": "Autoridades de transporte público"}),
]
