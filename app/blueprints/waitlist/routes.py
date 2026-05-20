"""Routes du blueprint waitlist.

POST /waitlist :
- Validation : Flask-WTF (CSRF + Email + Length)
- Anti-bot : honeypot (champ "website" caché qui doit rester vide)
- Rate limit : 5 req/min/IP (configuré ici via decorator @limiter.limit)
- Renvoie JSON pour permettre une soumission AJAX en Phase 4
"""

from __future__ import annotations

from flask import jsonify, request

from app.blueprints.waitlist import waitlist_bp
from app.blueprints.waitlist.forms import WaitlistForm
from app.blueprints.waitlist.service import subscribe_email
from app.extensions import limiter


@waitlist_bp.route("/waitlist", methods=["POST"])
@limiter.limit("5 per minute")
def subscribe():  # type: ignore[no-untyped-def]
    """Endpoint d'inscription à la waitlist.

    Returns:
        JSON {status, message, errors?}. Codes HTTP :
        - 200 : succès ou déjà inscrit (pas une erreur côté UX)
        - 400 : validation échouée (email invalide, champ manquant)
        - 422 : honeypot déclenché (on renvoie un succès fake pour ne pas alerter le bot)
        - 429 : rate limit dépassé (Flask-Limiter renvoie ça automatiquement)
    """
    form = WaitlistForm()

    # --- Étape 1 : honeypot ---
    # Si le bot a rempli le champ "website" caché, on simule un succès silencieux
    # plutôt qu'une erreur (pour ne pas signaler au bot qu'il est repéré).
    if form.is_honeypot_triggered():
        # Réponse "success" mais on ne sauvegarde RIEN
        return jsonify({
            "status": "success",
            "message": "You're on the list.",
        }), 200

    # --- Étape 2 : validation Flask-WTF ---
    if not form.validate_on_submit():
        # Renvoie les erreurs de validation au front (clé = nom du champ)
        return jsonify({
            "status": "error",
            "message": "Please check the form and try again.",
            "errors": form.errors,
        }), 400

    # --- Étape 3 : enregistrement via le service ---
    result = subscribe_email(
        email=form.email.data,
        source=form.source.data or "unknown",
        ip=request.remote_addr,
        user_agent=request.headers.get("User-Agent", ""),
    )

    # Tous les cas du service renvoient 200 (succès ou déjà inscrit = OK côté UX)
    return jsonify(result), 200
