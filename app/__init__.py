"""App Factory Flask.

Pattern recommandé Flask : on n'instancie pas une app globale, on fournit une
fabrique `create_app()` qui crée et configure une nouvelle instance Flask.

Avantages :
- Tests unitaires plus faciles (chaque test peut créer sa propre app isolée).
- Permet plusieurs configurations (dev / prod / test) sans variable globale.
- Évite les bugs liés à l'ordre d'import.
"""

from __future__ import annotations

import os

from flask import Flask

from app.config import DevConfig, ProdConfig


def create_app(config_class: type | None = None) -> Flask:
    """Crée et configure une nouvelle instance Flask.

    Args:
        config_class: Classe de configuration à utiliser. Si None, détecte
            automatiquement via la variable d'env FLASK_ENV.

    Returns:
        L'instance Flask configurée et prête à servir des requêtes.
    """
    # On précise `instance_relative_config=True` pour que Flask cherche la
    # config dans le dossier `instance/` (utile plus tard pour la BDD SQLite).
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder="templates",
        static_folder="static",
    )

    # Sélection de la config selon l'environnement
    if config_class is None:
        env = os.getenv("FLASK_ENV", "development")
        config_class = ProdConfig if env == "production" else DevConfig

    app.config.from_object(config_class)

    # Crée le dossier instance/ s'il n'existe pas (silencieux si déjà présent)
    os.makedirs(app.instance_path, exist_ok=True)

    # Enregistre les blueprints (un par domaine fonctionnel)
    _register_blueprints(app)

    # Enregistre les error handlers globaux (404, 500)
    _register_error_handlers(app)

    # Enregistre les context processors (variables injectées dans tous les templates)
    _register_context_processors(app)

    return app


def _register_context_processors(app: Flask) -> None:
    """Enregistre les fonctions qui injectent des variables globales dans Jinja2."""
    from app.utils.context_processors import inject_globals

    app.context_processor(inject_globals)


def _register_blueprints(app: Flask) -> None:
    """Enregistre tous les blueprints de l'app.

    Importer les blueprints DANS la fonction (pas en haut du fichier) évite
    les imports circulaires si un blueprint a besoin de `current_app`.
    """
    from app.blueprints.public import public_bp

    app.register_blueprint(public_bp)


def _register_error_handlers(app: Flask) -> None:
    """Enregistre les handlers d'erreur (404, 500) pour servir des pages custom."""
    from flask import render_template

    @app.errorhandler(404)
    def not_found(_error):  # type: ignore[no-untyped-def]
        # Renvoie la page 404 custom avec le bon code HTTP
        return render_template("public/404.html"), 404

    @app.errorhandler(500)
    def server_error(_error):  # type: ignore[no-untyped-def]
        # Loggue l'erreur pour le monitoring, puis affiche une page minimale
        app.logger.exception("Erreur serveur 500")
        return render_template("public/404.html"), 500
