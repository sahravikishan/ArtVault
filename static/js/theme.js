/**
 * ArtVault — Dark Mode Toggle (theme.js)
 *
 * - Reads preference from cookie "artvault_theme"
 * - Applies .dark class to <body> immediately (before paint)
 * - Toggle button switches mode and writes cookie (1-year expiry)
 */

(function () {
  'use strict';

  const COOKIE_NAME  = 'artvault_theme';
  const DARK_CLASS   = 'dark';
  const COOKIE_DAYS  = 365;

  // ── Cookie helpers ──────────────────────────────────────────────
  function getCookie(name) {
    const match = document.cookie.match(
      new RegExp('(?:^|; )' + name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '=([^;]*)')
    );
    return match ? decodeURIComponent(match[1]) : null;
  }

  function setCookie(name, value, days) {
    const expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = name + '=' + encodeURIComponent(value) +
      '; expires=' + expires + '; path=/; SameSite=Lax';
  }

  // ── Apply saved theme immediately ──────────────────────────────
  const saved = getCookie(COOKIE_NAME);
  if (saved === DARK_CLASS) {
    document.documentElement.classList.add(DARK_CLASS); // on <html> for FOUC prevention
    document.addEventListener('DOMContentLoaded', function () {
      document.body.classList.add(DARK_CLASS);
      document.documentElement.classList.remove(DARK_CLASS);
    });
  }

  // ── Wire up the toggle button ───────────────────────────────────
  document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('theme-toggle-btn');
    if (!btn) return;

    // Sync button aria-label
    function updateLabel() {
      const isDark = document.body.classList.contains(DARK_CLASS);
      btn.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
      btn.setAttribute('title',      isDark ? 'Light mode'           : 'Dark mode');
    }
    updateLabel();

    btn.addEventListener('click', function () {
      const isDark = document.body.classList.toggle(DARK_CLASS);
      setCookie(COOKIE_NAME, isDark ? DARK_CLASS : 'light', COOKIE_DAYS);
      updateLabel();
    });
  });
})();
