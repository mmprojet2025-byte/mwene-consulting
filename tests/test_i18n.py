"""Tests des traductions (étape 2)."""

import json

import pytest
from flask import render_template_string

from app import i18n
from app.i18n import DOSSIER_TRADUCTIONS, LANGUES, t


def lire_json(langue):
    chemin = DOSSIER_TRADUCTIONS / f"{langue}.json"
    return json.loads(chemin.read_text(encoding="utf-8"))


@pytest.mark.parametrize("langue", ["fr", "en"])
def test_memes_cles_que_le_portugais(langue):
    """Chaque fichier JSON a exactement les mêmes clés que pt.json."""
    assert set(lire_json(langue)) == set(lire_json("pt"))


@pytest.mark.parametrize("langue", LANGUES)
def test_aucune_valeur_vide(langue):
    """Aucun texte n'est vide."""
    vides = [cle for cle, valeur in lire_json(langue).items() if not valeur.strip()]
    assert vides == []


@pytest.mark.parametrize(
    "cle, langue, attendu",
    [
        # Valeurs recopiées de js/translations.js
        ("nav_home", "pt", "Início"),
        ("nav_home", "fr", "Accueil"),
        ("nav_home", "en", "Home"),
        ("footer_rights", "pt", "Todos os direitos reservados."),
        ("footer_rights", "fr", "Tous droits réservés."),
        ("notfound_btn", "fr", "Retour à l'accueil"),
        ("notfound_btn", "en", "Back to home"),
    ],
)
def test_valeurs_identiques_a_la_v1(cle, langue, attendu):
    assert t(cle, langue) == attendu


def test_langue_par_defaut_est_le_portugais():
    assert t("nav_home") == "Início"


def test_repli_sur_le_portugais(monkeypatch):
    """Si une clé manque en français, on affiche le texte portugais."""
    monkeypatch.delitem(i18n.TRADUCTIONS["fr"], "nav_home")
    assert t("nav_home", "fr") == "Início"


def test_langue_inconnue_repli_sur_le_portugais():
    assert t("nav_home", "de") == "Início"


def test_cle_inconnue_renvoie_la_cle():
    assert t("cle_qui_n_existe_pas", "fr") == "cle_qui_n_existe_pas"


def test_t_disponible_dans_les_templates(app):
    with app.app_context():
        assert render_template_string("{{ t('nav_home', 'fr') }}") == "Accueil"
