"""Sécurité de l'Espace Recrutement : connexion, CSRF, limite de tentatives.

Les trois outils sont créés ici, puis reliés à l'application dans create_app().
"""

from functools import wraps

from flask import abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, current_user, login_required
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import User, db

# --- Flask-Login : qui est connecté ? ------------------------------------------

login_manager = LoginManager()
# Page où l'on envoie un visiteur non connecté (dans la langue de la page en cours).
login_manager.login_view = "espace.connexion"
# Clé de traduction (et non une phrase) : elle est traduite à l'affichage.
login_manager.login_message = "espace_login_required"
login_manager.login_message_category = "info"


@login_manager.user_loader
def charger_compte(identifiant):
    """Retrouve le compte à partir de l'identifiant gardé dans le cookie de session."""
    return db.session.get(User, int(identifiant))


def admin_requis(vue):
    """Décorateur : page réservée aux administrateurs Mwene.

    - pas connecté -> redirection vers la page de connexion (comme @login_required) ;
    - connecté sans être administrateur -> erreur 403 (accès interdit).
    À placer au-dessus de chaque route d'administration.
    """

    @wraps(vue)
    @login_required
    def enveloppe(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return vue(*args, **kwargs)

    return enveloppe


# --- Flask-WTF : jeton CSRF obligatoire dans tous les formulaires POST ----------

csrf = CSRFProtect()

# --- Flask-Limiter : nombre de tentatives par adresse IP ------------------------

# Limitation : derrière un proxy (hébergement), get_remote_address verrait
# l'adresse du proxy. Il faudra régler ProxyFix au moment de la mise en ligne.
limiter = Limiter(key_func=get_remote_address)

LIMITE_CONNEXION = "5 per minute"

# --- Vérification des identifiants -----------------------------------------------

# Empreinte d'un mot de passe que personne ne connaît. Elle sert à prendre
# le même temps de calcul quand l'e-mail n'existe pas (voir ci-dessous).
_EMPREINTE_FACTICE = generate_password_hash("compte-inexistant-pour-egaliser-le-temps")


def verifier_identifiants(email, mot_de_passe):
    """Renvoie le compte si l'e-mail et le mot de passe sont bons, sinon None.

    Ne dit jamais si c'est l'e-mail ou le mot de passe qui est faux.
    Si l'e-mail est inconnu, on vérifie quand même une empreinte factice :
    sinon la réponse serait plus rapide, et un attaquant pourrait deviner
    quels e-mails ont un compte en mesurant le temps de réponse.
    """
    email = (email or "").strip().lower()
    mot_de_passe = mot_de_passe or ""
    compte = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
    if compte is None:
        check_password_hash(_EMPREINTE_FACTICE, mot_de_passe)
        return None
    return compte if compte.check_password(mot_de_passe) else None
