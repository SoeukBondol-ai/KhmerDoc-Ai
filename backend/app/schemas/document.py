from pydantic import BaseModel, Field
from datetime import datetime

class DocumentCreateRespone(BaseModel):
    document_id: str 
    filename: str
    content_type : str
    size_bytes: str
    saved_path: str
    created_at : datetime

class OCRRequest(BaseModel):
    force : bool = False

class OCRResponse(BaseModel):
    document_id : str
    ocr_engine : str = "NextOCR"
    text : str
    raw_respone : str
    output_path : str
    create_at : datetime

class DocumentRecord(BaseModel):
    document_id : str
    original_file_name : str
    store_file_name : str
    content_type : str
    size_bytes : str
    save_path : str
    create_at : datetime
    ocr_output_path: str | None = None

class DocumentDetailResponse(BaseModel):
    document: DocumentRecord
    ocr: OCRResponse | None = None


class DocumentListResponse(BaseModel):
    documents: list[DocumentRecord] = Field(default_factory=list)


