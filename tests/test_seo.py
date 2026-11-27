"""Tests du référencement (étape 5) : sitemap, robots.txt, titres traduits, hreflang."""

import xml.etree.ElementTree as ET

import pytest
from markupsafe import escape

from app.i18n import LANGUES, t

DOMAINE = "http://localhost"  # domaine utilisé par le client de test de Flask
PAGES_INDEXEES = ["", "services", "about", "contact"]
PAGES_NON_INDEXEES = ["mentions-legales", "confidentialite"]

# Espaces de noms XML du sitemap (préfixes des balises <url> et <xhtml:link>)
NS = {
    "s": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "xhtml": "http://www.w3.org/1999/xhtml",
}


def lire_sitemap(client):
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert response.mimetype == "application/xml"
    return ET.fromstring(response.data)  # échoue si le XML est mal formé


def test_sitemap_liste_chaque_page_dans_chaque_langue(client):
    """4 pages indexables × 3 langues = 12 adresses, ni plus ni moins."""
    racine = lire_sitemap(client)
    adresses = [loc.text for loc in racine.findall("s:url/s:loc", NS)]

    attendues = [f"{DOMAINE}/{lang}/{page}" for page in PAGES_INDEXEES for lang in LANGUES]
    assert sorted(adresses) == sorted(attendues)


def test_sitemap_chaque_adresse_a_ses_versions(client):
    """Chaque <url> annonce ses 3 langues + x-default (portugais)."""
    racine = lire_sitemap(client)
    for url in racine.findall("s:url", NS):
        page = url.find("s:loc", NS).text.split("/", 4)[4]  # « services », « » pour l'accueil
        liens = {
            lien.get("hreflang"): lien.get("href")
            for lien in url.findall("xhtml:link", NS)
        }
        attendus = {lang: f"{DOMAINE}/{lang}/{page}" for lang in LANGUES}
        attendus["x-default"] = f"{DOMAINE}/pt/{page}"
        assert liens == attendus


@pytest.mark.parametrize("page", PAGES_NON_INDEXEES)
def test_sitemap_sans_pages_non_indexees(client, page):
    assert page not in client.get("/sitemap.xml").get_data(as_text=True)


def test_robots_indique_le_sitemap(client):
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert response.mimetype == "text/plain"
    texte = response.get_data(as_text=True)
    assert "User-agent: *" in texte
    assert f"Sitemap: {DOMAINE}/sitemap.xml" in texte


def test_le_titre_change_selon_la_langue(client):
    titres = set()
    for lang in LANGUES:
        html = client.get(f"/{lang}/services").get_data(as_text=True)
        titre = str(escape(t("meta_title_services", lang)))
        assert f"<title>{titre}</title>" in html
        titres.add(titre)
    assert titres == {"Serviços — Mwene Consulting", "Services — Mwene Consulting"}


@pytest.mark.parametrize("lang", LANGUES)
def test_la_description_change_selon_la_langue(client, lang):
    html = client.get(f"/{lang}/contact").get_data(as_text=True)
    description = str(escape(t("meta_desc_contact", lang)))
    assert f'<meta content="{description}" name="description"/>' in html


def test_404_titre_traduit(client):
    html = client.get("/en/page-inexistante").get_data(as_text=True)
    assert "<title>Page not found — Mwene Consulting</title>" in html


@pytest.mark.parametrize("lang", LANGUES)
@pytest.mark.parametrize("page", PAGES_INDEXEES)
def test_canonical_et_hreflang(client, lang, page):
    html = client.get(f"/{lang}/{page}").get_data(as_text=True)
    assert f'<link href="{DOMAINE}/{lang}/{page}" rel="canonical"/>' in html
    for code in LANGUES:
        assert f'<link href="{DOMAINE}/{code}/{page}" hreflang="{code}" rel="alternate"/>' in html
    assert f'<link href="{DOMAINE}/pt/{page}" hreflang="x-default" rel="alternate"/>' in html


def test_canonical_sans_parametres(client):
    """?service=… ne fait pas partie de l'adresse officielle de la page."""
    html = client.get("/fr/contact?service=formacao").get_data(as_text=True)
    assert f'<link href="{DOMAINE}/fr/contact" rel="canonical"/>' in html
    assert f'href="{DOMAINE}/en/contact" hreflang="en"' in html


@pytest.mark.parametrize(
    "adresse", ["/pt/mentions-legales", "/fr/confidentialite", "/pt/page-inexistante", "/de/"]
)
def test_pas_de_hreflang_sur_les_pages_non_indexees(client, adresse):
    """Pas de <link> canonical/alternate dans le <head>.

    (Les liens PT/FR/EN du sélecteur de langue ont aussi un attribut hreflang,
    mais ce sont des <a>, présents sur toutes les pages : c'est normal.)
    """
    html = client.get(adresse).get_data(as_text=True)
    assert 'rel="alternate"' not in html
    assert 'rel="canonical"' not in html
