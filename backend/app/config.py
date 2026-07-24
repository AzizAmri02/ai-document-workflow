from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "sqlite:///./app.db"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_hours: int = 24
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()