"""Tests des routes publiques : home, privacy, sitemap, robots, healthz, favicon, 404.

Chaque test couvre :
- Le code HTTP attendu (200, 404, 405)
- Le content-type
- Un contenu clé pour vérifier que le bon template a été rendu
"""

from __future__ import annotations

from flask.testing import FlaskClient


# ============================================================================
# GET /
# ============================================================================

def test_home_returns_200(client: FlaskClient) -> None:
    """La home renvoie 200 et du HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.content_type.startswith("text/html")


def test_home_contains_all_sections(client: FlaskClient) -> None:
    """La home affiche les 6 sections principales (Features, How, Tools, Models, FAQ, Waitlist)."""
    response = client.get("/")
    body = response.get_data(as_text=True)

    # On vérifie la présence des id de section
    for section_id in ["features", "how-it-works", "tools", "models", "faq", "waitlist"]:
        assert f'id="{section_id}"' in body, f"Section #{section_id} missing from home page"


def test_home_renders_eleven_features(client: FlaskClient) -> None:
    """La grille Features doit contenir exactement 11 cards."""
    response = client.get("/")
    body = response.get_data(as_text=True)
    # Chaque card de feature commence par <article class="group rounded-lg
    count = body.count('<article class="group rounded-lg')
    assert count == 11, f"Expected 11 feature cards, got {count}"


def test_home_includes_json_ld(client: FlaskClient) -> None:
    """La home doit injecter au moins 2 blocs JSON-LD (SoftwareApplication + Organization)."""
    response = client.get("/")
    body = response.get_data(as_text=True)
    count = body.count('application/ld+json')
    assert count >= 2, f"Expected ≥ 2 JSON-LD blocks, got {count}"


# ============================================================================
# GET /privacy
# ============================================================================

def test_privacy_returns_200(client: FlaskClient) -> None:
    """La page privacy renvoie 200 et contient le titre attendu."""
    response = client.get("/privacy")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Privacy Policy" in body
    assert "Last updated" in body


# ============================================================================
# GET /sitemap.xml
# ============================================================================

def test_sitemap_returns_valid_xml(client: FlaskClient) -> None:
    """Le sitemap renvoie du XML valide avec les URLs principales."""
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert response.content_type.startswith("application/xml")

    body = response.get_data(as_text=True)
    # Header XML obligatoire
    assert body.startswith('<?xml version="1.0"')
    # Namespace sitemaps.org
    assert "sitemaps.org/schemas/sitemap/0.9" in body
    # Au moins 2 URLs (home + privacy)
    assert body.count("<url>") >= 2
    # Vérification que les routes critiques sont listées
    assert "/privacy" in body


# ============================================================================
# GET /robots.txt
# ============================================================================

def test_robots_returns_plain_text(client: FlaskClient) -> None:
    """Le robots.txt renvoie du text/plain et bloque les endpoints techniques."""
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert response.content_type.startswith("text/plain")

    body = response.get_data(as_text=True)
    # Allow all par défaut
    assert "User-agent: *" in body
    assert "Allow: /" in body
    # Endpoints techniques bloqués
    assert "Disallow: /waitlist" in body
    assert "Disallow: /healthz" in body
    # Sitemap déclaré pour les crawlers
    assert "Sitemap:" in body
    assert "/sitemap.xml" in body


# ============================================================================
# GET /healthz
# ============================================================================

def test_healthz_returns_json_ok(client: FlaskClient) -> None:
    """L'endpoint healthcheck renvoie un JSON 'status: ok'."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.content_type.startswith("application/json")

    data = response.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "gecko-agent-landing"
    assert "version" in data


# ============================================================================
# GET /favicon.ico
# ============================================================================

def test_favicon_serves_png(client: FlaskClient) -> None:
    """La route favicon sert le logo PNG."""
    response = client.get("/favicon.ico")
    assert response.status_code == 200
    assert response.content_type.startswith("image/png")
    # Le PNG doit avoir un poids minimum (signe que c'est pas vide)
    assert len(response.data) > 1000


# ============================================================================
# 404 custom
# ============================================================================

def test_unknown_route_returns_custom_404(client: FlaskClient) -> None:
    """Une route inexistante renvoie le 404 custom (pas la page Flask par défaut)."""
    response = client.get("/this-route-definitely-does-not-exist")
    assert response.status_code == 404
    body = response.get_data(as_text=True)
    # Notre 404 custom contient ce texte
    assert "This page wandered off" in body
    # Et le lien retour à la home
    assert "Back to homepage" in body
