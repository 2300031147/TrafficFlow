from typing import List, Dict, Any

class FeatureExtractor:
    """Extracts normalization paths from historical DB results to feed LSTM."""
    
    def __init__(self, settings_features: List[str] = None):
        # We define relevant features expected by the pipeline config
        self.features = settings_features or ['count', 'stopped_count', 'motorcycles', 'cars']

    def normalize(self, raw_data: List[Dict[str, Any]]) -> List[List[float]]:
        # Mocking generic min-max normalization logic over sequence
        return [[0.5] * len(self.features) for _ in raw_data]
