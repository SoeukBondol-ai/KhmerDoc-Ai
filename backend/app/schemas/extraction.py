from datetime import datetime
from pydantic import BaseModel, Field


class ExtractedDocument(BaseModel):
    document_id: str
    document_type: str | None = None
    company_name: str | None = None
    phone: str | None = None
    date: str | None = None
    invoice_number: str | None = None
    total_amount: str | None = None
    currency: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)


class ExtractionRequest(BaseModel):
    force: bool = False


class ExtractionResponse(BaseModel):
    document_id: str
    extraction: ExtractedDocument
    created_at: datetime