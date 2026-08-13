/**
 * Freedom Blades Platform — Phase 3 Visual Prototype (Step 2)
 * Accessible Native Portrait Preview Modal Controller
 */
document.addEventListener('DOMContentLoaded', function() {
  const dialog = document.getElementById('portrait-preview-dialog');
  if (!dialog) return;

  const isNativeDialogSupported = (
    typeof HTMLDialogElement === 'function' &&
    typeof dialog.showModal === 'function' &&
    typeof dialog.close === 'function'
  );

  const triggers = document.querySelectorAll('[data-portrait-trigger]');
  const unavailableMsg = document.getElementById('portrait-preview-unavailable-message');

  // Feature detection: If native modal dialog support is unavailable,
  // expose explanatory message and disable triggers gracefully with aria-describedby.
  if (!isNativeDialogSupported) {
    if (unavailableMsg) {
      unavailableMsg.removeAttribute('hidden');
    }
    triggers.forEach(function(btn) {
      btn.disabled = true;
      btn.setAttribute('aria-disabled', 'true');
      if (unavailableMsg) {
        btn.setAttribute('aria-describedby', 'portrait-preview-unavailable-message');
      }
      btn.title = 'Larger portrait preview is unavailable in this browser';
      btn.classList.add('btn-portrait-preview-disabled');
    });
    return;
  }

  const dialogTitle = document.getElementById('portrait-dialog-title');
  const dialogImg = document.getElementById('portrait-dialog-img');
  const dialogFallback = document.getElementById('portrait-dialog-fallback');
  const closeBtn = document.getElementById('portrait-dialog-close');
  let lastFocusedElement = null;
  let isClosing = false;

  function openPreview(trigger) {
    if (isClosing) return;
    lastFocusedElement = trigger;
    const src = trigger.getAttribute('data-portrait-src') || '';
    const name = trigger.getAttribute('data-character-name') || 'Character';
    const initials = trigger.getAttribute('data-character-initials') || name.substring(0, 2).toUpperCase();

    if (dialogTitle) {
      dialogTitle.textContent = name;
    }

    // Reset presentation state cleanly before opening
    if (dialogImg && dialogFallback) {
      dialogFallback.style.display = 'none';
      dialogFallback.removeAttribute('role');
      dialogFallback.innerHTML = '';

      dialogImg.style.display = 'block';
      dialogImg.alt = 'Enlarged portrait of ' + name;

      dialogImg.onerror = function() {
        dialogImg.style.display = 'none';
        dialogImg.onerror = null;

        // Accessible failure state
        dialogFallback.setAttribute('role', 'status');
        dialogFallback.innerHTML =
          '<span class="fallback-initials" aria-hidden="true">' + escapeHtml(initials) + '</span>' +
          '<span class="sr-only">Portrait unavailable for ' + escapeHtml(name) + '</span>';
        dialogFallback.style.display = 'flex';
      };

      dialogImg.setAttribute('src', src);
    }

    dialog.showModal();
    document.body.style.overflow = 'hidden';

    if (closeBtn) {
      closeBtn.focus();
    }
  }

  function closePreview() {
    if (isClosing || !dialog.open) return;
    isClosing = true;

    try {
      dialog.close();
    } catch (e) {
      // Ignore if already closing
    }

    // Clean reset of image and fallback states
    if (dialogImg) {
      dialogImg.onerror = null;
      dialogImg.style.display = 'none';
      dialogImg.removeAttribute('src');
      dialogImg.removeAttribute('alt');
    }

    if (dialogFallback) {
      dialogFallback.style.display = 'none';
      dialogFallback.removeAttribute('role');
      dialogFallback.innerHTML = '';
    }

    document.body.style.overflow = '';

    if (lastFocusedElement && typeof lastFocusedElement.focus === 'function') {
      lastFocusedElement.focus();
    }

    isClosing = false;
  }

  function escapeHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  // Bind trigger buttons
  triggers.forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      openPreview(btn);
    });
  });

  // Close button binding
  if (closeBtn) {
    closeBtn.addEventListener('click', function(e) {
      e.preventDefault();
      closePreview();
    });
  }

  // Native dialog cancel event (emitted when Escape key is pressed)
  dialog.addEventListener('cancel', function(e) {
    e.preventDefault();
    closePreview();
  });

  // Backdrop click dismissal
  dialog.addEventListener('click', function(e) {
    const rect = dialog.getBoundingClientRect();
    const isInDialog = (
      rect.top <= e.clientY &&
      e.clientY <= rect.top + rect.height &&
      rect.left <= e.clientX &&
      e.clientX <= rect.left + rect.width
    );
    if (!isInDialog || e.target === dialog) {
      closePreview();
    }
  });

  // Focus trap inside open modal
  dialog.addEventListener('keydown', function(e) {
    if (e.key === 'Tab') {
      const focusables = dialog.querySelectorAll('button:not([disabled]), [tabindex]:not([tabindex="-1"])');
      if (focusables.length === 0) return;
      const first = focusables[0];
      const last = focusables[focusables.length - 1];

      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  });
});
