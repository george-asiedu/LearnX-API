from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    ENVIRONMENT: str = 'development'
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    JWT_KEY: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    UPSTASH_REDIS_REST_URL: str
    UPSTASH_REDIS_REST_TOKEN: str
    SENDGRID_API_KEY: str
    SENDER_EMAIL: str

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()