"""Classes de configuration Flask.

On définit une classe de base `Config` avec les valeurs communes, puis des
sous-classes `DevConfig` / `ProdConfig` / `TestConfig` qui surchargent les
valeurs spécifiques à chaque environnement.

Cette approche permet de basculer entre environnements via `FLASK_ENV` sans
toucher au code.
"""

from __future__ import annotations

import os
from pathlib import Path


# Répertoire racine du projet (parent de app/)
BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Configuration commune à tous les environnements."""

    # --- Flask core ---
    # SECRET_KEY est OBLIGATOIRE en prod. En dev, on a un fallback faible
    # mais on log un warning si la valeur par défaut est utilisée.
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-CHANGE-ME-IN-PRODUCTION")

    # --- Sessions ---
    # Durée de vie des cookies de session (7 jours)
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 7

    # --- Base de données (Phase 3+) ---
    # On la prépare dès maintenant pour ne pas avoir à modifier le code plus tard
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'database.db'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Désactive un signal coûteux et déprécié

    # --- Liens externes affichés dans les templates ---
    # URL Chrome Web Store de l'extension Gecko Agent (publiée le 2026-04)
    CHROME_WEBSTORE_URL = os.getenv(
        "CHROME_WEBSTORE_URL",
        "https://chromewebstore.google.com/detail/gecko-agent/fodegmmmomdfjdfaamcldkemopidniep",
    )
    GITHUB_REPO_URL = os.getenv(
        "GITHUB_REPO_URL",
        "https://github.com/Gecko51/gecko-agent",
    )

    # --- Analytics (Phase 5) ---
    PLAUSIBLE_DOMAIN = os.getenv("PLAUSIBLE_DOMAIN", "")

    # --- Rate limiting (Phase 3+) ---
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")


class DevConfig(Config):
    """Config développement local : debug activé, logs verbeux."""

    DEBUG = True
    TESTING = False
    # Recharge les templates Jinja2 à chaque requête sans redémarrer le serveur
    # (sinon, en mode non-debug, les modifs HTML ne sont visibles qu'après restart)
    TEMPLATES_AUTO_RELOAD = True
    # Envoie les fichiers statiques avec un cache court pour voir les modifs CSS/JS rapidement
    SEND_FILE_MAX_AGE_DEFAULT = 0
    # En dev, on accepte que SECRET_KEY soit la valeur par défaut (pas idéal mais OK)


class ProdConfig(Config):
    """Config production : debug désactivé, contraintes de sécurité strictes."""

    DEBUG = False
    TESTING = False

    # --- Cookies sécurisés ---
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PREFERRED_URL_SCHEME = "https"

    # --- Flask-Talisman : headers de sécurité ---
    # On active Talisman uniquement en prod (en dev, pas de HTTPS donc no-op)
    TALISMAN_ENABLED = True

    # CSP (Content Security Policy) — strict mais fonctionnel pour notre stack
    # Plausible est ajouté conditionnellement par init_app si PLAUSIBLE_DOMAIN défini
    TALISMAN_CSP = {
        "default-src": "'self'",
        # Scripts : seulement notre main.js (et Plausible si activé)
        "script-src": ["'self'"],
        # Styles : Tailwind compilé en self, fonts Google injectent du CSS inline
        "style-src": ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
        # Fonts : Google Fonts
        "font-src": ["'self'", "https://fonts.gstatic.com", "data:"],
        # Images : logo + favicon (self) + data: pour les SVG inlinés en URI
        "img-src": ["'self'", "data:"],
        # Fetch AJAX (waitlist) : self uniquement
        "connect-src": ["'self'"],
        # Empêche d'être embedded en iframe (anti-clickjacking)
        "frame-ancestors": "'none'",
        # Form submissions vers self uniquement
        "form-action": "'self'",
        # Base URI bloqué (anti-DOM-based XSS)
        "base-uri": "'self'",
    }

    # HSTS : 1 an + includeSubDomains + preload (eligibility hstspreload.org)
    TALISMAN_STRICT_TRANSPORT_SECURITY = True
    TALISMAN_STRICT_TRANSPORT_SECURITY_MAX_AGE = 31536000  # 1 an en secondes
    TALISMAN_STRICT_TRANSPORT_SECURITY_INCLUDE_SUBDOMAINS = True
    TALISMAN_STRICT_TRANSPORT_SECURITY_PRELOAD = True

    # Autres headers
    TALISMAN_REFERRER_POLICY = "strict-origin-when-cross-origin"
    TALISMAN_FRAME_OPTIONS = "DENY"  # Renforce frame-ancestors


class TestConfig(Config):
    """Config tests pytest : BDD en mémoire, CSRF désactivé."""

    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False  # Simplifie les tests de formulaires (à activer en intégration)
    # Désactive le rate limiter en test (sinon les tests qui font plusieurs POST hit 429)
    RATELIMIT_ENABLED = False
    # Pas de Talisman en test (force_https casserait les requêtes test http://)
    TALISMAN_ENABLED = False
