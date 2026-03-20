import time
import structlog
from edge.hardware.base import SignalBackend
from edge.config.settings import config

logger = structlog.get_logger(__name__)

class SignalSim(SignalBackend):
    """
    Simulated traffic light backend logic tracking phases in memory. 
    Logs phase changes using structlog semantics.
    """
    def __init__(self):
        self._current_phase = "ALL_RED"
        self._phase_start_time = time.time()
        self._duration = 3  # Initial startup duration

    def set_phase(self, phase_name: str, duration_seconds: int) -> None:
        if self._current_phase != phase_name:
            logger.info(
                "Signal Phase Changed", 
                old_phase=self._current_phase, 
                new_phase=phase_name, 
                duration=duration_seconds
            )
        else:
            logger.debug("Signal Phase Extended", phase=phase_name, extension=duration_seconds)
            
        self._current_phase = phase_name
        self._phase_start_time = time.time()
        self._duration = duration_seconds

    def get_current_phase(self) -> str:
        return self._current_phase

    def get_remaining_seconds(self) -> int:
        elapsed = int(time.time() - self._phase_start_time)
        return max(0, self._duration - elapsed)
