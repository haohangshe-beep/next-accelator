from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    database_url: str
    secret: str
    token_ttl_days: int = 7


def load_settings() -> Settings:
    return Settings(
        database_url=os.environ.get("FTOS_DATABASE_URL", "sqlite:///./ftos.db"),
        secret=os.environ.get("FTOS_SECRET", "dev-ftos-secret-change-me-0123456789"),
    )


settings = load_settings()
