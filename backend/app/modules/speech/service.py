"""
Speech Service
==============
Orchestrates TTS synthesis. This service enforces the most critical
invariant in the system:

    ONLY messages with approval_status == "approved" and owned by
    the requesting user may be sent to speech synthesis.

The TTS endpoint receives a message_id — this service reloads the
approved text from MongoDB. Arbitrary text is NEVER accepted.
"""

import logging
from typing import Tuple

from fastapi import HTTPException, status

from app.repositories.message_repository import MessageRepository
from app.repositories.speech_repository import SpeechRepository
from app.integrations.gnani.timbre import GnaniTimbreAdapter
from app.schemas.speech import SpeechJobResponse

logger = logging.getLogger(__name__)


class SpeechService:
    def __init__(
        self,
        message_repo: MessageRepository,
        speech_repo: SpeechRepository,
        tts_adapter: GnaniTimbreAdapter | None = None,
    ):
        self._messages = message_repo
        self._speech = speech_repo
        self._tts = tts_adapter or GnaniTimbreAdapter()

    async def synthesize(
        self,
        message_id: str,
        user_id: str,
        language: str,
        voice: str | None,
        api_key: str | None = None,
    ) -> Tuple[bytes, SpeechJobResponse]:
        """
        Convert an approved message to speech.

        Flow:
        1. Load message from MongoDB (not from client request)
        2. Verify user owns the message
        3. Verify approval_status == "approved"
        4. Send approved_text to Gnani (never client-supplied text)
        5. Record job metadata
        6. Return audio bytes and job record
        """
        message = await self._messages.find_by_id(message_id, user_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "RESOURCE_NOT_FOUND", "message": "Message not found"},
            )

        if message.get("approval_status") != "approved":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "APPROVAL_REQUIRED",
                    "message": "Message must be explicitly approved before speech synthesis",
                },
            )

        approved_text = message.get("approved_text")
        if not approved_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "APPROVAL_REQUIRED",
                    "message": "No approved text found for this message",
                },
            )

        job = await self._speech.create_job(
            user_id=user_id,
            message_id=message_id,
            approved_text_snapshot=approved_text,
        )
        job_id = job["id"]

        try:
            await self._speech.update_status(job_id, "processing")
            audio_bytes = await self._tts.synthesize(approved_text, language, voice, api_key=api_key)
            updated_job = await self._speech.update_status(job_id, "completed")
            logger.info("TTS completed for message %s, job %s (lang=%s, voice=%s)", message_id, job_id, language, voice)
            if not updated_job:
                updated_job = await self._speech.find_by_id(job_id, user_id)
            return audio_bytes, self._to_response(updated_job)
        except RuntimeError as exc:
            await self._speech.update_status(job_id, "failed", error_message=str(exc))
            logger.error("TTS failed for message %s: %s", message_id, exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "TTS_FAILED",
                    "message": "Speech synthesis failed. The approved text is still available.",
                    "approved_text": approved_text,
                    "job_id": job_id,
                },
            )

    async def synthesize_direct(
        self,
        text: str,
        language: str,
        voice: str | None,
        api_key: str | None = None,
    ) -> bytes:
        """Direct synthesis for phrases and quick sentences without a prior message record."""
        return await self._tts.synthesize(text, language, voice, api_key=api_key)

    async def get_job_status(self, job_id: str, user_id: str) -> SpeechJobResponse:
        job = await self._speech.find_by_id(job_id, user_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "RESOURCE_NOT_FOUND", "message": "Speech job not found"},
            )
        return self._to_response(job)

    def _to_response(self, job: dict) -> SpeechJobResponse:
        return SpeechJobResponse(
            job_id=job["id"],
            message_id=job["message_id"],
            status=job["status"],
            audio_url=job.get("audio_url"),
            error_message=job.get("error_message"),
            created_at=job.get("created_at", ""),
            completed_at=job.get("completed_at"),
        )
