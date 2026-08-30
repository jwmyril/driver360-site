# Driver360 — driver360.atmart.ltd

La suite conduite d'Atmart pour le Massachusetts : préparation au permis et
recrutement de chauffeurs, réunis sous une adresse à eux.

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

## Régénérer les pages

Les quatre pages sont **dérivées** d'atmart.ltd, jamais éditées ici :

```bash
python tools/regen.py
```

Sources : `chofe360.html`, `setd360.html`, `rejistre.html`, `anplwaye360.html`.
Le script pose l'en-tête et le pied Driver360, retire les scripts propres à
atmart.ltd, et rend absolus les liens qui sortent de la suite.

## Ce dont ça dépend

- **Worker `atmart-chat`** — routes `/wout`, `/setd`, `/rejistre`, `/anplwaye`.
  `https://driver360.atmart.ltd` doit figurer dans `ALLOWED_ORIGINS`, sinon le
  Worker répond et le navigateur jette la réponse : panne silencieuse.
- **GitHub Pages** — publier = pousser sur `main`.
- **DNS** — un CNAME `driver360` → `jwmyril.github.io` chez le registrar.
