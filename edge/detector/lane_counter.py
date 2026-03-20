from dataclasses import dataclass
from typing import Dict

@dataclass
class LaneCounts:
    """Represents the real-time vehicle counts and logic state for a given moment in a lane."""
    total_count: int = 0
    stopped_count: int = 0
    motorcycles: int = 0
    cars: int = 0
    buses: int = 0
    trucks: int = 0
    autorickshaws: int = 0
    avg_speed: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return {
            "total_count": self.total_count,
            "stopped_count": self.stopped_count,
            "motorcycles": self.motorcycles,
            "cars": self.cars,
            "buses": self.buses,
            "trucks": self.trucks,
            "autorickshaws": self.autorickshaws,
            "avg_speed": self.avg_speed
        }
