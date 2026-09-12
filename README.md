# Mwene Consulting — Guide du projet

**Version du site : 1.0 — Septembre 2026**
**Fondatrice : Ritatelma Fernandes Ambrosio**

---

## Sommaire

1. [Structure du projet](#1-structure-du-projet)
2. [Ouvrir le projet dans VS Code](#2-ouvrir-le-projet-dans-vs-code)
3. [Lancer le site localement](#3-lancer-le-site-localement)
4. [Modifier les textes et traductions](#4-modifier-les-textes-et-traductions)
5. [Renseigner les coordonnées](#5-renseigner-les-coordonnées)
6. [Activer le formulaire de contact](#6-activer-le-formulaire-de-contact)
7. [Ce qui reste à compléter avant publication](#7-ce-qui-reste-à-compléter-avant-publication)
8. [Mettre le site en ligne](#8-mettre-le-site-en-ligne)

---

## 1. Structure du projet

```
mwene-consulting/
├── index.html              ← Page Accueil
├── services.html           ← Page Nos services
├── about.html              ← Page À propos
├── contact.html            ← Page Contact
├── mentions-legales.html   ← Mentions légales
├── confidentialite.html    ← Politique de confidentialité
├── 404.html                ← Page introuvable
├── sitemap.xml             ← Plan du site (à mettre à jour avec le domaine)
├── robots.txt              ← Instructions pour les moteurs de recherche
├── README.md               ← Ce guide
├── css/
│   └── style.css           ← Toute la mise en forme du site
└── js/
    ├── translations.js     ← Tous les textes en PT, FR et EN
    ├── components.js       ← En-tête et pied de page partagés
    └── main.js             ← Navigation, formulaire, animations
```

---

## 2. Ouvrir le projet dans VS Code

1. Décompressez le fichier ZIP dans le dossier de votre choix.
2. Ouvrez VS Code.
3. Cliquez sur **Fichier → Ouvrir le dossier** et sélectionnez le dossier `mwene-consulting`.
4. Vous verrez tous les fichiers dans le panneau de gauche.

**Extension recommandée :** installez **Live Server** (ritwickdey.LiveServer) depuis l'onglet Extensions de VS Code. Elle permet de voir le site en direct dans votre navigateur.

---

## 3. Lancer le site localement

### Avec Live Server (recommandé)

1. Installez l'extension **Live Server** dans VS Code.
2. Faites un clic droit sur `index.html` dans le panneau de fichiers.
3. Cliquez sur **Open with Live Server**.
4. Le site s'ouvre automatiquement dans votre navigateur.

Toute modification d'un fichier est visible immédiatement sans recharger manuellement.

### Sans extension (alternative)

Ouvrez simplement `index.html` dans votre navigateur en double-cliquant dessus.

> ⚠️ Le formulaire de contact ne fonctionnera pas en local tant que Formspree n'est pas configuré. C'est normal — voir section 6.

---

## 4. Modifier les textes et traductions

**Tous les textes du site se trouvent dans un seul fichier :**

```
js/translations.js
```

Ce fichier contient trois sections : `pt` (portugais), `fr` (français), `en` (anglais).

### Exemple : modifier le titre de la page d'accueil

Recherchez `home_hero_title` dans `translations.js` :

```javascript
pt: {
  home_hero_title: "Recrute e acompanhe as suas equipas com a Mwene Consulting",
  ...
},
fr: {
  home_hero_title: "Recrutez et accompagnez vos équipes avec Mwene Consulting",
  ...
},
en: {
  home_hero_title: "Recruit and support your teams with Mwene Consulting",
  ...
}
```

Modifiez le texte entre guillemets dans la langue souhaitée, enregistrez le fichier, et la modification apparaît immédiatement dans le navigateur.

### Règles importantes

- Ne modifiez pas les clés (ex. `home_hero_title`) — seulement les valeurs entre guillemets.
- Si un texte contient une apostrophe (`'`), utilisez `\'` ou remplacez par `"..."`.
- Modifiez les trois langues pour maintenir la cohérence.

---

## 5. Renseigner les coordonnées

Les coordonnées directes (email, WhatsApp, LinkedIn) ne sont pas encore renseignées. Voici comment les ajouter.

### Email professionnel

Dans `contact.html`, recherchez :

```html
<span class="contact-placeholder">[E-mail profissional a completar]</span>
```

Remplacez par :

```html
<a href="mailto:contact@mweneconsulting.com">contact@mweneconsulting.com</a>
```

### WhatsApp

Dans `contact.html`, recherchez :

```html
<span class="contact-placeholder">[WhatsApp profissional a completar]</span>
```

Remplacez par (en adaptant le numéro au format international) :

```html
<a href="https://wa.me/33600000000" target="_blank" rel="noopener">+33 6 00 00 00 00</a>
```

### LinkedIn

Dans `contact.html`, recherchez :

```html
<span class="contact-placeholder">[LinkedIn à compléter]</span>
```

Remplacez par :

```html
<a href="https://linkedin.com/company/mwene-consulting" target="_blank" rel="noopener">Mwene Consulting sur LinkedIn</a>
```

### Pied de page

Le pied de page est généré par `js/components.js`. Pour y ajouter des liens de contact, modifiez la fonction `renderFooter()` dans ce fichier.

---

## 6. Activer le formulaire de contact

Le formulaire utilise **Formspree** — un service gratuit qui reçoit les messages et les envoie par email. Aucun serveur n'est nécessaire.

### Étape 1 : Créer un compte Formspree

1. Allez sur [formspree.io](https://formspree.io)
2. Créez un compte gratuit avec l'adresse email professionnelle de Mwene Consulting.

### Étape 2 : Créer un formulaire

1. Dans votre tableau de bord Formspree, cliquez sur **New Form**.
2. Donnez-lui un nom (ex. : "Mwene Consulting — Contact").
3. Formspree vous donne un identifiant de formulaire, par exemple : `xpwzabcd`

### Étape 3 : Configurer le site

Dans `contact.html`, recherchez cette ligne :

```html
<form id="contact-form" novalidate data-formspree-id="YOUR_FORMSPREE_ID" ...>
```

Remplacez `YOUR_FORMSPREE_ID` par votre identifiant Formspree :

```html
<form id="contact-form" novalidate data-formspree-id="xpwzabcd" ...>
```

### Étape 4 : Vérifier la réception

1. Ouvrez la page Contact dans votre navigateur.
2. Remplissez le formulaire avec vos propres coordonnées.
3. Cliquez sur **Envoyer**.
4. Vérifiez que vous recevez bien l'email dans la boîte associée à Formspree.

### Protection anti-spam

Le formulaire inclut déjà :
- Un champ honeypot invisible (les robots le remplissent, les humains non).
- La validation côté navigateur avant envoi.
- Formspree ajoute sa propre protection anti-spam côté serveur.

### ⚠️ Important — Sécurité

Ne placez jamais de mot de passe, clé API secrète ou token d'accès dans les fichiers JavaScript publics. L'identifiant Formspree est public par conception — c'est prévu ainsi.

---

## 7. Ce qui reste à compléter avant publication

### Indispensable avant mise en ligne

| Élément | Où modifier | Statut |
|---|---|---|
| Email professionnel | `contact.html` — section coordonnées | ⬜ À compléter |
| Numéro WhatsApp | `contact.html` — section coordonnées | ⬜ À compléter |
| Lien LinkedIn | `contact.html` — section coordonnées | ⬜ À compléter |
| Identifiant Formspree | `contact.html` — attribut `data-formspree-id` | ⬜ À configurer |
| Mentions légales | `mentions-legales.html` | ⬜ À compléter |
| Politique de confidentialité | `confidentialite.html` | ⬜ À compléter |
| Domaine du site | `sitemap.xml` et `robots.txt` | ⬜ À remplacer |
| Validation des textes FR | `js/translations.js` — section `fr` | ⬜ À valider par Ritatelma |
| Validation des textes PT | `js/translations.js` — section `pt` | ⬜ À relire par locuteur natif |
| Validation des textes EN | `js/translations.js` — section `en` | ⬜ À valider |

### Facultatif

| Élément | Où modifier | Statut |
|---|---|---|
| Photo de Ritatelma | `about.html` — remplacer le bloc `.founder-visual` | ⬜ Facultatif |
| Logo définitif | `css/style.css` et `js/components.js` | ⬜ Facultatif |
| Confirmation des services assurables | `js/translations.js` — textes des services | ⬜ À valider par Ritatelma |

### Ajouter une photo (si disponible)

Dans `about.html`, remplacez le bloc :

```html
<div class="founder-visual fade-in" ...>
  <div class="founder-initials" aria-hidden="true">RFA</div>
  ...
</div>
```

Par :

```html
<div class="founder-visual fade-in">
  <img src="images/ritatelma.jpg" alt="Ritatelma Fernandes Ambrosio, fondatrice de Mwene Consulting"
       style="width:100%; border-radius:12px; margin-bottom:16px;">
  <div class="founder-name">Ritatelma Fernandes Ambrosio</div>
  <div class="founder-role">Fondatrice · Mwene Consulting</div>
</div>
```

Placez la photo dans le dossier `images/` sous le nom `ritatelma.jpg`.

---

## 8. Mettre le site en ligne

### Option A — Hébergement simple (recommandé pour démarrer)

**Netlify** (gratuit, très simple) :

1. Allez sur [netlify.com](https://netlify.com) et créez un compte.
2. Glissez-déposez le dossier `mwene-consulting` sur la page d'accueil Netlify.
3. Le site est en ligne en moins d'une minute avec une URL temporaire.
4. Connectez votre domaine dans les paramètres.

**GitHub Pages** (gratuit) :

1. Créez un compte sur [github.com](https://github.com).
2. Créez un dépôt public et uploadez les fichiers.
3. Activez GitHub Pages dans les paramètres du dépôt.

### Option B — Hébergement classique

Uploadez tous les fichiers du dossier `mwene-consulting` à la racine de votre hébergement via FTP (FileZilla ou équivalent).

### Après mise en ligne

1. Remplacez `VOTRE-DOMAINE.com` dans `sitemap.xml` et `robots.txt` par votre vrai domaine.
2. Testez le formulaire avec un vrai envoi.
3. Vérifiez l'affichage sur mobile et sur ordinateur.
4. Vérifiez les trois langues.

---

## Bilan honnête du projet

### Ce qui a été réalisé

- ✅ 4 pages principales (Accueil, Services, À propos, Contact)
- ✅ 2 pages légales (Mentions légales, Confidentialité)
- ✅ Page 404
- ✅ 3 langues complètes (PT, FR, EN) dans un fichier centralisé
- ✅ Sélecteur de langue fonctionnel avec mémorisation
- ✅ Présélection du service sur la page Contact depuis les boutons de services
- ✅ Formulaire avec validation, états (succès, erreur, envoi), protection honeypot
- ✅ Navigation mobile (menu hamburger)
- ✅ Design responsive (mobile, tablette, ordinateur)
- ✅ Animations légères au scroll (respecte prefers-reduced-motion)
- ✅ Navigation au clavier et focus visible
- ✅ Hiérarchie des titres cohérente
- ✅ Aucune information inventée
- ✅ Aucun témoignage, logo client ou statistique fictif
- ✅ Sitemap et robots.txt préparés
- ✅ Favicon intégré

### Ce qui a été testé en local

- ✅ Structure HTML valide sur toutes les pages
- ✅ Liens entre pages vérifiés
- ✅ Changement de langue fonctionnel
- ✅ Validation du formulaire (champs obligatoires, format email)
- ✅ États du formulaire (succès, erreur, non configuré)
- ✅ Menu mobile (ouverture, fermeture, Escape)
- ✅ Présélection du service via paramètre URL

### Ce qui reste à configurer

- ⬜ Formspree : test de réception réelle impossible sans compte configuré
- ⬜ Coordonnées directes (email, WhatsApp, LinkedIn) non encore renseignées
- ⬜ Mentions légales et politique de confidentialité à compléter avec les vraies informations

### Ce qui doit être validé par Ritatelma avant publication

- ⬜ Tous les textes dans les trois langues (en particulier le portugais)
- ⬜ Les services présentés correspondent bien aux prestations qu'elle peut assurer
- ⬜ Les informations légales de l'entreprise
- ⬜ Le choix du domaine et de l'hébergeur

---

*Mwene Consulting — Site web v1.0 — Septembre 2026*