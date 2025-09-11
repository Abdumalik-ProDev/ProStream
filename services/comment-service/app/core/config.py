from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    # General
    project_name: str = Field("comment-service", env="PROJECT_NAME")

    # Database
    db_user: str = Field(..., env="DB_USER")
    db_pass: str = Field(..., env="DB_PASS")
    db_host: str = Field(..., env="DB_HOST")
    db_port: int = Field(..., env="DB_PORT")
    db_name: str = Field(..., env="DB_NAME")

    # Redis
    redis_url: str = Field(..., env="REDIS_URL")

    # Kafka
    kafka_bootstrap_servers: str = Field(..., env="KAFKA_BOOTSTRAP_SERVERS")
    kafka_topic: str = Field("comments", env="KAFKA_TOPIC")

    # JWT
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")

    # gRPC
    grpc_server_port: int = Field(50054, env="GRPC_SERVER_PORT")

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def database_url(self) -> str:
        """Build the SQLAlchemy/Postgres URL dynamically"""
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_pass}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


# Cached singleton instance so every import shares one object
@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()