"""Routes de l'Espace Recrutement : connexion, déconnexion, tableau de bord.

Toutes les adresses commencent par /<lang>/espace/.
"""

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.i18n import brancher_langue
from app.securite import LIMITE_CONNEXION, limiter, verifier_identifiants

espace = Blueprint("espace", __name__, url_prefix="/<lang>/espace")

# Langue lue dans l'URL et rangée dans g.lang ; /de/espace/… -> 404 (voir app/i18n.py).
brancher_langue(espace)


@espace.route("/connexion", methods=["GET", "POST"])
@limiter.limit(LIMITE_CONNEXION, methods=["POST"])  # seuls les envois du formulaire comptent
def connexion():
    if current_user.is_authenticated:
        return redirect(url_for("espace.tableau_de_bord"))

    email = ""
    echec = False
    if request.method == "POST":
        email = request.form.get("email", "")
        compte = verifier_identifiants(email, request.form.get("mot_de_passe", ""))
        if compte is not None:
            # On repart d'une session vide : rien d'avant la connexion n'est gardé.
            session.clear()
            login_user(compte)
            # Toujours le tableau de bord : on ignore « ?next= » (redirection ouverte).
            return redirect(url_for("espace.tableau_de_bord"))
        # Message neutre : on ne dit pas si c'est l'e-mail ou le mot de passe.
        echec = True

    return render_template("espace/connexion.html", email=email, echec=echec)


@espace.route("/tableau-de-bord")
@login_required
def tableau_de_bord():
    return render_template("espace/tableau-de-bord.html")


@espace.route("/deconnexion", methods=["POST"])  # POST + jeton CSRF : pas de déconnexion par simple lien
@login_required
def deconnexion():
    logout_user()
    flash("espace_logout_done", "succes")  # clé de traduction, traduite à l'affichage
    return redirect(url_for("espace.connexion"))
