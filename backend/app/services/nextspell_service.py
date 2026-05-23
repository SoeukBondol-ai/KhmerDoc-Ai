import asyncio
from pathlib import Path
from typing import Any

from nextocr import NextOCRClient

from app.core.config import Settings


class NextSpellService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = NextOCRClient(
            username=settings.nextspell_username,
            secretkey=settings.nextspell_secret_key,
        )

    async def extract_text(self, file_path: Path) -> dict[str, Any]:
        """Run OCR using NextSpell and return text + raw lines."""
        try:
            text = await asyncio.to_thread(self.client.ocr_image, str(file_path))

            # Collect streaming events to get per-line detail
            raw_lines: list[dict[str, Any]] = []
            try:
                for event in self.client.ocr_image_events(str(file_path)):
                    if isinstance(event, dict) and "text" in event:
                        raw_lines.append(
                            {
                                "text": event.get("text", ""),
                                "confidence": event.get("confidence", 0.0),
                            }
                        )
                    elif isinstance(event, str):
                        raw_lines.append({"text": event, "confidence": 0.0})
            except Exception:
                pass  # streaming is optional; we already have the full text

            if not raw_lines:
                raw_lines = [
                    {"text": line, "confidence": 0.0}
                    for line in text.split("\n")
                    if line.strip()
                ]

            return {
                "text": text,
                "raw_response": {"lines": raw_lines},
            }
        except Exception as e:
            return {
                "text": f"OCR Failed: {str(e)}",
                "raw_response": {"error": str(e)},
            }
