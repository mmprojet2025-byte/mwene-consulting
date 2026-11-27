"""Traductions côté serveur.

Les textes sont rangés dans translations/pt.json, fr.json et en.json,
avec exactement les mêmes clés dans les trois fichiers.
"""

import json
from pathlib import Path

from flask import g, request, url_for

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

    Même comportement que t() dans la v1 (js/translations.js, branche main) :
    1. le texte dans la langue demandée ;
    2. sinon le texte en portugais ;
    3. sinon la clé elle-même (on voit tout de suite qu'il manque une traduction).
    """
    return (
        TRADUCTIONS.get(langue, {}).get(cle)
        or TRADUCTIONS[LANGUE_PAR_DEFAUT].get(cle)
        or cle
    )


def t_template(cle, langue=None):
    """Version de t() pour les templates.

    Sans langue précisée, on prend celle de la page en cours (g.lang,
    lue dans l'URL par le blueprint), sinon le portugais.
    """
    return t(cle, langue or g.get("lang", LANGUE_PAR_DEFAUT))


def url_pour_langue(langue):
    """Adresse de la page en cours dans une autre langue (pour le sélecteur PT/FR/EN).

    /fr/contact?service=formacao -> /en/contact?service=formacao par exemple :
    les paramètres après « ? » sont gardés, comme dans la v1.
    Si la page en cours n'est pas connue (page d'erreur), on renvoie vers
    l'accueil de cette langue.
    """
    if request.endpoint and request.view_args is not None:
        parametres = {**request.args.to_dict(), **request.view_args, "lang": langue}
        return url_for(request.endpoint, **parametres)
    return url_for("vitrine.accueil", lang=langue)


def url_canonique(langue):
    """Adresse complète et « propre » de la page en cours dans une langue.

    Sert aux balises canonical et hreflang : /pt/contact?service=formacao
    donne http://domaine/fr/contact pour langue="fr". Les paramètres après
    « ? » sont retirés, pour que les moteurs de recherche ne voient qu'une
    adresse par page et par langue. Le domaine est celui de la requête :
    rien n'est écrit en dur.
    """
    return url_for(request.endpoint, **request.view_args, lang=langue, _external=True)
