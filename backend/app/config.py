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
    groq_fast_model: str = "openai/gpt-oss-120b"
    tenant_id: str = "acme"
    dev_role: str = "AUDITOR"
    dev_user: str = "demo-auditor"
    allow_hindsight_mock: bool = False

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"

    hindsight_url: str = "https://api.hindsight.vectorize.io"
    hindsight_api_key: str = ""
    hindsight_bank_id: str = "verichron-compliance"

    openclaw_enabled: bool = True
    openclaw_legacy_fallback: bool = False
    openclaw_gateway_url: str = "http://127.0.0.1:18789"
    openclaw_gateway_token: str = ""
    openclaw_agent: str = "openclaw/default"
    openclaw_model: str = "groq/openai/gpt-oss-120b"
    openclaw_timeout_s: float = 90.0
    openclaw_tool_token: str = ""

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
