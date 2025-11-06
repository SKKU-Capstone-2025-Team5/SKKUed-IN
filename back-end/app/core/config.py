from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "SKKUed-IN"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your_super_secret_key_here"
<<<<<<< HEAD
    DATABASE_URL: str = f"sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'test.db')}"
    
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    BASE_URL: str = "http://127.0.0.1:8000" # Add this line

    # Email
    MAIL_USERNAME: str | None = None
    MAIL_PASSWORD: str | None = None
    MAIL_FROM: str | None = None
    MAIL_PORT: int | None = None
    MAIL_SERVER: str | None = None
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False

    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
