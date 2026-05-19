# Shoe Visual Customizer Mobile

Flutter scanner MVP.

## Responsibilities

- Record two guided shoe scan videos:
  - side orbit, 360 degrees around the shoe.
  - top-angle orbit, 30-45 degrees from above.
- Collect required scan metadata.
- Upload both videos and metadata to the FastAPI backend.
- Check backend reconstruction readiness before uploading, so missing COLMAP/OpenMVS/Blender or low resources are reported early.

The mobile app does not perform real-time 3D reconstruction and does not scan the bottom sole in the MVP.

## Run

Flutter is required locally.

```powershell
flutter pub get
flutter run --dart-define=BACKEND_BASE_URL=http://127.0.0.1:8000
```

For Android emulator, use the host bridge URL:

```powershell
flutter run --dart-define=BACKEND_BASE_URL=http://10.0.2.2:8000
```

## Physical Android device

For local LAN testing, do not use `127.0.0.1`. Use your laptop LAN IP:

```powershell
flutter run --dart-define=BACKEND_BASE_URL=http://192.168.1.20:8000
```

For VPS/production:

```powershell
flutter build apk --release --dart-define=BACKEND_BASE_URL=https://your-domain.example.com
```

The backend must set `WEB_APP_BASE_URL` to the same public web origin so the app can open `/design?scanId=...` after upload.

Full deployment guide: `docs/vps-android-deployment.md`.
