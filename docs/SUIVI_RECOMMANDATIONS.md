# Suivi des recommandations — Driver360

Ouvert le 30/08/2026, au terme d'une relecture adversariale du site entier par
huit agents indépendants : doctrine produit, langue et i18n, sécurité et
données personnelles, conformité légale, exactitude RMV/7D, accessibilité et
thème, chaîne de fabrication, parcours réel au navigateur.

## Comment lire ce registre

**« fait » veut dire qu'un contrôle a été exécuté**, pas qu'on s'en souvient.
Lancer `python tools/etat_suivi.py` AVANT de répondre à « où en est-on » : il
recalcule ce qui est recalculable et **sort en erreur si ce tableau ment**.

Les lignes marquées **humain** ne sont vérifiables par aucun programme — une
relecture en kreyòl, un avis d'avocat, un arbitrage éditorial. Elles resteront
ouvertes tant qu'une personne ne les aura pas fermées, et c'est normal.

Gravité : 🔴 **bloquant** — ne pas publier en l'état · 🟠 **à corriger** —
affaiblit sans disqualifier · 🔵 **à arbitrer** — une décision, pas un défaut.

L'état d'une ligne n'est jamais « à moitié » par confort : soit le contrôle
passe, soit il ne passe pas, soit il n'existe pas.

---

## A — Doctrine produit

| # | Recommandation | Gravité | État | Preuve |
|---|---|---|---|---|
| A1 | Retirer la promesse « nous publions votre offre » (jobs, index, terms) ou ajouter un champ `offres` à `emplois.py` **avant** de la promettre | 🔴 | **à faire** | `EMPLOYEURS` n'a que `genre/nom/url/zone/quoi` : aucun chemin entre le mailto de collecte et la page |
| A2 | Régénérer les 4 pages produit en anglais : `<html lang="en">`, et repli de langue à l'anglais (il est au français) | 🔴 | **à faire** | décision du 29/08 ; `verif_langue.py` ne contrôle ni `lang` ni le repli |
| A3 | Réparer les 12 liens vers `rejistre.html` (la page s'appelle `vivye.html`) et élargir `regen.py` + `verif_actifs.py` aux `href` échappés | 🔴 | **vérifié** | cause : `regen.py` ne reecrivait que `href="…"` en guillemets doubles ; ces 14 liens vivaient dans des chaines JS en apostrophes. Les **trois formes** sont desormais reecrites, et `verif_actifs.py` les regarde toutes. **Preuve par la panne** : un `href='rejistre.html'` reintroduit dans `wout.html` fait sortir le controle en 1 ; 0 lien interne mort apres restauration |
| A4 | Renommer « 7D Pro » → « Driver Coach 7D » dans `setdi.html` (jusqu'au `<h1>`) et la lier depuis `wout.html` | 🔴 | **à faire** | `grep -c "setdi.html" *.html` → 0 : la page n'est liée de nulle part |
| A5 | Éliminer les restes « Chofè360 », « coach Wout », « 7D Pro », « pool Driver360 » des sujets de mailto et des dictionnaires | 🔴 | **à faire** | les sujets s'affichent dans le client mail du visiteur |
| A6 | Supprimer la phrase dupliquée d'`anplwaye.html:170` (guillemets `\"` littéraux dans du HTML) | 🔴 | **à faire** | le lien de vente des packs de codes tombe en 404 ; défaut propre à la version FR |
| A7 | « Checking eight pages every week » → 20 employeurs, dans les 4 langues | 🟠 | **à faire** | `grep -c "genre=" tools/emplois.py` → 20 |
| A8 | Corriger le README : 8 vs 20 employeurs, `noreferrer` annoncé mais absent, offre « nous publions » non documentée | 🟠 | **à faire** | le README se contredit lui-même (l. 82/86 contre l. 142) |
| A9 | Trancher la doctrine des salaires : `emplois.py` règle 3 les autorise datés, la consigne de relecture les interdit | 🔵 | **à arbitrer — humain** | deux textes maison s'opposent ; l'un doit être retiré |
| A10 | Dire sur `vivye.html` que l'envoi WhatsApp est manuel | 🟠 | **à faire** | `jobs.html` et `privacy.html` le disent ; la page où l'on coche, non |
| A11 | `jobs.html` : ramener à un appel à l'action et sortir le bloc employeur de la page des chauffeurs | 🟠 | **à faire** | 4 boutons + bifurcation rompue |
| A12 | « unlocks all 20 » (EN/ES) → le quiz annonce 25 et la banque en compte 28 | 🟠 | **à faire** | faux dans la langue de la cible |
| A13 | Trancher 90 j (`wout`) contre 92 j (`setdi`) pour le même Driver Coach, et l'écrire dans les CGU | 🟠 | **à faire** | `terms.html` ne dit ni l'un ni l'autre |
| A14 | Traduire les corps de mailto, aujourd'hui en français sur un site anglais | 🟠 | **à faire** | `jobs.html:244`, `:265`, `anplwaye.html:84` — au point exact de la conversion |

## B — Langue et internationalisation

| # | Recommandation | Gravité | État | Preuve |
|---|---|---|---|---|
| B1 | Retirer le voile `i18n-wait` du `setTimeout` et l'ôter à la fin d'`applyLang()` | 🔴 | **à faire** | mesuré : page blanche 1,5 s pour tout non-francophone sur 4 pages, alors que la traduction est finie à 275 ms |
| B2 | Brancher les 14 chaînes françaises en dur du tableau de bord employeur, et faire repeindre `render()` par `applyLang()` | 🔴 | **à faire** | 2 des clés existent déjà dans les 4 langues, posées correctement 2 lignes plus haut |
| B3 | Traduire `<meta name="description">` sur `vivye`, `wout`, `setdi` (modèle : `anplwaye.html:656`) | 🔴 | **à faire** | `wout.html` en ligne : page `lang="ht"`, description française annonçant « les communautés créole et hispanophone » |
| B4 | Pointer `verif_ids_traduits.py` sur ce dépôt (il lit `Atmart_website`) | 🟠 | **à faire** | l'étape 9 du build ne prouve rien sur le site publié |
| B5 | Traduire les 2 `confirm()` bilingues ht/fr d'une action destructive | 🟠 | **à faire** | `wout.html:707`, `setdi.html:317` ; `vivye.html:607` montre le bon modèle |
| B6 | Traduire `404.html` et l'ajouter à `PAGES` de `verif_langue.py` | 🟠 | **à faire** | kreyòl seul, sans sélecteur de langue, hors de tout contrôle |
| B7 | Traduire `aria-label="Language"` / `"Menu"` et ajouter `lang` au manifeste | 🟠 | **à faire** | l'app installée s'appelle en anglais pour tout le monde |
| B8 | Sortir l'espace avant deux-points du français : il est appliqué aux 4 langues | 🟠 | **à faire** | `regen.py:158`, `gen_legal.py:68` → « Last updated : » |
| B9 | Trancher la convention d'espace insécable en kreyòl (75 dans les dictionnaires, 0 dans `komand.json`) | 🔵 | **à arbitrer — humain** | les deux sources s'affichent dans le même écran |
| B10 | Relecture kreyòl : 12 fautes ou calques relevés, dont 5 où le site se contredit lui-même | 🔵 | **à faire — humain** | `angle`/`anglè` (11×), `Fok`/`Fòk`, `remet`/`remèt`, `kòmand`/`kòmandman` |
| B11 | Unifier le nom du produit : vivier/pool, vivye/pool, registro/pool changent selon la page dans les 3 langues | 🟠 | **à faire** | la coupure suit la frontière de fabrication ; `vivye.html` mélange les deux dans un seul dictionnaire |
| B12 | Transmettre `document.documentElement.lang` dans `profile()` | 🟠 | **à faire** | l'alerte WhatsApp redevine la langue et rate « panyòl », le mot que le site donne en exemple |
| B13 | Supprimer les 6 valeurs mortes `contact`/`droits` de `jobs.html` | 🟠 | **à faire** | résidu du mécanisme à trois couches qui a produit le bug d'origine |

## C — Sécurité et données personnelles

| # | Recommandation | Gravité | État | Preuve |
|---|---|---|---|---|
| C1 | `esc(e.city)` aux lignes 345 et 360 d'`anplwaye.html` — XSS stocké | 🔴 | **vérifié** | corrigé dans `anplwaye360.html` (2 insertions de `e.city`, lignes 359 et 382 de la source). **Prouvé au navigateur** : réponse serveur truquée avec `<img src=x onerror=…>` en ville → 0 image injectée, code non exécuté, ville rendue en texte |
| C2 | Retirer `auth` de la réponse `list` du Worker et la colonne de la vue libre | 🔴 | **à faire** | pastille ✅/⏳/❌ triable sur fiches anonymes — le site pose lui-même cette règle pour la nationalité |
| C3 | Porter `esc()` dans `vivye.html` et l'appliquer à `d.org`, `d.emp`, `d.at` | 🔴 | **vérifié** | `esc()` **créé** dans `rejistre.html` (il n'en avait aucune) et appliqué à `d.org`, `d.emp`, `d.at` — dont **deux attributs** `data-emp`, la variante la plus facile à rater. Prouvé au navigateur par le même essai, dans l'autre sens |
| C4 | `anplwaye.html:380` : `enAttente(b.dataset.id)` au lieu de `enAttente(id)` | 🔴 | **à faire** | `ReferenceError` en mode strict : le bouton « Sélectionner » ne fonctionne pas, et le chemin d'accord préalable n'a jamais tourné |
| C5 | Sortir les blocs `<script>` inline pour lever `'unsafe-inline'` | 🟠 | **à faire** | aucun filet sous C1 et C3 |
| C6 | Passer le code employeur en `sessionStorage` et purger à l'expiration | 🟠 | **à faire** | code à 15 $ la sélection, en clair, copiable d'un navigateur à l'autre |
| C7 | Passer les HTML du service worker en *network-first* et bumper `CACHE` | 🟠 | **à faire** | cache-first sans revalidation ; `CACHE` non bumpé depuis `c0acd86` alors que `09bc6d3` a touché `wout.html` |
| C8 | Passer le code chauffeur en fragment `#c=` | 🟠 | **à faire** | `?c=` atterrit dans le Cache Storage et dans l'historique |
| C9 | Exiger un clic avant de republier la fiche à l'ouverture d'un lien `?c=` | 🟠 | **à faire** | un aperçu de lien WhatsApp suffit à rafraîchir `lastSeen` |
| C10 | Compter les tentatives sur le code employeur (`codeEchec` existe déjà) | 🟠 | **à faire** | `worker.js:4180` renvoie `emp_invalid` sans frein ; la route chauffeur, elle, freine |
| C11 | Supprimer `code.txt` et l'ajouter au `.gitignore` | 🟠 | **à faire** | vide depuis le premier jour (aucune fuite), mais servi publiquement |
| C12 | `try/finally` ou `tempfile` dans `alertes_whatsapp.py:114` | 🟠 | **à faire** | fiche complète en clair dans `%TEMP%`, chemin fixe, laissée sur place si `wrangler()` lève |
| C13 | Obfusquer ou retirer les 10 `mailto:` personnels de `setdi.html:183` | 🟠 | **à faire** | téléphones et adresses personnelles sur une page indexée |
| C14 | Corriger le README : la nationalité EST collectée et affichée après sélection, et la validation du lien de CV n'existe PAS côté page | 🟠 | **à faire** | `privacy.html:125` est exact ; c'est le README qui déborde — voir H1 |
| C15 | Poser `Permissions-Policy` dans Cloudflare | 🟠 | **à faire — humain** | confirmé absent en ligne ; les 4 autres en-têtes sont bien là |
| C16 | Horodater le consentement au vivier comme le consentement WhatsApp (`optinAt`) | 🟠 | **à faire** | `optin: true` est écrit en dur côté Worker ; `fill()` recoche d'office |
| C17 | Vérifier l'entropie des codes `EMP-` (posés à la main dans le KV) | 🔵 | **à vérifier — humain** | décide si l'absence de frein (C10) est un détail ou une porte |

## D — Conformité légale

| # | Recommandation | Gravité | État | Preuve |
|---|---|---|---|---|
| D1 | Mettre `terms.html` et `privacy.html` dans le pied partagé (`regen.py:155`) et au-dessus des boutons d'envoi | 🔴 | **à faire** | seul `index.html` y renvoie : aucune page qui collecte ne les montre |
| D2 | Aligner `privacy.html:77` sur ce que l'employeur voit vraiment (7 données de plus) | 🔴 | **à faire** | résultats d'examen, préparation %, meilleur score, date de test, drapeau CV — la page se réclame pourtant d'une exactitude littérale |
| D3 | Case distincte, décochée par défaut, pour la publication des résultats d'examen | 🔴 | **à faire** | les cases actuelles ne parlent que de nom et téléphone |
| D4 | Retirer « Atmart LLC. Massachusetts. » du pied des 8 pages, ou immatriculer la LLC | 🔴 | **à faire** | `legal_specs.py:14` dit qu'elle n'y est PAS établie ; `terms.html:95` et `:102` se contredisent à 7 lignes |
| D5 | Ajouter aux CGU : droit applicable et for, langue faisant foi, exclusion de garanties, limitation de responsabilité | 🔴 | **à faire** | un contrat en 4 langues sans clause de langue engage dans les quatre |
| D6 | *(même défaut que C2, vu du côté légal)* retirer le statut d'autorisation de la vue libre | 🔴 | **à faire** | 8 U.S.C. § 1324b ; le vivier accepte et publie des « pas encore » |
| D7 | Compléter la case WhatsApp : identité de l'expéditeur, non-conditionnalité, frais | 🟠 | **à faire** | fréquence et STOP y sont déjà ; à corriger AVANT l'ouverture du compte Platform |
| D8 | Rendre le STOP praticable : `--stop` par numéro de téléphone, pas seulement par code | 🟠 | **à faire** | un STOP arrive avec un numéro ; `--liste` n'affiche pas les numéros |
| D9 | Clause FCRA : Driver360 n'est pas une agence d'évaluation, ses informations ne sont pas un *consumer report* | 🟠 | **à faire** | les résultats RMV sont d'origine tierce, hors de l'exception « transactions et expériences » |
| D10 | Écrire la fin d'accès : reconduction, résiliation, remboursement, sort des contacts déjà révélés | 🟠 | **à faire** | le README l'admet ; les CGU décrivent un produit payant qui n'existe pas encore sous cette forme |
| D11 | Poser un âge minimum et le traitement des 16-17 ans | 🟠 | **à faire** | 0 occurrence d'âge, mineur, parent ou tuteur ; le permis s'obtient à 16 ans |
| D12 | `anplwaye.html:170` : « chaque personne a explicitement accepté d'être contactée » est faux pour la posture `approval` | 🟠 | **à faire** | ceux-là n'ont justement accepté aucun contact avant validation |
| D13 | Remonter l'exclusion de garantie de `wout.html:115` au niveau du titre qui promet de faire « PASSER le test » | 🟠 | **à faire** | la hiérarchie visuelle est l'inverse de la hiérarchie juridique |
| D14 | Quatre questions pour un avocat du Massachusetts : statut FCRA, colonne `auth`, immatriculation, agence de placement | 🔵 | **à arbitrer — humain** | le site s'est auto-attribué la conclusion « we are not an employment agency » |

## E — Exactitude métier (RMV / 7D)

| # | Recommandation | Gravité | État | Preuve |
|---|---|---|---|---|
| E1 | Retourner l'argument de `setdi.html` : le manuel 7D existe en kreyòl, español et português depuis avril 2026 | 🔴 | **à faire** | mass.gov, *Gid sou Veyikil ki Transpòte Elèv Lekòl (7D)*, 42 p., éd. fév. 2026, mis en ligne le 10/04/2026 — le site affirme le contraire 4 fois |
| E2 | Écrire que l'accompagnateur doit détenir un permis **américain** — un permis étranger fait refuser le test | 🔴 | **à faire** | RDT101_0825 : « An individual with a foreign, non-U.S. license, cannot serve as a sponsor » ; + permis physique, 3 candidats/12 mois, place derrière le conducteur |
| E3 | `q15` : braquer **dans la direction du dérapage**, pas « où vous voulez aller » | 🔴 | **à faire** | manuel, ch. 5 « Skidding », formulation répétée 3 fois ; aucune des 4 options ne la contient |
| E4 | `jobs.html` : le 7D n'est pas « a written test only » | 🔴 | **à faire** | 21 ans, 3 ans de permis, CORI/SORI notarié, médical, 2 h de formation, PUIS l'écrit — `setdi.html:180` le dit déjà correctement |
| E5 | `jobs.html` : le covoiturage exige un Background Check Clearance Certificate du DPU | 🔴 | **à faire** | + permis américain depuis 1 an (23 ans et plus) ou 3 ans (moins de 23 ans) |
| E6 | `jobs.html` : Amazon exige 21 ans, pas « a Class D licence and a clean record » | 🔴 | **à faire** | employeur mis en avant comme la première source d'emploi de l'État |
| E7 | Relibeller la grille F/mineure en classement maison et trancher la contradiction sur la lenteur | 🔴 | **à faire** | le RMV ne publie aucune grille ; `komand.json:k11` et `wout.html:M.b6` se contredisent |
| E8 | Ajouter une question pour le permis d'apprenti : couvre-feu **minuit**, pas 0 h 30 | 🔴 | **à faire** | `q12` applique la règle du JOL à l'apprenti ; conduire à 0 h 15 devient une infraction pénale |
| E9 | Ajouter la manœuvre officielle manquante : démarrer, arrêter et tourner **en côte** | 🟠 | **à faire** | `k18` couvre le stationnement en pente, pas la côte |
| E10 | Écrire ce qui fait rater le test avant qu'il commence | 🟠 | **à faire** | formulaire imprimé, 15 min d'avance, frein à main accessible, odeur, enfants/animaux, 35 $ non remboursés, 6 tentatives/12 mois, Driver's Ed pour les mineurs |
| E11 | Corriger 10 imprécisions du test écrit (q21, q26, q13, q16, q02, q06, q10, q19, q01, q22) | 🟠 | **à faire** | détail par question dans le rapport de relecture |
| E12 | Corriger 4 conseils de `komand.json` (k09, k12, k18) et aligner la promesse « commandes réelles » sur la note du fichier | 🟠 | **à faire** | k12 : le manuel dit 2-3 pieds et « ne pas utiliser les rétroviseurs » |
| E13 | Retirer les 4 doublons de la banque (q03≡q24, q04≡q23, q05≡q22, q11⊂q26) | 🟠 | **à faire** | 25 tirées sur 28 : le candidat voit deux fois la même question |
| E14 | « les 12 manœuvres du test » : le RMV en liste 11, et ce ne sont pas les mêmes | 🟠 | **à faire** | écrire « les 12 manœuvres de notre grille » ou reprendre la liste officielle |
| E15 | `setdi.html` : ajouter employeur préalable, validité 1 an, médical 90 j, CORI notarié, coût 30 $ | 🟠 | **à faire** | toute cette matière est aujourd'hui déléguée à un LLM sans garde-fou |
| E16 | Dater et sourcer les prérequis d'embauche affirmés employeur par employeur, ou les retirer | 🟠 | **à faire** | « nothing on this page goes stale » ne survit pas à des prérequis codés en dur |
| E17 | Ajouter la preuve de présence légale exigée pour le 7D si le Class D est postérieur au 01/07/2023 | 🟠 | **à faire** | Work and Family Mobility Act — décisif pour le public visé |
| E18 | Demander au RMV Road Test Program si une grille de notation existe | 🔵 | **à faire — humain** | rien de public n'adosse les 13 « échecs automatiques » |
| E19 | Décider du garde-fou des deux coachs LLM, dont les réponses ne sont auditables dans aucun fichier | 🔵 | **à arbitrer — humain** | âge, durée de permis, CORI et renouvellement sont répondus hors du dépôt |

## F — Accessibilité, thème, téléphone

| # | Recommandation | Gravité | État | Preuve |
|---|---|---|---|---|
| F1 | `@media print` : `*{color:#000!important;background:transparent!important}` dans `wout.html`, et un bloc dans `terms`/`privacy` | 🔴 | **à faire** | mesuré : guide à 1,45:1 et titres légaux à 1,00:1 sur papier quand le visiteur est en fond sombre |
| F2 | `var(--accent)` → `--d-accent`, `var(--muted)` → `--d-doux` dans `regen.py` et `suite.js` | 🔴 | **à faire** | 21 usages d'un jeton défini nulle part : liens de pied à 1,00:1 contre leur texte, page active non marquée |
| F3 | Élargir le motif de `appliquer_theme.py:183` à `href="/?assets/style\.css"` | 🔴 | **à faire** | `404.html` n'a jamais reçu `theme.css` : toujours en sombre, sans focus visible, sans reduced-motion — et le contrôle dit « vert » |
| F4 | `font-size:16px` dans les 4 règles de page qui posent `0.93rem` sur les champs | 🔴 | **à faire** | 14,88 px mesuré : iOS zoome, malgré `theme.css:218` battu à la spécificité |
| F5 | `role="status"` / `aria-live="polite"` sur les 8 zones remplies par JS | 🟠 | **à faire** | 0 occurrence sur 9 pages ; WCAG 2.1 SC 4.1.3 est de niveau AA |
| F6 | Étiqueter `cf-input` et `sd-input` (placeholder seul aujourd'hui) | 🟠 | **à faire** | 55 champs sur 57 sont corrects |
| F7 | Réparer l'ordre des titres sur 4 pages | 🟠 | **à faire** | `anplwaye` place un `h2` avant son `h1` ; `vivye` enchaîne `h1`→`h3` |
| F8 | Donner au menu de langue l'`aria-expanded`/`aria-controls` et le retour de focus qu'a le menu du téléphone | 🟠 | **à faire** | le menu ☰ est le composant le mieux fait du lot — d'où l'écart |
| F9 | Poser le lien d'évitement que `style.css:827` définit depuis une refonte | 🟠 | **à faire** | 0 occurrence dans les 9 pages |
| F10 | Souligner les liens de contenu (1,92:1 et 1,71:1 contre le texte, seuil 3:1) | 🟠 | **à faire** | `a{text-decoration:none}` global |
| F11 | Corriger le README ou les cibles : « aucune cible tactile sous 44 px » est faux | 🟠 | **à faire** | `.sd-tools button` ≈ 21 px, sous les 24 px du SC 2.5.8 |
| F12 | Retirer le CSS mort Lojik360, dont un `outline:none` sans remplacement | 🟠 | **à faire** | inerte aujourd'hui, amorcé pour le jour où la classe resservira |
| F13 | `.cf-fb.bad` : bordure identique au fond (`--d-alerte-bord` voulu) | 🟠 | **à faire** | le retour « mauvaise réponse » perd son cadre |
| F14 | `alt=""` sur le logo, dont le lien énonce déjà le nom | 🟠 | **à faire** | lecture en double par un lecteur d'écran |
| F15 | Exclure cases et boutons radio du `min-height:44px` | 🟠 | **à vérifier** | déduit de la cascade, à confirmer au navigateur |
| F16 | Ajouter à `appliquer_theme.py --verifier` un contrôle des noms de `var()` non déclarés | 🟠 | **à faire** | deux lignes, et ça ferme la classe entière de F2 |

## G — Fabrication, dépôt, découvrabilité

| # | Recommandation | Gravité | État | Preuve |
|---|---|---|---|---|
| G1 | `sys.exit(1)` dans `regen.py` quand un fichier de données est introuvable | 🔴 | **à faire** | prouvé en dépôt isolé : source retirée → `REGEN EXIT: 0` → « Build vert », et `verif_actifs.py` passe sur la copie périmée |
| G2 | Poser les balises Open Graph sur les 9 pages | 🔴 | **à faire** | 0 balise ; le canal du produit est WhatsApp, où chaque lien s'affiche en texte nu |
| G3 | Poser `<link rel="canonical">` sur les 4 pages dérivées | 🔴 | **à faire** | leurs originaux sont toujours en ligne sur atmart.ltd : contenu dupliqué, et c'est le nouveau domaine qui perd |
| G4 | Supprimer `assets/i18n/` et `assets/i18n.js` | 🟠 | **à faire** | 828 Ko publiés que `regen.py:174` empêche de charger, dont 113 Ko appartenant à l'Explorateur Haïti |
| G5 | Aligner le précache du service worker sur les URL réellement demandées (`?v=`) | 🟠 | **à faire** | `caches.match` compare la query : les 4 entrées ne sont jamais servies |
| G6 | Automatiser le bump de `CACHE` dans le build | 🟠 | **à faire** | seul garde-fou humain sur ce que le README qualifie de fatal |
| G7 | Faire produire `sitemap.xml` par le build | 🟠 | **à faire** | écrit à la main, 6 `lastmod` périmés, une 9ᵉ page n'y entrerait pas |
| G8 | Ajouter `404.html` au précache du service worker | 🟠 | **à faire** | absente de `CORE` |
| G9 | `manifest.webmanifest` : `theme_color` figé alors que le site a deux fonds | 🟠 | **à faire** | — |
| G10 | Retirer le drapeau `bloquant` mort de `build.py` et garder la trace d'erreur complète | 🟠 | **à faire** | `lancer()` n'imprime que la dernière ligne de stderr : le fichier et la ligne sont perdus |
| G11 | Décider du modèle d'URL par langue (`/en/wout.html`) ou assumer la perte de référencement | 🔵 | **à arbitrer — humain** | aucun `hreflang` n'est possible avec 4 langues sur une URL |
| G12 | Ajouter `Organization` en données structurées ; arbitrer `Course`/`FAQPage` | 🔵 | **à arbitrer — humain** | `JobPosting` serait un faux, `jobs.html` ne republiant aucune annonce |


## H — Parcours réel (site exercé au navigateur)

Cette section vient de la seule revue qui a **exercé** le produit en ligne
plutôt que de le lire. Elle confirme la plupart des autres — et trouve ce que
la lecture du code avait jugé fermé.

| # | Recommandation | Gravité | État | Preuve |
|---|---|---|---|---|
| H1 | Valider le lien de CV **dans `vivye.html`** avant l'envoi (`^https?://`) | 🔴 | **vérifié** | `lienSur()` n'accepte que `^https?://`. **Mesuré** : `type="url"` accepte bel et bien `javascript:`, `data:` ET `vbscript:` — la revue de code avait tort. Charge utile interceptée à l'envoi : `javascript:alert(1)` → `""`, `https://…` → passe |
| H2 | Trancher Cloudflare Web Analytics : le désactiver, ou l'ouvrir dans la CSP | 🟠 | **à faire** | le beacon est injecté par la zone et refusé par la CSP sur **chaque page** : zéro mesure d'audience, 2 à 4 erreurs rouges en console par visite. « Aucun traceur tiers » ne tient que parce que la CSP bloque un traceur que la zone essaie de poser |
| H3 | Une seule clé de cache pour `style.css` (5 pages sans `?v=`, 4 avec `?v=32`) | 🟠 | **à faire** | après une modification du CSS, l'accueil et la page des offres servent l'ancienne feuille depuis le service worker jusqu'au prochain bump de `CACHE` |
| H4 | Retirer `data-oi` du DOM : il révèle la bonne réponse | 🟠 | **à faire** | le tirage mélange l'affichage mais laisse l'index d'origine ; sans gravité pour un essai gratuit, à régler avant de facturer |
| H5 | Traiter l'erreur du lien de CV dans la zone `#rj-st` de la page | 🟠 | **à faire** | aujourd'hui c'est la bulle native du navigateur, en anglais sur une page espagnole, hors de l'endroit où la page met ses autres erreurs |
| H6 | Caler le quota gratuit sur l'heure locale, pas sur UTC | 🟠 | **à faire** | `toISOString().slice(0,10)` : les 5 questions se réinitialisent à 20 h au Massachusetts, pas à minuit |
| H7 | Rendre obligatoires les champs du formulaire employeur | 🟠 | **à faire** | aucun attribut `required` dans `anplwaye.html` : organisation, contact et téléphone peuvent être vides, seul le code est testé |
| H8 | Academy Bus et SchoolSpring aboutissent à une page générique | 🟠 | **à faire** | la page promet « un lien direct vers leurs offres — vous postulez au bon endroit » ; c'est vrai pour 18 des 20, pas pour ces deux-là |

## Ce que la huitième revue a confirmé — et qui rassure

Exercé en ligne, hors des défauts ci-dessus : **le Worker accepte l'origine sur
ses quatre routes** (préflight vérifié à la main), donc la panne silencieuse que
le README redoute n'existe pas. **Aucun 404 réseau, aucune erreur JS** hors le
beacon de H2. Le site en ligne est **exactement** le dépôt, à l'obfuscation
d'adresses de Cloudflare près. Le test écrit va au bout, le lecteur vocal parle,
les exercices de commandes tournent, les 3 thèmes sont mémorisés, les 4 langues
basculent proprement, et à 375 px **aucune page ne déborde**. Les contrastes,
remesurés en compositant les fonds translucides, ne montrent **aucun échec AA**.

Le bouton « Suivant » resté en français — le défaut qui a fait naître
`verif_ids_traduits.py` — **ne se reproduit pas** dans le quiz. Le même défaut
vit ailleurs : sur le portail employeur (B2).

---

## Ce que cette relecture a déjà appris

**Les contrôles verts mesuraient moins que ce qu'ils laissaient croire.**
`build.py --liens` sort 0, les 26 paires de contraste tiennent, les 20 liens
employeurs répondent 200 — et pourtant : `verif_ids_traduits.py` lit un autre
dépôt (B4), `appliquer_theme.py --verifier` compte une page qui n'a jamais reçu
le thème (F3), `verif_contraste.py` ne voit pas un jeton qui n'existe pas (F2),
et `regen.py` sort en 0 quand la copie échoue (G1).

C'est la même leçon que celle des docstrings de `tools/` — **la panne est
silencieuse** — appliquée cette fois aux gardiens eux-mêmes. Un contrôle qui
passe au vert sur un périmètre plus étroit que ce qu'il annonce est plus
dangereux qu'un contrôle absent : il autorise à ne pas regarder.

D'où `tools/etat_suivi.py`, qui ne relit pas ce tableau mais le recalcule.
