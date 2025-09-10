"""Configuration management for SemWare."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import SettingsConfigDict

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API Configuration
    app_name: str = Field(default="SemWare", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")

    # API Key Authentication
    api_key: str = Field(default="your-secret-api-key", env="API_KEY")

    # Database Configuration
    db_path: Path = Field(default=Path("./data"), env="DB_PATH")

    # Model Configuration
    embedding_model_name: str = Field(
        default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL_NAME"
    )
    max_tokens_per_batch: int = Field(default=2000, env="MAX_TOKENS_PER_BATCH")
    embedding_dimension: int = Field(default=384, env="EMBEDDING_DIMENSION")

    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")

    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str | None = Field(default=None, env="LOG_FILE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


# Global settings instance
settings = get_settings()
