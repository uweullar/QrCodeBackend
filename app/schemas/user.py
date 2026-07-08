import datetime
import uuid
from pydantic import BaseModel, ConfigDict


# Схема для получения данных при регистрации (то, что присылает фронтенд)
class UserCreate(BaseModel):
    email: str
    password: str


# Схема для возврата данных (то, что мы отдаем обратно, без пароля!)
class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    created_at: datetime.datetime

    # Настройка для автоматической конвертации моделей SQLAlchemy в Pydantic
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str
