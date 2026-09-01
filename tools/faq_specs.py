# -*- coding: utf-8 -*-
"""Les questions-réponses des deux coachs, dans les quatre langues.

⚠️ CHAQUE RÉPONSE EST SOURCÉE. Manuel du conducteur du Massachusetts (rév.
2/2018) et formulaire officiel du certificat 7D (checklist + T21038-0516), les
deux téléchargés et lus. Aucune réponse ne dit un chiffre que ces documents
ne donnent pas.

POURQUOI CE FICHIER PLUTÔT QU'UN BALISAGE SEUL. Google demande que le contenu
d'un `FAQPage` soit **visible par le visiteur**. Un balisage qui décrit des
questions absentes de la page est un faux, et c'est la première chose qu'un
moteur sanctionne. On écrit donc la FAQ pour les gens, et le balisage se
déduit d'elle — jamais l'inverse.

⚠️ LA DERNIÈRE QUESTION DU 7D NE RÉPOND PAS, et c'est délibéré. Sur le statut
migratoire, deux faits sont établis et un troisième ne l'est pas ; pour un
public majoritairement immigré, se tromper décourage quelqu'un d'éligible ou
lui fait dépenser 15 $ et une visite médicale pour rien. On donne les deux
faits et le numéro qui tranche.
"""

# (identifiant, {langue: (question, réponse)})
WOUT = [
 ("q1", {
  "en": ("Can I bring an interpreter to the road test?",
         "Not as a right. The manual says an interpreter “may also be allowed” <strong>if the examiner so authorizes</strong>. Ask when you book your test, and do not assume — drill the English commands daily so you are not depending on it."),
  "fr": ("Puis-je amener un interprète au test de conduite ?",
         "Pas de plein droit. Le manuel dit qu'un interprète « peut être admis » <strong>si l'examinateur l'autorise</strong>. Demandez-le en réservant, et ne le supposez pas — travaillez les commandes anglaises tous les jours pour ne pas en dépendre."),
  "ht": ("Ès ke m ka vini ak yon entèprèt nan tès kondwi a ?",
         "Se pa yon dwa. Manyèl la di yon entèprèt « ka aksepte » <strong>si egzaminatè a otorize l</strong>. Mande sa lè w ap pran randevou, epi pa sipoze l — travay kòmand angle yo chak jou pou w pa depann de li."),
  "es": ("¿Puedo llevar un intérprete al examen de manejo?",
         "No como derecho. El manual dice que un intérprete « puede ser admitido » <strong>si el examinador lo autoriza</strong>. Pregúntalo al reservar, y no lo des por hecho — practica las órdenes en inglés a diario para no depender de él."),
 }),
 ("q2", {
  "en": ("Who can be my sponsor?",
         "Someone 21 or over, with at least one year of driving experience, holding a valid licence from their own US state. <strong>A foreign licence is not eligible</strong> — the manual is explicit. Without a sponsor you are not given a Class D road test."),
  "fr": ("Qui peut être mon accompagnateur ?",
         "Quelqu'un de 21 ans ou plus, avec au moins un an d'expérience, titulaire d'un permis valide de son propre État américain. <strong>Un permis étranger n'est pas accepté</strong> — le manuel est explicite. Sans accompagnateur, on ne vous fait pas passer le test Class D."),
  "ht": ("Kilès ki ka akonpaye m ?",
         "Yon moun 21 an oswa plis, ak omwen yon ane eksperyans, ki gen yon pèmi valid nan pwòp Eta ameriken li. <strong>Yon pèmi etranje pa aksepte</strong> — manyèl la di l klè. San akonpayatè, yo p ap fè w pase tès Class D a."),
  "es": ("¿Quién puede ser mi acompañante?",
         "Alguien de 21 años o más, con al menos un año de experiencia y licencia válida de su propio estado. <strong>Una licencia extranjera no sirve</strong> — el manual es explícito. Sin acompañante no te hacen el examen Class D."),
 }),
 ("q3", {
  "en": ("What can stop the test before it even starts?",
         "Arriving late. An incomplete road-test application, or no parental consent if you are under 18. A vehicle the examiner rejects: parking brake not reachable, a “donut” spare tire, a repair plate, or driver aids that cannot be turned off. Children or pets in the car — service animals are allowed."),
  "fr": ("Qu'est-ce qui peut arrêter le test avant même qu'il commence ?",
         "Arriver en retard. Une demande de test incomplète, ou l'absence d'autorisation parentale si vous avez moins de 18 ans. Un véhicule refusé par l'examinateur : frein à main inaccessible, roue galette, plaque « repair », ou aides à la conduite qu'on ne peut pas désactiver. Des enfants ou des animaux dans la voiture — les chiens d'assistance sont admis."),
  "ht": ("Kisa ki ka kanpe tès la anvan menm li kòmanse ?",
         "Rive an reta. Yon demann tès ki pa konplè, oswa san otorizasyon paran si w anba 18 an. Yon machin egzaminatè a refize : fren a men ki pa aksesib, yon kawotchou ti galèt, yon plak « repair », oswa èd kondwit ou pa ka dezaktive. Timoun oswa bèt nan machin nan — chen asistans aksepte."),
  "es": ("¿Qué puede parar el examen antes de empezar?",
         "Llegar tarde. Una solicitud incompleta, o sin consentimiento parental si eres menor de 18. Un vehículo que el examinador rechaza: freno de mano inaccesible, rueda de galleta, placa « repair », o ayudas a la conducción que no se pueden desactivar. Niños o mascotas en el coche — los animales de servicio sí."),
 }),
 ("q4", {
  "en": ("How many times can I take the road test?",
         "No more than <strong>six in a 12-month period</strong> for a Class D licence. The $35 fee is charged again if you fail, are unprepared, are refused over the vehicle, come without a sponsor, are late or absent, or cancel with less than 72 hours notice."),
  "fr": ("Combien de fois puis-je passer le test de conduite ?",
         "Pas plus de <strong>six fois sur 12 mois</strong> pour un permis Class D. Les 35 $ sont redus si vous échouez, êtes mal préparé, êtes refusé pour le véhicule, venez sans accompagnateur, arrivez en retard ou pas du tout, ou annulez à moins de 72 heures."),
  "ht": ("Konbien fwa m ka pase tès kondwi a ?",
         "Pa plis pase <strong>sis fwa nan 12 mwa</strong> pou yon pèmi Class D. 35 $ yo peye ankò si w echwe, si w pa prepare, si yo refize machin nan, si w vini san akonpayatè, si w an reta oswa ou pa vini, oswa si w anile a mwens pase 72 è."),
  "es": ("¿Cuántas veces puedo presentar el examen?",
         "No más de <strong>seis en 12 meses</strong> para una licencia Class D. Los $35 se cobran otra vez si suspendes, no estás preparado, te rechazan el vehículo, vienes sin acompañante, llegas tarde o no vienes, o cancelas con menos de 72 horas."),
 }),
 ("q5", {
  "en": ("Does Driver Coach guarantee I will pass?",
         "No. It is independent preparation and it is <strong>not affiliated with the RMV</strong>. The RMV publishes no scoring sheet, so nobody can tell you exactly what the examiner counts — our fault grid is ours, and we say so on every screen where it appears."),
  "fr": ("Driver Coach garantit-il que je vais réussir ?",
         "Non. C'est une préparation indépendante, <strong>non affiliée au RMV</strong>. Le RMV ne publie aucun barème : personne ne peut vous dire exactement ce que compte l'examinateur — notre grille de fautes est la nôtre, et nous l'écrivons partout où elle apparaît."),
  "ht": ("Ès ke Driver Coach garanti m ap pase ?",
         "Non. Se yon preparasyon endepandan, <strong>li pa afilye ak RMV la</strong>. RMV la pa pibliye okenn barèm : pèsòn pa ka di w egzakteman sa egzaminatè a konte — gril erè pa nou an se pa nou, epi nou di sa tout kote li parèt."),
  "es": ("¿Driver Coach garantiza que voy a aprobar?",
         "No. Es una preparación independiente y <strong>no está afiliada al RMV</strong>. El RMV no publica ningún baremo: nadie puede decirte exactamente qué cuenta el examinador — nuestra tabla de faltas es nuestra, y lo decimos en cada pantalla donde aparece."),
 }),
]

SETD = [
 ("q1", {
  "en": ("What does the RMV ask for a 7D certificate?",
         "Be 21 or over, hold a Class A, B, C or D licence for <strong>3 continuous years</strong>, pass a CORI and a SORI check, pass an eye exam and a physical exam, complete <strong>2 hours</strong> of pre-service training with your employer — and only then the written exam."),
  "fr": ("Que demande le RMV pour un certificat 7D ?",
         "Avoir 21 ans ou plus, détenir un permis Class A, B, C ou D depuis <strong>3 ans sans interruption</strong>, passer un contrôle CORI et un contrôle SORI, un examen de la vue et un examen physique, suivre <strong>2 heures</strong> de formation préalable chez votre employeur — et l'examen écrit seulement ensuite."),
  "ht": ("Kisa RMV la mande pou yon sètifika 7D ?",
         "Gen 21 an oswa plis, gen yon pèmi Class A, B, C oswa D depi <strong>3 ane san kanpe</strong>, pase yon kontòl CORI ak yon kontòl SORI, yon egzamen zye ak yon egzamen fizik, fè <strong>2 hèdtan</strong> fòmasyon lakay anplwayè w — epi se apre sa egzamen ekri a."),
  "es": ("¿Qué pide el RMV para un certificado 7D?",
         "Tener 21 años o más, licencia Class A, B, C o D durante <strong>3 años continuos</strong>, pasar un control CORI y uno SORI, un examen de la vista y uno físico, hacer <strong>2 horas</strong> de formación previa con tu empleador — y solo después el examen escrito."),
 }),
 ("q2", {
  "en": ("How much does the 7D certificate cost, and how long does it last?",
         "<strong>$15.00</strong> for a one-year certificate. <strong>$7.50</strong> for six months, which applies if you are 70 or over, an insulin-dependent diabetic, or have had a hypoglycemic episode. A new CORI is required at every renewal."),
  "fr": ("Combien coûte le certificat 7D, et combien de temps dure-t-il ?",
         "<strong>15,00 $</strong> pour un certificat d'un an. <strong>7,50 $</strong> pour six mois, ce qui s'applique si vous avez 70 ans ou plus, êtes diabétique insulino-dépendant, ou avez eu un épisode hypoglycémique. Un nouveau CORI est exigé à chaque renouvellement."),
  "ht": ("Konbien sètifika 7D a koute, epi konbien tan li dire ?",
         "<strong>15,00 $</strong> pou yon sètifika yon ane. <strong>7,50 $</strong> pou sis mwa, sa aplike si w gen 70 an oswa plis, si w dyabèt ensilin-depandan, oswa si w te gen yon epizòd ipoglisemi. Yo mande yon nouvo CORI chak fwa w renouvle."),
  "es": ("¿Cuánto cuesta el certificado 7D y cuánto dura?",
         "<strong>$15.00</strong> por un certificado de un año. <strong>$7.50</strong> por seis meses, lo que aplica si tienes 70 años o más, eres diabético insulinodependiente, o has tenido un episodio hipoglucémico. Se exige un nuevo CORI en cada renovación."),
 }),
 ("q3", {
  "en": ("Who can complete the medical form?",
         "A <strong>medical doctor (MD or DO) licensed in Massachusetts</strong>. The form says it plainly: a nurse practitioner or a physician assistant is <strong>not accepted</strong>. The exam must be dated within <strong>90 days</strong> of your application, so do not have it done too early."),
  "fr": ("Qui peut remplir le formulaire médical ?",
         "Un <strong>médecin (MD ou DO) licencié au Massachusetts</strong>. Le formulaire le dit tel quel : un infirmier praticien ou un assistant médical n'est <strong>pas accepté</strong>. L'examen doit dater de moins de <strong>90 jours</strong> au moment de la demande — ne le faites donc pas trop tôt."),
  "ht": ("Kilès ki ka ranpli fòm medikal la ?",
         "Yon <strong>doktè (MD oswa DO) ki gen lisans nan Massachusetts</strong>. Fòm nan di l klè : yon enfimyè pratisyen oswa yon asistan medikal <strong>pa aksepte</strong>. Egzamen an dwe gen mwens pase <strong>90 jou</strong> lè w ap fè demann nan — donk pa fè l twò bonè."),
  "es": ("¿Quién puede completar el formulario médico?",
         "Un <strong>médico (MD o DO) con licencia en Massachusetts</strong>. El formulario lo dice así: un enfermero practicante o un asistente médico <strong>no se acepta</strong>. El examen debe tener menos de <strong>90 días</strong> al presentar la solicitud — no te lo hagas demasiado pronto."),
 }),
 ("q4", {
  "en": ("Do I need an employer before I apply?",
         "Yes. The transportation company must appear on the application — name, address, phone and e-mail — and you must already work there or expect to. The 2 hours of pre-service training happen with that employer. You do not get a 7D certificate “just to have it”."),
  "fr": ("Faut-il un employeur avant de faire la demande ?",
         "Oui. L'entreprise de transport doit figurer sur la demande — nom, adresse, téléphone et courriel — et vous devez déjà y travailler ou être sur le point d'y entrer. Les 2 heures de formation préalable se font chez cet employeur. On ne prend pas un 7D « pour l'avoir »."),
  "ht": ("Ès mwen bezwen yon anplwayè anvan m fè demann nan ?",
         "Wi. Konpayi transpò a dwe parèt sou demann nan — non, adès, telefòn ak imel — epi fòk ou deja ap travay la oswa ou pral travay la. 2 hèdtan fòmasyon an fèt lakay anplwayè sa a. Ou pa pran yon 7D « jis pou genyen l »."),
  "es": ("¿Necesito un empleador antes de solicitarlo?",
         "Sí. La empresa de transporte debe figurar en la solicitud — nombre, dirección, teléfono y correo — y debes trabajar ya allí o estar a punto. Las 2 horas de formación previa se hacen con ese empleador. No se saca un 7D « por tenerlo »."),
 }),
 ("q5", {
  "en": ("Does my immigration status matter for the 7D?",
         "Two things are certain and one is not. Since 1 July 2023 the Work and Family Mobility Act lets Massachusetts residents obtain a Standard Class D licence regardless of immigration status, and the RMV's own 7D checklist lists <strong>no</strong> proof-of-lawful-presence document. We have <strong>not</strong> been able to confirm whether the 7D certificate itself adds one — so ask before you spend anything: RMV Vehicle Safety &amp; Compliance Services, <strong>857-368-8130</strong>."),
  "fr": ("Mon statut migratoire compte-t-il pour le 7D ?",
         "Deux choses sont sûres et une ne l'est pas. Depuis le 1<sup>er</sup> juillet 2023, le Work and Family Mobility Act permet aux résidents du Massachusetts d'obtenir un permis Class D standard quel que soit leur statut, et la liste officielle du 7D ne mentionne <strong>aucun</strong> document de présence légale. Nous n'avons <strong>pas</strong> pu confirmer si le certificat 7D en ajoute un — demandez-le avant de dépenser quoi que ce soit : RMV Vehicle Safety &amp; Compliance Services, <strong>857-368-8130</strong>."),
  "ht": ("Ès estati imigrasyon m konte pou 7D a ?",
         "De bagay siè epi youn pa si. Depi 1<sup>e</sup> jiyè 2023, Work and Family Mobility Act la pèmèt rezidan Massachusetts jwenn yon pèmi Class D estanda kèlkeswa estati yo, epi lis ofisyèl 7D a pa mansyone <strong>okenn</strong> dokiman prezans legal. Nou <strong>pa</strong> rive konfime si sètifika 7D a ajoute youn — mande sa anvan w depanse anyen : RMV Vehicle Safety &amp; Compliance Services, <strong>857-368-8130</strong>."),
  "es": ("¿Importa mi estatus migratorio para el 7D?",
         "Dos cosas son seguras y una no. Desde el 1 de julio de 2023, la Work and Family Mobility Act permite a los residentes de Massachusetts obtener una licencia Class D estándar sea cual sea su estatus, y la lista oficial del 7D no menciona <strong>ningún</strong> documento de presencia legal. <strong>No</strong> hemos podido confirmar si el certificado 7D añade uno — pregúntalo antes de gastar nada: RMV Vehicle Safety &amp; Compliance Services, <strong>857-368-8130</strong>."),
 }),
]

TITRE = {
 "en": "Questions people actually ask",
 "fr": "Les questions qu'on nous pose vraiment",
 "ht": "Kesyon moun poze nou tout bon",
 "es": "Las preguntas que de verdad nos hacen",
}


def bloc(entrees, langue):
    """Le HTML visible : des <details>, un par question."""
    out = ["<h2 style=\"font-size:1.15rem;margin:0 0 0.6rem\">%s</h2>" % TITRE[langue]]
    for _id, tr in entrees:
        q, r = tr[langue]
        out.append(
            "<details class=\"faq-q\"><summary>%s</summary>"
            "<div class=\"faq-r\">%s</div></details>" % (q, r))
    return "".join(out)
