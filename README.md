# Driver360 — driver360.atmart.ltd

La suite conduite d'Atmart **pour tous les résidents du Massachusetts** :
trouver un emploi de chauffeur, obtenir le permis qu'il demande, et recruter.

## À qui la suite s'adresse — décidé le 29/08/2026

Driver360 s'adresse à **tout résident du Massachusetts** qui veut lever la
barrière à l'emploi que représentent le Class D et le 7D. Ce n'est **pas** un
produit communautaire.

Conséquences, appliquées partout :

- **La langue écrite dans le HTML est l'anglais**, y compris la navigation. Le
  kreyòl, le français et l'espagnol restent à un clic sur chaque page : ils sont
  un **avantage** du produit, pas son identité.
- **Ni les Haïtiens ni le test de route ne sont mis en avant sur l'accueil.**
  L'accueil parle d'emploi. Le permis apparaît comme ce qui sépare quelqu'un
  d'un poste — un moyen, jamais la promesse principale.

## La règle qui commande la structure

Suite360 sert **une** personne : le chercheur d'emploi passe d'Interview360 à
Career360 sans changer de casquette. Ici, ce n'est pas le cas — un chauffeur et
un employeur ne veulent pas la même chose et n'arrivent pas par la même porte.

**L'accueil bifurque donc immédiatement**, et aucune page n'essaie de parler aux
deux à la fois :

## Trois produits, dans cet ordre

L'ordre est une décision, pas un hasard — il dit où est la valeur :

| # | Produit | Page | Pour qui |
|---|---|---|---|
| 1 | **Driver Pool** — le vivier. L'actif : sans chauffeurs inscrits, rien d'autre ne vaut. | `vivye.html` | chauffeurs |
| 2 | **Driver Employer** — la demande, et donc le revenu. | `anplwaye.html` | entreprises |
| 3 | **Driver Coach** — la préparation (test de route, 7D). Le canal qui *remplit* le vivier. | `wout.html`, `setdi.html` | chauffeurs |

**Attention aux noms.** La **suite** s'appelle Driver360 ; le **coach** s'appelle
**Driver Coach**. Les confondre — ce que faisait la première version — rend la
suite illisible : on ne sait plus si « Driver360 » désigne le tout ou une partie.

La navigation est **unique sur les six pages** : Driver Pool · Driver Employer ·
Job Postings · Driver Coach. Elle était séparée par côté du marché jusqu'au
30/08 — un chauffeur ne voyait pas le portail employeur. L'idée se défendait,
mais le produit qui rapporte n'apparaissait alors nulle part pour qui n'était
pas déjà du bon côté.

## Le vivier est vide, et la page le dit

Au 20 août 2026 : **zéro chauffeur inscrit** (vérifié dans le KV du Worker).

La page employeur, elle, **parcourt des viviers** — Class D, 7D, déjà licenciés.
Ces viviers sont donc vides, et un employeur qui clique sur « Ouvrir le pool »
ne trouve rien. Plutôt que de le lui laisser découvrir, `tools/regen.py` pose en
tête de page un bandeau qui le dit et **recueille sa demande** (quelle classe,
combien, quelle ville). Deux raisons : un employeur qui découvre une liste vide
ne revient jamais, et savoir qui cherche quoi donne aux chauffeurs une raison
concrète de s'inscrire.

**Retirer ce bandeau le jour où le vivier compte de vrais chauffeurs — pas avant.**
Il est dans `APPEL_EMPLOYEUR`, en tête de `tools/regen.py`.

## `jobs.html` — la page qui renverse la relation

Un chauffeur ne s'inscrit pas dans un vivier pour figurer dans une base. Il
s'inscrit parce qu'il y a un poste. Tant que le site ne disait que « inscrivez-
vous, on vous trouvera peut-être », il demandait un service au chauffeur au lieu
de lui en rendre un. `jobs.html` donne quelque chose d'utile **avant** de
demander quoi que ce soit.

**Elle ne republie aucune annonce.** Elle liste les employeurs qui recrutent des
chauffeurs au Massachusetts et renvoie sur *leur* page. Rien n'y périme, aucune
condition d'utilisation d'un agrégateur n'est enfreinte, et le chauffeur postule
au bon endroit du premier coup.

Les employeurs sont dans `tools/emplois.py`, avec la date de vérification.
**Aucune URL n'entre sans avoir été ouverte :**

```bash
python tools/gen_emplois.py --verifier   # ouvre les 20 liens, dit lesquels sont morts
python tools/gen_emplois.py              # régénère la page
```

Au 31/08/2026 : **20 employeurs sur 7 secteurs**, tous les liens ouverts et vérifiés.

Les employeurs qui nous ENVOIENT une offre ont leur propre liste, `OFFRES` dans
le même fichier. ⚠️ Une offre sans date de vérification ne s'affiche pas, et une
offre pourvue se retire : une page qui garde des postes fermés fait perdre son
temps à qui la lit.

## Les alertes WhatsApp

À l'inscription au vivier, une **deuxième case, facultative**, demande à être
prévenu quand une offre s'ouvre. Elle est distincte du consentement au vivier :
on peut vouloir être trouvé par un employeur sans vouloir recevoir de messages.

Le Worker stocke `wa` **et `waAt`**, l'horodatage du consentement. Le booléen
seul ne suffit pas : la loi américaine (TCPA) et les règles de Meta demandent de
pouvoir montrer *quand* il a été donné. Un consentement déjà donné **garde sa
date d'origine** quand la fiche est modifiée ; le retirer efface la date.

**Aujourd'hui l'envoi est manuel.** Le compte WhatsApp Business n'est pas ouvert
(il demande un numéro dédié, un compte vérifié et des gabarits approuvés par
Meta, facturés à la conversation). La page le dit en toutes lettres plutôt que
de laisser croire à un système automatique. Le consentement, lui, est collecté
et daté dès maintenant — c'est ce qui rendra l'ouverture du compte possible.

## Régénérer les pages

Les quatre pages dérivées d'atmart.ltd ne sont **jamais** éditées ici.
`index.html` et `jobs.html`, elles, appartiennent à ce dépôt :

```bash
python tools/regen.py        # les 4 pages derivees
python tools/gen_emplois.py  # jobs.html
```

Sources : `chofe360.html`, `setd360.html`, `rejistre.html`, `anplwaye360.html`.
Le script pose l'en-tête et le pied Driver360, retire les scripts propres à
atmart.ltd, et rend absolus les liens qui sortent de la suite.

## Ce dont ça dépend

- **Worker `atmart-chat`** — routes `/wout`, `/setd`, `/rejistre`, `/anplwaye`.
  `https://driver360.atmart.ltd` doit figurer dans `ALLOWED_ORIGINS`, sinon le
  Worker répond et le navigateur jette la réponse : panne silencieuse.
- **GitHub Pages** — publier = pousser sur `main`.
- **DNS** — un CNAME `driver360` → `jwmyril.github.io` **dans Cloudflare**,
  proxifié (nuage orange), comme `360` et `arpentaj`. Porkbun n'est que le
  bureau d'enregistrement : les serveurs de noms d'`atmart.ltd` sont délégués à
  Cloudflare, donc un enregistrement posé chez Porkbun ne serait jamais lu.
  Posé le 29/08/2026.
- **Service worker** — bumper `CACHE` dans `sw.js` à chaque refonte visible,
  sinon les visiteurs gardent l'ancienne page pendant des jours.


## Reconstruire

**Une seule commande**, et elle refuse de finir si quoi que ce soit est cassé :

```bash
python tools/build.py
```

Ajouter `--liens` pour rouvrir en plus les 20 liens employeurs.

L'ordre compte (le thème s'applique aux pages générées, les contrôles lisent le
résultat), et chaque oubli déjà commis dans ce dépôt était une panne
**silencieuse** : fichier de données absent, page à moitié traduite, couleur
écrite en dur. Rien ne casse, la page s'affiche — elle affiche juste faux.

## Fond clair et fond sombre

Trois états dans la barre : **Auto** (suit le système, c'est le défaut), Clair,
Sombre. Le choix est mémorisé.

Ce n'était pas qu'une affaire de goût : les pages portaient leurs couleurs
**écrites en dur**. Aucun réglage global ne rattrape cela.
`tools/appliquer_theme.py` les remplace donc toutes par des jetons dont
`assets/theme.css` donne deux jeux de valeurs, et son `--verifier` refuse
qu'une couleur littérale réapparaisse.

**Deux pièges, tous deux rencontrés :**

- ⚠️ **Convertir la moitié d'un système de couleurs est pire que ne rien
  convertir.** La première passe n'avait traité que les pages, pas `style.css` :
  sur fond clair, `.trn h4` restait blanc sur une carte devenue blanche —
  contraste 1,06:1, plus de cinquante textes invisibles. Les deux vont ensemble.
- ⚠️ **Les blocs `@media print` ne se thématisent pas.** La passe y avait
  transformé `background:#fff` en un jeton qui vaut presque noir sur fond
  clair : le guide de l'accompagnateur se serait imprimé en noir plein. Le
  papier est toujours blanc.

Les contrastes sont **mesurés**, pas estimés : les 8 pages passent le seuil AA
(4,5:1, ou 3:1 pour les grands titres) dans les deux fonds.

## Téléphone

À 375 px, la navigation empilait six lignes et occupait **tout le premier
écran**. La feuille prévoyait pourtant un menu repliable — mais l'en-tête ne
posait pas le bouton, et son `style="display:flex"` **écrit en ligne** battait
le `display:none` de la feuille. Un attribut `style` gagne toujours contre une
feuille : c'est exactement pourquoi il ne faut pas y mettre de mise en page.

Vérifié à 375 px : aucun débordement horizontal, et champs de formulaire à
16 px — en dessous, iOS zoome tout seul sur le champ et le visiteur se
retrouve perdu dans une page agrandie.

⚠️ **Ce paragraphe a longtemps affirmé « aucune cible tactile sous 44 px ».
C'était faux**, et mesuré faux le 30/08/2026 : `.sd-tools button` faisait
environ 21 px. La règle réelle, celle que le site applique, tient en deux
seuils :

- **44 px** pour ce qui se touche vraiment — boutons, options de menu, liens
  de navigation. C'est la règle d'Apple, et Google demande 48.
- **24 px** pour les boutons-texte qui vivent **dans une ligne de texte**.
  Les porter à 44 casserait la ligne ; 24 px est ce que demande le SC 2.5.8,
  et c'est le seuil qui s'applique à ce cas-là.

Un README qui promet mieux que le code ne sert à rien : c'est lui qu'on lit
avant de décider qu'un contrôle est inutile.

## Sécurité

En place :

- **Politique de sécurité du contenu** sur chaque page (posée par
  `appliquer_theme.py`) : aucun script d'un autre domaine, et un seul
  interlocuteur réseau — le Worker.
- **Échappement de toute donnée saisie par un utilisateur** avant insertion
  dans le HTML du portail employeur (`esc()`), et **validation du lien de CV**
  côté page *et* côté Worker : seul `http(s)` est accepté.
- `rel="noopener noreferrer"` sur les liens qui ouvrent un onglet.
- Le contact d'un chauffeur n'est jamais dans la liste parcourue ; la
  nationalité n'apparaît jamais dans la liste parcourue ; elle est révélée APRÈS sélection, avec le contact — c'est ce que dit `privacy.html`.

⚠️ **Ce qui manque, et qui ne peut pas venir d'ici.** `frame-ancestors` (contre
l'encadrement de la page dans un site tiers) et `X-Content-Type-Options` ne
s'appliquent QUE dans un en-tête HTTP, et GitHub Pages n'en pose aucun.
À créer dans **Cloudflare → Rules → Transform Rules → Modify Response Header**,
sur `driver360.atmart.ltd` :

| En-tête | Valeur | État au 30/08/2026 |
|---|---|---|
| `X-Frame-Options` | `SAMEORIGIN` | ✅ posé |
| `X-Content-Type-Options` | `nosniff` | ✅ posé |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | ✅ posé |
| `Strict-Transport-Security` | `max-age=15552000; includeSubDomains` | ✅ posé |
| `Permissions-Policy` | `geolocation=(), microphone=(), camera=()` | ⬜ à poser |

Vérifier à tout moment : `curl -sI https://driver360.atmart.ltd/ | grep -i policy`

`X-Frame-Options: SAMEORIGIN` couvre déjà l'encadrement dans un site tiers, donc
`frame-ancestors` en en-tête n'est plus indispensable. La CSP complète reste
dans un `<meta>` de chaque page : toutes ses directives s'y appliquent sauf
`frame-ancestors`, précisément celle que l'en-tête ci-dessus remplace.

## Le logo

`tools/gen_logo.py` dessine la marque et ses six déclinaisons. Elle dérive du
**logo actuel** d'Atmart — la boucle-ruban qui se déploie en filaments à
points. La boucle porte ici le sens du nom (360°), les filaments se lisent
comme des trajets, et le dégradé aboutit au turquoise du site.

En dessous de 64 px le dessin se **simplifie** — quatre filaments au lieu de
sept, plus épais. À 32 px les sept se rejoignaient en une bouillie, et un logo
doit survivre à sa plus petite taille : c'est là qu'on le voit le plus souvent.

## Ouvrir le compte WhatsApp Business

⚠️ **DEUX PRODUITS PORTENT CE NOM**, et confondre les deux fait perdre des
semaines.

| | WhatsApp Business (l'appli) | WhatsApp Business Platform (Cloud API) |
|---|---|---|
| Prix | gratuit | par message livré |
| Envoi | à la main, depuis un téléphone | par programme |
| Gabarits à faire approuver | non | oui |
| Vérification d'entreprise Meta | non | oui |
| Ce qu'il faut pour Driver360 **aujourd'hui** | ✅ suffit | prématuré |

**COMMENCER PAR L'APPLI GRATUITE.** `tools/alertes_whatsapp.py` prépare déjà
des liens `wa.me` qu'on ouvre et qu'on envoie à la main : c'est exactement le
mode de travail de l'appli. Avec zéro chauffeur dans le vivier, monter la
Platform maintenant, ce serait de la vérification d'entreprise et des gabarits
à faire approuver pour zéro message envoyé.

Le jour où l'envoi manuel devient impraticable — disons au-delà d'une trentaine
d'alertes par semaine — la Platform devient justifiée. Les quatre messages de
`MESSAGES` sont déjà écrits pour devenir les gabarits à soumettre.

### Un compte existe déjà (créé pour Arpentaj)

⚠️ **PARTAGER LA VÉRIFICATION, SÉPARER LES NUMÉROS.** C'est la décision, et
elle n'est pas symétrique.

Ce qui se PARTAGE — le **portefeuille d'entreprise Meta** et sa vérification.
Elle se fait une fois, au niveau du portefeuille, et couvre tous les comptes
WhatsApp qui vivent dessous. Refaire vérifier Atmart LLC pour Driver360 serait
du travail perdu.

Ce qui se SÉPARE — le **numéro**. Arpentaj écrit à des arpenteurs en Haïti au
sujet de leurs dossiers ; Driver360 écrit à des chauffeurs du Massachusetts au
sujet d'offres d'emploi. Trois raisons de ne pas mélanger :

  · **le consentement ne se transfère pas.** Quelqu'un qui a accepté d'être
    prévenu par Arpentaj n'a rien accepté de Driver360 ;
  · **la réputation est attachée au numéro.** Des alertes d'emploi signalées
    comme indésirables dégraderaient la qualité du numéro d'Arpentaj — et
    couperaient un canal client au passage ;
  · **une suspension frappe le numéro.** Un seul incident côté Driver360
    fermerait le canal d'Arpentaj le même jour.

**Vérifier ce qu'on a réellement**, avant toute chose :

| Question | Où regarder | Ce que ça veut dire |
|---|---|---|
| L'appli gratuite ou la Platform ? | business.facebook.com → WhatsApp Manager | si aucun « WhatsApp Account » n'apparaît, c'est l'appli gratuite |
| Le portefeuille est-il vérifié ? | Paramètres du portefeuille → Centre de sécurité | « Vérifiée » = l'étape la plus longue est déjà faite |
| Le numéro est-il pris ? | WhatsApp Manager → Numéros de téléphone | un numéro déjà sur l'appli doit être désinscrit, ou passer en Coexistence |

### Si un compte existe et a été restreint

Le vocabulaire de Meta distingue quatre états, du plus léger au plus grave :
**restreint** (ça marche, quelque chose est bridé), **suspendu** (verrouillé en
attente d'un examen humain), **banni** (le numéro est détaché de WhatsApp), et
**WABA désactivé** (l'actif est gelé pendant l'examen du portefeuille).

Demander l'examen : depuis l'appli, « Request a review » quand le bouton est
proposé ; depuis la Platform, par **Meta Business Support Home** ou WhatsApp
Manager. Compter 24 à 48 h, jusqu'à 7 jours ouvrés si la vérification
d'entreprise est en cause. **L'examen ne garantit pas le rétablissement.**

### Les pièges propres à Driver360

⚠️ **Nos alertes sont de catégorie « marketing »** au sens de Meta — une offre
d'emploi n'est pas une notification de service. C'est la catégorie la plus
chère, et elle est facturée à chaque message même dans une fenêtre de service
ouverte. Ne pas essayer de les faire passer pour de l'« utility » : c'est
exactement le genre de chose qui fait restreindre un compte.

⚠️ **Ne jamais utiliser un numéro personnel.** Un numéro déjà actif sur l'appli
gratuite doit être désinscrit avant de passer à la Cloud API — ou passer par
la **Coexistence**, qui permet de garder l'appli et l'API sur le même numéro.

⚠️ **La vérification d'entreprise demande le nom légal et l'adresse.** C'est le
MÊME renseignement qui manque aux pages légales (`terms.html`, `privacy.html`).
Une seule information manquante bloque deux chantiers : la fournir une fois
débloque les deux.

**Ce qui nous protège si le numéro est signalé** : le consentement horodaté
(`waAt` sur chaque fiche) et le plafond de deux messages par semaine, tenu par
`--marquer`. La qualité d'un numéro se dégrade quand les gens bloquent ou
signalent ; le plafond n'est pas seulement une promesse tenue, c'est ce qui
garde le numéro en vie.

Tarifs et catégories à jour : <https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing>

## Ce qui reste à faire, et par qui

Ce tableau est ici pour survivre à la conversation qui l'a produit.

| Quoi | Qui | Pourquoi ça bloque |
|---|---|---|
| Ouvrir le compte WhatsApp Business | vous | numéro dédié, compte vérifié, gabarits approuvés par Meta. Sans lui l'envoi reste manuel — ce que la page annonce déjà. Les 4 messages de `tools/alertes_whatsapp.py` sont écrits pour devenir ces gabarits. |
| Poser `Permissions-Policy` dans Cloudflare | vous | les 4 autres en-têtes sont déjà là ; celui-ci ferme géoloc / micro / caméra. |
| Relire les 8 questions ajoutées au test écrit (`q21`–`q28`) | vous | elles portent `verif: "a-relire-2026-08-30"`. Retirer ce marqueur une fois recoupées avec le manuel courant du RMV. |
| Relecture kreyòl | vous | accueil, offres, pages légales, message d'alerte. Vous êtes l'autorité sur cette langue. |
| Adresse postale et État d'immatriculation | vous | les pages légales le signalent en clair plutôt que de l'inventer. Atmart LLC n'étant pas au Massachusetts, le marché visé ne le renseigne pas. |
| Lier le contact employeur→chauffeur à l'abonnement | à décider ensemble | le mécanisme existe (sélection, quota, accord du chauffeur) mais c'est le *crédit* qui le déclenche, pas un abonnement actif. Reste à décider ce qui se passe quand un abonnement s'arrête alors que des contacts ont déjà été révélés. |
