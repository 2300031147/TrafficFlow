import os
import json
import random
import datetime
from typing import Dict, Any

from edge.config.settings import config
from edge.detector.lane_counter import LaneCounts

class SyntheticTrafficGenerator:
    """
    Generates dummy traffic counts based on traffic_patterns.json
    Used exclusively in pure simulated setups when video_path is empty.
    """
    def __init__(self):
        self.pattern_key = config.junction.traffic_pattern
        conf_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'traffic_patterns.json')
        with open(conf_path, 'r') as f:
            data = json.load(f)
            # Default fallback if the pattern key isn't found
            self.pattern = data.get('patterns', {}).get(self.pattern_key, data['patterns'][data['default_pattern']])

    def generate_for_lane(self, lane_prefix: str, hour: int, is_weekend: bool) -> LaneCounts:
        """
        Produce a LaneCounts struct modeled around the current hour and lane dir.
        Args:
            lane_prefix: strictly starts with 'ns' or 'ew' to index correctly.
        """
        hourly_data = self.pattern['hourly'].get(str(hour), {"ns_base": 10, "ew_base": 10})
        
        is_ns = lane_prefix.startswith('ns_') or lane_prefix.startswith('north') or lane_prefix.startswith('south')
        base_count = hourly_data['ns_base'] if is_ns else hourly_data['ew_base']
        
        # Apply sigma noise
        noise = random.gauss(0, self.pattern['noise_sigma'])
        base_count = max(0, int(base_count * (1.0 + noise)))

        # Apply weekend modifiers
        if is_weekend:
            if hour <= self.pattern['weekend']['morning_hours_end']:
                base_count = int(base_count * self.pattern['weekend']['morning_multiplier'])
            else:
                base_count = int(base_count * self.pattern['weekend']['evening_multiplier'])

        # Split into vehicle mix
        mix = self.pattern['vehicle_mix']
        
        counts = LaneCounts(
            total_count=base_count,
            stopped_count=int(base_count * 0.2),  # roughly 20% stopped waiting at junction
            motorcycles=int(base_count * mix['motorcycles']),
            cars=int(base_count * mix['cars']),
            buses=int(base_count * mix['buses']),
            trucks=int(base_count * mix['trucks']),
            autorickshaws=int(base_count * mix['autorickshaws']),
            avg_speed=float(random.randint(10, 45))
        )
        return counts

    def get_current_counts(self) -> Dict[str, LaneCounts]:
        now = datetime.datetime.now()
        hour = now.hour
        is_weekend = now.weekday() >= 5
        
        return {
            "north_in": self.generate_for_lane("ns_north", hour, is_weekend),
            "south_in": self.generate_for_lane("ns_south", hour, is_weekend),
            "east_in": self.generate_for_lane("ew_east", hour, is_weekend),
            "west_in": self.generate_for_lane("ew_west", hour, is_weekend),
        }
