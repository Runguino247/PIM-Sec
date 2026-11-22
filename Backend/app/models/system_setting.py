from datetime import datetime

from sqlalchemy import (
    BigInteger,
    String,
    Text,
    ForeignKey,
    DateTime,
    Index,
    func
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SystemSetting(Base):
    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    setting_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )

    setting_value: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text
    )

    updated_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        )
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    updater = relationship(
        "User",
        foreign_keys=[updated_by]
    )

    __table_args__ = (
        Index(
            "idx_system_settings_updated_by",
            "updated_by"
        ),
    )