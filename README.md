# Gecko Agent — Landing Page

Landing page officielle de l'extension Chrome **[Gecko Agent](https://github.com/Gecko51/gecko-agent)**.

> Audience : visiteurs internationaux (page **en anglais**). Code et docs internes en français.

---

## Stack

- **Python 3.13** + **Flask 3.1**
- **Jinja2** (templating)
- **Tailwind CSS** (via CDN en dev, compilé en Phase 4)
- **Vanilla JS** (zéro framework côté client)
- **SQLite** (waitlist, Phase 3)
- **Gunicorn** + **Render.com** (prod)

---

## Installation locale

### Prérequis
- Python 3.13.x ([download](https://www.python.org/downloads/))
- Git
- Un éditeur (VS Code recommandé avec extension Python)

### Setup

```powershell
# 1. Cloner le repo (ou se placer dans le dossier projet)
cd "C:\Users\jalen\Desktop\VScode\06 - Landing pages\Gecko_agent"

# 2. Créer le venv (déjà fait si tu suis le kickstart)
python -m venv .venv

# 3. Activer le venv (Windows PowerShell)
.venv\Scripts\Activate.ps1

# 4. Installer les dépendances
pip install -r requirements-dev.txt

# 5. Créer le fichier .env à partir du template
Copy-Item .env.example .env

# 6. Générer un SECRET_KEY et le coller dans .env
python -c "import secrets; print(secrets.token_hex(32))"

# 7. Lancer le serveur dev
python run.py
```

Ouvrir [http://127.0.0.1:5000](http://127.0.0.1:5000) dans le navigateur.

---

## Commandes utiles

```powershell
# Lancer le serveur dev (debug + hot reload)
python run.py

# Lancer le linter
ruff check .

# Formatter le code
black .

# Lancer les tests (à partir de la Phase 3)
pytest -v

# Vérifier la santé du serveur
curl http://127.0.0.1:5000/healthz
```

---

## Variables d'environnement

Voir [.env.example](.env.example) pour la liste complète avec descriptions.

Variables critiques :
- `SECRET_KEY` — Clé Flask (obligatoire, jamais la valeur par défaut en prod)
- `FLASK_ENV` — `development` ou `production`
- `DATABASE_URL` — Chemin SQLite local (Phase 3+)

---

## Déploiement

### Render.com (recommandé)

1. Connecter le repo GitHub dans le dashboard Render
2. Render détecte automatiquement [render.yaml](render.yaml) et configure le service
3. Renseigner les variables d'env dans le dashboard (SECRET_KEY est généré automatiquement)
4. Premier deploy automatique sur push `main`

### Procfile (Heroku / Railway)

Le [Procfile](Procfile) à la racine est compatible Heroku, Railway, Fly.io. Adapter les commandes selon la plateforme.

---

## Documentation projet

| Fichier | Contenu |
|---------|---------|
| [PRD.md](PRD.md) | Vision produit, user stories, features, stack, milestones |
| [STRUCTURE.md](STRUCTURE.md) | Arborescence complète du projet |
| [DEV-RULES.md](DEV-RULES.md) | Règles de développement (code, sécurité, Git, workflows) |

---

## Avancement

### Phase 1 — Setup & squelette ✅
- App Factory Flask
- Route `/` (landing placeholder) + `/healthz`
- Template `base.html` avec Tailwind CDN + variables oklch
- Config racine (`.env.example`, `.gitignore`, `requirements.txt`, etc.)

### Phase 2 — Sections principales ⏳
À venir : Hero finalisé, Features, How it works, Tools.

### Phase 3 — Sections avancées ⏳
À venir : Models, FAQ, Waitlist form, Footer.

### Phase 4 — Polish & SEO ⏳
À venir : Tailwind compilé, images optimisées, meta tags, Lighthouse ≥ 90.

### Phase 5 — MVP Release ⏳
À venir : tests, headers sécurité, déploiement Render.

---

## License

MIT — voir [LICENSE](LICENSE) (cohérent avec le repo extension).
