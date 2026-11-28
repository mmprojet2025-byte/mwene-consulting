"""Fabrique de l'application Flask.

create_app() construit une nouvelle application à chaque appel.
Les tests peuvent ainsi en créer une avec leurs propres réglages.
"""

from datetime import date

import click
import sqlalchemy
from flask import Flask, g, redirect, render_template, request, url_for

from app.config import DevelopmentConfig
from app.i18n import (
    LANGUE_PAR_DEFAUT,
    LANGUES,
    t_template,
    url_canonique,
    url_pour_langue,
)
from app.models import User, ajouter_pays_initiaux, db


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Base de données : l'adresse est lue dans SQLALCHEMY_DATABASE_URI (config.py).
    db.init_app(app)

    @app.cli.command("init-db")
    def init_db():
        """Crée les tables manquantes et ajoute les pays de départ (Angola).

        Usage : flask --app app init-db
        On peut la relancer sans risque : rien n'est effacé ni ajouté deux fois.
        """
        db.create_all()
        ajoutes = ajouter_pays_initiaux()
        click.echo(f"Base prête : {db.engine.url.database}")
        if ajoutes:
            click.echo(f"Pays ajoutés : {', '.join(ajoutes)}")
        else:
            click.echo("Aucun pays ajouté (déjà présents).")

    @app.cli.command("create-admin")
    @click.option("--email", prompt="E-mail de l'administrateur", help="E-mail du compte Mwene.")
    def create_admin(email):
        """Crée un compte administrateur Mwene (sans entreprise cliente).

        Usage : flask --app app create-admin --email adresse@exemple.com

        Le mot de passe est demandé deux fois, sans être affiché. Il n'est pas
        accepté en option, pour qu'il ne reste pas dans l'historique du terminal.
        """
        if not sqlalchemy.inspect(db.engine).has_table(User.__tablename__):
            raise click.ClickException(
                "Les tables n'existent pas encore : lancez d'abord « flask --app app init-db »."
            )

        try:
            admin = User(email=email, is_admin=True)
        except ValueError as erreur:
            raise click.ClickException(str(erreur))

        deja_pris = db.session.execute(
            db.select(User).filter_by(email=admin.email)
        ).scalar_one_or_none()
        if deja_pris is not None:
            raise click.ClickException(f"Un compte existe déjà avec l'e-mail {admin.email}.")

        mot_de_passe = click.prompt(
            "Mot de passe", hide_input=True, confirmation_prompt="Confirmez le mot de passe"
        )
        try:
            admin.set_password(mot_de_passe)
        except ValueError as erreur:
            raise click.ClickException(str(erreur))

        db.session.add(admin)
        db.session.commit()
        click.echo(f"Administrateur créé : {admin.email}")

    # Fonctions utilisables dans tous les templates.
    # {{ t('nav_home') }} traduit dans la langue de la page en cours.
    app.jinja_env.globals["t"] = t_template
    app.jinja_env.globals["url_pour_langue"] = url_pour_langue
    app.jinja_env.globals["url_canonique"] = url_canonique

    @app.context_processor
    def variables_communes():
        """Variables disponibles dans tous les templates."""
        return {
            "lang": g.get("lang", LANGUE_PAR_DEFAUT),
            "langues": LANGUES,
            "langue_par_defaut": LANGUE_PAR_DEFAUT,
            "annee": date.today().year,
        }

    from app.seo import seo
    from app.vitrine.routes import vitrine

    app.register_blueprint(vitrine)
    app.register_blueprint(seo)

    @app.route("/")
    def racine():
        """« / » renvoie vers la version portugaise, langue par défaut."""
        return redirect(url_for("vitrine.accueil", lang=LANGUE_PAR_DEFAUT))

    @app.errorhandler(404)
    def page_introuvable(erreur):
        """Page 404 personnalisée, dans la langue du début de l'adresse.

        /fr/page-inexistante -> 404 en français.
        /de/ ou /n-importe-quoi -> 404 en portugais.
        """
        if g.get("lang") not in LANGUES:
            premier_morceau = request.path.strip("/").split("/")[0]
            g.lang = premier_morceau if premier_morceau in LANGUES else LANGUE_PAR_DEFAUT
        return render_template("404.html"), 404

    return app
