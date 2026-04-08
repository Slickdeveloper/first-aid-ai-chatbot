"""Retrieval and answer-formatting tests.

These tests focus on how approved passages are selected and turned into grounded,
readable answers.
"""

from app.db.session import SessionLocal
from app.services.llm_service import build_clean_excerpt, generate_grounded_answer
from app.schemas.chat import Citation
from app.services.retrieval_service import retrieve_approved_content


def test_grounded_answer_falls_back_to_source_text_when_mock_mode_is_enabled() -> None:
    # The no-cost workflow should still produce useful grounded answers.
    answer = generate_grounded_answer(
        "How do I help with a burn?",
        [
            Citation(
                title="Burn First Aid",
                organization="American Red Cross",
                url="https://example.org",
                excerpt="For a minor burn, cool the burned area under cool running water.",
            )
        ],
        [
            "For a minor burn, cool the burned area under cool running water for at least 20 minutes."
        ],
        False,
    )

    assert "cool the burned area" in answer.lower()


def test_grounded_answer_keeps_full_procedure_not_just_three_steps() -> None:
    # Regression test: the assistant should keep the full approved procedure.
    answer = generate_grounded_answer(
        "How do I help with a burn?",
        [
            Citation(
                title="Burn First Aid",
                organization="American Red Cross",
                url="https://example.org",
                excerpt="For a minor burn, cool the burned area under cool running water.",
            )
        ],
        [
            (
                "For a minor burn, cool the burned area under cool running water for at least 20 minutes. "
                "Remove rings, watches, or tight clothing near the burn before swelling begins. "
                "Do not remove anything stuck to the skin. "
                "Cover the burn loosely with clean cling film or a sterile, non-fluffy dressing."
            )
        ],
        False,
    )

    assert "Step 4:" in answer
    assert "do not remove anything stuck to the skin" in answer.lower()


def test_emergency_answer_includes_emergency_intro_and_grounded_steps() -> None:
    # Emergency answers need both urgent action and the actual first-aid procedure.
    answer = generate_grounded_answer(
        "seizure",
        [
            Citation(
                title="Seizures",
                organization="IFRC",
                url="https://example.org",
                excerpt="Protect the person from nearby hazards during the seizure.",
            )
        ],
        [
            (
                "Protect the person from nearby hazards during the seizure. "
                "Do not restrain their movements and do not put anything in the mouth. "
                "When the seizure stops, place the person on their side if safe. "
                "Call emergency services if the seizure lasts longer than 5 minutes."
            )
        ],
        True,
    )

    assert "Call 112 in Ghana immediately" in answer
    assert "Step 1:" in answer
    assert "do not put anything in the mouth" in answer.lower()


def test_clean_excerpt_removes_markdown_heading() -> None:
    # UI snippets should not expose raw markdown headings.
    excerpt = build_clean_excerpt(
        "# Burn first aid\n\nFor a minor burn, cool the burned area under cool running water."
    )

    assert excerpt.startswith("For a minor burn")


def test_retrieval_matches_snake_bite_typos_to_who_topic() -> None:
    # Users often type natural variants like "snake bit" instead of canonical terms.
    db = SessionLocal()
    try:
        result = retrieve_approved_content("A snake bit her", db)
    finally:
        db.close()

    assert result.citations
    assert result.citations[0].organization == "World Health Organization"
    assert "Snakebite Envenoming" in result.citations[0].title


def test_retrieval_matches_typo_for_electric_shock() -> None:
    # Lightweight typo tolerance is important because emergency prompts are often rushed.
    db = SessionLocal()
    try:
        result = retrieve_approved_content("what to do after an electic shock", db)
    finally:
        db.close()

    assert result.citations
    assert "Electrical Shock" in result.citations[0].title


def test_retrieval_maps_emergency_synonyms_to_expected_topics() -> None:
    # Verify several synonym groups in one test so future ranking tweaks do not
    # silently break prompt coverage.
    db = SessionLocal()
    try:
        breathing = retrieve_approved_content("she has breathing difficulties", db)
        seizure = retrieve_approved_content("the person is having convulsions", db)
        allergic = retrieve_approved_content("these are severe allergic reactions", db)
        fainting = retrieve_approved_content("he passed out", db)
    finally:
        db.close()

    assert breathing.citations
    assert "Respiratory Distress" in breathing.citations[0].title
    assert seizure.citations
    assert "Seizure" in seizure.citations[0].title
    assert allergic.citations
    assert "Anaphylaxis" in allergic.citations[0].title or "Allergic" in allergic.citations[0].title
    assert fainting.citations
    assert "Fainting" in fainting.citations[0].title


def test_retrieval_maps_heartache_to_heart_attack_guidance() -> None:
    # "Heartache" is ambiguous in general English, but in this app we treat it as urgent.
    db = SessionLocal()
    try:
        result = retrieve_approved_content("heartache", db)
    finally:
        db.close()

    assert result.citations
    assert "Heart Attack" in result.citations[0].title


def test_retrieval_matches_bruise_prompt_to_bruise_guidance() -> None:
    db = SessionLocal()
    try:
        result = retrieve_approved_content("how do i deal with a bruise", db)
    finally:
        db.close()

    assert result.citations
    assert "Bruise First Aid" in result.citations[0].title


def test_retrieval_matches_broken_arm_to_muscle_bone_joint_guidance() -> None:
    db = SessionLocal()
    try:
        result = retrieve_approved_content("his arm is broken", db)
    finally:
        db.close()

    assert result.citations
    assert "Muscle, Bone and Joint Injury" in result.citations[0].title


def test_retrieval_matches_burnt_hand_prompt_to_burn_guidance() -> None:
    db = SessionLocal()
    try:
        result = retrieve_approved_content("her hand got burnt", db)
    finally:
        db.close()

    assert result.citations
    assert "Burn" in result.citations[0].title


def test_retrieval_matches_cut_prompt_to_cuts_guidance() -> None:
    db = SessionLocal()
    try:
        result = retrieve_approved_content("cut", db)
    finally:
        db.close()

    assert result.citations
    assert "Cut" in result.citations[0].title or "Scrape" in result.citations[0].title


def test_retrieval_filters_irrelevant_sources_for_head_bleeding() -> None:
    # This guards against weak secondary citations confusing the user during an emergency.
    db = SessionLocal()
    try:
        result = retrieve_approved_content("his head is bleeding", db)
    finally:
        db.close()

    titles = [citation.title.lower() for citation in result.citations]
    assert titles
    assert any("bleeding" in title for title in titles)
    assert all("nosebleeds" not in title for title in titles)
    assert all("animal bites" not in title for title in titles)
