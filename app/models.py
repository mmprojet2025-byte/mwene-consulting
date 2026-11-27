"""Modèles de la base de données.

Un modèle est une classe Python qui correspond à une table :
chaque attribut est une colonne, chaque objet est une ligne.
"""

import re

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.i18n import LANGUES, t

# Lien entre Flask et la base. Il est relié à l'application dans create_app().
db = SQLAlchemy()


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
