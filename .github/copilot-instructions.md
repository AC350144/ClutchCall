# Copilot instructions — ClutchCall

Short, focused guidance for AI coding agents working in this repo.

- **High level:** Frontend is a Vite + React TypeScript app in `frontend/`. Backend is a Flask app in `backend/` that exposes JSON endpoints and a small chat/budget assistant. ML logic lives under `backend/app/` and models are loaded via `backend/app/model.py` and used by `backend/app/logic.py`.

- **Key entry points (read these first):**
  - `backend/main.py` — Flask routes, auth/token and MFA flows, DB init via `db.create_tables()`.
  - `backend/db.py` — database connection and schema helpers (credentials live here or are read from environment/config).
  - `backend/database.sql` — canonical schema for MySQL.
  - `frontend/package.json` — dev/build/test scripts and Node engine requirement (Node >= 20.19.0).
  - `frontend/components/ChatWidget.tsx` — example of frontend → backend interaction for chat messages.

- **Requests & dataflow:**
  - Frontend calls backend JSON endpoints such as `/chat`, `/login`, `/mfa/setup`, `/mfa/validate` (see `backend/main.py`).
  - Auth uses JWT cookies: `temp_token` for MFA pairing (temporary tokens with `mfa_pending`) and `token` for access tokens (`type` field is `access`). Keep cookie names and token shape consistent when editing auth code.
  - Budget ML: `backend/app/logic.py` builds input DataFrame and calls `model.predict(...)` from `backend/app/model.py` — preserve input column names `['income','fixed_expenses','savings_goal','months_to_goal']`.

- **Developer workflows / commands:**
  - Frontend dev: `cd frontend` then `npm install` then `npm run dev` (runs Vite on ~5173). Tests: `npx vitest` (also in CI). See `frontend/package.json`.
  - Backend dev: `cd backend`, install `requirements.txt`, ensure MySQL is running and schema from `backend/database.sql` is applied, then `python main.py` (Flask runs on `localhost:3000`).
  - Backend tests: `cd backend && python -m pytest tests/`.

- **Conventions & gotchas (repo-specific):**
  - `SECRET_KEY` in `backend/main.py` is a placeholder (`TEST_SECRET`). Do not leave real secrets in code — read from env vars for production. Tests and local dev expect debug ports (3000/5173).
  - Passwords are stored as `password_hash` using `bcrypt`; login flow expects `pass` (password) field in JSON bodies (see `login` route).
  - MFA flow: when `mfa_secret` is absent, `login` sets a `temp_token` cookie and frontend triggers `/mfa/setup` or `/mfa/validate`. The token payload includes `mfa_pending` and `email` — tests/mock code may rely on that shape.
  - DB initialization: `backend/main.py` calls `create_tables()` at import time — modifying `db.create_tables()` may change test setup expectations.

- **Testing notes:**
  - Frontend uses Vitest + Testing Library. Tests live under `frontend/tests/` and root `tests/` mirrors — run from `frontend/`.
  - Backend tests live under `backend/tests/` and may expect a local MySQL or test DB configuration.

- **Where to update when adding endpoints/features:**
  - Add frontend UI under `frontend/components/` and update routes in `frontend/src/`.
  - Add backend endpoints to `backend/main.py` and keep token/cookie semantics consistent.
  - If new ML inputs are added, update `backend/app/logic.py` and `backend/app/model.py` together and include column names used by the model.

- **When editing code, prefer:**
  - Minimal, focused changes that preserve existing API shapes (tokens, cookie names, request bodies).
  - Updating `README.md` and this instructions file when changing startup commands, ports, or test commands.

If anything here is unclear or you'd like more detail (CI, env var names, DB credentials locations), tell me which area to expand. Thank you!
