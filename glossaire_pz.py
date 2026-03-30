#!/usr/bin/env python3
"""
glossaire_pz.py — CLI pour le Glossaire du Systeme Point Zero
=============================================================
Usage:
    python glossaire_pz.py list                         # tous les termes
    python glossaire_pz.py list --pilier ETH            # filtrer par pilier
    python glossaire_pz.py list --categorie dynamique   # filtrer par categorie
    python glossaire_pz.py show point-zero              # afficher un terme
    python glossaire_pz.py search "ether"               # recherche floue
    python glossaire_pz.py concepts                     # noms uniquement (pour import)
    python glossaire_pz.py concepts --format json       # noms en JSON (pour cdt/pilot)
    python glossaire_pz.py export --format csv           # export CSV
    python glossaire_pz.py export --format md            # export Markdown
    python glossaire_pz.py validate                     # verifier integrite
    python glossaire_pz.py stats                        # statistiques
"""

import argparse
import csv
import io
import json
import sys
from pathlib import Path

GLOSSAIRE_PATH = Path(__file__).parent / "glossaire_pz.json"


def load_glossaire(path=None):
    p = Path(path) if path else GLOSSAIRE_PATH
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize(text):
    """Normalise pour recherche insensible aux accents/casse."""
    import unicodedata
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text


# ── Commandes ────────────────────────────────────────────────────────────────

def cmd_list(args, data):
    termes = data["termes"]
    if args.pilier:
        termes = [t for t in termes if t["pilier"] == args.pilier.upper()]
    if args.categorie:
        termes = [t for t in termes if t["categorie"] == args.categorie.lower()]

    if not termes:
        print("Aucun terme trouve.")
        return

    # Regrouper par pilier
    by_pilier = {}
    for t in termes:
        by_pilier.setdefault(t["pilier"], []).append(t)

    for pilier in sorted(by_pilier):
        print(f"\n── {pilier} ({len(by_pilier[pilier])}) ──")
        for t in sorted(by_pilier[pilier], key=lambda x: x["terme"]):
            cat = t["categorie"][:4]
            print(f"  {t['id']:<35} [{cat}]  {t['terme']}")

    print(f"\nTotal: {len(termes)} termes")


def cmd_show(args, data):
    terme_id = args.terme_id.lower()
    # Chercher par ID ou alias
    found = None
    for t in data["termes"]:
        if t["id"] == terme_id:
            found = t
            break
        if terme_id in [a.lower() for a in t.get("aliases", [])]:
            found = t
            break

    if not found:
        # Tentative de recherche floue
        norm_q = normalize(terme_id)
        for t in data["termes"]:
            if norm_q in normalize(t["terme"]) or norm_q in normalize(t["id"]):
                found = t
                break

    if not found:
        print(f"Terme '{terme_id}' non trouve. Essayez: glossaire_pz.py search \"{terme_id}\"")
        return

    t = found
    print(f"\n{'=' * 60}")
    print(f"  {t['terme']}")
    print(f"{'=' * 60}")
    print(f"  ID       : {t['id']}")
    print(f"  Pilier   : {t['pilier']}")
    print(f"  Categorie: {t['categorie']}")
    if t.get("aliases"):
        print(f"  Aliases  : {', '.join(t['aliases'])}")
    print(f"\n  {t['definition_courte']}")
    print(f"\n  {t['definition']}")
    if t.get("relations"):
        print(f"\n  Relations: {', '.join(t['relations'])}")
    if t.get("excel_id"):
        print(f"\n  Excel ID : {t['excel_id']}")
    if t.get("ile"):
        print(f"  Ile      : {t['ile']}")
    if t.get("proprietes"):
        props = "; ".join(f"{k}={v}" for k, v in t["proprietes"].items())
        print(f"  Proprietes: {props}")
    if t.get("type_lien_special"):
        print(f"  Lien special: {t['type_lien_special']}")
    if t.get("tensor"):
        ts = t["tensor"]
        cat = t.get("tensor_category", "?")
        print(f"\n  Tenseur AURERABIDE [{cat}]:")
        print(f"    Security={ts['security']}  Coherence={ts['coherence']}  Resonance={ts['resonance']}")
        print(f"    Saturation={ts['saturation']}  Dimension_F={ts['dimension_f']}")
    print()


def cmd_search(args, data):
    query = normalize(args.query)
    results = []
    for t in data["termes"]:
        score = 0
        # Recherche dans terme, aliases, definitions
        if query in normalize(t["terme"]):
            score += 10
        if query in normalize(t["id"]):
            score += 8
        for alias in t.get("aliases", []):
            if query in normalize(alias):
                score += 6
        if query in normalize(t["definition_courte"]):
            score += 3
        if query in normalize(t["definition"]):
            score += 1
        if score > 0:
            results.append((score, t))

    results.sort(key=lambda x: -x[0])

    if not results:
        print(f"Aucun resultat pour '{args.query}'.")
        return

    print(f"\n{len(results)} resultat(s) pour '{args.query}':\n")
    for score, t in results[:20]:
        print(f"  [{t['pilier']:<10}] {t['terme']:<40} {t['definition_courte'][:60]}")


def cmd_concepts(args, data):
    termes = data["termes"]
    if args.pilier:
        termes = [t for t in termes if t["pilier"] == args.pilier.upper()]

    names = []
    for t in termes:
        names.append(t["terme"])
        for alias in t.get("aliases", []):
            if alias not in names and alias != t["terme"]:
                names.append(alias)

    names.sort()

    if args.format == "json":
        print(json.dumps(names, ensure_ascii=False, indent=2))
    elif args.format == "python":
        print("CONCEPTS = [")
        for n in names:
            print(f'    "{n}",')
        print("]")
    else:
        for n in names:
            print(n)


def cmd_export(args, data):
    termes = data["termes"]

    if args.format == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            "id", "terme", "pilier", "categorie", "definition_courte",
            "definition", "aliases", "relations"
        ])
        writer.writeheader()
        for t in termes:
            writer.writerow({
                "id": t["id"],
                "terme": t["terme"],
                "pilier": t["pilier"],
                "categorie": t["categorie"],
                "definition_courte": t["definition_courte"],
                "definition": t["definition"],
                "aliases": "; ".join(t.get("aliases", [])),
                "relations": "; ".join(t.get("relations", []))
            })
        print(output.getvalue())

    elif args.format == "md":
        by_pilier = {}
        for t in termes:
            by_pilier.setdefault(t["pilier"], []).append(t)

        print("# Glossaire du Systeme Point Zero\n")
        print(f"*{len(termes)} termes*\n")
        for pilier in sorted(by_pilier):
            print(f"\n## {pilier}\n")
            for t in sorted(by_pilier[pilier], key=lambda x: x["terme"]):
                print(f"### {t['terme']}")
                if t.get("aliases"):
                    print(f"*Aliases : {', '.join(t['aliases'])}*")
                print(f"\n{t['definition']}\n")
                if t.get("relations"):
                    print(f"**Relations** : {', '.join(t['relations'])}\n")

    else:
        print(json.dumps(termes, ensure_ascii=False, indent=2))


def cmd_validate(args, data):
    termes = data["termes"]
    ids = {t["id"] for t in termes}
    errors = []
    warnings = []

    for t in termes:
        # Verifier les relations pointent vers des IDs existants
        for rel in t.get("relations", []):
            if rel not in ids:
                errors.append(f"  [ERREUR] {t['id']} -> relation '{rel}' inexistante")

        # Verifier les champs requis
        for field in ["id", "terme", "definition_courte", "definition", "pilier", "categorie"]:
            if not t.get(field):
                errors.append(f"  [ERREUR] {t['id']} -> champ '{field}' manquant")

        # Verifier les relations bidirectionnelles
        for rel in t.get("relations", []):
            if rel in ids:
                rel_terme = next((x for x in termes if x["id"] == rel), None)
                if rel_terme and t["id"] not in rel_terme.get("relations", []):
                    warnings.append(f"  [WARN]   {t['id']} -> {rel} (pas de lien retour)")

    # Verifier doublons d'ID
    seen = set()
    for t in termes:
        if t["id"] in seen:
            errors.append(f"  [ERREUR] ID duplique: {t['id']}")
        seen.add(t["id"])

    print(f"\nValidation: {len(termes)} termes, {len(ids)} IDs uniques")
    print(f"  Piliers  : {sorted(set(t['pilier'] for t in termes))}")
    print(f"  Categories: {sorted(set(t['categorie'] for t in termes))}")

    if errors:
        print(f"\n{len(errors)} erreur(s):")
        for e in errors:
            print(e)
    else:
        print("\n  Aucune erreur.")

    if warnings:
        print(f"\n{len(warnings)} avertissement(s) (relations unidirectionnelles):")
        for w in warnings[:10]:
            print(w)
        if len(warnings) > 10:
            print(f"  ... et {len(warnings) - 10} autres")
    print()


def cmd_stats(args, data):
    termes = data["termes"]

    by_pilier = {}
    by_cat = {}
    total_relations = 0
    for t in termes:
        by_pilier[t["pilier"]] = by_pilier.get(t["pilier"], 0) + 1
        by_cat[t["categorie"]] = by_cat.get(t["categorie"], 0) + 1
        total_relations += len(t.get("relations", []))

    print(f"\n{'=' * 40}")
    print(f"  Glossaire PZ — Statistiques")
    print(f"{'=' * 40}")
    print(f"  Version : {data.get('version', '?')}")
    print(f"  Date    : {data.get('date', '?')}")
    print(f"  Termes  : {len(termes)}")
    print(f"  Relations: {total_relations} ({total_relations / len(termes):.1f} moy/terme)")

    print(f"\n  Par pilier:")
    for p in sorted(by_pilier, key=lambda x: -by_pilier[x]):
        bar = "#" * by_pilier[p]
        print(f"    {p:<12} {by_pilier[p]:>3}  {bar}")

    print(f"\n  Par categorie:")
    for c in sorted(by_cat, key=lambda x: -by_cat[x]):
        bar = "#" * by_cat[c]
        print(f"    {c:<14} {by_cat[c]:>3}  {bar}")
    print()


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Glossaire du Systeme Point Zero",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--glossaire", help="Chemin vers glossaire_pz.json")
    sub = parser.add_subparsers(dest="command")

    # list
    p_list = sub.add_parser("list", help="Lister les termes")
    p_list.add_argument("--pilier", help="Filtrer par pilier (PZ, ETH, GQ...)")
    p_list.add_argument("--categorie", help="Filtrer par categorie")

    # show
    p_show = sub.add_parser("show", help="Afficher un terme")
    p_show.add_argument("terme_id", help="ID ou nom du terme")

    # search
    p_search = sub.add_parser("search", help="Rechercher")
    p_search.add_argument("query", help="Terme de recherche")

    # concepts
    p_concepts = sub.add_parser("concepts", help="Liste des noms de concepts (pour import)")
    p_concepts.add_argument("--format", choices=["text", "json", "python"], default="text")
    p_concepts.add_argument("--pilier", help="Filtrer par pilier")

    # export
    p_export = sub.add_parser("export", help="Exporter le glossaire")
    p_export.add_argument("--format", choices=["json", "csv", "md"], default="json")

    # validate
    sub.add_parser("validate", help="Verifier l'integrite du glossaire")

    # stats
    sub.add_parser("stats", help="Statistiques du glossaire")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    data = load_glossaire(args.glossaire)

    commands = {
        "list": cmd_list,
        "show": cmd_show,
        "search": cmd_search,
        "concepts": cmd_concepts,
        "export": cmd_export,
        "validate": cmd_validate,
        "stats": cmd_stats,
    }
    commands[args.command](args, data)


if __name__ == "__main__":
    main()
