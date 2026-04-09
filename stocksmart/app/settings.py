from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    ALLOW_ORIGINS: List[str] = ["http://localhost:8000"]


settings = Settings()