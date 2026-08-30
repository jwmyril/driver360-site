# Driver360 — driver360.atmart.ltd

La suite conduite d'Atmart pour le Massachusetts : préparation au permis et
recrutement de chauffeurs, réunis sous une adresse à eux.

## La règle qui commande la structure

Suite360 sert **une** personne : le chercheur d'emploi passe d'Interview360 à
Career360 sans changer de casquette. Ici, ce n'est pas le cas — un chauffeur et
un employeur ne veulent pas la même chose et n'arrivent pas par la même porte.

**L'accueil bifurque donc immédiatement**, et aucune page n'essaie de parler aux
deux à la fois :

| Porte | Pages |
|---|---|
| 🚗 Je conduis | `wout.html` (coach du test de route) · `setdi.html` (permis 7D) · `vivye.html` (le vivier) |
| 🏢 Je recrute | `anplwaye.html` (dire son besoin) |

## Le vivier est vide, et la page le dit

Au 20 août 2026 : **zéro chauffeur inscrit**. La porte employeur ne montre donc
aucune liste — elle **recueille la demande** (quelle classe, combien, quelle
ville). Deux raisons : un employeur qui découvre une liste vide ne revient
jamais, et savoir qui cherche quoi donne aux chauffeurs une raison de s'inscrire.

**Ne pas remplacer ce bandeau par une promesse tant que le vivier n'existe pas.**

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
