import time
import structlog
from typing import Any
from edge.hardware.base import CameraBackend
from edge.config.settings import config

logger = structlog.get_logger(__name__)

class CameraSim(CameraBackend):
    """
    Simulated camera backend. 
    If video_path is provided, it simulates reading from a video.
    Otherwise, it acts as a stub that relies on purely data-driven fake traffic limits.
    """
    def __init__(self, lane_name: str):
        self.lane_name = lane_name
        self.video_path = config.junction.video_path
        self._running = False
        self._frame_count = 0

    def start(self) -> None:
        logger.info(f"Starting simulated camera for {self.lane_name}")
        self._running = True
        if self.video_path:
            logger.info(f"Will simulate reading from {self.video_path}")
        else:
            logger.info("No video path provided. Functioning as a pure data generator stub.")

    def read_frame(self) -> Any:
        if not self._running:
            return None
        
        # In a real environment, this might return a numpy array
        # Here we return a stubbed dictionary representing a "frame" safely
        self._frame_count += 1
        # L10: Non-blocking return. Let pipeline handle FPS pacing as requested
        return {"simulated": True, "frame_id": self._frame_count, "lane": self.lane_name}

    def stop(self) -> None:
        logger.info(f"Stopping simulated camera for {self.lane_name}")
        self._running = False
