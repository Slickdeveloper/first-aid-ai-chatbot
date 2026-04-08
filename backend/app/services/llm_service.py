"""Answer-generation helpers.

Despite the module name, this file currently has two jobs:
- build deterministic grounded answers from retrieved passages
- optionally call OpenAI if that path is enabled later

Keeping both here makes it easy to swap between the no-cost fallback and a hosted
LLM without changing the route or retrieval code.
"""

import re

from app.core.config import get_settings
from app.schemas.chat import Citation
from app.services.safety_service import build_emergency_action, localize_emergency_numbers


def _clean_passage_text(text: str) -> str:
    # Remove formatting noise so the chatbot sounds natural even though the stored
    # source content may come from markdown files.
    text = localize_emergency_numbers(text)
    lines = [line.strip() for line in text.splitlines()]
    cleaned_lines: list[str] = []

    for index, line in enumerate(lines):
        if not line:
            continue

        normalized = line.lstrip("#").strip()

        # Drop short title-like first lines such as "Burn first aid" that should not
        # appear in chat answers.
        if index == 0 and normalized and not re.search(r"[.!?]", normalized):
            word_count = len(normalized.split())
            if word_count <= 6:
                continue

        cleaned_lines.append(normalized)

    cleaned_text = " ".join(cleaned_lines)
    # Chunks may flatten headings into the first sentence, e.g.
    # "Burn first aid For a minor burn...".
    cleaned_text = re.sub(
        r"^[A-Za-z][A-Za-z\s]{0,40}\bfirst aid\b\s+(?=[A-Z])",
        "",
        cleaned_text,
        flags=re.IGNORECASE,
    )
    return cleaned_text


def _sentences_from_passages(passages: list[str]) -> list[str]:
    # Merge multiple retrieved passages into one sentence list so the formatter can
    # produce a single coherent response.
    text = " ".join(_clean_passage_text(passage) for passage in passages)
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text) if sentence.strip()]


def _format_grounded_answer(sentences: list[str]) -> str:
    # Convert cleaned source sentences into numbered steps because they scan more
    # easily during urgent first-aid situations.
    if not sentences:
        return ""

    # Keep the full grounded procedure, but skip duplicate sentences that can appear
    # across chunks.
    selected: list[str] = []
    seen: set[str] = set()

    for sentence in sentences:
        normalized = re.sub(r"\s+", " ", sentence).strip().lower()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        selected.append(sentence)

    normalized_steps: list[str] = []

    for index, sentence in enumerate(selected, start=1):
        cleaned = re.sub(r"\s+", " ", sentence).strip()
        if cleaned and not cleaned.endswith((".", "!", "?")):
            cleaned = f"{cleaned}."
        normalized_steps.append(f"Step {index}: {cleaned}")

    return " ".join(normalized_steps)


def build_clean_excerpt(text: str, max_length: int = 280) -> str:
    # Reuse passage cleanup for citation previews so the UI does not show raw
    # markdown headings.
    cleaned = _clean_passage_text(text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if len(cleaned) <= max_length:
        return cleaned

    shortened = cleaned[:max_length].rsplit(" ", 1)[0].strip()
    return f"{shortened}..."


def _build_fallback_answer(citations: list[Citation], supporting_passages: list[str]) -> str:
    # Build a concise answer directly from the retrieved approved passages.
    # This is the main no-cost answer path used by the current project.
    selected_sentences = _sentences_from_passages(supporting_passages)
    answer = _format_grounded_answer(selected_sentences)

    if answer:
        return answer

    source_name = citations[0].organization
    return (
        f"Based on {source_name} guidance, follow the steps shown in the cited source "
        "and seek professional care if symptoms worsen."
    )


def _build_emergency_answer(citations: list[Citation], supporting_passages: list[str]) -> str:
    # Emergency replies should lead with urgent action and still include the grounded
    # first-aid steps.
    emergency_intro = (
        f"This may be an emergency. {build_emergency_action()} and follow the first-aid steps below while help is on the way."
    )
    grounded_steps = _build_fallback_answer(citations, supporting_passages)

    if grounded_steps.startswith("Step 1:"):
        return f"{emergency_intro}\n\n{grounded_steps}"

    return emergency_intro


def _generate_with_openai(message: str, supporting_passages: list[str]) -> str | None:
    # This optional path exists so the project can later switch to a hosted model
    # while still grounding the answer in approved passages.
    settings = get_settings()
    if not settings.openai_api_key:
        return None

    try:
        from openai import OpenAI
    except ImportError:
        return None

    client = OpenAI(api_key=settings.openai_api_key)
    supporting_text = "\n\n".join(
        f"Approved passage {index + 1}:\n{build_clean_excerpt(passage, max_length=1000)}"
        for index, passage in enumerate(supporting_passages)
    )

    response = client.responses.create(
        model=settings.openai_model,
        reasoning={"effort": settings.openai_reasoning_effort},
        # The prompt deliberately forbids unsupported medical claims so the model is
        # still constrained by the retrieval layer.
        instructions=(
            "You are a first-aid assistant. Answer using only the approved passages provided. "
            "Do not add medical claims that are not supported by the passages. "
            "Keep the answer concise, practical, and easy to follow. "
            "If the passages are insufficient, say that you do not have enough approved source material."
        ),
        input=(
            f"User question:\n{message}\n\n"
            f"Approved source passages:\n{supporting_text}\n\n"
            "Write a brief answer grounded only in those passages."
        ),
    )
    return response.output_text.strip() or None


def generate_grounded_answer(
    message: str,
    citations: list[Citation],
    supporting_passages: list[str],
    emergency: bool,
) -> str:
    # This is the single public entry point used by the chat service.
    if emergency:
        return _build_emergency_answer(citations, supporting_passages)

    if not citations:
        # Refuse to answer when no approved source material supports the response.
        return (
            "I do not have enough approved source material to answer that safely yet. "
            "Please consult an official first-aid source or a qualified medical professional."
        )

    settings = get_settings()
    if not settings.allow_mock_responses:
        openai_answer = _generate_with_openai(message, supporting_passages)
        if openai_answer:
            return openai_answer

    return _build_fallback_answer(citations, supporting_passages)
