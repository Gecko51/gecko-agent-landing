"""Context processors : variables injectées automatiquement dans tous les templates.

Permet d'éviter de répéter `{{ current_year }}` ou `{{ config }}` dans chaque
appel render_template — Flask les injecte globalement.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


def inject_globals() -> dict[str, Any]:
    """Injecte des variables globales accessibles dans tous les templates Jinja2.

    Returns:
        Dict des variables à injecter (clé = nom dans le template).
    """
    return {
        # Année courante pour le copyright footer
        "current_year": datetime.now().year,
        # Version applicative (utile pour le footer ou meta)
        "app_version": "0.1.0",
    }
