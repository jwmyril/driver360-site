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
    "lead_court":  {'en': 'Twenty employers who actually hire drivers here, each linking straight to their own openings. Filter by the licence you already have.', 'fr': 'Vingt employeurs qui recrutent vraiment des chauffeurs ici, chacun renvoyant droit à ses propres offres. Filtrez selon le permis que vous avez déjà.', 'ht': 'Ven anplwayè ki anbochte chofè tout bon isit la, chak youn voye w dirèk sou pwòp òf pa l. Filtre selon pèmi ou genyen deja.', 'es': 'Veinte empleadores que de verdad contratan choferes aquí, cada uno enlazando directo a sus propias vacantes. Filtra según la licencia que ya tienes.'},
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
        "en": "We do not host job adverts and we do not copy them. Below is the list of employers who actually hire drivers here, with a link straight to their own openings — so you apply in the right place. The <em>links</em> do not go stale; the <em>requirements</em> can. Anything we state about age, licence or checks was taken from an official source on the date below, and each employer sets its own rules and changes them without telling us. Read their page before you count on ours.",
        "fr": "Nous n'hébergeons pas d'annonces et nous n'en recopions aucune. Voici la liste des employeurs qui recrutent réellement des chauffeurs ici, avec un lien direct vers leurs propres offres — vous postulez donc au bon endroit. Ce sont les <em>liens</em> qui ne périment pas ; les <em>conditions</em>, si. Ce que nous disons d'un âge, d'un permis ou d'un contrôle vient d'une source officielle à la date ci-dessous, et chaque employeur fixe ses propres règles et les change sans nous prévenir. Lisez leur page avant de compter sur la nôtre.",
        "ht": "Nou pa gen anons lakay nou epi nou pa kopye okenn. Men lis anplwayè ki tout bon ap chèche chofè isit la, ak yon lyen dirèk sou òf pa yo — konsa ou aplike nan bon kote a. Se <em>lyen</em> yo ki pa vin vye ; <em>kondisyon</em> yo, wi. Sa nou di sou yon laj, yon pèmi oswa yon kontòl soti nan yon sous ofisyèl nan dat ki anba a, epi chak anplwayè mete pwòp règ pa l epi chanje yo san avèti nou. Li paj pa yo anvan w konte sou pa nou.",
        "es": "No alojamos anuncios ni los copiamos. Esta es la lista de empleadores que de verdad contratan conductores aquí, con un enlace directo a sus propias vacantes — así postulas en el sitio correcto. Son los <em>enlaces</em> los que no caducan; los <em>requisitos</em>, sí. Lo que decimos sobre una edad, una licencia o un control viene de una fuente oficial en la fecha de abajo, y cada empleador fija sus propias reglas y las cambia sin avisarnos. Lee su página antes de fiarte de la nuestra.",
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
           len(EMPLOYEURS), t("f_compte"), t("f_rien")))


def construire():
    corps = [barre()]
    for genre, titres in SECTIONS:
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
  <meta name="description" content="Who actually hires drivers in Massachusetts: school transport, regional transit authorities and the state job board. Checked links, straight to each employer's own openings. Free WhatsApp alerts when a new one opens." />
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
    print("jobs.html ecrit : %d employeurs, %d octets" % (len(EMPLOYEURS), n))
