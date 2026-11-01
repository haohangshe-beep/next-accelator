# next-accelator

A minimal starter for practicing AI-assisted coding as a team: Next.js with
TypeScript in `frontend/`, and FastAPI managed with uv in `backend/`.

```text
frontend/
  app/              # Homepage, layout, and styles
  package.json
  package-lock.json
backend/
  app/main.py       # FastAPI application and health endpoint
  pyproject.toml
  uv.lock
```

## Prerequisites

- Node.js 24 LTS (recommended; `frontend/.nvmrc` is included) and npm.
- Python 3.11 or newer and [uv](https://docs.astral.sh/uv/getting-started/installation/).
  `uv sync` can install the Python version in `backend/.python-version` if needed.

## Run locally

Clone the repository, then run the two apps in separate terminals.

```sh
git clone https://github.com/Jackyman666/next-accelator.git
cd next-accelator
```

**Frontend**

```sh
cd frontend
npm ci
npm run dev
```

Open <http://localhost:3000>. Start editing `frontend/app/page.tsx`.

**Backend**

```sh
cd backend
uv sync --locked
uv run uvicorn app.main:app --reload
```

Open the interactive API docs at <http://127.0.0.1:8000/docs>.
`GET /health` returns `{"status":"ok"}`:

```sh
curl http://127.0.0.1:8000/health
```

Add API routes in `backend/app/main.py`.
The apps run independently; the starter homepage does not call the API.
No environment variables or external services are required.

## Checks and production commands

From `frontend/`:

```sh
npm run lint
npm run typecheck
npm run build
npm start
```

From `backend/`, start without automatic reload:

```sh
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Dependencies

Use `npm install <package>` in `frontend/` or `uv add <package>` in `backend/`.
Commit the updated manifests and lockfiles together. Keep local `.env` files,
virtual environments, dependencies, and generated output out of Git.

## Try AI-assisted coding

Open this repository in your AI coding tool and replace the bracketed text in
this starting prompt:

> Read the README and inspect the existing code. Help me build [my idea] using
> the Next.js frontend and FastAPI backend. Suggest a small first feature, then
> implement it step by step. Explain the files you change and how I can run and
> verify the result. Keep the two folders separate and use uv for Python
> dependencies. Ask before adding a database or external service.

Start with one small feature, review the changes, and run the checks above before
committing. The homepage and health endpoint are placeholders for your own ideas.
