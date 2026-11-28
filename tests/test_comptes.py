"""Tests des entreprises, des comptes et des mots de passe (étape 7)."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Company, Country, User, ajouter_pays_initiaux, db

MOT_DE_PASSE = "mot-de-passe-de-test"  # valeur factice, 20 caractères


@pytest.fixture
def contexte(app):
    """Contexte d'application + Angola en base (nécessaire pour créer une entreprise)."""
    with app.app_context():
        ajouter_pays_initiaux()
        yield


@pytest.fixture
def entreprise(contexte):
    angola = db.session.execute(db.select(Country).filter_by(code="AO")).scalar_one()
    entreprise = Company(nom="Entreprise Test", country=angola)
    db.session.add(entreprise)
    db.session.commit()
    return entreprise


def nouveau_compte(email, entreprise=None, is_admin=False, mot_de_passe=MOT_DE_PASSE):
    compte = User(email=email, company=entreprise, is_admin=is_admin)
    compte.set_password(mot_de_passe)
    return compte


# --- Mots de passe -------------------------------------------------------------


def test_l_empreinte_est_differente_du_mot_de_passe():
    compte = nouveau_compte("ana@exemple.com", is_admin=True)
    assert compte.password_hash != MOT_DE_PASSE
    assert MOT_DE_PASSE not in compte.password_hash
    assert compte.password_hash.startswith("scrypt:")


def test_check_password_accepte_le_bon_et_refuse_le_mauvais():
    compte = nouveau_compte("ana@exemple.com", is_admin=True)
    assert compte.check_password(MOT_DE_PASSE) is True
    assert compte.check_password("mauvais-mot-de-passe") is False
    assert compte.check_password("") is False
    assert compte.check_password(None) is False


def test_compte_sans_mot_de_passe_refuse_toute_connexion():
    assert User(email="ana@exemple.com").check_password(MOT_DE_PASSE) is False


def test_meme_mot_de_passe_empreintes_differentes():
    """Grâce au « sel » aléatoire, deux empreintes du même mot de passe diffèrent."""
    a = nouveau_compte("a@exemple.com", is_admin=True)
    b = nouveau_compte("b@exemple.com", is_admin=True)
    assert a.password_hash != b.password_hash


@pytest.mark.parametrize("trop_court", ["", "court", "11-caracter"])
def test_mot_de_passe_trop_court_refuse(trop_court):
    with pytest.raises(ValueError):
        User(email="ana@exemple.com").set_password(trop_court)


def test_repr_sans_empreinte():
    compte = nouveau_compte("ana@exemple.com", is_admin=True)
    assert compte.password_hash not in repr(compte)


# --- E-mails -------------------------------------------------------------------


def test_email_normalise():
    assert User(email="  Ana@Exemple.COM ").email == "ana@exemple.com"


@pytest.mark.parametrize("email", ["", "ana", "ana@", "@exemple.com", "ana@exemple", "a b@exemple.com"])
def test_email_invalide_refuse(email):
    with pytest.raises(ValueError):
        User(email=email)


@pytest.mark.parametrize("deuxieme", ["ana@exemple.com", "ANA@Exemple.com"])
def test_un_email_ne_sert_qu_une_fois(contexte, deuxieme):
    db.session.add(nouveau_compte("ana@exemple.com", is_admin=True))
    db.session.commit()
    db.session.add(nouveau_compte(deuxieme, is_admin=True))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


# --- Entreprises et rattachement -----------------------------------------------


def test_entreprise_rattachee_a_un_pays(entreprise):
    assert entreprise.country.code == "AO"


def test_nom_d_entreprise_obligatoire(contexte):
    with pytest.raises(ValueError):
        Company(nom="   ")


def test_compte_client_rattache_a_son_entreprise(entreprise):
    compte = nouveau_compte("rh@entreprise.ao", entreprise=entreprise)
    db.session.add(compte)
    db.session.commit()
    assert compte.company is entreprise
    assert entreprise.users == [compte]
    assert compte.is_admin is False


def test_compte_client_sans_entreprise_refuse(contexte):
    db.session.add(nouveau_compte("rh@entreprise.ao"))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_entreprise_inexistante_refusee(contexte):
    """Les clés étrangères sont vérifiées : pas de rattachement à une entreprise fantôme."""
    compte = nouveau_compte("rh@entreprise.ao")
    compte.company_id = 999
    db.session.add(compte)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_pays_inexistant_refuse(contexte):
    db.session.add(Company(nom="Fantôme", country_id=999))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


# --- Commande flask create-admin ----------------------------------------------


def lancer_create_admin(app, email, saisie):
    return app.test_cli_runner().invoke(args=["create-admin", "--email", email], input=saisie)


def comptes(app):
    with app.app_context():
        return db.session.execute(db.select(User)).scalars().all()


def test_create_admin(app):
    resultat = lancer_create_admin(app, "Admin@Mwene.test", f"{MOT_DE_PASSE}\n{MOT_DE_PASSE}\n")
    assert resultat.exit_code == 0, resultat.output
    assert "Administrateur créé : admin@mwene.test" in resultat.output
    assert MOT_DE_PASSE not in resultat.output  # le mot de passe n'est jamais affiché

    with app.app_context():
        admin = db.session.execute(db.select(User)).scalar_one()
        assert admin.email == "admin@mwene.test"
        assert admin.is_admin is True
        assert admin.company is None
        assert admin.check_password(MOT_DE_PASSE)


def test_create_admin_email_deja_pris(app):
    lancer_create_admin(app, "admin@mwene.test", f"{MOT_DE_PASSE}\n{MOT_DE_PASSE}\n")
    resultat = lancer_create_admin(app, "ADMIN@mwene.test", f"{MOT_DE_PASSE}\n{MOT_DE_PASSE}\n")
    assert resultat.exit_code == 1
    assert "existe déjà" in resultat.output
    assert len(comptes(app)) == 1


def test_create_admin_confirmation_differente(app):
    """Si la confirmation diffère, click redemande ; sans nouvelle saisie, rien n'est créé."""
    resultat = lancer_create_admin(app, "admin@mwene.test", f"{MOT_DE_PASSE}\nautre-chose-123\n")
    assert resultat.exit_code != 0
    assert comptes(app) == []


def test_create_admin_mot_de_passe_trop_court(app):
    resultat = lancer_create_admin(app, "admin@mwene.test", "court\ncourt\n")
    assert resultat.exit_code == 1
    assert "au moins 12 caractères" in resultat.output
    assert comptes(app) == []


def test_create_admin_email_invalide(app):
    resultat = lancer_create_admin(app, "pas-un-email", "")
    assert resultat.exit_code == 1
    assert "invalide" in resultat.output


def test_create_admin_sans_tables(app):
    with app.app_context():
        db.drop_all()
    resultat = lancer_create_admin(app, "admin@mwene.test", "")
    assert resultat.exit_code == 1
    assert "init-db" in resultat.output
