from typing import List, Dict, Any
from data_processor import DataProcessor
import asyncio
from datetime import datetime
import json

class AnalysisEngine:
    def __init__(self, batch_size: int = 100):
        self.processor = DataProcessor(threshold=15.0)
        self.batch_size = batch_size
        self.analysis_history: List[Dict[str, Any]] = []

    async def run_analysis(self, dataset: List[float]) -> Dict[str, Any]:
        if not self._validate_input(dataset):
            return {"error": "Invalid input data format"}

        batches = [dataset[i:i + self.batch_size]
                   for i in range(0, len(dataset), self.batch_size)]

        results = []
        for batch in batches:
            batch_result = await self.processor.process_batch(batch)
            results.append(batch_result)

        analysis_result = self._compile_results(results)
        self.analysis_history.append({
            "timestamp": datetime.now().isoformat(),
            "result": analysis_result
        })

        return analysis_result

    def _validate_input(self, dataset: List[float]) -> bool:
        return all(isinstance(x, (int, float)) for x in dataset)

    def _compile_results(self, results: List[Dict]) -> Dict[str, Any]:
        successful_results = [r["results"] for r in results if r["status"] == "success"]
        flattened_results = [item for sublist in successful_results for item in sublist]

        return {
            "total_processed": len(flattened_results),
            "statistics": self.processor.get_statistics(),
            "timestamp": datetime.now().isoformat()
        }

    def export_analysis_history(self, filepath: str) -> None:
        with open(filepath, 'w') as f:
            json.dump(self.analysis_history, f, indent=2)
