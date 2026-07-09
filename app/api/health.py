from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

router = APIRouter(tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Лёгкий пинг без обращения к БД.
    Именно этот эндпоинт указывайте в cron-job.org / UptimeRobot —
    он не расходует лимит соединений Supabase на free tier
    и держит Render-инстанс "тёплым", не давая ему уснуть.
    """
    return {"status": "ok"}


@router.get("/health/db")
async def health_check_db(db: AsyncSession = Depends(get_db)):
    """
    Полная проверка — реально ли бэкенд может достучаться до Supabase Postgres.
    Использовать вручную для диагностики, НЕ для автоматического пинга каждые
    несколько минут (тратит соединение из пула на каждый вызов).
    """
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "database": "unreachable",
                "detail": str(e),
            },
        )