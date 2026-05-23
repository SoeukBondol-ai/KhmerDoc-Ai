from fastapi import Request

from app.core.config import Settings
from app.services.document_store import DocumentStore
from app.services.extraction_pipeline import ExtractionPipeline
from app.services.extraction_service import ExtractionService
from app.services.nextspell_service import NextSpellService
from app.services.ocr_pipeline import OCRPipeline


def get_settings_from_app(request: Request) -> Settings:
    return request.app.state.settings


def get_document_store(request: Request) -> DocumentStore:
    settings = get_settings_from_app(request)
    return DocumentStore(settings.upload_dir, settings.ocr_output_dir)


def get_ocr_service(request: Request) -> NextSpellService:
    settings = get_settings_from_app(request)
    return NextSpellService(settings)


def get_ocr_pipeline(request: Request) -> OCRPipeline:
    return OCRPipeline(
        store=get_document_store(request),
        ocr_service=get_ocr_service(request),
    )


def get_extraction_pipeline(request: Request) -> ExtractionPipeline:
    settings = get_settings_from_app(request)
    return ExtractionPipeline(
        store=get_document_store(request),
        extraction_service=ExtractionService(),
        extraction_dir=settings.extraction_dir,
    )
