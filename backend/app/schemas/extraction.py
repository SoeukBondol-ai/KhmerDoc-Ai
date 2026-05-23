from pydantic import BaseModel, Field, model_validator


class ExtractionField(BaseModel):
    value: str | None = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    source: str = ""

    @model_validator(mode="before")
    @classmethod
    def coerce_plain_value(cls, data):
        if isinstance(data, str):
            return {"value": data, "confidence": 0.0, "source": "legacy"}
        if data is None:
            return {"value": None, "confidence": 0.0, "source": ""}
        return data


class ExtractedDocument(BaseModel):
    document_id: str
    document_type: ExtractionField = Field(default_factory=ExtractionField)
    company_name: ExtractionField = Field(default_factory=ExtractionField)
    phone: ExtractionField = Field(default_factory=ExtractionField)
    date: ExtractionField = Field(default_factory=ExtractionField)
    invoice_number: ExtractionField = Field(default_factory=ExtractionField)
    total_amount: ExtractionField = Field(default_factory=ExtractionField)
    currency: ExtractionField = Field(default_factory=ExtractionField)
    raw_text_preview: str = ""


class ExtractionRequest(BaseModel):
    force: bool = False


class ExtractionResponse(BaseModel):
    document_id: str
    extraction: ExtractedDocument
