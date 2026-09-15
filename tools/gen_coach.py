# -*- coding: utf-8 -*-
"""Fabrique wout.html — Driver Coach, le coach CARRIÈRE des chauffeurs DSP.

    python tools/gen_coach.py

DÉCISION DU 15/09/2026. « Orientez le coach driver vers l'amélioration de la
carrière des chauffeurs » — dans un Driver360 qui ne sert plus, pour le
moment, que les DSP d'Amazon (voir tools/portee.py).

POURQUOI UNE PAGE FABRIQUÉE, ET PLUS DÉRIVÉE
--------------------------------------------
wout.html était dérivée de `Atmart_website/chofe360.html`, le coach du TEST DE
ROUTE Class D : grille de manœuvres, guide de l'accompagnateur, résultats du
RMV, commandes de l'examinateur. Tout y est bâti pour quelqu'un qui n'a pas
encore son permis. Un chauffeur de DSP l'a déjà : c'est une condition
d'embauche.

Rapiécer onze cents lignes pour en faire autre chose aurait laissé traîner
des morceaux du produit précédent — une page à moitié dans un produit, à
moitié dans l'autre. On fabrique donc une page propre. La source d'atmart.ltd
n'est pas touchée : le coach du test de route y reste entier.

CE QUE LE COACH FAIT — cinq rôles précis (précisé le 15/09/2026)
Amazon et chaque DSP forment déjà les chauffeurs au métier : sécurité,
procédures de livraison, appareils, tournées. Le coach NE DOUBLE PAS cette
formation et renvoie ces questions vers le DSP. Son rôle est la place du
chauffeur dans le réseau :
  1. devenir DSP-ready (la liste, honnêtement, et ce que le DSP vérifiera) ;
  2. tenir le dossier à jour (déclaration du chauffeur ; statut à 14 jours) ;
  3. une pause, et le retour (seul le DSP dit ce qui est à refaire) ;
  4. lire une offre avant de dire oui ;
  5. rencontrer un DSP — répéter, caméra comprise : un miroir, pas un jury.
Jamais la promesse qu'un DSP va embaucher.

⚠️ CE QU'IL NE PRÉTEND PAS. La présentation classe le dossier portable,
le partage avec des DSP et l'échange d'expérience en « proposed
development ». La page le dit : le coach ne conserve aucun dossier et
n'envoie rien à aucun DSP.

Le prompt du coach vit dans tools/gen_doctrine.py (CARRIERE), pas ici :
une seule source, que le build contrôle.

⚠️ Le kreyòl est à relire par l'utilisateur.
"""
import io
import json
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from regen import entete, PIED  # noqa: E402  regen re-enveloppe sys.stdout
import portee  # noqa: E402

EP = "https://atmart-chat.atmartllc.workers.dev/wout"
MAILTO_CODE = ("mailto:sales@atmart.ltd?subject=Driver360%20-%20Driver%20Coach%20code"
               "&amp;body=Hello%2C%0A%0AI%20would%20like%20a%20free%20Driver%20Coach%20code.%0A%0AThank%20you.")

# (en, fr, ht, es)
TX = {
 "ti": ("Driver Coach — stay DSP-ready as a delivery driver | Driver360",
        "Driver Coach — rester DSP-ready comme chauffeur livreur | Driver360",
        "Driver Coach — rete DSP-ready kòm chofè livrezon | Driver360",
        "Driver Coach — seguir DSP-ready como conductor de reparto | Driver360"),
 "descr": ("A coach for delivery drivers at Amazon's Delivery Service Partners in Massachusetts: get DSP-ready, keep your record current, take a break and come back, read a job opening, and prepare to meet a DSP. Independent — not affiliated with Amazon.",
        "Un coach pour les chauffeurs livreurs des partenaires de livraison d'Amazon au Massachusetts : devenir DSP-ready, tenir votre dossier à jour, faire une pause et revenir, lire une offre, préparer la rencontre avec un DSP. Indépendant — non affilié à Amazon.",
        "Yon coach pou chofè livrezon patnè livrezon Amazon yo nan Massachusetts : vin DSP-ready, kenbe dosye w ajou, pran yon poz epi retounen, li yon òf travay, prepare w pou rankontre yon DSP. Endepandan — pa afilye ak Amazon.",
        "Un coach para conductores de reparto de los socios de entrega de Amazon en Massachusetts: estar DSP-ready, mantener tu historial al día, tomar una pausa y volver, leer una oferta y prepararte para conocer a un DSP. Independiente — sin afiliación con Amazon."),
 "fil": ("For delivery drivers at Amazon's Delivery Service Partners",
         "Pour les chauffeurs livreurs des partenaires de livraison d'Amazon",
         "Pou chofè livrezon patnè livrezon Amazon yo",
         "Para conductores de reparto de los socios de entrega de Amazon"),
 "lead": ("Amazon and your DSP train you for the job. This coach does what one DSP cannot do for you: it helps you stay ready and current — from one DSP to the next, through a break and back.",
        "Amazon et votre DSP vous forment au métier. Ce coach fait ce qu'un seul DSP ne peut pas faire pour vous : vous aider à rester prêt et à jour — d'un DSP à l'autre, pendant une pause et au retour.",
        "Amazon ak DSP ou fòme w pou travay la. Coach sa a fè sa yon sèl DSP pa ka fè pou ou : li ede w rete pare epi ajou — soti nan yon DSP rive nan yon lòt, pandan yon poz ak lè w retounen.",
        "Amazon y tu DSP te forman para el trabajo. Este coach hace lo que un solo DSP no puede hacer por ti: ayudarte a seguir listo y al día — de un DSP al siguiente, durante una pausa y a la vuelta."),
 "indep": ("Driver360 is independent. It is not affiliated with Amazon, and Amazon does not endorse it.",
           "Driver360 est indépendant. Il n'est pas affilié à Amazon, et Amazon ne l'approuve pas.",
           "Driver360 endepandan. Li pa afilye ak Amazon, epi Amazon pa apwouve l.",
           "Driver360 es independiente. No está afiliado a Amazon, y Amazon no lo avala."),

 "c1_t": ("Get DSP-ready",
        "Devenir DSP-ready",
        "Vin DSP-ready",
        "Estar DSP-ready"),
 "c1_d": ("Go through the checklist one item at a time — 21 or older, licence, work authorization, driving record, checks, lifting 50 lb, a phone that answers, an interview slot. Honestly, and knowing what the DSP will still check at hiring.",
        "Passer la liste point par point — 21 ans ou plus, permis, autorisation de travail, dossier de conduite, contrôles, porter 50 lb, un téléphone qui répond, un créneau d'entretien. En toute honnêteté, et en sachant ce que le DSP vérifiera encore à l'embauche.",
        "Pase lis la youn pa youn — 21 an oswa plis, pèmi, otorizasyon travay, dosye kondwi, kontwòl, leve 50 liv, yon telefòn ki reponn, yon lè pou entèvyou. Avèk onètete, epi konnen sa DSP a ap toujou tcheke lè l ap anboche.",
        "Repasar la lista punto por punto — 21 años o más, licencia, autorización de trabajo, historial de manejo, comprobaciones, levantar 50 lb, un teléfono que contesta, un horario de entrevista. Con honestidad, y sabiendo lo que el DSP seguirá comprobando al contratar."),
 "c2_t": ("Keep your record current",
        "Tenir votre dossier à jour",
        "Kenbe dosye w ajou",
        "Mantener tu historial al día"),
 "c2_d": ("Roles, dates, stations, vehicles, trainings completed — written plainly as your own statement, in a text you keep — and references who agreed to be named. A reminder too: DSP-ready needs an interview slot in the next 72 hours and an update in the last 14 days — to keep it, open your registration and pick new slots.",
        "Postes, dates, stations, véhicules, formations terminées — écrits simplement comme votre propre déclaration, dans un texte que vous gardez — et des références qui ont accepté d'être nommées. Et un rappel : DSP-ready demande un créneau d'entretien dans les 72 heures et une mise à jour dans les 14 derniers jours — pour le garder, rouvrez votre inscription et choisissez de nouveaux créneaux.",
        "Pòs, dat, estasyon, machin, fòmasyon ou fini — ekri senp kòm pwòp deklarasyon pa w, nan yon tèks ou kenbe — ak referans ki dakò pou yo site non yo. Epi yon rapèl : DSP-ready mande yon lè pou entèvyou nan 72 èdtan ki vini yo ak yon mizajou nan 14 dènye jou yo — pou w kenbe l, louvri enskripsyon w epi chwazi lòt moman.",
        "Puestos, fechas, estaciones, vehículos, formación terminada — escrito con sencillez como tu propia declaración, en un texto que guardas — y referencias que aceptaron ser nombradas. Y un recordatorio: DSP-ready requiere un horario de entrevista en las próximas 72 horas y una actualización en los últimos 14 días — para mantenerlo, abre tu inscripción y elige nuevos horarios."),
 "c3_t": ("A break, and coming back",
        "Une pause, et le retour",
        "Yon poz, epi retou a",
        "Una pausa, y la vuelta"),
 "c3_d": ("Pause your profile so DSPs stop seeing you, keep what you will need, and prepare your return — your profile is erased 90 days after its last update, even on pause. Only the DSP can say which checks or trainings start again — the coach helps you ask.",
        "Mettre votre profil en pause pour que les DSP ne vous voient plus, garder ce dont vous aurez besoin, préparer le retour — votre fiche est effacée 90 jours après sa dernière mise à jour, même en pause. Seul le DSP peut dire quels contrôles ou formations sont à refaire — le coach vous aide à le demander.",
        "Mete pwofil ou an pòz pou DSP yo pa wè w ankò, kenbe sa w ap bezwen, epi prepare retou w — pwofil ou efase 90 jou apre dènye mizajou li, menm lè l an pòz. Se sèlman DSP a ki ka di ki kontwòl oswa fòmasyon ki pou refèt — coach la ede w mande sa.",
        "Pausar tu perfil para que los DSP dejen de verte, guardar lo que vas a necesitar y preparar la vuelta — tu perfil se borra 90 días después de su última actualización, incluso en pausa. Solo el DSP puede decir qué comprobaciones o formaciones se repiten — el coach te ayuda a preguntarlo."),
 "c4_t": ("Read an opening",
        "Lire une offre",
        "Li yon òf travay",
        "Leer una oferta"),
 "c4_d": ("Pay, stated hours, days, station, commute, whether training is paid — what the posting says, what it leaves out, and what to ask before you say yes.",
        "Salaire, heures annoncées, jours, station, trajet, formation payée ou non — ce que dit l'offre, ce qu'elle ne dit pas, et ce qu'il faut demander avant de dire oui.",
        "Salè, èdtan yo anonse, jou, estasyon, trajè, si fòmasyon an peye — sa òf la di, sa li pa di, ak sa pou w mande anvan w di wi.",
        "Pago, horas anunciadas, días, estación, trayecto, si la formación es pagada — lo que dice la oferta, lo que no dice y qué preguntar antes de decir que sí."),
 "c5_t": ("Meet a DSP",
        "Rencontrer un DSP",
        "Rankontre yon DSP",
        "Conocer a un DSP"),
 "c5_d": ("Rehearse how you present your experience in about 60 seconds, in your language, then in English if you want. Feedback on your words — never on your accent or appearance.",
        "Répéter comment vous présentez votre expérience en une minute environ, dans votre langue, puis en anglais si vous le souhaitez. Des retours sur vos mots — jamais sur votre accent ni votre apparence.",
        "Repete kijan w prezante eksperyans ou nan anviwon 60 segonn, nan lang pa w, epi an anglè si w vle. Kòmantè sou mo w yo — pa janm sou aksan w oswa sou aparans ou.",
        "Ensayar cómo presentas tu experiencia en unos 60 segundos, en tu idioma, y luego en inglés si quieres. Comentarios sobre tus palabras — nunca sobre tu acento ni tu apariencia."),

 "h_t": ("What this coach is, and is not", "Ce qu'est ce coach, et ce qu'il n'est pas",
         "Sa coach sa a ye, ak sa li pa ye", "Lo que es este coach, y lo que no es"),
 "h_d": ("It does <strong>not</strong> repeat the training Amazon and your DSP give you: safety, delivery procedures, devices, routes and station rules are theirs, and the coach sends those questions back to your DSP. It does not store a professional record or send anything to a DSP — that part is not built yet. What you write together is yours to copy and keep. It will never give you a score, and it will never invent a pay rate or a requirement: when it does not know, it tells you to ask the DSP.",
        "Il ne <strong>refait pas</strong> la formation qu'Amazon et votre DSP vous donnent : la sécurité, les procédures de livraison, les appareils, les tournées et les règles de la station leur appartiennent, et le coach vous renvoie vers votre DSP pour ces questions. Il ne conserve pas de dossier professionnel et n'envoie rien à aucun DSP — cette partie n'est pas encore construite. Ce que vous écrivez ensemble vous appartient : copiez-le et gardez-le. Il ne vous donnera jamais de note, et il n'inventera jamais un salaire ou une condition : quand il ne sait pas, il vous dit de demander au DSP.",
        "Li <strong>pa</strong> refè fòmasyon Amazon ak DSP ou ba ou : sekirite, fason pou livre, aparèy, wout ak règ estasyon an se pou yo, epi coach la voye w bay DSP ou pou kesyon sa yo. Li pa kenbe okenn dosye pwofesyonèl epi li pa voye anyen bay okenn DSP — pati sa a poko bati. Sa nou ekri ansanm se pou ou : kopye l epi kenbe l. Li p ap janm ba w yon nòt, epi li p ap janm envante yon salè oswa yon kondisyon : lè li pa konnen, li di w mande DSP a.",
        "<strong>No</strong> repite la formación que te dan Amazon y tu DSP: la seguridad, los procedimientos de entrega, los dispositivos, las rutas y las normas de la estación son suyos, y el coach te remite a tu DSP para esas preguntas. No guarda un expediente profesional ni envía nada a ningún DSP — esa parte todavía no está construida. Lo que escribimos juntos es tuyo: cópialo y guárdalo. Nunca te pondrá una nota, y nunca se inventará un salario o un requisito: cuando no lo sabe, te dice que se lo preguntes al DSP."),

 "code_l": ("Your coach code", "Votre code du coach", "Kòd coach ou", "Tu código del coach"),
 "code_s": ("Free (WOUT-XXXX-XXXX). No code yet? <a href='%s'>Request one — free</a>" % MAILTO_CODE,
            "Gratuit (WOUT-XXXX-XXXX). Pas encore de code ? <a href='%s'>Demandez-le — gratuit</a>" % MAILTO_CODE,
            "Gratis (WOUT-XXXX-XXXX). Ou poko gen kòd ? <a href='%s'>Mande l — gratis</a>" % MAILTO_CODE,
            "Gratis (WOUT-XXXX-XXXX). ¿Aún sin código? <a href='%s'>Pídelo — gratis</a>" % MAILTO_CODE),

 "chat_t": ("Talk to your coach", "Parler à votre coach", "Pale ak coach ou", "Habla con tu coach"),
 "hello": ("Hi — I'm your Driver Coach. We can get you DSP-ready, update your record, plan a break or a return, read a job opening, or prepare to meet a DSP. Where would you like to start?",
        "Bonjour — je suis votre Driver Coach. Nous pouvons vous rendre DSP-ready, mettre votre dossier à jour, préparer une pause ou un retour, lire une offre, ou préparer une rencontre avec un DSP. Par où voulez-vous commencer ?",
        "Bonjou — se mwen ki Driver Coach ou. Nou ka fè w vin DSP-ready, mete dosye w ajou, prepare yon poz oswa yon retou, li yon òf travay, oswa prepare w pou rankontre yon DSP. Kote ou vle kòmanse ?",
        "Hola — soy tu Driver Coach. Podemos dejarte DSP-ready, actualizar tu historial, preparar una pausa o una vuelta, leer una oferta o prepararte para conocer a un DSP. ¿Por dónde quieres empezar?"),
 "q1": ("Go through the DSP-ready checklist with me",
        "Passons la liste DSP-ready ensemble",
        "Ann pase lis DSP-ready a ansanm",
        "Repasemos juntos la lista DSP-ready"),
 "q2": ("Help me update my record",
        "Aidez-moi à mettre mon dossier à jour",
        "Ede m mete dosye m ajou",
        "Ayúdame a actualizar mi historial"),
 "q3": ("I'm taking a break — how do I come back?",
        "Je fais une pause — comment revenir ?",
        "M ap pran yon poz — kijan pou m retounen ?",
        "Me tomo una pausa — ¿cómo vuelvo?"),
 "q4": ("Help me read a job opening",
        "Aidez-moi à lire une offre",
        "Ede m li yon òf travay",
        "Ayúdame a leer una oferta"),
 "q5": ("Help me prepare to meet a DSP",
        "Aidez-moi à préparer une rencontre avec un DSP",
        "Ede m prepare m pou m rankontre yon DSP",
        "Ayúdame a prepararme para conocer a un DSP"),
 "ph": ("Write to your coach…", "Écrivez à votre coach…", "Ekri coach ou…", "Escribe a tu coach…"),
 "send": ("Send", "Envoyer", "Voye", "Enviar"),
 "think": ("Your coach is thinking…", "Votre coach réfléchit…", "Coach ou ap reflechi…", "Tu coach está pensando…"),
 "need": ("Enter your coach code first.", "Entrez d'abord votre code du coach.", "Mete kòd coach ou an premye.", "Escribe primero tu código del coach."),
 "e_inv": ("That code is not recognised. Check it, or request a free one.", "Ce code n'est pas reconnu. Vérifiez-le, ou demandez-en un gratuit.", "Kòd sa a pa rekonèt. Tcheke l, oswa mande youn gratis.", "Ese código no se reconoce. Revísalo, o pide uno gratis."),
 "e_exp": ("This code has expired. Write to us for a new one.", "Ce code a expiré. Écrivez-nous pour en obtenir un nouveau.", "Kòd sa a ekspire. Ekri nou pou w jwenn yon lòt.", "Este código ha caducado. Escríbenos para conseguir uno nuevo."),
 "e_lim": ("You have reached today's limit. Come back tomorrow.", "Vous avez atteint la limite du jour. Revenez demain.", "Ou rive nan limit jodi a. Tounen demen.", "Has llegado al límite de hoy. Vuelve mañana."),
 "e_err": ("Something went wrong. Try again in a moment.", "Un problème est survenu. Réessayez dans un instant.", "Gen yon pwoblèm. Eseye ankò talè.", "Algo salió mal. Inténtalo de nuevo en un momento."),
 "priv": ("\U0001F512 Your conversation is tied to your code, not to your name.", "\U0001F512 Votre conversation est liée à votre code, pas à votre nom.", "\U0001F512 Konvèsasyon ou mare ak kòd ou, pa ak non w.", "\U0001F512 Tu conversación está ligada a tu código, no a tu nombre."),
 # ⚠️ LIBELLE EXACT. L'action `delete` du Worker remet le dossier a zero mais
 # GARDE le code valide (st = {exp, plan}). Dire « effacer » sans preciser
 # ferait croire au chauffeur qu'il perd son acces.
 "erase": ('Erase everything tied to my code — the code keeps working', 'Effacer tout ce qui est lié à mon code — le code reste valable', 'Efase tout sa ki mare ak kòd mwen — kòd la ap kontinye mache', 'Borrar todo lo ligado a mi código — el código sigue valiendo'),
 "erased": ("Erased. Your code still works.", "Effacé. Votre code fonctionne toujours.", "Efase. Kòd ou toujou mache.", "Borrado. Tu código sigue funcionando."),

 "cam_t": ("\U0001F3A5 Rehearse on camera", "\U0001F3A5 Répéter devant la caméra", "\U0001F3A5 Repete devan kamera", "\U0001F3A5 Ensaya ante la cámara"),
 "cam_priv": ("The video stays on your phone. It goes nowhere, we never see it, and there is no upload: it disappears when you close the page. And we do not score your face, your posture or your “confidence”. Those signals differ from one culture to the next: scoring them would mean measuring how far you sit from a norm. The camera is a mirror, not a jury.",
              "La vidéo reste dans votre téléphone. Elle ne part nulle part, nous ne la voyons jamais, et il n'y a aucun envoi : elle disparaît quand vous fermez la page. Et nous ne notons ni votre visage, ni votre posture, ni votre « confiance ». Ces signaux changent d'une culture à l'autre : les noter reviendrait à mesurer votre écart à une norme. La caméra est un miroir, pas un jury.",
              'Videyo a rete nan telefòn ou. Li pa ale okenn kote, nou pa janm wè l, epi pa gen anyen ki voye : li disparèt lè w fèmen paj la. Epi nou pa bay nòt ni pou figi w, ni pou posti w, ni pou « konfyans » ou. Siy sa yo pa menm nan chak kilti : bay yo nòt ta vle di mezire distans ki genyen ant ou ak yon nòm. Kamera a se yon glas, se pa yon jiri.',
              "El vídeo se queda en tu teléfono. No va a ninguna parte, nunca lo vemos y no hay envío: desaparece cuando cierras la página. Y no puntuamos ni tu cara, ni tu postura, ni tu «confianza». Esas señales cambian de una cultura a otra: puntuarlas sería medir cuánto te alejas de una norma. La cámara es un espejo, no un jurado."),
 "cam_sub": ("Say it out loud, then watch yourself. Hearing your own words is worth more than any tip.",
             "Dites-le à voix haute, puis regardez-vous. Entendre vos propres mots vaut plus que tous les conseils.",
             "Di l fò, epi gade tèt ou. Tande pwòp mo pa w vo plis pase nenpòt konsèy.",
             "Dilo en voz alta y luego mírate. Oír tus propias palabras vale más que cualquier consejo."),
 "cam_lt": ("What to cover", "Ce qu'il faut dire", "Sa pou w di", "Qué decir"),
 "cam_go": ("Turn on the camera", "Allumer la caméra", "Limen kamera a", "Encender la cámara"),
 "cam_rec": ("● Record", "● Enregistrer", "● Anrejistre", "● Grabar"),
 "cam_stop": ("■ Stop", "■ Arrêter", "■ Kanpe", "■ Detener"),
 "cam_del": ("Delete the recording", "Supprimer l'enregistrement", "Efase anrejistreman an", "Borrar la grabación"),
 "cam_run": ("Recording…", "Enregistrement…", "L ap anrejistre…", "Grabando…"),
 "cam_done": ("Done. Watch it back — it is only on this device.", "C'est fait. Regardez — c'est uniquement sur cet appareil.", "Fini. Gade l — li sèlman sou aparèy sa a.", "Listo. Míralo — solo está en este dispositivo."),
 "cam_no": ("This browser cannot record video.", "Ce navigateur ne peut pas enregistrer de vidéo.", "Navigatè sa a pa ka anrejistre videyo.", "Este navegador no puede grabar vídeo."),
 "cam_off": ("Camera rehearsal is not switched on for this site yet. Everything else on this page works.",
             "La r\u00e9p\u00e9tition devant la cam\u00e9ra n'est pas encore activ\u00e9e sur ce site. Tout le reste de la page fonctionne.",
             "Repetisyon devan kamera a poko aktive sou sit sa a. Tout r\u00e8s paj la mache.",
             "El ensayo ante la c\u00e1mara a\u00fan no est\u00e1 activado en este sitio. Todo lo dem\u00e1s de la p\u00e1gina funciona."),
 "cam_deny": ("The camera was not allowed. You can allow it in your browser settings — or skip this part.", "La caméra n'a pas été autorisée. Vous pouvez l'autoriser dans les réglages du navigateur — ou passer cette partie.", "Kamera a pa te otorize. Ou ka otorize l nan reglaj navigatè a — oswa sote pati sa a.", "No se permitió la cámara. Puedes permitirla en los ajustes del navegador — o saltarte esta parte."),

 "pool_t": ("Ready to be found by DSPs?", "Prêt à être trouvé par des DSP ?", "Ou pare pou DSP yo jwenn ou ?", "¿Listo para que te encuentren los DSP?"),
 "pool_b": ("Join the Driver Pool — free →", "Rejoindre le Driver Pool — gratuit →", "Antre nan Driver Pool la — gratis →", "Unirme al Driver Pool — gratis →"),
}

# Les trois exercices de la camera : (id, onglet, consigne, sous-titre, [points])
EXOS = {
 "en": [["exp", "60 seconds", "Tell a DSP about your experience in 60 seconds.", "Roles, dates, vehicles — and one thing you are proud of.",
         ["How long you have delivered, and where", "The vehicles and kinds of routes you know", "One day that went well because of you"]],
        ["pause", "A break", "Explain a break in your work history.", "Plainly, without apologising.",
         ["That you took a break, and roughly when", "What you did during it", "Why you are ready now"]],
        ["ask", "Your questions", "Ask a DSP about the opening, before you say yes.", "Calmly — asking shows you take the job seriously.",
         ["Pay, and the hours they state", "Days, station and commute", "Whether training is paid, and what the next step is"]]],
 "fr": [["exp", "60 secondes", "Présentez votre expérience à un DSP en 60 secondes.", "Postes, dates, véhicules — et une chose dont vous êtes fier.",
         ["Depuis combien de temps vous livrez, et où", "Les véhicules et les types de tournées que vous connaissez", "Une journée qui s'est bien passée grâce à vous"]],
        ["pause", "Une pause", "Expliquez une pause dans votre parcours.", "Simplement, sans vous excuser.",
         ["Que vous avez fait une pause, et à peu près quand", "Ce que vous avez fait pendant", "Pourquoi vous êtes prêt maintenant"]],
        ["ask", "Vos questions", "Posez vos questions à un DSP sur l'offre, avant de dire oui.", "Calmement — demander montre que vous prenez l'emploi au sérieux.",
         ["Le salaire, et les heures annoncées", "Les jours, la station et le trajet", "Si la formation est payée, et quelle est l'étape suivante"]]],
 "ht": [["exp", "60 segonn", "Prezante eksperyans ou bay yon DSP nan 60 segonn.", 'Pòs, dat, machin — ak yon bagay ki fè w fyè.',
         ["Depi konbyen tan w ap livre, ak ki kote", "Machin ak kalite wout ou konnen", "Yon jou ki te pase byen gras a ou"]],
        ["pause", "Yon poz", "Esplike yon poz nan pakou travay ou.", "Senp, san w pa mande eskiz.",
         ['Ou te pran yon poz, ak apeprè kilè', "Kisa w te fè pandan tan an", "Poukisa w pare kounye a"]],
        ["ask", "Kesyon w yo", "Poze yon DSP kesyon sou òf la, anvan w di wi.", "Trankil — lè w poze kesyon, sa montre w pran travay la oserye.",
         ["Salè a, ak èdtan yo anonse", "Jou yo, estasyon an ak trajè a", "Si fòmasyon an peye, ak ki pwochen etap la"]]],
 "es": [["exp", "60 segundos", "Presenta tu experiencia a un DSP en 60 segundos.", "Puestos, fechas, vehículos — y algo de lo que estés orgulloso.",
         ["Cuánto tiempo llevas repartiendo, y dónde", "Los vehículos y tipos de rutas que conoces", "Un día que salió bien gracias a ti"]],
        ["pause", "Una pausa", "Explica una pausa en tu trayectoria.", "Con sencillez, sin disculparte.",
         ["Que te tomaste una pausa, y más o menos cuándo", "Qué hiciste durante ella", "Por qué estás listo ahora"]],
        ["ask", "Tus preguntas", "Pregúntale a un DSP por la oferta, antes de decir que sí.", "Con calma — preguntar demuestra que te tomas el empleo en serio.",
         ["El pago, y las horas que anuncian", "Los días, la estación y el trayecto", "Si la formación es pagada, y cuál es el siguiente paso"]]],
}

CSS = """
    .co-cartes{display:grid;grid-template-columns:1fr;gap:.85rem;margin-top:1.4rem}
    @media(min-width:760px){.co-cartes{grid-template-columns:1fr 1fr}}
    .co-carte{background:var(--d-surface);border:1px solid var(--d-ligne);border-radius:14px;padding:1.1rem 1.25rem}
    .co-carte h2{margin:0 0 .4rem;font-family:'Space Grotesk',sans-serif;color:var(--d-fort);font-size:1.05rem}
    .co-carte p{margin:0;color:var(--d-doux);font-size:.9rem;line-height:1.6}
    .co-note{background:var(--d-alerte-fond);border:1px solid var(--d-alerte-bord);border-radius:14px;
      padding:1.1rem 1.3rem;margin-top:1.4rem;max-width:74ch}
    .co-note h2{margin:0 0 .45rem;font-family:'Space Grotesk',sans-serif;color:var(--d-fort);font-size:1.05rem}
    .co-note p{margin:0;color:var(--d-texte);font-size:.92rem;line-height:1.7}
    .co-bloc{background:var(--d-surface);border:1px solid var(--d-ligne);border-radius:16px;padding:1.3rem 1.4rem;margin-top:1.6rem}
    .co-bloc>h2{margin:0 0 .8rem;font-family:'Space Grotesk',sans-serif;color:var(--d-fort);font-size:1.2rem}
    .co-champ{width:100%;max-width:340px;background:var(--d-fond);color:var(--d-fort);border:1px solid var(--d-ligne);
      border-radius:9px;padding:.6rem .8rem;font:inherit;font-size:16px;min-height:44px;text-transform:uppercase}
    .co-aide{color:var(--d-doux);font-size:.85rem;margin:.4rem 0 0}
    .co-aide a{color:var(--d-accent);text-decoration:underline}
    .co-msgs{max-height:48vh;overflow-y:auto;display:flex;flex-direction:column;gap:.6rem;margin:1rem 0 .8rem;padding:.2rem}
    .co-m{max-width:88%;padding:.65rem .9rem;border-radius:13px;font-size:.95rem;line-height:1.6;white-space:pre-wrap}
    .co-m.coach{align-self:flex-start;background:var(--d-surface-2);color:var(--d-texte)}
    .co-m.user{align-self:flex-end;background:var(--d-accent-fond);color:var(--d-fort);border:1px solid var(--d-accent-bord)}
    .co-rapides{display:flex;flex-wrap:wrap;gap:.4rem;margin-bottom:.7rem}
    .co-rapides button{background:var(--d-surface-2);color:var(--d-texte);border:1px solid var(--d-ligne);
      border-radius:999px;padding:.45rem .85rem;font:inherit;font-size:.86rem;cursor:pointer;min-height:44px}
    .co-rapides button:hover{border-color:var(--d-accent-bord)}
    .co-saisie{display:flex;gap:.5rem;align-items:flex-end;flex-wrap:wrap}
    .co-saisie textarea{flex:1 1 260px;min-height:64px;background:var(--d-fond);color:var(--d-fort);
      border:1px solid var(--d-ligne);border-radius:10px;padding:.6rem .8rem;font:inherit;font-size:16px;resize:vertical}
    .co-st{color:var(--d-alerte);font-size:.88rem;min-height:1.3em;margin:.5rem 0 0}
    .co-bas{display:flex;flex-wrap:wrap;gap:.8rem;align-items:center;justify-content:space-between;margin-top:.8rem;
      color:var(--d-doux);font-size:.84rem}
    .co-lien{background:none;border:0;color:var(--d-accent);text-decoration:underline;font:inherit;font-size:.84rem;
      cursor:pointer;padding:.4rem 0;min-height:44px}
    .cf-ex{display:flex;flex-wrap:wrap;gap:0.4rem;margin-bottom:0.8rem}
    .cf-ex button{background:var(--d-surface-2);color:var(--d-texte);border:1px solid var(--d-ligne);
      border-radius:999px;padding:.45rem .85rem;font:inherit;font-size:.86rem;cursor:pointer;min-height:44px}
    .cf-ex button[aria-pressed="true"]{background:var(--d-accent);color:var(--d-accent-encre);border-color:var(--d-accent);font-weight:600}
    .cf-consigne{margin:.2rem 0 .5rem}
    .cf-consigne .en{display:block;color:var(--d-fort);font-weight:600;font-size:1.02rem;line-height:1.5}
    .cf-consigne .loc{color:var(--d-doux);font-size:0.88rem;line-height:1.6}
    .cam-liste{margin:.3rem 0 .8rem;padding-left:1.2rem;color:var(--d-texte);font-size:.9rem;line-height:1.7}
    .cf-video{width:100%;max-width:480px;aspect-ratio:4/3;background:var(--d-fond-2);border-radius:12px;display:block;margin-top:.4rem}
    .cf-cam-btns{display:flex;flex-wrap:wrap;gap:0.5rem;margin-top:0.7rem}
    /* ⚠️ .sr-only n'existe pas dans style.css : sans cette regle, l'etiquette du
       champ de message s'affichait en double au-dessus du champ (mesure 15/09). */
    .sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;
      clip:rect(0,0,0,0);white-space:nowrap;border:0}
    /* Le gris par defaut des textes indicatifs mesurait 3,45:1 (sombre) et 4,31:1 (clair). */
    .co-champ::placeholder,.co-saisie textarea::placeholder{color:var(--d-doux);opacity:1}
    .co-avert{color:var(--d-texte);font-size:.9rem;line-height:1.7;background:var(--d-vert-fond);
      border:1px solid var(--d-vert-bord);border-radius:10px;padding:.8rem 1rem;margin:0 0 .8rem}
"""

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="icon" href="assets/brand/favicon.ico" sizes="any" />
  <link rel="icon" type="image/png" href="assets/brand/logo-32.png" />
  <link rel="apple-touch-icon" href="assets/brand/apple-touch-icon.png" />
  <title>%(ti)s</title>
  <meta name="description" content="%(descr)s" />
  <link rel="canonical" href="https://driver360.atmart.ltd/wout.html" />
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

<section class="hero" style="padding-bottom:.4rem">
  <div class="container">
    <p class="kreyol" data-t="fil">%(fil)s</p>
    <h1>Driver Coach</h1>
    <p class="lead" data-t="lead">%(lead)s</p>
    <p style="font-size:.84rem;color:var(--d-doux);margin-top:.6rem" data-t="indep">%(indep)s</p>
  </div>
</section>

<section style="padding-top:.2rem;padding-bottom:2.6rem">
  <div class="container">
    <div class="co-cartes">
      <div class="co-carte"><h2 data-t="c1_t">%(c1_t)s</h2><p data-t="c1_d">%(c1_d)s</p></div>
      <div class="co-carte"><h2 data-t="c2_t">%(c2_t)s</h2><p data-t="c2_d">%(c2_d)s</p></div>
      <div class="co-carte"><h2 data-t="c3_t">%(c3_t)s</h2><p data-t="c3_d">%(c3_d)s</p></div>
      <div class="co-carte"><h2 data-t="c4_t">%(c4_t)s</h2><p data-t="c4_d">%(c4_d)s</p></div>
      <div class="co-carte"><h2 data-t="c5_t">%(c5_t)s</h2><p data-t="c5_d">%(c5_d)s</p></div>
    </div>

    <div class="co-note">
      <h2 data-t="h_t">%(h_t)s</h2>
      <p data-t="h_d">%(h_d)s</p>
    </div>

    <div class="co-bloc">
      <h2 data-t="chat_t">%(chat_t)s</h2>
      <label for="co-code" style="display:block;font-weight:600;color:var(--d-fort);margin-bottom:.3rem" data-t="code_l">%(code_l)s</label>
      <input id="co-code" class="co-champ" type="text" autocomplete="off" spellcheck="false" placeholder="WOUT-XXXX-XXXX" />
      <p class="co-aide" data-t="code_s">%(code_s)s</p>

      <div class="co-msgs" id="co-msgs" role="log" aria-live="polite"></div>
      <div class="co-rapides" id="co-rapides">
        <button type="button" data-t="q1">%(q1)s</button>
        <button type="button" data-t="q2">%(q2)s</button>
        <button type="button" data-t="q3">%(q3)s</button>
        <button type="button" data-t="q4">%(q4)s</button>
        <button type="button" data-t="q5">%(q5)s</button>
      </div>
      <div class="co-saisie">
        <label for="co-input" class="sr-only" data-t="ph">%(ph)s</label>
        <textarea id="co-input" data-tp="ph" placeholder="%(ph)s"></textarea>
        <button type="button" class="btn btn-primary" id="co-send" data-t="send">%(send)s</button>
      </div>
      <p class="co-st" id="co-st" role="status" aria-live="polite"></p>
      <div class="co-bas">
        <span data-t="priv">%(priv)s</span>
        <button type="button" class="co-lien" id="co-erase" data-t="erase">%(erase)s</button>
      </div>
    </div>

    <div class="co-bloc" id="cf-cam">
      <h2 data-t="cam_t">%(cam_t)s</h2>
      <p class="co-avert" data-t="cam_priv">%(cam_priv)s</p>
      <p style="color:var(--d-doux);font-size:.9rem;margin:0 0 .9rem" data-t="cam_sub">%(cam_sub)s</p>
      <div class="cf-ex" id="cam-ex"></div>
      <div class="cf-consigne" id="cam-consigne"></div>
      <p style="margin:.2rem 0 0;font-weight:600;color:var(--d-fort);font-size:.9rem" data-t="cam_lt">%(cam_lt)s</p>
      <ul class="cam-liste" id="cam-liste"></ul>
      <video class="cf-video" id="cam-video" playsinline muted></video>
      <div class="cf-cam-btns">
        <button class="btn" type="button" id="cam-go" data-t="cam_go">%(cam_go)s</button>
        <button class="btn" type="button" id="cam-rec" style="display:none" data-t="cam_rec">%(cam_rec)s</button>
        <button class="btn" type="button" id="cam-stop" style="display:none" data-t="cam_stop">%(cam_stop)s</button>
        <button class="btn" type="button" id="cam-del" style="display:none" data-t="cam_del">%(cam_del)s</button>
      </div>
      <p class="co-st" id="cam-st" role="status" aria-live="polite"></p>
    </div>

    <div class="co-note" style="background:var(--d-accent-fond);border-color:var(--d-accent-bord)">
      <h2 data-t="pool_t">%(pool_t)s</h2>
      <p style="margin-top:.6rem"><a class="btn btn-primary" href="vivye.html" data-t="pool_b">%(pool_b)s</a></p>
    </div>
  </div>
</section>

%(pied)s

<script>
var T = %(dico)s;
var EXOS_EN = %(exos_en)s;
var TITRE0 = document.title;   /* le titre anglais, ecrit dans le <title> */
function lg(){ var l=document.documentElement.lang; return T[l] ? l : "en"; }
/* ⚠️ T PORTE AUSSI L'ANGLAIS. Les messages du chat (erreurs, salutation,
   « entrez votre code ») n'existent dans aucun element du balisage : sans
   T.en, ils sortaient VIDES pour un visiteur anglophone. */
function tr(k){ return (T[lg()] && T[lg()][k]) || T.en[k] || ""; }
function appliquer(){
  var d = T[document.documentElement.lang];   /* en = ce qui est ecrit dans le HTML */
  document.title = (d && d.ti) ? d.ti : TITRE0;
  /* la description suit la langue, comme le titre (ligne B3 du registre) */
  var md = document.querySelector('meta[name="description"]');
  if (md && d && d.descr) md.setAttribute("content", d.descr);
  document.querySelectorAll("[data-t]").forEach(function(e){
    if(!e.dataset.original) e.dataset.original = e.innerHTML;
    e.innerHTML = d ? (d[e.dataset.t] || e.dataset.original) : e.dataset.original;
  });
  document.querySelectorAll("[data-tp]").forEach(function(e){
    if(!e.dataset.ph0) e.dataset.ph0 = e.getAttribute("placeholder") || "";
    e.setAttribute("placeholder", d ? (d[e.dataset.tp] || e.dataset.ph0) : e.dataset.ph0);
  });
  if (window.__camExos) window.__camExos((d && d.exos) || EXOS_EN);
  /* ⚠️ un message pose par cle doit se retraduire a la bascule de langue
     (J15) : « camera pas encore activee » restait en kreyol sur la page anglaise. */
  var cs = document.getElementById("cam-st");
  if (cs && cs.dataset.k) cs.textContent = tr(cs.dataset.k);
}
</script>
<script src="assets/suite.js?v=6"></script>
<script>if("serviceWorker" in navigator){navigator.serviceWorker.register("/sw.js");}</script>

<script>
  // ----------------------------------------------------------- le chat
  // ⚠️ mode:"carriere" — le Worker choisit alors le prompt CARRIERE
  // (tools/gen_doctrine.py) et un historique separe. Le coach du test de
  // route d'atmart.ltd appelle la meme route sans ce parametre.
  (function(){
    var EP = "%(ep)s";
    var codeEl = document.getElementById("co-code");
    var msgs = document.getElementById("co-msgs");
    var st = document.getElementById("co-st");
    var inp = document.getElementById("co-input");
    var occupe = false;
    try { codeEl.value = localStorage.getItem("chofe360_code") || ""; } catch(e) {}
    codeEl.addEventListener("change", function(){
      try { localStorage.setItem("chofe360_code", codeEl.value.trim().toUpperCase()); } catch(e) {}
    });

    function ajouter(role, texte){
      var d = document.createElement("div");
      d.className = "co-m " + (role === "user" ? "user" : "coach");
      d.textContent = texte;             /* jamais innerHTML : c'est le texte d'un modele */
      msgs.appendChild(d); msgs.scrollTop = msgs.scrollHeight;
    }
    function erreur(c){
      return c === "wout_invalid" || c === "trop_essais" ? tr("e_inv")
           : c === "wout_expired" ? tr("e_exp")
           : c === "rate_limited" ? tr("e_lim") : tr("e_err");
    }
    function poster(corps){
      corps.language = lg(); corps.code = codeEl.value.trim().toUpperCase();
      return fetch(EP, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(corps)})
        .then(function(r){ return r.json().then(function(b){ return {ok:r.ok, body:b}; }); });
    }
    function envoyer(texte){
      if (occupe) return;
      texte = (texte || "").trim(); if (!texte) return;
      if (!codeEl.value.trim()) { st.textContent = tr("need"); codeEl.focus(); return; }
      if (!msgs.querySelector(".co-m")) ajouter("coach", tr("hello"));
      occupe = true; ajouter("user", texte); inp.value = ""; st.textContent = tr("think");
      poster({message: texte, mode: "carriere"}).then(function(res){
        occupe = false;
        if (!res.ok) { st.textContent = erreur(res.body && res.body.error); return; }
        st.textContent = ""; ajouter("coach", res.body.reply);
      }).catch(function(){ occupe = false; st.textContent = tr("e_err"); });
    }
    document.getElementById("co-send").addEventListener("click", function(){ envoyer(inp.value); });
    inp.addEventListener("keydown", function(e){
      if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); envoyer(inp.value); }
    });
    document.getElementById("co-rapides").addEventListener("click", function(e){
      var b = e.target.closest("button"); if (b) envoyer(b.textContent);
    });
    document.getElementById("co-erase").addEventListener("click", function(){
      if (!codeEl.value.trim()) { st.textContent = tr("need"); return; }
      poster({action: "delete"}).then(function(res){
        if (!res.ok) { st.textContent = erreur(res.body && res.body.error); return; }
        msgs.innerHTML = ""; st.textContent = tr("erased");
      }).catch(function(){ st.textContent = tr("e_err"); });
    });
    new MutationObserver(appliquer).observe(document.documentElement, {attributes:true, attributeFilter:["lang"]});
  })();
</script>

<script>
  // ------------------------------------------------- la repetition filmee
  // ⚠️ RIEN NE SORT DU TELEPHONE. L'enregistrement vit dans un Blob local ;
  // aucune ligne ici n'appelle le reseau. tools/verif_camera.py le controle.
  (function () {
    var EXO = {}, courant = "exp", flux = null, rec = null, morceaux = [], url = null;
    var v = document.getElementById("cam-video");
    var st = document.getElementById("cam-st");
    var bGo = document.getElementById("cam-go"), bRec = document.getElementById("cam-rec");
    var bStop = document.getElementById("cam-stop"), bDel = document.getElementById("cam-del");
    if (!v) return;
    function esc(x){ return String(x).replace(/[&<>"]/g, function(c){ return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]; }); }

    window.__camExos = function (liste) { EXO = {}; liste.forEach(function (e) { EXO[e[0]] = e; }); peindre(liste); };
    function peindre(liste) {
      document.getElementById("cam-ex").innerHTML = liste.map(function (e) {
        return '<button type="button" data-ex="' + esc(e[0]) + '" aria-pressed="' + (e[0] === courant ? "true" : "false") + '">' + esc(e[1]) + "</button>";
      }).join("");
      consigne();
    }
    function consigne() {
      var e = EXO[courant]; if (!e) return;
      document.getElementById("cam-consigne").innerHTML = '<span class="en">' + esc(e[2]) + '</span><span class="loc">' + esc(e[3]) + "</span>";
      document.getElementById("cam-liste").innerHTML = e[4].map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("");
    }
    document.getElementById("cam-ex").addEventListener("click", function (ev) {
      var b = ev.target.closest("button[data-ex]"); if (!b) return;
      courant = b.dataset.ex;
      [].slice.call(this.querySelectorAll("button")).forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      consigne();
    });
    function nettoyer() { if (url) { URL.revokeObjectURL(url); url = null; } }
    // ⚠️ LA CAMERA PEUT ETRE INTERDITE PAR LE SITE, pas par le visiteur : l'en-tete
    // Permissions-Policy de driver360 disait camera=() (releve le 15/09/2026). Dans ce
    // cas, le message « autorisez-la dans votre navigateur » serait faux — rien dans
    // ses reglages ne peut la rendre. On le detecte et on dit la verite.
    function interdite() {
      var fp = document.permissionsPolicy || document.featurePolicy;
      return !!(fp && fp.allowsFeature && !fp.allowsFeature("camera"));
    }
    if (interdite()) { bGo.style.display = "none"; st.dataset.k = "cam_off"; st.textContent = tr("cam_off"); }
    bGo.addEventListener("click", function () {
      if (!navigator.mediaDevices || !window.MediaRecorder) { st.textContent = tr("cam_no"); return; }
      navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" }, audio: true })
        .then(function (f) {
          flux = f; v.srcObject = f; v.muted = true; v.controls = false; v.play();
          bGo.style.display = "none"; bRec.style.display = ""; st.textContent = "";
        })
        .catch(function () { st.textContent = tr("cam_deny"); });
    });
    bRec.addEventListener("click", function () {
      nettoyer(); morceaux = [];
      try { rec = new MediaRecorder(flux); } catch (e) { st.textContent = tr("cam_no"); return; }
      rec.ondataavailable = function (e) { if (e.data && e.data.size) morceaux.push(e.data); };
      rec.onstop = function () {
        var b = new Blob(morceaux, { type: morceaux[0] ? morceaux[0].type : "video/webm" });
        url = URL.createObjectURL(b);
        v.srcObject = null; v.src = url; v.muted = false; v.controls = true; v.loop = true; v.play();
        bStop.style.display = "none"; bRec.style.display = ""; bDel.style.display = "";
        st.textContent = tr("cam_done");
      };
      rec.start();
      bRec.style.display = "none"; bStop.style.display = ""; bDel.style.display = "none";
      st.textContent = tr("cam_run");
    });
    bStop.addEventListener("click", function () { if (rec && rec.state !== "inactive") rec.stop(); });
    bDel.addEventListener("click", function () {
      nettoyer(); v.src = ""; v.controls = false;
      if (flux) { v.srcObject = flux; v.muted = true; v.play(); }
      bDel.style.display = "none"; st.textContent = "";
    });
    // On coupe la camera en quittant : une diode qui reste allumee est une
    // promesse trahie, meme si rien n'est enregistre.
    window.addEventListener("pagehide", function () {
      nettoyer();
      if (flux) flux.getTracks().forEach(function (t) { t.stop(); });
    });
  })();
  appliquer();
</script>
</body>
</html>
"""


def dictionnaire():
    out = {}
    for i, lg in ((0, "en"), (1, "fr"), (2, "ht"), (3, "es")):
        d = {k: v[i] for k, v in TX.items()}
        d["exos"] = EXOS[lg]
        out[lg] = d
    return out


def ecrire():
    if not portee.dsp():
        print("wout.html : perimetre « %s » — la page reste derivee du coach de route" % portee.PORTEE)
        return None
    champs = {k: v[0] for k, v in TX.items()}
    champs.update(css=CSS, entete=entete("wout.html"), pied=PIED, ep=EP,
                  dico=json.dumps(dictionnaire(), ensure_ascii=False, indent=1),
                  exos_en=json.dumps(EXOS["en"], ensure_ascii=False))
    champs["descr"] = champs["descr"].replace('"', "&quot;")
    html = PAGE % champs
    chemin = os.path.join(RACINE, "wout.html")
    io.open(chemin + ".tmp", "w", encoding="utf-8", newline="\n").write(html)
    os.replace(chemin + ".tmp", chemin)
    print("wout.html ecrit : coach carriere DSP, %d textes x 4 langues, %d octets" % (len(TX), len(html)))
    return chemin


if __name__ == "__main__":
    ecrire()
