from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MTI_", case_sensitive=False)

    db_url: str = "sqlite+aiosqlite:///./mti.db"
    object_store_dir: Path = Path("./mti_object_store")

    signing_key_path: Path = Path("./mti_signing_key.ed25519")
    signing_pubkey_path: Path = Path("./mti_signing_key.pub")

    analysis_version: str = "2025.12.0"


settings = Settings()

