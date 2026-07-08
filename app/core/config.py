import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Вычисляем путь к папке backend
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

# НАДЖОРНЫЙ ПРИНТ: Выведет точный путь в консоль перед падением
print("\n" + "="*50)
print(f"🔍 Я ищу файл .env по этому пути:\n👉 {ENV_PATH}")
print(f"📋 Файл реально существует?: {'✅ ДА' if ENV_PATH.exists() else '❌ НЕТ'}")
print("="*50 + "\n")

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    
    # Проставляем дефолты. Если этих строк нет в .env, Pydantic возьмет значения отсюда:
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 дней
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    SERVER_HOST_URL: str = "http://127.0.0.1:8000"

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding="utf-8",
        env_case_sensitive=False,
        extra="ignore" 
    )

settings = Settings()