"""Tests du site vitrine (étape 3 : gabarit commun + page d'accueil)."""

from html import escape

import pytest

from app.i18n import t


def test_racine_redirige_vers_le_portugais(client):
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"] == "/pt/"


@pytest.mark.parametrize("lang", ["pt", "fr", "en"])
def test_accueil_dans_chaque_langue(client, lang):
    """/pt/, /fr/, /en/ répondent 200, avec le bon titre et le texte dans la bonne langue."""
    response = client.get(f"/{lang}/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert f'<html dir="ltr" lang="{lang}">' in html
    assert "<title>Mwene Consulting — Apoio em RH para PME em Angola</title>" in html
    assert escape(t("home_hero_title", lang), quote=False) in html
    assert escape(t("nav_home", lang), quote=False) in html


def test_langue_inconnue_404(client):
    assert client.get("/de/").status_code == 404


def test_selecteur_de_langue(client):
    """Sur /fr/, le bouton FR est actif et les liens mènent à /pt/ et /en/."""
    html = client.get("/fr/").get_data(as_text=True)
    assert 'href="/pt/"' in html
    assert 'href="/en/"' in html
    assert 'class="lang-btn active"' in html
    assert html.count('class="lang-btn active"') == 1


def test_lien_accueil_actif(client):
    html = client.get("/en/").get_data(as_text=True)
    assert 'class="nav-link active" aria-current="page">Home</a>' in html


def test_css_et_js_servis(client):
    assert client.get("/static/css/style.css").status_code == 200
    assert client.get("/static/js/main.js").status_code == 200
