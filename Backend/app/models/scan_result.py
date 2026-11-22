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


class ScanResult(Base):
    __tablename__ = "scan_results"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    scan_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "integrity_scans.id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    baseline_item_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "baseline_items.id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        )
    )

    asset_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "assets.id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        )
    )

    relative_path: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    expected_sha256: Mapped[str | None] = mapped_column(
        String(64)
    )

    actual_sha256: Mapped[str | None] = mapped_column(
        String(64)
    )

    actual_file_identity: Mapped[str | None] = mapped_column(
        Text
    )

    result: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )

    error_message: Mapped[str | None] = mapped_column(
        Text
    )

    scan = relationship(
        "IntegrityScan",
        back_populates="results"
    )

    baseline_item = relationship(
        "BaselineItem",
        back_populates="scan_results"
    )

    asset = relationship(
        "Asset",
        back_populates="scan_results"
    )

    __table_args__ = (
        UniqueConstraint(
            "scan_id",
            "relative_path",
            name="uq_scan_result_path"
        ),

        CheckConstraint(
            """
            result IN (
                'INTACT', 'MODIFIED', 'DELETED',
                'NEW', 'REPLACED', 'ERROR', 'UNVERIFIED'
            )
            """,
            name="chk_scan_result_type"
        ),

        CheckConstraint(
            "expected_sha256 IS NULL OR expected_sha256 ~ '^[0-9a-fA-F]{64}$'",
            name="chk_scan_expected_sha256"
        ),

        CheckConstraint(
            "actual_sha256 IS NULL OR actual_sha256 ~ '^[0-9a-fA-F]{64}$'",
            name="chk_scan_actual_sha256"
        ),

        CheckConstraint(
            """
            (
                result = 'INTACT'
                AND expected_sha256 IS NOT NULL
                AND actual_sha256 IS NOT NULL
                AND expected_sha256 = actual_sha256
            )
            OR (
                result = 'MODIFIED'
                AND expected_sha256 IS NOT NULL
                AND actual_sha256 IS NOT NULL
                AND expected_sha256 <> actual_sha256
            )
            OR (
                result = 'DELETED'
                AND expected_sha256 IS NOT NULL
                AND actual_sha256 IS NULL
            )
            OR (
                result = 'NEW'
                AND expected_sha256 IS NULL
                AND actual_sha256 IS NOT NULL
            )
            OR (
                result = 'REPLACED'
                AND expected_sha256 IS NOT NULL
                AND actual_sha256 IS NOT NULL
                AND expected_sha256 <> actual_sha256
            )
            OR result IN ('ERROR', 'UNVERIFIED')
            """,
            name="chk_scan_result_hash_consistency"
        ),

        Index(
            "idx_scan_results_scan_result",
            "scan_id",
            "result"
        ),

        Index(
            "idx_scan_results_baseline_item",
            "baseline_item_id"
        ),

        Index(
            "idx_scan_results_asset_id",
            "asset_id"
        ),
    )