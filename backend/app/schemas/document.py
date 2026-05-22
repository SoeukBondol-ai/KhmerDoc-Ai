from pydantic import BaseModel, Field
from datetime import datetime
from pathlib import Path
from typing import Any

from app.schemas.extraction import ExtractionResponse

class DocumentCreateResponse(BaseModel):
    document_id: str 
    filename: str
    content_type: str
    size_bytes: int
    saved_path: str
    created_at: datetime

class OCRRequest(BaseModel):
    force: bool = False

class OCRResponse(BaseModel):
    document_id: str
    text: str
    language: str | None = None
    source: str | None = None
    raw_response: Any | None = None
    created_at: datetime

class DocumentRecord(BaseModel):
    document_id: str
    original_filename: str
    stored_filename: str
    content_type: str
    size_bytes: int
    saved_path: Path
    created_at: datetime
    ocr_output_path: Path | None = None

class DocumentDetailResponse(BaseModel):
    document: DocumentRecord
    ocr: OCRResponse | None = None
    extraction: ExtractionResponse | None = None


class DocumentListResponse(BaseModel):
    documents: list[DocumentRecord] = Field(default_factory=list)
