# Current Neon System Flow

Mermaid diagrams in this document target Mermaid `v11.14.0`.

## Context

Repository hien tai da chuyen backend tu SQLite-only sang SQLAlchemy co Neon Postgres cloud database. Backend van dung local storage cho raw scan, generated model, design config va export ZIP. Neon Postgres chi luu metadata, ownership, status va duong dan artifact.

## End-to-end Product Flow

```mermaid
flowchart TD
    A["Flutter Mobile Scanner"] --> B["Record guided shoe video"]
    B --> C["Collect shoe metadata"]
    C --> D["POST /api/auth/demo-login"]
    D --> E["POST /api/scan-sessions"]
    E --> F["Insert scan session into Neon Postgres"]
    F --> G["POST /api/scan-sessions/{id}/upload-video"]
    G --> H["Store raw MP4 and metadata JSON in backend storage"]
    H --> I["Update scan status in Neon Postgres"]
    I --> J["Background reconstruction worker"]
    J --> K["Extract frames"]
    K --> L["Generate or process GLB, OBJ, MTL, texture"]
    L --> M["Insert model asset metadata into Neon Postgres"]
    M --> N["Vite React Web Editor"]
    N --> O["GET scan session and model metadata"]
    O --> P["Download authenticated GLB or OBJ asset"]
    P --> Q["Edit color, material, sticker, text"]
    Q --> R["POST or PUT /api/designs"]
    R --> S["Store design config JSON in backend storage"]
    S --> T["Insert design metadata into Neon Postgres"]
    T --> U["POST /api/designs/{id}/export"]
    U --> V["Create export package ZIP"]
    V --> W["Insert export package metadata into Neon Postgres"]
    W --> X["GET /api/exports/{id}/download"]
```

## Runtime Architecture

```mermaid
flowchart LR
    A["Mobile App"] -->|"Bearer token + multipart upload"| B["FastAPI Backend"]
    C["Web Editor"] -->|"Bearer token + JSON/file requests"| B
    B -->|"SQLAlchemy + psycopg"| D["Neon Postgres pooled endpoint"]
    B -->|"Read/write files"| E["Backend storage"]
    B -->|"BackgroundTasks now; external queue later"| F["Reconstruction worker"]
    F -->|"Artifact metadata updates"| D
    F -->|"GLB OBJ MTL PNG ZIP"| E
```

## Database Runtime Flow

```mermaid
flowchart TD
    A["FastAPI process starts"] --> B["Load backend/.env"]
    B --> C["Resolve DATABASE_URL"]
    C --> D{"DATABASE_URL starts with postgres or postgresql"}
    D -->|"Yes"| E["Normalize to postgresql+psycopg"]
    D -->|"No"| F["Keep SQLite URL for local fallback"]
    E --> G["Create SQLAlchemy engine"]
    F --> G
    G --> H["Enable pool_pre_ping"]
    H --> I{"Postgres runtime"}
    I -->|"Yes"| J["Set pool_recycle=300"]
    I -->|"No"| K["Set SQLite check_same_thread=false"]
    J --> L["API reads/writes Neon Postgres"]
    K --> M["API reads/writes local SQLite"]
```

## Migration Flow

```mermaid
flowchart TD
    A["Developer changes SQLAlchemy models"] --> B["Create Alembic revision"]
    B --> C["Review generated schema diff"]
    C --> D["Run migration against Neon branch"]
    D --> E["Validate tables, indexes, and alembic_version"]
    E --> F["Deploy backend with DATABASE_AUTO_CREATE_TABLES=false"]
    F --> G["Runtime uses existing schema only"]
```

## Scan Status Flow

```mermaid
stateDiagram-v2
    [*] --> created
    created --> uploaded: raw video and metadata saved
    uploaded --> extracting_frames: worker starts
    extracting_frames --> reconstructing
    reconstructing --> cleaning_mesh
    cleaning_mesh --> uv_unwrapping
    uv_unwrapping --> texture_baking
    texture_baking --> exporting
    exporting --> completed
    extracting_frames --> failed
    reconstructing --> failed
    cleaning_mesh --> failed
    uv_unwrapping --> failed
    texture_baking --> failed
    exporting --> failed
    completed --> [*]
    failed --> [*]
```

## Security Boundary

```mermaid
flowchart TD
    A["User device"] --> B["Bearer token"]
    B --> C["FastAPI auth dependency"]
    C --> D{"Authorized user owns resource"}
    D -->|"Yes"| E["Read or mutate metadata in Neon Postgres"]
    D -->|"No"| F["Reject request"]
    E --> G["Serve artifact through authenticated API endpoint"]
    G --> H["Do not expose raw server filesystem paths"]
    I["Secrets"] --> J["backend/.env or deployment secret manager"]
    J --> K["Ignored by git"]
    L["Examples"] --> M[".env.example without real credentials"]
```

## Current Data Ownership

```mermaid
erDiagram
    users ||--o{ scan_sessions : owns
    users ||--o{ designs : owns
    scan_sessions ||--o| model_assets : produces
    model_assets ||--o{ designs : customizes
    designs ||--o{ export_packages : exports

    users {
        string id PK
        string role
        string name
        string email
        datetime created_at
    }

    scan_sessions {
        string id PK
        string user_id FK
        string status
        text raw_video_path
        text metadata_path
        text error_message
        datetime created_at
        datetime updated_at
    }

    model_assets {
        string id PK
        string scan_session_id FK
        text glb_path
        text obj_path
        text mtl_path
        text texture_path
        text quality_report_path
        datetime created_at
    }

    designs {
        string id PK
        string user_id FK
        string model_asset_id FK
        string name
        text design_config_path
        string status
        datetime created_at
        datetime updated_at
    }

    export_packages {
        string id PK
        string design_id FK
        string status
        text zip_path
        datetime created_at
    }
```

## Trade-off After Neon Migration

| Decision | Scalable | Maintainable | Security | Performance | User experience |
|---|---|---|---|---|---|
| Neon Postgres for metadata | Supports multi-instance API and concurrent users better than SQLite | Keeps SQLAlchemy model layer stable | Requires strict secret handling and branch protection | Good for status/design/export queries | Reliable cross-device state |
| Local storage for 3D artifacts | Limited when multiple API instances are deployed | Simple for MVP, but will need storage adapter | Files must never be exposed by raw path | Fast on one server, weak for distributed serving | Good enough for demo, weaker for large downloads |
| Alembic for schema | Enables staged schema evolution | Clear revision history | Reduces accidental runtime schema drift | Migration cost is controlled and explicit | Fewer deployment surprises |
| Pooled Neon connection for API | Handles high connection churn | One connection string for runtime | Secrets stay server-side | Good for normal request/response traffic | More stable under concurrent web/mobile use |

## Next Production Flow Target

```mermaid
flowchart TD
    A["Mobile/Web"] --> B["FastAPI API"]
    B --> C["Neon Postgres metadata"]
    B --> D["Object storage for raw scans and artifacts"]
    B --> E["Queue"]
    E --> F["Dedicated reconstruction worker"]
    F --> C
    F --> D
    D --> G["Signed download URL or authenticated stream"]
    C --> H["Status polling, SSE, or WebSocket updates"]
```
