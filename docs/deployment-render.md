# Render Deployment

This project is set up to deploy as a single Render web service so the frontend and backend share one public URL.

## Why This Deployment Shape

- one public URL for both the UI and API
- no separate frontend/backend hosting setup
- no production `localhost` API mistakes
- no CORS wiring needed for the deployed UI
- no manual source-ingestion step after every restart because the backend can auto-bootstrap from `data/sources/`

## Recommended Plan

- Fastest setup: Render `free` web service
- Safest for the actual presentation: switch the service to `starter` before demo day to avoid free-tier cold starts

## What Gets Deployed

- frontend: built from `frontend/` with Vite
- backend: FastAPI app from `backend/`
- data: canonical source files from `data/sources/`
- runtime database: SQLite database created at startup

## Required Environment Variables

- `ADMIN_API_KEY`: required, set this to a real secret value

## Optional Environment Variables

- `AUTO_INGEST_SOURCES=true`: keeps the demo database populated from checked-in sources on startup
- `ALLOW_MOCK_RESPONSES=true`: keeps the no-cost demo flow working without an OpenAI key
- `OPENAI_API_KEY`: only needed if you later disable mock responses
- `OPENAI_MODEL`: optional if using OpenAI-backed responses
- `OPENAI_REASONING_EFFORT`: optional if using OpenAI-backed responses

## Deploy Steps

1. Push the latest code to GitHub.
2. Sign in to Render and choose `New +` -> `Blueprint`.
3. Connect the repository and select this repo.
4. Render will detect [`render.yaml`](/c:/Users/Ethel/Desktop/FirstAidChatbotProject/render.yaml).
5. When prompted for secrets, enter a strong `ADMIN_API_KEY`.
6. Create the Blueprint and wait for the first deploy to finish.
7. Open the generated `onrender.com` URL.

## Public URLs After Deploy

- frontend: `https://<your-service>.onrender.com/`
- backend health check: `https://<your-service>.onrender.com/health`
- chat API: `https://<your-service>.onrender.com/chat`
- admin API: `https://<your-service>.onrender.com/admin/sources`

## Smoke Test Checklist

1. Open `/` and confirm the chat page loads.
2. Ask a simple question like `How do I help with a burn?` and confirm you get an answer with citations.
3. Open `/?page=admin`, sign in with `ADMIN_API_KEY`, and confirm the approved source list loads.
4. Open `/health` and confirm it returns `{"status":"ok"}`.

## Important Limitations

- On Render free plan, the filesystem is ephemeral and the service can sleep.
- Because this app uses SQLite for the demo, any admin-added sources created during runtime can be lost on redeploy or restart on the free plan.
- The checked-in canonical sources are restored automatically at startup, so the demo still comes up usable.
- For a smoother live presentation, switch to Render `starter`. If you want SQLite persistence there too, add a Render disk and point `DATABASE_URL` at a file on that disk.
