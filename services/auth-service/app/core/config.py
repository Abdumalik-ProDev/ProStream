from pydantic import BaseSettings

class Settings(BaseSettings):

    APP_NAME: str = "auth-service"
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@auth-db:5432/auth_db"
    
    SECRET_KEY: str = "ProDevIsTheBestCEO,TeamLeadAndDeveloperInTheWorldWithoutAnyDoubt!"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    REDIS_URL: str = "redis://redis:6379/0"
    KAFKA_BOOTSTRAP: str = "kafka:9092"

    class Config:
        env_file = ".env"

settings = Settings()