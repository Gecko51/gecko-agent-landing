"""Service waitlist : logique métier pure (sans Flask request context direct).

Les routes appellent ces fonctions, qui encapsulent les accès BDD et les règles
métier. Cela permet de tester la logique sans simuler une requête HTTP.
"""

from __future__ import annotations

from typing import TypedDict

from flask import current_app
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.waitlist import WaitlistEmail
from app.utils.security import hash_ip


class SubscribeResult(TypedDict):
    """Réponse renvoyée au front après une tentative d'inscription."""

    status: str  # "success" | "already_subscribed" | "error"
    message: str  # Message à afficher à l'utilisateur (en anglais)


def subscribe_email(
    email: str,
    source: str | None = None,
    ip: str | None = None,
    user_agent: str | None = None,
) -> SubscribeResult:
    """Inscrit un email à la waitlist.

    Comportement :
    - Si l'email n'existe pas : on l'enregistre, on renvoie status=success.
    - Si l'email existe déjà : on renvoie status=already_subscribed (pas une erreur).
    - Si erreur BDD : on log et on renvoie status=error.

    Args:
        email: Email validé en amont par WaitlistForm (lowercase, format OK).
        source: Section d'origine ("hero", "footer", "waitlist_cta"…).
        ip: IP du client (sera hashée avant stockage, jamais en clair).
        user_agent: User agent du navigateur (tronqué à 500 chars).

    Returns:
        SubscribeResult avec status et message user-friendly en anglais.
    """
    # Vérification préalable : email déjà inscrit ?
    # On évite un INSERT qui lèverait une IntegrityError pour rien.
    existing = db.session.execute(
        select(WaitlistEmail).where(WaitlistEmail.email == email)
    ).scalar_one_or_none()

    if existing is not None:
        return SubscribeResult(
            status="already_subscribed",
            message="You're already on the list — we'll notify you when we ship.",
        )

    # Création de l'entrée
    entry = WaitlistEmail(
        email=email,
        source=source or None,
        ip_hash=hash_ip(ip),
        user_agent=(user_agent or "")[:500] or None,
    )

    try:
        db.session.add(entry)
        db.session.commit()
    except IntegrityError:
        # Race condition rare : deux requêtes simultanées pour le même email.
        # On rollback et on renvoie le message "already subscribed" comme si OK.
        db.session.rollback()
        return SubscribeResult(
            status="already_subscribed",
            message="You're already on the list — we'll notify you when we ship.",
        )
    except Exception as exc:
        # Toute autre erreur BDD : on log et on renvoie une erreur générique.
        # Ne JAMAIS exposer le détail de l'exception au client (info leak).
        db.session.rollback()
        current_app.logger.exception("Erreur BDD lors de l'inscription waitlist : %s", exc)
        return SubscribeResult(
            status="error",
            message="Something went wrong. Please try again in a moment.",
        )

    # Succès
    return SubscribeResult(
        status="success",
        message="You're on the list. We'll email you when Gecko Agent goes live on Chrome Web Store.",
    )
