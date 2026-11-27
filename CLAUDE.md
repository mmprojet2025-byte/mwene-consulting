# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projet

Site vitrine statique et trilingue (PT par défaut, FR, EN) de Mwene Consulting, cabinet de conseil en RH pour les PME en Angola. HTML/CSS/JS natif : pas d'étape de build, pas de gestionnaire de paquets, pas de tests, pas de serveur. Le formulaire de contact envoie ses données à Formspree. Version 1.0, pas encore publiée. `README.md` est le guide destiné à la propriétaire du site et contient la liste des tâches avant mise en ligne (section 7).

## Lancer le site en local

Il n'y a rien à compiler. Servez le dossier racine avec n'importe quel serveur statique, par exemple `python3 -m http.server 8000`, puis ouvrez `http://localhost:8000/`. Le README recommande l'extension Live Server de VS Code. Ouvrir `index.html` directement en `file://` fonctionne aussi.

## Architecture

Toutes les pages ont le même squelette : des emplacements vides `<div id="site-header">` / `<div id="site-footer">`, puis trois scripts chargés **dans cet ordre** (ils partagent des variables globales, sans modules) :

1. `js/translations.js` définit `TRANSLATIONS` (objets `pt` / `fr` / `en` aux clés identiques) ainsi que le moteur i18n : `t(key)` (repli sur `pt`, puis sur la clé elle-même), `applyTranslations()`, `switchLang()`, `initLang()`.
2. `js/components.js` contient `renderHeader()` / `renderFooter()` sous forme de template strings. `injectComponents()` remplace les emplacements : la navigation, le sélecteur de langue, le pied de page et le bouton de retour en haut se modifient donc ici, pas dans les pages HTML.
3. `js/main.js` s'exécute au `DOMContentLoaded` : injection des composants → `initLang()` → branchement de la navigation, du retour en haut, des fondus, des boutons de langue et du formulaire de contact. Les composants doivent être injectés avant la traduction et la pose des écouteurs d'événements.

### i18n

- Le texte est traduit côté client grâce à des attributs : `data-i18n` (textContent), `data-i18n-placeholder`, `data-i18n-aria` (aria-label), `data-i18n-title`. Le texte écrit en dur dans le HTML sert de repli en portugais ; gardez-le identique à la valeur `pt`.
- Tout nouveau texte a besoin d'une clé dans **les trois** objets de langue de `translations.js`.
- Choix de la langue : paramètre d'URL `?lang=` → `localStorage['mc_lang']` → `pt`. `switchLang()` met à jour `?lang=` avec `history.replaceState` (sans rechargement) et définit `<html lang>`.
- `<title>` et `<meta name="description">` sont en portugais en dur et **ne sont pas** traduits.
- `data-i18n` définit `textContent`, donc les valeurs de traduction ne peuvent pas contenir de HTML.

### Formulaire de contact (`contact.html` + `initContactForm` dans `main.js`)

- L'identifiant Formspree vient de l'attribut `data-formspree-id`. Tant qu'il vaut `YOUR_FORMSPREE_ID`, l'envoi affiche l'état `not-configured` au lieu d'envoyer.
- Les états de l'interface sont des éléments `.form-state` d'id `state-<nom>` (`form`, `success`, `error`, `not-configured`), basculés par `showState()`.
- `#website` est un champ honeypot. Les champs `name`, `company`, `email` et `message` sont obligatoires, et les erreurs s'affichent dans `#error-<id>`.
- `?service=<valeur>` présélectionne le `<select>` `#service`. Les liens de la page Services utilisent `recrutamento`, `organizacao-rh` et `formacao`, qui doivent correspondre aux valeurs des `<option>`.

### Autres remarques

- Les ancres de services de `services.html` (`#recrutamento`, `#organizacao-rh`, `#formacoes`) sont liées depuis le pied de page. `services.html` contient un script en ligne qui refait défiler jusqu'à l'ancre après l'injection.
- `getBasePath()` dans `components.js` et `detectLang()` dans `translations.js` prévoient d'éventuels sous-dossiers `/fr/`, `/en/`, `/pt/` qui n'existent pas encore. Toutes les pages sont actuellement à la racine.
- Les éléments `.fade-in` apparaissent grâce à un IntersectionObserver qui ajoute `.visible`.
- Tous les styles sont dans `css/style.css`. Les polices sont Poppins et Inter, chargées depuis Google Fonts. Le favicon est un data URI SVG répété dans le `<head>` de chaque page.

## Contraintes sur le contenu

- N'inventez aucune information sur l'entreprise. Le README précise que le site ne contient ni témoignages, ni logos clients, ni statistiques, ni coordonnées inventés. Les textes provisoires comme `[E-mail profissional a completar]` (`.contact-placeholder` dans `contact.html`) sont volontaires, en attendant que la propriétaire fournisse les vraies informations.
- `sitemap.xml` et `robots.txt` utilisent le domaine provisoire `VOTRE-DOMAINE.com`.
