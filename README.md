# Shoe Visual Customizer

Prototype MVP for a shoe-only video-to-3D reconstruction and visual customization workflow.

The system is intentionally split into three apps:

- `backend/`: Python FastAPI API, local storage, Neon Postgres persistence, reconstruction worker.
- `mobile/`: Flutter scanner app. Mobile captures two guided shoe videos and metadata only.
- `frontend/`: Vite + React web editor. Web loads GLB models and creates visual designs.
- `docs/`: Architecture, API contract, scan guidelines, and demo notes.

The current MVP requires two shoe scan passes: a side orbit and a top-angle orbit. The bottom sole is intentionally out of scope. Backend processing is asynchronous and prioritizes visual similarity and texture quality over industrial measurement accuracy.

## Local Pipeline

The real reconstruction worker expects these tools on the backend host:

```text
ffmpeg
colmap
InterfaceCOLMAP
DensifyPointCloud
ReconstructMesh
RefineMesh
TextureMesh
blender
```

Configure paths in `backend/.env` with `FFMPEG_BIN`, `COLMAP_BIN`, `OPENMVS_BIN_DIR`, and `BLENDER_BIN`.
Before a scan starts, the API checks tool availability, available RAM, free storage, and the configured thread limit. The web and mobile apps read:

```text
GET /api/system/reconstruction-readiness
```

Default safety settings are conservative for a laptop test run:

```text
RECONSTRUCTION_MAX_THREADS=4
RECONSTRUCTION_MIN_AVAILABLE_MEMORY_GB=4.0
RECONSTRUCTION_MIN_FREE_STORAGE_GB=8.0
```

Outputs are stored under `backend/storage/models/{scan_id}/` and served through authenticated API endpoints:

```text
shoe_preview.glb
shoe.obj
shoe.mtl
shoe_texture.png
metadata.json
quality_report.json
shoe_obj_package.zip
```

## Development

Backend:

```bash
cd backend
uv run alembic upgrade head
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

Mobile:

```bash
cd mobile
flutter run --dart-define=BACKEND_BASE_URL=http://YOUR_BACKEND_HOST:8000
```

## Deployment

See `docs/vps-android-deployment.md` for Android device usage, Docker Compose VPS deployment, and firewall/networking rules.
