/* =========================================================
   INTEGRI Forensic and Protection Services — interactions
   Vanilla JS, no dependencies. Shared by every page.
   FROZEN FILE — see BRAND.md §5
   ========================================================= */
(function () {
  'use strict';

  var $  = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Header state, scroll progress, to-top, action bar ---------- */
  var header    = $('#siteHeader');
  var progress  = $('#scrollProgress');
  var toTop     = $('#toTop');
  var actionBar = $('.action-bar');

  function onScroll() {
    var y   = window.pageYOffset;
    var max = document.documentElement.scrollHeight - window.innerHeight;

    if (header) header.classList.toggle('scrolled', y > 20);
    if (progress) progress.style.width = (max > 0 ? (y / max) * 100 : 0) + '%';
    if (toTop) toTop.classList.toggle('show', y > 600);
    if (actionBar) actionBar.classList.toggle('show', y > 240);
  }

  var ticking = false;
  window.addEventListener('scroll', function () {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () { onScroll(); ticking = false; });
  }, { passive: true });
  onScroll();

  if (toTop) {
    toTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: reduced ? 'auto' : 'smooth' });
    });
  }

  /* ---------- Mobile drawer ---------- */
  var hamburger  = $('#hamburger');
  var mobileMenu = $('#mobileMenu');

  function setMenu(open) {
    if (!mobileMenu || !hamburger) return;
    mobileMenu.classList.toggle('open', open);
    hamburger.classList.toggle('open', open);
    hamburger.setAttribute('aria-expanded', open ? 'true' : 'false');
    hamburger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    mobileMenu.setAttribute('aria-hidden', open ? 'false' : 'true');
    document.body.style.overflow = open ? 'hidden' : '';
  }

  if (hamburger) {
    hamburger.addEventListener('click', function () {
      setMenu(!mobileMenu.classList.contains('open'));
    });
  }
  if (mobileMenu) {
    // close on backdrop click or on any link tap
    mobileMenu.addEventListener('click', function (e) {
      if (e.target === mobileMenu || e.target.closest('a')) setMenu(false);
    });
  }
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && mobileMenu && mobileMenu.classList.contains('open')) setMenu(false);
  });

  /* ---------- Scroll reveal ---------- */
  var revealEls = $$('.reveal');
  if ('IntersectionObserver' in window && !reduced) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('in'); });
  }

  /* ---------- Animated counters (data-count) ---------- */
  function animateCount(el) {
    var target = parseFloat(el.getAttribute('data-count'));
    if (isNaN(target)) return;
    var suffix   = el.getAttribute('data-suffix') || '';
    var duration = 1400;
    var start    = null;

    function step(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased) + suffix;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  var counters = $$('[data-count]');
  if (counters.length) {
    if ('IntersectionObserver' in window && !reduced) {
      var cio = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) { animateCount(en.target); cio.unobserve(en.target); }
        });
      }, { threshold: 0.5 });
      counters.forEach(function (c) { cio.observe(c); });
    } else {
      counters.forEach(function (c) {
        c.textContent = c.getAttribute('data-count') + (c.getAttribute('data-suffix') || '');
      });
    }
  }

  /* ---------- Smooth in-page anchors, offset for the fixed header ---------- */
  $$('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var id = a.getAttribute('href');
      if (!id || id === '#' || id.length < 2) return;
      var target = document.getElementById(id.slice(1));
      if (!target) return;
      e.preventDefault();
      var offset = parseInt(getComputedStyle(document.documentElement)
                    .getPropertyValue('--header-h'), 10) || 74;
      var top = target.getBoundingClientRect().top + window.pageYOffset - offset - 12;
      window.scrollTo({ top: top, behavior: reduced ? 'auto' : 'smooth' });
      history.replaceState(null, '', id);
    });
  });

  /* ---------- Contact form: validate, then hand off to the mail client ---------- */
  var form = $('#contactForm');
  var note = $('#formNote');

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!note) return;

      // Read fields via form.elements — `form.name` happens to work (HTMLFormElement is
      // [LegacyOverrideBuiltIns], so the named-element getter beats the built-in `name`
      // property) but it reads like a bug, so go through elements explicitly.
      function field(n) {
        var el = form.elements.namedItem(n);
        return el && typeof el.value === 'string' ? el.value.trim() : '';
      }

      var name    = field('name');
      var email   = field('email');
      var service = field('service');
      var message = field('message');

      note.className = 'form__note';

      if (!name || !email || !message) {
        note.textContent = 'Please complete your name, email address and message.';
        note.classList.add('err');
        return;
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        note.textContent = 'That email address does not look right — please check it.';
        note.classList.add('err');
        return;
      }

      var subject = 'Website enquiry' + (service ? ' — ' + service : '');
      var body    = 'Name: ' + name +
                    '\nEmail: ' + email +
                    (service ? '\nService: ' + service : '') +
                    '\n\n' + message;

      window.location.href = 'mailto:ops@integriforensicandprotectionservices.com'
        + '?subject=' + encodeURIComponent(subject)
        + '&body='    + encodeURIComponent(body);

      note.textContent = 'Opening your email app — if nothing happens, write to us directly at ops@integriforensicandprotectionservices.com';
      note.classList.add('ok');
      form.reset();
    });
  }

  /* ---------- Current year in the footer ---------- */
  $$('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
