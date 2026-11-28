"""Routes de l'Espace Recrutement : connexion, déconnexion, tableau de bord.

Toutes les adresses commencent par /<lang>/espace/.
"""

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from app.i18n import brancher_langue
from app.models import LONGUEUR_MIN_MOT_DE_PASSE, Company, Country, User, db
from app.securite import LIMITE_CONNEXION, admin_requis, limiter, verifier_identifiants

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


# --- Administration Mwene (comptes is_admin uniquement) --------------------------
# Les administrateurs créent les entreprises clientes et leurs comptes.
# Les comptes administrateurs, eux, se créent avec « flask create-admin ».


def _trouver(modele, identifiant):
    """L'objet dont l'identifiant vient d'un formulaire, ou None s'il est absent ou invalide."""
    try:
        return db.session.get(modele, int(identifiant))
    except (TypeError, ValueError):
        return None


def _afficher_admin(erreurs_entreprise=(), erreurs_compte=(), saisie=None, statut=200):
    """Page d'administration, avec les erreurs (clés de traduction) et la saisie à garder."""
    entreprises = db.session.execute(db.select(Company).order_by(Company.nom)).scalars().all()
    pays = db.session.execute(db.select(Country).order_by(Country.code)).scalars().all()
    return render_template(
        "espace/admin.html",
        entreprises=entreprises,
        pays=pays,
        erreurs_entreprise=erreurs_entreprise,
        erreurs_compte=erreurs_compte,
        saisie=saisie or {},
        longueur_min=LONGUEUR_MIN_MOT_DE_PASSE,
    ), statut


@espace.route("/admin")
@admin_requis
def admin():
    return _afficher_admin()


@espace.route("/admin/entreprises", methods=["POST"])
@admin_requis
def creer_entreprise():
    nom = request.form.get("nom", "").strip()
    pays = _trouver(Country, request.form.get("pays"))

    erreurs = []
    if not nom:
        erreurs.append("admin_error_company_name")
    if pays is None:
        erreurs.append("admin_error_country")
    if erreurs:
        return _afficher_admin(erreurs_entreprise=erreurs, saisie=request.form, statut=400)

    db.session.add(Company(nom=nom, country=pays))
    db.session.commit()
    flash("admin_company_created", "succes")
    return redirect(url_for("espace.admin"))


@espace.route("/admin/utilisateurs", methods=["POST"])
@admin_requis
def creer_compte():
    entreprise = _trouver(Company, request.form.get("entreprise"))
    mot_de_passe = request.form.get("mot_de_passe", "")

    erreurs = []
    if entreprise is None:
        erreurs.append("admin_error_company")

    # Le compte n'est rattaché à l'entreprise qu'une fois tout vérifié, juste
    # avant db.session.add(). Avec SQLAlchemy 2, le rattacher plus tôt ne
    # l'enregistrerait pas, mais provoquerait un avertissement (SAWarning) à
    # chaque requête faite entre-temps (vérification de l'e-mail).
    compte = None
    try:
        compte = User(email=request.form.get("email", ""), is_admin=False)
    except ValueError:
        erreurs.append("admin_error_email_invalid")

    if compte is not None:
        deja_pris = db.session.execute(
            db.select(User).filter_by(email=compte.email)
        ).scalar_one_or_none()
        if deja_pris is not None:
            erreurs.append("admin_error_email_taken")

    if len(mot_de_passe) < LONGUEUR_MIN_MOT_DE_PASSE:
        erreurs.append("admin_error_password_short")

    if erreurs:
        # On garde l'e-mail et l'entreprise choisie, jamais le mot de passe.
        return _afficher_admin(erreurs_compte=erreurs, saisie=request.form, statut=400)

    compte.set_password(mot_de_passe)
    compte.company = entreprise
    db.session.add(compte)
    try:
        db.session.commit()
    except IntegrityError:
        # Cas rare : le même e-mail créé au même moment par une autre requête.
        db.session.rollback()
        return _afficher_admin(
            erreurs_compte=["admin_error_email_taken"], saisie=request.form, statut=400
        )
    flash("admin_user_created", "succes")
    return redirect(url_for("espace.admin"))
