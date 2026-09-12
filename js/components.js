/**
 * Mwene Consulting — Composants HTML partagés
 * Header et footer injectés dynamiquement
 */

function getBasePath() {
  // Detect depth from root to set correct relative paths
  const path = window.location.pathname;
  if (path.includes('/fr/') || path.includes('/en/') || path.includes('/pt/')) return '../';
  return '';
}

function renderHeader(activePage) {
  const base = getBasePath();
  return `
<header class="site-header" role="banner">
  <div class="container">
    <div class="header-inner">
      <a href="${base}index.html" class="logo" data-i18n-aria="aria_logo" aria-label="Mwene Consulting — Accueil">
        <span class="logo-main">MWENE</span>
        <span class="logo-sub">Consulting</span>
      </a>
      <button class="menu-toggle" id="menu-toggle" aria-expanded="false" aria-controls="main-nav" aria-label="Ouvrir le menu">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">
          <line x1="3" y1="6" x2="21" y2="6"/>
          <line x1="3" y1="12" x2="21" y2="12"/>
          <line x1="3" y1="18" x2="21" y2="18"/>
        </svg>
      </button>
      <nav class="main-nav" id="main-nav" role="navigation" aria-label="Navigation principale">
        <a href="${base}index.html" class="nav-link${activePage==='home'?' active':''}" data-i18n="nav_home">Início</a>
        <a href="${base}services.html" class="nav-link${activePage==='services'?' active':''}" data-i18n="nav_services">Serviços</a>
        <a href="${base}about.html" class="nav-link${activePage==='about'?' active':''}" data-i18n="nav_about">Sobre</a>
        <a href="${base}contact.html" class="nav-link${activePage==='contact'?' active':''}" data-i18n="nav_contact">Contacto</a>
        <div class="lang-switcher" data-i18n-aria="aria_lang_select" role="group" aria-label="Sélecteur de langue">
          <button class="lang-btn" data-lang="pt" aria-label="Português">PT</button>
          <button class="lang-btn" data-lang="fr" aria-label="Français">FR</button>
          <button class="lang-btn" data-lang="en" aria-label="English">EN</button>
        </div>
      </nav>
    </div>
  </div>
</header>`;
}

function renderFooter() {
  const base = getBasePath();
  return `
<footer class="site-footer" role="contentinfo">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <a href="${base}index.html" class="logo" aria-label="Mwene Consulting">
          <span class="logo-main">MWENE</span>
          <span class="logo-sub">Consulting</span>
        </a>
        <p data-i18n="footer_tagline">Apoio em recursos humanos para PME em Angola.</p>
        <p class="footer-note" data-i18n="footer_note">Site em fase de preparação. Informações de contacto a completar.</p>
      </div>
      <div class="footer-col">
        <h4 data-i18n="footer_services">Serviços</h4>
        <ul>
          <li><a href="${base}services.html#recrutamento" data-i18n="footer_recruitment">Apoio ao recrutamento</a></li>
          <li><a href="${base}services.html#organizacao-rh" data-i18n="footer_hr_org">Organização de RH</a></li>
          <li><a href="${base}services.html#formacoes" data-i18n="footer_training">Formações</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4 data-i18n="footer_legal">Legal</h4>
        <ul>
          <li><a href="${base}mentions-legales.html" data-i18n="footer_mentions">Menções legais</a></li>
          <li><a href="${base}confidentialite.html" data-i18n="footer_privacy">Política de privacidade</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4 data-i18n="footer_contact_us">Contacto</h4>
        <ul>
          <li><a href="${base}contact.html" data-i18n="home_cta_primary">Vamos falar do seu projeto</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© <span id="footer-year"></span> Mwene Consulting. <span data-i18n="footer_rights">Todos os direitos reservados.</span></span>
    </div>
  </div>
</footer>
<button class="back-to-top" id="back-to-top" aria-label="Voltar ao topo">
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true">
    <polyline points="18 15 12 9 6 15"/>
  </svg>
</button>`;
}

function injectComponents(activePage) {
  const headerEl = document.getElementById('site-header');
  const footerEl = document.getElementById('site-footer');
  if (headerEl) headerEl.outerHTML = renderHeader(activePage);
  if (footerEl) footerEl.outerHTML = renderFooter();
  // Set footer year
  const yearEl = document.getElementById('footer-year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();
}