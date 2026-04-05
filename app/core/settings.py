from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "TruthForge AI"
    app_env: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"
    default_source_type: str = "text"

    dspy_provider: str = Field(default="ollama_chat", min_length=1)
    dspy_model: str = Field(default="qwen2.5:7b", min_length=1)
    dspy_api_base: str = Field(default="http://localhost:11434", min_length=1)
    dspy_api_key: str = ""
    dspy_model_type: str | None = None
    dspy_temperature: float = 0.0
    dspy_max_tokens: int = 1200
    dspy_timeout_seconds: int = 60

    @property
    def dspy_model_identifier(self) -> str:
        return f"{self.dspy_provider}/{self.dspy_model}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
