"""Routes du blueprint public.

Phase 1 : home + healthz + favicon.
Phase 2-3 : on ajoutera /privacy, /terms, /sitemap.xml, /robots.txt.
"""

from __future__ import annotations

import os

from flask import current_app, render_template, send_from_directory

from app.blueprints.public import public_bp


@public_bp.route("/", methods=["GET"])
def home() -> str:
    """Rendu de la landing principale (page d'accueil).

    Returns:
        HTML rendu via le template public/home.html.
    """
    # render_template cherche dans app/templates/ par défaut
    return render_template("public/home.html")


@public_bp.route("/favicon.ico", methods=["GET"])
def favicon():  # type: ignore[no-untyped-def]
    """Sert le logo PNG à l'URL /favicon.ico.

    Les navigateurs (Chrome, Edge, Firefox) cherchent automatiquement
    /favicon.ico à la racine du site, indépendamment des balises <link>.
    On évite ainsi un 404 disgracieux dans les logs et on garantit l'affichage
    du favicon même quand le navigateur ignore les <link rel="icon"> du HTML.

    Les navigateurs modernes acceptent un PNG servi comme favicon depuis ~2010
    (le format .ico historique n'est plus requis).
    """
    # send_from_directory garde le fichier en static/img/ : on ne le déplace pas
    img_dir = os.path.join(current_app.root_path, "static", "img")
    return send_from_directory(img_dir, "logo.png", mimetype="image/png")


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
