from pathlib import Path

from app.schemas.extraction import ExtractionResponse, ExtractedDocument
from app.services.document_store import DocumentStore
from app.services.extraction_service import ExtractionService
from app.utils.files import read_json, utc_now, write_json


class ExtractionPipeline:
    def __init__(self, store: DocumentStore, extraction_service: ExtractionService, extraction_dir: Path):
        self.store = store
        self.extraction_service = extraction_service
        self.extraction_dir = extraction_dir

    async def run(self, document_id: str, force: bool = False) -> ExtractionResponse:
        document = self.store.get_document(document_id)
        if document is None:
            raise FileNotFoundError(document_id)

        if not document.ocr_output_path or not Path(document.ocr_output_path).exists():
            raise ValueError(f"OCR output not found for document: {document_id}")

        output_path = self.extraction_dir / f"{document_id}.json"
        if output_path.exists() and not force:
            return ExtractionResponse.model_validate(read_json(output_path))

        ocr_data = read_json(Path(document.ocr_output_path))
        ocr_text = ocr_data.get("text", "")
        raw_lines = ocr_data.get("raw_response", {}).get("lines", [])

        extracted: ExtractedDocument = self.extraction_service.extract(ocr_text, raw_lines, document_id)

        response = ExtractionResponse(
            document_id=document_id,
            extraction=extracted,
            created_at=utc_now(),
        )

        write_json(output_path, response.model_dump(mode="json"))
        return response