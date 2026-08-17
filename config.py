from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    shopify_shop: str
    shopify_access_token: str
    shopify_api_version: str = "2025-10"

    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None

    openai_api_key: Optional[str] = None

    poll_interval: int = 60
    daily_report_hour: int = 8

    # Agent toggles – flip these if you want to disable something
    enable_order_agent: bool = True
    enable_inventory_agent: bool = True
    enable_support_agent: bool = True
    enable_reporter: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
