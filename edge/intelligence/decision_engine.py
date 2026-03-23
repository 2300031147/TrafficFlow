import structlog
import time
import datetime

from edge.config.settings import config
from edge.intelligence.webster import WebsterEngine
from edge.intelligence.safety_rules import SafetyRules
from edge.intelligence.pattern_engine import PatternEngine
from edge.intelligence.festival_calendar import FestivalCalendar
from edge.signal.controller import SignalController
from edge.hardware.simulated.signal_sim import SignalSim
from edge.detector.lane_counter import LaneCounts

logger = structlog.get_logger(__name__)

class DecisionEngine:
    """
    Master brain core for edge execution locally on independent devices.
    Never awaits network responses for any of these decisions.
    """
    def __init__(self, signal_backend=None):
        self.signal_controller = SignalController(signal_backend or SignalSim())
        self.webster = WebsterEngine()
        self.safety = SafetyRules()
        self.patterns = PatternEngine()
        self.festivals = FestivalCalendar()
        self.pcu_weights = config.pcu

    def _get_pcu(self, counts: LaneCounts) -> float:
        return (counts.motorcycles * self.pcu_weights.motorcycle +
                counts.cars * self.pcu_weights.car +
                counts.autorickshaws * self.pcu_weights.autorickshaw +
                counts.buses * self.pcu_weights.bus +
                counts.trucks * self.pcu_weights.truck)

    def run_cycle(self, raw_ns_counts: LaneCounts, raw_ew_counts: LaneCounts) -> dict:
        """Executes layer evaluations (realtime + pattern + events)."""
        today = datetime.date.today()
        
        # Apply layer multipliers (patterns, events)
        festival_modifier = self.festivals.get_combined_modifier(today)
        active_events = self.festivals.get_active_event_names(today)
        
        def apply_modifier(counts: LaneCounts, mod: float) -> LaneCounts:
            return LaneCounts(
                total_count=int(counts.total_count * mod),
                stopped_count=int(counts.stopped_count * mod),
                motorcycles=int(counts.motorcycles * mod),
                cars=int(counts.cars * mod),
                buses=int(counts.buses * mod),
                trucks=int(counts.trucks * mod),
                autorickshaws=int(counts.autorickshaws * mod),
                avg_speed=counts.avg_speed
            )
            
        ns_scaled = apply_modifier(raw_ns_counts, festival_modifier)
        ew_scaled = apply_modifier(raw_ew_counts, festival_modifier)

        ns_pcu = self._get_pcu(ns_scaled)
        ew_pcu = self._get_pcu(ew_scaled)

        # Layer 1: Base Webster using scaled counts
        base_decision = self.webster.calculate_cycle(ns_scaled, ew_scaled)
        
        # Layer 1.5: Pattern adjustments
        pattern_confidence = 0.0
        pattern_data = self.patterns.match_patterns(ns_scaled, ew_scaled, current_phase="NS_GREEN", running_events=active_events)
        if pattern_data:
            pattern_confidence = pattern_data.get("confidence", 0.0)
            if pattern_confidence > 0.6:
                base_decision["ns_green"] = pattern_data["ns_green"]
                base_decision["ew_green"] = pattern_data["ew_green"]
                base_decision["total_cycle"] = pattern_data["total_cycle"]
                base_decision["reason"] = "pattern_matched"

        
        # Layer 2: Validating constraints via safety
        safe_decision = self.safety.enforce(base_decision)

        # Determine next phase (Toggle simulation logic)
        current_phase = self.signal_controller.backend.get_current_phase()
        if current_phase == "NS_GREEN":
            next_phase = "EW_GREEN"
            dur = safe_decision["ew_green"]
        elif current_phase == "EW_GREEN":
            next_phase = "NS_GREEN"
            dur = safe_decision["ns_green"]
        else:
            next_phase = "NS_GREEN"
            dur = safe_decision["ns_green"]
        
        # Real calculation logging for metrics tracking
        logger.info("decision_log",
                    ns_pcu=ns_pcu,
                    ew_pcu=ew_pcu,
                    festival_modifier=festival_modifier,
                    active_events=active_events,
                    ns_green=safe_decision["ns_green"],
                    ew_green=safe_decision["ew_green"],
                    cycle_length=safe_decision["total_cycle"],
                    source="webster")

        success = self.signal_controller.transition(next_phase, dur, config.signal)
        if not success:
            logger.warning("fallback_activated")
            self.signal_controller.backend.set_phase("ALL_RED", config.signal.fallback_cycle_seconds)

        if festival_modifier > 1.0 and active_events:
            reason_text = f"Festival traffic modifier active: {active_events[0]}"
        elif pattern_confidence > 0.6:
            reason_text = "Pattern-matched timing applied"
        else:
            reason_text = f"Webster formula applied — NS demand {ns_pcu:.0f} EW demand {ew_pcu:.0f}"

        decision_record = {
            "time": time.time(),
            "cycle_length": safe_decision["total_cycle"],
            "ns_green": safe_decision["ns_green"],
            "ew_green": safe_decision["ew_green"],
            "ns_demand": float(ns_pcu),
            "ew_demand": float(ew_pcu),
            "source": safe_decision.get("reason", "webster"),
            "active_event": active_events[0] if active_events else None,
            "pattern_confidence": float(pattern_confidence),
            "decision_reason": reason_text
        }
        return decision_record
