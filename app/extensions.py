"""Instanciation des extensions Flask (singletons partagés).

Pattern : on instancie les extensions ICI sans app (pas d'init_app),
puis create_app() appelle init_app() sur chacune. Ça évite les imports
circulaires : tout module peut faire `from app.extensions import db` sans
dépendre de app/__init__.py.
"""

from __future__ import annotations

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

# --- ORM & migrations ---
# db : objet principal SQLAlchemy. Tous les modèles héritent de db.Model.
db = SQLAlchemy()

# migrate : intégration Alembic pour gérer les migrations de schéma versionées
migrate = Migrate()

# --- Sécurité ---
# csrf : protection CSRF automatique sur tous les formulaires Flask-WTF
csrf = CSRFProtect()

# limiter : rate limiting global + spécifique par route
# - key_func=get_remote_address : limite par IP (plus tard, par user_id si auth)
# - default_limits : protection DoS basique sur toutes les routes
# - storage_uri : configuré via Config.RATELIMIT_STORAGE_URI (memory en dev)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per minute", "1000 per hour"],
)
