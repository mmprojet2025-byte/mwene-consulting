"""Routes du site vitrine.

Toutes les adresses commencent par la langue : /pt/, /fr/, /en/.
Un « blueprint » regroupe ces routes et leur donne ce préfixe commun.
"""

from flask import Blueprint, abort, g, render_template

from app.i18n import LANGUES

vitrine = Blueprint("vitrine", __name__, url_prefix="/<lang>")


@vitrine.url_value_preprocessor
def lire_langue(endpoint, values):
    """Avant chaque page : on retire la langue de l'URL et on la range dans g.lang.

    Une langue inconnue (/de/, /xx/…) donne une erreur 404.
    """
    g.lang = values.pop("lang")
    if g.lang not in LANGUES:
        abort(404)


@vitrine.url_defaults
def ajouter_langue(endpoint, values):
    """url_for('vitrine.…') réutilise la langue de la page en cours si on ne la précise pas."""
    if "lang" not in values and "lang" in g:
        values["lang"] = g.lang


@vitrine.route("/")
def accueil():
    return render_template("vitrine/index.html", page="home")


@vitrine.route("/services")
def services():
    return render_template("vitrine/services.html", page="services")


@vitrine.route("/about")
def about():
    return render_template("vitrine/about.html", page="about")


@vitrine.route("/contact")
def contact():
    return render_template("vitrine/contact.html", page="contact")


@vitrine.route("/mentions-legales")
def mentions_legales():
    return render_template("vitrine/mentions-legales.html")


@vitrine.route("/confidentialite")
def confidentialite():
    return render_template("vitrine/confidentialite.html")
