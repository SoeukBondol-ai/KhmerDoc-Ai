from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.api.deps import (
    get_document_store,
    get_extraction_pipeline,
    get_layout_service,
    get_ocr_pipeline,
    get_settings_from_app,
)
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
from app.schemas.extraction import ExtractionRequest, ExtractionResponse
from app.schemas.layout import LayoutDetectionRequest, LayoutDetectionResponse
from app.services.document_store import DocumentStore
from app.services.extraction_pipeline import ExtractionPipeline
from app.services.layout_service import LayoutService
from app.services.ocr_pipeline import OCRPipeline
from app.utils.files import (
    extension_for_upload,
    make_document_id,
    read_json,
    save_upload_file,
    utc_now,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "/upload",
    response_model=DocumentCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="UPload docment to start processing",
    response_description="Document uploaded successfully",
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
    settings: Settings = Depends(get_settings_from_app),
) -> DocumentDetailResponse:
    document = store.get_document(document_id)
    if document is None:
        raise not_found(f"Document not found: {document_id}")

    ocr = None
    if document.ocr_output_path and Path(document.ocr_output_path).exists():
        ocr = OCRResponse.model_validate(read_json(Path(document.ocr_output_path)))

    extraction = None
    extraction_path = settings.extraction_dir / f"{document_id}.json"
    if extraction_path.exists():
        extraction = ExtractionResponse.model_validate(read_json(extraction_path))

    layout = None
    layout_path = settings.layout_dir / f"{document_id}.json"
    if layout_path.exists():
        layout = LayoutDetectionResponse.model_validate(read_json(layout_path))

    return DocumentDetailResponse(
        document=document, ocr=ocr, extraction=extraction, layout=layout
    )


@router.post("/{document_id}/ocr", response_model=OCRResponse)
async def run_ocr(
    document_id: str,
    body: OCRRequest | None = None,
    pipeline: OCRPipeline = Depends(get_ocr_pipeline),
) -> OCRResponse:
    try:
        force = body.force if body else False
        return await pipeline.run(document_id=document_id, force=force)
    except FileNotFoundError as exc:
        raise not_found(f"Document not found: {document_id}") from exc
    except Exception as exc:
        raise service_unavailable(f"OCR failed: {exc}") from exc


@router.post("/{document_id}/extract", response_model=ExtractionResponse)
async def run_extraction(
    document_id: str,
    body: ExtractionRequest | None = None,
    pipeline: ExtractionPipeline = Depends(get_extraction_pipeline),
) -> ExtractionResponse:
    try:
        force = body.force if body else False
        return await pipeline.run(document_id=document_id, force=force)
    except FileNotFoundError as exc:
        raise not_found(f"Document not found: {document_id}") from exc
    except ValueError as exc:
        raise bad_request(str(exc)) from exc
    except Exception as exc:
        raise service_unavailable(f"Extraction failed: {exc}") from exc


@router.get("/{document_id}/layout", response_model=LayoutDetectionResponse)
async def get_layout(
    document_id: str,
    settings: Settings = Depends(get_settings_from_app),
) -> LayoutDetectionResponse:
    layout_path = settings.layout_dir / f"{document_id}.json"
    if not layout_path.exists():
        raise not_found(f"Layout not found for document: {document_id}")
    return LayoutDetectionResponse.model_validate(read_json(layout_path))


@router.post("/{document_id}/layout", response_model=LayoutDetectionResponse)
async def run_layout(
    document_id: str,
    body: LayoutDetectionRequest | None = None,
    service: LayoutService = Depends(get_layout_service),
) -> LayoutDetectionResponse:
    try:
        force = body.force if body else False
        return await service.run(document_id=document_id, force=force)
    except FileNotFoundError as exc:
        raise not_found(f"Document not found: {document_id}") from exc
    except Exception as exc:
        raise service_unavailable(f"Layout detection failed: {exc}") from exc
