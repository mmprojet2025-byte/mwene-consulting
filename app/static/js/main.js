/**
 * Mwene Consulting — Script principal (v2)
 * Menu mobile, retour en haut, fondus au défilement.
 *
 * Les textes sont déjà traduits par le serveur : plus besoin du moteur i18n.
 * Les libellés du bouton de menu viennent des attributs data-label-open /
 * data-label-close, remplis par le template header.html.
 */

/* ── Navigation mobile ──────────────────────────────────────── */
function initMobileNav() {
  const toggle = document.getElementById('menu-toggle');
  const nav    = document.getElementById('main-nav');
  if (!toggle || !nav) return;

  const labelOpen  = toggle.dataset.labelOpen;
  const labelClose = toggle.dataset.labelClose;

  function closeMenu() {
    nav.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', labelOpen);
  }

  toggle.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open);
    toggle.setAttribute('aria-label', open ? labelClose : labelOpen);
  });

  // Fermer en cliquant à l'extérieur
  document.addEventListener('click', e => {
    if (!nav.contains(e.target) && !toggle.contains(e.target)) {
      closeMenu();
    }
  });

  // Fermer avec Échap
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && nav.classList.contains('open')) {
      closeMenu();
      toggle.focus();
    }
  });
}

/* ── Retour en haut ─────────────────────────────────────────── */
function initBackToTop() {
  const btn = document.getElementById('back-to-top');
  if (!btn) return;
  window.addEventListener('scroll', () => {
    btn.classList.toggle('visible', window.scrollY > 400);
  }, { passive: true });
  btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
}

/* ── Fondus au défilement ───────────────────────────────────── */
function initFadeIn() {
  if (!('IntersectionObserver' in window)) {
    document.querySelectorAll('.fade-in').forEach(el => el.classList.add('visible'));
    return;
  }
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); obs.unobserve(e.target); } });
  }, { threshold: 0.12 });
  document.querySelectorAll('.fade-in').forEach(el => obs.observe(el));
}

/* ── Démarrage ──────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initMobileNav();
  initBackToTop();
  initFadeIn();
});
