import structlog
from typing import Dict, Any

logger = structlog.get_logger(__name__)

class Validator:
    """Validates parameters before sending instructions directly to the signals."""
    
    @staticmethod
    def is_valid_phase(phase: str) -> bool:
        valid_phases = ["NS_GREEN", "EW_GREEN", "ALL_RED"]
        return phase in valid_phases

    @staticmethod
    def is_valid_duration(duration: int, min_val: int, max_val: int) -> bool:
        return min_val <= duration <= max_val
