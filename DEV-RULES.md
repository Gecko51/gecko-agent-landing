# Gecko Agent Landing — DEV-RULES.md

Règles de développement pour ce projet Flask. À appliquer **sans exception**.
Adaptées à la stack : Python 3.12 / Flask 3 / Jinja2 / Tailwind CSS / Vanilla JS.

---

## 0. Règle de langue (la plus importante)

**Distinction stricte entre langue du code et langue du contenu :**

| Élément | Langue | Raison |
|---------|--------|--------|
| Tous les **textes visibles utilisateur** (templates Jinja2, meta tags, emails, messages flash, erreurs front) | **Anglais** | Audience internationale, cohérence avec le repo extension |
| Attribut `<html lang="en">` | `en` | SEO, accessibilité (lecteurs d'écran) |
| **Commentaires Python** (`# ...`) | Français | Convention CLAUDE.md utilisateur |
| **Docstrings** (`"""..."""`) | Français | Lecture rapide par Guillaume |
| **Variables, fonctions, classes** | Anglais (convention) | `snake_case` Pythonique standard |
| **PRD, STRUCTURE, DEV-RULES, CHANGELOG** | Français | Docs internes équipe |
| **README.md du projet** | Français | Doc dev interne |
| **Messages de commit Git** | Anglais (convention `feat:`, `fix:`...) | Standard Conventional Commits |

### Exemples concrets

```python
# Hash l'IP pour stockage RGPD-friendly avant de renvoyer le message de succès.
def subscribe_email(email: str, ip: str) -> dict[str, str]:
    """Inscrit un email à la waitlist et renvoie la réponse à afficher.

    Args:
        email: Email validé par WaitlistForm.
        ip: IP client (sera hashée).

    Returns:
        Dict avec status et message en anglais (affiché à l'utilisateur).
    """
    # Si l'email existe déjà, on renvoie un message en anglais user-facing
    if _is_duplicate(email):
        return {"status": "already_subscribed", "message": "You're already on the list."}

    _save(email, hash_ip(ip))
    return {"status": "success", "message": "Welcome aboard. We'll keep you posted."}
```

```html
<!-- Section hero — visible utilisateur, donc anglais -->
<section class="hero">
  <h1>Your AI agent, right in your Chrome side panel.</h1>
  <p>Automate browser tasks with a conversational AI that thinks, acts, and observes.</p>
</section>
```

> **Erreur à éviter** : mélanger anglais et français dans les templates ("Welcome / Bienvenue"). Si tu as une hésitation sur un wording → anglais, point final.

---

## 1. Règles de Code Python

### 1.1 Typage strict
- **Type hints obligatoires** sur toutes les fonctions (paramètres ET retour).
- Pas de `Any` sauf justification écrite en commentaire.
- Utiliser `from __future__ import annotations` en tête de chaque fichier pour les forward references propres.
- Préférer `list[str]` / `dict[str, int]` (syntaxe 3.9+) à `List[str]` / `Dict`.

```python
# ✅ Bon
def hash_ip(ip: str) -> str:
    """Hash l'adresse IP en SHA-256 pour stockage RGPD-friendly."""
    return hashlib.sha256(ip.encode()).hexdigest()

# ❌ Mauvais — pas de type hint
def hash_ip(ip):
    return hashlib.sha256(ip.encode()).hexdigest()
```

### 1.2 Docstrings Google-style
- **Obligatoires** sur toutes les fonctions publiques (non préfixées `_`).
- **Optionnelles** sur les fonctions privées triviales.
- En français (cohérence avec le projet et le profil utilisateur).

```python
def save_waitlist_email(email: str, source: str, ip: str) -> WaitlistEmail:
    """Enregistre un email dans la waitlist avec déduplication.

    Args:
        email: Adresse email validée (déjà passée par WaitlistForm).
        source: Section d'origine (hero, footer, faq) pour analytics.
        ip: IP client en clair — sera hashée avant stockage.

    Returns:
        L'instance WaitlistEmail créée ou existante (si doublon).

    Raises:
        ValueError: Si l'email est invalide (devrait être attrapé en amont).
    """
    ...
```

### 1.3 Commentaires français inline
- **Commenter chaque section logique** non triviale.
- Les commentaires expliquent le **pourquoi**, pas le **quoi**.
- Cible : un développeur front-end qui découvre Python doit pouvoir suivre.

```python
# Hash l'IP avant stockage : on garde la possibilité de détecter du spam
# (même IP qui inscrit 50 emails) sans stocker la PII en clair (RGPD).
ip_hash = hashlib.sha256(ip.encode()).hexdigest()
```

### 1.4 Nommage
- **Variables / fonctions** : `snake_case`
- **Classes** : `PascalCase`
- **Constantes** : `UPPER_SNAKE_CASE`
- **Modules / fichiers** : `snake_case.py`
- **Templates** : `snake_case.html`
- Pas d'abréviations cryptiques (`usr` → `user`, `req` → `request`).

### 1.5 Taille
- **Fonction** : max 40 lignes (corps). Au-delà → découper.
- **Module / fichier** : max 200 lignes. Au-delà → splitter en sous-modules.
- **Une fonction = une responsabilité.** Si tu utilises "et" pour la décrire, découpe-la.

### 1.6 Imports
Ordre standard (isort géré automatiquement) :
```python
# 1. Standard library
import hashlib
from datetime import datetime

# 2. Third-party
from flask import Blueprint, request
from sqlalchemy import select

# 3. Local (relatif au package app/)
from app.extensions import db
from app.models.waitlist import WaitlistEmail
```

Pas d'import circulaire. Pas d'import * (wildcard).

### 1.7 Error handling
- **Jamais de `except:` ou `except Exception:` vide.** Toujours spécifier l'exception.
- Logger l'erreur avec contexte avant de re-raise ou de retourner une erreur user-friendly.
- Au niveau routes Flask : enregistrer un error handler global (`@app.errorhandler(500)`).

```python
# ✅ Bon
try:
    email_record = save_waitlist_email(email, source, ip)
except IntegrityError:
    # L'email existe déjà — c'est un cas attendu, pas une erreur
    current_app.logger.info("Email déjà en waitlist : %s", email)
    return jsonify({"status": "already_subscribed"}), 200
except SQLAlchemyError as exc:
    current_app.logger.exception("Erreur BDD waitlist : %s", exc)
    return jsonify({"status": "server_error"}), 500
```

### 1.8 Outils de qualité
- **Linter** : `ruff check .` (remplace flake8 + isort + pyupgrade)
- **Formatter** : `black .` (line length 100)
- **Type checker** : `mypy app/` (recommandé en CI, optionnel en dev)
- **Pas un seul warning toléré** avant un tag de phase.

---

## 2. Règles UI/UX

### 2.1 Mobile-first
- **Designer pour 375px de large** (iPhone SE) en premier, élargir ensuite.
- Breakpoints Tailwind par défaut : `sm:` 640px, `md:` 768px, `lg:` 1024px, `xl:` 1280px.
- Tester avec Chrome DevTools en mode responsive avant tout commit visuel.

### 2.2 Fidélité au design de l'extension
- **Palette neutral oklch** copiée intégralement depuis `globals.css` de l'extension Chrome.
- **Radius** : 0.625rem (`rounded-[0.625rem]` ou variable Tailwind custom).
- **Icônes Lucide** uniquement — pas de mélange avec Heroicons ou autres.
- **Inter** comme police principale (cohérence avec écosystème shadcn).
- **Pas de gradients colorés flashy** — esthétique noir/blanc/gris épurée.

### 2.3 États obligatoires
Chaque composant interactif doit gérer 4 états :
- **Default** : état au repos
- **Hover / Focus** : feedback survol clavier/souris (outline visible)
- **Loading** : spinner ou skeleton (formulaire en cours de soumission)
- **Error / Empty** : message clair, jamais un écran vide silencieux

### 2.4 Spacing
- Système basé sur les multiples de 4px (convention Tailwind native).
- Cohérent verticalement : sections espacées en `py-16 md:py-24`.
- Conteneur principal : `max-w-6xl mx-auto px-4 sm:px-6 lg:px-8`.

### 2.5 Feedback utilisateur
- Toute soumission de formulaire → feedback visuel sous 200ms (bouton désactivé + spinner).
- Confirmation d'inscription waitlist → message flash + idéalement micro-animation (check vert).
- Erreur → message rouge sous le champ concerné, jamais juste console.log.

---

## 3. Règles de Structure

### 3.1 Colocation
- Les fichiers liés à une feature restent ensemble : `blueprints/waitlist/` contient routes + forms + service.
- Les partials Jinja2 d'une section sont colocalisés dans `templates/partials/`.

### 3.2 Séparation des responsabilités
- **Routes** (`routes.py`) : extraction request, appel service, retour response. Pas de logique métier.
- **Service** (`service.py`) : logique métier pure, testable sans Flask request context.
- **Models** (`models/`) : définition SQLAlchemy uniquement, pas de méthodes business complexes.
- **Templates** : rendu visuel, **zéro logique métier** (pas de calculs lourds en Jinja2).

### 3.3 Pas d'import circulaire
- Si tu en crées un par accident, le découpler via injection (passer en paramètre) ou via `extensions.py`.
- Vérifier avant chaque nouvelle dépendance entre modules.

### 3.4 Convention de nommage fichiers
- **Python** : `snake_case.py`
- **Templates Jinja2** : `snake_case.html` (partials préfixés `_underscore.html` quand inclus, pas étendus)
- **Static (CSS/JS/img)** : `kebab-case` (convention web)
- **Variables CSS** : `--color-foo-bar` (kebab-case)

---

## 4. Règles de Données

### 4.1 Accès BDD via service layer
- **Jamais de requête SQLAlchemy directe dans une route.**
- Les routes appellent un `service.py` qui encapsule la logique BDD.

```python
# ✅ Bon
@waitlist_bp.route("/waitlist", methods=["POST"])
def subscribe():
    form = WaitlistForm()
    if form.validate_on_submit():
        result = waitlist_service.subscribe(form.email.data, source="hero", ip=request.remote_addr)
        return jsonify(result), 200
    return jsonify({"errors": form.errors}), 400

# ❌ Mauvais — logique BDD dans la route
@waitlist_bp.route("/waitlist", methods=["POST"])
def subscribe():
    email = request.form.get("email")
    db.session.add(WaitlistEmail(email=email))
    db.session.commit()
    return "ok"
```

### 4.2 Validation systématique
- **Côté serveur** : Flask-WTF + WTForms avec validators (`Email()`, `Length()`, `DataRequired()`).
- **Côté client** : `<input type="email" required>` — c'est du confort UX, ne JAMAIS s'y fier seul.
- **Honeypot** : un champ caché en CSS qui doit rester vide. Si rempli → bot → rejeter silencieusement.

### 4.3 Sécurité BDD
- **Pas de SQL brut** sauf justification. Utiliser SQLAlchemy ORM ou Core (`select(...)`).
- Si SQL brut absolument nécessaire → **paramètres bindés** uniquement, jamais de concaténation.
- **Pas de PII en clair dans la BDD** : IP hashée, jamais de mot de passe (pas d'auth ici).

### 4.4 Secrets
- **Jamais commit de `.env`.** Maintenir `.env.example` à jour avec toutes les variables documentées.
- `SECRET_KEY` Flask : généré aléatoirement par variable d'env, jamais hardcodé.
- En prod (Render/Railway) : variables définies dans le dashboard, jamais dans le code.

### 4.5 Migrations
- **Tout changement de schéma passe par une migration Alembic.**
- Commande : `flask db migrate -m "description"` puis `flask db upgrade`.
- Ne jamais éditer une migration déjà appliquée en prod. Créer une nouvelle migration corrective.

---

## 5. Règles de Documentation Externe

### 5.1 Context7 MCP (obligatoire)
- **Avant d'utiliser une API Flask, Jinja2, SQLAlchemy, Tailwind** que tu n'as pas utilisée récemment : appeler Context7 pour récupérer la doc à jour.
- **Ne jamais coder de mémoire** une signature d'API de librairie tierce sans vérification.
- Raison : Flask 3 a introduit des changements (typage strict, app context), SQLAlchemy 2.x a un nouveau style de query (`select()` vs `Query.filter()`), Tailwind 4 change la config.

Exemple d'usage Context7 :
```
Avant d'écrire le formulaire WTForms, je vais d'abord récupérer la doc Flask-WTF
à jour via Context7 pour vérifier la syntaxe de FlaskForm + validators en 2026.
```

### 5.2 README.md du projet
- **Maintenu à jour à chaque fin de phase.**
- Sections obligatoires : Description, Stack, Installation locale, Variables d'env, Commandes utiles, Déploiement, License.
- Section "Avancement" mise à jour après chaque phase avec ce qui est implémenté.

### 5.3 `.env.example`
Toutes les variables documentées avec commentaire :
```bash
# Flask
SECRET_KEY=                  # Clé secrète Flask — générer avec : python -c "import secrets; print(secrets.token_hex(32))"
FLASK_ENV=development        # development | production

# Base de données
DATABASE_URL=sqlite:///instance/database.db   # SQLite local par défaut

# Sécurité
RATELIMIT_STORAGE_URI=memory://               # Mémoire en dev, Redis en prod si scale

# Analytics (optionnel)
PLAUSIBLE_DOMAIN=            # Ex: gecko-agent.com (vide = désactivé)
```

### 5.4 CHANGELOG.md (recommandé)
- Format `Keep a Changelog` : sections Added, Changed, Fixed, Removed par version.
- Mis à jour à chaque tag Git de phase.

---

## 6. Règles Git

### 6.1 Commits atomiques
- **Un commit = une tâche logique.** Ne pas mélanger features et fixes dans le même commit.

### 6.2 Format des messages
```
type(scope): description courte à l'impératif (max 72 chars)

[corps optionnel : pourquoi, pas comment]
```

Types valides :
| Type | Usage |
|------|-------|
| `feat` | Nouvelle fonctionnalité |
| `fix` | Correction de bug |
| `refactor` | Réécriture sans changement fonctionnel |
| `docs` | Documentation |
| `style` | Formatage (pas de changement de logique) |
| `test` | Ajout/modif de tests |
| `chore` | Maintenance (deps, config) |
| `perf` | Optimisation de performance |

Exemples :
```
feat(waitlist): ajoute le formulaire d'inscription avec honeypot anti-bot
fix(seo): corrige les meta OG manquants sur /privacy
chore(deps): upgrade Flask 3.0.3 → 3.1.0
```

### 6.3 Tags de phase
À chaque fin de phase MVP :
```bash
git tag v0.X-label
git push origin v0.X-label
```

### 6.4 Branches
- `main` : production (protégée, deploy auto)
- `dev` : intégration continue (optionnel pour ce projet solo)
- `feat/xxx` : branches de feature (mergées via PR ou squash en local)

### 6.5 Fichiers à NE JAMAIS commit
Vérifier `.gitignore` :
```
.env
.venv/
venv/
__pycache__/
*.pyc
instance/
*.sqlite
*.db
.pytest_cache/
.mypy_cache/
.ruff_cache/
node_modules/
dist/
*.log
.DS_Store
Thumbs.db
.vscode/
.idea/
```

---

## 7. Règles de Sécurité

### 7.1 Inputs
- **Sanitize + validate côté serveur** sur 100 % des inputs.
- Pour les emails : `email-validator` + regex stricte.
- Jamais de `eval()`, `exec()`, ou `subprocess.shell=True` sur input utilisateur.

### 7.2 Rate limiting
- **Flask-Limiter** sur `/waitlist` : 5 req/min/IP, 20 req/jour/IP.
- Sur toutes les routes publiques : limite globale 200 req/min/IP (anti-DoS basique).

### 7.3 CSRF
- **Flask-WTF** activé sur tous les formulaires POST.
- Token automatiquement injecté via `{{ form.hidden_tag() }}` dans les templates.

### 7.4 Headers de sécurité
Via **Flask-Talisman** en production :
- `Content-Security-Policy` : strict (script-src 'self', style-src 'self' 'unsafe-inline' pour Tailwind initial)
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy` : désactive géoloc/micro/cam non utilisés

### 7.5 Dépendances
- **Audit régulier** : `pip-audit` ou `safety check` une fois par semaine.
- Mettre à jour les libs critiques (Flask, SQLAlchemy) dans les 7 jours après publication d'une CVE.

### 7.6 Logs
- **Pas de PII** dans les logs : pas d'email entier, pas d'IP en clair, pas de tokens.
- Logger niveau `INFO` en prod, `DEBUG` en dev uniquement.
- Stack traces complètes uniquement pour les `ERROR` et `CRITICAL`.

---

## 8. Workflow de Fin de Phase

À exécuter dans l'ordre exact à chaque fin de phase MVP :

1. **Build** — `pip install -r requirements.txt && python -c "from app import create_app; create_app()"` → doit passer sans erreur
2. **Lint** — `ruff check . && black --check . && mypy app/` → corriger tous les warnings
3. **Tests** — `pytest -v` → 100 % au vert
4. **Vérification fonctionnelle manuelle** :
   - Lancer `python run.py`
   - Tester chaque page nouvellement ajoutée dans Chrome + Firefox + Safari iOS (devtools)
   - Tester clavier seul (Tab, Enter) sur les nouveaux composants
5. **README** — mettre à jour la section "Avancement" avec la phase terminée
6. **`.env.example`** — ajouter les nouvelles variables si nécessaire
7. **CHANGELOG.md** — ajouter une entrée pour la phase
8. **Commit final** : `chore(release): v0.X — [titre de la phase]`
9. **Tag Git** : `git tag v0.X-label && git push origin v0.X-label`

### Rapport de phase attendu

À fournir dans le commit ou un fichier `.phase-reports/phase-X.md` :

```markdown
## Rapport Phase X — [Titre]

### Implémenté
- [Feature A] — Section Hero avec CTAs primaire et secondaire
- [Feature B] — Grille Features responsive 1/2/3 colonnes

### Non implémenté (et pourquoi)
- [Feature C] — Toggle dark mode reporté en Phase 4 (besoin de tester le contraste oklch en dark)

### Problèmes rencontrés
- [P1] Tailwind CDN bloque la CSP stricte → solution : autoriser cdn.tailwindcss.com en script-src jusqu'à la Phase 4 (Tailwind compilé)
- [P2] Police Inter clignote au chargement (FOUT) → ajout `font-display: swap` et `<link rel="preload">`

### Recommandations Phase suivante
- Avant Phase 3 : valider la wording finale des CTAs avec Guillaume
- Avant Phase 4 : générer le visuel hero 1200×630 pour l'OG image
```

---

## 9. Workflow de Debug

Processus systématique en 6 étapes — à respecter quand un bug apparaît :

### Étape 1 — Observer (lecture seule)
- Reproduire le problème en local sans rien modifier.
- Lire les logs serveur (`app.logger`), la console navigateur, les erreurs Flask debug.
- Lire les fichiers concernés dans leur intégralité.

### Étape 2 — Diagnostiquer
- Identifier la **cause racine**, pas le symptôme.
- Exemple : "le form retourne 400" est un symptôme. La cause peut être CSRF token manquant, validator qui rejette, ou middleware Flask-Limiter qui bloque.

### Étape 3 — Hypothèses
- Lister 2 à 3 hypothèses classées par probabilité.
- Pour chacune : preuve attendue si vraie.

### Étape 4 — Valider avec l'utilisateur
- **Présenter le diagnostic et les hypothèses avant de toucher au code.**
- Attendre la validation de Guillaume avant de coder le fix.

### Étape 5 — Corriger (fix minimal)
- Appliquer le fix le plus petit qui résout la cause racine.
- **Ne pas refactoriser en même temps.** Le refactor mérite un commit séparé.

### Étape 6 — Expliquer
- Documenter le fix : ce qui était cassé, pourquoi, ce qui a été changé.
- Ajouter un test de régression si le bug peut revenir.

### Garde-fous debug
- **Ne jamais modifier > 1 fichier sans le signaler** dans la conversation.
- **Si le fix implique une migration BDD** → STOP et alerter explicitement.
- **Vérifier les logs** (Flask, navigateur, BDD si pertinent) avant de conclure.
- **Consulter Context7** si le bug semble lié à une API de librairie (Flask change parfois subtilement entre 2.x et 3.x).
- **Ne pas supprimer du code "parce que ça marche sans"** sans comprendre pourquoi il était là.

---

## 10. Règles spécifiques à Flask

### 10.1 App Context
- Toujours utiliser `current_app` (proxy) plutôt qu'une variable globale `app`.
- En tests : utiliser `app.app_context()` ou les fixtures pytest-flask.

### 10.2 Blueprints
- Un blueprint = un domaine fonctionnel cohérent.
- Préfixer les routes : `Blueprint("waitlist", __name__, url_prefix="/waitlist")` quand pertinent.

### 10.3 Templates Jinja2
- **Pas de logique métier** dans les templates : pas de calculs lourds, pas d'appels DB.
- Utiliser des **context processors** pour les variables globales (`year`, `version`, `is_authenticated`).
- Utiliser des **macros** (`{% macro %}`) pour les composants réutilisables (bouton, badge).
- Échappement automatique activé (par défaut Jinja2), ne jamais désactiver avec `|safe` sur input utilisateur.

### 10.4 Static files
- En dev : Flask sert `/static/` automatiquement.
- En prod : configurer Nginx ou le CDN pour servir `static/` avec cache-control long.
- Versioner les assets en query string (`main.css?v=1.2.3`) pour cache-busting.

---

## 11. Performance

### 11.1 Côté serveur
- **Gunicorn** : 2-4 workers (selon CPU), `--worker-class sync` (suffit pour landing).
- Toutes les routes GET → renvoient en < 100ms.
- Cacher les pages statiques (`/`, `/privacy`) avec `Cache-Control: public, max-age=300` côté response.

### 11.2 Côté client
- **CSS critique inliné** dans `<head>` (Phase 4), reste en async.
- **Images** : WebP avec fallback, `loading="lazy"` sauf hero.
- **Fonts** : `font-display: swap`, preload des poids utilisés.
- **JS** : `defer` sur tous les scripts non critiques.
- **Pas de jQuery, Bootstrap JS, ou autre framework lourd.** Vanilla JS suffit.

### 11.3 Lighthouse cible
| Axe | Score min |
|-----|-----------|
| Performance | 90 |
| Accessibility | 95 |
| Best Practices | 95 |
| SEO | 100 |

---

## Synthèse — 11 commandements

1. **Code = commentaires/docstrings FR. Contenu utilisateur = EN.** Jamais de mix.
2. **Type hints partout, jamais `Any` sans raison.**
3. **Commentaires en français, expliquant le *pourquoi*.**
4. **Context7 avant d'utiliser une API tierce de mémoire.**
5. **Validation serveur systématique. Le client n'est jamais à confiance.**
6. **CSRF + rate limit + headers de sécu en prod.**
7. **Mobile-first, fidèle au design oklch de l'extension.**
8. **Pas de logique métier dans les templates Jinja2.**
9. **Un commit = une tâche. Tag Git à chaque phase.**
10. **Fin de phase : build → lint → tests → README → tag.**
11. **Debug = observer → diagnostiquer → valider AVANT de coder.**
