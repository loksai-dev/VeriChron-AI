"""Thin adapter around vectorize-io Hindsight retain / recall / reflect / create_mental_model."""

from app.services.hindsight_service import MockHindsightService, RealHindsightService

__all__ = ["MockHindsightService", "RealHindsightService"]
