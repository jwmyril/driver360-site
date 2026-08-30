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

2. AUCUNE URL N'ENTRE ICI SANS AVOIR ETE OUVERTE. Le champ `VERIFIE_LE` porte
   la date a laquelle toutes ont renvoye 200. Une URL inventee qui tombe sur un
   404 coute la confiance d'un chauffeur qu'on ne revoit jamais.

3. LES SALAIRES SONT CITES AVEC LEUR DATE ET RENVOIENT A L'EMPLOYEUR. Un
   chiffre lu sur un agregateur en aout 2026 n'engage personne ; seule la page
   de l'employeur engage l'employeur. La page le dit explicitement.

CORRECTION DE CAP DU 30/08/2026 — L'UTILISATEUR AVAIT RAISON
-------------------------------------------------------------
La premiere version penchait lourdement vers le transport SCOLAIRE : sur huit
entrees, deux etaient des bus scolaires, une un site de districts, et le seul
salaire cite etait celui d'un chauffeur de bus scolaire. C'etait un heritage
de Driver Coach (le 7D est un permis scolaire) — mais le chauffeur qui cherche
un emploi, lui, se moque de savoir d'ou vient le produit.

Le marche reel est ailleurs, et il est plus grand : en aout 2026, environ 575
postes de livreur Amazon DSP etaient annonces au Massachusetts, SANS CDL,
contre une centaine de postes scolaires. La livraison de colis passe donc
devant, et le scolaire devient une section parmi sept.

`genre` decide de la section. Ordre voulu : on cherche d'abord soi-meme, puis
les secteurs SANS CDL (accessibles avec un simple Class D), puis ceux qui
demandent un permis lourd.
"""

# Date de la derniere verification collective des liens (toutes les URL
# ci-dessous ont renvoye HTTP 200 ce jour-la).
VERIFIE_LE = "2026-08-30"

EMPLOYEURS = [
    # ---------------------------------------------------------- on cherche
    dict(
        genre="board", nom="MassHire JobQuest", url="https://jobquest.mass.gov/",
        zone={"en": "Statewide, every sector", "es": "Todo el estado, todos los sectores",
              "ht": "Tout eta a, tout sektè", "fr": "Tout l'État, tous secteurs"},
        quoi={
            "en": "The state of Massachusetts runs its own job board. Search “driver” and your town: school, delivery, medical, transit, trucking — everything is there, including employers who never appear on the big commercial sites.",
            "es": "El estado de Massachusetts tiene su propia bolsa de empleo. Busca «driver» y tu ciudad: escolar, reparto, médico, transporte público, camión — está todo, incluidos empleadores que nunca salen en los grandes sitios comerciales.",
            "ht": "Eta Massachusetts la gen pwòp sit travay pa l. Chèche « driver » ak vil ou : lekòl, livrezon, medikal, transpò piblik, kamyon — tout bagay la, ak anplwayè ki pa janm parèt sou gwo sit komèsyal yo.",
            "fr": "L'État du Massachusetts tient son propre site d'emploi. Cherchez « driver » et votre ville : scolaire, livraison, médical, transport public, camion — tout y est, y compris des employeurs qui n'apparaissent jamais sur les grands sites commerciaux.",
        },
    ),
    # ------------------------------------------- livraison (aucun CDL exige)
    dict(
        genre="livraison", nom="Amazon", url="https://hiring.amazon.com",
        zone={"en": "Depots across the state", "es": "Centros en todo el estado",
              "ht": "Depo toupatou nan eta a", "fr": "Dépôts dans tout l'État"},
        quoi={
            "en": "Delivery vans, through Amazon's partner companies. <strong>No CDL needed</strong> — a Class D licence and a clean record are enough. It is the biggest single source of driving work in the state right now.",
            "es": "Furgonetas de reparto, a través de las empresas socias de Amazon. <strong>No hace falta CDL</strong> — basta una licencia Class D y un historial limpio. Es la mayor fuente de empleo de conductor del estado ahora mismo.",
            "ht": "Kamyonèt livrezon, atravè konpayi patnè Amazon yo. <strong>Ou pa bezwen CDL</strong> — yon pèmi Class D ak yon dosye pwòp ase. Se pi gwo sous travay chofè nan eta a kounye a.",
            "fr": "Camionnettes de livraison, via les sociétés partenaires d'Amazon. <strong>Aucun CDL exigé</strong> — un permis Class D et un dossier propre suffisent. C'est aujourd'hui la plus grosse source d'emplois de chauffeur de l'État.",
        },
    ),
    dict(
        genre="livraison", nom="FedEx", url="https://careers.fedex.com",
        zone={"en": "Statewide", "es": "Todo el estado", "ht": "Tout eta a", "fr": "Tout l'État"},
        quoi={
            "en": "Package delivery and line haul. Some routes take a Class D, the heavier ones a CDL.",
            "es": "Reparto de paquetes y transporte de línea. Algunas rutas admiten Class D, las más pesadas exigen CDL.",
            "ht": "Livrezon pake ak transpò long distans. Kèk wout aksepte Class D, sa ki pi lou yo mande CDL.",
            "fr": "Livraison de colis et transport longue distance. Certaines tournées se font en Class D, les plus lourdes en CDL.",
        },
    ),
    dict(
        genre="livraison", nom="UPS", url="https://www.jobs-ups.com",
        zone={"en": "Statewide", "es": "Todo el estado", "ht": "Tout eta a", "fr": "Tout l'État"},
        quoi={
            "en": "Delivery and warehouse work, unionised, with seasonal hiring peaks. Some driving posts are filled from inside the warehouse.",
            "es": "Reparto y trabajo de almacén, con sindicato y picos de contratación estacionales. Algunos puestos de conductor se cubren desde el almacén.",
            "ht": "Livrezon ak travay depo, ak sendika, epi gen sezon kote yo anboche plis. Gen pòs chofè yo ranpli ak moun ki soti nan depo a.",
            "fr": "Livraison et travail d'entrepôt, syndiqué, avec des pics d'embauche saisonniers. Certains postes de conduite sont pourvus depuis l'entrepôt.",
        },
    ),
    # --------------------------------------- medical, personnes agees, adapte
    dict(
        genre="medical", nom="Modivcare", url="https://www.modivcare.com/company/careers/",
        zone={"en": "Statewide", "es": "Todo el estado", "ht": "Tout eta a", "fr": "Tout l'État"},
        quoi={
            "en": "Non-emergency medical transport: taking people to their appointments. Class D is usually enough; a first-aid certificate is often asked for.",
            "es": "Transporte médico no urgente: llevar a las personas a sus citas. Suele bastar la Class D; a menudo piden un certificado de primeros auxilios.",
            "ht": "Transpò medikal ki pa ijans : mennen moun nan randevou yo. Class D ase anjeneral ; souvan yo mande yon sètifika premye swen.",
            "fr": "Transport médical non urgent : conduire les gens à leurs rendez-vous. Le Class D suffit en général ; un certificat de premiers secours est souvent demandé.",
        },
    ),
    dict(
        genre="medical", nom="Transdev", url="https://transdevna.jobs/",
        zone={"en": "Greater Boston and beyond", "es": "Gran Boston y alrededores",
              "ht": "Gran Boston ak pi lwen", "fr": "Grand Boston et au-delà"},
        quoi={
            "en": "Operates paratransit and shuttle services under contract, including part of the MBTA's door-to-door service.",
            "es": "Opera servicios de transporte adaptado y lanzaderas por contrato, incluida parte del servicio puerta a puerta de la MBTA.",
            "ht": "Yo dirije sèvis transpò adapte ak navèt sou kontra, ak yon pati nan sèvis pòt an pòt MBTA a.",
            "fr": "Exploite des services de transport adapté et des navettes sous contrat, dont une partie du service porte-à-porte de la MBTA.",
        },
    ),
    dict(
        genre="medical", nom="MART", url="https://www.mrta.us/job-postings/",
        zone={"en": "Fitchburg, Leominster, Gardner", "es": "Fitchburg, Leominster, Gardner",
              "ht": "Fitchburg, Leominster, Gardner", "fr": "Fitchburg, Leominster, Gardner"},
        quoi={
            "en": "The Montachusett authority: fixed routes and door-to-door medical transport in north-central Massachusetts. It is also the state's broker for MassHealth rides.",
            "es": "La autoridad de Montachusett: líneas regulares y transporte médico puerta a puerta en el centro-norte de Massachusetts. También gestiona los viajes de MassHealth para el estado.",
            "ht": "Otorite Montachusett la : liy regilye ak transpò medikal pòt an pòt nan nò-santral Massachusetts. Se li menm tou ki jere vwayaj MassHealth yo pou eta a.",
            "fr": "La régie du Montachusett : lignes régulières et transport médical porte-à-porte dans le centre-nord du Massachusetts. C'est aussi le courtier de l'État pour les trajets MassHealth.",
        },
    ),
    # ------------------------------------------------------ transport public
    dict(
        genre="transit", nom="MBTA", url="https://www.mbta.com/careers",
        zone={"en": "Greater Boston", "es": "Gran Boston", "ht": "Gran Boston", "fr": "Grand Boston"},
        quoi={
            "en": "Buses, the RIDE and support roles. Public-sector pay, benefits and a union. CDL training is provided for bus operators.",
            "es": "Autobuses, el servicio RIDE y puestos de apoyo. Salario público, prestaciones y sindicato. La formación de CDL está incluida para los operadores.",
            "ht": "Bis, sèvis RIDE la ak lòt pòs. Salè sektè piblik, avantaj sosyal ak sendika. Fòmasyon CDL a bay pou chofè bis yo.",
            "fr": "Bus, service RIDE et postes de soutien. Salaire du secteur public, avantages sociaux et syndicat. La formation au CDL est assurée pour les conducteurs de bus.",
        },
    ),
    dict(
        genre="transit", nom="WRTA", url="https://therta.com/about-us/careers/",
        zone={"en": "Worcester area", "es": "Zona de Worcester", "ht": "Zòn Worcester", "fr": "Région de Worcester"},
        quoi={
            "en": "The Worcester regional authority. Bus operators and paratransit drivers.",
            "es": "La autoridad regional de Worcester. Operadores de autobús y conductores de transporte adaptado.",
            "ht": "Otorite rejyonal Worcester la. Chofè bis ak chofè transpò adapte.",
            "fr": "La régie régionale de Worcester. Conducteurs de bus et chauffeurs de transport adapté.",
        },
    ),
    dict(
        genre="transit", nom="PVTA", url="https://www.pvta.us/site/business-opportunites/career-opportunities/",
        zone={"en": "Springfield & the Valley", "es": "Springfield y el valle",
              "ht": "Springfield ak vale a", "fr": "Springfield et la vallée"},
        quoi={
            "en": "The Pioneer Valley authority, in the west of the state.",
            "es": "La autoridad de Pioneer Valley, en el oeste del estado.",
            "ht": "Otorite Pioneer Valley la, nan lwès eta a.",
            "fr": "La régie de Pioneer Valley, dans l'ouest de l'État.",
        },
    ),
    # ------------------------------------------------------------- autocars
    dict(
        genre="car", nom="Peter Pan Bus Lines", url="https://www.peterpanbus.com/employment/",
        zone={"en": "Springfield, Boston, Worcester", "es": "Springfield, Boston, Worcester",
              "ht": "Springfield, Boston, Worcester", "fr": "Springfield, Boston, Worcester"},
        quoi={
            "en": "A Massachusetts motorcoach company: intercity lines and charters. CDL with a passenger endorsement.",
            "es": "Empresa de autocares de Massachusetts: líneas interurbanas y servicios discrecionales. CDL con habilitación de pasajeros.",
            "ht": "Yon konpayi otokar Massachusetts : liy ant vil ak vwayaj espesyal. CDL ak andòsman pasaje.",
            "fr": "Un autocariste du Massachusetts : lignes interurbaines et voyages en groupe. CDL avec mention voyageurs.",
        },
    ),
    dict(
        genre="car", nom="DATTCO", url="https://dattco.com/join-our-team/",
        zone={"en": "Massachusetts and New England", "es": "Massachusetts y Nueva Inglaterra",
              "ht": "Massachusetts ak New England", "fr": "Massachusetts et Nouvelle-Angleterre"},
        quoi={
            "en": "Motorcoach, school transport and shuttles across the region. Trains people who do not yet have a CDL.",
            "es": "Autocares, transporte escolar y lanzaderas en toda la región. Forma a quienes aún no tienen CDL.",
            "ht": "Otokar, transpò lekòl ak navèt nan tout rejyon an. Yo fòme moun ki poko gen CDL.",
            "fr": "Autocars, transport scolaire et navettes dans toute la région. Forme ceux qui n'ont pas encore de CDL.",
        },
    ),
    dict(
        genre="car", nom="Academy Bus", url="https://academybus.com/careers",
        zone={"en": "Boston commuter lines", "es": "Líneas de cercanías de Boston",
              "ht": "Liy navèt Boston yo", "fr": "Lignes de banlieue de Boston"},
        quoi={
            "en": "Commuter coaches and corporate shuttles into Boston.",
            "es": "Autocares de cercanías y lanzaderas de empresa hacia Boston.",
            "ht": "Otokar pou moun k ap vwayaje chak jou ak navèt konpayi pou Boston.",
            "fr": "Autocars de banlieue et navettes d'entreprise vers Boston.",
        },
    ),
    # ------------------------------------------------------------- scolaire
    dict(
        genre="ecole", nom="NRT Bus", url="https://nrtbus.com/careers/",
        zone={"en": "Eastern & Central MA", "es": "Este y centro de Massachusetts",
              "ht": "Lès ak sant Massachusetts", "fr": "Est et centre du Massachusetts"},
        quoi={
            "en": "School bus and 7D van routes across dozens of towns. Trains people who do not yet have a CDL.",
            "es": "Rutas de autobús escolar y van 7D en decenas de ciudades. Forma a quienes aún no tienen CDL.",
            "ht": "Wout bis lekòl ak van 7D nan plizyè douzèn vil. Yo fòme moun ki poko gen CDL.",
            "fr": "Circuits de bus scolaires et de vans 7D dans des dizaines de villes. Forme ceux qui n'ont pas encore de CDL.",
        },
    ),
    dict(
        genre="ecole", nom="First Student", url="https://firststudentinc.com/careers/",
        zone={"en": "Depots across MA", "es": "Bases en todo Massachusetts",
              "ht": "Depo toupatou nan Massachusetts", "fr": "Dépôts partout au Massachusetts"},
        quoi={
            "en": "The largest school bus operator in North America. Paid licence training is part of the job.",
            "es": "El mayor operador de autobuses escolares de Norteamérica. La formación para la licencia es pagada y forma parte del puesto.",
            "ht": "Pi gwo konpayi bis lekòl nan Amerik di Nò. Fòmasyon pou pèmi a peye epi li fè pati travay la.",
            "fr": "Le plus gros transporteur scolaire d'Amérique du Nord. La formation au permis est payée et fait partie du poste.",
        },
    ),
    dict(
        genre="ecole", nom="SchoolSpring", url="https://www.schoolspring.com/",
        zone={"en": "School districts", "es": "Distritos escolares",
              "ht": "Distri lekòl yo", "fr": "Districts scolaires"},
        quoi={
            "en": "Where Massachusetts school districts post their own openings — including van and bus driver posts they never advertise elsewhere.",
            "es": "Donde los distritos escolares de Massachusetts publican sus vacantes — incluidos puestos de conductor de van y autobús que no anuncian en ningún otro sitio.",
            "ht": "Se la distri lekòl Massachusetts yo mete pòs pa yo — ak pòs chofè van ak bis yo pa janm anonse lòt kote.",
            "fr": "C'est là que les districts scolaires du Massachusetts publient leurs postes — y compris des postes de chauffeur de van et de bus qu'ils n'affichent nulle part ailleurs.",
        },
    ),
    # ------------------------------------------- poids lourd (CDL demande)
    dict(
        genre="cdl", nom="Sysco", url="https://jobs.sysco.com",
        zone={"en": "Plympton distribution centre", "es": "Centro de distribución de Plympton",
              "ht": "Sant distribisyon Plympton", "fr": "Centre de distribution de Plympton"},
        quoi={
            "en": "Food distribution to restaurants. CDL-A, early starts, among the best-paid driving work in the state.",
            "es": "Distribución de alimentos a restaurantes. CDL-A, madrugones, y de los empleos de conductor mejor pagados del estado.",
            "ht": "Distribisyon manje bay restoran. CDL-A, ou leve bonè, epi se pami travay chofè ki pi byen peye nan eta a.",
            "fr": "Distribution alimentaire aux restaurants. CDL-A, départs très tôt, et parmi les postes de conduite les mieux payés de l'État.",
        },
    ),
    dict(
        genre="cdl", nom="US Foods", url="https://careers.usfoods.com/us/en",
        zone={"en": "Seabrook & Peabody area", "es": "Zona de Seabrook y Peabody",
              "ht": "Zòn Seabrook ak Peabody", "fr": "Région de Seabrook et Peabody"},
        quoi={
            "en": "The other big food distributor serving New England. CDL-A, with delivery routes rather than long haul.",
            "es": "El otro gran distribuidor de alimentos de Nueva Inglaterra. CDL-A, con rutas de reparto más que larga distancia.",
            "ht": "Lòt gwo distribitè manje ki sèvi New England. CDL-A, ak wout livrezon olye long distans.",
            "fr": "L'autre grand distributeur alimentaire de Nouvelle-Angleterre. CDL-A, sur des tournées plutôt que de la longue distance.",
        },
    ),
    dict(
        genre="cdl", nom="WM", url="https://careers.wm.com",
        zone={"en": "Statewide", "es": "Todo el estado", "ht": "Tout eta a", "fr": "Tout l'État"},
        quoi={
            "en": "Waste collection. CDL-B, local routes, home every night — and they train people who do not have the licence yet.",
            "es": "Recogida de residuos. CDL-B, rutas locales, en casa cada noche — y forman a quienes aún no tienen la licencia.",
            "ht": "Ranmase fatra. CDL-B, wout lokal, ou lakay ou chak swa — epi yo fòme moun ki poko gen pèmi a.",
            "fr": "Collecte des déchets. CDL-B, tournées locales, à la maison tous les soirs — et ils forment ceux qui n'ont pas encore le permis.",
        },
    ),
    dict(
        genre="cdl", nom="Republic Services", url="https://jobs.republicservices.com",
        zone={"en": "Statewide", "es": "Todo el estado", "ht": "Tout eta a", "fr": "Tout l'État"},
        quoi={
            "en": "The other big waste operator. Same idea: local routes, fixed hours, licence training available.",
            "es": "El otro gran operador de residuos. La misma idea: rutas locales, horario fijo, formación de licencia disponible.",
            "ht": "Lòt gwo konpayi fatra a. Menm bagay la : wout lokal, orè fiks, epi yo ka fòme w pou pèmi a.",
            "fr": "L'autre grand opérateur de déchets. Même logique : tournées locales, horaires fixes, formation au permis possible.",
        },
    ),
]

SECTIONS = [
    ("board", {"en": "Start here — search every opening yourself",
               "es": "Empieza aquí — busca tú mismo en todas las ofertas",
               "ht": "Kòmanse la — chèche tèt ou nan tout òf yo",
               "fr": "Commencez ici — chercher vous-même dans toutes les offres"}),
    ("livraison", {"en": "Package and courier delivery — no CDL needed",
                   "es": "Reparto de paquetes y mensajería — sin CDL",
                   "ht": "Livrezon pake ak kourye — ou pa bezwen CDL",
                   "fr": "Livraison de colis et courses — sans CDL"}),
    ("medical", {"en": "Medical, senior and door-to-door transport",
                 "es": "Transporte médico, de mayores y puerta a puerta",
                 "ht": "Transpò medikal, granmoun ak pòt an pòt",
                 "fr": "Transport médical, personnes âgées et porte-à-porte"}),
    ("transit", {"en": "Public transit authorities",
                 "es": "Autoridades de transporte público",
                 "ht": "Konpayi transpò piblik",
                 "fr": "Régies de transport public"}),
    ("car", {"en": "Motorcoach, shuttles and charter",
             "es": "Autocares, lanzaderas y servicios discrecionales",
             "ht": "Otokar, navèt ak vwayaj espesyal",
             "fr": "Autocars, navettes et voyages en groupe"}),
    ("ecole", {"en": "School and student transport",
               "es": "Transporte escolar",
               "ht": "Transpò lekòl",
               "fr": "Transport scolaire"}),
    ("cdl", {"en": "Trucking, food distribution and waste — CDL",
             "es": "Camión, distribución de alimentos y residuos — CDL",
             "ht": "Kamyon, distribisyon manje ak fatra — CDL",
             "fr": "Camion, distribution alimentaire et déchets — CDL"}),
]
