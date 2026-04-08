# Backend

FastAPI backend for the First Aid AI Chatbot.

This part of the project is responsible for turning a user question into a grounded response.

## Responsibilities

- serve the `/chat` API
- manage protected `/admin/sources` routes
- run emergency detection and refusal logic
- retrieve approved source chunks from the database
- format grounded responses with citations

## Important Areas

- `app/main.py`: app startup, CORS, router registration
- `app/api/routes/`: chat and admin routes
- `app/services/`: retrieval, safety, answer formatting, ingestion
- `app/db/models/`: source, chunk, chat log, and audit models
- `tests/`: API, retrieval, and safety tests

If you are trying to understand the backend quickly, start with:

1. `app/api/routes/chat.py`
2. `app/services/chat_service.py`
3. `app/services/retrieval_service.py`
4. `app/services/llm_service.py`
5. `app/services/safety_service.py`

## Local Start

```powershell
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Admin Access

Set `ADMIN_API_KEY` in `backend/.env` to protect the admin routes. The frontend admin page sends this key through the `X-Admin-Key` header after sign-in.

## Current Limitations

- the backend currently uses a shared admin key rather than full account-based authentication
- SQLite is used for simplicity in local/demo mode
- the OpenAI settings in `backend/.env` are optional and inactive unless `OPENAI_API_KEY` is set and mock responses are turned off
- retrieval depends on source files having been ingested into the database first
