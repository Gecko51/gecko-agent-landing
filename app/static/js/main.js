// =============================================================================
// main.js — Scripts client globaux.
//
// Phase 3 : soumission AJAX du formulaire waitlist + feedback inline.
// Phase 4 : highlight de la nav active au scroll (intersection observer).
//
// Pas de framework. Vanilla JS ES2022, défensif (vérifie l'existence des éléments).
// =============================================================================

(() => {
  'use strict';

  // Marqueur de chargement utile en debug
  if (typeof window !== 'undefined') {
    window.__GECKO_LANDING__ = { version: '0.3.0' };
  }

  /**
   * Récupère le token CSRF injecté dans <meta name="csrf-token"> par base.html.
   * Flask-WTF accepte ce token via le header X-CSRFToken pour les requêtes AJAX.
   */
  function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
  }

  /**
   * Soumission AJAX du formulaire waitlist.
   * Empêche le rechargement de page, envoie en JSON, affiche le feedback inline.
   *
   * @param {HTMLFormElement} form - Le <form data-waitlist-form>
   */
  async function handleWaitlistSubmit(form) {
    const submitBtn = form.querySelector('[data-waitlist-submit]');
    const feedbackEl = form.parentElement.querySelector('[data-waitlist-feedback]');

    // Désactive le bouton pour éviter les doubles clics
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Submitting…';
    }

    // Reset du feedback précédent
    if (feedbackEl) {
      feedbackEl.classList.add('hidden');
      feedbackEl.textContent = '';
    }

    try {
      // Construction du body x-www-form-urlencoded (Flask-WTF s'attend à ce format)
      const formData = new FormData(form);

      const response = await fetch(form.action, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCsrfToken(),
          'Accept': 'application/json',
        },
        body: formData,
        // Pas de credentials needed : même origine
      });

      // Parse la réponse JSON (la route renvoie toujours du JSON sur 2xx/4xx)
      let data = {};
      try {
        data = await response.json();
      } catch {
        // Si pas de JSON valide (erreur serveur 500), data reste vide
      }

      // --- Affichage du feedback ---
      if (feedbackEl) {
        feedbackEl.classList.remove('hidden');

        if (response.ok && data.status === 'success') {
          // Succès : message vert avec coche
          feedbackEl.textContent = '✓ ' + (data.message || "You're on the list.");
          feedbackEl.className = 'mt-4 text-sm text-green-400';
          form.reset();
        } else if (response.ok && data.status === 'already_subscribed') {
          // Déjà inscrit : message info, pas une erreur visible
          feedbackEl.textContent = 'ℹ ' + (data.message || "You're already on the list.");
          feedbackEl.className = 'mt-4 text-sm text-background/80';
        } else if (response.status === 429) {
          // Rate limit
          feedbackEl.textContent = '⚠ Too many attempts. Please wait a minute and try again.';
          feedbackEl.className = 'mt-4 text-sm text-yellow-400';
        } else {
          // Erreur de validation ou serveur
          const msg = data.message || 'Something went wrong. Please try again.';
          feedbackEl.textContent = '✗ ' + msg;
          feedbackEl.className = 'mt-4 text-sm text-red-400';
        }
      }
    } catch (err) {
      // Erreur réseau : connexion perdue, CORS, etc.
      console.error('Waitlist submit failed:', err);
      if (feedbackEl) {
        feedbackEl.classList.remove('hidden');
        feedbackEl.textContent = '✗ Network error. Please check your connection and try again.';
        feedbackEl.className = 'mt-4 text-sm text-red-400';
      }
    } finally {
      // Réactive le bouton dans tous les cas (succès ou erreur)
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Notify me';
      }
    }
  }

  /**
   * Toggle le menu burger mobile : ouvre/ferme le panel et switch les icônes.
   * Met aussi à jour aria-expanded pour les lecteurs d'écran.
   */
  function setupMobileMenu() {
    const toggleBtn = document.querySelector('[data-mobile-menu-toggle]');
    const menu = document.querySelector('[data-mobile-menu]');
    if (!toggleBtn || !menu) return;

    const iconClosed = toggleBtn.querySelector('[data-mobile-menu-icon="closed"]');
    const iconOpen = toggleBtn.querySelector('[data-mobile-menu-icon="open"]');

    /** Ferme le menu (état par défaut) */
    function closeMenu() {
      menu.classList.add('hidden');
      toggleBtn.setAttribute('aria-expanded', 'false');
      toggleBtn.setAttribute('aria-label', 'Open menu');
      if (iconClosed) iconClosed.classList.remove('hidden');
      if (iconOpen) iconOpen.classList.add('hidden');
    }

    /** Ouvre le menu */
    function openMenu() {
      menu.classList.remove('hidden');
      toggleBtn.setAttribute('aria-expanded', 'true');
      toggleBtn.setAttribute('aria-label', 'Close menu');
      if (iconClosed) iconClosed.classList.add('hidden');
      if (iconOpen) iconOpen.classList.remove('hidden');
    }

    // Toggle sur clic du burger
    toggleBtn.addEventListener('click', () => {
      const isOpen = toggleBtn.getAttribute('aria-expanded') === 'true';
      isOpen ? closeMenu() : openMenu();
    });

    // Ferme automatiquement le menu après clic sur un lien (UX mobile)
    menu.querySelectorAll('[data-mobile-menu-link]').forEach((link) => {
      link.addEventListener('click', () => closeMenu());
    });

    // Ferme avec la touche Escape
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && toggleBtn.getAttribute('aria-expanded') === 'true') {
        closeMenu();
        toggleBtn.focus(); // Retour focus sur le bouton (a11y)
      }
    });
  }

  // --- Bootstrap : attache les listeners au chargement du DOM ---
  document.addEventListener('DOMContentLoaded', () => {
    // Mobile menu burger
    setupMobileMenu();

    // Cherche tous les formulaires waitlist (au cas où on en a plusieurs sur la page)
    document.querySelectorAll('[data-waitlist-form]').forEach((form) => {
      form.addEventListener('submit', (event) => {
        event.preventDefault();
        handleWaitlistSubmit(form);
      });
    });
  });

})();
