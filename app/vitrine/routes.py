"""Routes du site vitrine.

Toutes les adresses commencent par la langue : /pt/, /fr/, /en/.
Un « blueprint » regroupe ces routes et leur donne ce préfixe commun.
"""

from flask import Blueprint, render_template

from app.i18n import brancher_langue

vitrine = Blueprint("vitrine", __name__, url_prefix="/<lang>")

# Langue lue dans l'URL et rangée dans g.lang ; /de/ -> 404 (voir app/i18n.py).
brancher_langue(vitrine)


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
