/**
 * Mwene Consulting — Script principal (v2)
 * Menu mobile, retour en haut, fondus au défilement, formulaire de contact.
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

/* ── Formulaire de contact ──────────────────────────────────── */
// Même logique que la v1. Seule différence : les messages traduits
// viennent des attributs data-msg-* du formulaire (contact.html).
function initContactForm() {
  const form = document.getElementById('contact-form');
  if (!form) return;

  const msg = {
    required: form.dataset.msgRequired,
    email:    form.dataset.msgEmail,
    sending:  form.dataset.msgSending,
    submit:   form.dataset.msgSubmit,
  };

  // Présélection du service depuis l'URL (?service=recrutamento)
  const params = new URLSearchParams(window.location.search);
  const serviceParam = params.get('service');
  if (serviceParam) {
    const sel = form.querySelector('#service');
    if (sel) sel.value = serviceParam;
  }

  // Aides à la validation
  function getVal(id) { return (form.querySelector('#' + id) || {}).value || ''; }
  function showError(id, text) {
    const el = form.querySelector('#error-' + id);
    const input = form.querySelector('#' + id);
    if (el) { el.textContent = text; el.classList.add('visible'); }
    if (input) { input.classList.add('error'); input.setAttribute('aria-invalid', 'true'); }
  }
  function clearError(id) {
    const el = form.querySelector('#error-' + id);
    const input = form.querySelector('#' + id);
    if (el) { el.textContent = ''; el.classList.remove('visible'); }
    if (input) { input.classList.remove('error'); input.removeAttribute('aria-invalid'); }
  }
  function validateEmail(v) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v); }

  function validate() {
    let ok = true;
    const fields = ['name', 'company', 'email', 'message'];
    fields.forEach(f => clearError(f));

    if (!getVal('name').trim()) { showError('name', msg.required); ok = false; }
    if (!getVal('company').trim()) { showError('company', msg.required); ok = false; }
    if (!getVal('email').trim()) { showError('email', msg.required); ok = false; }
    else if (!validateEmail(getVal('email').trim())) { showError('email', msg.email); ok = false; }
    if (!getVal('message').trim()) { showError('message', msg.required); ok = false; }
    return ok;
  }

  // Validation en direct quand on quitte un champ
  ['name', 'company', 'email', 'message'].forEach(id => {
    const el = form.querySelector('#' + id);
    if (!el) return;
    el.addEventListener('blur', () => {
      clearError(id);
      if (!el.value.trim()) { showError(id, msg.required); }
      else if (id === 'email' && !validateEmail(el.value.trim())) { showError(id, msg.email); }
    });
    el.addEventListener('input', () => clearError(id));
  });

  // Formspree est-il configuré ?
  const FORMSPREE_ID = form.getAttribute('data-formspree-id') || '';
  const isConfigured = FORMSPREE_ID && FORMSPREE_ID !== 'YOUR_FORMSPREE_ID';

  // Avertissement si ce n'est pas le cas
  const notice = document.getElementById('not-configured-notice');
  if (notice && !isConfigured) notice.style.display = 'block';

  function showState(name) {
    document.querySelectorAll('.form-state').forEach(s => s.classList.remove('active'));
    const el = document.getElementById('state-' + name);
    if (el) el.classList.add('active');
  }

  let sending = false;

  form.addEventListener('submit', async e => {
    e.preventDefault();
    if (sending) return;
    if (!validate()) { form.querySelector('.error')?.focus(); return; }

    // Honeypot : un robot a rempli le champ caché
    const honey = form.querySelector('#website');
    if (honey && honey.value) return;

    if (!isConfigured) {
      showState('not-configured');
      return;
    }

    sending = true;
    const submitBtn = form.querySelector('[type="submit"]');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = msg.sending;
    }

    // On garde les données en cas d'erreur
    const formData = {
      name: getVal('name'),
      company: getVal('company'),
      email: getVal('email'),
      phone: getVal('phone'),
      service: getVal('service'),
      message: getVal('message'),
    };

    try {
      const res = await fetch('https://formspree.io/f/' + FORMSPREE_ID, {
        method: 'POST',
        headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      if (res.ok) {
        showState('success');
        form.reset();
      } else {
        throw new Error('Server error ' + res.status);
      }
    } catch (err) {
      console.error('Form error:', err);
      // On remet les données dans le formulaire
      Object.entries(formData).forEach(([k, v]) => {
        const el = form.querySelector('#' + k);
        if (el) el.value = v;
      });
      showState('error');
    } finally {
      sending = false;
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = msg.submit;
      }
    }
  });

  // Bouton « Réessayer »
  const retryBtn = document.getElementById('retry-btn');
  if (retryBtn) {
    retryBtn.addEventListener('click', () => showState('form'));
  }
}

/* ── Démarrage ──────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initMobileNav();
  initBackToTop();
  initFadeIn();
  initContactForm();
});
