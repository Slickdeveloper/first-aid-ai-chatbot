"""Citation fallback helpers.

The current project avoids inventing citations when retrieval has no approved
source match, so this module returns an empty list instead of fake references.
"""

from app.schemas.chat import Citation


def build_citations() -> list[Citation]:
    # No fallback citations should be invented for medical answers.
    # Returning an empty list is safer than implying evidence that does not exist.
    return []
