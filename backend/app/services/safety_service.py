EMERGENCY_KEYWORDS = {
    "not breathing",
    "unconscious",
    "severe bleeding",
    "heart attack",
    "stroke",
    "seizure",
    "choking",
}


def is_emergency(message: str) -> bool:
    # Simple keyword detection is enough for a starter scaffold and can later become rules/NLP.
    lower_message = message.lower()
    return any(keyword in lower_message for keyword in EMERGENCY_KEYWORDS)


def build_disclaimer() -> str:
    # Every medical answer should remind the user that this is not a diagnosis tool.
    return (
        "This chatbot provides first-aid guidance from approved sources and does not "
        "replace professional medical diagnosis, treatment, or certified training."
    )
