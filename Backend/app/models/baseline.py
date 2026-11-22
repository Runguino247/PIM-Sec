from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Integer,
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


class Baseline(Base):
    __tablename__ = "baselines"

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
    

    version_no: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PROPOSED",
        server_default="PROPOSED"
    )

    created_by: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    approved_by: Mapped[int | None] = mapped_column(
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

    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    hmac_sha256: Mapped[str | None] = mapped_column(
        String(64)
    )

    repository = relationship(
        "Repository",
        back_populates="baselines"
    )

    creator = relationship(
        "User",
        back_populates="created_baselines",
        foreign_keys=[created_by]
    )

    approver = relationship(
        "User",
        back_populates="approved_baselines",
        foreign_keys=[approved_by]
    )

    items = relationship(
        "BaselineItem",
        back_populates="baseline"
    )

    scans = relationship(
        "IntegrityScan", 
        back_populates="baseline",
        foreign_keys="[IntegrityScan.baseline_id]"  # <--- Agrega esto
    )

    __table_args__ = (
        UniqueConstraint(
            "repository_id",
            "version_no",
            name="uq_baseline_version"
        ),

        UniqueConstraint(
            "id",
            "repository_id",
            name="uq_baseline_id_repository"
        ),

        CheckConstraint(
            "version_no > 0",
            name="chk_baseline_version"
        ),

        CheckConstraint(
            "status IN ('PROPOSED', 'ACTIVE', 'REJECTED', 'SUPERSEDED')",
            name="chk_baseline_status"
        ),

        CheckConstraint(
            "hmac_sha256 IS NULL OR hmac_sha256 ~ '^[0-9a-fA-F]{64}$'",
            name="chk_baseline_hmac"
        ),

        CheckConstraint(
            """
            (approved_by IS NULL AND approved_at IS NULL)
            OR
            (approved_by IS NOT NULL AND approved_at IS NOT NULL)
            """,
            name="chk_baseline_approval"
        ),

        CheckConstraint(
            "approved_by IS NULL OR approved_by <> created_by",
            name="chk_baseline_approver"
        ),

        CheckConstraint(
            """
            status <> 'ACTIVE'
            OR (
                approved_by IS NOT NULL
                AND approved_at IS NOT NULL
                AND hmac_sha256 IS NOT NULL
            )
            """,
            name="chk_active_baseline_requirements"
        ),

        Index("idx_baselines_created_by", "created_by"),
        Index("idx_baselines_approved_by", "approved_by"),

        Index(
            "uq_baseline_active_repository",
            "repository_id",
            unique=True,
            postgresql_where=(status == "ACTIVE")
        ),
    )