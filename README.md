# First Aid AI Chatbot

A retrieval-first first-aid assistant built for a final-year project demo. The system uses approved medical content to answer common first-aid questions, show supporting citations, and surface emergency escalation guidance when a situation appears urgent.

---

## 🌐 Live Demo

* Public app: https://first-aid-ai-chatbot.onrender.com
* Health check: https://first-aid-ai-chatbot.onrender.com/health

---

## 📘 Project Summary

The project combines a **React + TypeScript** frontend with a **FastAPI + Python** backend. Instead of answering from open-ended model memory, the chatbot retrieves from approved first-aid source material and formats a grounded response with citations.

This makes the system better suited to a safety-focused academic demo because it is designed to:

* answer only from approved medical content
* prefer trusted organizations such as **IFRC** and **WHO**
* show citations alongside first-aid guidance
* refuse unsupported topics instead of guessing
* highlight emergencies using Ghana-specific emergency contact guidance

---

## ✨ Key Features

* Public chat interface for first-aid questions
* Grounded answers with source citations
* Emergency banner for urgent cases
* Admin page for managing approved source content
* Ingestion pipeline for canonical files in [data/sources](data/sources)
* Automated tests for API, retrieval, and safety behavior
* Hosted demo deployment on Render

---

## 🛠️ Technology Stack

* **Frontend:** React, TypeScript, Vite
* **Backend:** FastAPI, SQLAlchemy, Pydantic
* **Retrieval:** TF-IDF ranking over approved document chunks
* **Database:** SQLite
* **Deployment:** Render (hosted demo), Docker (packaging)
* **Optional LLM:** OpenAI (not required for demo)

---

## 🧠 System Architecture

High-level flow:

```
User → React frontend → FastAPI backend → Safety checks → Retrieval → Answer formatting → Response with citations
```

More detail is available in the [Architecture Documentation](docs/architecture.md).

---

## 📁 Repository Structure

* `frontend/` – Chat UI and admin interface
* `backend/` – API routes, services, schemas, and database models
* `data/` – Approved source content and local data assets
* `docs/` – Architecture, limitations, safety, and deployment notes
* `infra/` – Docker and local deployment assets
* `deploy/` – Hosted deployment Docker assets
* `scripts/` – Helper scripts (e.g., ingestion)

---

## ⚙️ Local Development Setup

### 1. Backend

```powershell
cd backend
python -m venv ..\.venv
..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `.env` from [backend/.env.example](backend/.env.example):

```env
ADMIN_API_KEY=your-admin-key
AUTO_INGEST_SOURCES=true
ALLOW_MOCK_RESPONSES=true
```

Start the backend:

```powershell
uvicorn app.main:app --reload
```

---

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173` (or another port if occupied).

---

## 🎯 Demo Routes

* Chat: `/`
* Successful demo: `/?demo=successful`
* Emergency demo: `/?demo=emergency`
* Admin page: `/?page=admin`

---

## 📦 Source Ingestion

Approved source files live in [data/sources](data/sources).

To ingest or refresh the knowledge base:

```powershell
python scripts/ingest_sources.py
```

The Render deployment auto-loads these sources on startup.

---

## 🧪 Running Tests

Backend tests:

```powershell
python -m pytest backend/tests
```

Frontend production build:

```powershell
cd frontend
npm run build
```

---

## 🚀 Deployment

### Recommended (Render)

This repo includes:

* [render.yaml](render.yaml)
* [Dockerfile for Render](deploy/Dockerfile.render)

Full instructions:
👉 [Render Deployment Guide](docs/deployment-render.md)

---

### Local Docker Deployment

Files used:

* [docker-compose.yml](infra/docker-compose.yml)
* [compose.env.example](infra/compose.env.example)

```powershell
Copy-Item infra/compose.env.example infra/compose.env
# edit and set ADMIN_API_KEY
docker compose --env-file infra/compose.env -f infra/docker-compose.yml up --build
```

Services:

* API → http://localhost:8000
* Frontend → http://localhost:8080

---

## 🔐 Environment Variables

### Required

* `ADMIN_API_KEY`

### Optional

* `AUTO_INGEST_SOURCES`
* `ALLOW_MOCK_RESPONSES`
* `OPENAI_API_KEY`
* `OPENAI_MODEL`
* `OPENAI_REASONING_EFFORT`
* `DATABASE_URL`
* `CORS_ORIGINS`

---

## ⚠️ Current Limitations

* Uses TF-IDF instead of semantic search
* Admin uses shared key (no user accounts)
* SQLite is not production-grade
* Free hosting may cause cold starts
* Emergency detection is rule-based

More details:
👉 [Limitations Documentation](docs/limitations.md)

---

## 🔮 Future Improvements

* Upgrade to embedding-based semantic search
* Implement role-based authentication
* Use PostgreSQL for persistence
* Expand medical coverage and evaluation
* Improve admin monitoring and audit tools

---

## 📌 Submission Notes

This project is a **safety-aware academic prototype**, not a production medical system.

Core contributions:

* Retrieval-based answering from approved sources
* Citation-backed responses
* Emergency detection and escalation
* Admin-controlled knowledge base

---

## 👨‍💻 Author

GitHub Repository:
👉 https://github.com/Slickdeveloper/first-aid-ai-chatbot

