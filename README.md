# MediStock — Intelligent Medicine Stock Monitoring and Redistribution

> ⚠️ **Decision-support prototype using simulated data. Not for clinical use.**

---

## 1. Project Name

**MediStock** — BuildX 0.1, Challenge 03

---

## 2. Team Identifier

> **[TEAM-IDENTIFIER — replace this line before submission]**
>
> Team size: 6 members | Hackathon: Applied Computing & Innovation Hackathon (BuildX 0.1)

---

## 3. Problem Being Addressed

Healthcare institutions face critical inventory management challenges:

- Facilities may run out of essential medicines while neighbouring facilities sit on excess stock.
- Consumption patterns change with seasons, disease outbreaks, and staffing levels.
- Manual inventory checks are slow and error-prone.

This leads to medicine shortages at some sites and unnecessary wastage at others — a problem
directly addressable with intelligent stock monitoring and redistribution recommendations.

**Scope (from Challenge 03 spec):** Inventory management and operational decision support only.
Medical diagnosis and treatment recommendations are explicitly out of scope.

---

## 4. Proposed Solution

MediStock provides a **decision-support web application** that:

1. **Monitors** medicine inventories across multiple simulated healthcare facilities.
2. **Forecasts** days-to-depletion from historical consumption data (weighted moving average).
3. **Classifies** each inventory item as `critical / warning / ok / excess`.
4. **Recommends** redistribution quantities — which facility should send how much of which
   medicine to which other facility — with plain-language explanations.
5. **Displays** everything through a risk-coded dashboard.

The system uses only simulated data and clearly labels all outputs as decision support.

---

## 5. Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend | Python + FastAPI | 3.11+ / 0.115.x |
| ASGI server | Uvicorn | 0.32.x |
| Database | Firebase Firestore (emulator) | demo-medistock |
| DB fallback | JSON files | — |
| Frontend | React + Vite | 18.x / 5.x |
| Testing | pytest + httpx | 8.x / 0.27.x |
| Config | python-dotenv | 1.0.x |

---

## 6. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  Browser (React + Vite, :5173)                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Disclaimer banner  │  Inventory dashboard  │  Reco panel  │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────────┘
                           │  HTTP  /api/*
┌──────────────────────────▼──────────────────────────────────────┐
│  FastAPI backend (:8000)                                         │
│  ┌────────────┐  ┌──────────────────────────────────────────┐   │
│  │  /api/     │  │  engine/  (PURE PYTHON — no DB imports)  │   │
│  │  health    │  │  forecaster.py  risk.py  optimiser.py    │   │
│  │  inventory │  └──────────────────────────────────────────┘   │
│  │  recommend │  ┌──────────────────────────────────────────┐   │
│  └────────────┘  │  data/db.py                              │   │
│                  │  Firestore emulator ──► JSON fallback     │   │
│                  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

**Key architectural decision — engine isolation:**
The `engine/` package is pure-Python with no imports of Firebase, FastAPI, or any database
module. This means every algorithm can be unit-tested in milliseconds without any
infrastructure running. A test enforces this rule at the AST level.

---

## 7. Installation Instructions

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

### Environment

```bash
cp .env.example .env
# Edit .env if you have a real Firebase project; leave as-is for JSON fallback mode.
```

### Firebase emulator (optional — requires Java 11+ and Firebase CLI)

```bash
npm install -g firebase-tools
firebase emulators:start --only firestore
```

If Java or the Firebase CLI is not installed, the app automatically uses the JSON fallback.

---

## 8. Execution Instructions

### Run the backend

```bash
cd backend
# Activate venv first (see Installation)
uvicorn app.main:app --reload --port 8000
```

API docs available at: `http://localhost:8000/api/docs`

### Run the frontend

```bash
cd frontend
npm run dev
# Open http://localhost:5173
```

### Run tests

```bash
cd backend
pytest
```

### Build frontend for production

```bash
cd frontend
npm run build
# Output in frontend/dist/
```

---

## 9. Dataset and API Information

**All data is simulated.** No real patient or facility data is used.

| Data type | Source | Phase |
|-----------|--------|-------|
| Facility records | Hardcoded seed (3 facilities) | 1 |
| Medicine catalogue | Hardcoded seed (5+ categories) | 1 |
| Consumption history | Deterministic random generation (fixed seed) | 1 |
| Redistribution recommendations | Generated by engine at runtime | 2 |

No external APIs are used. The system is fully self-contained and can run offline.

The seed script (`backend/seed/seed_data.py`) uses a fixed random seed so every team member
gets identical data, making demos reproducible.

---

## 10. Known Limitations

| Limitation | Phase it will be addressed |
|------------|---------------------------|
| All data is simulated — no live hospital feeds | Out of scope (prototype) |
| JSON fallback has no concurrency control | Phase 2 (Firestore upgrade) |
| Forecaster uses simple moving average only | Phase 1 (weighted avg) |
| No authentication or access control | Out of scope for hackathon |
| No expiry-date tracking | Phase 3 (advanced extension) |
| Redistribution ignores transport cost and distance | Phase 3 (advanced extension) |
| Frontend has no offline support | Out of scope |
| Firebase emulator requires Java 11+ | Use JSON fallback if unavailable |

---

## Development Notes

### Branch strategy

```
main  ← stable releases only
dev   ← integration branch; all PRs target dev
feature/m1-setup     ← Tech Lead: scaffold (Phase 0)
feature/m2-engine    ← Engine developer: forecaster + risk (Phase 1)
...
```

### Commit prefix convention

| Prefix | Use |
|--------|-----|
| `chore:` | Build config, dependencies, tooling |
| `feat:` | New feature or endpoint |
| `docs:` | Documentation only |
| `test:` | Tests only |
| `fix:` | Bug fix |
| `refactor:` | Code change without behaviour change |

### PR rule

All PRs must pass `pytest` with zero failures before merging into `dev`.
