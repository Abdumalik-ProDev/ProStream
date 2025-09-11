from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "comment-service"
    ENV: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8300

    DATABASE_URL: str
    REDIS_URL: str
    KAFKA_BOOTSTRAP_SERVERS: str | None = None
    KAFKA_TOPIC_COMMENTS: str = "comments"

    AUTH_SERVICE_JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    GRPC_PORT: int = 50054

    class Config:
        env_file = ".env"

settings = Settings()