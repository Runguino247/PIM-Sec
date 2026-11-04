from datetime import datetime

from sqlalchemy import (
    BigInteger,
    String,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
    CheckConstraint,
    UniqueConstraint,
    Index,
    func
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Asset(Base):
    __tablename__ = "assets"

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

    category_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "asset_categories.id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        )
    )

    relative_path: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    mime_type: Mapped[str | None] = mapped_column(
        String(120)
    )

    size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )

    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true"
    )

    repository = relationship(
        "Repository",
        back_populates="assets"
    )

    category = relationship(
        "AssetCategory",
        back_populates="assets"
    )

    baseline_items = relationship(
        "BaselineItem",
        back_populates="asset"
    )

    scan_results = relationship(
        "ScanResult",
        back_populates="asset"
    )

    security_events = relationship(
        "SecurityEvent",
        back_populates="asset"
    )

    __table_args__ = (
        UniqueConstraint(
            "repository_id",
            "relative_path",
            name="uq_asset_repository_path"
        ),
        CheckConstraint(
            "size_bytes >= 0",
            name="chk_asset_size"
        ),
        CheckConstraint(
            "last_seen_at IS NULL OR last_seen_at >= first_seen_at",
            name="chk_asset_dates"
        ),
        Index("idx_assets_category_id", "category_id"),
        Index(
            "idx_assets_repository_active",
            "repository_id",
            "is_active"
        ),
    )