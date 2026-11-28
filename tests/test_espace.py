"""Tests de l'Espace Recrutement : connexion, déconnexion, CSRF, limite de tentatives (étape 8)."""

import re

import pytest
from markupsafe import escape

from app import securite
from app.i18n import LANGUES, t
from app.models import User, db

EMAIL = "rh@mwene.test"
MOT_DE_PASSE = "mot-de-passe-de-test"  # valeur factice


def texte(cle, lang):
    """Le texte tel qu'il apparaît dans le HTML (apostrophes échappées par Jinja)."""
    return str(escape(t(cle, lang)))


@pytest.fixture
def compte(app):
    """Un compte administrateur en base (le plus simple : pas besoin d'entreprise)."""
    with app.app_context():
        admin = User(email=EMAIL, is_admin=True)
        admin.set_password(MOT_DE_PASSE)
        db.session.add(admin)
        db.session.commit()


def jeton(client, adresse="/pt/espace/connexion"):
    """Récupère le jeton CSRF dans la page, comme le ferait un navigateur."""
    html = client.get(adresse).get_data(as_text=True)
    return re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', html).group(1)


def se_connecter(client, email=EMAIL, mot_de_passe=MOT_DE_PASSE, lang="pt", adresse=None):
    adresse = adresse or f"/{lang}/espace/connexion"
    return client.post(
        adresse,
        data={"email": email, "mot_de_passe": mot_de_passe, "csrf_token": jeton(client, f"/{lang}/espace/connexion")},
    )


# --- Page de connexion ---------------------------------------------------------


@pytest.mark.parametrize("lang", LANGUES)
def test_page_de_connexion(client, lang):
    response = client.get(f"/{lang}/espace/connexion")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert f"<title>{texte('meta_title_login', lang)}</title>" in html
    assert texte("espace_login_title", lang) in html
    assert 'name="csrf_token"' in html
    # Espace privé : non indexé, sans canonical ni hreflang.
    assert '<meta content="noindex, nofollow" name="robots"/>' in html
    assert 'rel="canonical"' not in html


def test_langue_inconnue_404(client):
    assert client.get("/de/espace/connexion").status_code == 404


# --- Connexion -----------------------------------------------------------------


def test_connexion_reussie(client, compte):
    response = se_connecter(client)
    assert response.status_code == 302
    assert response.headers["Location"] == "/pt/espace/tableau-de-bord"

    tableau = client.get("/pt/espace/tableau-de-bord")
    assert tableau.status_code == 200
    assert EMAIL in tableau.get_data(as_text=True)


@pytest.mark.parametrize("lang", LANGUES)
def test_connexion_dans_chaque_langue(client, compte, lang):
    response = se_connecter(client, lang=lang)
    assert response.headers["Location"] == f"/{lang}/espace/tableau-de-bord"
    html = client.get(response.headers["Location"]).get_data(as_text=True)
    assert texte("espace_dashboard_title", lang) in html


def test_email_reconnu_en_majuscules(client, compte):
    assert se_connecter(client, email="  RH@Mwene.TEST ").status_code == 302


@pytest.mark.parametrize(
    "email, mot_de_passe",
    [(EMAIL, "mauvais-mot-de-passe"), ("inconnu@mwene.test", MOT_DE_PASSE), (EMAIL, "")],
)
def test_connexion_ratee_message_neutre(client, compte, email, mot_de_passe):
    """Même message, qu'il s'agisse de l'e-mail ou du mot de passe."""
    response = se_connecter(client, email=email, mot_de_passe=mot_de_passe)
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert texte("espace_login_error", "pt") in html
    # Toujours pas connecté :
    assert client.get("/pt/espace/tableau-de-bord").status_code == 302


def test_mot_de_passe_jamais_renvoye_dans_la_page(client, compte):
    html = se_connecter(client, mot_de_passe="secret-tape-par-erreur").get_data(as_text=True)
    assert "secret-tape-par-erreur" not in html
    assert f'value="{EMAIL}"' in html  # l'e-mail, lui, est gardé pour corriger la saisie


def test_email_inconnu_calcule_quand_meme_une_empreinte(app, monkeypatch):
    """Même temps de calcul que pour un mauvais mot de passe : on ne trahit pas les e-mails."""
    appels = []
    monkeypatch.setattr(securite, "check_password_hash", lambda *args: appels.append(args) or False)
    with app.app_context():
        assert securite.verifier_identifiants("inconnu@mwene.test", "nimporte-quoi-123") is None
    assert len(appels) == 1


def test_next_vers_un_autre_site_ignore(client, compte):
    response = se_connecter(client, adresse="/pt/espace/connexion?next=https://site-pirate.example/")
    assert response.headers["Location"] == "/pt/espace/tableau-de-bord"


def test_deja_connecte_redirige_vers_le_tableau_de_bord(client, compte):
    se_connecter(client)
    response = client.get("/pt/espace/connexion")
    assert response.status_code == 302
    assert response.headers["Location"] == "/pt/espace/tableau-de-bord"


# --- Tableau de bord protégé ---------------------------------------------------


@pytest.mark.parametrize("lang", LANGUES)
def test_tableau_de_bord_sans_connexion_redirige(client, lang):
    response = client.get(f"/{lang}/espace/tableau-de-bord")
    assert response.status_code == 302
    assert response.headers["Location"].startswith(f"/{lang}/espace/connexion")

    page = client.get(response.headers["Location"]).get_data(as_text=True)
    assert texte("espace_login_required", lang) in page


# --- Déconnexion ----------------------------------------------------------------


def test_deconnexion(client, compte):
    se_connecter(client)
    response = client.post(
        "/fr/espace/deconnexion", data={"csrf_token": jeton(client, "/fr/espace/tableau-de-bord")}
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/fr/espace/connexion"

    page = client.get("/fr/espace/connexion").get_data(as_text=True)
    assert texte("espace_logout_done", "fr") in page
    assert client.get("/fr/espace/tableau-de-bord").status_code == 302


def test_deconnexion_par_simple_lien_refusee(client, compte):
    se_connecter(client)
    assert client.get("/pt/espace/deconnexion").status_code == 405
    assert client.get("/pt/espace/tableau-de-bord").status_code == 200  # toujours connecté


# --- CSRF -----------------------------------------------------------------------


@pytest.mark.parametrize("lang", LANGUES)
def test_formulaire_sans_jeton_csrf_refuse(client, compte, lang):
    response = client.post(f"/{lang}/espace/connexion", data={"email": EMAIL, "mot_de_passe": MOT_DE_PASSE})
    html = response.get_data(as_text=True)
    assert response.status_code == 400
    assert texte("espace_csrf_title", lang) in html
    assert f'<html dir="ltr" lang="{lang}">' in html
    assert client.get(f"/{lang}/espace/tableau-de-bord").status_code == 302  # pas connecté


def test_deconnexion_sans_jeton_csrf_refusee(client, compte):
    se_connecter(client)
    assert client.post("/pt/espace/deconnexion").status_code == 400
    assert client.get("/pt/espace/tableau-de-bord").status_code == 200


# --- Limite de tentatives ------------------------------------------------------


@pytest.mark.parametrize("lang", LANGUES)
def test_sixieme_tentative_ratee_recoit_429(client, compte, lang):
    """5 tentatives par minute : les 5 premières sont traitées, la 6e est refusée."""
    for _ in range(5):
        response = se_connecter(client, mot_de_passe="mauvais-mot-de-passe", lang=lang)
        assert response.status_code == 200

    response = se_connecter(client, mot_de_passe="mauvais-mot-de-passe", lang=lang)
    html = response.get_data(as_text=True)
    assert response.status_code == 429
    assert texte("espace_too_many_title", lang) in html
    assert texte("espace_too_many_text", lang) in html


def test_meme_le_bon_mot_de_passe_est_bloque_apres_la_limite(client, compte):
    for _ in range(5):
        se_connecter(client, mot_de_passe="mauvais-mot-de-passe")
    assert se_connecter(client).status_code == 429


def test_afficher_la_page_ne_compte_pas(client, compte):
    for _ in range(10):
        assert client.get("/pt/espace/connexion").status_code == 200
    assert se_connecter(client).status_code == 302
