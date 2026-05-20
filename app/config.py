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
    CHROME_WEBSTORE_URL = os.getenv(
        "CHROME_WEBSTORE_URL",
        "https://chromewebstore.google.com/",
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
    # En dev, on accepte que SECRET_KEY soit la valeur par défaut (pas idéal mais OK)


class ProdConfig(Config):
    """Config production : debug désactivé, contraintes de sécurité strictes."""

    DEBUG = False
    TESTING = False
    # En prod, les cookies doivent être en HTTPS uniquement
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # Force HTTPS sur tous les URLs (Flask-Talisman complètera ça en Phase 5)
    PREFERRED_URL_SCHEME = "https"


class TestConfig(Config):
    """Config tests pytest : BDD en mémoire, CSRF désactivé."""

    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False  # Simplifie les tests de formulaires (à activer en intégration)
