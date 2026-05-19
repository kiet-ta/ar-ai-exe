# Implementation Flows

Mermaid diagrams in this document target Mermaid `v11.14.0`.

## Current Phase 0 Repository Flow

```mermaid
flowchart TD
    A["Workspace root"] --> B["backend"]
    A --> C["mobile"]
    A --> D["frontend"]
    A --> E["docs"]

    B --> F["app"]
    B --> G["storage"]
    B --> H["pyproject.toml"]
    B --> I["uv.lock"]

    F --> J["api"]
    F --> K["core"]
    F --> L["db"]
    F --> M["models"]
    F --> N["schemas"]
    F --> O["services"]
    F --> P["workers"]
    F --> Q["main.py"]

    G --> R["raw-scans"]
    G --> S["frames"]
    G --> T["models"]
    G --> U["designs"]
    G --> V["exports"]
```

## Current Backend Startup Flow

```mermaid
flowchart TD
    A["Start uvicorn app.main:app"] --> B["Load Settings"]
    B --> C["Resolve backend root"]
    C --> D["Resolve storage root"]
    C --> E["Resolve database URL"]
    D --> F["FastAPI lifespan starts"]
    F --> G["Create storage directories"]
    G --> H["API ready"]
    H --> I["GET /health"]
    I --> J["Return status ok"]
```

## Current Local Development Flow

```mermaid
flowchart LR
    A["Developer"] --> B["Install or bootstrap uv"]
    B --> C["Run uv sync in backend"]
    C --> D["Create local .venv"]
    C --> E["Create uv.lock"]
    D --> F["Run uvicorn"]
    F --> G["Call /health"]
    G --> H["Confirm backend is alive"]
```

## Current Health Request Sequence

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant API as FastAPI App
    participant Settings as Settings
    participant Storage as Local Storage

    Dev->>API: GET /health
    API->>Settings: Read app name and environment
    API-->>Dev: 200 status ok
    Note over API,Storage: Storage folders are initialized during app startup.
```

## Target MVP Product Flow

This is the full project flow the repository is being prepared for. Only Phase 0 is implemented now.

```mermaid
flowchart TD
    A["Flutter Mobile Scanner"] --> B["Record side orbit video"]
    B --> C["Record top-angle orbit video"]
    C --> D["Upload videos and metadata"]
    D --> E["FastAPI scan session API"]
    E --> F["Store raw scan files"]
    F --> G["Neon Postgres scan status tracking"]
    G --> H["Async processing job"]
    H --> I["Extract frames with FFmpeg"]
    I --> J["COLMAP and OpenMVS reconstruction"]
    J --> K["Mesh cleanup"]
    K --> L["UV unwrap"]
    L --> M["Texture bake"]
    M --> N["Export GLB and OBJ assets"]
    N --> O["Vite React web editor"]
    O --> P["Load scanned GLB"]
    P --> Q["Apply color stickers and text"]
    Q --> R["Save design_config.json separately"]
    R --> S["Generate visual design package"]
    S --> T["ZIP with GLB OBJ MTL texture previews notes"]
```

## Implemented Backend MVP Flow

```mermaid
flowchart TD
    A["POST /api/auth/demo-login"] --> B["Return bearer token"]
    B --> C["POST /api/scan-sessions"]
    C --> D["Create ScanSession with shoe metadata"]
    D --> E["POST /api/scan-sessions/{id}/videos/side-orbit"]
    E --> F["POST /api/scan-sessions/{id}/videos/top-orbit"]
    F --> G["POST /api/scan-sessions/{id}/process"]
    G --> H["Extract and filter frames"]
    H --> I["Run COLMAP OpenMVS Blender"]
    I --> J["Generate GLB OBJ MTL texture metadata quality ZIP"]
    J --> K["Create ModelAsset"]
    K --> L["GET /api/models/{id}"]
    L --> M["POST /api/designs"]
    M --> N["Store design_config.json separately"]
    N --> O["POST /api/designs/{id}/export"]
    O --> P["Copy final files and production notes"]
    P --> Q["Create downloadable ZIP"]
```

## Implemented Scan Status Flow

```mermaid
stateDiagram-v2
    [*] --> created
    created --> waiting_for_uploads: first video pass saved
    waiting_for_uploads --> uploaded: both video passes saved
    uploaded --> extracting_frames: process endpoint starts worker
    extracting_frames --> filtering_frames
    filtering_frames --> preparing_reconstruction
    preparing_reconstruction --> reconstructing
    reconstructing --> cleaning_mesh
    cleaning_mesh --> exporting
    exporting --> completed
    extracting_frames --> failed
    reconstructing --> failed
    cleaning_mesh --> failed
    exporting --> failed
    completed --> [*]
    failed --> [*]
```

## Implemented Export Package Flow

```mermaid
flowchart TD
    A["Saved Design"] --> B["Load ModelAsset"]
    B --> C["Create export folder"]
    C --> D["Copy final_shoe.glb"]
    C --> E["Copy final_shoe.obj"]
    C --> F["Copy final_shoe.mtl"]
    C --> G["Copy final_texture.png"]
    A --> H["Copy design_config.json"]
    B --> I["Read scan metadata"]
    I --> J["Write measurement_info.json"]
    A --> K["Write production_notes.json"]
    C --> L["Write preview images"]
    D --> M["Zip package"]
    E --> M
    F --> M
    G --> M
    H --> M
    J --> M
    K --> M
    L --> M
```

## Implemented Frontend Editor Flow

```mermaid
flowchart TD
    A["Open Vite React app"] --> B["POST /api/auth/demo-login"]
    B --> C["Paste scan session ID"]
    C --> D["GET /api/scan-sessions/{id}"]
    D --> E{"Has modelAssetId"}
    E -->|"No"| F["Show scan status"]
    E -->|"Yes"| G["GET /api/models/{model_id}"]
    G --> H["Fetch protected GLB as blob URL"]
    H --> I["Render GLB in React Three Fiber Canvas"]
    I --> J["Edit base color"]
    I --> K["Add sticker layer"]
    I --> L["Add text layer"]
    J --> M["Save design_config.json"]
    K --> M
    L --> M
    M --> N["POST or PUT /api/designs"]
    N --> O["POST /api/designs/{id}/export"]
    O --> P["Download ZIP with bearer token"]
```

## Implemented Flutter Scanner Source Flow

```mermaid
flowchart TD
    A["ScanSetupScreen"] --> B["Validate shoe metadata"]
    B --> C["CameraScanScreen"]
    C --> D["Camera preview with guide overlay"]
    D --> E["Start recording"]
    E --> F["Stop recording"]
    F --> G["UploadProgressScreen"]
    G --> H["CameraScanScreen top-angle pass"]
    H --> I["Record second MP4"]
    I --> J["UploadProgressScreen"]
    J --> K["POST /api/scan-sessions"]
    K --> L["Upload side-orbit and top-orbit"]
    L --> M["POST /process"]
    M --> N["ScanResultScreen"]
```

## Planned Auth And Demo Login Flow

```mermaid
flowchart TD
    A["User opens app"] --> B{"Has account session"}
    B -->|"Yes"| C["Use authenticated user"]
    B -->|"No"| D["Show login screen"]
    D --> E["Login or register"]
    D --> F["Skip login for demo"]
    F --> G["Use fixed demo user"]
    E --> H["Issue authorized API session"]
    G --> H
    H --> I["Access scan design and export APIs"]
```

## Phased Implementation Roadmap

```mermaid
flowchart TD
    P0["Phase 0 Repository and FastAPI foundation"] --> P1["Phase 1 Backend scan session API"]
    P1 --> P2["Phase 2 Flutter mobile scanner"]
    P1 --> P3["Phase 3 Frame extraction and real reconstruction"]
    P3 --> P4["Phase 4 COLMAP and OpenMVS hooks"]
    P3 --> P5["Phase 5 Vite React 3D viewer"]
    P5 --> P6["Phase 6 Web decoration editor"]
    P6 --> P7["Phase 7 Visual design package export"]
    P7 --> P8["Phase 8 End to end demo script"]
```
