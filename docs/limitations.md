# Project Limitations

This document collects the main technical limitations and demo constraints for the current version of the First Aid AI Chatbot.

## Retrieval Limitations

- The active retrieval layer uses `TF-IDF`, not semantic embeddings.
- Matching quality is improved with synonyms, typo normalization, and query hints, but unusual phrasing can still miss the best source.
- Retrieval quality depends on the approved source corpus currently stored in the database.

## Data and Ingestion Limitations

- Approved medical files live in `data/sources/`, but they are not usable by the chatbot until `scripts/ingest_sources.py` has been run.
- If the database is reset or replaced, the knowledge base must be ingested again before the admin page and chatbot show expected content.
- The current project uses a local SQLite database for simplicity. This is suitable for demo use, but PostgreSQL would be stronger for a more robust deployment.

## Authentication and Security Limitations

- The admin area uses a shared key (`ADMIN_API_KEY`) rather than named user accounts.
- This is acceptable for a course project or controlled demo, but it is not the same as full production-grade authentication and authorization.

## LLM Limitations

- The project is designed to work without a paid model API.
- `OPENAI_API_KEY`, `OPENAI_MODEL`, and `OPENAI_REASONING_EFFORT` appear in `backend/.env`, but they are optional placeholders unless:
  - a real API key is provided
  - `ALLOW_MOCK_RESPONSES` is set to `false`
- In the current no-cost mode, answers are generated from retrieved approved passages rather than a production hosted LLM.

## Frontend and Deployment Limitations

- The frontend depends on the backend being reachable through the configured API base URL.
- Local development can shift from port `5173` to `5174`, so CORS and frontend URLs must be aligned.
- Docker and deployment files are included, but local Docker usage still depends on Docker being installed on the machine.

## Safety Limitations

- Emergency detection is rule-based, not clinically intelligent.
- The chatbot is designed to refuse unsupported topics instead of guessing, but it is still a first-aid guidance tool, not a diagnosis or treatment system.
- The system should always be presented with its disclaimer and emergency escalation behavior intact.

## Recommended Future Improvements

- upgrade retrieval to embedding-based semantic search
- replace shared-key admin access with stronger user authentication
- move from SQLite to PostgreSQL for a more robust hosted setup
- expand IFRC/WHO topic coverage further
- add more evaluation cases for edge phrasing and emergency prompts
