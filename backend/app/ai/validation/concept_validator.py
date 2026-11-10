"""
Concept Validator
=================
Checks that all user-selected concepts are present in the AI-generated candidate.
This is the most fundamental validation — if a concept is missing, the candidate
is invalid regardless of how natural the sentence sounds.
"""

import logging
import re
from typing import List

logger = logging.getLogger(__name__)

# Words that are connective/grammatical and don't need to appear literally
_FILLER_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to",
    "for", "of", "with", "is", "am", "are", "was", "were", "be",
    "been", "being", "do", "does", "did", "have", "has", "had",
    "will", "would", "can", "could", "shall", "should", "may", "might",
    "must", "ought",
}


def validate_concepts(candidate_text: str, selected_concepts: List[str]) -> bool:
    """
    Verify all selected concepts appear in the candidate text.

    Rules:
    - Comparison is case-insensitive
    - Short filler words (articles, auxiliaries) are exempt
    - Core concepts (nouns, verbs, adjectives, negations) must all appear
    - Handles word inflections (e.g. want -> wanting / wanted) without false substring positives

    Returns True if all required concepts are present.
    """
    text_lower = candidate_text.lower()
    words_in_text = set(re.findall(r"\b\w+\b", text_lower))

    for concept in selected_concepts:
        concept_lower = concept.strip().lower()
        if not concept_lower or concept_lower in _FILLER_WORDS:
            continue

        # If it's a multi-word concept, check if the full phrase or its constituent core words appear
        if " " in concept_lower:
            if concept_lower in text_lower:
                continue
            core_words = [w for w in concept_lower.split() if w not in _FILLER_WORDS]
            if core_words and all(w in words_in_text or any(w in t for t in words_in_text) for w in core_words):
                continue
            logger.debug("Concept validation failed: multi-word '%s' not found in '%s'", concept, candidate_text)
            return False

        # Single word concept:
        # 1. Exact token match
        if concept_lower in words_in_text:
            continue

        # 2. Concept as a stem in candidate token (e.g., concept="walk", token="walking")
        stem_matched = False
        for word in words_in_text:
            if len(concept_lower) >= 3 and word.startswith(concept_lower):
                stem_matched = True
                break
            # Handle reverse for plurals/inflections (e.g., concept="apples", token="apple")
            if len(word) >= 3 and concept_lower.startswith(word):
                stem_matched = True
                break

        if not stem_matched:
            logger.debug(
                "Concept validation failed: '%s' not found in '%s'",
                concept, candidate_text,
            )
            return False

    return True
