import structlog
from typing import Dict, Any
from edge.detector.lane_counter import LaneCounts
from edge.config.settings import config

logger = structlog.get_logger(__name__)

class WebsterEngine:
    """Calculates optimal traffic light signal timings using Webster's 1958 IRC method."""
    def __init__(self):
        self.pcu = config.pcu
        self.constraints = config.signal
        self.saturation_flow = 1800.0  # vehicles per hour green time
        self.lost_time_per_phase = 4.0 # seconds

    def calculate_cycle(self, ns_counts: LaneCounts, ew_counts: LaneCounts) -> Dict[str, Any]:
        """Returns Webster timing cycle based on heavily weighted PCU data."""
        
        # Calculate passenger car unit ratios for both directions
        def get_pcu_ratio(counts: LaneCounts) -> float:
            return (counts.motorcycles * self.pcu.motorcycle +
                    counts.cars * self.pcu.car +
                    counts.autorickshaws * self.pcu.autorickshaw +
                    counts.buses * self.pcu.bus +
                    counts.trucks * self.pcu.truck)

        ns_pcu = get_pcu_ratio(ns_counts)
        ew_pcu = get_pcu_ratio(ew_counts)
        
        # y = flow_ratio per phase (demand / saturation_flow)
        y_ns = min(ns_pcu / self.saturation_flow, 0.45)
        y_ew = min(ew_pcu / self.saturation_flow, 0.45)
        
        Y = y_ns + y_ew
        if Y >= 1.0:
            Y = 0.9  # Cap to avoid negative or infinite cycle
            
        num_phases = 2
        L = num_phases * self.lost_time_per_phase
        
        # C = (1.5 * L + 5) / (1 - Y)
        C_calc = (1.5 * L + 5) / (1 - Y)
        
        # Cap cycle based on constraints
        C = max(self.constraints.min_cycle_seconds, min(self.constraints.max_cycle_seconds, int(C_calc)))
        
        # Effective green time
        G = C - L
        
        # Green per phase = (C - L) * (y / Y)
        if Y > 0:
            ns_green = int(G * (y_ns / Y))
            ew_green = int(G * (y_ew / Y))
        else:
            # Fallback to equal split if no demand
            ns_green = int(G / 2)
            ew_green = int(G / 2)
            
        # Enforce phase constraints
        ns_green = max(self.constraints.min_green_seconds, min(self.constraints.max_green_seconds, ns_green))
        ew_green = max(self.constraints.min_green_seconds, min(self.constraints.max_green_seconds, ew_green))

        return {
            "ns_green": ns_green,
            "ew_green": ew_green,
            "total_cycle": ns_green + ew_green + int(L),
            "reason": "webster"
        }
