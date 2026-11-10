"""
Safety Validator
================
Checks that the AI candidate does not add facts, people, places, emotions,
medical terms, or other information not present in the user's selected concepts.

This validator is the last line of defence before a candidate is shown to the user.
"""

import logging
import re
from typing import List

logger = logging.getLogger(__name__)

# Categories of content that must NOT be invented by the AI
_FORBIDDEN_ADDITIONS_CATEGORIES = [
    # Medical / diagnostic
    {"fever", "infection", "diagnosis", "disease", "condition", "medicine",
     "drug", "tablet", "injection", "hospital", "doctor", "nurse", "pain",
     "hurt", "sick", "ill", "symptom", "emergency"},
    # Emotions (only allowed if user selected them)
    {"happy", "sad", "angry", "scared", "worried", "anxious", "depressed",
     "frustrated", "excited", "afraid", "love", "hate", "fear"},
    # Consent / intention
    {"agree", "consent", "allow", "permit", "want", "wish", "hope", "intend"},
]


def validate_safety(
    candidate_text: str,
    selected_concepts: List[str],
    unsupported_additions: List[str],
) -> bool:
    """
    Check that the candidate does not contain critical unsupported additions.

    Two checks:
    1. Gemini's self-reported unsupported_additions list is non-empty
       and contains significant content (not just conjunctions/articles)
    2. The candidate does not contain high-risk words absent from selected concepts

    Returns True if the candidate is safe to show.
    """
    # Check 1: Gemini flagged unsupported additions
    significant_additions = [
        word for word in unsupported_additions
        if len(word) > 2  # ignore trivial words
    ]
    if significant_additions:
        logger.warning(
            "Safety: Gemini flagged unsupported additions: %s",
            significant_additions,
        )
        return False

    # Check 2: Independent check for high-risk invented content
    # Extract clean lower-cased tokens from concepts
    concept_tokens = set()
    for c in selected_concepts:
        concept_tokens.update(re.findall(r"\b\w+\b", c.lower()))

    # Extract clean tokens from candidate text
    text_words = set(re.findall(r"\b\w+\b", candidate_text.lower()))
    added_words = text_words - concept_tokens

    for forbidden_set in _FORBIDDEN_ADDITIONS_CATEGORIES:
        invented = added_words & forbidden_set
        if invented:
            logger.warning(
                "Safety: Candidate invents restricted content: %s", invented
            )
            return False

    return True
