import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import aiofiles
from fastapi import UploadFile

ALLOW_CONTENT_TYPE = {
    "images/jpeg": ".jpg",
    "image/png": ".png",
    "application/pdf": ".pdf",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def make_document_id() -> str:
    return f"doc_{uuid4().hex[:12]}"


def extension_for_upload(file: UploadFile) -> str:
    if file.content_type in ALLOW_CONTENT_TYPE:
        return ALLOW_CONTENT_TYPE[file.content_type]
    suffix = Path(file.filename or "").suffix.lower()
    return suffix or ".bin"


async def save_upload_file(
    file: UploadFile,
    destination: Path,
    max_bytes: int,
) -> int:
    size = 0
    destination.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(destination, "wb") as out_file:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > max_bytes:
                max_mb = max_bytes // (1024 * 1024)
                raise ValueError(f"File exceeds {max_mb}MB upload limit")
            await out_file.write(chunk)
    await file.seek(0)
    return size


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
