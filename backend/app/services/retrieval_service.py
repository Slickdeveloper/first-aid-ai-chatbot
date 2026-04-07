from app.schemas.chat import Citation
from app.services.citation_service import build_citations


def retrieve_approved_content(_: str) -> list[Citation]:
    # This will later search the approved knowledge base; for now it returns starter data.
    return build_citations()
