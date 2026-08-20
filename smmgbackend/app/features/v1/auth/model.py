from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.helpers.ulid import generate_ulid


class VerificationCode(Base):
    __tablename__ = "verification_codes"

    id: Mapped[str] = mapped_column(
        String(26), primary_key=True, default=generate_ulid
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    purpose: Mapped[str] = mapped_column(
        String(50), nullable=False, default="email_verification"
    )
    code_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_consumed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
