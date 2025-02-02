from typing import List, Dict, Union, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging

@dataclass
class DataPoint:
    value: float
    timestamp: datetime
    processed: bool = False

class DataProcessor:
    def __init__(self, threshold: float = 10.0):
        self.threshold = threshold
        self.data_points: List[DataPoint] = []
        self.logger = logging.getLogger(__name__)

    async def process_batch(self, numbers: List[float]) -> Dict[str, Union[List[float], str]]:
        try:
            data_points = [DataPoint(value=n, timestamp=datetime.now()) for n in numbers]
            self.data_points.extend(data_points)
            processed = await self._transform_data(data_points)
            return {"status": "success", "results": processed}
        except Exception as e:
            self.logger.error(f"Processing error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _transform_data(self, points: List[DataPoint]) -> List[float]:
        tasks = [self._process_point(point) for point in points]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

    async def _process_point(self, point: DataPoint) -> Optional[float]:
        if point.value > self.threshold:
            point.processed = True
            return point.value * 2
        return None

    def get_statistics(self) -> Dict[str, Union[int, float]]:
        processed_points = [p for p in self.data_points if p.processed]
        return {
            "total_points": len(self.data_points),
            "processed_points": len(processed_points),
            "average_value": sum(p.value for p in processed_points) / len(processed_points) if processed_points else 0
        }
