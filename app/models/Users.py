import datetime
import uuid
from sqlalchemy import String, DateTime
from typing import TYPE_CHECKING, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.QrCode import QrCode


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.now,  # Исправлено: теперь это функция, а не класс
    )

    # ВАЖНО: имя переменной теперь строго qr_codes (с подчеркиванием!)
    qr_codes: Mapped[List["QrCode"]] = relationship(back_populates="user")
