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

- `app/__init__.py` : `create_app(config_class)` est la fabrique de l'application. Elle relie `db`, `login_manager`, `csrf` et `limiter` à l'application, enregistre les blueprints `vitrine`, `espace` et `seo`, crée la redirection `/` → `/pt/` et les commandes `init-db` et `create-admin`. Elle rend disponibles dans tous les templates `t()`, `url_pour_langue()`, `url_canonique()`, `lang`, `langues`, `langue_par_defaut` et `annee`. Pages d'erreur traduites : 404 (`404.html`), 429 et 400 CSRF (`espace/erreur.html`). Leur langue vient de `langue_de_la_page_d_erreur()`.
- `app/config.py` : `DevelopmentConfig` et `TestConfig`. `SECRET_KEY` se lit dans l'environnement, jamais en dur. `SESSION_COOKIE_SAMESITE = "Lax"`, et `RATELIMIT_STORAGE_URI = "memory://"` (compteurs de tentatives en mémoire).
- `app/vitrine/routes.py` : blueprint avec le préfixe `/<lang>`, branché sur la langue par `brancher_langue(vitrine)` (voir i18n). Chaque route passe `page=` pour indiquer le lien actif du menu.
- `app/espace/routes.py` : blueprint `espace` avec le préfixe `/<lang>/espace`, lui aussi branché par `brancher_langue`. Routes `connexion` (GET/POST), `tableau_de_bord` (`@login_required`) et `deconnexion` (POST uniquement).
- `app/securite.py` : `login_manager` (Flask-Login), `csrf` (`CSRFProtect` de Flask-WTF, pour tous les POST de l'application), `limiter` (Flask-Limiter, par adresse IP), `LIMITE_CONNEXION = "5 per minute"` et `verifier_identifiants()`.
- `app/seo.py` : `/sitemap.xml` (les pages de `PAGES_INDEXEES` × 3 langues, avec `hreflang`) et `/robots.txt`. Les adresses sont complètes (`_external=True`) : aucun domaine n'est écrit en dur.
- `app/templates/` : `base.html` (le `<head>`, avec `canonical` et `hreflang` sur les pages indexables), `partials/header.html` et `footer.html`, `vitrine/*.html`, `espace/*.html` (connexion, tableau de bord, erreur), `404.html`, `sitemap.xml`.
- `app/static/` : `css/style.css` (repris de la v1) et `js/main.js` (menu mobile, retour en haut, fondus `.fade-in` → `.visible`, formulaire de contact). Il n'y a pas d'i18n côté client.

### i18n (côté serveur)

- Les textes sont dans `translations/pt.json`, `fr.json` et `en.json`, qui doivent avoir **exactement les mêmes clés** (un test le vérifie). Tout nouveau texte demande une clé dans les trois fichiers.
- `app/i18n.py` : `t(cle, langue)` se replie sur `pt`, puis sur la clé elle-même. Dans les templates, `{{ t('cle') }}` utilise la langue de la page.
- La langue est le premier morceau de l'URL : `/pt/`, `/fr/`, `/en/`. Le sélecteur de langue est fait de simples liens (`url_pour_langue()` garde la page et les paramètres `?…`).
- `brancher_langue(blueprint)` (dans `i18n.py`) : tout blueprint dont les adresses commencent par `/<lang>/` l'appelle. Elle retire la langue de l'URL, la range dans `g.lang` (une langue inconnue donne une 404), et fait réutiliser `g.lang` par `url_for('<blueprint>.…')`.
- `<title>` (`{% block title %}`) et la description (`{% set description = t('meta_desc_…') %}`) sont traduits avec les clés `meta_title_*` et `meta_desc_*`. Une page définit `{% set robots = "noindex, follow" %}` pour ne pas être indexée : elle n'a alors ni `canonical` ni `hreflang`, et ne doit pas figurer dans le sitemap. Les pages de l'espace privé utilisent `noindex, nofollow`.
- Jinja échappe le HTML : les valeurs de traduction ne doivent pas contenir de balises.

### Formulaire de contact (`vitrine/contact.html` + `initContactForm` dans `main.js`)

- Envoi vers Formspree. L'identifiant vient de `data-formspree-id`. Tant qu'il vaut `YOUR_FORMSPREE_ID`, le formulaire affiche l'état `not-configured` au lieu d'envoyer.
- Les messages traduits sont passés à `main.js` par des attributs `data-msg-*` du formulaire.
- Les états sont des éléments `.form-state` d'id `state-<nom>` (`form`, `success`, `error`, `not-configured`), basculés par `showState()`. `#website` est un champ honeypot.
- Les champs `name`, `company`, `email` et `message` sont obligatoires, et les erreurs s'affichent dans `#error-<id>`.
- `?service=<valeur>` présélectionne `#service`. Les valeurs `recrutamento`, `organizacao-rh` et `formacao` des liens de la page Services doivent correspondre aux `<option>` (un test le vérifie). Les ancres `#recrutamento`, `#organizacao-rh` et `#formacoes` de la page Services sont liées depuis le pied de page.

### Espace Recrutement : connexion

- Tout formulaire POST de l'application doit contenir `<input name="csrf_token" type="hidden" value="{{ csrf_token() }}"/>`. Sans ce champ, il est refusé avec une erreur 400, et une page traduite s'affiche. Le formulaire de contact n'est pas concerné : il envoie ses données à Formspree.
- Les messages `flash()` et `login_manager.login_message` sont des **clés de traduction**, traduites au moment de l'affichage avec `t()`. Ce ne sont jamais des phrases.
- Connexion : un échec affiche un message neutre (`espace_login_error`), sans dire si c'est l'e-mail ou le mot de passe qui est faux. `verifier_identifiants()` calcule une empreinte factice quand l'e-mail est inconnu, pour que le temps de réponse soit le même. Le mot de passe n'est jamais renvoyé dans la page. En cas de succès, la session est vidée (`session.clear()`) avant `login_user()`, et on redirige **toujours** vers le tableau de bord : `?next=` est ignoré exprès (redirection ouverte).
- Déconnexion : en POST avec jeton CSRF uniquement, jamais par un simple lien.
- Limite de tentatives : `@limiter.limit(LIMITE_CONNEXION, methods=["POST"])`. Seuls les envois du formulaire comptent, et une fois la limite dépassée, même le bon mot de passe est refusé (429). Limites connues : les compteurs sont en mémoire (remis à zéro au redémarrage, non partagés entre plusieurs processus), et derrière un proxy, toutes les requêtes semblent venir de la même IP. Il faudra régler `ProxyFix` à la mise en ligne.
- `User` hérite de `UserMixin`. `current_user` est disponible dans les templates.

### Tests

- `tests/conftest.py` fournit les fixtures `app` (`create_app(TestConfig)`) et `client`.
- `test_i18n.py` (traductions), `test_vitrine.py` (chaque page × chaque langue, 404, menu, formulaire), `test_seo.py` (sitemap, robots, titres, hreflang), `test_models.py` (`Country`, `init-db`), `test_comptes.py` (`Company`, `User`, mots de passe, `create-admin`), `test_espace.py` (connexion, déconnexion, CSRF, limite de tentatives).
- La protection CSRF reste **activée** pendant les tests : un test qui envoie un formulaire récupère d'abord le jeton dans la page (voir `jeton()` dans `test_espace.py`). Les compteurs de Flask-Limiter repartent de zéro à chaque test, car chaque test crée sa propre application.
- Pour comparer un texte traduit au HTML, utilisez `markupsafe.escape(t(...))`, car Jinja échappe les apostrophes.

### Base de données

- Flask-SQLAlchemy, avec `db = SQLAlchemy()` défini dans `app/models.py` et relié à l'application par `db.init_app(app)` dans `create_app()`.
- Adresse de la base (`SQLALCHEMY_DATABASE_URI` dans `config.py`) : `sqlite:///mwene.db` en développement (Flask-SQLAlchemy place un chemin relatif dans `instance/`, donc `instance/mwene.db`), et `sqlite://` (en mémoire) pour les tests.
- Les clés étrangères sont vérifiées : SQLite ne le fait pas par défaut, donc un écouteur d'événement de `models.py` envoie `PRAGMA foreign_keys=ON` à chaque connexion. Ne le retirez pas : il empêche de rattacher un compte à une entreprise inexistante.
- `flask --app app init-db` crée les tables manquantes (`db.create_all()`) et ajoute les pays de `PAYS_INITIAUX` (uniquement l'Angola). Elle peut être relancée sans risque : elle n'efface rien et ne crée pas de doublon. Il n'y a pas encore d'outil de migration : `create_all()` ne modifie pas une table qui existe déjà.
- `flask --app app create-admin --email …` crée un administrateur Mwene (`is_admin`, sans entreprise). Le mot de passe est demandé deux fois sans être affiché. Il n'est volontairement pas accepté en option, pour ne pas rester dans l'historique du terminal. C'est à l'utilisateur de lancer cette commande lui-même : Claude ne doit ni choisir ni connaître ce mot de passe.
- Modèle `Country` : `code` (ISO 3166-1, 2 majuscules, unique), `langue_par_defaut` (une des `LANGUES`) et `devise` (ISO 4217, 3 majuscules). Des `@validates` refusent les valeurs mal formées. Le nom du pays n'est pas stocké : `nom(langue)` lit la clé `country_<code en minuscules>` dans les traductions. Ajouter un pays demande donc une ligne en base et cette clé dans les 3 fichiers JSON, sans modifier le code.
- Modèles `Company` (`nom` obligatoire, `country` obligatoire) et `User` :
  - `email` est unique et toujours enregistré en minuscules et sans espaces (`@validates`), pour que `Ana@X.com` et `ana@x.com` soient le même compte ;
  - `password_hash` est une empreinte scrypt (`werkzeug.security`), jamais le mot de passe. Passez toujours par `set_password()` (minimum `LONGUEUR_MIN_MOT_DE_PASSE` = 12 caractères) et `check_password()` ;
  - `__repr__` n'affiche pas l'empreinte ;
  - une contrainte de la base (`compte_client_avec_entreprise`) impose qu'un compte non administrateur ait une `company_id` : pas de compte client sans entreprise.
- Tests : la fixture `app` crée les tables avant chaque test et les supprime après. Elle n'ouvre le contexte d'application que pour ces deux opérations : s'il restait ouvert, les requêtes du client de test le réutiliseraient et partageraient le même `g` (donc `g.lang`). Dans un test qui utilise `db.session`, ouvrez `with app.app_context():` (voir la fixture `contexte` de `test_models.py` et `test_comptes.py`). Les mots de passe des tests sont des valeurs factices.
- Le fichier `.db` et le dossier `instance/` ne doivent jamais être commités (ils sont dans `.gitignore`). Ne lisez pas les fichiers `.db` (règle de `.claude/settings.json`).

## Règles

- Tout texte visible existe en PT, FR et EN.
- Le site doit pouvoir fonctionner pour plusieurs pays (pays, langue, devise).
- L'IA aide mais ne décide jamais à la place d'un humain.
- Les CV sont des données personnelles : consentement obligatoire, et accès limité à l'entreprise concernée.
- Ne jamais lire, ouvrir ni inspecter la base de données ou les fichiers du dossier `instance/` (base SQLite, CV envoyés), par aucun moyen : outil de lecture, `cat`/`head`/`strings`, script ou commande Python (`python -c`, `flask shell`), `sqlite3`, copie du fichier… sans l'accord explicite de l'utilisateur, demandé à chaque fois. Les règles `deny` de `.claude/settings.json` et le hook `.claude/hooks/proteger_instance.py` (qui bloque toute commande Bash contenant `instance/` ou `.db`) ne bloquent qu'une partie de ces moyens : cette règle s'applique même quand aucun outil ne l'empêche. Conséquence pratique du hook : une commande qui mentionne seulement ces textes, par exemple un message de commit ou un `grep`, est bloquée elle aussi. Il faut alors la reformuler, sans chercher à contourner le hook. Reste permis : lancer l'application et ses commandes (`flask run`, `flask init-db`), qui utilisent la base sans en afficher le contenu, et les tests, qui utilisent une base en mémoire.
- N'inventez aucune information sur l'entreprise : ni témoignages, ni logos clients, ni statistiques, ni coordonnées, ni prix. Les textes provisoires comme `[E-mail profissional a completar]` (`.contact-placeholder` dans `vitrine/contact.html`) sont volontaires, en attendant les vraies informations de la propriétaire.
- Les traductions FR/EN nouvelles sont à faire valider par la propriétaire (voir la section du README « Textes à faire valider »).

## Façon de travailler

- L'utilisateur est étudiant : explique chaque changement simplement avant de le faire.
- Avance par petites étapes, chacune testable seule.
- Demande son accord avant de modifier un fichier, de faire un commit ou un push.
- N'invente jamais d'informations (coordonnées, témoignages, chiffres, prix).
- Réponds en français.
