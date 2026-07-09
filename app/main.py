from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine
from app.models import Base
from app.api.redirect import router as redirect_router
from app.api.auth import router as auth_router
from app.api.qr import router as qr_router
from app.api.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="QR Code Service API", lifespan=lifespan)

# Список разрешенных адресов
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://qr-code-frontend-tau.vercel.app",  # Твой фронтенд на Vercel
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Разрешаем запросы с этих сайтов
    allow_credentials=True,
    allow_methods=["*"],    # Разрешаем любые методы (GET, POST и т.д.)
    allow_headers=["*"],    # Разрешаем любые заголовки
)

app.include_router(auth_router, prefix="/api")
app.include_router(qr_router, prefix="/api")
app.include_router(redirect_router)
app.include_router(health_router)


@app.get("/")
def read_root():
    return {
        "status": "alive",
        "message": "Бэкенд QR-сервиса успешно запущен и подключен к БД!",
    }