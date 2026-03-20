import structlog
from edge.hardware.base import SignalBackend
from edge.signal.validator import Validator

logger = structlog.get_logger(__name__)

class SignalController:
    """Orchestrates hardware phase execution via constraints logic"""
    def __init__(self, backend: SignalBackend):
        self.backend = backend

    def transition(self, target_phase: str, target_duration: int, constraints) -> bool:
        if not Validator.is_valid_phase(target_phase):
            logger.error(f"Invalid Phase Requested: {target_phase}")
            return False

        if not Validator.is_valid_duration(target_duration, constraints.min_green_seconds, constraints.max_green_seconds):
            logger.error(f"Invalid Duration Requested: {target_duration}")
            return False

        # Apply transition
        logger.info(f"Transitioning cleanly to {target_phase} for {target_duration}s")
        self.backend.set_phase(target_phase, target_duration)
        return True
