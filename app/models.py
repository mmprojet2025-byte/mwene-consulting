"""Modèles de la base de données.

Un modèle est une classe Python qui correspond à une table :
chaque attribut est une colonne, chaque objet est une ligne.
"""

import re
import sqlite3

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, ForeignKey, String, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from werkzeug.security import check_password_hash, generate_password_hash

from app.i18n import LANGUES, t

# Lien entre Flask et la base. Il est relié à l'application dans create_app().
db = SQLAlchemy()

# Longueur minimale d'un mot de passe.
LONGUEUR_MIN_MOT_DE_PASSE = 12


@event.listens_for(Engine, "connect")
def _activer_cles_etrangeres(connexion, _infos):
    """SQLite ne vérifie pas les clés étrangères par défaut : on l'active.

    Sans cela, on pourrait rattacher un utilisateur à une entreprise
    qui n'existe pas.
    """
    if isinstance(connexion, sqlite3.Connection):
        curseur = connexion.cursor()
        curseur.execute("PRAGMA foreign_keys=ON")
        curseur.close()


class Country(db.Model):
    """Un pays où l'application est utilisée.

    Ajouter un pays = ajouter une ligne dans cette table (aucun code à modifier)
    + son nom dans les 3 fichiers de traduction (clé « country_<code> »).
    """

    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Code ISO 3166-1 alpha-2 : 2 lettres majuscules (AO = Angola).
    code: Mapped[str] = mapped_column(String(2), unique=True)
    # Langue proposée par défaut dans ce pays : une des langues du site.
    langue_par_defaut: Mapped[str] = mapped_column(String(2))
    # Code ISO 4217 de la devise : 3 lettres majuscules (AOA = kwanza).
    devise: Mapped[str] = mapped_column(String(3))

    @validates("code")
    def _verifier_code(self, cle, valeur):
        if not re.fullmatch(r"[A-Z]{2}", valeur or ""):
            raise ValueError(f"Code pays invalide : {valeur!r} (2 lettres majuscules, ex. AO)")
        return valeur

    @validates("langue_par_defaut")
    def _verifier_langue(self, cle, valeur):
        if valeur not in LANGUES:
            raise ValueError(f"Langue invalide : {valeur!r} (attendu : {', '.join(LANGUES)})")
        return valeur

    @validates("devise")
    def _verifier_devise(self, cle, valeur):
        if not re.fullmatch(r"[A-Z]{3}", valeur or ""):
            raise ValueError(f"Devise invalide : {valeur!r} (3 lettres majuscules, ex. AOA)")
        return valeur

    @property
    def cle_traduction(self):
        """Clé du nom du pays dans translations/*.json : AO -> « country_ao »."""
        return f"country_{self.code.lower()}"

    def nom(self, langue):
        """Nom du pays dans la langue demandée, lu dans les traductions."""
        return t(self.cle_traduction, langue)

    def __repr__(self):
        return f"<Country {self.code}>"


class Company(db.Model):
    """Une entreprise cliente de Mwene, rattachée à un pays."""

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200))
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"))

    country: Mapped[Country] = relationship()
    users: Mapped[list["User"]] = relationship(back_populates="company")

    @validates("nom")
    def _verifier_nom(self, cle, valeur):
        valeur = (valeur or "").strip()
        if not valeur:
            raise ValueError("Le nom de l'entreprise est obligatoire.")
        return valeur

    def __repr__(self):
        return f"<Company {self.id} {self.nom!r}>"


class User(UserMixin, db.Model):
    """Un compte : un administrateur Mwene, ou une personne d'une entreprise cliente.

    UserMixin ajoute ce qu'attend Flask-Login (is_authenticated, get_id()…).
    """

    __tablename__ = "users"
    __table_args__ = (
        # Un compte qui n'est pas administrateur appartient forcément à une
        # entreprise : pas de compte client « flottant », sans entreprise.
        CheckConstraint(
            "is_admin = 1 OR company_id IS NOT NULL",
            name="compte_client_avec_entreprise",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # Toujours enregistré en minuscules (voir _normaliser_email).
    email: Mapped[str] = mapped_column(String(254), unique=True)
    # Empreinte du mot de passe (scrypt, via werkzeug). Jamais le mot de passe lui-même.
    password_hash: Mapped[str] = mapped_column(String(255))
    # Vide pour un administrateur Mwene, qui n'appartient à aucune entreprise cliente.
    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id"))
    is_admin: Mapped[bool] = mapped_column(default=False)

    company: Mapped[Company | None] = relationship(back_populates="users")

    @validates("email")
    def _normaliser_email(self, cle, valeur):
        """« Ana@Exemple.com » et « ana@exemple.com » sont le même compte."""
        valeur = (valeur or "").strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", valeur):
            raise ValueError(f"Adresse e-mail invalide : {valeur!r}")
        return valeur

    def set_password(self, mot_de_passe):
        """Enregistre l'empreinte du mot de passe (le mot de passe n'est pas gardé).

        Le hachage est à sens unique : on ne peut pas retrouver le mot de passe
        à partir de l'empreinte. Un « sel » aléatoire est ajouté : deux comptes
        avec le même mot de passe ont des empreintes différentes.
        """
        if len(mot_de_passe or "") < LONGUEUR_MIN_MOT_DE_PASSE:
            raise ValueError(
                f"Le mot de passe doit contenir au moins {LONGUEUR_MIN_MOT_DE_PASSE} caractères."
            )
        self.password_hash = generate_password_hash(mot_de_passe)

    def check_password(self, mot_de_passe):
        """Vrai si « mot_de_passe » correspond à l'empreinte enregistrée."""
        if not self.password_hash or mot_de_passe is None:
            return False
        return check_password_hash(self.password_hash, mot_de_passe)

    def __repr__(self):
        # Volontairement sans l'empreinte : elle ne doit pas finir dans les logs.
        role = "admin" if self.is_admin else f"entreprise {self.company_id}"
        return f"<User {self.email} ({role})>"


# Pays ajoutés par « flask init-db ». Uniquement l'Angola pour l'instant.
PAYS_INITIAUX = [
    {"code": "AO", "langue_par_defaut": "pt", "devise": "AOA"},
]


def ajouter_pays_initiaux():
    """Ajoute les pays de PAYS_INITIAUX qui ne sont pas encore dans la base.

    On peut relancer cette fonction sans risque : un pays déjà présent
    n'est pas ajouté une deuxième fois. Renvoie la liste des codes ajoutés.
    """
    ajoutes = []
    for donnees in PAYS_INITIAUX:
        deja_la = db.session.execute(
            db.select(Country).filter_by(code=donnees["code"])
        ).scalar_one_or_none()
        if deja_la is None:
            db.session.add(Country(**donnees))
            ajoutes.append(donnees["code"])
    db.session.commit()
    return ajoutes
