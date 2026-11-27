"""Fabrique de l'application Flask.

create_app() construit une nouvelle application à chaque appel.
Les tests peuvent ainsi en créer une avec leurs propres réglages.
"""

from flask import Flask

from app.config import DevelopmentConfig
from app.i18n import t


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Rend t() utilisable dans tous les templates : {{ t('nav_home', 'fr') }}.
    # À l'étape 3, la langue sera déduite de l'URL (/pt/, /fr/, /en/).
    app.jinja_env.globals["t"] = t

    # Route provisoire : elle prouve que l'application répond.
    # À l'étape 3, « / » redirigera vers « /pt/ ».
    @app.route("/")
    def index():
        return "Mwene Consulting"

    return app
