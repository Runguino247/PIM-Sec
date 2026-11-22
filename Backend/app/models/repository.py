from datetime import datetime

from sqlalchemy import (
    BigInteger,
    String,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    Index,
    func
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )

    root_path: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text
    )

    created_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        )
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )

    creator = relationship(
        "User",
        back_populates="created_repositories",
        foreign_keys=[created_by]
    )

    assets = relationship(
        "Asset",
        back_populates="repository"
    )

    baselines = relationship(
        "Baseline",
        back_populates="repository"
    )

    scans = relationship(
        "IntegrityScan",
        back_populates="repository"
    )

    authorized_changes = relationship(
        "AuthorizedChange",
        back_populates="repository"
    )

    __table_args__ = (
        UniqueConstraint(
            "root_path",
            name="uq_repository_root_path"
        ),
        Index("idx_repositories_created_by", "created_by"),
    )