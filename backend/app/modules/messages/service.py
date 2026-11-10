"""
Message Service
===============
Business logic for message composition.
Coordinates literal message generation and AI candidate pipeline.
"""

import logging
from typing import List

from fastapi import HTTPException, status

from app.core.config import settings
from app.ai.generation.composer import AIComposer
from app.repositories.message_repository import MessageRepository
from app.repositories.user_repository import UserRepository
from app.schemas.message import (
    ComposeRequest,
    MessageResponse,
    CandidateInResponse,
    ConceptItem,
    GenerationMetadata,
)

logger = logging.getLogger(__name__)


class MessageService:
    def __init__(
        self,
        message_repo: MessageRepository,
        user_repo: UserRepository,
        composer: AIComposer | None = None,
    ):
        self._messages = message_repo
        self._users = user_repo
        self._composer = composer or AIComposer()

    async def compose(self, user_id: str, request: ComposeRequest) -> MessageResponse:
        """
        Create a new message from selected concepts.
        Always generates a literal message.
        Optionally requests AI candidates from Gemini.
        If AI fails, activates resilient literal fallback candidate.
        """
        concepts = [c.label for c in request.selected_concepts]

        # Always build literal first
        literal = self._composer.build_literal(concepts)
        candidates = []
        gen_meta = {
            "status": "literal_only",
            "fallback_used": False,
            "model": None,
            "reason": "no_ai_requested" if not request.request_ai_suggestions else None,
        }

        # Optionally request AI suggestions
        if request.request_ai_suggestions:
            profile = await self._users.get_profile(user_id)
            language = profile.get("language", "en") if profile else "en"
            try:
                literal, candidates, gen_meta = await self._composer.generate(concepts, language)
            except Exception as exc:
                logger.warning("AI generation error, using literal fallback: %s", exc)
                literal_candidate = {
                    "candidate_id": "c_literal",
                    "text": literal,
                    "validation_status": "passed",
                    "requires_clarification": False,
                    "model": "literal_fallback",
                }
                candidates = [literal_candidate]
                gen_meta = {
                    "status": "fallback",
                    "fallback_used": True,
                    "model": None,
                    "reason": str(exc),
                }

        # Persist the message
        concepts_dicts = [c.model_dump() for c in request.selected_concepts]
        used_model = candidates[0].get("model") if candidates else None
        message = await self._messages.create(
            user_id=user_id,
            selected_concepts=concepts_dicts,
            literal_text=literal,
            candidates=candidates,
            model=used_model,
            generation=gen_meta,
        )

        return self._to_response(message)

    async def get_message(self, message_id: str, user_id: str) -> MessageResponse:
        message = await self._messages.find_by_id(message_id, user_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "RESOURCE_NOT_FOUND", "message": "Message not found"},
            )
        return self._to_response(message)

    async def list_messages(self, user_id: str) -> List[MessageResponse]:
        messages = await self._messages.find_recent(user_id)
        return [self._to_response(m) for m in messages]

    def _to_response(self, msg: dict) -> MessageResponse:
        concepts = [ConceptItem(**c) for c in msg.get("selected_concepts", [])]
        candidates = [
            CandidateInResponse(
                candidate_id=c["candidate_id"],
                text=c["text"],
                validation_status=c["validation_status"],
                requires_clarification=c.get("requires_clarification", False),
                model=c.get("model", msg.get("model")),
            )
            for c in msg.get("candidates", [])
            if c.get("validation_status") == "passed"  # Only return passed candidates
        ]
        gen_meta = msg.get("generation")
        generation_obj = GenerationMetadata(**gen_meta) if gen_meta else None

        return MessageResponse(
            id=msg["id"],
            user_id=msg["user_id"],
            selected_concepts=concepts,
            literal_text=msg["literal_text"],
            candidates=candidates,
            model=msg.get("model"),
            generation=generation_obj,
            approved_text=msg.get("approved_text"),
            approval_status=msg.get("approval_status", "pending"),
            version=msg.get("version", 0),
            created_at=msg.get("created_at", ""),
            updated_at=msg.get("updated_at", ""),
        )
