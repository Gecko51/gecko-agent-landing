"""Blueprint public : pages visibles par tout visiteur (landing, privacy, 404).

On expose `public_bp` directement depuis ce fichier pour que l'App Factory
puisse l'importer simplement : `from app.blueprints.public import public_bp`.
"""

from __future__ import annotations

from flask import Blueprint

# Création du blueprint
# - name="public" : identifiant utilisé par url_for("public.home")
# - url_prefix=None : pas de préfixe (les routes restent à la racine "/")
public_bp = Blueprint(
    "public",
    __name__,
    template_folder="../../templates",
    static_folder="../../static",
)

# Import des routes APRÈS la création du blueprint pour éviter l'import circulaire
# (les routes décorées avec @public_bp.route() ont besoin que public_bp existe)
from app.blueprints.public import routes  # noqa: E402, F401
