"""Modèle WaitlistEmail — emails inscrits à la liste d'attente Chrome Web Store.

Stocke :
- L'email (unique, normalisé en lowercase)
- La source d'inscription (hero, footer, modal…) pour analytics simples
- L'IP hashée SHA-256 (RGPD : on peut détecter du spam sans stocker la PII en clair)
- Le user agent (détection bot léger)
- created_at (timestamp d'inscription)
- confirmed (booléen, pour un double opt-in plus tard si on branche Mailjet)
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


def _utc_now() -> datetime:
    """Renvoie l'instant courant en UTC (timezone-aware).

    Note : SQLAlchemy 2.x recommande des datetimes UTC-aware pour éviter
    les bugs liés aux fuseaux horaires (notamment passages heure d'été).
    """
    return datetime.now(timezone.utc)


class WaitlistEmail(db.Model):
    """Email inscrit à la waitlist pour la sortie Chrome Web Store."""

    __tablename__ = "waitlist_emails"

    # --- Colonnes ---
    # Note : on utilise la syntaxe SQLAlchemy 2.x (Mapped[...] + mapped_column)
    # qui est typée et plus claire que l'ancien db.Column(...)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Email unique (un même email ne peut s'inscrire qu'une fois)
    # Longueur 255 = max RFC 5321 pour la partie locale + domaine
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    # Source d'inscription pour pouvoir attribuer le trafic plus tard
    # Ex: "hero", "footer", "waitlist_cta", "exit_intent"
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # IP hashée SHA-256 — 64 hex chars en sortie
    # On hashe pour avoir un identifiant de spam-tracking sans PII en clair
    ip_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # User agent du navigateur — utile pour repérer les bots primitifs
    # Tronqué à 500 chars pour éviter des UAs anormalement longs
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Timestamp d'inscription en UTC
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utc_now,
    )

    # Double opt-in : passe à True après clic sur lien de confirmation par mail
    # Pour l'instant : pas de confirmation → confirmed=False par défaut, à activer
    # si on branche Mailjet/Brevo en Phase post-MVP
    confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # --- Index supplémentaires ---
    # Index sur created_at pour les requêtes analytics (count par jour/semaine)
    __table_args__ = (
        Index("idx_waitlist_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        """Représentation lisible en debug (jamais affichée à l'utilisateur)."""
        # On masque la partie locale de l'email pour ne pas la cracher dans les logs
        masked = self.email.split("@")[0][:2] + "***@" + self.email.split("@")[-1]
        return f"<WaitlistEmail id={self.id} email={masked} source={self.source}>"
