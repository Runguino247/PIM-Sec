from datetime import datetime

from sqlalchemy import (
    BigInteger,
    String,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
    Index,
    func
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    role_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "roles.id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    username: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
        unique=True
    )

    email: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True
    )

    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true"
    )

    must_change_password: Mapped[bool] = mapped_column(
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

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    # Relaciones

    role = relationship(
        "Role",
        back_populates="users"
    )

    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    created_repositories = relationship(
        "Repository",
        back_populates="creator",
        foreign_keys="Repository.created_by"
    )

    created_baselines = relationship(
        "Baseline",
        back_populates="creator",
        foreign_keys="Baseline.created_by"
    )

    approved_baselines = relationship(
        "Baseline",
        back_populates="approver",
        foreign_keys="Baseline.approved_by"
    )

    initiated_scans = relationship(
        "IntegrityScan",
        back_populates="initiator"
    )

    assigned_alerts = relationship(
        "Alert",
        back_populates="assignee"
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="actor"
    )

    authorized_changes = relationship(
        "AuthorizedChange",
        back_populates="requester",
        foreign_keys="AuthorizedChange.requested_by"
    )

    __table_args__ = (
        Index(
            "uq_users_username_lower",
            func.lower(username),
            unique=True
        ),
        Index(
            "idx_users_role_id",
            "role_id"
        ),
        Index(
            "idx_users_active",
            "is_active",
            postgresql_where=(is_active.is_(True))
        ),
    )   