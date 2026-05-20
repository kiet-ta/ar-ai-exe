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
uv run alembic upgrade head
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
- Required two-pass MP4 upload: `side_orbit` and `top_orbit`.
- Manual/background processing start after both videos are uploaded.
- Real local reconstruction command orchestration for FFmpeg, COLMAP, OpenMVS, and Blender.
- Toolchain, RAM, storage, and thread-limit readiness checks before reconstruction starts.
- GLB, OBJ, MTL, texture, metadata, quality report, and OBJ ZIP package outputs.
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
ENABLE_REAL_RECONSTRUCTION=true
COLMAP_BIN=colmap
OPENMVS_BIN_DIR=/opt/openmvs/bin
BLENDER_BIN=blender
FFMPEG_BIN=ffmpeg
RECONSTRUCTION_FRAME_FPS=2.0
RECONSTRUCTION_MAX_FRAMES_PER_PASS=90
RECONSTRUCTION_MIN_BRIGHTNESS=28.0
RECONSTRUCTION_MIN_SHARPNESS=95.0
RECONSTRUCTION_DUPLICATE_HAMMING_THRESHOLD=4
RECONSTRUCTION_COMMAND_TIMEOUT_SECONDS=7200
RECONSTRUCTION_MAX_THREADS=4
RECONSTRUCTION_MIN_AVAILABLE_MEMORY_GB=4.0
RECONSTRUCTION_MIN_FREE_STORAGE_GB=8.0
```

Check local readiness with:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/system/reconstruction-readiness
```

The reconstruction worker does not fall back to mock assets. In Docker/VPS deploys, `backend/Dockerfile` builds OpenMVS and installs FFmpeg, COLMAP, and Blender. If any required binary or resource guard is missing, `/process` returns `toolchain_unavailable` and keeps the uploaded scan for retry after deployment is fixed.

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
