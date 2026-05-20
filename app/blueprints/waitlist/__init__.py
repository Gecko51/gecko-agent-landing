"""Blueprint waitlist : gestion de l'inscription à la liste d'attente."""

from __future__ import annotations

from flask import Blueprint

# Blueprint sans préfixe : la route /waitlist sera servie directement
waitlist_bp = Blueprint("waitlist", __name__)

# Import des routes APRÈS création du blueprint (pattern Flask standard)
from app.blueprints.waitlist import routes  # noqa: E402, F401
