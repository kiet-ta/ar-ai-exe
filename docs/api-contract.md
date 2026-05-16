# API Contract

Base URL for local development:

```text
http://127.0.0.1:8000
```

## Auth

### POST /api/auth/demo-login

Returns a local demo bearer token and creates the demo user if needed.

Request:

```http
POST /api/auth/demo-login
```

Response:

```json
{
  "accessToken": "local-demo-token-change-me",
  "tokenType": "bearer",
  "user": {
    "id": "user_abc",
    "role": "demo_user",
    "name": "Demo User",
    "email": "demo@shoe-customizer.local",
    "createdAt": "2026-05-17T01:00:00"
  }
}
```

### GET /api/auth/me

Request:

```http
GET /api/auth/me
Authorization: Bearer local-demo-token-change-me
```

Response:

```json
{
  "id": "user_abc",
  "role": "demo_user",
  "name": "Demo User",
  "email": "demo@shoe-customizer.local",
  "createdAt": "2026-05-17T01:00:00"
}
```

## System

### GET /health

Checks that the API process is running.

Response:

```json
{
  "status": "ok",
  "service": "Shoe Visual Customizer API",
  "environment": "local"
}
```

## Scan Sessions

All scan endpoints require:

```http
Authorization: Bearer local-demo-token-change-me
```

### POST /api/scan-sessions

Creates an empty scan session.

Request:

```json
{}
```

Response:

```json
{
  "id": "scan_abc",
  "userId": "user_abc",
  "status": "created",
  "errorMessage": null,
  "modelAssetId": null,
  "createdAt": "2026-05-17T01:00:00",
  "updatedAt": "2026-05-17T01:00:00"
}
```

### POST /api/scan-sessions/{scan_session_id}/upload-video

Uploads MP4 video and scan metadata. Processing starts automatically after upload.

Request:

```http
POST /api/scan-sessions/scan_abc/upload-video
Content-Type: multipart/form-data
```

Form fields:

```text
video: raw_video.mp4
metadata: JSON string
```

Metadata example:

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

Response:

```json
{
  "scanSession": {
    "id": "scan_abc",
    "userId": "user_abc",
    "status": "uploaded",
    "errorMessage": null,
    "modelAssetId": null,
    "createdAt": "2026-05-17T01:00:00",
    "updatedAt": "2026-05-17T01:00:10"
  },
  "processingStarted": true
}
```

### GET /api/scan-sessions/{scan_session_id}

Returns the scan session and model asset ID when processing is complete.

### GET /api/scan-sessions/{scan_session_id}/status

Response:

```json
{
  "id": "scan_abc",
  "status": "completed",
  "errorMessage": null,
  "modelAssetId": "model_abc",
  "updatedAt": "2026-05-17T01:00:20"
}
```

### POST /api/scan-sessions/{scan_session_id}/process

Manually starts processing. Upload already starts processing automatically, so this is mainly a recovery/debug endpoint.

Security note: scan responses intentionally do not expose raw server filesystem paths. Model and export downloads are served through authenticated API endpoints.

## Model Assets

### GET /api/models/{model_asset_id}

Response:

```json
{
  "id": "model_abc",
  "scanSessionId": "scan_abc",
  "glbUrl": "/api/models/model_abc/download/glb",
  "objUrl": "/api/models/model_abc/download/obj",
  "mtlUrl": "/api/models/model_abc/download/mtl",
  "textureUrl": "/api/models/model_abc/download/texture",
  "qualityReportUrl": "/api/models/model_abc/quality-report",
  "qualityReport": {
    "overallScore": 75,
    "frameCount": 1,
    "lighting": "unknown",
    "blur": "unknown",
    "coverage": "unknown",
    "scaleConfidence": "medium",
    "recommendation": "Usable for visual design package."
  },
  "createdAt": "2026-05-17T01:00:20"
}
```

### GET /api/models/{model_asset_id}/download/glb

Downloads `shoe_base.glb`.

### GET /api/models/{model_asset_id}/download/obj

Downloads `shoe_base.obj`.

### GET /api/models/{model_asset_id}/download/mtl

Downloads `shoe_base.mtl`.

### GET /api/models/{model_asset_id}/download/texture

Downloads `base_texture.png`.

### GET /api/models/{model_asset_id}/quality-report

Returns the generated quality report JSON.

## Designs

### POST /api/designs

Request:

```json
{
  "modelAssetId": "model_abc",
  "name": "Demo red text shoe",
  "config": {
    "modelAssetId": "model_abc",
    "baseColor": "#ffffff",
    "material": {
      "roughness": 0.5,
      "metallic": 0.0
    },
    "stickers": [
      {
        "id": "sticker_001",
        "type": "image",
        "imageUrl": "/assets/stickers/flame.png",
        "position": [0.2, 0.5, 0.1],
        "rotation": [0, 0.5, 0],
        "scale": 0.25
      }
    ],
    "texts": [
      {
        "id": "text_001",
        "value": "TAK",
        "font": "Arial",
        "color": "#111111",
        "position": [0.1, 0.4, 0.2],
        "rotation": [0, 0.3, 0],
        "scale": 0.2
      }
    ]
  }
}
```

Response:

```json
{
  "id": "design_abc",
  "userId": "user_abc",
  "modelAssetId": "model_abc",
  "name": "Demo red text shoe",
  "status": "draft",
  "designConfig": {
    "modelAssetId": "model_abc",
    "baseColor": "#ffffff",
    "material": {
      "roughness": 0.5,
      "metallic": 0.0
    },
    "stickers": [],
    "texts": []
  },
  "createdAt": "2026-05-17T01:00:30",
  "updatedAt": "2026-05-17T01:00:30"
}
```

### GET /api/designs/{design_id}

Returns a saved design draft.

### PUT /api/designs/{design_id}

Updates the design name and/or `designConfig`.

### POST /api/designs/{design_id}/export

Creates the visual design package ZIP.

Response:

```json
{
  "id": "export_abc",
  "designId": "design_abc",
  "status": "completed",
  "downloadUrl": "/api/exports/export_abc/download",
  "files": [
    "final_shoe.glb",
    "final_shoe.obj",
    "final_shoe.mtl",
    "final_texture.png",
    "preview_front.png",
    "preview_side.png",
    "preview_top.png",
    "preview_back.png",
    "design_config.json",
    "measurement_info.json",
    "production_notes.json"
  ],
  "createdAt": "2026-05-17T01:00:40"
}
```

## Exports

### GET /api/exports/{export_id}

Returns export package metadata.

### GET /api/exports/{export_id}/download

Downloads the ZIP package.
