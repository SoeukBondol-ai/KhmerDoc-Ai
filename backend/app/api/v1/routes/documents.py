from pathlib import Path
from fastapi import APIRouter, Depends, File, UploadFile, status

from app.api.deps import get_document_store, get_ocr_pipeline, get_settings_from_app
from app.core.config import Settings
from app.core.exceptions import bad_request, not_found, service_unavailable
from app.schemas.document import (
    DocumentCreateResponse,
    DocumentDetailResponse,
    DocumentListResponse,
    DocumentRecord,
    OCRRequest,
    OCRResponse,
)
from app.services.document_store import DocumentStore
from app.services.ocr_pipeline import OCRPipeline
from app.utils.files import extension_for_upload, make_document_id, read_json, save_upload_file, utc_now

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post(
    "/upload",
    response_model = DocumentCreateResponse,
    status_code = status.HTTP_201_CREATED,
    summary = "UPload docment to start processing",
    response_description="Document uploaded successfully"
)
async def upload_document(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings_from_app),
    store: DocumentStore = Depends(get_document_store),
) -> DocumentCreateResponse:
    document_id = make_document_id()
    extension = extension_for_upload(file)
    stored_filename = f"{document_id}{extension}"
    saved_path = settings.upload_dir / stored_filename

    try:
        size_bytes = await save_upload_file(file, saved_path, settings.max_upload_bytes)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc

    now = utc_now()
    record = DocumentRecord(
        document_id=document_id,
        original_filename=file.filename or stored_filename,
        stored_filename=stored_filename,
        content_type=file.content_type or "application/octet-stream",
        size_bytes=size_bytes,
        saved_path=saved_path,
        created_at=now,
    )
    store.add_document(record)

    return DocumentCreateResponse(
        document_id=document_id,
        filename=record.original_filename,
        content_type=record.content_type,
        size_bytes=size_bytes,
        saved_path=str(saved_path),
        created_at=now,
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    store: DocumentStore = Depends(get_document_store),
) -> DocumentListResponse:
    return DocumentListResponse(documents=store.list_documents())


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: str,
    store: DocumentStore = Depends(get_document_store),
) -> DocumentDetailResponse:
    document = store.get_document(document_id)
    if document is None:
        raise not_found(f"Document not found: {document_id}")

    ocr = None
    if document.ocr_output_path and Path(document.ocr_output_path).exists():
        ocr = OCRResponse.model_validate(read_json(Path(document.ocr_output_path)))

    return DocumentDetailResponse(document=document, ocr=ocr)


@router.post("/{document_id}/ocr", response_model=OCRResponse)
async def run_ocr(
    document_id: str,
    body: OCRRequest | None = None,
    pipeline: OCRPipeline = Depends(get_ocr_pipeline),
) -> OCRResponse:
    try:
        return await pipeline.run(document_id=document_id, force=body.force if body else False)
    except FileNotFoundError as exc:
        raise not_found(f"Document not found: {document_id}") from exc
    except Exception as exc:
        raise service_unavailable(f"OCR failed: {exc}") from exc
