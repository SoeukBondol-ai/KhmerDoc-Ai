from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router as api_router
from app.core.config import get_settings
from app.core.lifespan import lifespan

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Khmer document understanding backend with Kiri-OCR integration.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
