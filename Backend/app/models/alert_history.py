from datetime import datetime

from sqlalchemy import (
    BigInteger,
    String,
    Text,
    ForeignKey,
    DateTime,
    CheckConstraint,
    Index,
    func
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AlertHistory(Base):
    __tablename__ = "alert_history"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    alert_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "alerts.id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    changed_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        )
    )

    previous_status: Mapped[str | None] = mapped_column(
        String(20)
    )

    new_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    note: Mapped[str | None] = mapped_column(
        Text
    )

    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )

    alert = relationship(
        "Alert",
        back_populates="history"
    )

    changed_by_user = relationship(
        "User",
        foreign_keys=[changed_by]
    )

    __table_args__ = (
        CheckConstraint(
            "new_status IN ('NEW', 'ACKNOWLEDGED', 'RESOLVED')",
            name="chk_alert_history_new_status"
        ),

        CheckConstraint(
            """
            previous_status IS NULL
            OR previous_status IN ('NEW', 'ACKNOWLEDGED', 'RESOLVED')
            """,
            name="chk_alert_history_previous_status"
        ),

        CheckConstraint(
            "previous_status IS NULL OR previous_status <> new_status",
            name="chk_alert_history_transition"
        ),

        Index(
            "idx_alert_history_alert_changed",
            "alert_id",
            changed_at.desc()
        ),
    )