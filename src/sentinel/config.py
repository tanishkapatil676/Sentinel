from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Sentinel", description="Application name")
    environment: str = Field(default="development", description="Environment mode")
    log_level: str = Field(default="INFO", description="Logging level")
    host: str = Field(default="0.0.0.0", description="API Host")
    port: int = Field(default=8000, description="API Port")

    database_url: str = Field(
        default="postgresql+asyncpg://sentinel:sentinel_secret@localhost:5432/sentinel_db",
        description="PostgreSQL async database URL",
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0", description="Redis broker URL"
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
