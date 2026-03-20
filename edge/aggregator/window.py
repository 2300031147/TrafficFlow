import structlog
import time
from typing import List, Dict, Any
from edge.detector.lane_counter import LaneCounts
from edge.config.settings import config

logger = structlog.get_logger(__name__)

class ReportingWindow:
    """Aggregates multiple detection cycles into a single unified window payload."""
    def __init__(self):
        self.window_size = config.timing.report_interval_seconds
        self.start_time = time.time()
        self.buffered_decisions: List[Dict[str, Any]] = []
        self.latest_counts: Dict[str, Any] = {}

    def record_decision(self, decision: Dict[str, Any]):
        self.buffered_decisions.append(decision)

    def record_counts(self, counts: Dict[str, LaneCounts]):
        self.latest_counts = {lane: count.to_dict() for lane, count in counts.items()}

    def is_ready(self) -> bool:
        return (time.time() - self.start_time) >= self.window_size

    def pop_payload(self) -> Dict[str, Any]:
        """Returns the payload and resets the window. Latest counts are preserved
        between windows so we never send empty {} for lanes."""
        payload = {
            "timestamp": time.time(),
            "lanes": self.latest_counts,
            "decisions": self.buffered_decisions
        }
        self.buffered_decisions = []
        # M10: Do not reset self.latest_counts so we don't send empty lanes on next report
        self.start_time = time.time()
        return payload
