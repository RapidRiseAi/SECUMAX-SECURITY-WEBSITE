/* =========================================================
   SECUMAX SECURITY — interactions
   ========================================================= */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $  = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---------- Header scroll state + progress + to-top + action bar ---------- */
  var header    = $('#siteHeader');
  var progress  = $('#scrollProgress');
  var toTop     = $('#toTop');
  var actionBar = $('.action-bar');

  function onScroll() {
    var y = window.pageYOffset || document.documentElement.scrollTop;
    var docH = document.documentElement.scrollHeight - window.innerHeight;

    if (header) header.classList.toggle('scrolled', y > 24);
    if (progress) progress.style.width = (docH > 0 ? (y / docH) * 100 : 0) + '%';
    if (toTop) toTop.classList.toggle('show', y > 700);
    if (actionBar) actionBar.classList.toggle('show', y > 400);
  }

  /* ---------- Scroll-linked parallax (transform-only, disabled under reduced motion) ---------- */
  var parallaxEls = reduceMotion ? [] : $$('[data-parallax]');
  function updateParallax() {
    if (!parallaxEls.length) return;
    var vh = window.innerHeight || document.documentElement.clientHeight;
    for (var i = 0; i < parallaxEls.length; i++) {
      var el = parallaxEls[i];
      var r = el.getBoundingClientRect();
      if (r.bottom <= 0 || r.top >= vh) continue;           // skip off-screen
      var prog = (vh - r.top) / (vh + r.height);             // 0 entering → 1 leaving
      var yPct = (prog - 0.5) * 8;                           // -4% … 4%
      el.style.transform = 'translate3d(0,' + yPct.toFixed(2) + '%,0)';
    }
  }

  // rAF-throttled scroll handler — at most one layout pass per frame
  var scrollTicking = false;
  window.addEventListener('scroll', function () {
    if (scrollTicking) return;
    scrollTicking = true;
    requestAnimationFrame(function () {
      onScroll();
      updateParallax();
      scrollTicking = false;
    });
  }, { passive: true });
  window.addEventListener('resize', updateParallax, { passive: true });
  onScroll();
  updateParallax();

  if (toTop) toTop.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
  });

  /* ---------- Mobile drawer ---------- */
  var hamburger = $('#hamburger');
  var mobileMenu = $('#mobileMenu');

  function setMenu(open) {
    if (!mobileMenu || !hamburger) return;
    mobileMenu.classList.toggle('open', open);
    hamburger.setAttribute('aria-expanded', open ? 'true' : 'false');
    hamburger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    mobileMenu.setAttribute('aria-hidden', open ? 'false' : 'true');
    document.body.style.overflow = open ? 'hidden' : '';
  }
  if (hamburger) hamburger.addEventListener('click', function () {
    setMenu(!mobileMenu.classList.contains('open'));
  });
  if (mobileMenu) {
    mobileMenu.addEventListener('click', function (e) {
      if (e.target === mobileMenu || e.target.closest('a')) setMenu(false);
    });
  }
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') setMenu(false);
  });

  /* ---------- Scroll reveal (base .reveal + directional/scale variants) ---------- */
  var revealEls = $$('[class*="reveal"]');
  if ('IntersectionObserver' in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('in'); });
  }

  /* ---------- Animated counters ---------- */
  function animateCount(el) {
    var target = parseFloat(el.getAttribute('data-count')) || 0;
    var suffix = el.getAttribute('data-suffix') || '';
    if (reduceMotion) { el.textContent = target + suffix; return; }
    var dur = 1400, start = null;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased) + (p === 1 ? suffix : '');
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = target + suffix;
    }
    requestAnimationFrame(step);
  }
  var counters = $$('.stat__num');
  if ('IntersectionObserver' in window) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { animateCount(en.target); cio.unobserve(en.target); }
      });
    }, { threshold: 0.5 });
    counters.forEach(function (c) { cio.observe(c); });
  } else {
    counters.forEach(animateCount);
  }

  /* ---------- Active nav link on scroll ---------- */
  var sections = $$('main section[id]');
  var navLinks = $$('.nav-desktop a');
  if ('IntersectionObserver' in window && navLinks.length) {
    var sio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          var id = en.target.getAttribute('id');
          navLinks.forEach(function (a) {
            a.classList.toggle('active', a.getAttribute('href') === '#' + id);
          });
        }
      });
    }, { threshold: 0.4, rootMargin: '-30% 0px -55% 0px' });
    sections.forEach(function (s) { sio.observe(s); });
  }

  /* ---------- Smooth anchor scrolling with header offset ---------- */
  $$('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var id = a.getAttribute('href');
      if (id.length < 2) return;
      var target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      var h = header ? header.offsetHeight : 0;
      var top = target.getBoundingClientRect().top + window.pageYOffset - h + 2;
      window.scrollTo({ top: top, behavior: reduceMotion ? 'auto' : 'smooth' });
    });
  });

  /* ---------- Contact form (front-end validation + mailto fallback) ---------- */
  var form = $('#contactForm');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var note = $('#formNote');
      var name = $('#name').value.trim();
      var email = $('#email').value.trim();
      var message = $('#message').value.trim();
      var validEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

      if (!name || !validEmail || !message) {
        note.textContent = 'Please add your name, a valid email and a message.';
        note.className = 'form__note err';
        return;
      }
      // Compose a mailto so the message reaches the inbox without a backend.
      var subject = encodeURIComponent('Website enquiry from ' + name);
      var body = encodeURIComponent(message + '\n\n— ' + name + ' (' + email + ')');
      note.textContent = 'Opening your email app…';
      note.className = 'form__note ok';
      window.location.href = 'mailto:info@secumaxsecurity.co.za?subject=' + subject + '&body=' + body;
      setTimeout(function () {
        note.textContent = 'Thank you — we will be in touch shortly.';
        form.reset();
      }, 800);
    });
  }

  /* ---------- Year (footer safety, keeps copyright current) ---------- */
  $$('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
