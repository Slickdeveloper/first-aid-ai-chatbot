# Infrastructure

Deployment and containerization assets for local demo and online hosting.

This folder is mainly for packaging and deployment, not for the core chatbot logic.

## Docker Compose

From the repository root:

```powershell
docker compose -f infra/docker-compose.yml up --build
```

This starts:

- API: `http://localhost:8000`
- Frontend: `http://localhost:8080`

## Environment Notes

- The backend accepts `CORS_ORIGINS` as a comma-separated list.
- The frontend image expects `VITE_API_BASE_URL` at build time.
- SQLite is kept for the current project demo flow. For production, PostgreSQL would be a stronger next step.
