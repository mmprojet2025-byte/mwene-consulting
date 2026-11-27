"""Tests du site vitrine (étapes 3 et 4)."""

import pytest
from markupsafe import escape  # le même échappement que Jinja (' devient &#39;)

from app.i18n import LANGUES, t

# Chaque page : (adresse après la langue, titre <title>, clé du <h1>)
PAGES = [
    ("", "Mwene Consulting — Apoio em RH para PME em Angola", "home_hero_title"),
    ("services", "Serviços — Mwene Consulting", "services_hero_title"),
    ("about", "Sobre — Mwene Consulting", "about_hero_title"),
    ("contact", "Contacto — Mwene Consulting", "contact_hero_title"),
    ("mentions-legales", "Menções legais — Mwene Consulting", "legal_title"),
    ("confidentialite", "Política de privacidade — Mwene Consulting", "privacy_title"),
]


def texte(cle, lang):
    """Le texte tel qu'il apparaît dans le HTML (apostrophes échappées par Jinja)."""
    return str(escape(t(cle, lang)))


def test_racine_redirige_vers_le_portugais(client):
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"] == "/pt/"


@pytest.mark.parametrize("lang", LANGUES)
@pytest.mark.parametrize("chemin, titre, cle_h1", PAGES)
def test_chaque_page_dans_chaque_langue(client, lang, chemin, titre, cle_h1):
    """6 pages × 3 langues = 18 combinaisons : 200, bon titre, bon <h1>, bonne langue."""
    response = client.get(f"/{lang}/{chemin}")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert f'<html dir="ltr" lang="{lang}">' in html
    assert f"<title>{titre}</title>" in html
    assert texte(cle_h1, lang) in html
    assert texte("nav_home", lang) in html  # en-tête traduit
    assert texte("footer_rights", lang) in html  # pied de page traduit


@pytest.mark.parametrize("chemin", ["mentions-legales", "confidentialite"])
def test_pages_legales_non_indexees(client, chemin):
    html = client.get(f"/pt/{chemin}").get_data(as_text=True)
    assert '<meta content="noindex, follow" name="robots"/>' in html
    assert 'name="description"' not in html


def test_selecteur_de_langue(client):
    """Sur /fr/, le bouton FR est actif et les liens mènent à /pt/ et /en/."""
    html = client.get("/fr/").get_data(as_text=True)
    assert 'href="/pt/"' in html
    assert 'href="/en/"' in html
    assert html.count('class="lang-btn active"') == 1


def test_selecteur_garde_la_page_et_le_service(client):
    html = client.get("/pt/contact?service=formacao").get_data(as_text=True)
    assert 'href="/fr/contact?service=formacao"' in html
    assert 'href="/en/contact?service=formacao"' in html


@pytest.mark.parametrize(
    "chemin, nom_lien",
    [("", "Home"), ("services", "Services"), ("about", "About"), ("contact", "Contact")],
)
def test_lien_actif_du_menu(client, chemin, nom_lien):
    html = client.get(f"/en/{chemin}").get_data(as_text=True)
    assert f'class="nav-link active" aria-current="page">{nom_lien}</a>' in html
    assert html.count("nav-link active") == 1


def test_ancres_des_services(client):
    html = client.get("/pt/services").get_data(as_text=True)
    for ancre in ("recrutamento", "organizacao-rh", "formacoes"):
        assert f'id="{ancre}"' in html


def test_liens_services_vers_contact_correspondent_au_select(client):
    """Les liens ?service=… de la page Services existent dans le <select> du contact."""
    services = client.get("/pt/services").get_data(as_text=True)
    contact = client.get("/pt/contact").get_data(as_text=True)
    for valeur in ("recrutamento", "organizacao-rh", "formacao"):
        assert f'href="/pt/contact?service={valeur}"' in services
        assert f'<option value="{valeur}">' in contact


def test_formulaire_contact(client):
    html = client.get("/fr/contact").get_data(as_text=True)
    assert 'data-formspree-id="YOUR_FORMSPREE_ID"' in html
    assert 'id="website"' in html  # honeypot
    for etat in ("form", "success", "error", "not-configured"):
        assert f'id="state-{etat}"' in html
    # Messages traduits transmis à main.js
    assert f'data-msg-required="{texte("contact_field_required", "fr")}"' in html


@pytest.mark.parametrize(
    "adresse, lang",
    [("/pt/page-inexistante", "pt"), ("/fr/page-inexistante", "fr"),
     ("/en/page-inexistante", "en"), ("/de/", "pt"), ("/rien/page", "pt")],
)
def test_page_404_personnalisee(client, adresse, lang):
    response = client.get(adresse)
    html = response.get_data(as_text=True)
    assert response.status_code == 404
    assert texte("notfound_title", lang) in html
    assert f'<html dir="ltr" lang="{lang}">' in html
    assert '<meta content="noindex, follow" name="robots"/>' in html


def test_css_et_js_servis(client):
    assert client.get("/static/css/style.css").status_code == 200
    assert client.get("/static/js/main.js").status_code == 200
