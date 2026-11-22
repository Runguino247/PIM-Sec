from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Integer,
    String,
    ForeignKey,
    DateTime,
    CheckConstraint,
    UniqueConstraint,
    Index,
    ForeignKeyConstraint,
    func
)

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class IntegrityScan(Base):
    __tablename__ = "integrity_scans"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
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

    baseline_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "baselines.id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    initiated_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        )
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="RUNNING",
        server_default="RUNNING"
    )

    files_checked: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )

    summary_json: Mapped[dict | None] = mapped_column(
        JSONB
    )

    repository = relationship(
        "Repository",
        back_populates="scans",
        foreign_keys=[repository_id]
    )

    # Relación de vuelta
    baseline = relationship(
        "Baseline", 
        back_populates="scans",
        foreign_keys=[baseline_id]  # <--- También es buena práctica especificarlo aquí
    )

    initiator = relationship(
        "User",
        back_populates="initiated_scans"
    )

    results = relationship(
        "ScanResult",
        back_populates="scan"
    )

    security_events = relationship(
        "SecurityEvent",
        back_populates="scan"
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["baseline_id", "repository_id"],
            ["baselines.id", "baselines.repository_id"],
            name="fk_scan_baseline_same_repo",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),

        UniqueConstraint(
            "id",
            "repository_id",
            name="uq_scan_id_repository"
        ),

        CheckConstraint(
            "status IN ('RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED')",
            name="chk_scan_status"
        ),

        CheckConstraint(
            "files_checked >= 0",
            name="chk_scan_files_checked"
        ),

        CheckConstraint(
            "finished_at IS NULL OR finished_at >= started_at",
            name="chk_scan_dates"
        ),

        Index(
            "idx_integrity_scans_repository_started",
            "repository_id",
            started_at.desc()
        ),

        Index("idx_integrity_scans_baseline_id", "baseline_id"),

        Index("idx_integrity_scans_initiated_by", "initiated_by"),

        Index(
            "idx_scans_status_started",
            "status",
            started_at.desc()
        ),
    )