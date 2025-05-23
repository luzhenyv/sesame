from pydantic_settings import BaseSettings
from typing import Optional

from pathlib import Path


class Settings(BaseSettings):
    PROJECT_NAME: str = "Sesame Health"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # JWT settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SECRET_KEY: str = "your-secret-key"  # Change this in production!
    ALGORITHM: str = "HS256"  # Algorithm for JWT token generation

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "sesame_health"
    POSTGRES_PORT: str = "5432"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # File upload settings
    ROOT_DIR: str = str(Path(__file__).parent.parent.parent)
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png"]
    ALLOWED_DOC_TYPES: list = ["application/pdf"]

    @property
    def get_database_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
