from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AssetCategory(Base):
    __tablename__ = "asset_categories"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        unique=True
    )

    description: Mapped[str | None] = mapped_column(
        Text
    )

    assets = relationship(
        "Asset",
        back_populates="category"
    )