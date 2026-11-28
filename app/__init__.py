"""Fabrique de l'application Flask.

create_app() construit une nouvelle application à chaque appel.
Les tests peuvent ainsi en créer une avec leurs propres réglages.
"""

from datetime import date

import click
import sqlalchemy
from flask import Flask, g, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFError

from app.config import DevelopmentConfig
from app.i18n import (
    LANGUE_PAR_DEFAUT,
    LANGUES,
    t_template,
    url_canonique,
    url_pour_langue,
)
from app.models import User, ajouter_pays_initiaux, db
from app.securite import csrf, limiter, login_manager


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

    # Sécurité de l'Espace Recrutement (voir app/securite.py).
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    from app.espace.routes import espace
    from app.seo import seo
    from app.vitrine.routes import vitrine

    app.register_blueprint(vitrine)
    app.register_blueprint(espace)
    app.register_blueprint(seo)

    @app.route("/")
    def racine():
        """« / » renvoie vers la version portugaise, langue par défaut."""
        return redirect(url_for("vitrine.accueil", lang=LANGUE_PAR_DEFAUT))

    def langue_de_la_page_d_erreur():
        """Langue d'une page d'erreur : celle du début de l'adresse, sinon le portugais.

        /fr/page-inexistante -> français ; /de/ ou /n-importe-quoi -> portugais.
        """
        if g.get("lang") not in LANGUES:
            premier_morceau = request.path.strip("/").split("/")[0]
            g.lang = premier_morceau if premier_morceau in LANGUES else LANGUE_PAR_DEFAUT

    @app.errorhandler(404)
    def page_introuvable(erreur):
        """Page 404 personnalisée, dans la langue du début de l'adresse."""
        langue_de_la_page_d_erreur()
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def acces_interdit(erreur):
        """Page réservée aux administrateurs, visitée par un compte client."""
        langue_de_la_page_d_erreur()
        return render_template(
            "espace/erreur.html",
            cle_titre="espace_forbidden_title",
            cle_texte="espace_forbidden_text",
            endpoint_retour="espace.tableau_de_bord",
            cle_retour="espace_back_to_dashboard",
        ), 403

    @app.errorhandler(429)
    def trop_de_tentatives(erreur):
        """Plus de LIMITE_CONNEXION tentatives : message traduit, code 429 conservé."""
        langue_de_la_page_d_erreur()
        return render_template(
            "espace/erreur.html", cle_titre="espace_too_many_title", cle_texte="espace_too_many_text"
        ), 429

    @app.errorhandler(CSRFError)
    def jeton_csrf_invalide(erreur):
        """Formulaire sans jeton CSRF valide (absent, expiré, ou venant d'un autre site)."""
        langue_de_la_page_d_erreur()
        return render_template(
            "espace/erreur.html", cle_titre="espace_csrf_title", cle_texte="espace_csrf_text"
        ), 400

    return app
