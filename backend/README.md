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
- SQLite persistence for users, scan sessions, model assets, designs, and export packages.
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
ENABLE_REAL_RECONSTRUCTION=false
COLMAP_BIN=colmap
OPENMVS_BIN_DIR=
BLENDER_BIN=blender
```

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
- SQLite configuration is ready for Phase 1 persistence.
