from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    demo_mode: bool = True
    app_env: str = "development"
    cors_origins: str = "http://localhost:3000"

    groq_api_key: str = ""
    groq_reasoning_model: str = "openai/gpt-oss-120b"
    groq_fast_model: str = "qwen/qwen3-32b"

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"

    hindsight_url: str = "http://localhost:8888"
    hindsight_bank_id: str = "verichron-compliance"

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
