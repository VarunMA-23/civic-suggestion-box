# Bengaluru Civic Suggestion Box

A modern, production-ready digital civic suggestion and engagement platform for local governance, tailored for the Bengaluru metropolitan region (BBMP).

Built with **FastAPI** (Python 3.13) + **Next.js 16** (React 19, TypeScript, Tailwind CSS, Leaflet). Designed for clean standalone execution without Docker containers or complex third-party API dependencies.

---

## 🌟 Highlights

- **English First & Pure Localization**: Operates primarily in English with complete i18n support.
- **Bangalore Civic Geo Integration**:
  - Live interactive map of approved civic proposals pinned to Bengaluru neighborhoods (Indiranagar, Koramangala, Bellandur, Cubbon Park, etc.).
  - Map pin picker with client/server geolocation support.
  - Neighborhood hotspots dashboard with category counts and analytical charts.
  - Optional photo uploads for suggestions.
- **Zero Third-Party API Burden**:
  - Pure SQLite storage (`backend/data/civic.db`) with full-text search (FTS5).
  - Console-based email login (one-time codes printed directly to server logs for instant local testing).
  - External paid analytics and tracking services disabled by default.
  - Free and open Leaflet / OpenStreetMap CARTO basemaps with local fallback coordinates.
- **No Docker Compose Required**: Runs cleanly on native PowerShell/Windows terminal using standard Python and Node.js toolchains.

---

## 🏗️ Architecture

```
civic-suggestion-box/
├── backend/                  # FastAPI 0.121 + SQLAlchemy 2.0 + SQLite
│   ├── authentication/       # JWT token generation and verification
│   ├── config/               # Platform settings (Bengaluru jurisdiction, colors, branding)
│   ├── data/                 # SQLite database and uploaded images
│   ├── models/               # Pydantic schemas, domain exceptions, models
│   ├── repositories/         # Database access layer
│   ├── routers/              # Clean API routes (/api/ideas, /api/auth, /api/civic, etc.)
│   ├── services/             # Core business rules and validation
│   ├── init_db.py            # Database initialization and admin seeding
│   ├── main.py               # Application entrypoint
│   └── requirements.txt      # Python dependencies
├── frontend/                 # Next.js 16 App Router + Tailwind CSS + Radix UI
│   ├── src/app/              # Next.js App Router pages (/, /map, /dashboard, /ideas, etc.)
│   ├── src/components/       # UI components & Leaflet map widgets
│   ├── src/i18n/             # Locales (English default)
│   ├── src/lib/              # Centralized API client & configuration provider
│   └── package.json          # Node dependencies
└── scripts/                  # Helper scripts
```

---

## 🚀 Quickstart: Running the Demo

### 1. Prerequisites
- **Python 3.11+ / 3.13** installed
- **Node.js 18+** with **pnpm** or **npm** installed

### 2. Backend Setup & Run

Open a terminal in `civic-suggestion-box/backend`:

```powershell
# Navigate to backend
cd c:\Users\91888\Desktop\tmr\civic-suggestion-box\backend

# Activate existing virtualenv (or create one: python -m venv venv)
.\venv\Scripts\Activate.ps1

# (Optional) Verify dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --port 8000
```

> **Backend API Docs**: Once started, open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.
>
> **Default Admin Account**:
> - Email: `admin@example.org`
> - Password: `ChangeMe!2024`

### 3. Frontend Setup & Run

Open a second terminal in `civic-suggestion-box/frontend`:

```powershell
# Navigate to frontend
cd c:\Users\91888\Desktop\tmr\civic-suggestion-box\frontend

# Start Next.js development server
pnpm dev
# (or: npm run dev)
```

> **Web App**: Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🗺️ Key Demo Features to Showcase

1. **Homepage & Leaderboard** (`http://localhost:3000`):
   - Displays approved citizen proposals for Bengaluru with vote counts, score filters, and category tabs.
2. **Interactive Live Map** (`http://localhost:3000/map`):
   - Shows live geo-located pins throughout Bengaluru (Indiranagar, Koramangala, Bellandur / ORR, Cubbon Park).
   - Click pins to preview suggestions and jump directly to their discussion pages.
3. **Civic Dashboard & Hotspots** (`http://localhost:3000/dashboard`):
   - Displays issue category breakdown and top hotspots by neighborhood.
4. **Submit an Idea with Map Pin** (`http://localhost:3000/submit`):
   - Click anywhere on the Bengaluru map to auto-set coordinates.
   - Attach photos and assign categories.
5. **Admin Panel** (`http://localhost:3000/admin`):
   - Sign in with `admin@example.org` / `ChangeMe!2024` to moderate ideas, manage categories, and review analytics.

---

## 🛡️ Privacy & Compliance

Configured in accordance with India's **Digital Personal Data Protection Act, 2023 (DPDP Act)**:
- Transparent consent settings under `/settings/consent`.
- User data export and account deletion under `/settings/data`.
- Device management and TOTP 2-Factor Authentication under `/settings/security`.
