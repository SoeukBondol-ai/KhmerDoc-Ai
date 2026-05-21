import asyncio
from pathlib import Path
from typing import Any
import os
import warnings
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
warnings.filterwarnings("ignore", module="huggingface_hub")

from kiri_ocr import OCR
from app.core.config import Settings

class KiriOCRService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        # Initialize Kiri OCR (auto-downloads from Hugging Face if first time)
        self.client = OCR()

    async def extract_text(self, file_path: Path) -> dict[str, Any]:
        """
        Extract text from an image using the kiri-ocr package.
        Runs the synchronous ocr.extract_text method in a thread pool to avoid blocking the event loop.
        """
        try:
            # We must pass the string representation of the Path object
            text, results = await asyncio.to_thread(self.client.extract_text, str(file_path))
            
            # Extract detailed box-by-box results
            detailed_results = []
            for line in results:
                detailed_results.append({
                    "text": line['text'],
                    "confidence": line['confidence']
                })
            
            return {
                "text": text,
                "raw_response": {"lines": detailed_results}
            }
        except Exception as e:
            return {
                "text": f"OCR Failed: {str(e)}", 
                "raw_response": {"error": str(e)}
            }
