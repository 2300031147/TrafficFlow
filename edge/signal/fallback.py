import structlog
from edge.hardware.base import SignalBackend
from edge.config.settings import config

logger = structlog.get_logger(__name__)

class FallbackController:
    """Manages system failure scenarios returning lights to a safe fixed cycle state."""
    
    def __init__(self, backend: SignalBackend):
        self.backend = backend
        self.cycle_time = config.signal.fallback_cycle_seconds

    def activate_fallback(self) -> None:
        logger.warning(f"FALLBACK ACTIVATED: Setting fixed {self.cycle_time}s ALL_RED cycle")
        self.backend.set_phase("ALL_RED", self.cycle_time)
