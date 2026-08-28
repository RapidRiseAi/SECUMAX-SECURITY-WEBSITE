/* =========================================================
   Greyman Protection: interactions
   Vanilla JS, no dependencies. Shared by every page.
   FROZEN FILE: see BRAND.md §5
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

  /* ---------- Contact form ----------
     Posts to /api/contact, which the Worker relays to the ops mailbox through
     Resend. This is progressive enhancement over a real <form action method>:
     with JavaScript off the browser posts natively and the Worker answers with
     a confirmation page instead of JSON.

     The previous version handed off to mailto:, which only worked for visitors
     with a desktop mail client configured. On a phone, or on webmail, it did
     nothing while still saying "sent", so enquiries were being lost. The
     status messages below only ever claim what the server actually confirmed. */
  var form = $('#contactForm');
  var formNote = $('#formNote');

  if (form) {
    var stamp = $('#formTs');
    var submit = $('#formSubmit');
    var submitLabel = submit ? submit.textContent : '';
    // Stamped now, read by the Worker: a submission that arrives within
    // three seconds of the form being ready was not typed by a person.
    if (stamp) stamp.value = String(Date.now());

    function say(text, cls) {
      if (!formNote) return;
      formNote.className = 'form__note' + (cls ? ' ' + cls : '');
      formNote.textContent = text;
    }

    function busy(on) {
      if (!submit) return;
      submit.disabled = on;
      submit.textContent = on ? 'Sending...' : submitLabel;
    }

    form.addEventListener('submit', function (e) {
      // Clear the honeypot before anything reads the form. A browser that
      // autofills the hidden field would otherwise get the visitor dropped as a
      // bot and told their enquiry had sent, which is how real enquiries went
      // missing. Anything that does not run this script keeps whatever it put
      // in the field, so the trap still works on exactly what it is aimed at.
      var hp = form.elements.namedItem('enquiry_subject');
      if (hp) hp.value = '';

      // Read fields via form.elements. `form.name` happens to work (HTMLFormElement is
      // [LegacyOverrideBuiltIns], so the named-element getter beats the built-in `name`
      // property) but it reads like a bug, so go through elements explicitly.
      function field(n) {
        var el = form.elements.namedItem(n);
        return el && typeof el.value === 'string' ? el.value.trim() : '';
      }

      var name    = field('name');
      var email   = field('email');
      var message = field('message');

      // Check before preventing the default, so that if this browser has no
      // fetch the native post still happens and the server validates instead.
      if (!name || !email || !message) {
        e.preventDefault();
        say('Please complete your name, email address and message.', 'err');
        return;
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        e.preventDefault();
        say('That email address does not look right. Please check it.', 'err');
        return;
      }
      if (!window.fetch || !window.FormData) return;   // let the browser post it

      e.preventDefault();
      busy(true);
      say('Sending your enquiry...', '');

      fetch(form.action, {
        method: 'POST',
        headers: { 'Accept': 'application/json', 'X-Requested-With': 'fetch' },
        body: new FormData(form)
      }).then(function (res) {
        return res.json().then(function (data) { return { ok: res.ok, data: data }; });
      }).then(function (r) {
        busy(false);
        if (r.ok && r.data && r.data.ok) {
          say(r.data.message || 'Thank you. Your enquiry has been sent.', 'ok');
          form.reset();
          if (stamp) stamp.value = String(Date.now());
          return;
        }
        // The server's message may carry a mailto: link for the fallback. This
        // is our own endpoint, not third-party content, but set it as text and
        // strip the markup rather than injecting HTML from a response.
        var msg = (r.data && r.data.message ? r.data.message : '')
          .replace(/<[^>]*>/g, '');
        say(msg || 'We could not send that. Please email ops@greymanprotection.co.za directly.', 'err');
      }).catch(function () {
        busy(false);
        say('We could not reach the server. Please check your connection, or email ops@greymanprotection.co.za directly.', 'err');
      });
    });
  }

  /* ---------- Privacy notice ----------
     Deliberately NOT a cookie banner: the site sets no cookies, so there is
     nothing to consent to and a consent gate would be theatre. It states that
     once. The dismissal is kept in localStorage, which never leaves the device
     and is itself disclosed in the privacy policy. Wrapped because Safari in
     private mode throws on localStorage rather than returning null. */
  // NB the name. This block used to declare `var note` as well, in the same
  // function scope as the contact form's `note` above: `var` is not block
  // scoped, so the second declaration won the whole scope and every form
  // status message was written into the privacy aside instead of under the
  // send button. Keep these names distinct.
  var pNote = $('#privacyNote');
  var pNoteOk = $('#privacyOk');
  function noteSeen(v) {
    try {
      if (v === undefined) return localStorage.getItem('gm-privacy-note') === '1';
      localStorage.setItem('gm-privacy-note', '1');
    } catch (e) { return v === undefined ? true : undefined; }
  }
  if (pNote && pNoteOk && !noteSeen()) {
    pNote.hidden = false;
    pNoteOk.addEventListener('click', function () {
      pNote.hidden = true;
      noteSeen(true);
    });
  }

  /* ---------- Current year in the footer ---------- */
  $$('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
