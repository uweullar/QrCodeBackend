import datetime
import uuid
from typing import Optional, Dict
from pydantic import BaseModel, ConfigDict


class QrCodeCreate(BaseModel):
    target_url: str
    title: Optional[str] = None
    is_dynamic: bool = True


class QrCodeOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    short_id: str
    target_url: str
    title: Optional[str]
    is_dynamic: bool
    created_at: datetime.datetime
    scan_count: int = 0

    class Config:
        from_attributes = True


class QrCodeUpdate(BaseModel):
    target_url: Optional[str] = None  # Новая ссылка (необязательно)
    title: Optional[str] = None  # Новое название (необязательно)


class QrCodeStatsOut(BaseModel):
    total_clicks: int  # Общее количество переходов
    browsers_breakdown: Dict[str, int]  # Статистика по браузерам/девайсам
