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

CE QUE LE COACH FAIT — et c'est la présentation à Ryan qui le définit
  1. mettre l'expérience en mots (postes, dates, véhicules, formations) ;
  2. préparer un nouveau DSP ;
  3. une pause, et le retour ;
  4. l'étape suivante (référent, formateur, répartition, certification DOT) ;
  5. répéter devant la caméra — un miroir, pas un jury.

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
 "ti": ("Driver Coach — your career as a DSP delivery driver | Driver360",
        "Driver Coach — votre carrière de chauffeur livreur DSP | Driver360",
        "Driver Coach — karyè w kòm chofè livrezon DSP | Driver360",
        "Driver Coach — tu carrera como conductor de reparto DSP | Driver360"),
 "descr": ("A career coach for delivery drivers at Amazon's Delivery Service Partners in Massachusetts: put your experience into words, prepare for a new DSP or a return after a break, and think through your next step. Independent — not affiliated with Amazon.",
           "Un coach de carrière pour les chauffeurs livreurs des partenaires de livraison d'Amazon au Massachusetts : mettre son expérience en mots, préparer un nouveau DSP ou un retour après une pause, réfléchir à l'étape suivante. Indépendant — non affilié à Amazon.",
           "Yon coach karyè pou chofè livrezon patnè livrezon Amazon yo nan Massachusetts : mete eksperyans ou an mo, prepare yon nouvo DSP oswa yon retou apre yon poz, reflechi sou pwochen etap la. Endepandan — pa afilye ak Amazon.",
           "Un coach de carrera para conductores de reparto de los socios de entrega de Amazon en Massachusetts: poner tu experiencia en palabras, prepararte para un nuevo DSP o para volver tras una pausa, y pensar tu siguiente paso. Independiente — sin afiliación con Amazon."),
 "fil": ("For delivery drivers at Amazon's Delivery Service Partners",
         "Pour les chauffeurs livreurs des partenaires de livraison d'Amazon",
         "Pou chofè livrezon patnè livrezon Amazon yo",
         "Para conductores de reparto de los socios de entrega de Amazon"),
 "lead": ("A delivery job is a start. This coach helps you turn it into a career that lasts longer than one DSP — in your language, at your pace.",
          "Un emploi de livreur, c'est un début. Ce coach vous aide à en faire une carrière qui dure plus longtemps qu'un seul DSP — dans votre langue, à votre rythme.",
          'Yon travay livrezon se yon kòmansman. Coach sa a ede w fè l tounen yon karyè ki dire pi lontan pase yon sèl DSP — nan lang pa w, san prese.',
          "Un empleo de repartidor es un comienzo. Este coach te ayuda a convertirlo en una carrera que dure más que un solo DSP — en tu idioma, a tu ritmo."),
 "indep": ("Driver360 is independent. It is not affiliated with Amazon, and Amazon does not endorse it.",
           "Driver360 est indépendant. Il n'est pas affilié à Amazon, et Amazon ne l'approuve pas.",
           "Driver360 endepandan. Li pa afilye ak Amazon, epi Amazon pa apwouve l.",
           "Driver360 es independiente. No está afiliado a Amazon, y Amazon no lo avala."),

 "c1_t": ("Your experience, in words", "Votre expérience, en mots", "Eksperyans ou, an mo", "Tu experiencia, en palabras"),
 "c1_d": ("Roles, dates, vehicles, the kinds of routes you ran, the training you finished — written plainly, in a form you can take to the next DSP.",
          "Postes, dates, véhicules, types de tournées, formations terminées — écrit simplement, sous une forme que vous emportez au prochain DSP.",
          "Pòs, dat, machin, kalite wout ou te fè, fòmasyon ou te fini — ekri senp, yon fason ou ka pote l bay pwochen DSP a.",
          "Puestos, fechas, vehículos, tipos de rutas, formación terminada — escrito con sencillez, de una forma que puedas llevar al próximo DSP."),
 "c2_t": ("A new DSP", "Un nouveau DSP", "Yon nouvo DSP", "Un nuevo DSP"),
 "c2_d": ("What to ask before you accept — pay, hours, days, station, commute, paid training — and what a first week is likely to look like.",
          "Ce qu'il faut demander avant d'accepter — salaire, heures, jours, station, trajet, formation payée — et à quoi ressemble souvent une première semaine.",
          "Kisa pou w mande anvan w aksepte — salè, èdtan, jou, estasyon, trajè, fòmasyon ki peye — ak kijan yon premye semèn souvan pase.",
          "Qué preguntar antes de aceptar — pago, horas, días, estación, trayecto, formación pagada — y cómo suele ser una primera semana."),
 "c3_t": ("A break, and coming back", "Une pause, et le retour", "Yon poz, epi retou a", "Una pausa, y la vuelta"),
 "c3_d": ("What to keep while you are away, and how to come back without starting from zero. Only the DSP can say which checks or trainings start again — the coach helps you ask.",
          "Ce qu'il faut garder pendant votre absence, et comment revenir sans repartir de zéro. Seul le DSP peut dire quels contrôles ou formations sont à refaire — le coach vous aide à le demander.",
          "Kisa pou w kenbe pandan w pa la, ak kijan pou w retounen san w pa rekòmanse a zewo. Se sèlman DSP a ki ka di ki kontwòl oswa fòmasyon ki pou refèt — coach la ede w mande sa.",
          "Qué conservar mientras estás fuera, y cómo volver sin empezar de cero. Solo el DSP puede decir qué comprobaciones o formaciones se repiten — el coach te ayuda a preguntarlo."),
 "c4_t": ("Your next step", "L'étape suivante", "Pwochen etap ou", "Tu siguiente paso"),
 "c4_d": ("Lead driver, trainer, dispatch, a different vehicle, a DOT certification: what the role involves and how to ask for it. Amazon's own page for DSP drivers mentions advancement and DOT certification.",
          "Chauffeur référent, formateur, répartition, un autre véhicule, une certification DOT : ce que le poste demande et comment le demander. La page d'Amazon pour les chauffeurs DSP mentionne elle-même l'évolution et la certification DOT.",
          "Chofè lidè, fòmatè, dispatch, yon lòt machin, yon sètifikasyon DOT : sa pòs la mande ak kijan pou w mande l. Paj Amazon an pou chofè DSP yo li menm pale de monte ak sètifikasyon DOT.",
          "Conductor líder, formador, despacho, otro vehículo, una certificación DOT: qué exige el puesto y cómo pedirlo. La propia página de Amazon para conductores DSP menciona el ascenso y la certificación DOT."),

 "h_t": ("What this coach is, and is not", "Ce qu'est ce coach, et ce qu'il n'est pas",
         "Sa coach sa a ye, ak sa li pa ye", "Lo que es este coach, y lo que no es"),
 "h_d": ("It helps you think, write and rehearse. It does <strong>not</strong> store a professional record or send anything to a DSP — that part is not built yet. What you write together is yours to copy and keep. It will never give you a score, and it will never invent a pay rate or a requirement: when it does not know, it tells you to ask the DSP.",
         "Il vous aide à réfléchir, écrire et répéter. Il ne conserve <strong>pas</strong> de dossier professionnel et n'envoie rien à aucun DSP — cette partie n'est pas encore construite. Ce que vous écrivez ensemble vous appartient : copiez-le et gardez-le. Il ne vous donnera jamais de note, et il n'inventera jamais un salaire ou une condition : quand il ne sait pas, il vous dit de demander au DSP.",
         "Li ede w reflechi, ekri epi repete. Li <strong>pa</strong> kenbe okenn dosye pwofesyonèl epi li pa voye anyen bay okenn DSP — pati sa a poko bati. Sa nou ekri ansanm se pou ou : kopye l epi kenbe l. Li p ap janm ba w yon nòt, epi li p ap janm envante yon salè oswa yon kondisyon : lè li pa konnen, li di w mande DSP a.",
         'Te ayuda a pensar, escribir y ensayar. <strong>No</strong> guarda un expediente profesional ni envía nada a ningún DSP — esa parte todavía no está construida. Lo que escribimos juntos es tuyo: cópialo y guárdalo. Nunca te pondrá una nota, y nunca se inventará un salario o un requisito: cuando no lo sabe, te dice que se lo preguntes al DSP.'),

 "code_l": ("Your coach code", "Votre code du coach", "Kòd coach ou", "Tu código del coach"),
 "code_s": ("Free (WOUT-XXXX-XXXX). No code yet? <a href='%s'>Request one — free</a>" % MAILTO_CODE,
            "Gratuit (WOUT-XXXX-XXXX). Pas encore de code ? <a href='%s'>Demandez-le — gratuit</a>" % MAILTO_CODE,
            "Gratis (WOUT-XXXX-XXXX). Ou poko gen kòd ? <a href='%s'>Mande l — gratis</a>" % MAILTO_CODE,
            "Gratis (WOUT-XXXX-XXXX). ¿Aún sin código? <a href='%s'>Pídelo — gratis</a>" % MAILTO_CODE),

 "chat_t": ("Talk to your coach", "Parler à votre coach", "Pale ak coach ou", "Habla con tu coach"),
 "hello": ("Hi — I'm your Driver Coach. We can work on your experience, a new DSP, a break, or your next step. Where would you like to start?",
           "Bonjour — je suis votre Driver Coach. Nous pouvons travailler votre expérience, un nouveau DSP, une pause, ou l'étape suivante. Par où voulez-vous commencer ?",
           "Bonjou — se mwen ki Driver Coach ou. Nou ka travay sou eksperyans ou, yon nouvo DSP, yon poz, oswa pwochen etap ou. Kote ou vle kòmanse ?",
           "Hola — soy tu Driver Coach. Podemos trabajar tu experiencia, un nuevo DSP, una pausa o tu siguiente paso. ¿Por dónde quieres empezar?"),
 "q1": ("Help me write down my experience", "Aidez-moi à écrire mon expérience", "Ede m ekri eksperyans mwen", "Ayúdame a escribir mi experiencia"),
 "q2": ("I'm starting at a new DSP — what should I ask?", "Je commence dans un nouveau DSP — que dois-je demander ?", "M ap kòmanse nan yon nouvo DSP — kisa pou m mande ?", "Empiezo en un nuevo DSP — ¿qué debo preguntar?"),
 "q3": ("I'm taking a break. What should I keep?", "Je fais une pause. Que dois-je garder ?", "M ap pran yon poz. Kisa pou m kenbe ?", "Me tomo una pausa. ¿Qué debo conservar?"),
 "q4": ("What could my next step be?", "Quelle pourrait être mon étape suivante ?", "Ki pwochen etap mwen ta ka ye ?", "¿Cuál podría ser mi siguiente paso?"),
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
        ["dur", "A hard day", "Describe a hard day on a route and what you did.", "No customer names or addresses — ever.",
         ["What happened", "What you did, following your DSP's rules", "What you would do the same way again"]]],
 "fr": [["exp", "60 secondes", "Présentez votre expérience à un DSP en 60 secondes.", "Postes, dates, véhicules — et une chose dont vous êtes fier.",
         ["Depuis combien de temps vous livrez, et où", "Les véhicules et les types de tournées que vous connaissez", "Une journée qui s'est bien passée grâce à vous"]],
        ["pause", "Une pause", "Expliquez une pause dans votre parcours.", "Simplement, sans vous excuser.",
         ["Que vous avez fait une pause, et à peu près quand", "Ce que vous avez fait pendant", "Pourquoi vous êtes prêt maintenant"]],
        ["dur", "Une journée difficile", "Racontez une journée difficile sur une tournée et ce que vous avez fait.", "Jamais de nom ni d'adresse de client.",
         ["Ce qui s'est passé", "Ce que vous avez fait, en suivant les règles de votre DSP", "Ce que vous referiez de la même façon"]]],
 "ht": [["exp", "60 segonn", "Prezante eksperyans ou bay yon DSP nan 60 segonn.", 'Pòs, dat, machin — ak yon bagay ki fè w fyè.',
         ["Depi konbyen tan w ap livre, ak ki kote", "Machin ak kalite wout ou konnen", "Yon jou ki te pase byen gras a ou"]],
        ["pause", "Yon poz", "Esplike yon poz nan pakou travay ou.", "Senp, san w pa mande eskiz.",
         ['Ou te pran yon poz, ak apeprè kilè', "Kisa w te fè pandan tan an", "Poukisa w pare kounye a"]],
        ["dur", "Yon jou difisil", "Rakonte yon jou difisil sou yon wout ak kisa w te fè.", 'Pa janm bay non oswa adrès yon kliyan.',
         ["Kisa ki te pase", "Kisa w te fè, dapre règ DSP ou", "Kisa w ta refè menm jan an"]]],
 "es": [["exp", "60 segundos", "Presenta tu experiencia a un DSP en 60 segundos.", "Puestos, fechas, vehículos — y algo de lo que estés orgulloso.",
         ["Cuánto tiempo llevas repartiendo, y dónde", "Los vehículos y tipos de rutas que conoces", "Un día que salió bien gracias a ti"]],
        ["pause", "Una pausa", "Explica una pausa en tu trayectoria.", "Con sencillez, sin disculparte.",
         ["Que te tomaste una pausa, y más o menos cuándo", "Qué hiciste durante ella", "Por qué estás listo ahora"]],
        ["dur", "Un día difícil", "Cuenta un día difícil en una ruta y qué hiciste.", "Nunca nombres ni direcciones de clientes.",
         ["Qué pasó", "Qué hiciste, siguiendo las reglas de tu DSP", "Qué volverías a hacer igual"]]],
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
