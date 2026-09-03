from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(
        default="postgresql://netopier:netopier@127.0.0.1:5432/netopier",
        validation_alias=AliasChoices("NETOPIER_DATABASE_URL", "DATABASE_URL"),
    )
    miniflux_base_url: str = "http://127.0.0.1:8088"
    miniflux_admin_username: str = "netopier"
    miniflux_admin_password: str = ""
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dimensions: int = 384
    embedding_cache_dir: str = "/var/cache/netopier/models"
    story_similarity_threshold: float = 0.83
    story_window_hours: int = 72
    reconciliation_batch_size: int = 20
    worker_interval_seconds: int = 300


@lru_cache
def get_settings() -> Settings:
    return Settings()
