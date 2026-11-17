# MediStock — Project Context and Master Specification

> **Single source of truth.** Every architectural decision, parameter, naming convention and phase
> boundary in this project is governed by this document. If anything conflicts with a code comment
> or a team member's verbal instruction, this document wins.

---

## 1. Project Overview

**Project name:** MediStock  
**Hackathon:** BuildX 0.1 — Applied Computing & Innovation Hackathon  
**Challenge:** 03 — Intelligent Medicine Stock Monitoring and Redistribution  
**Team:** [TEAM-IDENTIFIER — replace before submission]  
**Tech lead (M1):** Responsible for backend engine, API, and infrastructure  

MediStock is a **decision-support prototype** that monitors medicine inventories across multiple
simulated healthcare facilities, estimates potential shortages, and recommends redistribution
strategies. It is **not** a clinical system and must display that disclaimer at all times.

---

## 2. Problem Statement (from Challenge 03 spec)

Healthcare institutions need to maintain adequate medicine inventories while avoiding unnecessary
stock accumulation and wastage. Stock imbalances can occur when one facility has excess inventory
while another experiences shortages. Inventory decisions become more challenging when consumption
patterns change and available resources are limited.

**Scope restriction (from official spec):** This challenge concerns inventory management and
operational decision support. Do **not** implement medical diagnosis or treatment recommendations.

---

## 3. Functional Requirements (from official spec)

The application must:

1. Maintain medicine inventory information across multiple simulated facilities.
2. Record historical medicine consumption.
3. Calculate current stock levels.
4. Estimate the number of days before stock depletion.
5. Identify facilities at risk of medicine shortages.
6. Identify facilities with potentially transferable excess stock.
7. Recommend redistribution quantities.
8. Display the reasons behind redistribution recommendations.

**Minimum demonstration scale:**
- At least **3** simulated healthcare facilities.
- At least **5** medicine categories.
- Inventory monitoring, stock depletion estimation, shortage identification.
- A redistribution recommendation mechanism.
- A dashboard displaying inventory risks.

**Advanced extensions (Phase 3+):**
- Medicine expiry-date management.
- Demand spike simulation.
- Redistribution cost optimisation.
- Different urgency levels for shortages.
- Comparison of alternative redistribution strategies.

---

## 4. Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Backend language | Python 3.11+ | Team expertise, rich ML/data ecosystem |
| Backend framework | FastAPI | Async, OpenAPI docs auto-generated, fast |
| Database | Firebase Firestore (local emulator first) | Real-time, document model suits inventory |
| DB fallback | JSON files in `backend/app/data/` | Works without Firebase/Java installed |
| Frontend | React 18 + Vite | Fast HMR, modern component model |
| Styling | Plain CSS (Phase 0); Tailwind optional (Phase 2) | Avoids config overhead in Phase 0 |
| Testing | pytest + httpx | Standard, async-compatible |
| Seed data | Python script (no external deps) | Reproducible without network |

**Firestore project ID (emulator):** `demo-medistock`

---

## 5. Data Model

All documents live in Firestore (or the JSON fallback). Collection names are canonical.

### 5.1 `facilities` collection

```json
{
  "id": "FAC-001",
  "name": "City General Hospital",
  "location": "Colombo",
  "type": "hospital"
}
```

### 5.2 `inventory` collection

```json
{
  "facility_id": "FAC-001",
  "medicine_id": "MED-001",
  "medicine_name": "Paracetamol 500mg",
  "category": "analgesic",
  "current_stock_units": 1200,
  "unit": "tablet",
  "reorder_level_units": 500,
  "last_updated": "2026-11-17T00:00:00Z"
}
```

### 5.3 `consumption_logs` collection

```json
{
  "facility_id": "FAC-001",
  "medicine_id": "MED-001",
  "date": "2026-11-16",
  "units_consumed": 48
}
```

### 5.4 `redistribution_recommendations` collection (written by engine)

```json
{
  "from_facility": "FAC-001",
  "to_facility": "FAC-002",
  "medicine_id": "MED-001",
  "quantity": 300,
  "urgency": "high",
  "reason": "FAC-002 has 2.1 days of stock; FAC-001 has 42 days surplus",
  "created_at": "2026-11-17T06:00:00Z"
}
```

---

## 6. Folder Structure

```
buildx-medicine-redistribution/          ← repo root
├── docs/
│   └── PROJECT_CONTEXT.md               ← this file
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                      ← FastAPI app + CORS + /api/health
│   │   ├── config.py                    ← ALL tunable parameters (no magic numbers)
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   └── db.py                    ← Firestore client + JSON fallback
│   │   ├── engine/                      ← PURE PYTHON — no Firebase/FastAPI imports
│   │   │   ├── __init__.py
│   │   │   ├── forecaster.py            ← consumption trend + days-to-depletion
│   │   │   ├── risk.py                  ← shortage/excess classification
│   │   │   └── optimiser.py             ← redistribution recommendation
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── inventory.py             ← GET/POST inventory endpoints
│   │   │   └── recommendations.py      ← GET recommendations endpoint
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── facility.py              ← Pydantic models
│   │       ├── inventory.py
│   │       └── recommendation.py
│   ├── seed/
│   │   ├── __init__.py
│   │   └── seed_data.py                 ← generates seed JSON + Firestore docs
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_health.py               ← /api/health endpoint test
│   │   └── test_engine_isolation.py     ← engine must not import forbidden modules
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   └── components/
│   │       └── Disclaimer.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .env.example
├── .gitignore
├── firebase.json
├── .firebaserc
├── firestore.rules
├── firestore.indexes.json
└── README.md
```

**Engine isolation rule (enforced by test):**
> `backend/app/engine/` modules MUST NOT import `firebase_admin`, `fastapi`, `app.data`, or any
> database module. The engine is pure-Python computational logic that accepts plain dicts and
> returns plain dicts. This keeps it unit-testable without any infrastructure.

---

## 7. Engine Specifications

### 7.1 Forecaster (`engine/forecaster.py`)

**Input:** list of `{"date": str, "units_consumed": int}` dicts (most recent N days)  
**Output:** `{"avg_daily_consumption": float, "days_to_depletion": float, "forecast_method": str}`

Algorithm (Phase 1):
- If ≥ `MIN_FORECAST_WINDOW` days of data: use weighted moving average (recent days weighted higher).
- If < `MIN_FORECAST_WINDOW` days: simple mean.
- days_to_depletion = current_stock / avg_daily_consumption (∞ if consumption = 0).

### 7.2 Risk Classifier (`engine/risk.py`)

**Input:** `{"days_to_depletion": float, "current_stock": int, "reorder_level": int}`  
**Output:** `{"risk_level": "critical"|"warning"|"ok"|"excess", "reason": str}`

Thresholds (from `config.py`):
- `days_to_depletion < CRITICAL_STOCK_DAYS` → `"critical"`
- `days_to_depletion < WARNING_STOCK_DAYS` → `"warning"`
- `days_to_depletion > EXCESS_STOCK_DAYS` → `"excess"`
- otherwise → `"ok"`

### 7.3 Optimiser (`engine/optimiser.py`)

**Input:** list of inventory items with risk levels across facilities  
**Output:** list of redistribution recommendations `{from, to, medicine_id, quantity, reason}`

Algorithm (Phase 2):
- Priority-queue approach: sort `"critical"` and `"warning"` by urgency.
- For each deficit facility, find `"excess"` facilities with the same medicine.
- Transfer `min(excess_surplus, deficit_need)` units.
- Record reason string in plain language.

---

## 8. API Design

Base path: `/api`  
All responses: `Content-Type: application/json`

| Method | Path | Phase | Description |
|--------|------|-------|-------------|
| GET | `/api/health` | 0 | Liveness check; returns version + db mode |
| GET | `/api/facilities` | 1 | List all facilities |
| GET | `/api/inventory/{facility_id}` | 1 | Inventory for one facility |
| POST | `/api/inventory/{facility_id}/consume` | 1 | Record consumption |
| GET | `/api/risk` | 1 | Risk summary across all facilities |
| GET | `/api/recommendations` | 2 | Latest redistribution recommendations |
| POST | `/api/recommendations/run` | 2 | Trigger optimiser run |

### `/api/health` response (Phase 0)

```json
{
  "status": "ok",
  "version": "0.1.0",
  "phase": 0,
  "db_mode": "json_fallback",
  "disclaimer": "Decision-support prototype using simulated data. Not for clinical use."
}
```

---

## 9. Frontend

### Phase 0

- Disclaimer banner (exact text): `"Decision-support prototype using simulated data. Not for clinical use."`
- Backend health check: fetch `/api/health` and display the JSON response.
- No auth, no routing.

### Phase 1

- Facility selector.
- Inventory table per facility with colour-coded risk levels.
- Days-to-depletion column.

### Phase 2

- Redistribution recommendation panel.
- Reason strings displayed verbatim.
- Run optimiser button.

---

## 10. Testing Strategy

| Test file | What it tests | Phase |
|-----------|--------------|-------|
| `test_health.py` | `GET /api/health` returns 200 + correct shape | 0 |
| `test_engine_isolation.py` | engine/*.py contain no forbidden imports (AST check) | 0 |
| `test_forecaster.py` | forecaster with known consumption series | 1 |
| `test_risk.py` | risk classifier boundary conditions | 1 |
| `test_optimiser.py` | redistribution logic with synthetic data | 2 |

**Rule:** `pytest` must pass with zero failures before any PR is merged to `dev`.

---

## 11. Security

- Credentials never committed. `.env` and `serviceAccount.json` are in `.gitignore`.
- Verify with: `git check-ignore -v .env serviceAccount.json`
- `serviceAccount.json` must appear **nowhere** in the repo — not even as a sample.
- `.env.example` contains placeholder strings only (e.g., `FIREBASE_PROJECT_ID=your-project-id`).
- Firestore rules (Phase 0): deny all reads/writes by default; allow only from authenticated
  service account in production.
- CORS: Phase 0 allows `http://localhost:5173` only. Production origins added in `.env`.

---

## 12. Configuration Parameters (`config.py`)

All magic numbers live here. No other file may hardcode these values.

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `CRITICAL_STOCK_DAYS` | 3 | Days-to-depletion below which risk = critical |
| `WARNING_STOCK_DAYS` | 7 | Days-to-depletion below which risk = warning |
| `EXCESS_STOCK_DAYS` | 30 | Days-to-depletion above which stock is excess |
| `MIN_FORECAST_WINDOW` | 7 | Min days of history for weighted avg forecast |
| `MAX_FORECAST_WINDOW` | 30 | Max days of history considered |
| `MIN_FACILITIES` | 3 | Minimum facilities required by spec |
| `MIN_MEDICINE_CATEGORIES` | 5 | Minimum medicine categories required by spec |
| `API_PREFIX` | `"/api"` | URL prefix for all API routes |
| `APP_VERSION` | `"0.1.0"` | Semantic version |
| `APP_PHASE` | `0` | Current build phase |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed CORS origins |
| `FIRESTORE_PROJECT_ID` | `"demo-medistock"` | Emulator project ID |
| `JSON_DATA_DIR` | `"backend/app/data/json_store"` | Fallback JSON directory |
| `DISCLAIMER` | (see below) | Required UI/API disclaimer text |

`DISCLAIMER = "Decision-support prototype using simulated data. Not for clinical use."`

---

## 13. Firebase Setup

**Emulator (development):**
```bash
firebase emulators:start --only firestore
```
Requires Java 11+ and Firebase CLI. If unavailable, the app automatically falls back to JSON files.

**Files:**
- `firebase.json` — emulator ports (Firestore: 8080, UI: 4000)
- `.firebaserc` — project alias `default` → `demo-medistock`
- `firestore.rules` — deny-all base rules (loosen per phase)
- `firestore.indexes.json` — empty index list (Phase 0)

**JSON fallback detection:**
`db.py` attempts to initialise `firebase_admin`. If it raises any exception (no credentials, no
emulator), it sets `DB_MODE = "json_fallback"` and reads/writes JSON files in `JSON_DATA_DIR`.
The `/api/health` endpoint reports which mode is active.

---

## 14. Phase Roadmap and Deliverables

### Phase 0 — Scaffold (this phase)

**Deliverables:**
- [ ] `docs/PROJECT_CONTEXT.md` (this file)
- [ ] All folders with `__init__.py` (using correct double-underscore name)
- [ ] `.gitignore` with `.env`, `serviceAccount.json`, `node_modules`, venv dirs
- [ ] `.env.example` with placeholder values only
- [ ] `requirements.txt` pinned to compatible versions
- [ ] `firebase.json`, `.firebaserc`, `firestore.rules`, `firestore.indexes.json`
- [ ] `backend/app/main.py` — FastAPI with CORS + `GET /api/health`
- [ ] `backend/app/config.py` — all parameters, no magic numbers
- [ ] `backend/app/engine/*.py` — docstring-only placeholders
- [ ] `backend/app/data/db.py` — docstring-only placeholder
- [ ] `backend/app/routers/*.py` — docstring-only placeholders
- [ ] `backend/app/models/*.py` — docstring-only placeholders
- [ ] `backend/tests/test_health.py` — passes green
- [ ] `backend/tests/test_engine_isolation.py` — passes green
- [ ] `frontend/` — Vite + React scaffold with disclaimer + health check
- [ ] `README.md` — all 10 required sections

**NOT in Phase 0:**
- Forecasting logic, risk classification, optimiser, seed data, authentication,
  dashboard features, Firestore live reads, redistribution endpoints.

### Phase 1 — Core Engine + Data Layer

- Implement `forecaster.py` and `risk.py`.
- Implement `db.py` JSON fallback reads.
- Implement `/api/facilities`, `/api/inventory/{id}`, `/api/risk`.
- Seed data script with 3 facilities, 5+ medicines, 14 days of consumption history.
- Tests: `test_forecaster.py`, `test_risk.py`.
- Frontend: inventory table with risk colour coding.

### Phase 2 — Redistribution Optimiser

- Implement `optimiser.py`.
- Implement `/api/recommendations` and `/api/recommendations/run`.
- Tests: `test_optimiser.py`.
- Frontend: recommendation panel with reason strings.
- Firebase emulator integration (optional upgrade from JSON fallback).

### Phase 3 — Advanced Extensions

- Expiry-date management.
- Demand spike simulation.
- Redistribution cost optimisation.
- Multiple urgency levels.
- Comparative strategy analysis.
- Production Firestore deployment.

---

## 15. Decisions Log

| Decision | Rationale | Date |
|----------|-----------|------|
| Firestore + JSON fallback | Firestore emulator needs Java; JSON fallback ensures CI and teammates without Java can still run the app | 2026-11-17 |
| Engine isolation rule | Keeps computational logic pure-Python and unit-testable without any infrastructure running | 2026-11-17 |
| `config.py` for all parameters | Judges will ask why specific thresholds were chosen; having them in one file makes the answer easy | 2026-11-17 |
| Phase 0 = scaffold only | 7-hour hackathon; getting the scaffold right once prevents painful refactors later | 2026-11-17 |
| `__init__.py` not `_init_.py` | Python requires double underscores; single-underscore version is silently ignored | 2026-11-17 |
