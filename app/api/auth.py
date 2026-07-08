from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.Users import User
from app.schemas.user import UserCreate, UserOut
from app.core.security import hash_password
from app.schemas.user import (
    UserCreate,
    UserOut,
    Token,
)  # Добавь Token в импорт вверху файла
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)  # Обнови импорт


router = APIRouter(prefix="/auth", tags=["Auth (Авторизация)"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(user_date: UserCreate, db: AsyncSession = Depends(get_db)):

    query = select(User).where(User.email == user_date.email)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует!",
        )

    new_user = User(
        email=user_date.email, password_hash=hash_password(user_date.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
async def login_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # 1. Ищем пользователя по email
    query = select(User).where(User.email == user_data.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    # 2. Если не нашли или пароль не совпал — бьем по рукам
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль!",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Генерируем токен, зашивая туда ID пользователя
    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}
