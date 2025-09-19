from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "mental-health-assistant"

    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "mental_health"

    # JWT
    JWT_SECRET_KEY: str = "CHANGE_ME"  # override in .env
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24h

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # AI model
    HF_MODEL_NAME: str = "j-hartmann/emotion-english-distilroberta-base"

    # Translation
    USE_TR_EN_TRANSLATION: bool = True
    HF_TR_EN_MODEL: str = "Helsinki-NLP/opus-mt-tr-en"

    # Spotify API (Client Credentials)
    SPOTIFY_CLIENT_ID: str | None = None
    SPOTIFY_CLIENT_SECRET: str | None = None
    SPOTIFY_MARKET: str = "TR"  # default market
    SPOTIFY_REDIRECT_URI: str | None = None  # optional; not needed for client credentials

settings = Settings()
