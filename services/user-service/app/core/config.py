from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "user-service"
    env: str = "development"
    host: str = "0.0.0.0"
    port: int = 8100

    database_url: str
    secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_audience: str | None = None

    redis_url: str
    kafka_bootstrap_service: str | None = None
    kafka_topic_user: str = "user-events"

    grpc_port: int = 50052

settings = Settings()