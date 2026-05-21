from pathlib import Path
from typing import Any
from app.core.config import Settings
import httpx

class NextOCRService:
    def __init__(self, settings:Settings) -> None:
        self.settings = settings
    def _headers(self) -> dict[str,str]:
        return {
            "X-username":self.settings.next_ocr_username,
            "X-Secret-Key":self.settings.nextocr_secret_key,
        }
    async def extract_text(self, file_path: Path) -> dict[str, Any]:
        if not self.settings.next_ocr_username or not self.settings.nextocr_secret_key:
            raise ValueError("NextOCR credentials are not configured")

        async with httpx.AsyncClient(timeout=120) as client:
            with file_path.open("rb") as file_obj:
                files = {"file": (file_path.name, file_obj)}
                response = await client.post(
                    self.settings.nextocr_api_url,
                    headers=self._headers(),
                    files=files,
                )
        response.raise_for_status()
        try :
            payload : response.json()
            text 
    