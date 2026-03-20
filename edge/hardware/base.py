from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple
# Use Any or basic types to avoid importing large libraries like numpy in the base interface unless needed.

class CameraBackend(ABC):
    """Abstract interface for all camera captures. Could be simulated or real RTSP."""
    @abstractmethod
    def start(self) -> None:
        """Initialize the camera connection or file reader."""
        pass

    @abstractmethod
    def read_frame(self) -> Any:
        """
        Read the latest frame.
        Returns:
            The raw frame array, generally a numpy ndarray.
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """Release camera resources and close connection."""
        pass

class InferenceBackend(ABC):
    """Abstract interface for all ML inference backends (YOLO, HailoRT, etc.)."""
    @abstractmethod
    def initialize(self) -> None:
        """Load the model into memory."""
        pass

    @abstractmethod
    def detect_batch(self, frames: List[Any]) -> List[List[Dict[str, Any]]]:
        """
        Run inference on a batch of frames.
        Args:
            frames: List of image arrays.
        Returns:
            A list of detections for each frame.
            Each detection is a dict with at minimum {'class_id': int, 'confidence': float, 'bbox': [x1, y1, x2, y2]}
        """
        pass

class SignalBackend(ABC):
    """Abstract interface for physical or simulated signal lights."""
    
    @abstractmethod
    def set_phase(self, phase_name: str, duration_seconds: int) -> None:
        """
        Command the junction to switch to a specific phase.
        Args:
            phase_name: String representing the phase (e.g., 'NS_GREEN', 'EW_GREEN')
            duration_seconds: How long this phase should be held.
        """
        pass

    @abstractmethod
    def get_current_phase(self) -> str:
        """Returns the active phase."""
        pass

    @abstractmethod
    def get_remaining_seconds(self) -> int:
        """Returns time remaining for the current phase."""
        pass
