"""Point d'entrée WSGI pour la production.

Usage :
    gunicorn wsgi:app --workers 2 --bind 0.0.0.0:$PORT

Gunicorn (ou un autre serveur WSGI) cible cet objet `app` exposé au niveau module.
"""

from __future__ import annotations

from dotenv import load_dotenv

from app import create_app

# Charge .env en prod aussi (Render injecte les vars, mais load_dotenv ne fait rien si .env absent)
load_dotenv()

# Instance WSGI exposée à Gunicorn
app = create_app()
