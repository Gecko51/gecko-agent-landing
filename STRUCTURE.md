# Gecko Agent Landing — STRUCTURE.md

Arborescence complète du projet Flask. Conventions respectées :
- **App Factory pattern** (`create_app()`) — recommandé Flask pour la testabilité
- **Blueprints** pour séparer les domaines (public, waitlist)
- **Templates Jinja2** avec héritage (`base.html` → enfants)
- **Static** servi en dev par Flask, par Nginx/CDN en prod

---

## Arborescence racine

```text
Gecko_agent/
│
├── .claude/                          # Configuration Claude Code (optionnel, géré par toi)
│   └── settings.json                 # Permissions, hooks, etc.
│
├── .env.example                      # Variables d'env documentées (à copier en .env local)
├── .gitignore                        # Fichiers à exclure du versioning
├── .python-version                   # Pour pyenv : 3.12.x
├── runtime.txt                       # Pour Render/Heroku : python-3.12.x
├── requirements.txt                  # Dépendances Python prod
├── requirements-dev.txt              # Dépendances dev (pytest, ruff, black)
├── pyproject.toml                    # Config ruff + black + isort centralisée
│
├── README.md                         # Doc projet : install, run, deploy
├── PRD.md                            # Product Requirements (généré)
├── STRUCTURE.md                      # Ce fichier
├── DEV-RULES.md                      # Règles de dev (généré)
├── LICENSE                           # MIT (cohérent avec l'extension)
│
├── wsgi.py                           # Point d'entrée Gunicorn : "wsgi:app"
├── run.py                            # Point d'entrée dev local : "python run.py"
│
├── render.yaml                       # Config déploiement Render (si tu pars sur Render)
├── Procfile                          # Alternative Heroku/Railway : "web: gunicorn wsgi:app"
│
├── app/                              # Package principal de l'application Flask
│   ├── __init__.py                   # create_app() — App Factory
│   ├── config.py                     # Classes Config / DevConfig / ProdConfig
│   ├── extensions.py                 # Instanciation db, csrf, limiter, babel
│   │
│   ├── blueprints/                   # Blueprints Flask (routes regroupées par domaine)
│   │   ├── __init__.py
│   │   │
│   │   ├── public/                   # Pages publiques (landing, privacy, 404)
│   │   │   ├── __init__.py           # Blueprint init : public = Blueprint(...)
│   │   │   ├── routes.py             # GET / , /privacy, /terms, sitemap, robots
│   │   │   └── seo.py                # Helpers SEO (génération sitemap, OG tags)
│   │   │
│   │   └── waitlist/                 # Inscription waitlist
│   │       ├── __init__.py
│   │       ├── routes.py             # POST /waitlist
│   │       ├── forms.py              # WaitlistForm (Flask-WTF + honeypot)
│   │       └── service.py            # Logique métier : save_email(), check_duplicate()
│   │
│   ├── models/                       # Modèles SQLAlchemy
│   │   ├── __init__.py
│   │   └── waitlist.py               # Modèle WaitlistEmail
│   │
│   ├── templates/                    # Templates Jinja2
│   │   ├── base.html                 # Layout racine : <html>, <head>, header, footer, {% block content %}
│   │   ├── _macros.html              # Macros réutilisables (icone, bouton, badge)
│   │   │
│   │   ├── public/                   # Templates pages publiques
│   │   │   ├── home.html             # Landing principale (extends base.html)
│   │   │   ├── privacy.html          # Politique de confidentialité
│   │   │   ├── terms.html            # CGU (si activé)
│   │   │   └── 404.html              # Page 404 custom
│   │   │
│   │   ├── partials/                 # Fragments inclus dans home.html
│   │   │   ├── header.html           # Header sticky + nav + mobile burger
│   │   │   ├── footer.html           # Footer (liens, copyright)
│   │   │   ├── hero.html             # Section hero
│   │   │   ├── features.html         # Grille des 11 features
│   │   │   ├── how_it_works.html     # Loop Think → Act → Observe
│   │   │   ├── tools.html            # Table des 9 tools
│   │   │   ├── models.html           # Logos providers
│   │   │   ├── faq.html              # Accordéon FAQ
│   │   │   ├── waitlist_cta.html     # Formulaire d'inscription
│   │   │   └── seo_head.html         # Meta tags + JSON-LD (inclus dans base.html)
│   │   │
│   │   └── waitlist/
│   │       ├── success.html          # Confirmation inscription (si pas en AJAX)
│   │       └── _flash.html           # Messages flash réutilisable
│   │
│   ├── static/                       # Assets statiques
│   │   ├── css/
│   │   │   ├── tailwind.css          # Tailwind CSS compilé (Phase 4) — sortie de `npx tailwindcss`
│   │   │   ├── tailwind.src.css      # Source Tailwind avec @apply customs + variables oklch
│   │   │   └── critical.css          # CSS critique inliné dans <head> (Phase 4)
│   │   │
│   │   ├── js/
│   │   │   ├── main.js               # Smooth scroll, mobile menu, FAQ accordion
│   │   │   ├── waitlist.js           # Soumission AJAX du form waitlist
│   │   │   └── theme.js              # Toggle dark/light (si activé)
│   │   │
│   │   ├── img/
│   │   │   ├── logo.svg              # Logo Gecko (copié depuis le repo extension)
│   │   │   ├── logo-128.png          # Favicon HD
│   │   │   ├── hero-cover.webp       # Visuel principal du hero (gecko agent cover)
│   │   │   ├── hero-cover.png        # Fallback PNG si WebP non supporté
│   │   │   ├── how-it-works.svg      # Illustration boucle Think/Act/Observe
│   │   │   ├── og-image.png          # Open Graph (1200×630) pour partages sociaux
│   │   │   │
│   │   │   ├── providers/            # Logos modèles LLM
│   │   │   │   ├── anthropic.svg
│   │   │   │   ├── openai.svg
│   │   │   │   ├── google.svg
│   │   │   │   ├── meta.svg
│   │   │   │   └── openrouter.svg
│   │   │   │
│   │   │   └── icons/                # Icônes Lucide en SVG inline (subset utilisé)
│   │   │       ├── brain.svg
│   │   │       ├── bot.svg
│   │   │       ├── chrome.svg
│   │   │       └── ...               # Une dizaine d'icônes max
│   │   │
│   │   ├── favicon.ico               # Favicon multi-tailles
│   │   ├── apple-touch-icon.png      # iOS home screen icon
│   │   └── fonts/
│   │       ├── Inter-Regular.woff2   # Self-hosted pour perf et RGPD
│   │       ├── Inter-SemiBold.woff2
│   │       └── Inter-Bold.woff2
│   │
│   └── utils/                        # Helpers transverses
│       ├── __init__.py
│       ├── security.py               # hash_ip(), validate_email(), sanitize_input()
│       ├── filters.py                # Filtres Jinja2 custom (markdown, format_date)
│       └── context_processors.py     # Variables injectées dans tous les templates (year, version)
│
├── migrations/                       # Migrations Alembic (Flask-Migrate)
│   ├── alembic.ini
│   ├── env.py
│   ├── script.py.mako
│   └── versions/                     # Fichiers de migration générés
│       └── 001_initial_waitlist.py
│
├── tests/                            # Tests pytest
│   ├── __init__.py
│   ├── conftest.py                   # Fixtures pytest (client, db, app)
│   ├── test_public_routes.py         # Tests routes /, /privacy, 404
│   ├── test_waitlist.py              # Tests inscription, doublon, honeypot
│   ├── test_security.py              # Tests CSRF, rate limit, headers
│   └── test_seo.py                   # Tests sitemap, robots.txt, OG tags
│
├── scripts/                          # Scripts utilitaires one-shot
│   ├── init_db.py                    # Création DB SQLite locale
│   ├── export_waitlist.py            # Export CSV des emails (pour Mailjet/Brevo)
│   └── generate_sitemap.py           # Génération statique sitemap.xml (optionnel)
│
├── instance/                         # Données runtime (jamais commit — dans .gitignore)
│   └── database.db                   # SQLite local (généré au premier run)
│
├── tailwind.config.js                # Config Tailwind (Phase 4) — purge des classes utilisées
├── package.json                      # Uniquement pour devDependencies Tailwind CLI
└── .github/
    └── workflows/
        ├── ci.yml                    # Lint + tests sur PR (ruff, black --check, pytest)
        └── deploy.yml                # Deploy auto sur push main (Render webhook)
```

---

## Notes sur l'arborescence

### Pourquoi App Factory ?
Le pattern `create_app()` permet d'instancier l'app avec différentes configs (dev, prod, test) et facilite les tests pytest sans variable globale. C'est la convention Flask recommandée dès qu'un projet dépasse `app.py` mono-fichier.

### Pourquoi des blueprints ?
Même pour une landing, séparer `public` (rendu HTML) et `waitlist` (POST + logique) rend le code plus lisible et permet d'ajouter facilement un blueprint `blog` ou `docs` plus tard sans refactor.

### Pourquoi `instance/` ?
Flask sait servir un dossier `instance/` situé à la racine pour les données runtime (DB SQLite, secrets locaux). Il est exclu du package, donc jamais embarqué dans un build / Docker / déploiement par erreur.

### Pourquoi `wsgi.py` ET `run.py` ?
- `run.py` → dev local avec `flask run` ou `python run.py` (debug=True, hot reload)
- `wsgi.py` → prod via `gunicorn wsgi:app` (multi-workers, pas de debug)

### Compilation Tailwind (Phase 4)
En Phase 1-3 : CDN suffit pour itérer vite.
En Phase 4 : `package.json` minimal avec `tailwindcss` CLI uniquement, compilation `tailwind.src.css` → `tailwind.css` purgée (~10 KB).

### Langue unique (English only)
Le projet est **monolingue anglais**. Pas de dossier `translations/`, pas de Flask-Babel, pas de routes préfixées par locale. Tous les textes Jinja2 sont écrits directement en anglais dans les templates. Si tu veux ajouter du multilingue plus tard (Phase 9 post-MVP), créer un dossier `app/translations/` à ce moment-là.

### Si waitlist non activée
Supprimer `blueprints/waitlist/`, `models/waitlist.py`, `migrations/`, et `Flask-SQLAlchemy` des requirements. La landing devient purement statique côté serveur (mais reste servie par Flask).

---

## Profondeur de l'arborescence

- **Niveau 1 (racine)** : ~20 fichiers/dossiers — config projet
- **Niveau 2 (app/)** : ~10 dossiers — séparation par responsabilité
- **Niveau 3+ (templates/, static/)** : détail métier

Total ≈ **70 fichiers** (sans compter les migrations générées).
Cohérent avec une landing pro maintenable mais pas surdimensionnée.
