import secrets
import string
from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.db.session import get_db
from app.models.QrCode import QrCode
from app.models.Users import User
from app.models.Click import Click
from app.schemas.qr import QrCodeCreate, QrCodeOut, QrCodeStatsOut, QrCodeUpdate
from app.api.deps import get_current_user

router = APIRouter(prefix="/qr", tags=["QR Codes (Управление QR-кодами)"])


def generate_short_id(length: int = 6) -> str:
    """Генерирует случайный уникальный суффикс для короткой ссылки"""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


@router.post("/create", response_model=QrCodeOut, status_code=status.HTTP_201_CREATED)
async def create_qr(
    qr_data: QrCodeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Роут теперь защищен токеном!
):
    # Генерируем уникальный short_id и проверяем, нет ли дубликата в БД
    while True:
        short_id = generate_short_id()
        query = select(QrCode).where(QrCode.short_id == short_id)
        result = await db.execute(query)
        if not result.scalar_one_or_none():
            break

    # Создаем запись в БД
    new_qr = QrCode(
        user_id=current_user.id,
        short_id=short_id,
        target_url=qr_data.target_url,
        title=qr_data.title,
        is_dynamic=qr_data.is_dynamic,
    )

    db.add(new_qr)
    await db.commit()
    await db.refresh(new_qr)

    return new_qr


@router.get("/my", response_model=list[QrCodeOut])
async def get_my_qrs(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Получить список всех QR-кодов текущего пользователя вместе с количеством переходов"""
    
    # Делаем LEFT JOIN с таблицей Click и считаем количество совпадений по ID кодов
    query = (
        select(QrCode, func.count(Click.id).label("scan_count"))
        .outerjoin(Click, QrCode.id == Click.qr_code_id)
        .where(QrCode.user_id == current_user.id)
        .group_by(QrCode.id)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    # Собираем объекты обратно, динамически подмешивая посчитанный scan_count
    qrs_with_stats = []
    for qr, scan_count in rows:
        qr.scan_count = scan_count  # Присваиваем количество кликов объекту модели
        qrs_with_stats.append(qr)
        
    return qrs_with_stats


@router.patch("/{qr_id}", response_model=QrCodeOut)
async def update_qr_code(
    qr_id: uuid.UUID,
    data: QrCodeUpdate,
    db: AsyncSession = Depends(get_db),  # Твоя функция сессии БД
    current_user: User = Depends(get_current_user),  # Зависимость авторизации
):
    """
    Обновление динамического QR-кода (изменение целевой ссылки или названия)
    """
    # 1. Ищем QR-код по ID И проверяем, что он принадлежит текущему юзеру
    query = select(QrCode).where(QrCode.id == qr_id, QrCode.user_id == current_user.id)
    result = await db.execute(query)
    qr_code = result.scalar_one_or_none()

    # Если код не найден (или принадлежит другому юзеру), отдаем 404 из соображений безопасности
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR-код не найден или у вас нет прав на его изменение",
        )

    # 2. Обновляем только те поля, которые пользователь передал в JSON
    if data.target_url is not None:
        qr_code.target_url = data.target_url
    if data.title is not None:
        qr_code.title = data.title

    # 3. Сохраняем изменения в базу данных
    await db.commit()
    await db.refresh(qr_code)

    return qr_code


@router.get("/{qr_id}/stats", response_model=QrCodeStatsOut)
async def get_qr_code_stats(
    qr_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получение статистики кликов по конкретному QR-коду
    """
    # 1. Проверяем, существует ли код и принадлежит ли он текущему юзеру
    qr_query = select(QrCode).where(
        QrCode.id == qr_id, QrCode.user_id == current_user.id
    )
    qr_result = await db.execute(qr_query)
    qr_code = qr_result.scalar_one_or_none()

    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR-код не найден или у вас нет прав на просмотр статистики",
        )

    # 2. Считаем общее количество кликов
    total_clicks_query = select(func.count(Click.id)).where(Click.qr_code_id == qr_id)
    total_clicks_result = await db.execute(total_clicks_query)
    total_clicks = total_clicks_result.scalar() or 0

    # 3. Группируем клики по User-Agent (устройствам), чтобы сделать разбивку
    breakdown_query = (
        select(Click.user_agent, func.count(Click.id))
        .where(Click.qr_code_id == qr_id)
        .group_by(Click.user_agent)
    )
    breakdown_result = await db.execute(breakdown_query)

    # Превращаем результат группировки в красивый словарь Python {"Браузер": кол-во}
    browsers_breakdown = {row[0]: row[1] for row in breakdown_result.all()}

    # 4. Возвращаем агрегированные данные
    return QrCodeStatsOut(
        total_clicks=total_clicks, browsers_breakdown=browsers_breakdown
    )
