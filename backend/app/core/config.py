"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "isekai-wanderer"
    app_env: str = "development"
    app_version: str = "1.0.0"
    log_level: str = "info"

    # Server
    backend_port: int = 8000

    # Database
    database_url: str = "postgresql+asyncpg://isekai:isekai_password@localhost:5432/isekai"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret: str = "change-me-local-only"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440  # 24 hours (CEO P0 fix)
    jwt_refresh_token_expire_days: int = 30

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:8081,http://127.0.0.1:8081,http://47.107.174.176:8081"

    # Rate limiting
    api_rate_limit: int = 60  # requests per minute
    llm_rate_limit: int = 10  # requests per minute

    # LLM
    llm_provider: str = "thoushub"  # "mock" | "openai" | "thoushub"
    llm_base_url: str = "https://www.thoushub.com/v1"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_default_model: str = "qwen3.7-plus"
    openai_api_key: str = ""  # empty → falls back to mock
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    # Email
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@isekai-wanderer.local"

    # TTS (CR-005: Aliyun CosyVoice)
    tts_enabled: bool = True
    tts_provider: str = "aliyun"
    tts_api_key: str = "sk-6Nig_1ndlOU3eaIVK2dDHQ"
    tts_base_url: str = "http://47.106.104.209/v1"
    tts_model: str = "cosyvoice-v3.5-flash"
    tts_voice_flash: str = "cosyvoice-v3.5-flash-hlthflash-dbffd19fadfe4e4ba9dee752a0456932"
    tts_voice_plus: str = "cosyvoice-v3.5-plus-hlthplus-174ab62afc7f413ca455dfc5f5d08667"
    tts_voice_output_dir: str = "/app/static/voices"

    # CR-027: Token Budget Configuration
    token_budget_total: int = 2300  # Total token budget for 6-layer prompt
    token_budget_l1_global: int = 200  # Global rules layer
    token_budget_l2_world: int = 500  # World knowledge (Lorebook)
    token_budget_l3_npc: int = 300  # NPC profile (character)
    token_budget_l4_memory: int = 800  # Memory recall
    token_budget_l5_narrative: int = 300  # Narrative director
    token_budget_l6_player: int = 200  # Player input
    token_encoding: str = "cl100k_base"  # tiktoken encoding model

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
