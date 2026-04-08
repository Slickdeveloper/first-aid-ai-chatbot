# Data

This directory stores authorized source material and development data artifacts.

For this project, the most important folder here is `sources/`. That is the canonical place where approved medical content lives before ingestion.

- `sources/`: canonical approved source files used directly for ingestion
- `processed/`: normalized text and chunked content
- `vector_store/`: local vector index for development
- `local_db/`: local-only database files if needed

## Current Use

For this project, the main active knowledge base comes from:

- canonical approved files in `sources/`

These are ingested into the database by `scripts/ingest_sources.py`.
