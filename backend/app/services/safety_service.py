"""Safety and emergency-detection helpers.

This file centralizes the emergency policy used across the backend and frontend.
That keeps urgent wording, disclaimers, and keyword detection consistent.
"""

import re


GHANA_EMERGENCY_ACTION = (
    "Call 112 in Ghana immediately. Police: 191, Fire: 192, Ambulance: 193."
)

EMERGENCY_PHRASE_GROUPS = {
    # Grouping related phrases makes the intent easier to maintain than one giant set.
    "breathing_distress": {
        "not breathing",
        "collapsed and not breathing",
        "cant breathe",
        "can't breathe",
        "cannot breathe",
        "trouble breathing",
        "trouble breath",
        "difficulty breathing",
        "breathing difficulty",
        "breathing difficulties",
        "shortness of breath",
        "breathless",
        "gasping",
    },
    "unresponsive_state": {
        "unconscious",
        "passed out",
        "passing out",
        "fainted",
        "unresponsive",
        "not responding",
        "won't wake up",
        "not waking up",
    },
    "severe_bleeding": {
        "severe bleeding",
        "heavy bleeding",
        "bleeding a lot",
        "bleeding heavily",
        "spurting blood",
        "gushing blood",
        "life threatening bleeding",
        "life-threatening bleeding",
        "stabbed",
        "stab wound",
    },
    "chest_emergency": {
        "heart attack",
        "heartache",
        "cardiac arrest",
        "chest pain",
        "chest hurts",
        "chest is hurting",
        "pain in chest",
        "crushing chest pain",
        "heart pain",
        "heart hurts",
    },
    "stroke_warning_signs": {
        "stroke",
        "stroke symptoms",
        "face drooping",
        "face is drooping",
        "facial drooping",
        "arm weakness",
        "sudden weakness",
        "slurred speech",
        "speech is slurred",
        "trouble speaking",
        "numbness",
        "one side weak",
    },
    "seizures": {
        "seizure",
        "seizures",
        "epileptic attack",
        "convulsion",
        "convulsions",
        "seizure longer than 5 minutes",
        "seizure lasting more than 5 minutes",
    },
    "choking": {
        "choking",
        "choked",
        "airway blocked",
        "food stuck in throat",
        "cant swallow",
        "can't swallow",
        "cannot swallow",
    },
    "electrical_emergency": {
        "electrocuted",
        "electrocution",
        "electric shock",
        "electrical shock",
    },
    "anaphylaxis": {
        "anaphylaxis",
        "severe allergic reaction",
        "severe allergic reactions",
        "allergic reaction",
        "allergic reactions",
        "swollen tongue",
        "swollen throat",
        "throat swelling",
        "tongue swelling",
    },
}

EMERGENCY_KEYWORDS = {
    keyword for phrases in EMERGENCY_PHRASE_GROUPS.values() for keyword in phrases
}


def is_emergency(message: str) -> bool:
    # Simple keyword detection is enough for a starter scaffold and can later become
    # rules/NLP.
    lower_message = message.lower()
    return any(keyword in lower_message for keyword in EMERGENCY_KEYWORDS)


def build_emergency_action() -> str:
    # Centralize emergency contact wording so the UI and backend stay aligned for Ghana.
    return GHANA_EMERGENCY_ACTION


def localize_emergency_numbers(text: str) -> str:
    # Normalize US-centric emergency wording into the Ghana deployment context.
    # This is especially useful because some supporting source material comes from
    # organizations outside Ghana.
    localized = re.sub(r"\b9-1-1\b", "112 in Ghana", text, flags=re.IGNORECASE)
    localized = re.sub(r"\b911\b", "112 in Ghana", localized, flags=re.IGNORECASE)
    localized = re.sub(
        r"\blocal emergency number\b",
        "112 in Ghana",
        localized,
        flags=re.IGNORECASE,
    )
    localized = re.sub(
        r"\blocal emergency services\b",
        "112 in Ghana",
        localized,
        flags=re.IGNORECASE,
    )
    return localized


def build_disclaimer() -> str:
    # Every medical answer should remind the user that this is not a diagnosis tool.
    return (
        "This chatbot provides first-aid guidance from approved sources and does not "
        "replace professional medical diagnosis, treatment, or certified training."
    )
