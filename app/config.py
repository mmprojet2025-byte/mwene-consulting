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

    # Cookie de session (connexion à l'Espace Recrutement) :
    # « Lax » = le navigateur ne l'envoie pas quand un autre site soumet un
    # formulaire vers le nôtre (protection CSRF en plus du jeton de Flask-WTF).
    # HttpOnly (JavaScript ne peut pas le lire) est déjà activé par Flask.
    SESSION_COOKIE_SAMESITE = "Lax"

    # Compteurs de Flask-Limiter (tentatives de connexion) gardés en mémoire :
    # suffisant en développement et en test. Remis à zéro au redémarrage.
    RATELIMIT_STORAGE_URI = "memory://"


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
