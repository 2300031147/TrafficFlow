import threading
import queue
import structlog
from typing import Optional, Any
from edge.hardware.base import CameraBackend

logger = structlog.get_logger(__name__)

class CameraCaptureThread(threading.Thread):
    """
    Spawns a background thread to continually poll the camera backend so we 
    always have the latest frame ready without blocking the main detection loops.
    """
    def __init__(self, backend: CameraBackend, max_queue_size: int = 1):
        super().__init__(daemon=True)
        self.backend = backend
        self._running = False
        self.frame_queue = queue.Queue(maxsize=max_queue_size)

    def run(self):
        self._running = True
        logger.info("Camera capture thread started")
        while self._running:
            frame = self.backend.read_frame()
            if frame is not None:
                # Always keep only the most recent frame
                if self.frame_queue.full():
                    try:
                        self.frame_queue.get_nowait()
                    except queue.Empty:
                        pass
                self.frame_queue.put(frame)
    
    def get_latest_frame(self) -> Optional[Any]:
        try:
            return self.frame_queue.get_nowait()
        except queue.Empty:
            return None

    def stop(self):
        self._running = False
        logger.info("Camera capture thread requested to stop")
