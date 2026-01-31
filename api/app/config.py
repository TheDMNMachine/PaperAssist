"""Application configuration via pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "PaperAssist API"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://paperassist:paperassist@localhost:5432/paperassist"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
