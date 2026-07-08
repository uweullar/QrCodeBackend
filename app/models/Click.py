import datetime
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, DateTime, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


if TYPE_CHECKING:
    from app.models.QrCode import QrCode


class Click(Base):
    __tablename__ = "clicks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    qr_code_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("qr_codes.id", ondelete="CASCADE"), nullable=False
    )
    clicked_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )
    user_agent: Mapped[str] = mapped_column(String(512), nullable=True)

    qr_code: Mapped["QrCode"] = relationship("QrCode", back_populates="clicks")
