from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# Создаем асинхронный движок для работы с PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Логирует все SQL-запросы в консоль
)

# Создаем фабрику сессий
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Функция-зависимость для роутов FastAPI
async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()