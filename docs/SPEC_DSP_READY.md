# Spécification « DSP-ready » — Driver360

Écrite le 03/09/2026, en réponse au courriel d'Ari Polivy (P1 Logistics,
DKO1 Littleton) du 02/09 : *« Time is my most precious commodity in logistics.
Money often comes second. »* et *« Indeed produces results, for a fee. Your
platform may cost less but doesn't have the results an employer like me
needs. »*

Il a raison. Ce document dit ce qu'on construit pour qu'il ait tort dans
soixante jours.

## 1. La thèse

Indeed vend des **candidatures**. Un DSP n'achète pas des candidatures ; il
achète l'absence de travail entre la candidature et le chauffeur qui se
présente lundi. Ce travail — vérifier l'âge et le permis, rappeler, planifier,
encaisser les absences, replanifier — c'est le temps d'Ari, et c'est ce que
Driver360 doit supprimer.

**DSP-ready** est le nom de cette suppression : un chauffeur que Driver360 a
déjà passé au crible des exigences d'un DSP, dont le téléphone répond, et dont
la disponibilité pour un entretien est déjà connue. Le DSP ne voit **que**
ceux-là, et n'a **rien à vérifier** avant de décrocher son téléphone.

Trois principes qui commandent tout le reste :

- **On vend des heures, pas des fiches.** Chaque champ ajouté doit retirer une
  vérification au DSP, sinon il n'entre pas.
- **On mesure, on ne déclare pas.** Ce qu'un chauffeur affirme est marqué
  *déclaré* ; ce que Driver360 a observé est marqué *mesuré*. Le badge ne
  confond jamais les deux.
- **Rien qui serve à discriminer.** La règle déjà posée pour la nationalité
  (`privacy.html`) s'applique à tout : un champ visible pendant le tri est une
  invitation à trier dessus.

## 2. Les exigences d'un DSP — ce qu'on vérifie

Source : les annonces publiées par les DSP du Massachusetts (ZipRecruiter,
Indeed, 09/2026). Elles sont stables d'un DSP à l'autre parce qu'elles viennent
du programme Amazon. **À confirmer avec Ari et Ryan Rappoport** — la liste
ci-dessous est ce que les annonces disent, pas ce qu'Amazon impose en interne.

| # | Exigence DSP | Comment Driver360 le sait | Nature | Champ |
|---|---|---|---|---|
| R1 | **21 ans ou plus** | attestation à l'inscription (« J'ai 21 ans ou plus ») | déclaré | **à créer** `age21` |
| R2 | **Permis américain valide** (Class D suffit pour une camionnette) | case Class D cochée **+** attestation « délivré par un État américain, non suspendu » | déclaré | `licenses` existe ; **à créer** `licUS` |
| R3 | **Autorisé à travailler aux États-Unis** | `auth === "yes"` | déclaré | existe |
| R4 | **Dossier de conduite propre** (le DSP tire le MVR) | attestation « aucune suspension, aucun accident responsable, pas plus de 2 infractions mineures sur 3 ans » | déclaré | **à créer** `recordClean` |
| R5 | **Accepte le contrôle d'antécédents et le dépistage** | attestation | déclaré | **à créer** `screenOk` |
| R6 | **Peut porter 50 lb** de façon répétée | attestation | déclaré | **à créer** `lift50` |
| R7 | **Téléphone qui répond** | code envoyé par WhatsApp/SMS et saisi en retour | **mesuré** | **à créer** `phoneOk`, `phoneOkAt` |
| R8 | **Disponible pour un entretien sous 72 h** | trois créneaux choisis par le chauffeur, renouvelés à chaque confirmation de présence dans le vivier | déclaré, daté | **à créer** `slots[]` |

Ce qu'on **ne vérifie pas**, et qu'on écrit en clair au DSP : Driver360 ne
tire pas de MVR, ne fait pas de contrôle d'antécédents, ne teste personne.
C'est le DSP qui le fait, comme aujourd'hui. Driver360 lui garantit seulement
qu'il ne le fera pas pour rien — et c'est déjà ce qui lui coûte du temps.

## 3. Ce que le modèle porte déjà

Relevé sur `vivye.html` (`profile()`), `wout.html` (bloc partage) et
`src/worker.js` (`drvProfile`, action `list`) au 03/09/2026 :

| Déjà là | Sert à |
|---|---|
| `licenses` (Class D · 7D · CDL), `years` | R2, expérience |
| `auth` (yes / sponsor / pending) | R3 — **jamais affiché avant sélection** (C2/D6) |
| `avail` (fulltime / parttime / both), `flex`, `seeking` | correspondance avec la demande |
| `city` | rayon autour du dépôt |
| `lang` | langue de l'alerte, langue de l'entretien |
| `contact` (direct / approval) | posture |
| `readiness`, `quizBest`, `written`, `road`, `testDate` (coach, si la case de partage est cochée) | la réserve invisible (§ 7) |
| `lastSeen` / `fresh`, `POOL_DORMANT_DAYS = 45` | fraîcheur |
| `outcome` (hired / rejected), `undeclared`, blocage à 3 | le score de fiabilité (§ 5) |
| `wa`, `waAt` | consentement aux alertes |

**Ce qui manque** tient en sept champs (R1, R2-bis, R4, R5, R6, R7, R8) et
deux mécanismes (la vérification du téléphone, les créneaux). Aucun n'exige
une donnée sensible : **pas de date de naissance, pas de numéro de permis,
pas d'adresse** — on reste hors de 201 CMR 17.00, comme aujourd'hui.

## 4. Le badge

Un chauffeur est **DSP-ready** quand R1 à R8 sont tous vrais **et** que sa
fiche a été confirmée depuis moins de 14 jours (pas 45 : un DSP recrute pour
lundi, pas pour le mois prochain).

Trois états, et un seul est visible du DSP :

| État | Qui le voit | Comment |
|---|---|---|
| **DSP-ready** | le DSP, avant sélection | badge `✔ DSP-ready · confirmé il y a 2 j` dans la liste. Aucun des huit champs n'est affiché individuellement — **le badge remplace les colonnes**, il ne s'y ajoute pas |
| **Presque** — il manque R7 ou R8 | le chauffeur seulement | « Confirmez votre téléphone » / « Choisissez trois créneaux » — deux actions, pas une leçon |
| **Non éligible** — R1 à R6 faux | le chauffeur seulement, en termes neutres | il n'apparaît pas dans le filtre DSP ; il reste dans le vivier général (7D, transport médical, districts n'ont pas les mêmes exigences) |

Pourquoi le badge remplace les colonnes : c'est la seule façon de tenir la
règle du § 1. « Autorisé : ⏳ » en colonne est un tri ; « DSP-ready » ne dit
rien de plus que « rien à vérifier », et ne dit rien de *qui* échoue à quoi.

Le badge porte une date parce qu'il **vieillit** : un chauffeur embauché
ailleurs mardi n'est plus disponible mercredi. `POOL_DORMANT_DAYS` reste à 45
pour le vivier ; DSP-ready expire à **14** et se renouvelle d'un clic depuis
l'alerte WhatsApp (« Toujours disponible ? Oui → 3 créneaux »).

## 5. Le score de fiabilité — mesuré, jamais déclaré

C'est l'actif que ni Indeed ni personne n'a, et il ne coûte qu'un champ de
plus dans le flux qui existe déjà.

Aujourd'hui l'employeur déclare `hired` ou `rejected`, et il est bloqué après
trois sélections non déclarées. On ajoute **une étape avant** : `showed` /
`noshow`. Le DSP la déclare le jour de l'entretien, en un clic depuis le
WhatsApp de rappel — pas dans un portail.

| Mesure | D'où elle vient | Ce qu'elle dit au DSP |
|---|---|---|
| **Délai de réponse** | temps entre l'alerte envoyée et la confirmation du chauffeur | « répond en 3 h en moyenne » |
| **Taux de présence** | `showed` / (`showed` + `noshow`) | « 4 entretiens, 4 présences » |
| **Embauches** | `hired` | « embauché 1 fois par un DSP » |
| **Tenue à 30 jours** | relance au DSP à J+30 (`kept` / `left`) | le seul chiffre qui prédit le suivant |

Règles :

- Rien ne s'affiche **avant 3 observations** — un 100 % sur une observation
  est un mensonge statistique, et un 0 % détruit quelqu'un pour une panne de
  voiture.
- Le chauffeur **voit son propre score** et sait ce qui le fait bouger.
- Un `noshow` déclaré par le DSP vaut une **notification au chauffeur** avec
  droit de réponse (24 h) avant d'être compté : le DSP peut s'être trompé de
  personne, et c'est arrivé partout où ce mécanisme existe.
- Ce n'est **pas un consumer report** : Driver360 observe ses propres
  transactions (l'exception « transactions et expériences » de la FCRA), et
  n'agrège aucune source tierce. La clause D9 du registre reste à écrire dans
  les CGU pour le dire.

## 6. La demande en un message — le « 48 heures »

Ari ne veut pas de portail. Le portail existe et reste pour ceux qui le
veulent ; **le chemin principal devient un message.**

```
DSP  →  WhatsApp / e-mail : « 5 DAs, Littleton, start Monday »
        ─ accusé sous 1 h (heure de réception publiée)
Driver360 filtre : DSP-ready · rayon 25 mi autour de DKO1 · dispo lundi
        ─ alerte aux N premiers, par langue, avec les créneaux du DSP
Chauffeurs confirment un créneau depuis WhatsApp (un tap)
        ─ liste courte au DSP sous 48 h : nom, téléphone, créneau confirmé
DSP tient l'entretien, déclare showed/noshow d'un tap
        ─ un noshow est remplacé dans les 24 h, sans redemander
```

Ce qui est **mesuré et publié** sur la page employeur, comme une page de
statut : délai d'accusé médian, délai de liste courte médian, taux de présence
global. Trois nombres, datés, recalculés chaque nuit. Un DSP qui les voit à
« 40 min · 31 h · 86 % » n'a pas besoin d'argumentaire. Et s'ils sont mauvais,
ils sont mauvais publiquement — c'est la même discipline que le registre.

Ce que ça demande côté outil : `tools/alertes_whatsapp.py` sait déjà écrire
aux chauffeurs par langue et tenir le plafond de deux messages par semaine ;
il lui manque **la demande comme objet** (`req:` dans le KV : DSP, dépôt,
nombre, date, rayon, créneaux) et **la réponse du chauffeur comme événement**
(`?r=REQ-XXXX&s=2` → confirmation du créneau 2, avec clic obligatoire, jamais
au simple chargement — règle C9).

## 7. La réserve invisible

Driver Coach prépare des gens qui **n'ont pas encore leur permis**. Sur
Indeed, ils n'existent pas. Driver360 connaît leur `testDate`.

Le produit, pour un DSP : une ligne dans sa vue — *« 9 candidats à moins de
25 mi de DKO1 passent leur test de route dans les 30 jours »* — et un bouton
**Réserver** qui pose une alerte : le jour où `road === "pass"` est déclaré,
le chauffeur reçoit la demande du DSP en premier, avant tout autre.

Conditions, toutes déjà dans le code : la case de partage du coach cochée
(`wout.html`, bloc « I want employers to see how far along I am »), le
résultat déclaré par le chauffeur, la ville. Rien à collecter de plus. C'est
la seule partie de Driver360 qu'aucun concurrent ne peut copier sans avoir
d'abord construit un coach de test de route dans quatre langues.

## 8. Tarification liée au temps épargné — indicative, à valider avec Ari

Le 49 $/mois actuel demande au DSP de payer **avant** d'avoir vu un résultat.
C'est exactement le risque qu'Ari refuse. On inverse :

| Événement | Prix indicatif | Pourquoi ce moment |
|---|---|---|
| Demande, liste courte, alertes | 0 $ | le DSP ne paie pas pour essayer |
| **Candidat présent à l'entretien** (`showed`) | 25–40 $ | c'est l'heure épargnée qu'on facture |
| **Embauche confirmée à J+30** (`kept`) | 150–250 $ | aligné sur ce que le DSP gagne vraiment |
| Programme fondateur (3 DSP, 90 j) | 0 $ contre les données de résultat | § 9 |

Repère à obtenir d'Ari : ce qu'Indeed lui coûte **par embauche tenue**, pas par
mois. C'est le seul chiffre qui rend la comparaison honnête.

Garde-fou légal (D14) : c'est l'employeur qui paie, jamais le chauffeur, ce
qui tient Driver360 hors du régime des frais d'agence de placement du MA
(c. 140 §§ 46A-46R) dans la lecture la plus probable — **à confirmer par un
avocat avant la première facture**.

## 9. Le démarrage : les vingt premiers

Aucun des paragraphes précédents ne vaut rien tant que le vivier est vide.

- **Trois DSP fondateurs**, Ari le premier : sourcing gratuit 90 jours contre
  la déclaration systématique `showed / noshow / hired / kept`. Ces données
  amorcent le § 5 ; sans elles il n'y a pas de score, et sans score il n'y a
  pas de différence avec Indeed.
- **L'offre** : le réseau personnel (Fitchburg, Malden, Brockton), les
  utilisateurs de Driver Coach qui ont coché le partage, et la page des offres
  qui reçoit déjà des chauffeurs. Objectif : **20 DSP-ready à moins de 25 mi
  de Littleton** avant d'envoyer la première liste à Ari.
- **La seule mesure du pilote** : le délai entre la première demande d'Ari et
  le premier entretien **tenu**. Cible : < 5 jours pour le premier, 48 h en
  régime établi.

## 10. Ce qui change, fichier par fichier

| Fichier | Changement | Mesure pour `etat_suivi.py` |
|---|---|---|
| `Atmart_website/rejistre.html` → `vivye.html` | 6 attestations (R1, R2-bis, R4, R5, R6 + 50 lb) en cases cochables, sous un titre « Pour les postes de livraison » ; sélecteur de 3 créneaux ; bouton « Confirmer mon téléphone » | présence de `age21`, `licUS`, `recordClean`, `screenOk`, `lift50` dans `profile()` |
| `src/worker.js` `drvProfile` | stocke les 7 champs + `phoneOk/phoneOkAt` + `slots[]` ; calcule `dspReady` et `dspReadyAt` **côté serveur** — jamais côté page | `dspReady` calculé dans le Worker, absent des pages |
| `src/worker.js` action `list` | filtre `dsp=1` ; renvoie `dspReady`, `dspReadyAt`, `reliability` (si ≥ 3 obs.) ; **ne renvoie jamais** les champs R1–R6 individuellement | aucune clé `age21`/`recordClean`/`auth` dans la réponse `list` |
| `src/worker.js` action `outcome` | accepte `showed` / `noshow` / `kept` / `left` en plus de `hired` / `rejected` ; délai de contestation 24 h sur `noshow` | — |
| `anplwaye360.html` → `anplwaye.html` | filtre « DSP-ready seulement » ; colonne badge à la place des colonnes de tri ; bloc « Faire une demande en un message » en tête | absence de colonne `auth` avant sélection |
| `tools/alertes_whatsapp.py` | objet `req:`, alerte par demande, gabarit avec créneaux, `--showed`/`--noshow` | — |
| page employeur | trois compteurs publiés (accusé, liste courte, présence), recalculés par un script de build | présence des trois `data-mf` |
| `terms.html` / `privacy.html` (`legal_specs.py`) | les 7 attestations dans « ce que nous collectons » ; le score de fiabilité, ce qu'il contient et le droit de réponse ; clause FCRA (D9) ; tarification à l'événement | `verif_langue.py` vert |

Ordre de livraison : **§ 10 lignes 1-3** (le badge, une semaine), **§ 6**
(la demande en un message, une semaine), **§ 5** (le score, il se remplit
seul dès que le pilote tourne), **§ 7** (la réserve, quand le coach aura des
utilisateurs qui partagent).

## 11. Ce qu'on ne fait pas

- On ne tire pas de MVR, on ne fait pas de contrôle d'antécédents, on ne
  garantit aucune embauche. La page le dit ; le pilote le redit.
- On n'affiche jamais un critère individuel avant sélection. Le badge, ou rien.
- On ne calcule aucun score sous trois observations.
- On ne demande ni date de naissance, ni numéro de permis, ni adresse.
- On ne fait pas payer le chauffeur, jamais, pour rien.

## 12. Comment on saura que ça marche

| Mesure | Avant (03/09/2026) | Cible à 90 jours |
|---|---|---|
| Chauffeurs DSP-ready à 25 mi de Littleton | 0 | 20 |
| Délai demande → premier entretien tenu | — | < 5 j, puis 48 h |
| Taux de présence aux entretiens | — | > 80 % |
| DSP ayant fait une deuxième demande | 0 | 2 sur 3 |
| Ce qu'Ari écrit dans son prochain courriel | *« doesn't have the results »* | autre chose |
