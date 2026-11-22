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

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AuthorizedChange(Base):
    __tablename__ = "authorized_changes"

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

    requested_by: Mapped[int] = mapped_column(
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

    decided_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        )
    )

    decision_note: Mapped[str | None] = mapped_column(
        Text
    )

    scope_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    valid_until: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDING",
        server_default="PENDING"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )

    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    repository = relationship(
        "Repository",
        back_populates="authorized_changes"
    )

    requester = relationship(
        "User",
        back_populates="authorized_changes",
        foreign_keys=[requested_by]
    )

    approver = relationship(
        "User",
        foreign_keys=[approved_by]
    )

    decider = relationship(
        "User",
        foreign_keys=[decided_by]
    )

    event_links = relationship(
        "ChangeEventLink",
        back_populates="authorized_change"
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'APPROVED', 'REJECTED', 'EXPIRED')",
            name="chk_authorized_change_status"
        ),

        CheckConstraint(
            "valid_until > valid_from",
            name="chk_authorized_change_validity"
        ),

        CheckConstraint(
            "approved_by IS NULL OR approved_by <> requested_by",
            name="chk_authorized_change_approver"
        ),

        CheckConstraint(
            """
            (
                status = 'PENDING'
                AND decided_by IS NULL
                AND decided_at IS NULL
                AND decision_note IS NULL
            )
            OR (
                status = 'APPROVED'
                AND decided_by IS NOT NULL
                AND decided_at IS NOT NULL
            )
            OR (
                status = 'REJECTED'
                AND decided_by IS NOT NULL
                AND decided_at IS NOT NULL
                AND decision_note IS NOT NULL
                AND LENGTH(TRIM(decision_note)) > 0
            )
            OR (
                status = 'EXPIRED'
                AND decided_at IS NOT NULL
            )
            """,
            name="chk_authorized_change_decision"
        ),

        Index(
            "idx_authorized_changes_repository_status",
            "repository_id",
            "status"
        ),

        Index(
            "idx_authorized_changes_requested_by",
            "requested_by"
        ),

        Index(
            "idx_authorized_changes_approved_by",
            "approved_by"
        ),
    )