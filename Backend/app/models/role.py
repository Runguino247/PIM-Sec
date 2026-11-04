from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    code: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        unique=True
    )

    name: Mapped[str] = mapped_column(
        String(80),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text
    )

    users = relationship(
        "User",
        back_populates="role"
    )