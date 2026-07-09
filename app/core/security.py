import datetime
import hashlib
import jwt
from app.core.config import settings
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: datetime.timedelta = None) -> str:
    """Генерирует защищенный JWT-токен доступа"""
    to_encode = data.copy()

    # Задаем время жизни токена (например, 1 день, если не указано иное)
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            days=1
        )

    to_encode.update({"exp": expire})
    # Кодируем токен с помощью нашего SECRET_KEY из .env
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

