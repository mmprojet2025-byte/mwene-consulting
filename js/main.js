/**
 * Mwene Consulting — Script principal
 * Navigation mobile, back-to-top, animations, formulaire
 */

/* ── Navigation mobile ──────────────────────────────────────── */
function initMobileNav() {
  const toggle = document.getElementById('menu-toggle');
  const nav    = document.getElementById('main-nav');
  if (!toggle || !nav) return;

  function closeMenu() {
    nav.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', t('aria_menu_open'));
  }

  toggle.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open);
    toggle.setAttribute('aria-label', open
      ? (window.t ? window.t('aria_menu_close') : 'Fermer le menu')
      : (window.t ? window.t('aria_menu_open')  : 'Ouvrir le menu'));
  });

  // Close on outside click
  document.addEventListener('click', e => {
    if (!nav.contains(e.target) && !toggle.contains(e.target)) {
      closeMenu();
    }
  });

  // Close on Escape
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && nav.classList.contains('open')) {
      closeMenu();
      toggle.focus();
    }
  });
}

/* ── Active nav link ────────────────────────────────────────── */
function setActiveNav() {
  const page = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-link').forEach(link => {
    const href = link.getAttribute('href') || '';
    const linkPage = href.split('/').pop() || 'index.html';
    link.classList.toggle('active', linkPage === page);
    link.setAttribute('aria-current', linkPage === page ? 'page' : 'false');
  });
}

/* ── Back to top ────────────────────────────────────────────── */
function initBackToTop() {
  const btn = document.getElementById('back-to-top');
  if (!btn) return;
  window.addEventListener('scroll', () => {
    btn.classList.toggle('visible', window.scrollY > 400);
  }, { passive: true });
  btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
}

/* ── Fade-in on scroll ──────────────────────────────────────── */
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

/* ── Language switcher ──────────────────────────────────────── */
function initLangSwitcher() {
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const lang = btn.getAttribute('data-lang');
      if (typeof switchLang === 'function') switchLang(lang);
    });
  });
}

/* ── Contact form ───────────────────────────────────────────── */
function initContactForm() {
  const form = document.getElementById('contact-form');
  if (!form) return;

  // Pre-select service from URL param
  const params = new URLSearchParams(window.location.search);
  const serviceParam = params.get('service');
  if (serviceParam) {
    const sel = form.querySelector('#service');
    if (sel) sel.value = serviceParam;
  }

  // Validation helpers
  function getVal(id) { return (form.querySelector('#' + id) || {}).value || ''; }
  function showError(id, msg) {
    const el = form.querySelector('#error-' + id);
    const input = form.querySelector('#' + id);
    if (el) { el.textContent = msg; el.classList.add('visible'); }
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

    if (!getVal('name').trim()) { showError('name', t('contact_field_required')); ok = false; }
    if (!getVal('company').trim()) { showError('company', t('contact_field_required')); ok = false; }
    if (!getVal('email').trim()) { showError('email', t('contact_field_required')); ok = false; }
    else if (!validateEmail(getVal('email').trim())) { showError('email', t('contact_invalid_email')); ok = false; }
    if (!getVal('message').trim()) { showError('message', t('contact_field_required')); ok = false; }
    return ok;
  }

  // Live validation on blur
  ['name', 'company', 'email', 'message'].forEach(id => {
    const el = form.querySelector('#' + id);
    if (!el) return;
    el.addEventListener('blur', () => {
      clearError(id);
      if (!el.value.trim()) { showError(id, t('contact_field_required')); }
      else if (id === 'email' && !validateEmail(el.value.trim())) { showError(id, t('contact_invalid_email')); }
    });
    el.addEventListener('input', () => clearError(id));
  });

  // Check if Formspree is configured
  const FORMSPREE_ID = form.getAttribute('data-formspree-id') || '';
  const isConfigured = FORMSPREE_ID && FORMSPREE_ID !== 'YOUR_FORMSPREE_ID';

  // Show notice if not configured
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

    // Honeypot check
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
      submitBtn.textContent = t('contact_sending');
    }

    // Save form data in case of error
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
      // Restore form data
      Object.entries(formData).forEach(([k, v]) => {
        const el = form.querySelector('#' + k);
        if (el) el.value = v;
      });
      showState('error');
    } finally {
      sending = false;
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = t('contact_submit');
      }
    }
  });

  // Retry button
  const retryBtn = document.getElementById('retry-btn');
  if (retryBtn) {
    retryBtn.addEventListener('click', () => showState('form'));
  }
}

/* ── Init ───────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  // Shared components must exist before translation and event binding.
  injectComponents();
  if (typeof initLang === 'function') initLang();
  initMobileNav();
  setActiveNav();
  initBackToTop();
  initFadeIn();
  initLangSwitcher();
  initContactForm();
  // Expose t() globally for form validation messages
  window.t = typeof t === 'function' ? t : (k => k);
});