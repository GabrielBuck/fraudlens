from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_url: str = "sqlite:///./fraudlens.db"
    frontend_url: str = "http://localhost:3000"
    log_level: str = "INFO"
    random_seed: int = 42
    auto_seed: bool = False
    enable_admin_api: bool = False
    admin_api_token: str = ""
    default_account_count: int = Field(default=1000, ge=8, le=100_000)
    default_transaction_count: int = Field(default=50_000, ge=80, le=5_000_000)
    model_artifact_path: Path = Path("./artifacts/isolation_forest.joblib")
    detection_config_path: Path = Path("./config/detection.yaml")

    @field_validator("frontend_url")
    @classmethod
    def validate_frontend_url(cls, value: str) -> str:
        if not value.startswith(("http://", "https://")):
            raise ValueError("FRONTEND_URL must be an HTTP(S) origin")
        return value.rstrip("/")


@lru_cache
def get_settings() -> Settings:
    return Settings()
