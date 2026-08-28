# backend/app/core/config.py
from pathlib import Path

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Locate .env in backend/ or root repository directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env" if (BASE_DIR / ".env").exists() else BASE_DIR.parent / ".env"


class Settings(BaseSettings):
    PROJECT_NAME: str = "RepoMind"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # --------------------------------------------------------------------------
    # Mandatory Database Configuration
    # --------------------------------------------------------------------------
    DATABASE_URL: str
    DB_ECHO: bool = False

    # --------------------------------------------------------------------------
    # Optional GitHub Token
    # --------------------------------------------------------------------------
    GITHUB_TOKEN: str | None = None

    # --------------------------------------------------------------------------
    # AI Provider & Model Configuration
    # --------------------------------------------------------------------------
    # Embeddings: "mock", "fastembed", "openai", "gemini"
    EMBEDDING_PROVIDER: str = "mock"
    EMBEDDING_MODEL: str = "gemini-embedding-001"
    EMBEDDING_BATCH_SIZE: int = 32

    # LLM: "mock", "openai", "openrouter", "groq", "anthropic", "gemini"
    LLM_PROVIDER: str = "mock"
    LLM_MODEL: str = "gemini-1.5-flash"
    LLM_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"

    # API Keys (Loaded from .env)
    LLM_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None

    # --------------------------------------------------------------------------
    # Security, Limits & CORS
    # --------------------------------------------------------------------------
    MAX_REPOSITORY_SIZE_MB: int = 100
    MAX_FILES: int = 5000
    MAX_FILE_SIZE_KB: int = 500
    RATE_LIMIT_PER_MINUTE: int = 60
    CORS_ORIGINS: list[str] = ["https://repo-mind-black.vercel.app","https://repo-mind-git-main-msrc.vercel.app"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return []

    @model_validator(mode="after")
    def validate_mandatory_and_conditional_secrets(self) -> "Settings":
        # 1. DATABASE_URL must be defined
        if not self.DATABASE_URL or not self.DATABASE_URL.strip():
            raise ValueError(
                "CRITICAL CONFIG ERROR: 'DATABASE_URL' is missing in .env. "
                "Please configure a valid PostgreSQL connection string."
            )

        # 2. Validate LLM Secret conditionally
        llm_provider = (self.LLM_PROVIDER or "").lower().strip()
        cloud_llm_providers = {"openai", "openrouter", "groq", "anthropic", "gemini"}

        if llm_provider in cloud_llm_providers:
            active_key = (self.LLM_API_KEY or "").strip() or (self.OPENAI_API_KEY or "").strip()
            if not active_key:
                raise ValueError(
                    f"CRITICAL CONFIG ERROR: LLM_PROVIDER is set to '{self.LLM_PROVIDER}', "
                    "which requires an API key. Please provide 'LLM_API_KEY' (or 'OPENAI_API_KEY') in your .env file."
                )

        # 3. Validate Embedding Secret conditionally
        emb_provider = (self.EMBEDDING_PROVIDER or "").lower().strip()
        cloud_emb_providers = {"openai", "cloud", "gemini"}

        if emb_provider in cloud_emb_providers:
            active_key = (self.LLM_API_KEY or "").strip() or (self.OPENAI_API_KEY or "").strip()
            if not active_key:
                raise ValueError(
                    f"CRITICAL CONFIG ERROR: EMBEDDING_PROVIDER is set to '{self.EMBEDDING_PROVIDER}', "
                    "which requires an API key. Please provide 'LLM_API_KEY' (or 'OPENAI_API_KEY') in your .env file."
                )

        return self

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE), env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


settings = Settings()
