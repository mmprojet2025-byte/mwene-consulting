"""Tests de la base de données et du modèle Country (étape 6)."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.i18n import LANGUES, TRADUCTIONS
from app.models import PAYS_INITIAUX, Country, ajouter_pays_initiaux, db


@pytest.fixture
def contexte(app):
    """Ouvre un contexte d'application : nécessaire pour utiliser db.session."""
    with app.app_context():
        yield


def tous_les_pays():
    return db.session.execute(db.select(Country).order_by(Country.code)).scalars().all()


def test_les_tests_utilisent_une_base_en_memoire(app):
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite://"


def test_la_base_de_test_est_vide_au_depart(contexte):
    assert tous_les_pays() == []


def test_enregistrer_et_relire_un_pays(contexte):
    db.session.add(Country(code="AO", langue_par_defaut="pt", devise="AOA"))
    db.session.commit()

    pays = db.session.execute(db.select(Country).filter_by(code="AO")).scalar_one()
    assert pays.langue_par_defaut == "pt"
    assert pays.devise == "AOA"
    assert repr(pays) == "<Country AO>"


@pytest.mark.parametrize("langue", LANGUES)
def test_le_nom_vient_des_traductions(contexte, langue):
    pays = Country(code="AO", langue_par_defaut="pt", devise="AOA")
    assert pays.cle_traduction == "country_ao"
    assert pays.nom(langue) == "Angola"


@pytest.mark.parametrize(
    "champs",
    [
        {"code": "Angola"},  # pas 2 lettres
        {"code": "ao"},  # minuscules
        {"langue_par_defaut": "de"},  # langue non prise en charge
        {"devise": "kz"},  # pas 3 lettres majuscules
        {"devise": "AOAX"},
    ],
)
def test_valeurs_invalides_refusees(contexte, champs):
    valides = {"code": "AO", "langue_par_defaut": "pt", "devise": "AOA"}
    with pytest.raises(ValueError):
        Country(**{**valides, **champs})


def test_code_pays_unique(contexte):
    db.session.add(Country(code="AO", langue_par_defaut="pt", devise="AOA"))
    db.session.commit()
    db.session.add(Country(code="AO", langue_par_defaut="fr", devise="EUR"))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_pays_initiaux_uniquement_l_angola():
    assert PAYS_INITIAUX == [{"code": "AO", "langue_par_defaut": "pt", "devise": "AOA"}]


def test_ajouter_pays_initiaux(contexte):
    assert ajouter_pays_initiaux() == ["AO"]
    assert [p.code for p in tous_les_pays()] == ["AO"]


def test_ajouter_pays_initiaux_sans_doublon(contexte):
    ajouter_pays_initiaux()
    assert ajouter_pays_initiaux() == []  # rien de nouveau la deuxième fois
    assert len(tous_les_pays()) == 1


@pytest.mark.parametrize("donnees", PAYS_INITIAUX)
def test_chaque_pays_initial_a_son_nom_dans_les_3_langues(donnees):
    cle = f"country_{donnees['code'].lower()}"
    for langue in LANGUES:
        assert cle in TRADUCTIONS[langue]


def test_commande_init_db(app):
    runner = app.test_cli_runner()

    resultat = runner.invoke(args=["init-db"])
    assert resultat.exit_code == 0
    assert "Pays ajoutés : AO" in resultat.output

    # Relancer la commande ne casse rien et n'ajoute pas de doublon.
    resultat = runner.invoke(args=["init-db"])
    assert resultat.exit_code == 0
    assert "Aucun pays ajouté" in resultat.output

    with app.app_context():
        assert [p.code for p in tous_les_pays()] == ["AO"]
