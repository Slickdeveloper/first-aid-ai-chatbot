from app.schemas.chat import Citation


def generate_grounded_answer(message: str, citations: list[Citation], emergency: bool) -> str:
    if emergency:
        # Emergency cases should prioritize urgent action over a long conversational answer.
        return (
            "This may be an emergency. Call your local emergency number now and follow "
            "the cited first-aid guidance while help is on the way."
        )

    # For now, the answer is derived from retrieved citations instead of a live model call.
    source_name = citations[0].organization if citations else "approved sources"
    return (
        f"Based on {source_name} guidance, start with the recommended first-aid steps "
        "shown in the cited source and seek professional care if symptoms worsen."
    )
