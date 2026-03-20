import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List
from dotenv import load_dotenv

# L3: Use absolute path so this works regardless of CWD (systemd, tests, etc.)
_ENV_PATH = Path(__file__).parent.parent.parent / '.env.edge'
load_dotenv(_ENV_PATH)

def _parse_int_list(env_val: str, default: List[int]) -> List[int]:
    """Helper to parse a comma-separated string of integers from an environment variable."""
    if not env_val:
        return default
    try:
        return [int(x.strip()) for x in env_val.split(',')]
    except ValueError:
        return default

@dataclass
class JunctionConfig:
    junction_id: str = os.getenv('JUNCTION_ID', 'default-uuid')
    junction_name: str = os.getenv('JUNCTION_NAME', 'Simulated Junction')
    city: str = os.getenv('JUNCTION_CITY', 'DefaultCity')
    district: str = os.getenv('JUNCTION_DISTRICT', 'DefaultDistrict')
    state: str = os.getenv('JUNCTION_STATE', 'DefaultState')
    country: str = os.getenv('JUNCTION_COUNTRY', 'DefaultCountry')
    junction_type: str = os.getenv('JUNCTION_TYPE', 'highway')
    lat: float = float(os.getenv('JUNCTION_LAT', '0.0'))
    lng: float = float(os.getenv('JUNCTION_LNG', '0.0'))
    mode: str = os.getenv('JUNCTION_MODE', 'simulated')
    video_path: str = os.getenv('VIDEO_PATH', '')
    traffic_pattern: str = os.getenv('TRAFFIC_PATTERN', 'default_pattern')
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')

@dataclass
class SignalConstraints:
    min_green_seconds: int = 10
    max_green_seconds: int = 60
    min_pedestrian_seconds: int = 15
    min_cycle_seconds: int = 50
    max_cycle_seconds: int = 180
    min_phase_change_interval_seconds: int = 4
    fallback_cycle_seconds: int = 100
    emergency_override_duration_seconds: int = 120
    queue_critical_threshold: int = 20
    cameras_offline_fallback_threshold: int = 2

@dataclass
class PCUWeights:
    motorcycle: float = 0.5
    car: float = 1.0
    autorickshaw: float = 1.2
    bus: float = 3.0
    truck: float = 4.0

@dataclass
class InferenceConfig:
    precision: str = "fp16"
    fps: int = 15
    cameras: int = 4
    model_path: str = os.getenv('MODEL_PATH', '/mnt/sata/models/yolov8n.pt')
    classifier_path: str = os.getenv('CLASSIFIER_PATH', '/mnt/sata/models/classifier.pt')  # L7: configurable
    confidence: float = 0.5
    vehicle_classes: List[int] = field(default_factory=lambda: [2, 3, 5, 7]) # car, motorcycle, bus, truck in general COCO

@dataclass
class LaneZones:
    north_in: List[int] = field(default_factory=lambda: _parse_int_list(os.getenv('ZONE_NORTH_IN', ''), [0, 0, 100, 100]))
    south_in: List[int] = field(default_factory=lambda: _parse_int_list(os.getenv('ZONE_SOUTH_IN', ''), [0, 0, 100, 100]))
    east_in: List[int] = field(default_factory=lambda: _parse_int_list(os.getenv('ZONE_EAST_IN', ''), [0, 0, 100, 100]))
    west_in: List[int] = field(default_factory=lambda: _parse_int_list(os.getenv('ZONE_WEST_IN', ''), [0, 0, 100, 100]))

@dataclass
class CameraConfig:
    cam_north_in: str = os.getenv('CAM_NORTH_IN', 'sim')
    cam_south_in: str = os.getenv('CAM_SOUTH_IN', 'sim')
    cam_east_in: str = os.getenv('CAM_EAST_IN', 'sim')
    cam_west_in: str = os.getenv('CAM_WEST_IN', 'sim')

@dataclass
class PatternConfig:
    multiplier_cap_low: float = 0.5
    multiplier_cap_high: float = 2.0
    update_hour: int = 2
    update_minute: int = 0
    min_days_before_learning: int = 7
    lookback_days: int = 28
    min_confidence_to_apply: float = 0.7

@dataclass
class ThermalConfig:
    npu_max_temp_celsius: int = 80
    cpu_max_temp_celsius: int = 85
    throttle_action: str = "reduce_fps"
    min_fps_before_fallback: int = 5

@dataclass
class TimingConfig:
    decision_interval_seconds: int = 5
    report_interval_seconds: int = 10
    watchdog_ping_interval: int = 5
    watchdog_fail_threshold: int = 3
    watchdog_reconnect_wait: int = 15
    stream_port: int = int(os.getenv('STREAM_PORT', '8080'))
    buffer_retry_interval: int = 60

@dataclass
class UplinkConfig:
    ccc_url: str = os.getenv('CCC_URL', 'http://127.0.0.1:8000')
    api_token: str = os.getenv('API_TOKEN', 'dev-token')
    vpn_ip: str = os.getenv('VPN_IP', '10.0.0.2')

@dataclass
class PathConfig:
    sata_base: str = field(default_factory=lambda: os.getenv('SATA_BASE', './data'))
    models_dir: str = field(default_factory=lambda: os.path.join(os.getenv('SATA_BASE', './data'), 'models'))
    data_dir: str = field(default_factory=lambda: os.path.join(os.getenv('SATA_BASE', './data'), 'data'))
    logs_dir: str = field(default_factory=lambda: os.path.join(os.getenv('SATA_BASE', './data'), 'logs'))
    patterns_db: str = field(default_factory=lambda: os.path.join(os.getenv('SATA_BASE', './data'), 'data', 'patterns.db'))
    buffer_db: str = field(default_factory=lambda: os.path.join(os.getenv('SATA_BASE', './data'), 'data', 'buffer.db'))
    decisions_db: str = field(default_factory=lambda: os.path.join(os.getenv('SATA_BASE', './data'), 'data', 'decisions.db'))
    festival_config: str = field(default_factory=lambda: os.path.join(os.path.dirname(os.path.abspath(__file__)), 'festival_config.json'))
    festival_dates_template: str = field(default_factory=lambda: os.path.join(os.path.dirname(os.path.abspath(__file__)), 'festival_dates_{year}.json'))

@dataclass
class FestivalConfig:
    festival_modifier_cap: float = 3.0
    geographic_scope_enabled: bool = True

@dataclass
class Config:
    junction: JunctionConfig = field(default_factory=JunctionConfig)
    signal: SignalConstraints = field(default_factory=SignalConstraints)
    pcu: PCUWeights = field(default_factory=PCUWeights)
    inference: InferenceConfig = field(default_factory=InferenceConfig)
    lanes: LaneZones = field(default_factory=LaneZones)
    cameras: CameraConfig = field(default_factory=CameraConfig)
    pattern: PatternConfig = field(default_factory=PatternConfig)
    thermal: ThermalConfig = field(default_factory=ThermalConfig)
    timing: TimingConfig = field(default_factory=TimingConfig)
    uplink: UplinkConfig = field(default_factory=UplinkConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    festival: FestivalConfig = field(default_factory=FestivalConfig)

# Singleton initialization
config = Config()

def ensure_data_dirs():
    """Call explicitly in main() — not at import time (L2)."""
    os.makedirs(config.paths.data_dir, exist_ok=True)
    os.makedirs(config.paths.models_dir, exist_ok=True)
    os.makedirs(config.paths.logs_dir, exist_ok=True)
