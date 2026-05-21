"""Génération du site statique via Frozen-Flask.

Usage :
    python freeze.py

Lit l'app Flask et écrit le HTML rendu dans `build/`. Sortie compatible Netlify
(ou n'importe quel hébergeur statique : Cloudflare Pages, Vercel, GitHub Pages,
nginx en static…).

Variables d'environnement importantes :
- SITE_URL : URL publique du site (ex: https://gecko-agent.com). Utilisé pour
  les liens absolus dans le sitemap, les og:image, le canonical URL, etc.
  Défaut : https://gecko-agent-landing.netlify.app
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from flask_frozen import Freezer

from app import create_app
from app.config import ProdConfig


# --- Variables d'environnement ---
# Sur Netlify, on définit SITE_URL dans netlify.toml. En local, fallback.
SITE_URL = os.getenv("SITE_URL", "https://gecko-agent-landing.netlify.app")

# Le scheme et le host sont extraits de SITE_URL pour Frozen-Flask
# (SERVER_NAME doit être SANS schéma : "gecko-agent.com" et pas "https://...")
from urllib.parse import urlparse

parsed = urlparse(SITE_URL)
server_name = parsed.netloc  # "gecko-agent.com"
url_scheme = parsed.scheme   # "https"


# --- Création de l'app pour le freeze ---
# On utilise ProdConfig pour avoir les bons paramètres de prod (mais SANS
# Talisman qui forcerait HTTPS et casserait Frozen-Flask).
class FreezeConfig(ProdConfig):
    """Config dédiée au freeze : prod-like sans Talisman ni rate limit."""

    DEBUG = False
    TESTING = False
    TALISMAN_ENABLED = False       # Pas de force HTTPS pendant le freeze
    RATELIMIT_ENABLED = False      # Pas de limit pendant le crawl
    SERVER_NAME = server_name       # Pour générer des URLs absolues correctes
    PREFERRED_URL_SCHEME = url_scheme
    # On garde une BDD éphémère en mémoire — le freeze ne touche pas la BDD
    # mais SQLAlchemy a besoin d'une URL valide pour s'initialiser
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Frozen-Flask config : où écrire et comment se comporter
    FREEZER_DESTINATION = str(Path(__file__).parent / "build")
    FREEZER_RELATIVE_URLS = False              # URLs absolues (mieux pour SEO)
    FREEZER_REMOVE_EXTRA_FILES = True          # Wipe build/ avant chaque run
    FREEZER_IGNORE_404_NOT_FOUND = False       # Échoue si une route renvoie 404
    FREEZER_DEFAULT_MIMETYPE = "text/html"
    # Liste explicite des routes à freezer (autres routes ignorées)
    FREEZER_STATIC_IGNORE = ["*.pyc", "__pycache__"]


def build_static_site() -> None:
    """Génère le site statique dans build/.

    Étapes :
    1. Wipe le dossier build/ existant
    2. Crée l'app Flask avec FreezeConfig
    3. Enregistre les URLs à freezer (URL generators)
    4. Lance Frozen-Flask qui crawle et écrit les fichiers HTML
    5. Génère le 404.html manuel (Frozen-Flask ne le freeze pas par défaut)
    """
    # Étape 1 : nettoyage du build précédent
    build_dir = Path(__file__).parent / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(exist_ok=True)

    # Étape 2 : création de l'app avec config de freeze
    app = create_app(config_class=FreezeConfig)

    # Initialise les tables BDD en mémoire (sinon SQLAlchemy gueule)
    from app.extensions import db
    with app.app_context():
        db.create_all()

    # Étape 3 : enregistre les routes statiques à freezer
    # with_no_argument_rules=False : on désactive l'auto-discovery des routes
    # pour exclure /healthz (renvoie du JSON, pas freezable proprement) et
    # /waitlist (POST only). On liste explicitement ce qu'on veut freezer.
    freezer = Freezer(app, with_no_argument_rules=False, with_static_files=True)

    @freezer.register_generator
    def public_routes():  # type: ignore[no-untyped-def]
        """Génère la liste des URLs à freezer côté blueprint public."""
        yield "public.home", {}
        yield "public.privacy", {}
        yield "public.sitemap", {}
        yield "public.robots", {}
        yield "public.favicon", {}
        # Pas /healthz : c'est pour les monitoring tools, pas pour le SEO
        # Pas /waitlist : POST only, pas freezable

    # Étape 4 : lancement du freeze
    print(f"Freezing site to {build_dir}...")
    freezer.freeze()
    print("Done.")

    # Étape 4b : post-process — renommer 'privacy' (sans extension) en 'privacy.html'
    # Frozen-Flask génère un fichier sans extension pour les routes sans trailing slash.
    # Netlify détecte mal le content-type sans extension : on renomme manuellement.
    privacy_no_ext = build_dir / "privacy"
    privacy_html = build_dir / "privacy.html"
    if privacy_no_ext.exists() and privacy_no_ext.is_file():
        privacy_no_ext.rename(privacy_html)
        print("Renamed privacy -> privacy.html (Netlify Pretty URLs handles /privacy redirect)")

    # Étape 5 : génération du 404.html (Netlify cherche /404.html par convention)
    # On force le rendu via test_client puisque Frozen-Flask ne freeze pas les errors
    print("Generating 404.html…")
    with app.test_client() as client:
        response = client.get("/__nonexistent_path_to_trigger_404__")
        assert response.status_code == 404, "Expected 404 for unknown route"
        (build_dir / "404.html").write_bytes(response.data)
    print("404.html written.")

    # Note : pas de caractères Unicode dans les prints (Windows cp1252 par défaut)
    print(f"\n[OK] Static site built in {build_dir}")
    print(f"     {len(list(build_dir.rglob('*')))} files generated")


if __name__ == "__main__":
    build_static_site()
