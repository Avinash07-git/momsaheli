"""Centralized settings loaded from .env."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- LLM cascade ---
    TOKEN_ROUTER_API_KEY: str = ""
    # Qwen comes tomorrow
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    QWEN_MODEL: str = "qwen-plus"
    # Gemini (free) is our active LLM today
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    ZAI_API_KEY: str = ""
    ZAI_BASE_URL: str = "https://api.z.ai/api/paas/v4"
    ZAI_MODEL: str = "glm-4-plus"

    # --- Web intel ---
    BRIGHT_DATA_API_TOKEN: str = ""
    BRIGHT_DATA_ZONE: str = ""
    # Tavily (free) is our active web-search engine today; swap to Bright Data when zone is set up
    TAVILY_API_KEY: str = ""
    ACTIONBOOK_API_KEY: str = ""
    ACTIONBOOK_WORKSPACE_ID: str = ""

    # --- Memory + backend ---
    EVERMIND_API_KEY: str = ""
    EVERMIND_NAMESPACE: str = "moms-saheli"
    BUTTERBASE_API_KEY: str = ""
    BUTTERBASE_PROJECT_ID: str = ""

    # --- Orchestration ---
    AGENTFIELD_API_KEY: str = ""
    AGENTFIELD_PROJECT: str = "moms-saheli"
    AGENTFIELD_CONTROL_PLANE_URL: str = "http://localhost:8080"

    # --- Runtime ---
    APP_BASE_URL: str = "http://localhost:8000"
    USE_FIXTURES: bool = True
    LOG_LEVEL: str = "INFO"

    @property
    def fixtures_dir(self) -> Path:
        return Path(__file__).resolve().parent / "fixtures"

    @property
    def cached_scrapes_dir(self) -> Path:
        return self.fixtures_dir / "cached_scrapes"

    @property
    def templates_dir(self) -> Path:
        return Path(__file__).resolve().parent / "templates"


settings = Settings()
