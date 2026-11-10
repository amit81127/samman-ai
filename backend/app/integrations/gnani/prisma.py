"""
Gnani Prisma STT Adapter (Stub — Phase 5)
==========================================
Speech-to-text adapter for Gnani Prisma.
This is a stub — STT is a future feature, not required for core MVP.
"""

import logging

logger = logging.getLogger(__name__)


class GnaniPrismaAdapter:
    """Stub STT adapter."""

    async def transcribe(
        self,
        audio: bytes,
        mime_type: str,
        language: str | None = None,
    ) -> str:
        """
        Transcribe audio to text.
        Returns the transcript — user must review before any action is taken.
        """
        raise NotImplementedError(
            "Gnani Prisma STT is not enabled in this phase. "
            "Enable after verifying Gnani Prisma API access and reviewing data retention terms."
        )
