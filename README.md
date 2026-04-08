# First Aid AI Chatbot

A retrieval-first first-aid assistant built for a final-year project demo. The system uses approved medical content to answer common first-aid questions, show supporting citations, and surface emergency escalation guidance when a situation appears urgent.

## Live Demo

- Public app: `https://first-aid-ai-chatbot.onrender.com`
- Health check: `https://first-aid-ai-chatbot.onrender.com/health`

## Project Summary

The project combines a `React + TypeScript` frontend with a `FastAPI + Python` backend. Instead of answering from open-ended model memory, the chatbot retrieves from approved first-aid source material and formats a grounded response with citations.

This makes the system better suited to a safety-focused academic demo because it is designed to:

- answer only from approved medical content
- prefer trusted organizations such as `IFRC` and `WHO`
- show citations alongside first-aid guidance
- refuse unsupported topics instead of guessing
- highlight emergencies using Ghana-specific emergency contact guidance

## Key Features

- public chat interface for first-aid questions
- grounded answers with source citations
- emergency banner for urgent cases
- admin page for managing approved source content
- ingestion pipeline for canonical files in [`data/sources`](/c:/Users/Ethel/Desktop/FirstAidChatbotProject/data/sources)
- automated tests for API, retrieval, and safety behavior
- hosted demo deployment on Render

## Technology Stack

- Frontend: `React`, `TypeScript`, `Vite`
- Backend: `FastAPI`, `SQLAlchemy`, `Pydantic`
- Retrieval: local `TF-IDF` ranking over approved document chunks
- Database: `SQLite`
- Deployment: `Render` for hosted demo, Docker support for packaging
- Optional LLM path: `OpenAI` integration is scaffolded but not required for the current no-cost demo flow

## System Architecture

High-level flow:

`User -> React frontend -> FastAPI backend -> safety checks -> approved-source retrieval -> grounded answer formatting -> cited response`

More detail is available in [`docs/architecture.md`](/c:/Users/Ethel/Desktop/FirstAidChatbotProject/docs/architecture.md).

## Repository Structure

- `frontend/`: chat UI and admin interface
- `backend/`: API routes, services, schemas, and database models
- `data/`: approved source content and local data assets
- `docs/`: architecture, limitations, safety, and deployment notes
- `infra/`: Docker and local deployment assets
- `deploy/`: hosted deployment Docker assets
- `scripts/`: helper scripts such as source ingestion

## Local Development Setup

### 1. Backend

```powershell
cd backend
python -m venv ..\.venv
..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `backend/.env` from [`backend/.env.example`](/c:/Users/Ethel/Desktop/FirstAidChatbotProject/backend/.env.example):

```env
ADMIN_API_KEY=your-admin-key
AUTO_INGEST_SOURCES=true
ALLOW_MOCK_RESPONSES=true
```

Start the backend:

```powershell
uvicorn app.main:app --reload
```

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

The frontend usually runs on `http://localhost:5173`. If that port is busy, Vite may move to another local port.

## Demo Routes

Once the frontend is running locally:

- chat page: `/`
- successful demo state: `/?demo=successful`
- emergency demo state: `/?demo=emergency`
- admin page: `/?page=admin`

## Source Ingestion

Approved source files live in [`data/sources`](/c:/Users/Ethel/Desktop/FirstAidChatbotProject/data/sources).

To ingest or refresh the local knowledge base:

```powershell
python scripts/ingest_sources.py
```

The hosted Render deployment is configured to auto-bootstrap the checked-in canonical sources on startup so the demo database is repopulated automatically when needed.

## Running Tests

Backend tests:

```powershell
python -m pytest backend/tests
```

Frontend production build:

```powershell
cd frontend
npm run build
```

## Deployment

### Recommended Hosted Deployment

The simplest public deployment path for this project is Render. The repository already includes:

- [`render.yaml`](/c:/Users/Ethel/Desktop/FirstAidChatbotProject/render.yaml)
- [`deploy/Dockerfile.render`](/c:/Users/Ethel/Desktop/FirstAidChatbotProject/deploy/Dockerfile.render)

Full hosted deployment instructions are in [`docs/deployment-render.md`](/c:/Users/Ethel/Desktop/FirstAidChatbotProject/docs/deployment-render.md).

### Local Docker Deployment

For a local containerized run, use:

- [`infra/docker-compose.yml`](/c:/Users/Ethel/Desktop/FirstAidChatbotProject/infra/docker-compose.yml)
- [`infra/compose.env.example`](/c:/Users/Ethel/Desktop/FirstAidChatbotProject/infra/compose.env.example)

```powershell
Copy-Item infra/compose.env.example infra/compose.env
# edit infra/compose.env and set ADMIN_API_KEY
docker compose --env-file infra/compose.env -f infra/docker-compose.yml up --build
```

This starts:

- API: `http://localhost:8000`
- Frontend: `http://localhost:8080`

## Environment Variables

Required:

- `ADMIN_API_KEY`

Common optional values:

- `AUTO_INGEST_SOURCES`
- `ALLOW_MOCK_RESPONSES`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_REASONING_EFFORT`
- `DATABASE_URL`
- `CORS_ORIGINS`

## Current Limitations

- retrieval currently uses `TF-IDF` rather than embedding-based semantic search
- admin access uses a shared key instead of account-based authentication
- SQLite is appropriate for demo use but not ideal for long-term hosted persistence
- free-tier hosting can introduce cold starts or ephemeral filesystem limits
- emergency detection is rule-based and should not be treated as a substitute for professional medical judgment

For a fuller discussion, see [`docs/limitations.md`](/c:/Users/Ethel/Desktop/FirstAidChatbotProject/docs/limitations.md).

## Future Improvements

- upgrade retrieval to semantic search with embeddings
- move from shared-key admin access to stronger authentication
- use PostgreSQL for more robust hosted persistence
- expand topic coverage and evaluation cases
- improve admin audit and monitoring features

## Submission Notes

This project is intended as a safety-aware academic prototype rather than a production medical device. Its main contribution is the combination of:

- approved-source retrieval
- citation-backed first-aid responses
- emergency escalation behavior
- a lightweight admin workflow for managing trusted source content

## Author

First Aid AI Chatbot project repository:
[`Slickdeveloper/first-aid-ai-chatbot`](https://github.com/Slickdeveloper/first-aid-ai-chatbot)
