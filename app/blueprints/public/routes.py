"""Routes du blueprint public.

Phases couvertes :
- 1 : home + healthz + favicon
- 3 : /privacy
- 4 : /sitemap.xml + /robots.txt (SEO)
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

from flask import Response, current_app, render_template, send_from_directory, url_for

from app.blueprints.public import public_bp


@public_bp.route("/", methods=["GET"])
def home() -> str:
    """Rendu de la landing principale (page d'accueil).

    Returns:
        HTML rendu via le template public/home.html.
    """
    # render_template cherche dans app/templates/ par défaut
    return render_template("public/home.html")


@public_bp.route("/privacy", methods=["GET"])
def privacy() -> str:
    """Rendu de la page Privacy Policy.

    Le contenu est statique (template public/privacy.html), basé sur le PRIVACY.md
    du repo extension. Toute modification du privacy se fait dans le template,
    pas via un CMS — c'est volontaire pour garder la trace dans Git.

    Returns:
        HTML rendu via le template public/privacy.html.
    """
    return render_template("public/privacy.html")


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


@public_bp.route("/sitemap.xml", methods=["GET"])
def sitemap() -> Response:
    """Génère un sitemap.xml dynamique pour les moteurs de recherche.

    On liste uniquement les pages indexables (pas /healthz, pas /waitlist, pas /favicon).
    `lastmod` est généré au moment de la requête — pas idéal pour le SEO mais
    correct pour une landing qui change rarement (les vrais robots cachent).

    Returns:
        Response XML avec content-type adapté.
    """
    # Liste des routes à indexer (endpoint, changefreq, priority)
    pages = [
        ("public.home", "weekly", "1.0"),
        ("public.privacy", "yearly", "0.3"),
    ]

    # Format ISO 8601 (Google recommande le format W3C)
    lastmod = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Construction du XML — on évite Jinja2 pour rester très simple et rapide
    urls_xml = "\n".join(
        f"""  <url>
    <loc>{url_for(endpoint, _external=True)}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>"""
        for endpoint, changefreq, priority in pages
    )

    xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls_xml}
</urlset>
"""

    return Response(xml_body, mimetype="application/xml")


@public_bp.route("/robots.txt", methods=["GET"])
def robots() -> Response:
    """Sert un robots.txt qui autorise l'indexation publique mais exclut les endpoints techniques.

    - /waitlist (POST only, pas de sens d'indexer)
    - /healthz (endpoint monitoring interne)
    - /favicon.ico (déjà accessible via meta tags)

    Le sitemap est annoncé explicitement pour aider les crawlers à le trouver.
    """
    sitemap_url = url_for("public.sitemap", _external=True)
    body = f"""User-agent: *
Allow: /
Disallow: /waitlist
Disallow: /healthz

Sitemap: {sitemap_url}
"""
    return Response(body, mimetype="text/plain")


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
