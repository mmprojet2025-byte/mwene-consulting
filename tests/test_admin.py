"""Tests de l'administration Mwene : entreprises et comptes clients (étape 9)."""

import re

import pytest
from markupsafe import escape

from app.i18n import LANGUES, t
from app.models import Company, Country, User, ajouter_pays_initiaux, db

ADMIN = "admin@mwene.test"
CLIENT = "rh@client.test"
MOT_DE_PASSE = "mot-de-passe-de-test"  # valeur factice


def texte(cle, lang="pt"):
    return str(escape(t(cle, lang)))


@pytest.fixture
def comptes(app):
    """Angola + un administrateur Mwene + une entreprise cliente avec un compte."""
    with app.app_context():
        ajouter_pays_initiaux()
        angola = db.session.execute(db.select(Country).filter_by(code="AO")).scalar_one()
        entreprise = Company(nom="Entreprise Cliente", country=angola)
        admin = User(email=ADMIN, is_admin=True)
        client = User(email=CLIENT, company=entreprise)
        for compte in (admin, client):
            compte.set_password(MOT_DE_PASSE)
        db.session.add_all([entreprise, admin, client])
        db.session.commit()
        return {"angola": angola.id, "entreprise": entreprise.id}


def jeton(client, adresse):
    """Récupère le jeton CSRF dans la page, comme le ferait un navigateur."""
    html = client.get(adresse).get_data(as_text=True)
    return re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', html).group(1)


def se_connecter(client, email, mot_de_passe=MOT_DE_PASSE, lang="pt"):
    adresse = f"/{lang}/espace/connexion"
    return client.post(
        adresse,
        data={"email": email, "mot_de_passe": mot_de_passe, "csrf_token": jeton(client, adresse)},
    )


def poster(client, chemin, donnees, lang="pt"):
    """Envoie un formulaire d'administration avec un jeton CSRF valide."""
    donnees = {**donnees, "csrf_token": jeton(client, f"/{lang}/espace/tableau-de-bord")}
    return client.post(f"/{lang}/espace/admin/{chemin}", data=donnees)


def nombre(app, modele):
    with app.app_context():
        return len(db.session.execute(db.select(modele)).scalars().all())


# --- Qui peut accéder ? ---------------------------------------------------------


def test_sans_connexion_redirige_vers_la_connexion(client, comptes):
    response = client.get("/pt/espace/admin")
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/pt/espace/connexion")


@pytest.mark.parametrize("lang", LANGUES)
def test_compte_client_recoit_403(client, comptes, lang):
    se_connecter(client, CLIENT, lang=lang)
    response = client.get(f"/{lang}/espace/admin")
    html = response.get_data(as_text=True)
    assert response.status_code == 403
    assert texte("espace_forbidden_title", lang) in html
    assert texte("espace_forbidden_text", lang) in html
    assert f'href="/{lang}/espace/tableau-de-bord"' in html


def test_compte_client_ne_peut_rien_creer(app, client, comptes):
    """Même en envoyant les formulaires directement : 403 et rien n'est enregistré."""
    se_connecter(client, CLIENT)
    entreprises, utilisateurs = nombre(app, Company), nombre(app, User)

    reponse = poster(client, "entreprises", {"nom": "Pirate", "pays": comptes["angola"]})
    assert reponse.status_code == 403
    reponse = poster(
        client,
        "utilisateurs",
        {"entreprise": comptes["entreprise"], "email": "intrus@client.test", "mot_de_passe": MOT_DE_PASSE},
    )
    assert reponse.status_code == 403

    assert nombre(app, Company) == entreprises
    assert nombre(app, User) == utilisateurs


@pytest.mark.parametrize("lang", LANGUES)
def test_admin_voit_la_page(client, comptes, lang):
    se_connecter(client, ADMIN, lang=lang)
    response = client.get(f"/{lang}/espace/admin")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert f"<title>{texte('meta_title_admin', lang)}</title>" in html
    assert "Entreprise Cliente" in html
    assert CLIENT in html
    assert f"{t('country_ao', lang)} (AO, AOA)" in html
    assert html.count('name="csrf_token"') == 2
    assert '<meta content="noindex, nofollow" name="robots"/>' in html


def test_lien_administration_seulement_pour_les_admins(client, comptes):
    se_connecter(client, CLIENT)
    assert 'href="/pt/espace/admin"' not in client.get("/pt/espace/tableau-de-bord").get_data(as_text=True)
    client.post("/pt/espace/deconnexion", data={"csrf_token": jeton(client, "/pt/espace/tableau-de-bord")})

    se_connecter(client, ADMIN)
    assert 'href="/pt/espace/admin"' in client.get("/pt/espace/tableau-de-bord").get_data(as_text=True)


# --- Parcours complet (la vérification « navigateur » du plan) ------------------


def test_creer_entreprise_puis_compte_puis_se_connecter(app, client, comptes):
    se_connecter(client, ADMIN)

    reponse = poster(client, "entreprises", {"nom": "  Nova Empresa  ", "pays": comptes["angola"]})
    assert reponse.status_code == 302
    assert reponse.headers["Location"] == "/pt/espace/admin"
    page = client.get("/pt/espace/admin").get_data(as_text=True)
    assert texte("admin_company_created") in page
    assert "Nova Empresa" in page

    with app.app_context():
        nova = db.session.execute(db.select(Company).filter_by(nom="Nova Empresa")).scalar_one()
        assert nova.country.code == "AO"
        id_nova = nova.id

    reponse = poster(
        client,
        "utilisateurs",
        {"entreprise": id_nova, "email": "Ana@Nova.test", "mot_de_passe": "palavra-passe-da-ana"},
    )
    assert reponse.status_code == 302
    assert texte("admin_user_created") in client.get("/pt/espace/admin").get_data(as_text=True)

    with app.app_context():
        ana = db.session.execute(db.select(User).filter_by(email="ana@nova.test")).scalar_one()
        assert ana.company_id == id_nova
        assert ana.is_admin is False

    # Le nouveau compte peut se connecter (dans un autre « navigateur »).
    autre_navigateur = app.test_client()
    reponse = se_connecter(autre_navigateur, "ana@nova.test", "palavra-passe-da-ana")
    assert reponse.headers["Location"] == "/pt/espace/tableau-de-bord"
    assert "ana@nova.test" in autre_navigateur.get("/pt/espace/tableau-de-bord").get_data(as_text=True)


def test_impossible_de_creer_un_admin_par_le_formulaire(app, client, comptes):
    se_connecter(client, ADMIN)
    poster(
        client,
        "utilisateurs",
        {"entreprise": comptes["entreprise"], "email": "faux-admin@client.test",
         "mot_de_passe": MOT_DE_PASSE, "is_admin": "1"},
    )
    with app.app_context():
        compte = db.session.execute(db.select(User).filter_by(email="faux-admin@client.test")).scalar_one()
        assert compte.is_admin is False


# --- Erreurs de saisie : refusées, rien n'est enregistré -------------------------


@pytest.mark.parametrize(
    "donnees, cle_erreur",
    [
        ({"nom": "   ", "pays": "ANGOLA"}, "admin_error_company_name"),
        ({"nom": "Sans Pays", "pays": "999"}, "admin_error_country"),
        ({"nom": "Sans Pays", "pays": "pas-un-nombre"}, "admin_error_country"),
        ({"nom": "Sans Pays"}, "admin_error_country"),
    ],
)
def test_entreprise_invalide_refusee(app, client, comptes, donnees, cle_erreur):
    se_connecter(client, ADMIN)
    avant = nombre(app, Company)
    reponse = poster(client, "entreprises", donnees)
    assert reponse.status_code == 400
    assert texte(cle_erreur) in reponse.get_data(as_text=True)
    assert nombre(app, Company) == avant


@pytest.mark.parametrize(
    "modifs, cle_erreur",
    [
        ({"entreprise": "999"}, "admin_error_company"),
        ({"entreprise": ""}, "admin_error_company"),
        ({"email": "pas-un-email"}, "admin_error_email_invalid"),
        ({"email": CLIENT}, "admin_error_email_taken"),
        ({"email": "RH@Client.TEST"}, "admin_error_email_taken"),
        ({"email": ADMIN}, "admin_error_email_taken"),
        ({"mot_de_passe": "court"}, "admin_error_password_short"),
    ],
)
def test_compte_invalide_refuse(app, client, comptes, modifs, cle_erreur):
    se_connecter(client, ADMIN)
    donnees = {"entreprise": comptes["entreprise"], "email": "nouveau@client.test",
               "mot_de_passe": "mot-de-passe-secret-42", **modifs}
    avant = nombre(app, User)

    reponse = poster(client, "utilisateurs", donnees)
    html = reponse.get_data(as_text=True)
    assert reponse.status_code == 400
    assert texte(cle_erreur).replace("{min}", "12") in html
    assert donnees["mot_de_passe"] not in html  # jamais renvoyé dans la page
    assert nombre(app, User) == avant
    # La page reste utilisable : aucune donnée invalide n'est restée dans la session.
    assert client.get("/pt/espace/admin").status_code == 200
    assert nombre(app, User) == avant


def test_message_mot_de_passe_court_indique_le_minimum(client, comptes):
    se_connecter(client, ADMIN, lang="fr")
    reponse = poster(
        client, "utilisateurs",
        {"entreprise": comptes["entreprise"], "email": "x@client.test", "mot_de_passe": "court"}, lang="fr",
    )
    assert "Le mot de passe doit contenir au moins 12 caractères." in reponse.get_data(as_text=True)


# --- CSRF -------------------------------------------------------------------------


@pytest.mark.parametrize("chemin", ["entreprises", "utilisateurs"])
def test_formulaires_admin_sans_jeton_refuses(app, client, comptes, chemin):
    se_connecter(client, ADMIN)
    avant = (nombre(app, Company), nombre(app, User))
    reponse = client.post(
        f"/pt/espace/admin/{chemin}",
        data={"nom": "Sans Jeton", "pays": comptes["angola"], "entreprise": comptes["entreprise"],
              "email": "sans-jeton@client.test", "mot_de_passe": MOT_DE_PASSE},
    )
    assert reponse.status_code == 400
    assert texte("espace_csrf_title") in reponse.get_data(as_text=True)
    assert (nombre(app, Company), nombre(app, User)) == avant
