"""Référencement : /sitemap.xml et /robots.txt.

Dans la v1, ces deux fichiers étaient écrits à la main avec un domaine
provisoire (VOTRE-DOMAINE.com). Ici, Flask les produit : les adresses sont
construites avec url_for(..., _external=True), donc avec le domaine sur
lequel le site tourne vraiment. Rien à remplacer avant la mise en ligne.
"""

from flask import Blueprint, Response, render_template, url_for

from app.i18n import LANGUE_PAR_DEFAUT, LANGUES

seo = Blueprint("seo", __name__)

# Pages que les moteurs de recherche doivent connaître : (route, priorité).
# Mêmes pages et mêmes priorités que le sitemap de la v1.
# Les pages légales et la 404 sont en « noindex », elles n'y figurent donc pas.
PAGES_INDEXEES = [
    ("vitrine.accueil", "1.0"),
    ("vitrine.services", "0.9"),
    ("vitrine.about", "0.8"),
    ("vitrine.contact", "0.8"),
]


@seo.route("/sitemap.xml")
def sitemap():
    """Une entrée par page et par langue (4 × 3 = 12 adresses).

    Chaque entrée liste aussi ses versions dans les autres langues
    (balises hreflang), comme Google le recommande.
    """
    entrees = []
    for route, priorite in PAGES_INDEXEES:
        versions = {lang: url_for(route, lang=lang, _external=True) for lang in LANGUES}
        for lang in LANGUES:
            entrees.append({"adresse": versions[lang], "versions": versions, "priorite": priorite})

    xml = render_template(
        "sitemap.xml", entrees=entrees, langue_par_defaut=LANGUE_PAR_DEFAUT
    )
    return Response(xml, mimetype="application/xml")


@seo.route("/robots.txt")
def robots():
    """Autorise tout le site et indique l'adresse du sitemap."""
    lignes = [
        "User-agent: *",
        "Allow: /",
        "",
        f"Sitemap: {url_for('seo.sitemap', _external=True)}",
    ]
    return Response("\n".join(lignes) + "\n", mimetype="text/plain")
