"""
API v1 Router — Complete (Phases 1 to 5)
========================================
Collects all v1 endpoint routers into one main APIRouter.
"""

from fastapi import APIRouter

from app.api.v1 import (
    auth,
    users,
    boards,
    vocabulary,
    messages,
    approvals,
    speech,
    phrases,
    partners,
    health,
    jobs,
)

api_router = APIRouter()

# Phase 1: Authentication & User Profiles
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="", tags=["Profile"])

# Phase 2: AAC Boards & Vocabulary
api_router.include_router(boards.router, prefix="/boards", tags=["Boards"])
api_router.include_router(vocabulary.router, prefix="/vocabulary", tags=["Vocabulary"])

# Phase 3: Message Composition & Approval Invariant
api_router.include_router(messages.router, prefix="/messages", tags=["Messages"])
api_router.include_router(approvals.router, prefix="/messages", tags=["Approvals"])

# Phase 4: Gnani Speech Synthesis (TTS)
api_router.include_router(speech.router, prefix="", tags=["Speech"])

# Phase 5: Saved Phrases, Delegated Partners & Health Monitoring
api_router.include_router(phrases.router, prefix="/phrases", tags=["Phrases"])
api_router.include_router(partners.router, prefix="/partners", tags=["Partners"])
api_router.include_router(health.router, prefix="", tags=["Health"])

# Phase 6: Durable Background Jobs & Processing (No Redis)
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
