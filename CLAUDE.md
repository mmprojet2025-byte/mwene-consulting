# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projet

Application web Flask de Mwene Consulting, cabinet de conseil en RH pour les PME en Angola (branche `v2-flask`). Elle comprend un site vitrine trilingue (PT par défaut, FR, EN) et, à venir, un Espace Recrutement pour les entreprises clientes. Le plan en 14 étapes se trouve dans `docs/PLAN-v2.md`. `README.md` décrit le projet et son avancement.

## Commandes

- Activer l'environnement : `source .venv/bin/activate`
- Installer les dépendances : `pip install -r requirements.txt`
- Lancer le site en développement : `flask --app app run --debug --port 5001`, puis ouvrir http://127.0.0.1:5001/. Sur Mac, il faut utiliser `--port 5001`, car le port 5000 (celui de Flask par défaut) est pris par AirPlay.
- Lancer tous les tests : `pytest`
- Lancer un seul fichier de tests : `pytest tests/test_app.py`
- Lister les routes : `flask --app app routes`

## Architecture

- `app/__init__.py` : `create_app(config_class)` est la fabrique de l'application. Elle enregistre les blueprints `vitrine` et `seo`, la page 404 personnalisée, la redirection `/` → `/pt/`, et rend disponibles dans tous les templates `t()`, `url_pour_langue()`, `url_canonique()`, `lang`, `langues`, `langue_par_defaut` et `annee`.
- `app/config.py` : `DevelopmentConfig` et `TestConfig`. `SECRET_KEY` se lit dans l'environnement, jamais en dur.
- `app/vitrine/routes.py` : blueprint avec le préfixe `/<lang>`. `url_value_preprocessor` retire la langue de l'URL, la range dans `g.lang`, et renvoie une 404 si elle est inconnue. `url_defaults` réutilise `g.lang` dans `url_for('vitrine.…')`. Chaque route passe `page=` pour indiquer le lien actif du menu.
- `app/seo.py` : `/sitemap.xml` (les pages de `PAGES_INDEXEES` × 3 langues, avec `hreflang`) et `/robots.txt`. Les adresses sont complètes (`_external=True`) : aucun domaine n'est écrit en dur.
- `app/templates/` : `base.html` (le `<head>`, avec `canonical` et `hreflang` sur les pages indexables), `partials/header.html` et `footer.html`, `vitrine/*.html`, `404.html`, `sitemap.xml`.
- `app/static/` : `css/style.css` (repris de la v1) et `js/main.js` (menu mobile, retour en haut, fondus `.fade-in` → `.visible`, formulaire de contact). Il n'y a pas d'i18n côté client.

### i18n (côté serveur)

- Les textes sont dans `translations/pt.json`, `fr.json` et `en.json`, qui doivent avoir **exactement les mêmes clés** (un test le vérifie). Tout nouveau texte demande une clé dans les trois fichiers.
- `app/i18n.py` : `t(cle, langue)` se replie sur `pt`, puis sur la clé elle-même. Dans les templates, `{{ t('cle') }}` utilise la langue de la page.
- La langue est le premier morceau de l'URL : `/pt/`, `/fr/`, `/en/`. Le sélecteur de langue est fait de simples liens (`url_pour_langue()` garde la page et les paramètres `?…`).
- `<title>` (`{% block title %}`) et la description (`{% set description = t('meta_desc_…') %}`) sont traduits avec les clés `meta_title_*` et `meta_desc_*`. Une page définit `{% set robots = "noindex, follow" %}` pour ne pas être indexée : elle n'a alors ni `canonical` ni `hreflang`, et ne doit pas figurer dans le sitemap.
- Jinja échappe le HTML : les valeurs de traduction ne doivent pas contenir de balises.

### Formulaire de contact (`vitrine/contact.html` + `initContactForm` dans `main.js`)

- Envoi vers Formspree. L'identifiant vient de `data-formspree-id`. Tant qu'il vaut `YOUR_FORMSPREE_ID`, le formulaire affiche l'état `not-configured` au lieu d'envoyer.
- Les messages traduits sont passés à `main.js` par des attributs `data-msg-*` du formulaire.
- Les états sont des éléments `.form-state` d'id `state-<nom>` (`form`, `success`, `error`, `not-configured`), basculés par `showState()`. `#website` est un champ honeypot.
- Les champs `name`, `company`, `email` et `message` sont obligatoires, et les erreurs s'affichent dans `#error-<id>`.
- `?service=<valeur>` présélectionne `#service`. Les valeurs `recrutamento`, `organizacao-rh` et `formacao` des liens de la page Services doivent correspondre aux `<option>` (un test le vérifie). Les ancres `#recrutamento`, `#organizacao-rh` et `#formacoes` de la page Services sont liées depuis le pied de page.

### Tests

- `tests/conftest.py` fournit les fixtures `app` (`create_app(TestConfig)`) et `client`.
- `test_i18n.py` (traductions), `test_vitrine.py` (chaque page × chaque langue, 404, menu, formulaire), `test_seo.py` (sitemap, robots, titres, hreflang).
- Pour comparer un texte traduit au HTML, utilisez `markupsafe.escape(t(...))`, car Jinja échappe les apostrophes.

### Base de données

- Flask-SQLAlchemy, avec `db = SQLAlchemy()` défini dans `app/models.py` et relié à l'application par `db.init_app(app)` dans `create_app()`.
- Adresse de la base (`SQLALCHEMY_DATABASE_URI` dans `config.py`) : `sqlite:///mwene.db` en développement (Flask-SQLAlchemy place un chemin relatif dans `instance/`, donc `instance/mwene.db`), et `sqlite://` (en mémoire) pour les tests.
- `flask --app app init-db` crée les tables manquantes (`db.create_all()`) et ajoute les pays de `PAYS_INITIAUX` (uniquement l'Angola). Elle peut être relancée sans risque : elle n'efface rien et ne crée pas de doublon. Il n'y a pas encore d'outil de migration : `create_all()` ne modifie pas une table qui existe déjà.
- Modèle `Country` : `code` (ISO 3166-1, 2 majuscules, unique), `langue_par_defaut` (une des `LANGUES`) et `devise` (ISO 4217, 3 majuscules). Des `@validates` refusent les valeurs mal formées. Le nom du pays n'est pas stocké : `nom(langue)` lit la clé `country_<code en minuscules>` dans les traductions. Ajouter un pays demande donc une ligne en base et cette clé dans les 3 fichiers JSON, sans modifier le code.
- Tests : la fixture `app` crée les tables avant chaque test et les supprime après. Elle n'ouvre le contexte d'application que pour ces deux opérations : s'il restait ouvert, les requêtes du client de test le réutiliseraient et partageraient le même `g` (donc `g.lang`). Dans un test qui utilise `db.session`, ouvrez `with app.app_context():` (voir la fixture `contexte` de `test_models.py`).
- Le fichier `.db` et le dossier `instance/` ne doivent jamais être commités (ils sont dans `.gitignore`). Ne lisez pas les fichiers `.db` (règle de `.claude/settings.json`).

## Règles

- Tout texte visible existe en PT, FR et EN.
- Le site doit pouvoir fonctionner pour plusieurs pays (pays, langue, devise).
- L'IA aide mais ne décide jamais à la place d'un humain.
- Les CV sont des données personnelles : consentement obligatoire, et accès limité à l'entreprise concernée.
- N'inventez aucune information sur l'entreprise : ni témoignages, ni logos clients, ni statistiques, ni coordonnées, ni prix. Les textes provisoires comme `[E-mail profissional a completar]` (`.contact-placeholder` dans `vitrine/contact.html`) sont volontaires, en attendant les vraies informations de la propriétaire.
- Les traductions FR/EN nouvelles sont à faire valider par la propriétaire (voir la section du README « Textes à faire valider »).

## Façon de travailler

- L'utilisateur est étudiant : explique chaque changement simplement avant de le faire.
- Avance par petites étapes, chacune testable seule.
- Demande son accord avant de modifier un fichier, de faire un commit ou un push.
- N'invente jamais d'informations (coordonnées, témoignages, chiffres, prix).
- Réponds en français.
