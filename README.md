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

Deux options selon ton besoin :

| Plateforme | Stack | Quand l'utiliser |
|------------|-------|------------------|
| **[Netlify](#netlifycom-recommand%C3%A9-pour-le-mvp)** (recommandé MVP) | Site statique pré-rendu via Frozen-Flask | Pas de waitlist active, simple, gratuit, CDN mondial |
| **[Render](#rendercom-alternative)** | Flask + Gunicorn + BDD SQLite/PostgreSQL | Si tu réactives le formulaire waitlist côté serveur |

---

### Netlify.com (recommandé pour le MVP)

Le site est généré en HTML statique via **Frozen-Flask**, puis publié sur le CDN Netlify. Pas de serveur Flask en prod = ultra rapide + gratuit + HTTPS auto.

#### Étape 1 — Signup Netlify + connexion repo

1. **Signup** : [netlify.com](https://www.netlify.com) (login GitHub, gratuit)
2. **Import** : Dashboard → **Add new site** → **Import an existing project** → choisir GitHub → repo `Gecko51/gecko-agent-landing`
3. Netlify détecte automatiquement [netlify.toml](netlify.toml) et lit toute la config
4. Cliquer **Deploy site** → le premier build se lance (~3 min)

#### Étape 2 — Variables d'environnement (ajustables dans le dashboard Netlify)

| Variable | Valeur par défaut | Quand l'ajuster |
|----------|-------------------|-----------------|
| `SITE_URL` | `https://gecko-agent-landing.netlify.app` | Quand tu ajoutes un domaine custom (ex: `https://gecko-agent.com`) |
| `PYTHON_VERSION` | `3.13.7` | Si tu changes la version Python |
| `NODE_VERSION` | `22` | Si tu changes la version Node |

**Important** : modifier `SITE_URL` et relancer un deploy met à jour les URLs absolues dans le sitemap, OG, canonical et JSON-LD.

#### Étape 3 — Build pipeline

Le build exécute automatiquement (cf. `netlify.toml`) :
1. `pip install -r requirements.txt` → installe Flask, Frozen-Flask, etc.
2. `npm install` → installe Tailwind CLI
3. `npm run build:css` → compile `tailwind.css` minifié
4. `python freeze.py` → génère le site statique dans `build/`
5. Netlify publie `build/` sur le CDN

#### Étape 4 — Custom domain (optionnel)

1. Dashboard Netlify → **Domain settings** → **Add custom domain** → renseigner ton domaine
2. Netlify donne les CNAME/A records à configurer chez ton registrar (OVH, Cloudflare…)
3. HTTPS Let's Encrypt s'active automatiquement après propagation DNS
4. **Important** : mettre à jour `SITE_URL` dans les env vars Netlify avec le nouveau domaine + redéployer

#### Étape 5 — Plausible Analytics (optionnel)

Le template `base.html` charge le script Plausible si la variable `config.PLAUSIBLE_DOMAIN` est définie. Sur Netlify (statique), on doit injecter cette valeur au moment du freeze :

1. Dans `netlify.toml` → ajouter `PLAUSIBLE_DOMAIN = "gecko-agent.com"` dans `[build.environment]`
2. Adapter `freeze.py` pour passer la variable à la config Flask au moment du freeze
3. Le script Plausible sera inliné dans le HTML rendu

#### Étape 6 — Vérifier le déploiement

```bash
# Vérifier la page principale
curl -I https://gecko-agent-landing.netlify.app/

# Headers de sécurité (vérif netlify.toml [[headers]])
curl -I https://gecko-agent-landing.netlify.app/ | grep -i -E "(content-security|strict-transport|x-frame)"

# Sitemap valide
curl https://gecko-agent-landing.netlify.app/sitemap.xml

# robots.txt
curl https://gecko-agent-landing.netlify.app/robots.txt
```

#### Build local (preview avant push)

```powershell
.venv\Scripts\Activate.ps1
npm run build:css
python freeze.py

# Sert le dossier build/ sur http://localhost:8000
python -m http.server -d build 8000
```

#### Limitations vs Render

| Feature | Netlify static | Render (Flask) |
|---------|----------------|-----------------|
| Performance | ⚡ CDN mondial | Bien (1 région) |
| Coût | Gratuit | Gratuit (free tier limité) |
| HTTPS auto | ✅ | ✅ |
| **Waitlist form** | ❌ (utiliser Netlify Forms) | ✅ (SQLite/PostgreSQL) |
| Routes dynamiques (POST) | ❌ | ✅ |
| Endpoint `/healthz` JSON | ❌ (exclu du freeze) | ✅ |

Si tu réactives le formulaire waitlist sur Netlify, deux options :
1. **Netlify Forms** : ajouter `data-netlify="true"` sur le `<form>` (gratuit jusqu'à 100 submissions/mois)
2. Conserver le backend Flask sur Render (les deux peuvent coexister, le formulaire pointerait vers `gecko-agent-api.onrender.com`)

---

### Render.com (alternative)

1. **Signup Render** : [render.com](https://render.com) (gratuit, login GitHub)
2. **New Blueprint** : Dashboard → New → Blueprint → connecter le repo `Gecko51/gecko-agent-landing`
3. Render détecte `render.yaml` automatiquement et lit la config
4. Cliquer **Apply** → le premier deploy se lance (build ~2 min)
5. Une fois OK, l'URL sera `https://gecko-agent-landing.onrender.com` (ou similaire)

> **Free tier note** : le service "s'endort" après 15 min d'inactivité. Premier accès après veille = ~30s. Solution : upgrade payant ou un cron externe qui ping `/healthz` toutes les 10 min.

### Étape 2 — Variables d'environnement

`render.yaml` pré-remplit l'essentiel. Variables à **ajuster manuellement** dans le dashboard Render :

| Variable | Valeur recommandée | Note |
|----------|--------------------|------|
| `SECRET_KEY` | (auto-généré par Render) | Ne jamais modifier |
| `DATABASE_URL` | (voir Étape 3) | Choix entre SQLite et PostgreSQL |
| `PLAUSIBLE_DOMAIN` | `gecko-agent.com` (ou vide) | Domaine déclaré dans Plausible |
| `CHROME_WEBSTORE_URL` | URL extension publiée | Une fois l'extension validée |

### Étape 3 — Base de données

Choisir l'une des 3 options :

#### Option A — SQLite éphémère (gratuit, simple, données perdues à chaque deploy)
- **Convient pour** : démarrage, MVP, pas de waitlist critique
- **Config** : laisser `DATABASE_URL=sqlite:///instance/database.db` (default)
- ⚠️ Render free tier wipe le filesystem à chaque redéploiement → tu perds la table `waitlist_emails`

#### Option B — Render PostgreSQL gratuit (recommandé pour la waitlist)
1. Dashboard Render → **New +** → **PostgreSQL**
2. Plan : Free ($0/mois pendant 90 jours, puis $7/mois ou supprimé)
3. Region : Frankfurt (matche le service web)
4. Une fois créé, copier l'**Internal Database URL**
5. Dans le service web → Environment → `DATABASE_URL` → coller cette URL
6. Redéployer : `flask db upgrade` s'exécutera automatiquement et créera la table

#### Option C — Render Disk persistant ($1/mois pour 1 GB)
- Configurer un disque attaché au service web (mount sur `/opt/render/project/src/instance`)
- SQLite persiste entre les deploys
- Plus lourd, mais pas de migration BDD

### Étape 4 — DNS custom (optionnel)

Si tu as un domaine (ex: `gecko-agent.com`) :
1. Dashboard Render → service web → **Settings** → **Custom Domains** → Add `gecko-agent.com`
2. Render donne un CNAME à pointer (`xxxxx.onrender.com`)
3. Côté registrar (OVH, Cloudflare…) : créer un CNAME ou ALIAS vers l'adresse Render
4. Attendre propagation DNS (~5 min à 24h)
5. HTTPS Let's Encrypt configuré automatiquement par Render

### Étape 5 — Plausible Analytics (optionnel, RGPD-friendly)

1. **Signup Plausible** : [plausible.io](https://plausible.io) (essai 30 jours, ~$9/mois)
2. Ajouter ton site : domaine = celui que tu utilises (ex: `gecko-agent.com`)
3. Dans Render → Environment → `PLAUSIBLE_DOMAIN` = le domaine déclaré dans Plausible
4. Redéploy → le script Plausible se charge automatiquement (voir `base.html`, ligne conditionnelle)
5. Pas de bandeau cookie nécessaire (Plausible ne dépose pas de cookie, conformité RGPD native)

### Étape 6 — Vérifier le déploiement

```bash
# Healthcheck
curl https://gecko-agent.com/healthz
# Doit renvoyer : {"service":"gecko-agent-landing","status":"ok","version":"0.1.0"}

# Headers de sécurité (vérif Talisman actif)
curl -I https://gecko-agent.com/
# Doit inclure : Strict-Transport-Security, Content-Security-Policy, X-Frame-Options: DENY
```

Audit Lighthouse final :
```
Chrome → DevTools → Lighthouse → Mobile + Performance + A11y + Best Practices + SEO → Run
```
Cible : ≥ 90 sur les 4 axes.

### Alternatives à Render

| Plateforme | Procfile | Render.yaml | Free tier |
|------------|----------|-------------|-----------|
| **Railway** | ✅ | ❌ (utilise nixpacks ou Procfile) | $5 crédit/mois |
| **Fly.io** | ❌ (utilise `fly.toml`) | ❌ | 3 micro-VMs gratuites |
| **Heroku** | ✅ | ❌ | Plus de free tier |
| **PythonAnywhere** | ❌ | ❌ | Free pour 1 app web |

---

## Documentation projet

| Fichier | Contenu |
|---------|---------|
| [PRD.md](PRD.md) | Vision produit, user stories, features, stack, milestones |
| [STRUCTURE.md](STRUCTURE.md) | Arborescence complète du projet |
| [DEV-RULES.md](DEV-RULES.md) | Règles de développement (code, sécurité, Git, workflows) |

---

## Avancement

### Phase 1 — Setup & squelette ✅ `v0.1-setup`
- App Factory Flask + config Dev/Prod/Test
- Routes `/`, `/healthz`, `/favicon.ico` + 404 custom
- Template `base.html` avec Tailwind + variables oklch + Inter

### Phase 2 — Sections principales ✅ `v0.2-content`
- Section Features (11 cards) + How it works (3 steps) + Tools (9 outils)
- Bibliothèque d'icônes Lucide centralisée (`_icons.html`)
- Navigation par ancres + smooth scroll

### Phase 3 — Sections avancées ✅ `v0.3-engagement`
- Section Models + FAQ accordion (8 Q/R) + Footer enrichi 3 colonnes
- Page `/privacy` complète
- Waitlist : modèle SQLAlchemy + blueprint + form CSRF + honeypot + rate limit

### Phase 4 — Polish & SEO ✅ `v0.4-polish`
- Tailwind v4 compilé (25.8 KB vs ~3 MB CDN — gain 99 %)
- Sitemap.xml + robots.txt + JSON-LD enrichi (SoftwareApplication + Organization)
- Skip link + ARIA + focus visible + prefers-reduced-motion
- Mobile menu burger fonctionnel

### Phase 5 — MVP Release ✅ `v1.0-mvp`
- Flask-Talisman : HSTS + CSP + X-Frame-Options en prod uniquement
- Tests pytest : 19 tests (routes + waitlist + security) — tous au vert
- Plausible analytics conditionnel (RGPD-friendly)
- `render.yaml` complet avec preDeployCommand pour migrations
- Guide de déploiement complet dans ce README (étapes Render + DB + DNS + Plausible)

---

## License

MIT — voir [LICENSE](LICENSE) (cohérent avec le repo extension).
