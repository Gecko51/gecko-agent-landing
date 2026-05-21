"""Fixtures pytest partagées par tous les tests.

Pattern Flask classique :
- `app` : instance Flask créée avec TestConfig (BDD en mémoire, CSRF désactivé)
- `client` : test client Flask pour faire des requêtes
- `db_session` : session SQLAlchemy isolée, rollbackée après chaque test
"""

from __future__ import annotations

from typing import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from app.config import TestConfig
from app.extensions import db as _db


@pytest.fixture(scope="session")
def app() -> Generator[Flask, None, None]:
    """Instance Flask de test, partagée pour toute la session pytest.

    Utilise TestConfig : BDD SQLite en mémoire, CSRF désactivé, Talisman off.
    """
    _app = create_app(config_class=TestConfig)

    # Crée toutes les tables en mémoire au début de la session
    with _app.app_context():
        _db.create_all()
        yield _app
        # Drop toutes les tables à la fin de la session (cleanup propre)
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app: Flask) -> FlaskClient:
    """Test client Flask pour faire des requêtes HTTP simulées.

    Re-créé pour chaque test pour isoler les cookies/session entre tests.
    """
    return app.test_client()


@pytest.fixture(scope="function", autouse=True)
def db_session(app: Flask) -> Generator[None, None, None]:
    """Isolation de la BDD entre tests : rollback automatique après chaque test.

    autouse=True : appliqué à TOUS les tests sans avoir à le déclarer.
    Garantit que les inserts d'un test ne contaminent pas le suivant.
    """
    with app.app_context():
        yield
        # Cleanup : on supprime tout ce qui a été inséré pendant le test
        # Note : sur SQLite en mémoire, c'est rapide même avec beaucoup de rows
        _db.session.remove()
        # On vide les tables (pas drop, juste delete) pour garder le schéma
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()
