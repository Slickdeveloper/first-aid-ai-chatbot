"""Retrieval logic for approved medical content.

This module is the heart of the no-cost RAG workflow:
- turn a user query into a better search query
- rank approved chunks with TF-IDF
- filter weak or misleading matches
- return citations and passages for answer generation
"""

from collections.abc import Iterable
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sqlalchemy.orm import Session

from app.db.models.document_chunk import DocumentChunk
from app.db.models.source_document import SourceDocument
from app.schemas.chat import Citation, RetrievalResult
from app.services.citation_service import build_citations
from app.services.llm_service import build_clean_excerpt

EMERGENCY_QUERY_HINTS: dict[str, str] = {
    # Query hints act like lightweight domain knowledge. They help short or messy
    # user prompts map to the right medical topic without requiring a paid model.
    "bleeding heavily": "life threatening external bleeding severe bleeding",
    "deep cut": "life threatening external bleeding severe bleeding deep wound cut",
    "stabbed": "life threatening external bleeding severe bleeding stab wound deep wound",
    "stab wound": "life threatening external bleeding severe bleeding stab wound deep wound",
    "lot of blood": "life threatening external bleeding severe bleeding blood loss",
    "blood coming out": "life threatening external bleeding severe bleeding blood loss",
    "chest pain": "heart attack chest pain",
    "heartache": "heart attack chest pain heart pain",
    "heart hurts": "heart attack chest pain heart pain",
    "heart pain": "heart attack chest pain heart pain",
    "crushing chest pain": "heart attack chest pain heart pain emergency",
    "bruise": "bruise contusion swelling ice pack compression",
    "bruising": "bruise contusion swelling ice pack compression",
    "contusion": "bruise contusion swelling ice pack compression",
    "cut": "cuts minor wound wound cleaning antiseptic dressing bandage",
    "cuts": "cuts minor wound wound cleaning antiseptic dressing bandage",
    "minor cut": "cuts minor wound wound cleaning antiseptic dressing bandage",
    "wound": "cuts minor wound wound cleaning antiseptic dressing bandage",
    "broken arm": "fracture broken bone arm injury splint immobilize muscle bone joint injury",
    "broke their arm": "fracture broken bone arm injury splint immobilize muscle bone joint injury",
    "arm is broken": "fracture broken bone arm injury splint immobilize muscle bone joint injury",
    "broken bone": "fracture broken bone injury splint immobilize muscle bone joint injury",
    "fracture": "fracture broken bone injury splint immobilize muscle bone joint injury",
    "broke arm": "fracture broken bone arm injury splint immobilize muscle bone joint injury",
    "broke leg": "fracture broken bone leg injury splint immobilize muscle bone joint injury",
    "broken leg": "fracture broken bone leg injury splint immobilize muscle bone joint injury",
    "sprain": "sprain strain fracture rest ice compression elevation muscle bone joint injury",
    "immobilize a fracture": "fracture broken bone splint immobilize muscle bone joint injury",
    "got burnt": "burn burns burn first aid burned hand burn cooling running water",
    "got burned": "burn burns burn first aid burned hand burn cooling running water",
    "burned hand": "burn burns burn first aid hand burn cooling running water",
    "burnt hand": "burn burns burn first aid hand burn cooling running water",
    "i burned my hand": "burn burns burn first aid hand burn cooling running water",
    "burned my hand": "burn burns burn first aid hand burn cooling running water",
    "burned my skin": "burn burns burn first aid skin burn cooling running water",
    "hot water burned": "burn burns scald hot water burn first aid cooling running water",
    "severe burn": "burn burns severe burn first aid cooling running water",
    "ice on a burn": "burn burns first aid do not use ice on burn",
    "chest hurts": "heart attack chest pain",
    "chest is hurting": "heart attack chest pain",
    "pain in chest": "heart attack chest pain",
    "collapsed and not breathing": "cpr steps cardiac arrest not breathing cpr aed",
    "not breathing": "cpr steps cardiac arrest not breathing cpr aed",
    "cardiac arrest": "cpr steps cardiac arrest cpr aed not breathing",
    "during cardiac arrest": "cpr steps cardiac arrest cpr aed not breathing",
    "perform cpr": "cpr steps perform cpr not breathing cardiac arrest",
    "how do i perform cpr": "cpr steps perform cpr not breathing cardiac arrest",
    "use an aed": "aed steps use an aed defibrillator cardiac arrest cpr",
    "aed": "aed steps use an aed defibrillator cardiac arrest cpr",
    "trouble breathing": "respiratory distress trouble breathing",
    "breathing difficulty": "respiratory distress trouble breathing breathing difficulty",
    "breathing difficulties": "respiratory distress trouble breathing breathing difficulty",
    "difficulty breathing": "respiratory distress trouble breathing",
    "shortness of breath": "respiratory distress trouble breathing",
    "breathless": "respiratory distress trouble breathing shortness of breath",
    "gasping": "respiratory distress trouble breathing not breathing",
    "cant breathe": "respiratory distress trouble breathing",
    "can't breathe": "respiratory distress trouble breathing",
    "cannot breathe": "respiratory distress trouble breathing",
    "face drooping": "stroke face drooping slurred speech arm weakness",
    "facial drooping": "stroke face drooping slurred speech arm weakness",
    "arm weakness": "stroke face drooping slurred speech arm weakness",
    "slurred speech": "stroke face drooping slurred speech arm weakness",
    "trouble speaking": "stroke face drooping slurred speech arm weakness trouble speaking",
    "numbness": "stroke face drooping sudden weakness numbness arm weakness",
    "stroke symptoms": "stroke face drooping slurred speech arm weakness numbness",
    "one side weak": "stroke face drooping sudden weakness arm weakness numbness",
    "face is drooping": "stroke face drooping slurred speech arm weakness",
    "bleed": "life threatening external bleeding severe bleeding",
    "heavy bleeding": "life threatening external bleeding severe bleeding",
    "severe bleeding": "life threatening external bleeding severe bleeding",
    "bleeding heavily": "life threatening external bleeding severe bleeding",
    "spurting blood": "life threatening external bleeding severe bleeding",
    "gushing blood": "life threatening external bleeding severe bleeding",
    "anaphylaxis": "allergic reaction anaphylaxis severe allergic reaction",
    "allergic reaction": "allergic reaction anaphylaxis severe allergic reaction",
    "allergic reactions": "allergic reaction anaphylaxis severe allergic reaction",
    "severe allergic reaction": "allergic reaction anaphylaxis severe allergic reaction",
    "severe allergic reactions": "allergic reaction anaphylaxis severe allergic reaction",
    "swollen throat": "allergic reaction anaphylaxis throat swelling",
    "throat swelling": "allergic reaction anaphylaxis throat swelling",
    "swollen tongue": "allergic reaction anaphylaxis tongue swelling",
    "tongue swelling": "allergic reaction anaphylaxis tongue swelling",
    "low blood sugar": "diabetic emergencies low blood sugar glucose diabetic",
    "diabetic": "diabetic emergencies low blood sugar glucose diabetic",
    "electric shock": "electrical shock electric shock electricity current",
    "electic shock": "electrical shock electric shock electricity current",
    "electrical shock": "electrical shock electric shock electricity current",
    "electrical burns": "electrical shock electric shock electricity current burn",
    "heat stroke": "heat related illness heat stroke heat emergency",
    "someone has heat stroke": "heat related illness heat stroke heat emergency",
    "heat exhaustion": "heat related illness heat exhaustion heat emergency",
    "heat emergency": "heat related illness heat stroke heat exhaustion",
    "hypothermia": "hypothermia cold exposure shivering cold emergency warming",
    "shivering badly": "hypothermia cold exposure shivering cold emergency warming",
    "asthma": "respiratory distress trouble breathing asthma wheeze wheezing",
    "asthma attack": "respiratory distress trouble breathing asthma wheeze wheezing",
    "wheezing": "respiratory distress trouble breathing asthma wheeze wheezing",
    "choking": "choking airway blocked cannot breathe cannot swallow",
    "choked": "choking airway blocked cannot breathe cannot swallow",
    "choking and can't breathe": "choking airway blocked cannot breathe cannot swallow abdominal thrusts",
    "choking and cant breathe": "choking airway blocked cannot breathe cannot swallow abdominal thrusts",
    "food is stuck": "choking choking choking airway blocked food stuck in throat cannot swallow",
    "stuck in throat": "choking choking choking airway blocked food stuck in throat cannot swallow",
    "stuck in the throat": "choking choking choking airway blocked food stuck in throat cannot swallow",
    "stuck in someone's throat": "choking choking choking airway blocked food stuck in throat cannot swallow",
    "food is stuck in someone's throat": "choking choking choking airway blocked food stuck in throat cannot swallow",
    "food stuck in throat": "choking choking choking airway blocked food stuck in throat cannot swallow",
    "heimlich maneuver": "choking airway blocked abdominal thrusts heimlich maneuver",
    "cant swallow": "choking airway blocked cannot swallow",
    "can't swallow": "choking airway blocked cannot swallow",
    "cannot swallow": "choking airway blocked cannot swallow",
    "seizure": "seizures seizure convulsion epileptic attack",
    "seizures": "seizures seizure convulsion epileptic attack",
    "epileptic attack": "seizures seizure convulsion epileptic attack",
    "convulsion": "seizures seizure convulsion epileptic attack",
    "convulsions": "seizures seizure convulsion epileptic attack",
    "passed out": "fainting unresponsive unconscious passed out",
    "passes out": "fainting unresponsive unconscious passed out",
    "passing out": "fainting unresponsive unconscious passed out",
    "fainted": "fainting unresponsive unconscious passed out",
    "unconscious": "fainting unresponsive unconscious not breathing",
    "unresponsive": "fainting unresponsive unconscious not breathing",
    "stroke": "stroke warning signs face drooping slurred speech arm weakness",
    "having a stroke": "stroke warning signs face drooping slurred speech arm weakness",
    "know if someone is having a stroke": "stroke warning signs face drooping slurred speech arm weakness",
    "electrocuted": "electrical shock electric shock electrocuted electricity current burn",
    "electrocution": "electrical shock electric shock electrocuted electricity current burn",
    "dog bite": "animal bites rabies bite wound wash water",
    "animal bite": "animal bites rabies bite wound wash water",
    "insect sting": "insect bites and stings insect sting bee sting wasp sting anaphylaxis",
    "insect stings": "insect bites and stings insect sting bee sting wasp sting anaphylaxis",
    "bee sting": "insect bites and stings insect sting bee sting anaphylaxis",
    "wasp sting": "insect bites and stings insect sting wasp sting anaphylaxis",
    "head is bleeding": "severe bleeding external bleeding scalp wound bleeding from head",
    "head bleeding": "severe bleeding external bleeding scalp wound bleeding from head",
    "bleeding from head": "severe bleeding external bleeding scalp wound bleeding from head",
    "scalp bleeding": "severe bleeding external bleeding scalp wound bleeding from head",
    "snake bite": "snakebite envenoming snake bite venomous snake immobilize move medical care",
    "snake bit": "snakebite envenoming snake bite venomous snake immobilize move medical care",
    "bitten by a snake": "snakebite envenoming snake bite venomous snake immobilize move medical care",
    "snake bitten": "snakebite envenoming snake bite venomous snake immobilize move medical care",
    "snakebit": "snakebite envenoming snake bite venomous snake immobilize move medical care",
    "snakebite": "snakebite envenoming snake bite venomous snake immobilize move medical care",
    "poison": "poison exposure poison swallowed chemicals vomiting poison help",
    "poisoning": "poison exposure poison swallowed chemicals vomiting poison help",
    "swallowed poison": "poison exposure poison swallowed chemicals vomiting poison help",
    "drinks chemicals": "poison exposure swallowed chemicals poison help",
    "drank chemicals": "poison exposure swallowed chemicals poison help",
    "make someone vomit": "poison exposure swallowed chemicals poison help do not vomit",
    "epinephrine injection": "anaphylaxis allergic reaction epinephrine auto injector injection",
    "epinephrine auto injector": "anaphylaxis allergic reaction epinephrine auto injector injection",
    "urgent help me now": "community emergency recognition first response urgent emergency help now",
    "this is urgent": "community emergency recognition first response urgent emergency help now",
    "help me now": "community emergency recognition first response urgent emergency help now",
    "first aid steps quickly": "community emergency recognition first response urgent emergency help now",
    "before an ambulance arrives": "community emergency recognition first response while help is on the way",
    "before ambulance arrives": "community emergency recognition first response while help is on the way",
    "what should i do in an emergency": "community emergency recognition first response urgent emergency help now",
}

PRIMARY_ORGANIZATIONS = (
    "ifrc",
    "world health organization",
    "who",
)

SUPPORTING_ORGANIZATIONS = (
    "american red cross",
)

IFRC_GUIDELINE_URL = "https://www.ifrc.org/document/international-first-aid-resuscitation-and-education-guidelines"

TYPO_NORMALIZATIONS: dict[str, str] = {
    # Common spelling mistakes and phrasing variants seen in natural chat input.
    "electic": "electric",
    "bleedingg": "bleeding",
    "nose bleed": "nosebleed",
    "nose bleeds": "nosebleeds",
    "breeth": "breathe",
    "brething": "breathing",
    "drowining": "drowning",
    "seizuree": "seizure",
    "anaphalaxis": "anaphylaxis",
    "allergic reacion": "allergic reaction",
    "faintted": "fainted",
}

TOPIC_GUARDS: dict[str, tuple[str, ...]] = {
    # Some topics are easy to confuse with each other. These guards stop the system
    # from returning a source unless the query includes topic-specific words.
    "nosebleeds": ("nose", "nosebleed", "nostril"),
    "animal bites": ("animal", "bite", "bitten", "dog", "cat", "rabies"),
    "drowning process resuscitation": ("drowning", "water", "submerged", "submersion"),
}


def _expand_variants(text: str) -> str:
    # Add lightweight singular/plural variants so short topic queries match titles
    # more reliably.
    words = text.split()
    expanded: list[str] = []

    for word in words:
        cleaned = word.strip().lower()
        expanded.append(cleaned)

        if cleaned.endswith("s") and len(cleaned) > 4:
            expanded.append(cleaned[:-1])
        elif len(cleaned) > 3:
            expanded.append(f"{cleaned}s")

    return " ".join(expanded)


def _normalize_typos(text: str) -> str:
    # Normalize before ranking so "electic shock" can still match "electrical shock".
    normalized = text.lower()
    for wrong, corrected in TYPO_NORMALIZATIONS.items():
        normalized = re.sub(rf"\b{re.escape(wrong)}\b", corrected, normalized)
    return normalized


def _expand_query(query: str) -> str:
    # Build a richer search query from the user's raw text.
    expanded_query = _normalize_typos(query)
    lower_query = expanded_query.lower()

    for trigger, hint in EMERGENCY_QUERY_HINTS.items():
        if trigger in lower_query:
            expanded_query = f"{expanded_query} {hint}"

    return _expand_variants(expanded_query)


def _build_search_document(chunk: DocumentChunk, source: SourceDocument) -> str:
    # Blend source metadata into the searchable text so TF-IDF can weight topic
    # names strongly, not just the body chunk text.
    title = _expand_variants(" ".join([source.title] * 4))
    section = _expand_variants(
        " ".join(filter(None, [chunk.section, chunk.citation_label, chunk.section]))
    )
    chunk_text = _expand_variants(" ".join([chunk.chunk_text] * 2))
    organization = _expand_variants(source.organization)
    return "\n".join([title, section, organization, chunk_text])


def _organization_priority(source: SourceDocument) -> int:
    # Governance policy is applied during ranking so IFRC/WHO win when content quality
    # is otherwise similar.
    organization = source.organization.lower()
    if any(name in organization for name in PRIMARY_ORGANIZATIONS):
        return 2
    if any(name in organization for name in SUPPORTING_ORGANIZATIONS):
        return 1
    return 0


def _build_citation(chunk: DocumentChunk, source: SourceDocument) -> Citation:
    # Citations are built here so answer generation and the UI receive one clean shape.
    label = chunk.citation_label or f"Chunk {chunk.chunk_index + 1}"
    excerpt = build_clean_excerpt(chunk.chunk_text)
    if source.organization.lower() == "ifrc":
        title = f"{source.title} (paraphrased from IFRC guidelines, {label})"
    else:
        title = f"{source.title} ({label})"

    return Citation(
        title=title,
        organization=source.organization,
        url=source.source_url,
        excerpt=excerpt,
    )


def _is_broad_guideline_source(source: SourceDocument) -> bool:
    # Broad landing pages are less helpful to end users than topic-specific pages.
    return source.organization.lower() == "ifrc" and source.source_url == IFRC_GUIDELINE_URL


def _passes_topic_guard(query: str, source: SourceDocument) -> bool:
    # These topic guards are safety/quality checks, not just ranking tweaks.
    # They prevent obviously wrong supporting citations from appearing in the UI.
    lower_query = _normalize_typos(query)
    lower_title = source.title.lower()

    if lower_title == "shock" and ("electric" in lower_query or "electrical" in lower_query):
        return False

    if "stroke warning signs" in lower_title and "heat stroke" in lower_query:
        return False

    if "burn" in lower_title and ("electric" in lower_query or "electrical" in lower_query):
        return False

    for guarded_title, required_terms in TOPIC_GUARDS.items():
        if guarded_title in lower_title:
            return any(term in lower_query for term in required_terms)

    return True


def _rank_chunks(
    query: str, chunks: Iterable[tuple[DocumentChunk, SourceDocument]]
) -> RetrievalResult:
    # Ranking happens fully in memory because the current project uses a small local
    # dataset and TF-IDF rather than a dedicated vector database.
    chunk_rows = list(chunks)
    if not chunk_rows:
        return RetrievalResult(citations=[], supporting_passages=[])

    search_documents = [
        _build_search_document(chunk, source) for chunk, source in chunk_rows
    ]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
    matrix = vectorizer.fit_transform(search_documents + [_expand_query(query)])
    query_vector = matrix[-1]
    document_vectors = matrix[:-1]
    # Linear kernel on TF-IDF vectors is effectively cosine-style similarity here.
    similarities = linear_kernel(query_vector, document_vectors).flatten()

    ranked_indices = similarities.argsort()[::-1]
    top_chunks: list[tuple[float, int, Citation, str, bool]] = []

    for index in ranked_indices:
        score = float(similarities[index])
        if score <= 0:
            continue

        chunk, source = chunk_rows[index]
        if not _passes_topic_guard(query, source):
            continue
        top_chunks.append(
            (
                score,
                _organization_priority(source),
                _build_citation(chunk, source),
                chunk.chunk_text,
                _is_broad_guideline_source(source),
            )
        )

    if not top_chunks:
        return RetrievalResult(citations=[], supporting_passages=[])

    best_similarity = max(score for score, _, _, _, _ in top_chunks)
    filtered_chunks = [item for item in top_chunks if item[0] >= max(best_similarity * 0.65, 0.11)]

    # Do not show broad IFRC guideline landing pages when a more specific source
    # is available.
    if any(not item[4] for item in filtered_chunks):
        filtered_chunks = [item for item in filtered_chunks if not item[4]]

    filtered_chunks.sort(key=lambda item: (item[1], item[0]), reverse=True)
    filtered_chunks = filtered_chunks[:3]

    return RetrievalResult(
        citations=[citation for _, _, citation, _, _ in filtered_chunks],
        supporting_passages=[passage for _, _, _, passage, _ in filtered_chunks],
    )


def retrieve_approved_content(message: str, db: Session | None = None) -> RetrievalResult:
    # Public entry point used by the chat service.
    #
    # NOTE: If `db` is missing we cannot retrieve real source material, so this falls
    # back to empty supporting passages.
    if db is None:
        return RetrievalResult(citations=build_citations(), supporting_passages=[])

    rows = (
        db.query(DocumentChunk, SourceDocument)
        .join(SourceDocument, DocumentChunk.source_document_id == SourceDocument.id)
        .filter(SourceDocument.is_approved.is_(True))
        .all()
    )
    return _rank_chunks(message, rows)
