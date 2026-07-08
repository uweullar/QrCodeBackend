from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse, HTMLResponse  # Добавили HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db  
from app.models.QrCode import QrCode
from app.models.Click import Click

router = APIRouter()

# Убрали response_class=RedirectResponse из декоратора, 
# так как теперь функция может возвращать и RedirectResponse, и HTMLResponse
@router.get("/r/{short_id}")
async def redirect_to_target(
    short_id: str, request: Request, db: AsyncSession = Depends(get_db)
):
    # 1. Ищем QR-код в базе по его короткому ID
    query = select(QrCode).where(QrCode.short_id == short_id)
    result = await db.execute(query)
    qr_code = result.scalar_one_or_none()

    # Если такого кода нет — отдаем 404
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="QR-код не найден или удален"
        )

    # 2. Собираем метаданные о клике
    user_agent = request.headers.get("user-agent", "Unknown")

    # 3. Создаем запись о клике (твоя аналитика успешно работает!)
    new_click = Click(
        qr_code_id=qr_code.id,
        user_agent=user_agent,  
    )

    db.add(new_click)
    await db.commit()

    # 4. Проверяем содержимое: ссылка это или обычный текст?
    clean_target = qr_code.target_url.strip()

    if clean_target.startswith(("http://", "https://")):
        # Если ссылка — редиректим как обычно
        return RedirectResponse(
            url=clean_target, status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )

    # Если это чистый текст — отдаем красивую карточку в цвет фронтенда
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Просмотр содержимого</title>
        <style>
            body {{
                background-color: #161213;
                color: #FFFFFF;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                padding: 20px;
                box-sizing: border-box;
            }}
            .card {{
                background: #231A1C;
                border: 1px solid rgba(255, 255, 255, 0.03);
                padding: 24px;
                border-radius: 16px;
                max-width: 420px;
                width: 100%;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                box-sizing: border-box;
            }}
            h1 {{
                color: #FFA3B1;
                font-size: 1.1rem;
                margin-top: 0;
                margin-bottom: 16px;
                font-weight: 600;
                letter-spacing: 0.5px;
            }}
            .text-box {{
                background: #322427;
                padding: 16px;
                border-radius: 12px;
                font-size: 0.95rem;
                line-height: 1.5;
                white-space: pre-wrap;
                word-break: break-word;
                color: #E5E5E5;
                border: 1px solid rgba(255,255,255,0.02);
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>📄 Содержимое QR-кода:</h1>
            <div class="text-box">{clean_target}</div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)