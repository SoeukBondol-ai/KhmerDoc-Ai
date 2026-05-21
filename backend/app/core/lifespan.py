from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.core.config import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.ocr_output_dir.mkdir(parents=True, exist_ok=True)
    app.state.settings = settings
    yield