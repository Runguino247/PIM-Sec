from datetime import datetime

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    DateTime,
    ForeignKeyConstraint,
    PrimaryKeyConstraint,
    Index,
    func
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ChangeEventLink(Base):
    __tablename__ = "change_event_links"

    authorized_change_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "authorized_changes.id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    event_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "security_events.id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    linked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )

    linked_by: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    authorized_change = relationship(
        "AuthorizedChange",
        back_populates="event_links"
    )

    event = relationship(
        "SecurityEvent",
        back_populates="change_links"
    )

    user = relationship(
        "User",
        foreign_keys=[linked_by]
    )

    __table_args__ = (
        PrimaryKeyConstraint(
            "authorized_change_id",
            "event_id",
            name="change_event_links_pkey"
        ),

        Index(
            "idx_change_event_links_event_id",
            "event_id"
        ),

        Index(
            "idx_change_event_links_linked_by",
            "linked_by"
        ),
    )