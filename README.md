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

La navigation reste séparée par côté du marché : un chauffeur ne voit pas le
portail employeur dans son menu, et réciproquement.

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
python tools/gen_emplois.py --verifier   # ouvre les 8 liens, dit lesquels sont morts
python tools/gen_emplois.py              # régénère la page
```

Au 29/08/2026 : 8 employeurs, 8 liens vivants.

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

Vérifié à 375 px : aucun débordement horizontal, aucune cible tactile sous
44 px, champs de formulaire à 16 px — en dessous, iOS zoome tout seul sur le
champ et le visiteur se retrouve perdu dans une page agrandie.

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
  nationalité n'y figure jamais du tout.

⚠️ **Ce qui manque, et qui ne peut pas venir d'ici.** `frame-ancestors` (contre
l'encadrement de la page dans un site tiers) et `X-Content-Type-Options` ne
s'appliquent QUE dans un en-tête HTTP, et GitHub Pages n'en pose aucun.
À créer dans **Cloudflare → Rules → Transform Rules → Modify Response Header**,
sur `driver360.atmart.ltd` :

| En-tête | Valeur |
|---|---|
| `Content-Security-Policy` | `frame-ancestors 'none'` |
| `X-Content-Type-Options` | `nosniff` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | `geolocation=(), microphone=(), camera=()` |

## Le logo

`tools/gen_logo.py` dessine la marque et ses six déclinaisons. Elle dérive du
**logo actuel** d'Atmart — la boucle-ruban qui se déploie en filaments à
points. La boucle porte ici le sens du nom (360°), les filaments se lisent
comme des trajets, et le dégradé aboutit au turquoise du site.

En dessous de 64 px le dessin se **simplifie** — quatre filaments au lieu de
sept, plus épais. À 32 px les sept se rejoignaient en une bouillie, et un logo
doit survivre à sa plus petite taille : c'est là qu'on le voit le plus souvent.
