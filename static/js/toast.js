/**
 * ArtVault — Global Toast Notification System (toast.js)
 *
 * Provides a luxury museum-grade pop-up notification system with:
 * - 5-second countdown progress bar
 * - Auto-dismiss after duration
 * - Manual close button
 * - Pause & resume on hover
 * - Full light & dark theme styling
 *
 * Usage:
 *   window.showToast("Painting added to your vault!", "success", 5000);
 *   window.showToast("Invalid credentials provided.", "error", 5000);
 *   window.showToast("Please fill all required fields.", "warning", 5000);
 *   window.showToast("Curatorial note saved.", "info", 5000);
 */

(function () {
  'use strict';

  const DEFAULT_DURATION = 5000; // 5 seconds default

  const ICONS = {
    success: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    error: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
    warning: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    info: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
  };

  const TITLES = {
    success: 'Success',
    error: 'Alert',
    warning: 'Warning',
    info: 'Notice',
  };

  function getOrCreateContainer() {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'toast-container';
      container.setAttribute('aria-live', 'polite');
      container.setAttribute('aria-atomic', 'true');
      if (document.body) {
        document.body.appendChild(container);
      } else if (document.documentElement) {
        document.documentElement.appendChild(container);
      }
    }
    return container;
  }

  function setupToastLifecycle(toast, duration) {
    if (!toast || toast.dataset.toastInit === 'true') return;
    toast.dataset.toastInit = 'true';

    const progressBar = toast.querySelector('.toast-progress-bar');
    const closeBtn = toast.querySelector('.toast-close');

    let remainingTime = duration || DEFAULT_DURATION;
    let startTime = Date.now();
    let timerId = null;

    function startTimer() {
      startTime = Date.now();
      if (progressBar) {
        progressBar.style.transition = 'width ' + remainingTime + 'ms linear';
        progressBar.style.width = '0%';
      }
      timerId = setTimeout(() => {
        dismissToast(toast);
      }, remainingTime);
    }

    function pauseTimer() {
      if (!timerId) return;
      clearTimeout(timerId);
      timerId = null;
      const elapsed = Date.now() - startTime;
      remainingTime = Math.max(0, remainingTime - elapsed);
      if (progressBar) {
        const computedWidth = window.getComputedStyle(progressBar).width;
        progressBar.style.transition = 'none';
        progressBar.style.width = computedWidth;
      }
    }

    // Pause countdown on hover
    toast.addEventListener('mouseenter', pauseTimer);
    toast.addEventListener('mouseleave', () => {
      if (remainingTime > 0) startTimer();
    });

    if (closeBtn) {
      closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (timerId) clearTimeout(timerId);
        dismissToast(toast);
      });
    }

    // Double frame wait so browser paints the initial 100% width before animating down
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        startTimer();
      });
    });
  }

  function dismissToast(toast) {
    if (!toast || toast.classList.contains('toast-hiding')) return;
    toast.classList.add('toast-hiding');
    toast.addEventListener('animationend', () => {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    });
    setTimeout(() => {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 650);
  }

  window.showToast = function (message, type, duration) {
    if (!message) return;
    type = (type || 'info').toLowerCase();
    duration = typeof duration === 'number' ? duration : DEFAULT_DURATION;

    const normalizedType = ['success', 'error', 'warning', 'info'].includes(type)
      ? type
      : (type === 'danger' ? 'error' : 'info');

    const container = getOrCreateContainer();

    const toast = document.createElement('div');
    toast.className = 'toast-popup toast-' + normalizedType;
    toast.setAttribute('role', 'alert');

    const iconSvg = ICONS[normalizedType] || ICONS.info;
    const titleText = TITLES[normalizedType] || 'Notice';

    toast.innerHTML = [
      '<div class="toast-icon-badge" aria-hidden="true">' + iconSvg + '</div>',
      '<div class="toast-body">',
      '  <span class="toast-title">' + titleText + '</span>',
      '  <p class="toast-text">' + message + '</p>',
      '</div>',
      '<button type="button" class="toast-close" aria-label="Close notification">&times;</button>',
      '<div class="toast-progress"><div class="toast-progress-bar"></div></div>'
    ].join('');

    container.appendChild(toast);
    setupToastLifecycle(toast, duration);
    return toast;
  };

  // Wire up any server-rendered toasts on DOM load
  function initServerToasts() {
    const existingToasts = document.querySelectorAll('#toast-container .toast-popup');
    existingToasts.forEach((toast) => {
      const duration = parseInt(toast.getAttribute('data-auto-dismiss'), 10) || DEFAULT_DURATION;
      setupToastLifecycle(toast, duration);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initServerToasts);
  } else {
    initServerToasts();
  }
})();
