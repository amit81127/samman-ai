"""
Prompt Builder — High Speed & High Fidelity
===========================================
Constructs a concise, semantically constrained prompt for Gemini AAC realization.
Optimized for minimum Time-To-First-Token (TTFT) and strict safety guardrails.
"""

import json
from typing import List


class PromptBuilder:
    """Build fast, safety-constrained prompts for AAC sentence generation."""

    def build(self, concepts: List[str], language: str) -> str:
        concepts_json = json.dumps(concepts, ensure_ascii=False)
        target_lang = json.dumps(language, ensure_ascii=False)

        return f"""You are an AAC (Augmentative and Alternative Communication) sentence composer.
Your task is to convert the ordered AAC concepts into a short, natural sentence in {target_lang}.

INPUT DATA:
- Target Language: {target_lang}
- Selected Concepts: {concepts_json}

CRITICAL SAFETY & SEMANTIC RULES:
1. INTENT PRESERVATION: Express the exact meaning of the concepts. Do not add or remove core ideas.
2. NEGATION PROTECTION: NEVER reverse, omit, or introduce negation. Words like 'not', 'no', 'never', 'don't', 'nahi', 'illa' must be preserved.
3. ENTITY & NUMBER INTEGRITY: Keep names, numbers, times, and quantities exact.
4. ZERO HALLUCINATION: Never invent unmentioned medical symptoms, diagnoses, emotions, family members, or opinions.
5. GRAMMAR & SIMPLICITY: Produce short, simple, grammatically correct spoken language in {target_lang}.

OUTPUT FORMAT:
Return ONLY valid JSON matching this exact schema:
{{
  "candidates": [
    {{
      "text": "Natural sentence here",
      "preserved_concepts": {concepts_json},
      "unsupported_additions": [],
      "requires_clarification": false
    }}
  ]
}}

Generate 1 or 2 natural candidates now:"""
