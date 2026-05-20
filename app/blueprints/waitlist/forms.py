"""Formulaire d'inscription à la waitlist.

Stratégies anti-bot/spam appliquées :
1. **CSRF token** (auto via Flask-WTF) — empêche les soumissions cross-site
2. **Honeypot** — champ caché qui doit rester vide. Les bots remplissent tout
   automatiquement et se trahissent.
3. **Email validator strict** — vérifie la syntaxe et le format RFC
4. **Rate limiting** (côté route) — 5 req/min/IP max
"""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email, Length, Regexp


class WaitlistForm(FlaskForm):
    """Formulaire d'inscription waitlist.

    Champs :
    - email : adresse email à enregistrer (validation stricte)
    - source : d'où vient l'inscription (optionnel, rempli par le front)
    - website : HONEYPOT — doit rester VIDE pour passer la validation
    """

    # --- Email : champ principal visible ---
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Please enter your email."),
            Email(message="Please enter a valid email address."),
            Length(max=255, message="Email is too long."),
        ],
        # Filtre custom : normaliser en lowercase pour éviter les doublons "Foo@x" / "foo@x"
        filters=[lambda x: x.strip().lower() if isinstance(x, str) else x],
    )

    # --- Source : caché, rempli par le JS front (hero, footer, modal…) ---
    # On valide qu'il est court et alphanumérique pour éviter des injections
    source = StringField(
        "Source",
        validators=[
            Length(max=50),
            Regexp(r"^[a-zA-Z0-9_-]*$", message="Invalid source value."),
        ],
        default="",
    )

    # --- Honeypot : champ "website" caché en CSS, DOIT rester vide ---
    # Les bots remplissent ce champ automatiquement → on rejette les soumissions
    # où il n'est pas vide. Nom "website" pour piéger les bots qui remplissent
    # automatiquement les champs d'URL.
    website = StringField("Website")

    def is_honeypot_triggered(self) -> bool:
        """Renvoie True si le honeypot a été rempli (signe quasi-certain de bot)."""
        return bool(self.website.data and self.website.data.strip())
