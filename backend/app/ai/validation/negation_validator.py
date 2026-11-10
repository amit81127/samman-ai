"""
Negation Validator
==================
Ensures that any negation in the user's selected concepts is preserved
in the AI candidate. This is a critical safety check — reversing "not want"
to "want" would completely change the user's intended meaning.
"""

import logging
import re
from typing import List

logger = logging.getLogger(__name__)

# Negation markers in English and common Indian language transliterations
NEGATION_TOKENS = {
    # English
    "not", "no", "never", "don't", "cannot", "can't", "won't", "wouldn't",
    "shouldn't", "couldn't", "doesn't", "didn't", "isn't", "aren't", "wasn't",
    "weren't", "without", "neither", "nor", "nothing", "nobody", "nowhere",
    "hardly", "barely", "scarcely",
    # Hindi transliterations
    "nahi", "nahin", "mat", "na",
    # Kannada transliterations
    "illa", "beda",
}


def validate_negation(candidate_text: str, selected_concepts: List[str]) -> bool:
    """
    Verify that all negation tokens in selected_concepts appear in the candidate.

    If the user selected "not" and the candidate removed it, return False.
    This is a hard failure — negation reversal is never acceptable.

    Returns True if no negation is reversed.
    """
    text_lower = candidate_text.lower()
    text_tokens = set(re.findall(r"\b[\w']+\b", text_lower))

    for concept in selected_concepts:
        concept_lower = concept.strip().lower()
        if concept_lower in NEGATION_TOKENS:
            # Check for the negation token itself or contraction
            negation_present = (
                concept_lower in text_tokens
                or _check_contractions(concept_lower, text_lower, text_tokens)
            )
            if not negation_present:
                logger.warning(
                    "Negation validation failed: '%s' missing from '%s'",
                    concept, candidate_text,
                )
                return False
    return True


def _check_contractions(negation: str, text: str, text_tokens: set[str]) -> bool:
    """Check if a full negation is covered by a contraction in the text."""
    contraction_map = {
        "not": ["n't", "not"],
        "cannot": ["can't", "cannot"],
        "will not": ["won't"],
        "do not": ["don't"],
        "does not": ["doesn't"],
        "did not": ["didn't"],
        "is not": ["isn't"],
        "are not": ["aren't"],
    }
    alternatives = contraction_map.get(negation, [negation])
    return any(alt in text_tokens or alt in text for alt in alternatives)
