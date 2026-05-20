"""Routes du blueprint public.

Phase 1 : home + healthz uniquement.
Phase 2-3 : on ajoutera /privacy, /terms, /sitemap.xml, /robots.txt.
"""

from __future__ import annotations

from flask import render_template

from app.blueprints.public import public_bp


@public_bp.route("/", methods=["GET"])
def home() -> str:
    """Rendu de la landing principale (page d'accueil).

    Returns:
        HTML rendu via le template public/home.html.
    """
    # render_template cherche dans app/templates/ par défaut
    return render_template("public/home.html")


@public_bp.route("/healthz", methods=["GET"])
def healthz() -> tuple[dict[str, str], int]:
    """Endpoint healthcheck pour Render / Railway / uptime monitoring.

    Doit rester ultra léger : pas d'accès BDD, pas de logique métier.
    Render appelle cette route régulièrement — si elle est lente ou échoue,
    le service est marqué unhealthy.

    Returns:
        Tuple (JSON, status code).
    """
    # Réponse minimale : status OK + version applicative (utile pour debug deploy)
    return {"status": "ok", "service": "gecko-agent-landing", "version": "0.1.0"}, 200
