from pathlib import Path
from app.schemas.document import DocumentRecord



class DocumentStore:
    def __init__(self, upload_dir:Path, ocr_output_dir:Path ) -> None:
        self.upload_dir = upload_dir
        self.ocr_output_dir = ocr_output_dir