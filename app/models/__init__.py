"""Package des modèles SQLAlchemy.

Chaque modèle hérite de `db.Model` (l'instance globale dans app.extensions).
Importer tous les modèles ici garantit qu'Alembic les voit lors des migrations
(autogenerate fonctionne uniquement sur les modèles chargés en mémoire).
"""

from __future__ import annotations

from app.models.waitlist import WaitlistEmail  # noqa: F401

__all__ = ["WaitlistEmail"]
