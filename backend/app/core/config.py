from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    app_name : str = "KhmerDocAI"
    app_env : str  = "local"
    api_v1_prefix: str = "/api/v1" 
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"


    upload_dir: Path = Path("storage/uploads")
    ocr_output_dir: Path = Path("storage/ocr_outputs")
    extraction_dir: Path = Path("storage/extractions")
    max_upload_mb: int = 15

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

def get_settings() -> Settings:
    return Settings()