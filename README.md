# Hong Kong FTOS

Frontier Talent Operating System for the next-accelator monorepo. A learner finishes a
skill module, joins a mission, submits evidence, and receives an employer certification
on a public Skills Passport.

The UI is English. Tracks are **AI**, **NewSpace**, **Robotics**, and **Low Altitude Economy**.
Talent search and apprenticeships are labelled placeholders. The career navigator is a
rule list, not a chatbot.

```text
frontend/     Next.js App Router
backend/      FastAPI + uv, SQLite by default
```

## Prerequisites

- Node.js 22.13 or newer (`frontend/.nvmrc` pins 24) and npm.
- Python 3.11 or newer and [uv](https://docs.astral.sh/uv/getting-started/installation/).

## Run locally

From the repository root, use two terminals.

**Backend** (creates `backend/ftos.db` and seeds demo data on startup)

```sh
cd backend
uv sync --locked
uv run uvicorn app.main:app --reload
```

`GET /health` returns `{"status":"ok"}`. Interactive docs: <http://127.0.0.1:8000/docs>.

**Frontend** (proxies `/api/*` to the backend)

```sh
cd frontend
npm ci
npm run dev
```

Open <http://localhost:3000>.

To reset the demo, stop the API, delete `backend/ftos.db`, and start it again.

## Demo accounts

Password for every account: `demo-ftos-2026`

| Role | Email | Person |
| --- | --- | --- |
| Learner | learner@demo.ftos | Alex Chen — AI101 is already on the passport, and Port Community Demand Forecast is waiting for review |
| Employer | employer@demo.ftos | Jordan Lam, Harbour Frontier Labs — can publish missions and certify that submission |
| Admin | admin@demo.ftos | Sam Wu — can add, edit, and delete skill modules |

Public passport (no login): <http://localhost:3000/passport/alex-chen>

## Demo script

1. Sign in as the learner. Open **Skills → AI102**, confirm every self-check line, and record it. AI102 appears on the passport after a refresh.
2. Open **Missions**, filter track **AI** and skill **AI101**, and open **SME Grant Narrative Assistant**. Join it and submit an `https://` URL plus notes.
3. Sign out. Sign in as the employer. **Workspace** lists the pending Port Community Demand Forecast submission. Open it, choose **Demand forecasting**, and issue the certification.
4. Sign out and open `/passport/alex-chen`. Modules, the mission, and the certification are visible without a session.
5. Sign in as the learner again. **Navigator** shows at least three next steps (continue AI102 if it is still open, a mission you qualify for, and a Robotics foundation module).
6. Sign in as the admin and add a module from **Modules**.

The same path is covered by `cd backend && uv run pytest`.

## Seeded catalogue

Modules: `AI101`, `AI102` (requires AI101), `PE101` (NewSpace), `CV101` (Robotics), `DO101` (Low Altitude Economy).

Missions, all open and owned by Harbour Frontier Labs:

- Port Community Demand Forecast — AI, requires AI101 (Alex has a pending submission)
- Bilingual Service Triage Brief — AI, requires AI101 and AI102
- SME Grant Narrative Assistant — AI, requires AI101
- CubeSat Payload Health Log — NewSpace, requires PE101
- Warehouse Picking Vision Trial — Robotics, requires CV101
- Country Park Corridor Survey Plan — Low Altitude Economy, requires DO101

## API

Session auth is a bearer JWT (`Authorization: Bearer …`), kept in the browser under `ftos.token`. Routes live under `/api/v1` (auth, modules, missions, submissions, passport, navigator, admin modules, waitlist). `/health` is unchanged.

Useful environment variables (see `.env.example`):

| Variable | Default | Purpose |
| --- | --- | --- |
| `FTOS_DATABASE_URL` | `sqlite:///./ftos.db` | SQLAlchemy URL. Run uvicorn from `backend/` so the file is created there. |
| `FTOS_SECRET` | a dev string in `app/config.py` | HMAC secret for demo tokens. Change it before any shared deployment. |
| `API_PROXY_TARGET` | `http://127.0.0.1:8000` | Where Next.js forwards `/api/*`. |
| `NEXT_PUBLIC_API_URL` | empty | Set this only if the browser should call the API host directly instead of the proxy. |

PostgreSQL is not wired with a driver in this demo. The schema uses portable types, timezone-aware timestamps, and JSONB when the dialect is PostgreSQL. Point `FTOS_DATABASE_URL` at `postgresql+psycopg://…` and add a driver before using it. `create_all` builds tables on startup; it does not migrate existing tables.

This is a demonstration auth setup: one shared password, no rate limiting, and tokens in local storage.

## Checks

```sh
cd frontend && npm run lint && npm run typecheck
cd backend && uv run pytest
curl -s http://127.0.0.1:8000/health
```
