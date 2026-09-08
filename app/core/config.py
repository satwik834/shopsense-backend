from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ShopSense Analytics Platform"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./shopsense.db"

    # JWT Authentication Settings
    SECRET_KEY: str = "shopsense_secret_jwt_key_for_vendor_approval_2026"
    ALGORITHM: str = "HS256"
    
    # Token Durations
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Short-lived access token (15 mins)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7    # Long-lived refresh token (7 days)

    # HTTP-Only Cookie Configuration
    ACCESS_COOKIE_NAME: str = "access_token"
    REFRESH_COOKIE_NAME: str = "refresh_token"
    COOKIE_SECURE: bool = False  # False for local HTTP development
    COOKIE_SAMESITE: str = "lax"

    # AI & Gemini API Settings
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-3.6-flash"

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
