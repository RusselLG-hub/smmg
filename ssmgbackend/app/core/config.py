from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ssmg"

    # JWT
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "ssmg"
    MINIO_SECURE: bool = False

    # Resend
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "noreply@example.com"

    # AI Configuration
    AI_GOOGLE_API_KEY: str = ""
    AI_MODEL: str = "gemini-2.5-flash"
    AI_TEMPERATURE: float = 0.3
    AI_MAX_OUTPUT_TOKENS: int = 1000
    AI_REQUEST_TIMEOUT_SECONDS: int = 30
    AI_HISTORY_MESSAGE_LIMIT: int = 10

    # Admin Seeding
    ADMIN_EMAIL: str = "admin@ssmg.local"
    ADMIN_PASSWORD: str = "AdminPassword123!"
    ADMIN_NAME: str = "System Admin"

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
