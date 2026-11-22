from datetime import datetime

from sqlalchemy import (
    BigInteger,
    String,
    ForeignKey,
    ForeignKeyConstraint,
    DateTime,
    CheckConstraint,
    Index,
    func
)

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    scan_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

    repository_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "repositories.id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    asset_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "assets.id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        )
    )

    scan_result_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "scan_results.id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        )
    )

    event_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    expected_sha256: Mapped[str | None] = mapped_column(
        String(64)
    )

    actual_sha256: Mapped[str | None] = mapped_column(
        String(64)
    )

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )

    actor_user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        )
    )

    details_json: Mapped[dict | None] = mapped_column(
        JSONB
    )

    scan = relationship(
        "IntegrityScan",
        back_populates="security_events",
        foreign_keys=[scan_id, repository_id]
    )

    asset = relationship(
        "Asset",
        back_populates="security_events"
    )

    scan_result = relationship(
        "ScanResult",
        foreign_keys=[scan_result_id]
    )

    actor = relationship(
        "User",
        foreign_keys=[actor_user_id]
    )

    alert = relationship(
        "Alert",
        back_populates="event",
        uselist=False
    )

    change_links = relationship(
        "ChangeEventLink",
        back_populates="event"
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["scan_id", "repository_id"],
            ["integrity_scans.id", "integrity_scans.repository_id"],
            name="fk_event_scan_same_repo",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),

        CheckConstraint(
            """
            event_type IN (
                'FILE_MODIFIED',
                'FILE_DELETED',
                'FILE_NEW',
                'FILE_REPLACED',
                'FILE_CHECK_ERROR',
                'BASELINE_HMAC_INVALID',
                'UNAUTHORIZED_APPROVAL_ATTEMPT',
                'SCAN_STARTED',
                'SCAN_COMPLETED'
            )
            """,
            name="chk_event_type"
        ),

        CheckConstraint(
            "severity IN ('INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL')",
            name="chk_security_severity"
        ),

        CheckConstraint(
            "expected_sha256 IS NULL OR expected_sha256 ~ '^[0-9a-fA-F]{64}$'",
            name="chk_event_expected_sha256"
        ),

        CheckConstraint(
            "actual_sha256 IS NULL OR actual_sha256 ~ '^[0-9a-fA-F]{64}$'",
            name="chk_event_actual_sha256"
        ),

        Index(
            "idx_security_events_repository_detected",
            "repository_id",
            detected_at.desc()
        ),

        Index("idx_security_events_scan_id", "scan_id"),
        Index("idx_security_events_asset_id", "asset_id"),
        Index("idx_security_events_actor", "actor_user_id"),
    )