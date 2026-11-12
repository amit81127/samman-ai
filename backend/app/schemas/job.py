"""
Job Schemas
===========
Pydantic models for background job tracking, enqueuing, and status reporting.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, Enum):
    TTS_SYNTHESIS = "tts_synthesis"
    AUDIO_CLEANUP = "audio_cleanup"
    CACHE_CLEANUP = "cache_cleanup"
    ANALYTICS_AGGREGATION = "analytics_aggregation"
    PARTNER_NOTIFICATION = "partner_notification"


class JobCreateRequest(BaseModel):
    job_type: str = Field(..., description="Type of background job to execute")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Job parameters and arguments")
    idempotency_key: Optional[str] = Field(None, description="Unique key to prevent duplicate job execution")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum retry attempts on failure")


class TTSJobEnqueueRequest(BaseModel):
    message_id: str = Field(..., description="ID of the approved message to synthesize")
    language: Optional[str] = Field(None, description="Target language code, e.g. en-IN, hi-IN")
    voice: Optional[str] = Field(None, description="Target voice persona, e.g. Shivani, Prakash")
    api_key: Optional[str] = Field(None, description="Custom Gnani AI API key if provided")


class MaintenanceJobEnqueueRequest(BaseModel):
    job_type: str = Field(
        ...,
        description="Maintenance task to enqueue: audio_cleanup, cache_cleanup, or analytics_aggregation",
    )


class JobResponse(BaseModel):
    id: str = Field(..., description="Job identifier")
    job_type: str = Field(..., description="Type of job")
    status: str = Field(..., description="Job status: pending, running, completed, failed, cancelled")
    user_id: Optional[str] = Field(None, description="Owning user ID if user-scoped")
    attempts: int = Field(default=0, description="Number of execution attempts")
    max_retries: int = Field(default=3, description="Maximum allowable retries")
    result: Optional[Dict[str, Any]] = Field(None, description="Execution result on completion")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: str = Field(..., description="ISO 8601 creation timestamp")
    started_at: Optional[str] = Field(None, description="ISO 8601 execution start timestamp")
    completed_at: Optional[str] = Field(None, description="ISO 8601 completion timestamp")


class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int


class QueueStatsResponse(BaseModel):
    pending: int
    running: int
    completed: int
    failed: int
    total: int

