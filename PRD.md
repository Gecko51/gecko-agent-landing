# Gecko Agent Landing Page — PRD

| Champ | Valeur |
|-------|--------|
| **Date** | 2026-05-20 |
| **Version** | v0.1 (MVP) |
| **Auteur** | AI-Generated PRD |
| **Stack** | Python 3.12 + Flask 3.x + Jinja2 + Tailwind CSS (CDN) + Vanilla JS |
| **Projet lié** | Extension Chrome [Gecko Agent](https://github.com/Gecko51/gecko-agent) |
| **Objectif business** | Acquisition utilisateurs + crédibilité produit pour l'extension Chrome |
| **Langue du site** | **English only** (cible internationale, cohérent avec le repo extension en anglais) |
| **Langue du code/docs** | Français (commentaires, docstrings, PRD, README dev) |

---

## 1. Vision & Problème

### Problème concret
L'extension **Gecko Agent** est aujourd'hui découvrable uniquement via GitHub. Sans page de vente claire, les utilisateurs non-tech ne comprennent pas immédiatement la valeur (un agent IA qui automatise le navigateur dans un side panel) et le funnel d'installation (clone → npm install → load unpacked) est dissuasif pour 90 % des cibles métier (sales, recruteurs, marketers).

### Cible
**Persona principal** — "Léa, Sales Ops, 32 ans" :
- Utilise LinkedIn Sales Navigator + Airtable au quotidien
- Fait du prospecting manuel répétitif (extraction profils, remplissage CRM)
- N'est **pas développeuse** mais sait installer une extension Chrome
- A entendu parler d'IA agentique mais n'a jamais testé concrètement

**Personas secondaires** :
- Recruteurs LinkedIn (sourcing batch)
- Marketers (extraction concurrentielle, scraping léger)
- Power users no-code (Make/Zapier) curieux d'agents browser

### Résultat attendu
1. **Compréhension en 5 secondes** — Le visiteur sait à quoi sert le produit dès le hero (Think → Act → Observe sur navigateur)
2. **Installation simplifiée** — CTA primaire vers le Chrome Web Store (futur) + fallback GitHub
3. **Crédibilité technique** — Liste des 9 tools, modèles supportés, open source MIT visible
4. **Trust & RGPD** — Page Privacy claire, mention OpenRouter, pas de tracking invasif

### Différenciation
- **vs Manus AI / Claude Computer Use** : extension Chrome légère, pas de VM cloud, l'utilisateur garde sa session
- **vs scrapers classiques (Bardeen, Magical)** : vrai agent IA (loop think-act-observe), pas juste des macros
- **vs Browser-Use / Skyvern** : UI side panel native Chrome, pas un produit dev

---

## 2. User Stories (MVP)

> Priorisation : 🔴 Must / 🟡 Should / 🟢 Nice

| # | User Story | Prio |
|---|-----------|------|
| US-01 | En tant que visiteur, je veux comprendre en 5 secondes ce que fait Gecko Agent, afin de décider si je continue à lire. | 🔴 |
| US-02 | En tant que visiteur, je veux voir un CTA d'installation visible en permanence, afin d'installer rapidement l'extension. | 🔴 |
| US-03 | En tant que prospect Sales/Recruteur, je veux voir des cas d'usage concrets (LinkedIn, Airtable), afin de me projeter dans mon workflow. | 🔴 |
| US-04 | En tant que développeur curieux, je veux accéder à la stack technique et au repo GitHub, afin d'évaluer la qualité du produit. | 🔴 |
| US-05 | En tant que visiteur mobile, je veux que la landing soit parfaitement responsive, afin de la lire sans pincer-zoomer. | 🔴 |
| US-06 | En tant que visiteur sensible à la vie privée, je veux lire la politique de confidentialité, afin de comprendre où vont mes données. | 🔴 |
| US-07 | En tant que visiteur indécis, je veux lire une FAQ qui répond à mes objections (prix, sécurité, modèles), afin de me rassurer. | 🟡 |
| US-08 | En tant que visiteur intéressé, je veux laisser mon email pour la prochaine release (waitlist Chrome Web Store), afin d'être notifié. | 🟡 |
| US-09 | En tant que visiteur, je veux voir une démo visuelle (GIF/vidéo), afin de comprendre concrètement le produit en action. | 🟡 |

---

## 3. Fonctionnalités Clés (MVP)

### Module A — Pages publiques

| Feature | Description | Critères d'acceptation | Complexité |
|---------|-------------|------------------------|------------|
| **Landing principale** | Page `/` avec sections : Hero, Features, How it works, Tools, Models, FAQ, CTA final, Footer | Toutes les sections visibles, navigation par ancres fonctionnelle, contenu fidèle au README | Moyen |
| **Privacy Policy** | Page `/privacy` reprenant `PRIVACY.md` du repo, mise en forme HTML | Contenu complet, lisible, lié depuis le footer | Simple |
| **404** | Page d'erreur custom avec mascotte Gecko + CTA retour accueil | Renvoyée sur toute route inconnue | Simple |

### Module B — Composants visuels

| Feature | Description | Critères d'acceptation | Complexité |
|---------|-------------|------------------------|------------|
| **Hero section** | Titre puissant + sous-titre + CTA primaire (Chrome Web Store) + CTA secondaire (GitHub) + visuel produit | Visible above the fold, CTA primaire ≥ 44px de hauteur, image optimisée WebP | Moyen |
| **Features grid** | Grille 3-4 colonnes des 11 features de l'extension avec icône Lucide + titre + description courte | Layout responsive (1 col mobile, 2 cols tablet, 3-4 desktop) | Simple |
| **How it works** | Animation/illustration du loop Think → Act → Observe en 3 cards | Compréhensible sans audio, accessible (alt texts) | Moyen |
| **Tools table** | Tableau des 9 outils d'automatisation (nom, description, exemple) | Scrollable horizontalement sur mobile | Simple |
| **Models showcase** | Logos des providers supportés (Claude, GPT, Gemini, Llama, OpenRouter) | Logos en SVG, dark/light mode compatible | Simple |
| **FAQ accordion** | 6-8 questions/réponses fréquentes en accordéon | Une seule ouverte à la fois, ARIA correct (button + aria-expanded) | Moyen |
| **Footer** | Liens GitHub, MIT License, Privacy, contact, copyright | Présent sur toutes les pages | Simple |

### Module C — Interactions

| Feature | Description | Critères d'acceptation | Complexité |
|---------|-------------|------------------------|------------|
| **Smooth scroll** | Navigation par ancres avec scroll fluide | Sans saccades, prend en compte le header sticky | Simple |
| **Waitlist form** [HYPOTHÈSE] | Formulaire email POST `/waitlist` → stocké en SQLite ou envoyé vers Resend/Mailjet | Validation côté serveur, anti-spam (honeypot), feedback visuel | Moyen |
| **Theme toggle** [HYPOTHÈSE] | Bouton dark/light mode persisté en localStorage | Respecte `prefers-color-scheme` par défaut | Simple |

> Les features [HYPOTHÈSE] sont des défauts raisonnables. À confirmer / déprioriser selon ton avis.

---

## 4. Stack Technique

| Couche | Technologie | Justification |
|--------|-------------|---------------|
| **Langage** | Python 3.12 | Imposé par toi. Versions LTS, syntaxe moderne (match, type hints natifs) |
| **Framework web** | Flask 3.0+ | Imposé par toi. Léger, parfait pour une landing (pas besoin de Django) |
| **Templating** | Jinja2 (natif Flask) | Inclus avec Flask, héritage de templates propre, conditionnels Pythoniques |
| **Styling** | Tailwind CSS 3.4 via CDN (MVP) puis CLI compilé (prod) | Charte exactement comme l'extension. CDN pour Phase 1, compilé en Phase 4 pour performances |
| **UI tokens** | Variables CSS oklch (copiées de `globals.css` extension) | Cohérence visuelle 100 % avec le side panel : neutral palette, radius 0.625rem |
| **Icônes** | Lucide (via `lucide-static` CDN ou SVG inlinés) | Même bibliothèque que l'extension → cohérence visuelle |
| **Police** | Inter (Google Fonts ou self-hosted woff2) | Lisible, moderne, gratuite, performante |
| **JS client** | Vanilla JS (ES2022) | Aucune dépendance lourde. Une landing n'a pas besoin de React/Vue |
| **Forms** | Flask-WTF + WTForms | Validation serveur + CSRF natif |
| **Stockage waitlist** | SQLite (via Flask-SQLAlchemy) | Zéro config, suffit pour < 10k emails. Migration PostgreSQL si scale |
| **Server WSGI** | Gunicorn 23.x | Production-ready, multi-worker, recommandé Flask |
| **Reverse proxy** | Nginx (si VPS) ou intégré (Render/Railway) | TLS, gzip/brotli, cache statiques |
| **Déploiement** | Render.com (free tier) [HYPOTHÈSE] | Build automatique depuis Git, HTTPS gratuit, suffit pour landing |
| **Analytics** | Plausible ou Umami (self-hosted) [HYPOTHÈSE] | Conformes RGPD, pas de bandeau cookie nécessaire |
| **Documentation IA** | Context7 MCP | Docs Flask/Jinja2/Tailwind à jour injectées dans Claude Code |

### Alternatives écartées (et pourquoi)
- **FastAPI** — Plus orienté API, surdimensionné pour une landing avec rendu HTML
- **Django** — Trop lourd pour quelques pages statiques
- **Static site (Astro/Hugo)** — Aurait été plus rapide, mais tu as imposé Flask
- **React/Next.js** — Hors stack imposée, et inutile ici (pas d'interactivité complexe)
- **Bootstrap** — Style ne matchera pas l'extension (Tailwind est plus proche du système de tokens shadcn)

---

## 5. Modèle de Données

### Base SQLite légère pour le MVP

```sql
table waitlist_emails {
  id           integer PK autoincrement
  email        text UNIQUE NOT NULL
  source       text         -- D'où vient l'inscription (hero/footer/faq)
  user_agent   text         -- Détection bot light
  ip_hash      text         -- IP hashée SHA-256 (RGPD friendly)
  created_at   datetime default CURRENT_TIMESTAMP
  confirmed    boolean default 0  -- Double opt-in si tu actives Mailjet

  index idx_email (email)
  index idx_created_at (created_at)
}
```

```sql
table contact_messages {  -- Si formulaire contact ajouté plus tard
  id         integer PK autoincrement
  email      text NOT NULL
  message    text NOT NULL
  ip_hash    text
  created_at datetime default CURRENT_TIMESTAMP

  index idx_created_at (created_at)
}
```

> Aucune table user / auth. La landing est 100 % publique, pas de comptes.

---

## 6. Routes Flask

| Méthode | Route | Description | Auth |
|---------|-------|-------------|------|
| GET | `/` | Page d'accueil (landing principale) | ❌ |
| GET | `/privacy` | Politique de confidentialité | ❌ |
| GET | `/terms` | Conditions d'utilisation [HYPOTHÈSE] | ❌ |
| POST | `/waitlist` | Inscription email waitlist (form Flask-WTF, retourne JSON ou redirect) | ❌ + CSRF + Honeypot |
| GET | `/sitemap.xml` | Sitemap SEO | ❌ |
| GET | `/robots.txt` | Robots crawlers | ❌ |
| GET | `/healthz` | Healthcheck Render/Railway | ❌ |
| GET | `/static/<path>` | Servi par Flask en dev, Nginx en prod | ❌ |
| * | `/<n'importe quoi>` | 404 custom | ❌ |

### Note langue
- **Toutes les routes sont servies en anglais**, sans préfixe `/en/`.
- Pas de Flask-Babel, pas de fichiers `.po`, pas de `hreflang`.
- `<html lang="en">` figé dans le `base.html`.

---

## 7. Pages & Navigation

| Page | Route | Sections / Composants clés | Auth |
|------|-------|---------------------------|------|
| **Home** | `/` | Header sticky, Hero, Features, How it works, Tools, Models, FAQ, Waitlist CTA, Footer | ❌ |
| **Privacy** | `/privacy` | Header, contenu markdown rendu, Footer | ❌ |
| **404** | `*` fallback | Header, illustration Gecko, CTA retour home, Footer | ❌ |

### Flow utilisateur principal
1. Arrivée sur `/` (via search, LinkedIn, X, GitHub)
2. Lecture Hero → clic CTA primaire **"Install on Chrome"** → ouvre Chrome Web Store dans nouvel onglet
3. *(Alternative)* Scroll → Features → Tools → FAQ → Inscription waitlist
4. *(Alternative)* Footer → GitHub repo

---

## 8. Contraintes Techniques

### Performance (objectif Core Web Vitals)
- **LCP** ≤ 2.0s
- **CLS** ≤ 0.05
- **INP** ≤ 200ms
- **Poids initial** : HTML + CSS critique + 1 image hero ≤ 150 KB compressé
- **Images** : WebP avec fallback PNG, `loading="lazy"` hors above-the-fold
- **Fonts** : `font-display: swap`, preload Inter en woff2

### Sécurité
- **HTTPS forcé** en production (HSTS 1 an, preload)
- **Headers** : CSP strict, X-Frame-Options DENY, X-Content-Type-Options nosniff, Referrer-Policy strict-origin
- **CSRF** : tokens Flask-WTF sur tout formulaire POST
- **Rate limiting** : Flask-Limiter sur `/waitlist` (5 req/min/IP)
- **Validation email** : regex + DNS check (optionnel via `email-validator`)
- **Honeypot** : champ caché anti-bots sur les formulaires
- **Secrets** : `.env` jamais commit, `SECRET_KEY` Flask via env var
- **Logs** : pas de PII en clair (hash IP, jamais l'email entier dans les logs)

### Tests (stratégie minimale)
- **Unit** : routes 200/302/404 via `pytest` + `pytest-flask`
- **Integration** : soumission formulaire waitlist (succès, doublon, honeypot piégé)
- **Lighthouse CI** : seuil 90 sur Performance, Accessibility, Best Practices, SEO
- **E2E** : Playwright en Phase 5 (smoke test des CTAs)

### Compatibilité
- **Navigateurs** : Chrome / Edge / Firefox / Safari 2 dernières versions
- **Mobile** : iOS Safari 15+, Chrome Android 100+
- **Python runtime** : 3.12.x (à figer dans `runtime.txt` pour Render)

### SEO
- **Meta tags** : title, description, OG (image 1200×630), Twitter Card — tous en anglais
- **Schema.org** : `SoftwareApplication` JSON-LD avec rating fictif retiré (uniquement les champs réels)
- **Sitemap.xml** généré dynamiquement
- **robots.txt** : autorise tout sauf `/healthz` et `/waitlist`
- **`<html lang="en">`** sur toutes les pages

### Accessibilité
- **WCAG 2.1 AA** ciblé
- Contraste texte ≥ 4.5:1
- Navigation clavier complète (Tab, Enter sur tous les CTAs)
- ARIA correct sur l'accordéon FAQ et le menu mobile
- Focus visible (outline custom mais visible)
- `prefers-reduced-motion` respecté (désactive les animations)

---

## 9. Milestones de développement

```
Phase 1 — Setup & squelette → git tag v0.1-setup
  - Init projet Flask (structure App Factory)
  - .env.example, .gitignore, requirements.txt, runtime.txt
  - Route GET / avec template base.html (header + footer + hero placeholder)
  - Tailwind CDN intégré dans base.html
  - Variables CSS oklch copiées de l'extension
  - Healthcheck /healthz
  - README.md projet (commandes locales)

Phase 2 — Sections principales → git tag v0.2-content
  - Section Hero finalisée (titre + sous-titre + 2 CTAs + visuel)
  - Section Features (grille 11 features avec icônes Lucide)
  - Section How it works (3 cards Think / Act / Observe)
  - Section Tools (table 9 outils responsive)
  - Smooth scroll + navigation par ancres

Phase 3 — Sections avancées → git tag v0.3-engagement
  - Section Models (logos providers)
  - FAQ accordéon (8 Q/R)
  - Waitlist form fonctionnel (SQLite + Flask-WTF + honeypot + rate limit)
  - Footer complet
  - Page /privacy
  - Page 404 custom

Phase 4 — Polish & SEO → git tag v0.4-polish
  - Tailwind compilé (purge CSS, ~10 KB final)
  - Optimisation images (WebP, lazy loading)
  - Meta tags + OG + Twitter Card
  - Sitemap.xml + robots.txt
  - JSON-LD SoftwareApplication
  - Lighthouse audit ≥ 90 sur tous les axes
  - Accessibilité (ARIA, contraste, clavier)

Phase 5 — MVP Release → git tag v1.0-mvp
  - Tests pytest (routes + waitlist)
  - Headers de sécurité (Flask-Talisman)
  - Déploiement Render.com
  - DNS custom (gecko-agent.com ou ton domaine)
  - HTTPS + HSTS preload
  - Plausible analytics configuré
  - Smoke test Playwright sur prod
```

### Phases optionnelles post-MVP
```
Phase 6 — Section "Use cases" détaillée (LinkedIn, Airtable, Sales)
Phase 7 — Blog en anglais (articles d'autorité SEO)
Phase 8 — Page /docs (intégrée depuis le README du repo)
Phase 9 — i18n FR/ES/DE si besoin marché (Flask-Babel, post-traction)
```

---

## 10. Hypothèses à confirmer

Marquées `[HYPOTHÈSE]` dans le doc. Récap :

1. **Déploiement Render.com** — alternative possible : Railway, Fly.io, VPS Hetzner
2. **Waitlist activée dès MVP** — sinon retirer la table et le form
3. **Analytics Plausible** — alternative : Umami self-hosted, ou rien
4. **Theme toggle dark/light** — l'extension est en light only, on peut s'aligner
5. **Page /terms** — pas obligatoire si tu n'as pas encore de CGU rédigées
