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

from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    actor_user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        )
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    resource_type: Mapped[str] = mapped_column(
        String(80),
        nullable=False
    )

    resource_id: Mapped[str | None] = mapped_column(
        String(100)
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )

    source_ip: Mapped[str | None] = mapped_column(
        INET
    )

    outcome: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    details_json: Mapped[dict | None] = mapped_column(
        # PostgreSQL JSONB
        __import__(
            "sqlalchemy.dialects.postgresql",
            fromlist=["JSONB"]
        ).JSONB
    )

    previous_log_hash: Mapped[str | None] = mapped_column(
        String(64)
    )

    log_hash: Mapped[str | None] = mapped_column(
        String(64)
    )

    actor = relationship(
        "User",
        back_populates="audit_logs"
    )

    __table_args__ = (
        CheckConstraint(
            "outcome IN ('SUCCESS', 'FAILURE', 'DENIED')",
            name="chk_audit_outcome"
        ),

        CheckConstraint(
            "previous_log_hash IS NULL OR previous_log_hash ~ '^[0-9a-fA-F]{64}$'",
            name="chk_audit_previous_hash"
        ),

        CheckConstraint(
            "log_hash IS NULL OR log_hash ~ '^[0-9a-fA-F]{64}$'",
            name="chk_audit_log_hash"
        ),

        Index(
            "idx_audit_logs_occurred_at",
            occurred_at.desc()
        ),

        Index("idx_audit_logs_actor", "actor_user_id"),

        Index(
            "idx_audit_logs_resource",
            "resource_type",
            "resource_id"
        ),
    )