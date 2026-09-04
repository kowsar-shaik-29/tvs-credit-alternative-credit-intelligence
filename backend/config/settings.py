"""Configuration and settings for TVS Credit NIRNAY Backend."""

from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"

    # CORS Configuration
    FRONTEND_URL: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5500,http://127.0.0.1:5500,http://localhost:8000,http://127.0.0.1:8000"

    # Artifact File Paths (relative to backend or absolute)
    MODEL_PATH: str = "models/enhanced_random_forest.pkl"
    PREPROCESSOR_PATH: str = "models/enhanced_preprocessor.pkl"
    THRESHOLD_PATH: str = "models/risk_threshold.pkl"
    NORMALIZATION_PARAMS_PATH: str = "config/normalization_params.json"

    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated FRONTEND_URL string into a list."""
        if not self.FRONTEND_URL:
            return ["*"] if self.ENVIRONMENT == "development" else []
        origins = [origin.strip() for origin in self.FRONTEND_URL.split(",") if origin.strip()]
        return origins

    def resolve_path(self, path_str: str) -> Path:
        """Resolve a path relative to the backend directory if not absolute."""
        p = Path(path_str)
        if p.is_absolute():
            return p
        return (BASE_DIR / p).resolve()

    @property
    def resolved_model_path(self) -> Path:
        return self.resolve_path(self.MODEL_PATH)

    @property
    def resolved_preprocessor_path(self) -> Path:
        return self.resolve_path(self.PREPROCESSOR_PATH)

    @property
    def resolved_threshold_path(self) -> Path:
        return self.resolve_path(self.THRESHOLD_PATH)

    @property
    def resolved_normalization_params_path(self) -> Path:
        return self.resolve_path(self.NORMALIZATION_PARAMS_PATH)


settings = Settings()
