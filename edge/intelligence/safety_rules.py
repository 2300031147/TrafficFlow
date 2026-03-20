import structlog
from typing import Dict, Any
from edge.config.settings import config

logger = structlog.get_logger(__name__)

class SafetyRules:
    """
    Applies hard constraints to proposed timings to prevent dangerous light configs.
    Limits loaded from settings.signal. ZERO hardcoded parameters.
    """
    def __init__(self):
        self.constraints = config.signal

    def enforce(self, proposed_timings: Dict[str, int]) -> Dict[str, int]:
        """
        Adjusts raw timings back to safe boundaries if they exceed specs.
        Expects keys like: ns_green, ew_green.
        """
        enforced = dict(proposed_timings)
        
        if "ns_green" in enforced:
            enforced["ns_green"] = max(self.constraints.min_green_seconds, min(self.constraints.max_green_seconds, enforced["ns_green"]))
        if "ew_green" in enforced:
            enforced["ew_green"] = max(self.constraints.min_green_seconds, min(self.constraints.max_green_seconds, enforced["ew_green"]))

        return enforced
