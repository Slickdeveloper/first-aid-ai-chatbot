# First Aid AI Chatbot

A retrieval-first first-aid chatbot built with `React + TypeScript` on the frontend and `FastAPI + Python` on the backend. The system answers only from approved medical content stored in the local knowledge base, with `IFRC` and `WHO` treated as primary sources and `American Red Cross` or `Mayo Clinic` used as supporting sources where needed.

## Project Status

This project is currently at a strong prototype stage:

- grounded chat flow is working end to end
- emergency prompts trigger a visible Ghana-specific warning path
- answers include citations
- admin/source management is available in the web UI
- approved source files are centralized in a single canonical source directory
- prompt coverage has been widened for common first-aid emergency phrasing

## Stack

- Frontend: `React`, `TypeScript`, `Vite`
- Backend: `FastAPI`, `SQLAlchemy`, `Pydantic`
- Retrieval: local `TF-IDF` ranking with approved document chunks
- Database: local `SQLite` for the current project flow
- Source ingestion: Python scripts over canonical approved source files
- Optional LLM path: OpenAI integration is scaffolded but not required for the current no-cost workflow

## Core Principles

- answer only from approved medical sources
- prefer `IFRC` and `WHO` whenever equivalent content exists
- show citations for medical guidance
- refuse unsupported answers instead of guessing
- detect emergencies and escalate clearly
- keep a clear separation between ingestion, retrieval, answer generation, and safety checks

## Main Features

- chat interface for first-aid questions
- source-backed assistant responses
- structured emergency alert flow using Ghana emergency numbers
- admin page for managing approved sources with simple shared-key sign-in
- ingestion pipeline for canonical `data/sources` documents
- organized backend tests for API, retrieval, and safety behavior

## Repository Layout

- `frontend/`: React UI for chat and admin tools
- `backend/`: FastAPI app, retrieval pipeline, schemas, models, and services
- `data/`: approved source material and local data assets
- `docs/`: architecture, safety, and source-governance documentation
- `infra/`: deployment and Docker configuration
- `scripts/`: ingestion, sync, and setup helpers

## Local Run

### Backend

```powershell
cd backend
python -m venv ..\.venv
..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

If your virtual environment is already created in the project root, just activate it and run the install/start commands.

Create `backend/.env` from `backend/.env.example` and set an admin key before using the admin page:

```env
ADMIN_API_KEY=your-admin-key
```

### Frontend

```powershell
cd frontend
$env:Path += ";C:\Program Files\nodejs"
& "C:\Program Files\nodejs\npm.cmd" install
& "C:\Program Files\nodejs\npm.cmd" run dev
```

Vite may choose a different port if `5173` is already in use. Use the `Local:` URL printed in the terminal.

## Demo URLs

Once the frontend is running:

- chat page: `/`
- successful demo state: `/?demo=successful`
- emergency demo state: `/?demo=emergency`
- admin page: `/?page=admin`

## Source Ingestion Workflow

1. Place approved `.md` or `.txt` files in [`data/sources`](/c:/Users/Ethel/Desktop/FirstAidChatbotProject/data/sources)
2. Ingest source files into the database:

```powershell
python scripts/ingest_sources.py
```

## Deployment

Docker-based deployment files are included in [`infra/docker-compose.yml`](/c:/Users/Ethel/Desktop/FirstAidChatbotProject/infra/docker-compose.yml), [`backend/Dockerfile`](/c:/Users/Ethel/Desktop/FirstAidChatbotProject/backend/Dockerfile), and [`frontend/Dockerfile`](/c:/Users/Ethel/Desktop/FirstAidChatbotProject/frontend/Dockerfile).

For Docker-based deployment, copy [`infra/compose.env.example`](/c:/Users/Ethel/Desktop/FirstAidChatbotProject/infra/compose.env.example) to `infra/compose.env` and replace `ADMIN_API_KEY` with a real value.

If Docker is installed locally:

```powershell
docker compose --env-file infra/compose.env -f infra/docker-compose.yml up --build
```

This starts:

- API: `http://localhost:8000`
- Frontend: `http://localhost:8080`

The Compose stack now includes basic health checks and restart policies for both containers.

## Current Limitations

- retrieval is still TF-IDF based rather than embedding-based semantic search
- some edge-case phrasings still require additional synonym tuning
- admin authentication is intentionally lightweight and currently uses a shared key rather than full user accounts
- the active no-cost path does not rely on a production LLM
- the `OPENAI_API_KEY`, `OPENAI_MODEL`, and `OPENAI_REASONING_EFFORT` settings are optional placeholders unless a real API key is added and mock responses are disabled
- the chatbot depends on the approved source files having been ingested into the database; if ingestion has not been run, the admin page and retrieval layer will appear empty
- SQLite is fine for prototype/demo use but PostgreSQL would be stronger for production

For a fuller project-risk and limitation list, see [`docs/limitations.md`](/c:/Users/Ethel/Desktop/FirstAidChatbotProject/docs/limitations.md).

## Recommended Next Steps

- replace shared-key admin authentication with stronger user/session-based auth
- expand IFRC/WHO topic-specific coverage further
- improve deployment story for hosted demo
- update report materials and screenshots
