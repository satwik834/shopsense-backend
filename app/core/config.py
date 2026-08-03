from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ShopSense Analytics Platform"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./shopsense.db"

    # JWT Authentication Settings
    SECRET_KEY: str = "shopsense_secret_jwt_key_for_vendor_approval_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day expiration

    class Config:
        case_sensitive = True

settings = Settings()
