"""Fixtures partagées par tous les tests.

pytest lit ce fichier automatiquement. Un test qui demande un paramètre
nommé « app » ou « client » reçoit l'objet fabriqué ici.
"""

import pytest

from app import create_app
from app.config import TestConfig


@pytest.fixture
def app():
    """Une application neuve, réglée pour les tests."""
    return create_app(TestConfig)


@pytest.fixture
def client(app):
    """Un faux navigateur qui envoie des requêtes à l'application."""
    return app.test_client()
