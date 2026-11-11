# CLAUDE.md — Digital Suggestion Box for Local Governance

This file is the operating plan for building a single, production-quality "digital
suggestion box for local governance" that implements **everything that exists in
`opencitivibes-main`**, while folding in the useful civic-location ideas from
`CivicTrack-main`.

Use this file as the source of truth for scope, architecture, conventions, build
order, and definition of done. Update it only when a decision changes.

---

## 1. Mission & Source Repositories

| Repo | Role | Path |
|------|------|------|
| `opencitivibes-main` | **Feature source of truth.** Full citizen-engagement platform (ideas, voting, comments, moderation, admin, analytics, auth, i18n, Law-25 privacy tooling). | `C:\Users\91888\Desktop\tmr\opencitivibes-main` |
| `CivicTrack-main` | **Civic-location feature donor.** Issue reporting with map pinning, reverse geocoding, photo upload, live map, hotspot dashboard, charts. | `C:\Users\91888\Desktop\tmr\CivicTrack-main` |

**Target:** a new unified project folder:

```
C:\Users\91888\Desktop\tmr\civic-suggestion-box\
```

Do **not** modify the two source repos. Treat them as read-only references.

### Guiding decision (locked)
- New project is **based on the opencivibes stack** (FastAPI + Next.js), not on
  CivicTrack's Supabase-only stack.
- **Drop Supabase.** All persistence goes through the FastAPI backend +
  SQLAlchemy. CivicTrack's map/photo features are re-implemented against the
  FastAPI API.
- The result must be a **full parity implementation of opencivibes** plus the
  civic geo layer. "Everything that exists" means every feature in Section 6,
  not just the obvious ones.

---

## 2. Non-Negotiable Decisions

1. **Backend:** Python 3.13, FastAPI 0.121.x, SQLAlchemy 2.0.x, Pydantic 2.12.x,
   Alembic, JWT auth, SQLite for dev / PostgreSQL for prod.
2. **Frontend:** Next.js 16 (App Router) + React 19 + TypeScript, Tailwind CSS,
   Radix/shadcn UI, Zustand, Axios, SWR, react-i18next, Recharts, Tiptap,
   next-themes, Sonner. Add Leaflet/react-leaflet for maps.
3. **Architecture:** strict layered backend `Router -> Service -> Repository`.
   Enforced by `backend/.importlinter`. Never import repositories directly from
   routers; never import FastAPI/Starlette in services/repositories; services
   raise domain exceptions, not HTTP exceptions.
4. **Config-driven branding:** all instance identity (name, entity, colors,
   logo, hero, locales, legal) comes from `platform.config.json` via
   `/api/config/public`. No hardcoded city names in components.
5. **i18n first:** every user-facing string goes through i18n. Ship `en`, `fr`,
   `es` locale files; default locale is configurable.
6. **Privacy & compliance:** keep the Law-25-style tooling (consent logs, data
   export, account deletion, retention, audit, 2FA, parental consent). Do not
   strip these to "simplify".
7. **Security:** never commit secrets; use `.env`. Never trust client URLs;
   validate uploads; keep security headers and rate limiting.

---

## 3. Target Repository Layout

Mirror opencivibes, then add the civic geo layer.

```
civic-suggestion-box/
├── CLAUDE.md                      # this file (copy here too)
├── README.md
├── docker-compose.yml             # dev/staging/prod profiles (from opencivibes)
├── docker-compose.dev.yml
├── .env.example
├── backend/
│   ├── main.py                    # FastAPI app + middleware + exception handlers
│   ├── init_db.py                 # seed categories + admin
│   ├── pyproject.toml / requirements.txt
│   ├── alembic/                   # migrations
│   ├── routers/                   # HTTP layer (see Section 8)
│   ├── services/                  # business logic
│   │   └── search/                # search backends (sqlite_fts5 / postgresql_fts)
│   ├── repositories/              # data access (db_models.py, database.py, *_repository.py)
│   ├── models/                    # schemas.py, exceptions.py, config.py, notification_types.py
│   ├── authentication/            # JWT + password hashing
│   ├── helpers/                   # pagination, sanitization, rate_limiter, security_headers, ...
│   ├── core/                      # logging, sentry, scheduler, correlation
│   ├── tasks/                     # scheduled cleanup
│   ├── templates/                 # email templates
│   ├── config/
│   │   ├── platform.config.json   # NEW: must be created (source repo has none)
│   │   └── legal/                 # terms/privacy markdown per locale
│   ├── data/                      # runtime sqlite + uploads (gitignored)
│   └── tests/
├── frontend/
│   ├── src/app/                   # App Router pages (see Section 9)
│   ├── src/components/            # UI + feature components
│   ├── src/lib/                   # api client, theme, seo, config provider
│   ├── src/store/                 # zustand auth store
│   ├── src/hooks/
│   ├── src/i18n/locales/          # en.json, fr.json, es.json
│   ├── src/types/
│   └── public/                    # icons, images, instance assets
├── instances/                     # per-deployment platform configs + legal + assets
│   └── <instance>/
│       ├── platform.config.json
│       ├── legal/*.md
│       └── images/
├── nginx/                         # reverse proxy templates
├── ntfy/                          # push notification server config
├── scripts/                       # setup/switch-instance/backup/deploy helpers
└── shared/config/platform.schema.json
```

---

## 4. Frontend Design Direction (REQUIRED)

The new UI must keep the **structure, layout, spacing, and component "vibes" of
opencivibes-main**, but with a **completely different, minimalist, clean color
system**. Do not reuse opencivibes' blue (#0066CC / #003366).

### 4.1 Palette — "Evergreen & Ivory"

A calm, civic, editorial palette. Two core hues (evergreen + warm clay) on warm
ivory neutrals. Use color sparingly; let whitespace do the work.

**Light mode**

| Token | Hex | Use |
|-------|-----|-----|
| `background` | `#F7F6F2` | Page background (warm ivory) |
| `surface` | `#FFFFFF` | Cards, panels, inputs |
| `surface-muted` | `#EFEDE7` | Subtle section fills, hover rows |
| `foreground` | `#1B2420` | Primary text (near-black green) |
| `muted-foreground` | `#5C6B63` | Secondary text, metadata |
| `border` | `#E2E0D8` | Hairline borders, dividers |
| `primary` | `#1F6F5C` | Primary buttons, links, active nav |
| `primary-hover` | `#17584A` | Primary hover/pressed |
| `primary-foreground` | `#FFFFFF` | Text on primary |
| `secondary` | `#C97B5A` | Clay accent (badges, highlights) |
| `secondary-foreground` | `#FFFFFF` | Text on secondary |
| `accent` | `#E9B44C` | Sparing highlight / rating |
| `ring` | `#1F6F5C` | Focus ring |
| `success` | `#3F8F5F` | Success |
| `warning` | `#C99A3F` | Warning |
| `destructive` | `#B4534B` | Errors / destructive actions |

**Dark mode**

| Token | Hex |
|-------|-----|
| `background` | `#121A17` |
| `surface` | `#1A2420` |
| `surface-muted` | `#223029` |
| `foreground` | `#F2F1EC` |
| `muted-foreground` | `#A7B3AC` |
| `border` | `#2C3A33` |
| `primary` | `#4FB39A` |
| `primary-foreground` | `#0F1A16` |
| `secondary` | `#E0977A` |
| `accent` | `#E9B44C` |

### 4.2 How to apply it

The opencivibes frontend is theme-driven. Wire the new palette through these
files (paths relative to `frontend/`):

- `src/app/globals.css` — CSS variables (`--background`, `--foreground`,
  `--primary`, `--secondary`, `--accent`, `--border`, `--ring`, `--radius`, ...)
  for `:root` and `.dark`. Replace opencivibes' blue values with the tables above.
- `tailwind.config.ts` — map `colors.primary`, `colors.secondary`, etc. to the
  CSS variables; keep the existing `tailwindcss-animate` setup.
- `src/lib/theme/themeConfig.ts` — default theme tokens + presets.
- `src/lib/config/PlatformConfigProvider.tsx` — reads branding from
  `/api/config/public`; ensure custom `primary_color` overrides the CSS var at
  runtime via the existing style-injection mechanism.
- `src/components/ui/*` — re-skin button/card/dialog/select/tabs to the new
  tokens (subtle borders, `rounded-xl`, no heavy shadows).
- `backend/config/platform.config.json` (and `instances/<name>/`) — set
  `branding.primary_color`, `secondary_color`, `accent`, `dark_mode`, `fonts`,
  `border_radius`.

### 4.3 Visual rules (minimalist & clean)

- **Generous whitespace.** Favor `gap-6`/`gap-8`, `py-10`+ section rhythm.
- **Flat by default.** Hairline `border-border`, minimal shadows; one soft
  elevation max on modals/popovers.
- **Rounded but restrained.** `rounded-xl` for cards, `rounded-lg` for buttons,
  `rounded-full` only for pills/avatars.
- **Typography.** Inter (or Geist) for body/UI; optional serif display
  (e.g. Fraunces/Lora via `branding.font_url`) for hero headings only. Tight
  tracking on headings, comfortable line-height on body.
- **Color discipline.** Primary is for actions/links; secondary/accent only for
  emphasis or status. Never color large background areas in primary.
- **Motion.** Subtle and fast (150–200ms ease-out). No bouncing.
- **Maps.** Use muted map tiles consistent with the palette; pins use
  `primary` (reported) and `muted-foreground`/`success` for status.
- **Accessibility.** Body text ≥ 4.5:1 contrast; visible `ring` on focus; all
  interactive elements keyboard reachable. Respect `prefers-reduced-motion`.

### 4.4 Do / Don't

- Do keep opencivibes' page structure, nav patterns, card layout, and spacing.
- Do keep shadcn/radix primitives and their behavior.
- Don't introduce a third bright brand color or gradients everywhere.
- Don't use the legacy blue anywhere except as a "link visited" fallback if
  unavoidable.
- Don't rely on color alone to convey status (add icon/label).

---

## 5. Tech Stack (exact)

**Backend (from opencivibes `pyproject.toml`)**
`fastapi==0.121.3`, `pydantic[email]==2.12.4`, `pydantic-settings==2.12.0`,
`sqlalchemy==2.0.44`, `alembic==1.17.2`, `uvicorn[standard]==0.38.0`,
`python-multipart`, `python-magic`, `bcrypt`, `pyjwt[crypto]`,
`cryptography`, `pyotp`, `bleach`, `markdown`, `loguru`, `sentry-sdk[fastapi]`,
`slowapi`, `apscheduler`, `httpx`, `psycopg2-binary`, `email-validator`.

Dev: `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-xdist`, `factory-boy`,
`faker`, `ruff`, `pyright`, `bandit`, `pip-audit`, `import-linter`, `pre-commit`.

**Frontend (from opencivibes `package.json`)**
`next@^16`, `react@^19`, `react-dom@^19`, `typescript@^5`, `tailwindcss@^3.3`
(with `tailwindcss-animate`), all `@radix-ui/react-*`, `lucide-react`,
`class-variance-authority`, `clsx`, `tailwind-merge`, `zustand`, `axios`, `swr`,
`i18next`, `react-i18next`, `recharts`, `date-fns`, `sonner`, `next-themes`,
`cmdk`, `dompurify`, `@tiptap/*`, `qrcode.react`,
`react-infinite-scroll-component`, `@sentry/nextjs`.

**Added from CivicTrack:** `leaflet`, `react-leaflet`,
`leaflet-defaulticon-compatibility`, `@types/leaflet`. Reverse geocoding via
OpenStreetMap Nominatim (server-side proxy preferred to avoid CORS/rate limits).

---

## 6. Feature Parity Checklist ("everything in opencivibes")

Tick every item before declaring done. Source references in
`opencivibes-main/backend` and `opencivibes-main/frontend`.

### Core citizen features
- [ ] Idea submission (rich text, title, description, category, language)
- [ ] Idea editing + soft delete + restore (admin)
- [ ] Leaderboard (approved ideas, scored)
- [ ] My Ideas (own submissions + status)
- [ ] Voting: upvote / downvote, one vote per user per idea
- [ ] Quality feedback on votes (quality keys per category)
- [ ] Comments (create, delete, sort: relevance/newest/oldest/most-liked)
- [ ] Comment likes
- [ ] Tags (create, popular, filter, autocomplete)
- [ ] Similar-ideas check before submit
- [ ] Full-text search (title/description/tags) + filters + autocomplete + suggestions
- [ ] Idea detail page with quality breakdown + trust signals
- [ ] Share tracking + share buttons
- [ ] Public user profiles (privacy-filtered)

### Auth & account
- [ ] Register / login (JWT), refresh, me
- [ ] Profile update, avatar upload, password change
- [ ] Email-code login (magic code)
- [ ] Password reset flow (request → verify → reset)
- [ ] 2FA (TOTP): setup, verify-setup, verify login, disable, backup codes
- [ ] Trusted devices ("remember this device", rename, revoke, revoke all)
- [ ] Activity history
- [ ] Roles: user, category admin, global admin, official
- [ ] Official request / grant / revoke / pending requests

### Moderation & trust
- [ ] Flag content (ideas/comments) with reasons; retract; status check
- [ ] Moderation queue, review (dismiss/action), flagged users
- [ ] Penalties (warning/ban/etc.), revoke, user penalty history
- [ ] Appeals: submit, my appeals, admin review (approve/reject)
- [ ] Keyword watchlist (literal + regex), test endpoint
- [ ] Pending-comment approval (approve/reject)
- [ ] Admin notes per user
- [ ] Moderation stats
- [ ] Content validation + sanitization
- [ ] Trust score, weighted score, score anomalies, quality signals

### Admin & analytics
- [ ] Admin: pending/approved/rejected/deleted ideas, merge, search
- [ ] Admin: comments (all, moderate, delete, restore, pending)
- [ ] Admin: categories CRUD + statistics
- [ ] Admin: users list/detail/update/delete/statistics
- [ ] Admin: admin roles (category moderators) CRUD
- [ ] Analytics: overview, trends (granularity), categories, top contributors
- [ ] Analytics: quality analytics, weighted scores, score anomalies
- [ ] Analytics: export (CSV/JSON), cache refresh
- [ ] Diagnostics: health, DB, system resources, SMTP test
- [ ] Admin notifications (ntfy) + counts + test

### Privacy, compliance, security
- [ ] Consent status, update, history; policy versions + reconsent
- [ ] Privacy settings (profile visibility)
- [ ] Data export (JSON/CSV); account deletion/anonymization
- [ ] Security audit logs, alerts, incidents, pending notifications
- [ ] Login events + security summary
- [ ] Data retention policy + scheduler + manual cleanup
- [ ] Parental consent (token verify/grant/deny/resend, minor status)
- [ ] Beta access gate (server-side password)
- [ ] Contact form
- [ ] Error reporting endpoint

### Platform & content
- [ ] Public platform config endpoint + branding provider
- [ ] Legal documents (terms/privacy markdown per locale) + moderation transparency + cross-border transfers
- [ ] i18n: en/fr/es, language switch, localized content fields
- [ ] SEO: metadata, canonical, structured data, sitemap, robots, OG/Twitter images
- [ ] PWA manifest + icons
- [ ] Dark mode toggle
- [ ] Cookie notice
- [ ] Command palette
- [ ] Loading/error/not-found states, skeletons, toasts
- [ ] Notifications (ntfy) admin viewer

### Civic geo layer (donor: CivicTrack)
- [ ] Idea location: latitude, longitude, neighborhood, address
- [ ] Map pin picker on submit with reverse geocoding (Nominatim)
- [ ] Optional photo upload for ideas (local storage or S3-compatible)
- [ ] Live map of approved ideas (Leaflet, muted tiles, status-colored pins)
- [ ] Hotspot list by neighborhood + map bbox endpoint
- [ ] "Top issues" chart (category counts) on dashboard
- [ ] Category config doubles as complaint categories vs. amenity requests

---

## 7. Data Model

Reuse opencivibes `repositories/db_models.py` entities exactly:

`users`, `categories`, `ideas`, `votes`, `comments`, `comment_likes`,
`admin_roles`, `tags`, `idea_tags`, `qualities`, `category_qualities`,
`vote_qualities`, `content_flags`, `user_penalties`, `appeals`,
`keyword_watchlist`, `admin_notes`, `email_login_codes`,
`password_reset_tokens`, `user_totp_secrets`, `user_backup_codes`,
`policy_versions`, `consent_logs`, `login_events`, `security_audit_logs`,
`share_events`, `privacy_incidents`, `trusted_devices`,
`parental_consent_tokens`, `parental_consent_logs`.

Core enums: `IdeaStatus`, `VoteType`, `StakeholderType`, `FlagReason`,
`FlagStatus`, `ContentType`, `PenaltyType`, `PenaltyStatus`, `AppealStatus`,
`SharePlatform`, `LoginEventType`, `LoginFailureReason`, `CommentSortOrder`,
`ProfileVisibility`, `ParentalConsentStatus`, `Granularity`, `ContributorType`.

### Civic geo additions (new, keep additive)
Prefer **new tables** over bloating `ideas`:

- `idea_locations` — `id`, `idea_id` (FK unique), `latitude` (float),
  `longitude` (float), `neighborhood` (str), `address` (str nullable),
  `created_at`.
- `idea_images` — `id`, `idea_id` (FK), `url` (str), `content_hash`
  (nullable), `created_at`.
- Indexes: `(latitude, longitude)` for bbox queries; `neighborhood` for hotspots.

Do not break existing `ideas` columns. Add Alembic migration(s).

---

## 8. API Surface (mount prefix `/api`)

Keep opencivibes routers/prefixes:

`/auth` (+ `/auth/email-login`, `/auth/2fa`, `/auth/password-reset`),
`/categories`, `/ideas`, `/votes`, `/comments`, `/tags`, `/search`,
`/admin` (+ `/admin/analytics`, `/admin/moderation`, `/admin/security`,
`/admin/notifications`), `/flags`, `/appeals`, `/officials`, `/sitemap`,
`/config`, `/contact`, `/legal`, `/notifications`, `/errors`, `/users`,
`/shares`, `/beta`, `/parental-consent`, `/health`.

Add civic endpoints under `/ideas`:
- `GET /api/ideas/map?min_lat&min_lng&max_lat&max_lng&status&category_id`
- `GET /api/ideas/hotspots?limit=&category_id=`
- `POST /api/ideas/{idea_id}/location`
- `POST /api/ideas/{idea_id}/images` (multipart)
- `DELETE /api/ideas/{idea_id}/images/{image_id}`

Response models live in `models/schemas.py`. Errors use domain exceptions →
centralized handlers in `main.py` with `correlation_id`.

---

## 9. Frontend Routes (App Router)

Keep opencivibes pages, apply new palette:

`/` (home/leaderboard), `/ideas/[id]`, `/ideas/[id]/edit`, `/submit`,
`/my-ideas`, `/search`, `/tags/[tag]`, `/profile`, `/settings/{consent,data,
delete-account,devices,security}`, `/signin`, `/signup`,
`/signup/pending-official`, `/officials`, `/officials/ideas`,
`/officials/ideas/[id]`, `/admin` (+ analytics/qualities/weighted-scores/
categories/category-admins/deleted-ideas/diagnostics/moderation/{appeals,
flagged-users,pending-comments,stats,watchlist}/notifications/officials/
rejected-ideas/users), `/contact`, `/privacy`, `/terms`,
`/parental-consent/*`.

Civic additions:
- `/map` — live map of approved ideas (Leaflet).
- `/dashboard` — totals, top issues chart, hotspot list (merge into admin
  analytics or keep public, per config).
- Submit page gains map picker + photo upload + neighborhood auto-fill.

Shared UI: use `src/components/ui/*`, `Navbar/*`, `Card`, `Button`, `Badge`,
`Alert`, `Skeleton`, `Toast`/`sonner`, `CommandPalette`, `ThemeToggle`.

---

## 10. Configuration

### Backend `.env`
From opencivibes `.env.example`: `SECRET_KEY` (required), `TOTP_ENCRYPTION_KEY`,
`DATABASE_URL`, `PLATFORM_CONFIG_PATH`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`,
`ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `CORS_ORIGINS`, `ENVIRONMENT`,
`LOG_LEVEL`, optional `SENTRY_DSN`. Plus email (`EMAIL_PROVIDER`, `SMTP_*`),
ntfy (`NTFY_*`, `APP_URL`), security/retention/TOTP tuning.

### Frontend `.env.local`
`NEXT_PUBLIC_API_URL=http://localhost:8000/api`,
`NEXT_PUBLIC_SITE_URL=http://localhost:3000`,
`NEXT_PUBLIC_DEFAULT_LOCALE`, `NEXT_PUBLIC_ENVIRONMENT`,
`NEXT_PUBLIC_BETA_MODE`, optional Sentry vars.

### `platform.config.json`
**Must be created** — the source repo ships none (it falls back to a Montreal
default). Create `backend/config/platform.config.json` and an
`instances/<instance>/platform.config.json` using
`shared/config/platform.schema.json`. Minimum:

```json
{
  "platform": { "name": "Civic Suggestion Box", "version": "1.0.0" },
  "instance": {
    "name": { "en": "Civic Suggestion Box", "fr": "Boîte à idées civique" },
    "entity": { "type": "city", "name": { "en": "Your City", "fr": "Votre ville" } },
    "location": { "display": { "en": "Your City" }, "coordinates": { "lat": 0, "lng": 0 }, "timezone": "UTC" }
  },
  "contact": { "email": "contact@example.org" },
  "localization": { "default_locale": "en", "supported_locales": ["en", "fr", "es"] },
  "branding": {
    "primary_color": "#1F6F5C",
    "secondary_color": "#C97B5A",
    "accent": "#E9B44C",
    "border_radius": "lg",
    "dark_mode": { "primary": "#4FB39A", "background": "#121A17", "surface": "#1A2420" }
  },
  "features": { "map": true, "images": true, "officials": true }
}
```

Remove all Montreal/Quebec defaults in code fallbacks; default to neutral
generic values or require config.

---

## 11. Build Order (phased, verify each phase)

1. **Scaffold** — create `civic-suggestion-box/`; copy backend, frontend,
   nginx, ntfy, scripts, shared, instances, docker files from opencivibes.
   Copy this `CLAUDE.md`. Init git.
2. **Baseline run** — create `.env` files, create `platform.config.json`,
   `python init_db.py`, start backend (`uvicorn main:app --reload --port 8000`)
   and frontend (`pnpm dev`). Confirm `/api/health`, `/api/config/public`,
   login as seeded admin, leaderboard/idea flows.
3. **Backend parity audit** — run existing backend tests
   (`uv run pytest` or `pytest`); fix import/route gaps; verify every router in
   Section 8 is mounted and every schema imports.
4. **Frontend parity audit** — confirm all routes in Section 9 render; fix
   broken imports; ensure API client covers all endpoints.
5. **Design system** — apply the "Evergreen & Ivory" palette (Section 4) across
   `globals.css`, `tailwind.config.ts`, `themeConfig.ts`, `PlatformConfigProvider`,
   and shadcn components. Verify light + dark.
6. **Civic geo layer** — add tables + migration + schemas + repositories +
   services + routers for locations/images/hotspots/map; add tests.
7. **Frontend civic UI** — map picker on submit, photo upload, `/map`,
   `/dashboard` (or admin analytics integration), reverse-geocode proxy.
8. **De-brand & i18n** — remove hardcoded Montreal strings; move all copy to
   i18n; create neutral en/fr/es; configure instance identity/branding.
9. **Security & compliance pass** — confirm 2FA, trusted devices, consent,
   export/delete, retention, audit, parental consent, beta gate all wired.
10. **Deployment** — docker compose dev/prod, nginx, ntfy, env docs, README.
11. **Final QA** — full test suite, lint, typecheck, import-linter, manual E2E
    of every checklist item in Section 6.

---

## 12. Commands

### Backend (from `backend/`)
```powershell
python -m venv venv
source venv/Scripts/activate          # Git Bash; or: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python init_db.py
uvicorn main:app --reload --port 8000
uv run pytest                          # if using uv
pytest -v --cov=. --cov-report=term-missing
ruff check .
ruff format --check .
pyright
lint-imports                           # import-linter (.importlinter)
```

### Frontend (from `frontend/`)
```powershell
pnpm install
pnpm dev
pnpm build
pnpm start
pnpm lint
npx tsc --noEmit
```

### Docker (project root)
```powershell
docker compose --profile dev up -d
docker compose --profile prod up -d
```

---

## 13. Coding Conventions & Guardrails

- Backend layer rules are enforced: routers → services → repositories.
  Routers may import `repositories.db_models` (types) and
  `repositories.database` (get_db) only.
- Services raise domain exceptions from `models/exceptions.py`; never
  `HTTPException`. Central handlers already map them.
- Every request gets `X-Correlation-ID`; log via `loguru`.
- All input validated with Pydantic; sanitize user HTML (bleach/DOMPurify).
- Parameterized SQL only; never build SQL strings from user input.
- Uploads: validate MIME/size, randomize filenames, store under
  `backend/data/uploads`, serve via `/data/uploads` + frontend `/uploads` rewrite.
- External URLs (Nominatim, images) validated; server-side proxy for geocoding.
- Frontend: `'use client'` only where needed; use the centralized `lib/api.ts`
  client; use `PlatformConfigProvider` for branding; never hardcode locale text.
- Accessibility and reduced-motion respected; keyboard focus rings visible.
- No secrets in code or git. Keep `.env` gitignored.

---

## 14. Definition of Done

- [ ] New project builds and runs backend + frontend locally from a clean clone.
- [ ] Every item in Section 6 is implemented and manually verified.
- [ ] All backend tests pass; lint, typecheck, and `lint-imports` pass.
- [ ] Frontend `pnpm lint`, `npx tsc --noEmit`, and `pnpm build` pass.
- [ ] Light + dark themes use the Evergreen & Ivory palette consistently.
- [ ] No hardcoded city/brand strings; instance config drives identity, colors,
      locales, legal.
- [ ] Civic geo features work: pin + photo submit, live map, hotspots, dashboard.
- [ ] Supabase is fully removed; no references remain.
- [ ] README + `.env.example` + platform config documented; docker compose works.
- [ ] Source repos `opencitivibes-main` and `CivicTrack-main` are untouched.

---

## 15. Reference File Map (read-only source)

**Backend (opencivibes)**
- `main.py` — app, middleware, all exception handlers
- `models/config.py` — settings/env
- `repositories/db_models.py` — all ORM models/enums
- `repositories/database.py` — engine/session
- `models/schemas.py` — all Pydantic schemas
- `models/exceptions.py` — domain exceptions
- `routers/*.py` — endpoint surface (Section 8)
- `services/*.py`, `services/search/*` — business logic
- `repositories/*_repository.py` — data access
- `services/config_service.py` — platform config + defaults
- `init_db.py` — seed categories/admin
- `.importlinter` — layer contracts

**Frontend (opencivibes)**
- `src/lib/api.ts` — full API client (auth, ideas, votes, comments, admin,
  moderation, search, analytics, officials, legal, contact, shares)
- `src/lib/config/PlatformConfigProvider.tsx` — branding
- `src/lib/theme/themeConfig.ts` + `src/app/globals.css` — theme tokens
- `src/i18n/locales/{en,fr,es}.json` — translations
- `src/components/**` — UI + feature components
- `src/app/**` — routes (Section 9)

**Civic donor (CivicTrack)**
- `components/SubmitForm.tsx` — report form + upload + location
- `components/MapPicker.tsx` — click-to-pin + Nominatim reverse geocode
- `components/LiveMap.tsx` — Leaflet live map + popups
- `components/MapLoader.tsx` — client-only map wrapper
- `components/HotspotList.tsx`, `components/TopIssuesChart.tsx` — dashboard
- `app/dashboard/page.tsx`, `app/map/page.tsx` — dashboard/map pages
- `lib/types.ts`, `setup.sql` — complaint shape (reference only; migrate to API)
