import datetime
import uuid
from typing import TYPE_CHECKING, List
from sqlalchemy import ForeignKey, String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


if TYPE_CHECKING:
    from app.models.Click import Click
    from app.models.Users import User


class QrCode(Base):
    __tablename__ = "qr_codes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    short_id: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    target_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    is_dynamic: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    # Обратные связи строками
    user: Mapped["User"] = relationship(back_populates="qr_codes")
    clicks: Mapped[List["Click"]] = relationship(
        "Click", back_populates="qr_code", cascade="all, delete-orphan"
    )
