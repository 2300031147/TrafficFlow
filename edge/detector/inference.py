import structlog
from typing import Any, Dict, List
from edge.hardware.base import InferenceBackend

logger = structlog.get_logger(__name__)

class DetectorPipeline:
    def __init__(self, backend: InferenceBackend):
        self.backend = backend

    def run_inference(self, frame_batch: List[Any]) -> List[List[Dict[str, Any]]]:
        """
        Executes the backend on a batched set of frames.
        Returns bounding box lists organized per frame.
        """
        # Batch size from settings is implicit if frame_batch is length of connected cameras
        if not frame_batch:
            return []
            
        try:
            results = self.backend.detect_batch(frame_batch)
            return results
        except Exception as e:
            logger.error(f"Inference exception: {e}")
            return [[] for _ in frame_batch]
