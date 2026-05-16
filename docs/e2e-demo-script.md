# End-to-End Demo Script

## Required Local Services

- Python 3.11+
- `uv`
- Node.js and npm
- Flutter SDK for the mobile app
- Optional: FFmpeg for real frame extraction

The backend still works in mock mode if FFmpeg is unavailable or the uploaded video is not readable.

## Backend Startup

From the project root:

```powershell
$env:UV_CACHE_DIR="F:\_FPT\EXE101\test-project\backend\.uv-cache"
backend\.venv\Scripts\uv.exe sync --project backend
backend\.venv\Scripts\uv.exe run --project backend uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

## Frontend Startup

From the project root:

```powershell
node "C:\Program Files\nodejs\node_modules\npm\bin\npm-cli.js" --prefix frontend install
node "C:\Program Files\nodejs\node_modules\npm\bin\npm-cli.js" --prefix frontend run dev -- --host 127.0.0.1 --port 5173
```

Open:

```text
http://127.0.0.1:5173
```

## Flutter Startup

From `mobile/`:

```powershell
flutter pub get
flutter run --dart-define=BACKEND_BASE_URL=http://127.0.0.1:8000
```

For Android emulator:

```powershell
flutter run --dart-define=BACKEND_BASE_URL=http://10.0.2.2:8000
```

## Test Scan Data

Use these values in the mobile setup form:

```json
{
  "shoe": {
    "sizeSystem": "EU",
    "size": "42",
    "side": "left",
    "type": "sneaker",
    "material": "canvas",
    "condition": "used"
  },
  "measurements": {
    "lengthCm": 27.0,
    "widthCm": 9.5
  },
  "scanSetup": {
    "calibrationReference": "A4 paper",
    "lighting": "bright",
    "background": "plain"
  },
  "customizationGoal": ["change_color", "add_sticker", "add_text"]
}
```

## Demo Flow

1. Start the FastAPI backend.
2. Start the Vite frontend.
3. Run the Flutter mobile app.
4. In Flutter, complete scan metadata.
5. Record a guided shoe scan video.
6. Upload the video.
7. Copy the scan session ID from the result screen.
8. Open the frontend and paste the scan session ID.
9. Load the completed scan.
10. Change the base color, add a sticker, and add text.
11. Save the design draft.
12. Export the package.
13. Download the ZIP.

## Expected Backend Outputs

```text
backend/storage/raw-scans/{scan_session_id}/raw_video.mp4
backend/storage/raw-scans/{scan_session_id}/metadata.json
backend/storage/frames/{scan_session_id}/frame_0001.jpg
backend/storage/models/{scan_session_id}/shoe_base.glb
backend/storage/models/{scan_session_id}/shoe_base.obj
backend/storage/models/{scan_session_id}/shoe_base.mtl
backend/storage/models/{scan_session_id}/base_texture.png
backend/storage/models/{scan_session_id}/quality_report.json
backend/storage/designs/{design_id}/design_config.json
backend/storage/exports/{export_id}/{export_id}.zip
```

## Expected ZIP Contents

```text
final_shoe.glb
final_shoe.obj
final_shoe.mtl
final_texture.png
preview_front.png
preview_side.png
preview_top.png
preview_back.png
design_config.json
measurement_info.json
production_notes.json
```

## Troubleshooting

- If the frontend cannot load data, make sure the backend is running on `127.0.0.1:8000`.
- If Flutter runs on Android emulator, use `10.0.2.2:8000` instead of `127.0.0.1:8000`.
- If processing completes with only one frame, FFmpeg likely failed or is unavailable. Mock mode still creates usable MVP assets.
- If protected downloads fail in the browser, use the frontend download buttons. They fetch files with the demo bearer token.
- If `npm` resolves to a broken user-level install, run npm through `node "C:\Program Files\nodejs\node_modules\npm\bin\npm-cli.js"`.
