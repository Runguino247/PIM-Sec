from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Text,
    ForeignKey,
    DateTime,
    CheckConstraint,
    Index,
    func
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id",
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    token_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )

    user = relationship(
        "User",
        back_populates="refresh_tokens"
    )

    __table_args__ = (
        CheckConstraint(
            "expires_at > created_at",
            name="chk_refresh_token_dates"
        ),
        CheckConstraint(
            "revoked_at IS NULL OR revoked_at >= created_at",
            name="chk_refresh_token_revocation"
        ),
        CheckConstraint(
            "token_hash ~ '^[0-9a-fA-F]{64}$'",
            name="chk_refresh_token_hash_format"
        ),
        Index("idx_refresh_tokens_user_id", "user_id"),
        Index("idx_refresh_tokens_expires_at", "expires_at"),
        Index(
            "idx_refresh_tokens_active",
            "user_id",
            "expires_at",
            postgresql_where=(revoked_at.is_(None))
        ),
    ) 