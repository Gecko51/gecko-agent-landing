"""Instanciation des extensions Flask (singletons partagés).

Pourquoi ce fichier ?
- Permet d'éviter les imports circulaires : tout module peut importer `db`
  ou `csrf` sans dépendre de `app/__init__.py`.
- Les extensions sont créées ici SANS app, puis attachées via `init_app(app)`
  dans `create_app()`.

Phase 1 : ce fichier est quasi vide. On le remplit au fur et à mesure
des phases pour rester dans le pattern.
"""

from __future__ import annotations

# Exemples d'extensions à ajouter en Phase 3 (waitlist) :
#
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# from flask_wtf.csrf import CSRFProtect
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
#
# db = SQLAlchemy()
# migrate = Migrate()
# csrf = CSRFProtect()
# limiter = Limiter(key_func=get_remote_address)
#
# Puis dans create_app() :
#   db.init_app(app)
#   migrate.init_app(app, db)
#   csrf.init_app(app)
#   limiter.init_app(app)
