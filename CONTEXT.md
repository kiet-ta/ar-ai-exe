# ar-ai-exe Domain Context

This repository contains the architecture for the `ar-ai-exe` application, organized into distinct subsystems.

## Architecture Boundaries

- **`backend/`**: Python-based API server using FastAPI and SQLAlchemy (managed with Alembic).
- **`frontend/`**: Web application using React, Vite, and TypeScript.
- **`mobile/`**: Mobile application (ensure boundaries are isolated from frontend/web logic).
- **`docs/`**: Project documentation, including ADRs and agent domain contexts.

## AI Agent Guidelines

1. **Rule Skills**: All agents should follow the rules defined in `.agents/skills/tech-stack-rules` to adhere to coding conventions and SDLC.
2. **Project Navigation**: Do not guess file structures. Read the `backend`, `frontend`, and `mobile` directories explicitly using the `project-structure` skill when searching for implementations.
3. **Database**: Backend uses `alembic` for migrations. Keep database schemas in sync with Python models.
