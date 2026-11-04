from datetime import datetime

from sqlalchemy import (
    BigInteger,
    String,
    Text,
    ForeignKey,
    DateTime,
    CheckConstraint,
    UniqueConstraint,
    Index,
    func
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    event_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "security_events.id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="NEW",
        server_default="NEW"
    )

    assigned_to: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        )
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )

    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    resolution_note: Mapped[str | None] = mapped_column(
        Text
    )

    event = relationship(
        "SecurityEvent",
        back_populates="alert"
    )

    assignee = relationship(
        "User",
        back_populates="assigned_alerts"
    )

    history = relationship(
        "AlertHistory",
        back_populates="alert"
    )

    __table_args__ = (
        UniqueConstraint(
            "event_id",
            name="uq_alert_event"
        ),

        CheckConstraint(
            "status IN ('NEW', 'ACKNOWLEDGED', 'RESOLVED')",
            name="chk_alert_status"
        ),

        CheckConstraint(
            """
            (
                status = 'NEW'
                AND acknowledged_at IS NULL
                AND resolved_at IS NULL
            )
            OR (
                status = 'ACKNOWLEDGED'
                AND acknowledged_at IS NOT NULL
                AND resolved_at IS NULL
            )
            OR (
                status = 'RESOLVED'
                AND acknowledged_at IS NOT NULL
                AND resolved_at IS NOT NULL
            )
            """,
            name="chk_alert_status_dates"
        ),

        CheckConstraint(
            """
            status <> 'RESOLVED'
            OR (
                resolution_note IS NOT NULL
                AND LENGTH(TRIM(resolution_note)) > 0
            )
            """,
            name="chk_alert_resolution_note"
        ),

        CheckConstraint(
            "acknowledged_at IS NULL OR acknowledged_at >= created_at",
            name="chk_alert_acknowledged_date"
        ),

        CheckConstraint(
            "resolved_at IS NULL OR resolved_at >= created_at",
            name="chk_alert_resolved_date"
        ),

        Index(
            "idx_alerts_status_created",
            "status",
            created_at.desc()
        ),

        Index("idx_alerts_assigned_to", "assigned_to"),
    )