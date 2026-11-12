"""
Background Jobs API Endpoints
=============================
REST endpoints for enqueuing, tracking, and monitoring durable background jobs
without Redis.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.dependencies import get_current_user_id, get_db
from app.repositories.job_repository import JobRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.job import (
    JobCreateRequest,
    JobListResponse,
    JobResponse,
    MaintenanceJobEnqueueRequest,
    QueueStatsResponse,
    TTSJobEnqueueRequest,
)

router = APIRouter()


@router.post("/speech", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def enqueue_tts_job(
    request: TTSJobEnqueueRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Enqueue a durable TTS synthesis background job for an approved message.
    Strictly verifies:
    1. Message exists and belongs to current user.
    2. approval_status == "approved".
    3. Idempotency key prevents duplicate queue entries.
    """
    message_repo = MessageRepository(db)
    message = await message_repo.find_by_id(request.message_id, user_id)
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

    language = request.language or "en-IN"
    voice = request.voice or "Shivani"
    idempotency_key = f"tts:{request.message_id}:{language}:{voice}"

    job_repo = JobRepository(db)
    job = await job_repo.create_job(
        job_type="tts_synthesis",
        payload={
            "message_id": request.message_id,
            "language": language,
            "voice": voice,
            "api_key": request.api_key,
        },
        user_id=user_id,
        idempotency_key=idempotency_key,
        max_retries=3,
    )

    return JobResponse(**job)


@router.get("/stats/queue", response_model=QueueStatsResponse)
async def get_queue_statistics(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Return real-time queue health counts (pending, running, completed, failed)."""
    job_repo = JobRepository(db)
    stats = await job_repo.get_queue_stats()
    return QueueStatsResponse(**stats)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Query execution status and results of a specific background job."""
    job_repo = JobRepository(db)
    job = await job_repo.find_by_id(job_id, user_id=user_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "RESOURCE_NOT_FOUND", "message": "Job not found"},
        )
    return JobResponse(**job)


@router.get("", response_model=JobListResponse)
async def list_user_jobs(
    status_filter: Optional[str] = Query(None, alias="status"),
    job_type: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """List recent background jobs belonging to the authenticated user."""
    job_repo = JobRepository(db)
    jobs = await job_repo.list_jobs(
        user_id=user_id,
        status=status_filter,
        job_type=job_type,
        limit=limit,
        skip=skip,
    )
    total = await job_repo.count_jobs(user_id=user_id, status=status_filter)
    return JobListResponse(
        jobs=[JobResponse(**j) for j in jobs],
        total=total,
    )


@router.post("/maintenance", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def enqueue_maintenance_job(
    request: MaintenanceJobEnqueueRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Enqueue an asynchronous maintenance task:
    - audio_cleanup: evicts stale disk audio files
    - cache_cleanup: evicts expired memory and disk cache items
    - analytics_aggregation: computes offline usage snapshots
    """
    valid_types = {"audio_cleanup", "cache_cleanup", "analytics_aggregation"}
    if request.job_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_JOB_TYPE",
                "message": f"job_type must be one of {list(valid_types)}",
            },
        )

    job_repo = JobRepository(db)
    job = await job_repo.create_job(
        job_type=request.job_type,
        payload={"requested_by": user_id},
        user_id=user_id,
        max_retries=2,
    )
    return JobResponse(**job)


@router.delete("/{job_id}", response_model=JobResponse)
async def cancel_job(
    job_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Cancel a pending job before execution."""
    job_repo = JobRepository(db)
    cancelled = await job_repo.cancel_job(job_id, user_id=user_id)
    if not cancelled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "CANNOT_CANCEL",
                "message": "Job cannot be cancelled (it may have already started or completed)",
            },
        )
    return JobResponse(**cancelled)

