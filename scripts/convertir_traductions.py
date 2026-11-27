"""Conversion unique : js/translations.js -> translations/{pt,fr,en}.json

À lancer une seule fois depuis la racine du projet :
    python scripts/convertir_traductions.py

Le script lit le fichier JavaScript ligne par ligne. Il ne garde que les
lignes de la forme   cle: "valeur",   et les range dans la bonne langue.
Il s'arrête avec une erreur s'il trouve une ligne qu'il ne comprend pas,
une clé en double, ou des langues qui n'ont pas les mêmes clés.
"""

import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "js" / "translations.js"
DESTINATION = RACINE / "translations"
LANGUES = ("pt", "fr", "en")

# « pt: {»  -> début du bloc d'une langue
DEBUT_LANGUE = re.compile(r"^\s*(pt|fr|en): \{$")
# « nav_home: "Início", »  -> une traduction
LIGNE_CLE = re.compile(r'^\s*([a-z0-9_]+): "([^"\\]*)",?$')
# Lignes sans intérêt : vides, commentaires, accolades de fin de bloc
LIGNE_IGNOREE = re.compile(r"^\s*(//.*)?$|^\s*\},?$")


def lire_traductions():
    traductions = {}
    langue = None

    for numero, ligne in enumerate(SOURCE.read_text(encoding="utf-8").splitlines(), 1):
        if ligne.startswith("const TRANSLATIONS"):
            langue = "debut"
            continue
        if langue is None:
            continue  # en-tête du fichier, avant l'objet TRANSLATIONS
        if ligne.startswith("};"):
            break  # fin de l'objet : la suite est le moteur i18n

        debut = DEBUT_LANGUE.match(ligne)
        if debut:
            langue = debut.group(1)
            traductions[langue] = {}
            continue

        cle_valeur = LIGNE_CLE.match(ligne)
        if cle_valeur:
            cle, valeur = cle_valeur.groups()
            if cle in traductions[langue]:
                sys.exit(f"Ligne {numero} : clé « {cle} » en double en {langue}.")
            traductions[langue][cle] = valeur
            continue

        if LIGNE_IGNOREE.match(ligne):
            continue

        sys.exit(f"Ligne {numero} non comprise : {ligne!r}")

    return traductions


def verifier(traductions):
    if tuple(traductions) != LANGUES:
        sys.exit(f"Langues trouvées : {list(traductions)}, attendues : {list(LANGUES)}")
    cles_pt = set(traductions["pt"])
    for langue in ("fr", "en"):
        cles = set(traductions[langue])
        if cles != cles_pt:
            sys.exit(
                f"{langue} n'a pas les mêmes clés que pt.\n"
                f"  Manquantes : {sorted(cles_pt - cles)}\n"
                f"  En trop : {sorted(cles - cles_pt)}"
            )


def ecrire(traductions):
    DESTINATION.mkdir(exist_ok=True)
    for langue, valeurs in traductions.items():
        chemin = DESTINATION / f"{langue}.json"
        # ensure_ascii=False garde les accents lisibles (« Início » et non « Início »).
        texte = json.dumps(valeurs, ensure_ascii=False, indent=2) + "\n"
        chemin.write_text(texte, encoding="utf-8")
        print(f"{chemin.relative_to(RACINE)} : {len(valeurs)} clés")


if __name__ == "__main__":
    resultat = lire_traductions()
    verifier(resultat)
    ecrire(resultat)
