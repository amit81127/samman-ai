"""
Speech Endpoints
================
POST /messages/{id}/speech       — Synthesize speech for an approved message
POST /speech/synthesize          — Direct speech synthesis for phrases or custom text
GET  /speech-jobs/{job_id}       — Check speech job status
"""

from typing import Optional
from fastapi import APIRouter, Depends, Response, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.dependencies import get_db, get_current_user_id
from app.repositories.message_repository import MessageRepository
from app.repositories.speech_repository import SpeechRepository
from app.repositories.user_repository import UserRepository
from app.modules.speech.service import SpeechService
from app.schemas.speech import SpeechJobResponse, SpeechSynthesizeRequest, DirectSynthesizeRequest

router = APIRouter()


def _service(db: AsyncIOMotorDatabase) -> SpeechService:
    return SpeechService(MessageRepository(db), SpeechRepository(db))


@router.post(
    "/messages/{message_id}/speech",
    summary="Synthesize speech for an approved message",
    responses={
        200: {"content": {"audio/wav": {}}},
        403: {"description": "Message not approved or not owned by user"},
        503: {"description": "Speech synthesis failed — approved text still available"},
    },
)
async def synthesize_speech(
    message_id: str,
    body: Optional[SpeechSynthesizeRequest] = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Convert an approved message to speech audio using Gnani AI Timbre v3.0.

    - Only approved messages can be synthesized
    - Text is loaded server-side from the approval record
    - Language, voice persona, and custom API key can be overridden per request
    - Returns audio/wav bytes on success
    """
    user_repo = UserRepository(db)
    profile = await user_repo.get_profile(user_id)

    language = (body.language if body and body.language else None) or (profile.get("language") if profile else "en-IN")
    voice = (body.voice if body and body.voice else None) or (profile.get("voice_preference") if profile else None)
    api_key = (body.api_key if body and body.api_key else None) or (profile.get("gnani_api_key") if profile else None)

    service = _service(db)
    audio_bytes, job = await service.synthesize(message_id, user_id, language, voice, api_key=api_key)

    return Response(
        content=audio_bytes,
        media_type="audio/wav",
        headers={"X-Speech-Job-Id": job.job_id},
    )


@router.post(
    "/speech/synthesize",
    summary="Direct speech synthesis for phrases or quick text",
    responses={
        200: {"content": {"audio/wav": {}}},
        503: {"description": "Speech synthesis failed"},
    },
)
async def synthesize_direct(
    request: DirectSynthesizeRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Directly synthesize any text using Gnani AI Timbre with multi-language and voice persona support."""
    user_repo = UserRepository(db)
    profile = await user_repo.get_profile(user_id)

    language = request.language or (profile.get("language") if profile else "en-IN")
    voice = request.voice or (profile.get("voice_preference") if profile else None)
    api_key = request.api_key or (profile.get("gnani_api_key") if profile else None)

    service = _service(db)
    audio_bytes = await service.synthesize_direct(request.text, language, voice, api_key=api_key)

    return Response(
        content=audio_bytes,
        media_type="audio/wav",
    )


@router.get(
    "/speech-jobs/{job_id}",
    response_model=SpeechJobResponse,
    summary="Check speech job status",
)
async def get_speech_job(
    job_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Check the status of an async speech synthesis job."""
    return await _service(db).get_job_status(job_id, user_id)
