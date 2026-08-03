import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "ShopSense Analytics Platform")
    VERSION: str = os.getenv("VERSION", "0.1.0")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./shopsense.db")

    class Config:
        case_sensitive = True

settings = Settings()
