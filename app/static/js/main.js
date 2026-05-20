// =============================================================================
// main.js — Scripts client globaux (Phase 1 : presque rien).
//
// Phase 2 : navigation par ancres avec offset header sticky.
// Phase 3 : accordéon FAQ, soumission AJAX du form waitlist.
// =============================================================================

(() => {
  'use strict';

  // Marqueur de chargement pour debug en console
  // (utile pour vérifier que main.js a bien été chargé en prod)
  if (typeof window !== 'undefined') {
    window.__GECKO_LANDING__ = { version: '0.1.0' };
  }
})();
