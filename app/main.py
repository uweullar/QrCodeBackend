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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,  # берём из .env / переменных Render
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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