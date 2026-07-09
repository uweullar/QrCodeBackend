import datetime
import hashlib
import jwt
from app.core.config import settings
from passlib.context import CryptContext
import bcrypt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def hash_password(password: str) -> str:
    # Переводим строку в байты
    password_bytes = password.encode('utf-8')
    # Генерируем соль
    salt = bcrypt.gensalt()
    # Хешируем и декодируем обратно в строку для сохранения в БД
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Переводим обе строки в байты для проверки
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


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

