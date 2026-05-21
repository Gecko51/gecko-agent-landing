"""Tests du blueprint waitlist : inscription, doublons, honeypot, validation.

Vérifications systématiques :
- Code HTTP correct
- Status JSON renvoyé
- État final de la BDD (entry présente ou non)

CSRF est désactivé dans TestConfig (WTF_CSRF_ENABLED=False),
donc on peut POSTer directement sans extraire le token.
"""

from __future__ import annotations

from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import select

from app.extensions import db
from app.models.waitlist import WaitlistEmail


def _count_emails(app: Flask) -> int:
    """Helper : compte les emails en BDD dans l'app context."""
    with app.app_context():
        return db.session.execute(select(WaitlistEmail)).scalars().all().__len__()


# ============================================================================
# Cas nominal : nouvel email valide
# ============================================================================

def test_subscribe_valid_email_returns_success(client: FlaskClient, app: Flask) -> None:
    """Un email valide est enregistré et renvoie status=success."""
    response = client.post("/waitlist", data={
        "email": "test@example.com",
        "source": "test_suite",
        "website": "",  # Honeypot vide
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "list" in data["message"].lower()  # "You're on the list"

    # Vérif BDD : 1 entrée créée
    assert _count_emails(app) == 1


def test_subscribe_normalizes_email_to_lowercase(client: FlaskClient, app: Flask) -> None:
    """Les emails sont normalisés en lowercase (anti-doublon Foo@x / foo@x)."""
    client.post("/waitlist", data={"email": "MiXeDcAsE@Example.com", "website": ""})

    with app.app_context():
        entry = db.session.execute(select(WaitlistEmail)).scalar_one()
        assert entry.email == "mixedcase@example.com"


# ============================================================================
# Doublon : même email re-soumis
# ============================================================================

def test_subscribe_duplicate_returns_already_subscribed(
    client: FlaskClient,
    app: Flask,
) -> None:
    """Un email déjà inscrit renvoie status=already_subscribed (pas une erreur)."""
    # 1ère inscription
    r1 = client.post("/waitlist", data={"email": "dup@example.com", "website": ""})
    assert r1.get_json()["status"] == "success"

    # 2ème inscription du même email
    r2 = client.post("/waitlist", data={"email": "dup@example.com", "website": ""})
    assert r2.status_code == 200
    assert r2.get_json()["status"] == "already_subscribed"

    # En BDD : 1 seule entrée (le doublon n'a pas été ajouté)
    assert _count_emails(app) == 1


# ============================================================================
# Honeypot : bot détecté
# ============================================================================

def test_subscribe_honeypot_triggered_returns_silent_success(
    client: FlaskClient,
    app: Flask,
) -> None:
    """Si le honeypot est rempli, on renvoie success fake MAIS l'email n'est PAS sauvegardé."""
    response = client.post("/waitlist", data={
        "email": "bot@spam.com",
        "source": "test_suite",
        "website": "evil-bot.com",  # Honeypot rempli = bot détecté
    })

    # On répond 200 success pour ne pas alerter le bot qu'il est repéré
    assert response.status_code == 200
    assert response.get_json()["status"] == "success"

    # Mais en BDD : 0 entrée (le bot n'a PAS été inscrit)
    assert _count_emails(app) == 0


# ============================================================================
# Validation : email invalide ou vide
# ============================================================================

def test_subscribe_invalid_email_returns_400(client: FlaskClient, app: Flask) -> None:
    """Un email sans @ est rejeté avec 400 BAD REQUEST."""
    response = client.post("/waitlist", data={
        "email": "not-an-email",
        "website": "",
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] == "error"
    assert "errors" in data
    assert "email" in data["errors"]

    # Aucune entrée en BDD
    assert _count_emails(app) == 0


def test_subscribe_empty_email_returns_400(client: FlaskClient, app: Flask) -> None:
    """Un email vide est rejeté avec 400 BAD REQUEST (DataRequired)."""
    response = client.post("/waitlist", data={
        "email": "",
        "website": "",
    })
    assert response.status_code == 400
    assert response.get_json()["status"] == "error"
    assert _count_emails(app) == 0


def test_subscribe_too_long_email_returns_400(client: FlaskClient, app: Flask) -> None:
    """Un email > 255 chars est rejeté (Length validator)."""
    # 250 'a' + '@x.com' = 256 chars total
    long_local = "a" * 250
    response = client.post("/waitlist", data={
        "email": f"{long_local}@x.com",
        "website": "",
    })
    assert response.status_code == 400
    assert _count_emails(app) == 0


# ============================================================================
# Méthode HTTP : seul POST est autorisé
# ============================================================================

def test_subscribe_get_method_returns_405(client: FlaskClient) -> None:
    """GET /waitlist doit renvoyer 405 Method Not Allowed."""
    response = client.get("/waitlist")
    assert response.status_code == 405


# ============================================================================
# IP hashing : pas d'IP en clair en BDD (vérif RGPD)
# ============================================================================

def test_subscribe_stores_ip_hashed_not_raw(client: FlaskClient, app: Flask) -> None:
    """L'IP est stockée hashée (SHA-256 = 64 chars hex), jamais en clair."""
    client.post("/waitlist", data={"email": "ip-test@example.com", "website": ""})

    with app.app_context():
        entry = db.session.execute(select(WaitlistEmail)).scalar_one()
        # Le test client utilise 127.0.0.1 → hash doit être différent
        assert entry.ip_hash is not None
        assert "127.0.0.1" not in entry.ip_hash
        assert len(entry.ip_hash) == 64  # SHA-256 hex
        # Caractères hex uniquement
        assert all(c in "0123456789abcdef" for c in entry.ip_hash)
