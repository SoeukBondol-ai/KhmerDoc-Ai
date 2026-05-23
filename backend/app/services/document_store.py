from pathlib import Path

from app.schemas.document import DocumentRecord
from app.utils.files import read_json, write_json


class DocumentStore:
    def __init__(self, upload_dir: Path, ocr_output_dir: Path) -> None:
        self.upload_dir = upload_dir
        self.ocr_output_dir = ocr_output_dir
        self.index_path = upload_dir.parent / "documents_index.json"

    def _load_index(self) -> dict[str, dict]:
        if not self.index_path.exists():
            return {}
        return read_json(self.index_path)

    def _save_index(self, index: dict[str, dict]) -> None:
        write_json(self.index_path, index)

    def add_document(self, record: DocumentRecord) -> None:
        index = self._load_index()
        data = record.model_dump(mode="json")
        index[record.document_id] = data
        self._save_index(index)

    def get_document(self, document_id: str) -> DocumentRecord | None:
        index = self._load_index()
        data = index.get(document_id)
        if not data:
            return None
        return DocumentRecord.model_validate(data)

    def list_documents(self) -> list[DocumentRecord]:
        index = self._load_index()
        records = [DocumentRecord.model_validate(item) for item in index.values()]
        return sorted(records, key=lambda item: item.created_at, reverse=True)

    def update_ocr_path(self, document_id: str, ocr_output_path: Path) -> None:
        index = self._load_index()
        if document_id not in index:
            return
        index[document_id]["ocr_output_path"] = str(ocr_output_path)
        self._save_index(index)
