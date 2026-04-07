from app.schemas.chat import Citation


def build_citations() -> list[Citation]:
    # Placeholder citation data until the retrieval layer is connected to real documents.
    return [
        Citation(
            title="First aid guidance",
            organization="Approved Source",
            url="https://example.org/first-aid-guidance",
            excerpt="Use approved first-aid guidance and seek urgent help for severe symptoms.",
        )
    ]
