"""Chunking helpers for retrieval.

These functions break long source text into smaller overlapping slices so the
retrieval layer can match focused medical passages instead of whole documents.
"""

from collections.abc import Iterable


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 120) -> list[str]:
    # Break long source text into overlapping chunks so retrieval has focused
    # passages to search.
    normalized = " ".join(text.split())
    if not normalized:
        return []

    chunks: list[str] = []
    start = 0

    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        chunks.append(normalized[start:end].strip())
        if end == len(normalized):
            break
        # Overlap helps keep context when an important sentence sits near a chunk boundary.
        start = max(end - overlap, start + 1)

    return chunks


def enumerate_chunks(chunks: Iterable[str]) -> list[tuple[int, str]]:
    # Pair each chunk with its index so citations can refer back to stable positions.
    return [(index, chunk) for index, chunk in enumerate(chunks)]
