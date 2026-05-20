"""Point d'entrée dev local.

Usage :
    python run.py

Lance le serveur de développement Flask avec debug + hot reload.
Ne JAMAIS utiliser en production — utiliser wsgi:app avec Gunicorn à la place.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

from app import create_app

# Charge les variables d'env depuis .env avant d'instancier l'app
load_dotenv()

# Crée l'instance Flask via l'App Factory
app = create_app()


if __name__ == "__main__":
    # En dev : host=127.0.0.1 (localhost uniquement), port 5000
    # Le debug se règle via FLASK_DEBUG dans .env (lu par create_app)
    app.run(
        host="127.0.0.1",
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
