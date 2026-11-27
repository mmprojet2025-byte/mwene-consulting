"""Traductions côté serveur.

Les textes sont rangés dans translations/pt.json, fr.json et en.json,
avec exactement les mêmes clés dans les trois fichiers.
"""

import json
from pathlib import Path

LANGUES = ("pt", "fr", "en")
LANGUE_PAR_DEFAUT = "pt"

DOSSIER_TRADUCTIONS = Path(__file__).resolve().parent.parent / "translations"


def charger_traductions():
    """Lit les trois fichiers JSON et renvoie {"pt": {...}, "fr": {...}, "en": {...}}."""
    traductions = {}
    for langue in LANGUES:
        chemin = DOSSIER_TRADUCTIONS / f"{langue}.json"
        traductions[langue] = json.loads(chemin.read_text(encoding="utf-8"))
    return traductions


# Lu une seule fois, au démarrage de l'application.
TRADUCTIONS = charger_traductions()


def t(cle, langue=LANGUE_PAR_DEFAUT):
    """Renvoie le texte de « cle » dans « langue ».

    Même comportement que t() dans js/translations.js :
    1. le texte dans la langue demandée ;
    2. sinon le texte en portugais ;
    3. sinon la clé elle-même (on voit tout de suite qu'il manque une traduction).
    """
    return (
        TRADUCTIONS.get(langue, {}).get(cle)
        or TRADUCTIONS[LANGUE_PAR_DEFAUT].get(cle)
        or cle
    )
