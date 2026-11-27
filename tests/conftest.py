"""Fixtures partagées par tous les tests.

pytest lit ce fichier automatiquement. Un test qui demande un paramètre
nommé « app » ou « client » reçoit l'objet fabriqué ici.
"""

import pytest

from app import create_app
from app.config import TestConfig
from app.models import db


@pytest.fixture
def app():
    """Une application neuve, réglée pour les tests.

    Sa base SQLite est en mémoire : les tables sont créées avant le test
    et supprimées après. Chaque test part donc d'une base vide.
    """
    app = create_app(TestConfig)
    # On n'ouvre le contexte que le temps de créer puis de supprimer les tables.
    # S'il restait ouvert pendant le test, toutes les requêtes du client de test
    # partageraient le même « g » (et donc g.lang).
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    """Un faux navigateur qui envoie des requêtes à l'application."""
    return app.test_client()
