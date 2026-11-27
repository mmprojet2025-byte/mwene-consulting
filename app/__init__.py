"""Fabrique de l'application Flask.

create_app() construit une nouvelle application à chaque appel.
Les tests peuvent ainsi en créer une avec leurs propres réglages.
"""

from flask import Flask

from app.config import DevelopmentConfig


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Route provisoire : elle prouve que l'application répond.
    # À l'étape 3, « / » redirigera vers « /pt/ ».
    @app.route("/")
    def index():
        return "Mwene Consulting"

    return app
