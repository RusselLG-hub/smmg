from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/ssmg"

    # JWT
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_PUBLIC_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = ""
    MINIO_SECRET_KEY: str = ""
    MINIO_BUCKET: str = "ssmg"
    MINIO_SECURE: bool = False

    # Resend
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = ""

    # AI Configuration
    AI_GOOGLE_API_KEY: str = ""
    AI_MODEL: str = "gemini-3.1-flash-lite"
    AI_TEMPERATURE: float = 0.3
    AI_MAX_OUTPUT_TOKENS: int = 1000
    AI_REQUEST_TIMEOUT_SECONDS: int = 30
    AI_HISTORY_MESSAGE_LIMIT: int = 10

    # Admin Seeding
    ADMIN_EMAIL: str = ""
    ADMIN_PASSWORD: str = ""
    ADMIN_NAME: str = ""

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    @property
    def database_url(self) -> str:
        if Path("/.dockerenv").exists():
            # PostgreSQL runs in a separate container and is reachable through
            # the shared service name, not through the backend's localhost.
            return self.DATABASE_URL.replace("@localhost:", "@postgres:", 1)
        return self.DATABASE_URL.replace("@postgres:", "@localhost:", 1)

    @property
    def minio_endpoint(self) -> str:
        if Path("/.dockerenv").exists():
            return self.MINIO_ENDPOINT
        return self.MINIO_ENDPOINT.replace("minio:", "localhost:", 1)

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
