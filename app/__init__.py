"""Fabrique de l'application Flask.

create_app() construit une nouvelle application à chaque appel.
Les tests peuvent ainsi en créer une avec leurs propres réglages.
"""

from datetime import date

from flask import Flask, g, redirect, url_for

from app.config import DevelopmentConfig
from app.i18n import LANGUE_PAR_DEFAUT, LANGUES, t_template, url_pour_langue


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Fonctions utilisables dans tous les templates.
    # {{ t('nav_home') }} traduit dans la langue de la page en cours.
    app.jinja_env.globals["t"] = t_template
    app.jinja_env.globals["url_pour_langue"] = url_pour_langue

    @app.context_processor
    def variables_communes():
        """Variables disponibles dans tous les templates."""
        return {
            "lang": g.get("lang", LANGUE_PAR_DEFAUT),
            "langues": LANGUES,
            "annee": date.today().year,
        }

    from app.vitrine.routes import vitrine

    app.register_blueprint(vitrine)

    @app.route("/")
    def racine():
        """« / » renvoie vers la version portugaise, langue par défaut."""
        return redirect(url_for("vitrine.accueil", lang=LANGUE_PAR_DEFAUT))

    return app
