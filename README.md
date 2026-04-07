# First Aid AI Chatbot

This project is structured as a retrieval-first first-aid chatbot that answers only from approved medical sources such as WHO and Red Cross materials.

## High-Level Architecture

- `frontend/`: React + TypeScript chat interface
- `backend/`: FastAPI application, retrieval pipeline, guardrails, and APIs
- `data/`: approved source documents, processed chunks, and local development storage
- `docs/`: architecture, safety, and academic documentation
- `infra/`: Docker and deployment configuration
- `scripts/`: setup and ingestion helper scripts

## Core Principles

- Only answer from authorized sources
- Attach citations to medical guidance
- Detect emergencies and escalate to local emergency services
- Keep audit logs for transparency
- Separate ingestion, retrieval, generation, and safety logic

## Quick Start

### Backend

1. Create a virtual environment
2. Install dependencies from `backend/requirements.txt`
3. Start the API from `backend/`

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

1. Install dependencies in `frontend/`
2. Copy `.env.example` to `.env`
3. Start the Vite development server

```powershell
npm install
npm run dev
```

## Current Starter Features

- FastAPI health endpoint and chat endpoint
- Emergency keyword detection
- Placeholder grounded response contract with citations
- Admin endpoint for approved source records
- React chat interface with sources and emergency banner
- Data folders for raw documents, processed chunks, and vector storage
