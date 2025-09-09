import os
from functools import lru_cache
from pathlib import Path
from typing import Literal
from pydantic import AnyHttpUrl, Field, SecretStr, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


def _guess_env_file() -> str | None:
    explicit = os.getenv("NLBONE_ENV_FILE")
    if explicit:
        return explicit

    cwd_env = Path.cwd() / ".env"
    if cwd_env.exists():
        return str(cwd_env)

    for i in range(0, 8):
        p = Path.cwd().resolve().parents[i]
        f = p / ".env"
        if f.exists():
            return str(f)


def _is_production_env() -> bool:
    raw = os.getenv("NLBONE_ENV") or os.getenv("ENV") or os.getenv("ENVIRONMENT")
    if not raw:
        return False
    return raw.strip().lower() in {"prod", "production"}


class Settings(BaseSettings):
    # ---------------------------
    # App
    # ---------------------------
    PORT: int = 8000
    ENV: Literal["local", "dev", "staging", "prod"] = Field(default="local",
                                                            validation_alias=AliasChoices("NLBONE_ENV", "ENV",
                                                                                          "ENVIRONMENT"))
    DEBUG: bool = Field(default=False)
    LOG_LEVEL: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"] = Field(default="INFO")
    LOG_JSON: bool = Field(default=True)

    # ---------------------------
    # HTTP / Timeouts
    # ---------------------------
    HTTP_TIMEOUT_SECONDS: float = Field(default=10.0)

    # ---------------------------
    # Keycloak / Auth
    # ---------------------------
    KEYCLOAK_SERVER_URL: AnyHttpUrl = Field(default="https://keycloak.local/auth",
                                            validation_alias=AliasChoices("NLBONE_KEYCLOAK_SERVER_URL",
                                                                          "KEYCLOAK_SERVER_URL"))
    KEYCLOAK_REALM_NAME: str = Field(default="numberland",
                                     validation_alias=AliasChoices("NLBONE_KEYCLOAK_REALM_NAME", "KEYCLOAK_REALM_NAME"))
    KEYCLOAK_CLIENT_ID: str = Field(default="nlbone",
                                    validation_alias=AliasChoices("NLBONE_KEYCLOAK_CLIENT_ID", "KEYCLOAK_CLIENT_ID"))
    KEYCLOAK_CLIENT_SECRET: SecretStr = Field(default=SecretStr("dev-secret"),
                                              validation_alias=AliasChoices("NLBONE_KEYCLOAK_CLIENT_SECRET",
                                                                            "KEYCLOAK_CLIENT_SECRET"))

    # ---------------------------
    # Database
    # ---------------------------
    POSTGRES_DB_DSN: str = Field(default="postgresql+asyncpg://user:pass@localhost:5432/nlbone",
                                 validation_alias=AliasChoices("NLBONE_POSTGRES_DB_DSN",
                                                               "POSTGRES_DB_DSN", "DATABASE_URL", "DB_DSN"))
    DB_ECHO: bool = Field(default=False)
    DB_POOL_SIZE: int = Field(default=5)
    DB_MAX_OVERFLOW: int = Field(default=10)

    # ---------------------------
    # Messaging / Cache
    # ---------------------------
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    # --- Event bus / Outbox ---
    EVENT_BUS_BACKEND: Literal["inmemory"] = Field(default="inmemory")
    OUTBOX_ENABLED: bool = Field(default=False)
    OUTBOX_POLL_INTERVAL_MS: int = Field(default=500)

    # ---------------------------
    # UPLOADCHI
    # ---------------------------
    UPLOADCHI_BASE_URL: AnyHttpUrl = Field(default="https://uploadchi.numberland.ir/v1/files")
    UPLOADCHI_TOKEN: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("NLBONE_UPLOADCHI_TOKEN", "UPLOADCHI_TOKEN"),
    )

    model_config = SettingsConfigDict(
        env_prefix="NLBONE_",
        env_file=None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @classmethod
    def load(cls, env_file: str | None = None) -> "Settings":
        if _is_production_env():
            return cls()
        return cls(_env_file=env_file or _guess_env_file())


@lru_cache(maxsize=4)
def get_settings(env_file: str | None = None) -> Settings:
    """
    Cached settings for fast access across the app.
    Usage:
        from nlbone.config.settings import get_settings
        settings = get_settings()
    """
    return Settings.load(env_file)
