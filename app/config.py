# app/config.py — Application configuration
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./guest_services_full.db"  # Override with DATABASE_URL
    debug: bool = True  # SQL echo, etc.
    secret_key: str = "dev-secret-change-in-prod"  # For session encryption; set in prod


settings = Settings()
