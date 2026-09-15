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

from emplois import EMPLOYEURS, SECTIONS, VERIFIE_LE, OFFRES
from regen import entete, PIED  # regen re-enveloppe sys.stdout : ne pas le refaire ici

LANGUES = ["en", "fr", "ht", "es"]

# Les phrases de la page. La cle est courte, la valeur est le texte dans les
# quatre langues. `en` est la langue ECRITE DANS LE HTML : les autres sont
# appliquees par le petit script de bascule en bas de page.
#
# NOTE KREYOL. Traduit a partir du SENS, jamais mot a mot. A relire par
# l'utilisateur, qui est l'autorite sur cette langue.
TX = {
    "lead_court":  {'en': 'Twenty employers who actually hire drivers across the state, each linking straight to their own openings. Filter by the licence you already have.', 'fr': 'Vingt employeurs qui recrutent vraiment des chauffeurs au Massachusetts, chacun renvoyant droit à ses propres offres. Filtrez selon le permis que vous avez déjà.', 'ht': 'Ven anplwayè ki anbochte chofè tout bon nan Eta a, chak youn voye w dirèk sou pwòp òf pa l. Filtre selon pèmi ou genyen deja.', 'es': 'Veinte empleadores que de verdad contratan choferes en el estado, cada uno enlazando directo a sus propias vacantes. Filtra según la licencia que ya tienes.'},
    "lead_plus":   {'en': 'How this list works, and what it does not promise', 'fr': "Comment cette liste fonctionne, et ce qu'elle ne promet pas", 'ht': 'Kijan lis sa a mache, ak sa li pa pwomèt', 'es': 'Cómo funciona esta lista, y lo que no promete'},
    "f_titre":   {'en': 'Filter by what you have today', 'fr': "Filtrez selon ce que vous avez aujourd'hui", 'ht': 'Filtre selon sa ou genyen jodi a', 'es': 'Filtra según lo que tienes hoy'},
    "f_tous":    {'en': 'All', 'fr': 'Tous', 'ht': 'Tout', 'es': 'Todos'},
    "f_aucun":   {'en': 'No CDL needed', 'fr': 'Sans CDL', 'ht': 'San CDL', 'es': 'Sin CDL'},
    "f_7d":      {'en': '7D', 'fr': '7D', 'ht': '7D', 'es': '7D'},
    "f_cdlb":    {'en': 'CDL-B', 'fr': 'CDL-B', 'ht': 'CDL-B', 'es': 'CDL-B'},
    "f_cdla":    {'en': 'CDL-A', 'fr': 'CDL-A', 'ht': 'CDL-A', 'es': 'CDL-A'},
    "f_forme":   {'en': 'They train you', 'fr': 'Ils vous forment', 'ht': 'Yo fòme w', 'es': 'Te forman'},
    "f_rech":    {'en': 'Search an employer or a town…', 'fr': 'Cherchez un employeur ou une ville…', 'ht': 'Chèche yon anplwayè oswa yon vil…', 'es': 'Busca un empleador o una ciudad…'},
    "f_compte":  {'en': 'employers shown', 'fr': 'employeurs affichés', 'ht': 'anplwayè parèt', 'es': 'empleadores mostrados'},
    "f_rien":    {'en': 'Nothing matches that. Clear a filter and try again.', 'fr': 'Rien ne correspond. Retirez un filtre et réessayez.', 'ht': 'Anyen pa koresponn. Retire yon filtè epi eseye ankò.', 'es': 'Nada coincide. Quita un filtro e inténtalo de nuevo.'},
    "f_note":    {'en': 'These labels come from what each employer says on its own page, read by hand on the date below. They are a guide, not a promise — the employer decides.', 'fr': "Ces étiquettes viennent de ce que chaque employeur dit sur sa propre page, lu à la main à la date ci-dessous. Ce sont des repères, pas des promesses — c'est l'employeur qui décide.", 'ht': 'Etikèt sa yo soti nan sa chak anplwayè di sou pwòp paj pa l, li alamen nan dat anba a. Se repè, se pa pwomès — se anplwayè a ki deside.', 'es': 'Estas etiquetas vienen de lo que cada empleador dice en su propia página, leído a mano en la fecha de abajo. Son referencias, no promesas — decide el empleador.'},
    "p_aucun":   {'en': 'No CDL needed', 'fr': 'Sans CDL', 'ht': 'San CDL', 'es': 'Sin CDL'},
    "p_7d":      {'en': '7D', 'fr': '7D', 'ht': '7D', 'es': '7D'},
    "p_cdlb":    {'en': 'CDL-B', 'fr': 'CDL-B', 'ht': 'CDL-B', 'es': 'CDL-B'},
    "p_cdla":    {'en': 'CDL-A', 'fr': 'CDL-A', 'ht': 'CDL-A', 'es': 'CDL-A'},
    "p_varie":   {'en': 'Varies by role', 'fr': 'Selon le poste', 'ht': 'Depann de pòs la', 'es': 'Según el puesto'},
    "p_forme":   {'en': 'Trains you for the licence', 'fr': 'Vous forme au permis', 'ht': 'Fòme w pou pèmi a', 'es': 'Te forma para la licencia'},
    "p_syndic":  {'en': 'Unionised', 'fr': 'Syndiqué', 'ht': 'Sendika', 'es': 'Sindicato'},
    "p_public":  {'en': 'Public sector', 'fr': 'Secteur public', 'ht': 'Sektè piblik', 'es': 'Sector público'},
    "p_soir":    {'en': 'Home every night', 'fr': 'À la maison le soir', 'ht': 'Lakay chak swa', 'es': 'En casa cada noche'},
    "p_21":      {'en': '21 or over', 'fr': '21 ans et plus', 'ht': '21 an ak plis', 'es': '21 años o más'},

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
        "en": "Massachusetts is short of drivers — package delivery, medical transport, transit, school runs, trucking. For most of these jobs the licence is the only thing in the way.",
        "es": "A Massachusetts le faltan conductores — reparto de paquetes, transporte médico, transporte público, rutas escolares, camión. Para la mayoría de estos puestos la licencia es el único obstáculo.",
        "ht": "Massachusetts manke chofè — livrezon pake, transpò medikal, transpò piblik, wout lekòl, kamyon. Pou pifò nan travay sa yo, se pèmi a ki sèl bagay k ap bare wout la.",
        "fr": "Le Massachusetts manque de chauffeurs — livraison de colis, transport médical, transport public, circuits scolaires, camion. Pour la plupart de ces postes, le permis est le seul obstacle.",
    },
    "lead": {
        "en": "We do not host job adverts and we do not copy them. Below is the list of employers who actually hire drivers in Massachusetts, with a link straight to their own openings — so you apply in the right place. The <em>links</em> do not go stale; the <em>requirements</em> can. Anything we state about age, licence or checks was taken from an official source on the date below, and each employer sets its own rules and changes them without telling us. Read their page before you count on ours.",
        "fr": "Nous n'hébergeons pas d'annonces et nous n'en recopions aucune. Voici la liste des employeurs qui recrutent réellement des chauffeurs au Massachusetts, avec un lien direct vers leurs propres offres — vous postulez donc au bon endroit. Ce sont les <em>liens</em> qui ne périment pas ; les <em>conditions</em>, si. Ce que nous disons d'un âge, d'un permis ou d'un contrôle vient d'une source officielle à la date ci-dessous, et chaque employeur fixe ses propres règles et les change sans nous prévenir. Lisez leur page avant de compter sur la nôtre.",
        "ht": "Nou pa gen anons lakay nou epi nou pa kopye okenn. Men lis anplwayè ki tout bon ap chèche chofè nan Massachusetts, ak yon lyen dirèk sou òf pa yo — konsa ou aplike nan bon kote a. Se <em>lyen</em> yo ki pa vin vye ; <em>kondisyon</em> yo, wi. Sa nou di sou yon laj, yon pèmi oswa yon kontòl soti nan yon sous ofisyèl nan dat ki anba a, epi chak anplwayè mete pwòp règ pa l epi chanje yo san avèti nou. Li paj pa yo anvan w konte sou pa nou.",
        "es": "No alojamos anuncios ni los copiamos. Esta es la lista de empleadores que de verdad contratan conductores en Massachusetts, con un enlace directo a sus propias vacantes — así postulas en el sitio correcto. Son los <em>enlaces</em> los que no caducan; los <em>requisitos</em>, sí. Lo que decimos sobre una edad, una licencia o un control viene de una fuente oficial en la fecha de abajo, y cada empleador fija sus propias reglas y las cambia sin avisarnos. Lee su página antes de fiarte de la nuestra.",
    },
    "descr": {
        "en": "Who actually hires drivers in Massachusetts: school transport, regional transit authorities and the state job board. Checked links, straight to each employer's own openings. Free WhatsApp alerts when a new one opens.",
        "fr": "Qui recrute vraiment des chauffeurs au Massachusetts : transport scolaire, r\u00e9gies de transport et site d'emploi de l'\u00c9tat. Des liens v\u00e9rifi\u00e9s, droit vers les offres de chaque employeur. Alertes WhatsApp gratuites.",
        "ht": "Kil\u00e8s ki anbochte chof\u00e8 tout bon nan Massachusetts : transp\u00f2 lek\u00f2l, konpayi transp\u00f2 piblik ak sit travay Eta a. Lyen verifye, dir\u00e8k sou \u00f2f chak anplway\u00e8. Al\u00e8t WhatsApp gratis.",
        "es": "Qui\u00e9n contrata de verdad conductores en Massachusetts: transporte escolar, autoridades de transporte y el portal de empleo del estado. Enlaces verificados, directo a las vacantes de cada empleador. Avisos de WhatsApp gratis.",
    },
    "verifie": {
        "en": "Every link below was opened and checked on %s." % VERIFIE_LE,
        "fr": "Chaque lien ci-dessous a été ouvert et vérifié le %s." % VERIFIE_LE,
        "ht": "Chak lyen anba a te louvri epi verifye nan dat %s." % VERIFIE_LE,
        "es": "Cada enlace de abajo fue abierto y verificado el %s." % VERIFIE_LE,
    },
    "offres_t": {
        "en": "Openings employers sent us",
        "fr": "Les offres que des employeurs nous ont envoyées",
        "ht": "Òf anplwayè yo voye ban nou",
        "es": "Vacantes que nos enviaron los empleadores",
    },
    "offres_d": {
        "en": "These came to us directly. We checked each link before publishing it, and we take a posting down once it is filled — a jobs page that keeps closed roles wastes the time of the person reading it.",
        "fr": "Elles nous sont parvenues directement. Nous avons ouvert chaque lien avant de le publier, et nous retirons une offre dès qu'elle est pourvue — une page d'offres qui garde des postes fermés fait perdre son temps à qui la lit.",
        "ht": "Yo rive jwenn nou dirèkteman. Nou louvri chak lyen anvan nou pibliye l, epi nou retire yon òf depi yo jwenn moun — yon paj travay ki kenbe pòs ki fèmen fè moun k ap li a pèdi tan l.",
        "es": "Nos llegaron directamente. Abrimos cada enlace antes de publicarlo y retiramos una oferta en cuanto se cubre — una página de empleos que conserva puestos cerrados le hace perder el tiempo a quien la lee.",
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
        "en": "In August 2026, delivery van work was advertised at roughly $17 to $26 an hour and asks for no CDL; school bus posts at roughly $27 to $32, often with a sign-on bonus; and CDL work in food distribution or waste collection pays more again. Those are figures read on job boards, not a promise from anyone: the only number that binds an employer is the one on the employer's own page. Watch the hours too — school runs are usually split shifts, delivery is full days, waste starts before dawn.",
        "es": "En agosto de 2026, el reparto en furgoneta se anunciaba entre 17 y 26 dólares la hora y no exige CDL; los puestos de autobús escolar entre 27 y 32, a menudo con bono de contratación; y el trabajo con CDL en distribución de alimentos o recogida de residuos paga más todavía. Son cifras leídas en portales de empleo, no una promesa: el único número que compromete a un empleador es el de su propia página. Mira también el horario — lo escolar suele ser jornada partida, el reparto son días completos, los residuos empiezan antes del amanecer.",
        "ht": "Nan mwa out 2026, travay livrezon nan kamyonèt te afiche ant 17 ak 26 dola lè a epi li pa mande CDL ; pòs bis lekòl yo ant 27 ak 32, souvan ak yon prim lè ou siyen ; epi travay CDL nan distribisyon manje oswa ranmase fatra peye pi plis toujou. Se chif nou li sou sit travay, se pa yon pwomès : sèl chif ki angaje yon anplwayè se sa ki sou paj pa l. Gade orè a tou — lekòl se souvan orè koupe, livrezon se jounen konplè, fatra kòmanse anvan solèy leve.",
        "fr": "En août 2026, la livraison en camionnette était affichée autour de 17 à 26 dollars de l'heure et ne demande aucun CDL ; les postes de bus scolaire autour de 27 à 32, souvent avec une prime à l'embauche ; et le travail sous CDL en distribution alimentaire ou en collecte des déchets paie davantage encore. Ce sont des chiffres lus sur des sites d'emploi, pas une promesse : le seul chiffre qui engage un employeur est celui de sa propre page. Regardez aussi les horaires — le scolaire est en journée coupée, la livraison en journée pleine, les déchets démarrent avant le jour.",
    },
    "pub_t": {
        "en": "Hiring? We publish your opening here — free",
        "fr": "Vous recrutez ? Nous publions votre offre ici — gratuitement",
        "ht": "W ap chèche moun ? N ap pibliye òf ou a isit la — gratis",
        "es": "¿Estás contratando? Publicamos tu oferta aquí — gratis",
    },
    "pub_d": {
        "en": "If your company, your district or your agency has a driver post open, send it to us and it appears on this page. There is no charge for this, and there will not be one: the page is only worth reading if it is complete. We check the posting, publish it, and tell the drivers who asked to hear about openings in that area. You keep your own application process — we link straight to it.",
        "fr": "Si votre entreprise, votre district ou votre régie a un poste de chauffeur ouvert, envoyez-le-nous et il paraît sur cette page. C'est gratuit, et cela le restera : la page ne vaut d'être lue que si elle est complète. Nous vérifions l'offre, nous la publions, et nous prévenons les chauffeurs qui ont demandé à être avertis dans ce secteur. Vous gardez votre propre procédure de candidature — nous y renvoyons directement.",
        "ht": "Si konpayi w, distri w oswa ajans ou gen yon pòs chofè ki louvri, voye l ban nou epi l ap parèt sou paj sa a. Se gratis, epi l ap rete gratis : paj la vo lapèn li li sèlman si li konplè. Nou verifye òf la, nou pibliye l, epi nou avèti chofè ki te mande pou yo konnen lè gen travay nan zòn sa a. Ou kenbe pwòp fason w pou moun aplike — nou voye moun dirèk sou li.",
        "es": "Si tu empresa, tu distrito o tu agencia tiene una vacante de conductor, envíanosla y aparecerá en esta página. Es gratis, y lo seguirá siendo: la página solo vale la pena si está completa. Verificamos la oferta, la publicamos y avisamos a los conductores que pidieron enterarse de las vacantes de esa zona. Conservas tu propio proceso de solicitud — enlazamos directamente a él.",
    },
    "pub_b": {
        "en": "Send us an opening", "fr": "Nous envoyer une offre",
        "ht": "Voye yon òf ban nou", "es": "Enviarnos una oferta",
    },
    "pub_n": {
        "en": "No fee, no commission, and no cut of a hire. If you would rather browse drivers yourself, that is what Driver Employer is for.",
        "fr": "Sans frais, sans commission, et sans pourcentage sur une embauche. Si vous préférez parcourir vous-même les chauffeurs, c'est à cela que sert Driver Employer.",
        "ht": "Pa gen frè, pa gen komisyon, epi nou pa pran anyen sou yon anbochaj. Si w pito gade chofè yo ou menm, se pou sa Driver Employer la ye.",
        "es": "Sin costo, sin comisión y sin porcentaje sobre una contratación. Si prefieres revisar tú mismo a los conductores, para eso está Driver Employer.",
    },
    "alerte_t": {
        "en": "Get told when a new one opens", "fr": "Être prévenu quand une offre s'ouvre",
        "ht": "Konnen lè yon nouvo òf louvri", "es": "Que te avisen cuando se abra una",
    },
    "alerte_d": {
        "en": "Checking twenty employer pages every week is work. Tick one box when you join the driver pool and we will send you a WhatsApp message when something opens near you — two a week at most, and STOP ends it. Right now those messages are written and sent by hand, by a person, from a Massachusetts number. We would rather say that than pretend we have an automated system we do not yet have.",
        "fr": "Vérifier vingt pages d'employeurs chaque semaine, c'est du travail. Cochez une case en vous inscrivant au vivier et nous vous enverrons un message WhatsApp quand une offre s'ouvre près de chez vous — deux par semaine au maximum, et STOP y met fin. Aujourd'hui ces messages sont écrits et envoyés à la main, par une personne, depuis un numéro du Massachusetts. Nous préférons le dire plutôt que de faire croire à un système automatique que nous n'avons pas encore.",
        "ht": "Tcheke ven paj anplwayè chak semèn se travay. Koche yon sèl kaz lè w ap enskri nan vivye a epi n ap voye yon mesaj WhatsApp ba ou lè yon òf louvri toupre lakay ou — de pa semèn, pa plis, epi STOP fè sa kanpe. Kounye a se yon moun ki ekri epi voye mesaj sa yo alamen, depi yon nimewo Massachusetts. Nou pito di sa pase pou nou fè kwè nou gen yon sistèm otomatik nou poko genyen.",
        "es": "Revisar veinte páginas de empleadores cada semana es trabajo. Marca una casilla al inscribirte en el registro y te enviaremos un mensaje de WhatsApp cuando se abra algo cerca de ti — dos por semana como máximo, y STOP lo termina. Hoy esos mensajes los escribe y los envía una persona, a mano, desde un número de Massachusetts. Preferimos decirlo antes que fingir un sistema automático que todavía no tenemos.",
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
        "en": "Delivery and medical transport need only a <strong>Class D</strong> — the licence you already have, or can get. Rideshare needs a Class D <em>plus</em> a <strong>Background Check Clearance Certificate</strong> from the state (DPU), and the licence held 1 year from age 23, 3 years under 23. School runs need the <strong>7D</strong>: 21 years old, a licence held 3 years, CORI and SORI checks, an eye and physical exam, 2 hours of training with your employer — and then the written exam. Buses, trucks and waste need a <strong>CDL</strong>, and several of the employers above pay to train you for it. Driver Coach drills the Class D road test and the 7D written exam, in English, Spanish, Haitian Creole and French.",
        "es": "El reparto y el transporte médico solo necesitan una <strong>Class D</strong> — la licencia que ya tienes o puedes obtener. Las apps de viajes necesitan una Class D <em>y además</em> un <strong>Background Check Clearance Certificate</strong> del estado (DPU), con la licencia en mano 1 año desde los 23 años, 3 años por debajo de 23. Las rutas escolares necesitan la <strong>7D</strong>: 21 años, licencia desde hace 3 años, controles CORI y SORI, examen de la vista y examen físico, 2 horas de formación con tu empleador — y después el examen escrito. Autobuses, camiones y residuos necesitan un <strong>CDL</strong>, y varios de los empleadores de arriba pagan tu formación. Driver Coach practica el examen Class D y el examen escrito 7D, en inglés, español, criollo haitiano y francés.",
        "ht": "Livrezon ak transpò medikal mande sèlman yon <strong>Class D</strong> — pèmi ou gen deja, oswa ou ka jwenn. Aplikasyon vwayaj yo mande yon Class D <em>plis</em> yon <strong>Background Check Clearance Certificate</strong> nan men Eta a (DPU), epi ou dwe gen pèmi an depi 1 an si w gen 23 an oswa plis, 3 an si w anba 23 an. Wout lekòl mande <strong>7D</strong> a : 21 an, yon pèmi depi 3 an, kontòl CORI ak SORI, egzamen zye ak egzamen fizik, 2 èdtan fòmasyon lakay anplwayè a — epi apre sa egzamen ekri a. Bis, kamyon ak fatra mande yon <strong>CDL</strong>, epi plizyè nan anplwayè anwo yo peye pou fòme w. Driver Coach fè w travay tès wout Class D a ak egzamen ekri 7D a, an anglè, an panyòl, an kreyòl ak an franse.",
        "fr": "La livraison et le transport médical ne demandent qu'un <strong>Class D</strong> — le permis que vous avez déjà, ou que vous pouvez obtenir. Les applications de course demandent un Class D <em>et</em> un <strong>Background Check Clearance Certificate</strong> de l'État (DPU), avec un permis détenu depuis 1 an à partir de 23 ans, 3 ans en dessous. Les circuits scolaires demandent le <strong>7D</strong> : 21 ans, un permis depuis 3 ans, contrôles CORI et SORI, examen de la vue et examen physique, 2 heures de formation chez l'employeur — et ensuite l'examen écrit. Les bus, camions et déchets demandent un <strong>CDL</strong>, et plusieurs employeurs ci-dessus paient votre formation. Driver Coach fait travailler le test de route Class D et l'examen écrit 7D, en anglais, espagnol, kreyòl et français.",
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
}


# ============================================================================
# LE PERIMETRE DSP (decide le 15/09/2026) — ces textes REMPLACENT ceux du
# dessus quand `portee.PORTEE == "dsp"`. Les textes d'avant restent intacts
# au-dessus : rallumer le perimetre complet ne demande aucune reecriture.
#
# ⚠️ AUCUNE PHRASE NE DIT QUE DRIVER360 TRAVAILLE AVEC AMAZON. La presentation
# a Ryan le dit elle-meme : « No Amazon integration or endorsement is
# assumed. » Le site non plus, et il l'ecrit.
# ============================================================================
TX_DSP = {
    "ti": {
        "en": "Amazon DSP delivery driver jobs in Massachusetts \u2014 Driver360",
        "fr": "Emplois de chauffeur livreur DSP Amazon au Massachusetts \u2014 Driver360",
        "ht": "Travay chof\u00e8 livrezon DSP Amazon nan Massachusetts \u2014 Driver360",
        "es": "Empleos de conductor de reparto DSP de Amazon en Massachusetts \u2014 Driver360",
    },
    "descr": {
        "en": "Delivery driver jobs with Amazon Delivery Service Partners in Massachusetts: where DSPs post their openings, what the work asks for, and what it pays. Independent \u2014 not affiliated with Amazon.",
        "fr": "Emplois de chauffeur livreur chez les partenaires de livraison d'Amazon au Massachusetts : o\u00f9 les DSP publient leurs postes, ce que le travail demande et ce qu'il paie. Ind\u00e9pendant \u2014 non affili\u00e9 \u00e0 Amazon.",
        "ht": "Travay chof\u00e8 livrezon ak patn\u00e8 livrezon Amazon yo nan Massachusetts : kote DSP yo pibliye p\u00f2s yo, sa travay la mande ak konbyen li peye. Endepandan \u2014 pa afilye ak Amazon.",
        "es": "Empleos de conductor de reparto con los socios de entrega de Amazon en Massachusetts: d\u00f3nde publican los DSP sus vacantes, qu\u00e9 pide el trabajo y cu\u00e1nto paga. Independiente \u2014 sin afiliaci\u00f3n con Amazon.",
    },
    "titre": {
        "en": "Delivery driver jobs with Amazon DSPs",
        "fr": "Emplois de chauffeur livreur chez les DSP d'Amazon",
        "ht": "Travay chof\u00e8 livrezon nan DSP Amazon yo",
        "es": "Empleos de conductor de reparto en los DSP de Amazon",
    },
    "fil": {
        "en": "For now, Driver360 is focused on one kind of work: delivering for Amazon through its Delivery Service Partners \u2014 the independent companies that hire the drivers.",
        "fr": "Pour le moment, Driver360 se concentre sur un seul m\u00e9tier : livrer pour Amazon via ses partenaires de livraison \u2014 les entreprises ind\u00e9pendantes qui embauchent les chauffeurs.",
        "ht": "Pou kounye a, Driver360 konsantre sou yon s\u00e8l kalite travay : livre pou Amazon atrav\u00e8 patn\u00e8 livrezon li yo \u2014 konpayi endepandan ki anbochte chof\u00e8 yo.",
        "es": "Por ahora, Driver360 se centra en un solo tipo de trabajo: repartir para Amazon a trav\u00e9s de sus socios de entrega \u2014 las empresas independientes que contratan a los conductores.",
    },
    "lead_court": {
        "en": "Every DSP is its own employer. Amazon lists their openings in one place \u2014 start there, near where you live.",
        "fr": "Chaque DSP est un employeur \u00e0 part enti\u00e8re. Amazon liste leurs postes en un seul endroit \u2014 commencez l\u00e0, pr\u00e8s de chez vous.",
        "ht": "Chak DSP se pwòp anplway\u00e8 pa l. Amazon mete p\u00f2s yo tout nan yon s\u00e8l kote \u2014 k\u00f2manse la, toupre kote w rete.",
        "es": "Cada DSP es su propio empleador. Amazon re\u00fane sus vacantes en un solo lugar \u2014 empieza ah\u00ed, cerca de donde vives.",
    },
    "lead": {
        "en": "We do not host job adverts and we do not copy them. Amazon contracts with Delivery Service Partners; each one is an independent company that hires, pays and schedules its own drivers. Amazon lists their openings on its official DSP driver page, searchable by location \u2014 that is the link below, and you apply there, directly with the DSP. Anything we say about age, licence or pay was read on an official page or a job board on the date below, and each DSP sets its own terms: read the posting before you count on ours. <strong>Driver360 is independent and is not affiliated with or endorsed by Amazon.</strong>",
        "fr": "Nous n'h\u00e9bergeons pas d'annonces et nous n'en recopions aucune. Amazon sous-traite \u00e0 des partenaires de livraison ; chacun est une entreprise ind\u00e9pendante qui embauche, paie et planifie ses propres chauffeurs. Amazon liste leurs postes sur sa page officielle des chauffeurs DSP, avec recherche par lieu \u2014 c'est le lien ci-dessous, et c'est l\u00e0 que vous postulez, directement aupr\u00e8s du DSP. Ce que nous disons d'un \u00e2ge, d'un permis ou d'un salaire a \u00e9t\u00e9 lu sur une page officielle ou un site d'emploi \u00e0 la date ci-dessous, et chaque DSP fixe ses conditions : lisez l'offre avant de compter sur la n\u00f4tre. <strong>Driver360 est ind\u00e9pendant, ni affili\u00e9 \u00e0 Amazon ni approuv\u00e9 par Amazon.</strong>",
        "ht": "Nou pa gen anons lakay nou epi nou pa kopye okenn. Amazon bay patn\u00e8 livrezon yo kontra ; chak se yon konpayi endepandan ki anbochte, peye epi f\u00e8 or\u00e8 pwòp chof\u00e8 pa l. Amazon mete p\u00f2s yo sou paj ofisy\u00e8l chof\u00e8 DSP li a, ou ka ch\u00e8che selon kote w ye \u2014 se lyen ki anba a, epi se la ou aplike, dir\u00e8k ak DSP a. Sa nou di sou laj, p\u00e8mi oswa sal\u00e8 nou li l sou yon paj ofisy\u00e8l oswa yon sit travay nan dat ki anba a, epi chak DSP mete pwòp kondisyon pa l : li \u00f2f la anvan w konte sou pa nou. <strong>Driver360 endepandan, li pa afilye ak Amazon epi Amazon pa apwouve l.</strong>",
        "es": "No alojamos anuncios ni los copiamos. Amazon contrata a socios de entrega; cada uno es una empresa independiente que contrata, paga y organiza a sus propios conductores. Amazon re\u00fane sus vacantes en su p\u00e1gina oficial de conductores DSP, con b\u00fasqueda por ubicaci\u00f3n \u2014 es el enlace de abajo, y postulas ah\u00ed, directamente con el DSP. Lo que decimos sobre edad, licencia o salario se ley\u00f3 en una p\u00e1gina oficial o un portal de empleo en la fecha de abajo, y cada DSP fija sus condiciones: lee la oferta antes de fiarte de la nuestra. <strong>Driver360 es independiente y no est\u00e1 afiliado ni avalado por Amazon.</strong>",
    },
    "paye_t": {
        "en": "What DSP driving pays", "fr": "Ce que paie la livraison en DSP",
        "ht": "Konbyen travay chof\u00e8 DSP peye", "es": "Cu\u00e1nto paga conducir para un DSP",
    },
    "paye_d": {
        "en": "In August 2026, DSP delivery van work was advertised at roughly $17 to $26 an hour. That is a range read on job boards, not a promise: the only figure that binds a DSP is the one in its own posting. Amazon's page says the DSP provides the van, gas and insurance, and that full-time and part-time schedules <em>may</em> be available \u2014 ask about hours, route length and which days you would work before you accept.",
        "fr": "En ao\u00fbt 2026, la livraison en camionnette pour un DSP \u00e9tait affich\u00e9e autour de 17 \u00e0 26 dollars de l'heure. C'est une fourchette lue sur des sites d'emploi, pas une promesse : le seul chiffre qui engage un DSP est celui de sa propre offre. La page d'Amazon dit que le DSP fournit la camionnette, l'essence et l'assurance, et que des horaires \u00e0 temps plein ou partiel <em>peuvent</em> exister \u2014 demandez les heures, la longueur des tourn\u00e9es et les jours travaill\u00e9s avant d'accepter.",
        "ht": "Nan mwa out 2026, travay livrezon nan kamyon\u00e8t pou yon DSP te afiche ant 17 ak 26 dola l\u00e8 a. Se yon ranje nou li sou sit travay, se pa yon pwom\u00e8s : s\u00e8l chif ki angaje yon DSP se sa ki nan pwòp \u00f2f pa l. Paj Amazon an di se DSP a ki bay kamyon\u00e8t la, gaz la ak asirans lan, epi or\u00e8 tan pl\u00e8n oswa tan pasy\u00e8l <em>ka</em> egziste \u2014 mande konbyen \u00e8dtan, longv\u00e8 wout yo ak ki jou w ap travay anvan w aksepte.",
        "es": "En agosto de 2026, el reparto en furgoneta para un DSP se anunciaba entre 17 y 26 d\u00f3lares la hora. Es un rango le\u00eddo en portales de empleo, no una promesa: la \u00fanica cifra que compromete a un DSP es la de su propia oferta. La p\u00e1gina de Amazon dice que el DSP pone la furgoneta, la gasolina y el seguro, y que <em>puede</em> haber jornadas completas o parciales \u2014 pregunta por las horas, la duraci\u00f3n de las rutas y los d\u00edas de trabajo antes de aceptar.",
    },
    "pub_t": {
        "en": "A DSP hiring? We publish your opening here \u2014 free",
        "fr": "Un DSP qui recrute ? Nous publions votre offre ici \u2014 gratuitement",
        "ht": "Yon DSP k ap anbochte ? N ap pibliye \u00f2f ou a isit la \u2014 gratis",
        "es": "\u00bfUn DSP contratando? Publicamos tu oferta aqu\u00ed \u2014 gratis",
    },
    "pub_d": {
        "en": "If you run or hire for an Amazon DSP in Massachusetts and have a driver opening, send it to us and it appears on this page. There is no charge. We check the posting, publish it, and link straight to your own application \u2014 you keep your process.",
        "fr": "Si vous dirigez un DSP d'Amazon au Massachusetts, ou recrutez pour lui, et avez un poste de chauffeur ouvert, envoyez-le-nous et il para\u00eet sur cette page. C'est gratuit. Nous v\u00e9rifions l'offre, nous la publions, et nous renvoyons directement vers votre propre candidature \u2014 vous gardez votre proc\u00e9dure.",
        "ht": "Si w dirije yon DSP Amazon nan Massachusetts, oswa w ap anbochte pou li, epi w gen yon p\u00f2s chof\u00e8 ki louvri, voye l ban nou epi l ap par\u00e8t sou paj sa a. Se gratis. Nou verifye \u00f2f la, nou pibliye l, epi nou voye moun dir\u00e8k sou pwòp fason pa w pou yo aplike \u2014 ou kenbe pwos\u00e8 pa w.",
        "es": "Si diriges un DSP de Amazon en Massachusetts, o contratas para uno, y tienes una vacante de conductor, env\u00edanosla y aparecer\u00e1 en esta p\u00e1gina. Es gratis. Verificamos la oferta, la publicamos y enlazamos directo a tu propio proceso de solicitud \u2014 conservas tu proceso.",
    },
    "alerte_d": {
        "en": "Tick one box when you join the driver pool and we will send you a WhatsApp message when a DSP opening appears near you \u2014 two a week at most, and STOP ends it. Right now those messages are written and sent by hand, by a person. We would rather say that than pretend we have an automated system we do not have yet.",
        "fr": "Cochez une case en vous inscrivant au vivier et nous vous enverrons un message WhatsApp quand un poste DSP s'ouvre pr\u00e8s de chez vous \u2014 deux par semaine au maximum, et STOP y met fin. Aujourd'hui ces messages sont \u00e9crits et envoy\u00e9s \u00e0 la main, par une personne. Nous pr\u00e9f\u00e9rons le dire plut\u00f4t que de faire croire \u00e0 un syst\u00e8me automatique que nous n'avons pas encore.",
        "ht": "Koche yon s\u00e8l kaz l\u00e8 w ap enskri nan vivye a epi n ap voye yon mesaj WhatsApp ba ou l\u00e8 yon p\u00f2s DSP louvri toupre lakay ou \u2014 de pa sem\u00e8n, pa plis, epi STOP f\u00e8 sa kanpe. Kounye a se yon moun ki ekri epi voye mesaj sa yo alamen. Nou pito di sa pase pou nou f\u00e8 kw\u00e8 nou gen yon sist\u00e8m otomatik nou poko genyen.",
        "es": "Marca una casilla al inscribirte en el registro y te enviaremos un mensaje de WhatsApp cuando se abra una vacante DSP cerca de ti \u2014 dos por semana como m\u00e1ximo, y STOP lo termina. Hoy esos mensajes los escribe y los env\u00eda una persona, a mano. Preferimos decirlo antes que fingir un sistema autom\u00e1tico que todav\u00eda no tenemos.",
    },
    "permis_t": {
        "en": "Already driving for a DSP?", "fr": "Vous livrez d\u00e9j\u00e0 pour un DSP ?",
        "ht": "Ou deja ap kondwi pou yon DSP ?", "es": "\u00bfYa conduces para un DSP?",
    },
    "permis_d": {
        "en": "Delivering for a DSP takes a regular <strong>Class D</strong> licence \u2014 no CDL \u2014 and you must be <strong>21 or over</strong> with a clean record. Amazon's own page lists <strong>advancement opportunities</strong> and the chance to obtain <strong>DOT certification</strong>. Driver Coach helps with what comes after the first job: putting your experience into words, getting ready for a new DSP, taking a break and coming back.",
        "fr": "Livrer pour un DSP demande un permis <strong>Class D</strong> ordinaire \u2014 aucun CDL \u2014 et il faut avoir <strong>21 ans ou plus</strong> avec un dossier propre. La page d'Amazon cite elle-m\u00eame des <strong>possibilit\u00e9s d'\u00e9volution</strong> et la possibilit\u00e9 d'obtenir la <strong>certification DOT</strong>. Driver Coach vous aide pour la suite : mettre votre exp\u00e9rience en mots, vous pr\u00e9parer \u00e0 un nouveau DSP, faire une pause et revenir.",
        "ht": "Livre pou yon DSP mande yon p\u00e8mi <strong>Class D</strong> n\u00f2mal \u2014 pa bezwen CDL \u2014 epi f\u00f2k ou gen <strong>21 an oswa plis</strong> ak yon dosye pw\u00f2p. Paj Amazon an li menm pale de <strong>chans pou monte</strong> ak posiblite pou jwenn <strong>s\u00e8tifikasyon DOT</strong>. Driver Coach ede w pou sa ki vini apre premye travay la : mete eksperyans ou an mo, prepare w pou yon l\u00f2t DSP, pran yon poz epi retounen.",
        "es": "Repartir para un DSP pide una licencia <strong>Class D</strong> normal \u2014 sin CDL \u2014 y hay que tener <strong>21 a\u00f1os o m\u00e1s</strong> con historial limpio. La propia p\u00e1gina de Amazon menciona <strong>oportunidades de ascenso</strong> y la posibilidad de obtener la <strong>certificaci\u00f3n DOT</strong>. Driver Coach te ayuda con lo que viene despu\u00e9s del primer empleo: poner tu experiencia en palabras, prepararte para un nuevo DSP, tomar una pausa y volver.",
    },
    "permis_b": {
        "en": "Work on my career with Driver Coach \u2192", "fr": "Travailler ma carri\u00e8re avec Driver Coach \u2192",
        "ht": "Travay sou kary\u00e8 m ak Driver Coach \u2192", "es": "Trabajar mi carrera con Driver Coach \u2192",
    },
    "manque_t": {
        "en": "A DSP opening we have missed?", "fr": "Un poste DSP qui manque ?",
        "ht": "Yon p\u00f2s DSP ki manke ?", "es": "\u00bfFalta una vacante DSP?",
    },
    "manque_d": {
        "en": "If you know an Amazon DSP in Massachusetts that is hiring drivers, tell us \u2014 we check the posting and add it.",
        "fr": "Si vous connaissez un DSP d'Amazon au Massachusetts qui recrute des chauffeurs, dites-le-nous : nous v\u00e9rifions l'offre et nous l'ajoutons.",
        "ht": "Si w konnen yon DSP Amazon nan Massachusetts k ap ch\u00e8che chof\u00e8, di nou l : n ap verifye \u00f2f la epi n ap mete l.",
        "es": "Si conoces un DSP de Amazon en Massachusetts que est\u00e9 contratando conductores, d\u00ednoslo: verificamos la oferta y la a\u00f1adimos.",
    },
    "manque_b": {
        "en": "Tell us about a DSP opening", "fr": "Signaler un poste DSP",
        "ht": "Siyale yon p\u00f2s DSP", "es": "Avisar de una vacante DSP",
    },
}


import portee  # noqa: E402

# Le perimetre decide quels textes s'affichent. Les textes d'avant ne bougent
# pas : seules les cles presentes dans TX_DSP sont remplacees.
if portee.dsp():
    TX.update(TX_DSP)


def montres():
    """Les fiches reellement rendues, dans l'ordre des sections actives."""
    return [e for g, _ in SECTIONS if portee.section_active(g)
            for e in EMPLOYEURS if e["genre"] == g]


def date_verification():
    """⚠️ La plus ANCIENNE des fiches visibles, pas la date globale.

    La page ecrit « chaque lien ci-dessous a ete verifie le … ». Afficher une
    date plus recente que la verification de l'une des fiches montrees serait
    une affirmation fausse sur un lien precis.
    """
    vus = [e.get("verifie", VERIFIE_LE) for e in montres()]
    return min(vus) if vus else VERIFIE_LE


_D = date_verification()
TX["verifie"] = {
    "en": "Every link below was opened and checked on %s." % _D,
    "fr": "Chaque lien ci-dessous a \u00e9t\u00e9 ouvert et v\u00e9rifi\u00e9 le %s." % _D,
    "ht": "Chak lyen anba a te louvri epi verifye nan dat %s." % _D,
    "es": "Cada enlace de abajo fue abierto y verificado el %s." % _D,
}

MAILTO_PUB = ("mailto:sales@atmart.ltd?subject=Driver360%20-%20job%20posting"
              "&amp;body=" + "Employer%3A%0ATown%20or%20area%3A%0ARole%3A%0ALicence%20required%20%28Class%20D%20/%207D%20/%20CDL%29%3A%0AFull%20or%20part%20time%3A%0AAdvertised%20pay%3A%0ALink%20to%20your%20own%20application%20page%3A%0A%0AThank%20you.")

MAILTO = ("mailto:sales@atmart.ltd?subject=Driver360%20-%20an%20employer%20who%20hires"
          "&amp;body=" + "Employer%20name%3A%0ATown%3A%0ALink%20to%20their%20jobs%20page%3A%0A%0AThank%20you.")

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
    .jb-emp{background:rgba(93,156,236,.08);border-color:rgba(93,156,236,.4)}
    .d3-lang{display:flex;gap:.4rem;flex-wrap:wrap}
    .d3-lang button{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.14);
      color:#c9d8e6;border-radius:99px;padding:.3rem .8rem;font-size:.8rem;cursor:pointer;font-family:inherit}
    .d3-lang button.actif{border-color:#2ec4b6;color:#2ec4b6;font-weight:600}

    /* La barre de filtres. Elle colle en haut quand on defile : sur vingt
       cartes on perd sinon le moyen de changer d'avis sans remonter. */
    /* ⚠️ `top` VAUT LA HAUTEUR DE L'EN-TETE, PAS ZERO. L'en-tete du site est
       lui aussi `sticky; top:0` (z-index 50) : avec `top:0` ici, les deux se
       superposaient et le logo passait PAR-DESSUS le champ de recherche —
       mesure au telephone le 03/09/2026, l'en-tete fait 69 px. On se colle
       dessous, et le z-index reste inferieur au sien pour que l'ordre
       d'empilement dise la meme chose que la geometrie. */
    .jb-filtres{position:sticky;top:69px;z-index:20;background:var(--d-fond);
      border-bottom:1px solid var(--d-ligne);padding:0.7rem 0;margin-bottom:1.2rem}
    .jb-f-rech{width:100%;max-width:420px;background:var(--d-surface);
      color:var(--d-fort);border:1px solid var(--d-ligne);border-radius:9px;
      padding:0.6rem 0.85rem;font:inherit;font-size:16px;min-height:44px}
    .jb-f-lig{display:flex;flex-wrap:wrap;gap:0.4rem;margin-top:0.6rem}
    .jb-f{background:var(--d-surface);color:var(--d-texte);
      border:1px solid var(--d-ligne);border-radius:999px;
      padding:0.45rem 0.85rem;font:inherit;font-size:0.86rem;cursor:pointer;
      min-height:44px}
    .jb-f:hover{border-color:var(--d-accent-bord)}
    .jb-f[aria-pressed="true"]{background:var(--d-accent);
      color:var(--d-accent-encre);border-color:var(--d-accent);font-weight:600}
    .jb-compte{color:var(--d-doux);font-size:0.85rem;margin-top:0.55rem}
    /* Les pastilles d'une carte. */
    .jb-tags{display:flex;flex-wrap:wrap;gap:0.32rem;margin:0.5rem 0 0}
    .jb-tag{background:var(--d-surface-2);color:var(--d-texte);
      border-radius:6px;padding:0.16rem 0.5rem;font-size:0.76rem;
      white-space:nowrap}
    .jb-tag.cle{background:var(--d-accent-fond);color:var(--d-accent);
      border:1px solid var(--d-accent-bord);font-weight:600}
    .jb-tag.paye{background:var(--d-vert-fond);color:var(--d-vert);
      border:1px solid var(--d-vert-bord);font-weight:600}
    .jb-vide{color:var(--d-doux);padding:1.4rem 0}
    .jb-sec.off{display:none}
    /* ⚠️ LA MISE EN GARDE PASSE DERRIERE UN DEPLIANT, ELLE NE DISPARAIT PAS.
       Mesure au telephone le 03/09/2026 : on defilait un ecran ENTIER de
       prose avant d'atteindre quoi que ce soit d'actionnable. Sur un produit
       dont un employeur nous a dit que « le temps coute plus cher que
       l'argent », c'est le defaut le plus cher de la page. Tout le texte est
       toujours la, a un clic — mais il ne barre plus la porte. */
    .jb-plus{margin-top:.6rem;max-width:760px}
    .jb-plus summary{cursor:pointer;color:var(--d-accent);font-size:.9rem;
      padding:.4rem 0;min-height:44px;display:flex;align-items:center}
    .jb-plus p{margin:.3rem 0 0}
    .sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;
      overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
    /* ⚠️ SUR TELEPHONE, LES FILTRES TIENNENT SUR UNE SEULE LIGNE QUI DEFILE.
       Mesure du 03/09/2026 : a 375 px les six pastilles passaient sur deux
       lignes et la barre collante occupait 233 px, soit 29 % de l'ecran, en
       permanence. On regarde des offres a travers une meurtriere. Une ligne
       qui defile horizontalement est ce que fait Indeed sur mobile, et pour
       cette raison-la. */
    @media (max-width:700px){
      .jb-filtres{padding:0.55rem 0}
      .jb-f-lig{flex-wrap:nowrap;overflow-x:auto;-webkit-overflow-scrolling:touch;
        scrollbar-width:none;padding-bottom:0.2rem}
      .jb-f-lig::-webkit-scrollbar{display:none}
      .jb-f{flex:0 0 auto}
      .jb-compte{margin-top:0.35rem;font-size:0.8rem}
    }
"""


def t(cle, lg="en"):
    return TX[cle][lg]


def pastilles(e):
    """Les pastilles d'une fiche, dans l'ordre ou elles servent.

    ⚠️ ORDRE VOULU : le permis d'abord, parce que c'est la question qui decide
    si la personne peut postuler aujourd'hui ou dans six mois. Le salaire
    ensuite. Le reste apres.
    """
    out = []
    for p in e.get("permis", []):
        cl = "jb-tag cle" if p in ("aucun", "7d") else "jb-tag"
        out.append('<span class="%s" data-t="p_%s">%s</span>' % (cl, p, t("p_" + p)))
    if e.get("forme"):
        out.append('<span class="jb-tag cle" data-t="p_forme">%s</span>' % t("p_forme"))
    if e.get("paye"):
        # ⚠️ PAS DE data-t : un montant en dollars ne se traduit pas, et lui
        # donner une cle le ferait effacer par le dictionnaire des trois
        # autres langues.
        out.append('<span class="jb-tag paye">%s</span>' % e["paye"])
    for a in e.get("atouts", []):
        out.append('<span class="jb-tag" data-t="p_%s">%s</span>' % (a, t("p_" + a)))
    return "".join(out)


def carte(e):
    return (
        '      <a class="jb" href="%s" target="_blank" rel="noopener"'
        ' data-permis="%s" data-forme="%s">\n'
        '        <span class="n"><h3>%s</h3><span class="z" data-t="z_%s">%s</span></span>\n'
        '        <span class="jb-tags">%s</span>\n'
        '        <p data-t="q_%s">%s</p>\n'
        '        <span class="v" data-t="voir">%s</span>\n'
        '      </a>' % (e["url"], " ".join(e.get("permis", [])),
                        "1" if e.get("forme") else "0",
                        e["nom"], cle(e), e["zone"]["en"], pastilles(e),
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



def offres():
    """Les offres envoyées par des employeurs, si elles sont vérifiées.

    ⚠️ UNE OFFRE SANS `verifie` NE SORT PAS. Même règle que pour les
    employeurs : on n'envoie personne vers un lien qu'on n'a pas ouvert.
    """
    pretes = [o for o in OFFRES if o.get("verifie") and o.get("url")]
    if not pretes:
        return ""          # rien à montrer : la page ne change pas
    cartes = []
    for o in pretes:
        detail = " · ".join(x for x in [o.get("ville", ""), o.get("permis", "")] if x)
        cartes.append(
            '      <a class="jb" href="%s" target="_blank" rel="noopener">\n'
            '        <span class="n"><h3>%s</h3><span class="z">%s</span></span>\n'
            '        <p>%s</p>\n'
            '        <span class="v" data-t="voir">%s</span>\n'
            '      </a>' % (o["url"], o["employeur"], detail,
                            o.get("poste", ""), t("voir")))
    return ('    <div class="jb-sec">\n      <h2 data-t="offres_t">%s</h2>\n'
            '      <p class="n" data-t="offres_d">%s</p>\n'
            '      <div class="jb-liste">\n%s\n      </div>\n    </div>\n'
            % (t("offres_t"), t("offres_d"), "\n".join(cartes)))

FILTRES = [("tous", "f_tous"), ("aucun", "f_aucun"), ("7d", "f_7d"),
           ("cdlb", "f_cdlb"), ("cdla", "f_cdla"), ("forme", "f_forme")]


def barre():
    """La barre de filtres.

    ⚠️ « Ils vous forment » EST LE FILTRE QUI JUSTIFIE LA PAGE. Indeed ne sait
    pas le proposer : l'information n'est dans aucune annonce, elle est dans la
    connaissance du secteur. C'est la seule chose qu'on offre et qu'un
    agregateur ne peut pas offrir.
    """
    b = "".join(
        '<button type="button" class="jb-f" data-f="%s" data-t="%s"'
        ' aria-pressed="%s">%s</button>' % (f, k, "true" if f == "tous" else "false", t(k))
        for f, k in FILTRES)
    return (
        '    <div class="jb-filtres">\n'
        '      <label class="sr-only" for="jb-rech" data-t="f_rech">%s</label>\n'
        '      <input id="jb-rech" class="jb-f-rech" type="search"'
        ' placeholder="%s" data-tp="f_rech" />\n'
        '      <div class="jb-f-lig" role="group" aria-label="%s">%s</div>\n'
        '      <p class="jb-compte" id="jb-compte">%d <span data-t="f_compte">%s</span></p>\n'
        '    </div>\n'
        '    <p class="jb-vide" id="jb-vide" data-t="f_rien" style="display:none">%s</p>'
        % (t("f_rech"), t("f_rech"), t("f_titre"), b,
           len(montres()), t("f_compte"), t("f_rien")))


def construire():
    # ⚠️ PAS DE BARRE DE FILTRES EN PERIMETRE DSP. Sept filtres de permis
    # (7D, CDL-B, CDL-A…) pour une seule section, c'est du bruit — et des
    # boutons qui filtrent vers le vide. Le script de la page sort proprement
    # quand la barre est absente (`if(!champ||...) return`).
    corps = [] if portee.dsp() else [barre()]
    for genre, titres in SECTIONS:
        if not portee.section_active(genre):
            continue           # en pause : la fiche reste dans emplois.py
        gens = [e for e in EMPLOYEURS if e["genre"] == genre]
        if not gens:
            continue
        corps.append('    <div class="jb-sec">\n      <h2 data-t="s_%s">%s</h2>\n'
                     '      <div class="jb-liste">\n%s\n      </div>\n    </div>'
                     % (genre, titres["en"], "\n".join(carte(e) for e in gens)))
    recues = offres()
    return (recues + "\n" if recues else "") + "\n".join(corps)


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="icon" href="assets/brand/favicon.ico" sizes="any" />
  <link rel="icon" type="image/png" href="assets/brand/logo-32.png" />
  <link rel="apple-touch-icon" href="assets/brand/apple-touch-icon.png" />
  <title>Driving jobs in Massachusetts — Driver360</title>
  <meta name="description" content="%(descr)s" />
  <link rel="canonical" href="https://driver360.atmart.ltd/jobs.html" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet" />
  <link rel="manifest" href="manifest.webmanifest" />
  <meta name="theme-color" content="#0e2240" />
  <link rel="stylesheet" href="assets/style.css?v=33" />
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
    <p class="lead" data-t="lead_court">%(lead_court)s</p>
    <details class="jb-plus">
      <summary data-t="lead_plus">%(lead_plus)s</summary>
      <p data-t="lead">%(lead)s</p>
    </details>
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

    <div class="jb-note jb-emp">
      <h2 data-t="pub_t">%(pub_t)s</h2>
      <p data-t="pub_d">%(pub_d)s</p>
      <p style="margin-top:1.1rem">
        <a class="lien-action" href="%(mailto_pub)s" data-t="pub_b">%(pub_b)s</a>
      </p>
      <p style="margin-top:.7rem;font-size:.84rem;color:#9db2c7" data-t="pub_n">%(pub_n)s</p>
    </div>

    <div class="jb-note">
      <h2 data-t="permis_t">%(permis_t)s</h2>
      <p data-t="permis_d">%(permis_d)s</p>
      <p style="margin-top:1.1rem">
        <a class="lien-action" href="wout.html" data-t="permis_b">%(permis_b)s</a>
      </p>
    </div>

    <div class="jb-note">
      <h2 data-t="manque_t">%(manque_t)s</h2>
      <p data-t="manque_d">%(manque_d)s</p>
      <p style="margin-top:1.1rem">
        <a class="lien-action" href="%(mailto)s" data-t="manque_b">%(manque_b)s</a>
      </p>
    </div>
  </div>
</section>

%(pied)s

<script>
var T = %(dico)s;
var TITRE0 = document.title;   /* le titre anglais, ecrit dans le <title> */
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
/* Le menu de langue vit dans assets/suite.js et se contente de poser `lang`
   sur <html> : c'est ce changement qu'on observe. Cette page construisait
   autrefois sa propre rangee de boutons ; le jour ou elle a disparu, le script
   sortait avant meme de traduire (il cherchait un element absent) et la page
   restait en anglais sous un pied traduit. */
new MutationObserver(appliquer).observe(document.documentElement,
  {attributes:true, attributeFilter:["lang"]});
</script>
<script src="assets/suite.js?v=6"></script>
<script>if("serviceWorker" in navigator){navigator.serviceWorker.register("/sw.js");}</script>

  <script>
  (function(){
    var champ=document.getElementById("jb-rech");
    var btns=[].slice.call(document.querySelectorAll(".jb-f"));
    var cartes=[].slice.call(document.querySelectorAll(".jb"));
    var compte=document.getElementById("jb-compte");
    var vide=document.getElementById("jb-vide");
    if(!champ||!cartes.length) return;
    var actif="tous";
    function filtrer(){
      var q=(champ.value||"").trim().toLowerCase(), n=0;
      cartes.forEach(function(c){
        var permis=(c.dataset.permis||"").split(" ");
        var okP = actif==="tous"
          || (actif==="forme" ? c.dataset.forme==="1" : permis.indexOf(actif)>=0);
        var okQ = !q || (c.textContent||"").toLowerCase().indexOf(q)>=0;
        var ok = okP && okQ;
        c.style.display = ok ? "" : "none";
        if(ok) n++;
      });
      // une section dont toutes les cartes sont masquees ne doit pas laisser
      // son titre orphelin en haut d'un vide
      [].slice.call(document.querySelectorAll(".jb-sec")).forEach(function(s){
        var v=[].slice.call(s.querySelectorAll(".jb"))
                .some(function(c){return c.style.display!=="none"});
        s.classList.toggle("off",!v);
      });
      if(compte) compte.firstChild.nodeValue=n+" ";
      if(vide) vide.style.display = n ? "none" : "";
    }
    btns.forEach(function(b){
      b.addEventListener("click",function(){
        actif=b.dataset.f;
        btns.forEach(function(x){x.setAttribute("aria-pressed", x===b?"true":"false")});
        filtrer();
      });
    });
    champ.addEventListener("input",filtrer);
    filtrer();
  })();
  </script>
</body>
</html>
"""


def ecrire():
    import json
    champs = {k: t(k) for k in TX}
    champs.update(mailto_pub=MAILTO_PUB, css=CSS, entete=entete("jobs.html"), pied=PIED,
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
    print("jobs.html ecrit : %d employeur(s) montre(s) sur %d, perimetre %s, %d octets"
          % (len(montres()), len(EMPLOYEURS), portee.PORTEE, n))
