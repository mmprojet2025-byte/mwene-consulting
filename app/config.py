"""Réglages de l'application.

Chaque classe regroupe les réglages d'un environnement.
create_app() choisit la classe à utiliser.
"""

import os


class Config:
    """Réglages communs à tous les environnements."""

    # Clé qui signe les cookies de session. Elle se lit dans la variable
    # d'environnement SECRET_KEY et ne doit jamais être écrite dans le code.
    # La valeur de repli ne sert qu'en développement local.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-non-secrete-a-changer")


class DevelopmentConfig(Config):
    """Réglages pour travailler en local."""

    DEBUG = True
    # Fichier SQLite. Un chemin relatif est placé par Flask-SQLAlchemy dans
    # le dossier instance/ (créé automatiquement, jamais commité).
    SQLALCHEMY_DATABASE_URI = "sqlite:///mwene.db"


class TestConfig(Config):
    """Réglages utilisés par pytest."""

    TESTING = True
    SECRET_KEY = "cle-de-test"
    # Base SQLite en mémoire : vide au départ, aucun fichier créé,
    # et une base neuve pour chaque test.
    SQLALCHEMY_DATABASE_URI = "sqlite://"
