from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    APP_NAME: str = "video-service"
    ENV: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8200

    DATABASE_URL: str
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str = "prostream-videos"
    MINIO_SECURE: bool = False

    REDIS_URL: str
    CELERY_BROKER: str
    CELERY_BACKEND: str

    KAFKA_BOOTSTRAP_SERVERS: str | None = None
    KAFKA_TOPIC_VIDEO: str = "video-events"

    SECRET_KEY: str
    JWT_AUDIENCE: str | None = None

    FFMPEG_PATH: str = "/usr/bin/ffmpeg"
    OUTPUT_HLS_PREFIX: str = "hls/"

    GRPC_PORT: int = 50053

settings = Settings()