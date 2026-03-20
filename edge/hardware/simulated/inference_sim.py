import structlog
from typing import Any, Dict, List
from edge.hardware.base import InferenceBackend
from edge.config.settings import config

logger = structlog.get_logger(__name__)

# Stub out the ultralytics dependency so we can run syntax checks freely without installation
try:
    # from ultralytics import YOLO
    _has_yolo = True
except ImportError:
    _has_yolo = False

class InferenceSim(InferenceBackend):
    """
    Simulated inference backend using tiny YOLOv8 in CPU mode.
    Outputs the same format that HailoRT will output.
    """
    
    def __init__(self):
        self.model_path = config.inference.model_path
        self._model = None
        self.classes = config.inference.vehicle_classes

    def initialize(self) -> None:
        logger.info(f"Initializing InferenceSim with model: {self.model_path}")
        if not _has_yolo:
            logger.warning("ultralytics not installed locally. Stubbing YOLO initialization.")
            return

        # Assuming we would load the torch CPU model here:
        # self._model = YOLO(self.model_path)
        logger.info("Model loaded successfully into simulated backend.")

    def detect_batch(self, frames: List[Any]) -> List[List[Dict[str, Any]]]:
        results = []
        for f in frames:
            # We would run:
            # detections = self._model(f, classes=self.classes, conf=config.inference.confidence)
            # and map to our dictionary schema.
            
            # Since this is simulated / executing without UI, we return dummy bounding box responses
            stub_bbox = [10, 10, 100, 100]
            # Simulated vehicle detection: Class 2 is usually Car in COCO
            results.append([{
                'class_id': 2,
                'confidence': 0.88,
                'bbox': stub_bbox,
            }])
        return results
