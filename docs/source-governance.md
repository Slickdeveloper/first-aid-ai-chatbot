# Source Governance

This project uses a source-priority policy for medical guidance:

- Primary approved sources: `IFRC` and `WHO`
- Supporting approved sources: `American Red Cross` and `Mayo Clinic` when needed

The purpose of this policy is to keep the chatbot grounded in trusted, reviewable medical content instead of general web text or model memory.

## Governance Rules

- New content should be added from `IFRC` or `WHO` first whenever equivalent guidance is available.
- Supporting content may be used to supplement coverage when an IFRC or WHO source is not yet available for the scenario.
- All source entries must include the official organization name, source URL, summary, and approved content path.
- The canonical filesystem location for approved content is `data/sources/`.
- The admin/source-management page is used to review, approve, ingest, unapprove, or remove sources from retrieval.
- Retrieval should prefer IFRC and WHO content when multiple approved sources match the same question.

## Review Guidance

- Keep paraphrases faithful to the underlying medical source.
- Do not invent unsupported medical steps.
- Re-ingest a source whenever approved content changes.
- Remove or unapprove outdated content if a newer official source supersedes it.
