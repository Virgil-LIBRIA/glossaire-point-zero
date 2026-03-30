# Glossaire du Systeme Point Zero

Lexique structure de 88 concepts du systeme philosophique Point Zero — un cadre ontologique explorant les dynamiques qualitatives de l'existence, de la conscience et de l'auto-organisation.

## Contenu

| Fichier | Description |
|---------|-------------|
| `glossaire_pz.json` | Glossaire complet (88 termes, relations, tenseurs) |
| `glossaire_pz.py` | CLI Python (stdlib uniquement) |
| `index.html` | Interface web de consultation |
| `GLOSSAIRE.md` | Export Markdown lisible |

## Les 6 piliers

| Code | Domaine | Termes |
|------|---------|--------|
| PZ | Point Zero — fondement ontologique | 24 |
| GQ | Geometrie Qualitative — mathematique du systeme | 15 |
| ETH | Ether Fluide — physique qualitative | 15 |
| CONSCIENCE | Conscience comme meta-organe sensoriel | 10 |
| PG | Psychologie Gestationnaire | 9 |
| A# | Systemie Symbiotique | 5 |
| OSS | Organisation Systemique Spontanee | 4 |
| MT | Machine Temporelle | 3 |
| INT | INTemple — OS philosophique | 2 |
| MC | MetaConjugaison | 1 |

## CLI

```bash
python glossaire_pz.py list                       # tous les termes
python glossaire_pz.py list --pilier ETH          # filtrer par pilier
python glossaire_pz.py show point-zero            # afficher un terme
python glossaire_pz.py search "ether"             # recherche
python glossaire_pz.py export --format md         # export Markdown
python glossaire_pz.py export --format csv        # export CSV
python glossaire_pz.py validate                   # verifier integrite
python glossaire_pz.py stats                      # statistiques
```

Python 3.8+ requis. Aucune dependance externe.

## Interface web

Ouvrir `index.html` dans un navigateur. Filtres par pilier, recherche instantanee, affichage des relations.

Egalement disponible en ligne : [glossaire-point-zero](https://virgil-libria.github.io/glossaire-point-zero/)

## Schema JSON

Chaque terme contient :

```json
{
  "id": "point-zero",
  "terme": "Point Zero",
  "definition_courte": "...",
  "definition": "...",
  "pilier": "PZ",
  "categorie": "ontologie",
  "relations": ["ether-fluidique", "unimultiplicite", "..."],
  "aliases": ["PZ", "..."]
}
```

Champs optionnels : `proprietes`, `tensor`, `tensor_category`, `excel_id`, `ile`, `type_lien_special`.

## Auteur

Virgil — Systeme Point Zero

## Licence

Ce travail est mis a disposition selon les termes de la licence [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
