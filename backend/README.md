# Shoe Visual Customizer Backend

FastAPI backend for the Shoe Visual Customizer MVP.

## Requirements

- Python 3.11+
- `uv`

Install `uv` if needed:

```powershell
winget install astral-sh.uv
```

## Setup

From `backend/`:

```powershell
uv sync
Copy-Item .env.example .env
```

## Run Locally

```powershell
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "Shoe Visual Customizer API",
  "environment": "local"
}
```

## Demo Auth

The local MVP uses a bearer token so protected endpoints already run with an explicit user identity.

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/auth/demo-login
```

Use the returned `accessToken` as:

```text
Authorization: Bearer local-demo-token-change-me
```

The demo token is for local MVP use only. Replace `DEMO_ACCESS_TOKEN` and disable demo-login before deploying beyond local development.

## Implemented Backend MVP

Current backend support includes:

- Demo auth and current-user lookup.
- SQLAlchemy persistence for users, scan sessions, model assets, designs, and export packages.
- Neon Postgres support for cloud database deployment.
- Scan session creation.
- MP4 upload with metadata validation.
- Automatic background processing after upload.
- Mock reconstruction output with GLB, OBJ, MTL, texture, and quality report.
- Model metadata and file download endpoints.
- Design draft save/reload/update.
- Visual design package export as a ZIP.

## Configuration

Settings are loaded from environment variables or `.env`.

Important values:

```text
STORAGE_ROOT=storage
DATABASE_URL=sqlite:///./storage/app.db
DATABASE_AUTO_CREATE_TABLES=true
ENABLE_REAL_RECONSTRUCTION=false
COLMAP_BIN=colmap
OPENMVS_BIN_DIR=
BLENDER_BIN=blender
```

For Neon Postgres, set `DATABASE_URL` to the pooled Neon connection string and disable
runtime schema creation:

```text
DATABASE_URL=postgresql://USER:PASSWORD@HOST-POOLER.neon.tech/neondb?sslmode=require&channel_binding=require
DATABASE_AUTO_CREATE_TABLES=false
```

The current Neon project provisioned for this app is:

```text
Project ID: billowing-wildflower-81765826
Branch ID: br-still-grass-aky91j80
Database: neondb
Role: neondb_owner
```

Do not commit the real connection string. Keep it in `backend/.env` or the deployment
platform secret manager.

## Database Migrations

Alembic owns schema changes after the initial Neon setup.

```powershell
uv run alembic upgrade head
```

Use the pooled Neon connection string for the API runtime. For long-running migration or
admin workflows, use a direct Neon connection string from the Neon Console.

## Local Storage

The backend creates these folders on startup:

```text
storage/raw-scans/
storage/frames/
storage/models/
storage/designs/
storage/exports/
```

## Phase 0 Acceptance Criteria

- FastAPI application is present at `app/main.py`.
- `/health` returns `status: ok`.
- CORS is configured for local Vite development.
- Environment and storage settings are centralized.
- SQLAlchemy configuration can run against SQLite locally or Neon Postgres in cloud environments.
