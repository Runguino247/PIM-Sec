from sqlalchemy import (
    BigInteger,
    String,
    Text,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Index
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BaselineItem(Base):
    __tablename__ = "baseline_items"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
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

    sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )

    size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

    file_identity: Mapped[str | None] = mapped_column(
        Text
    )

    mime_type: Mapped[str | None] = mapped_column(
        String(120)
    )

    baseline = relationship(
        "Baseline",
        back_populates="items"
    )

    asset = relationship(
        "Asset",
        back_populates="baseline_items"
    )

    scan_results = relationship(
        "ScanResult",
        back_populates="baseline_item"
    )

    __table_args__ = (
        UniqueConstraint(
            "baseline_id",
            "relative_path",
            name="uq_baseline_item_path"
        ),

        CheckConstraint(
            "size_bytes >= 0",
            name="chk_baseline_item_size"
        ),

        CheckConstraint(
            "sha256 ~ '^[0-9a-fA-F]{64}$'",
            name="chk_baseline_item_sha256"
        ),

        Index("idx_baseline_items_asset_id", "asset_id"),
    )