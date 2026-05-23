from app.schemas.document import OCRResponse
from app.services.document_store import DocumentStore
from app.services.nextspell_service import NextSpellService
from app.utils.files import read_json, utc_now, write_json


class OCRPipeline:
    def __init__(self, store: DocumentStore, ocr_service: NextSpellService):
        self.store = store
        self.ocr_service = ocr_service

    async def run(self, document_id: str, force: bool = False) -> OCRResponse:
        document = self.store.get_document(document_id)
        if document is None:
            raise FileNotFoundError(document_id)
        output_path = self.store.ocr_output_dir / f"{document_id}.json"
        if output_path.exists() and not force:
            return OCRResponse.model_validate(read_json(output_path))

        result = await self.ocr_service.extract_text(document.saved_path)
        response = OCRResponse(
            document_id=document_id,
            text=result["text"],
            language="km",
            source="nextspell",
            created_at=utc_now(),
            raw_response=result["raw_response"],
        )

        write_json(output_path, response.model_dump(mode="json"))
        self.store.update_ocr_path(document_id, output_path)
        return response
