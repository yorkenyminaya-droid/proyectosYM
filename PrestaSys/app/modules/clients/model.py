from datetime import datetime

from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import DateTime

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.core.database.base import Base


class Client(Base):

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    code: Mapped[str] = mapped_column(
        String(20),
        unique=True
    )

    first_name: Mapped[str] = mapped_column(
        String(100)
    )

    last_name: Mapped[str] = mapped_column(
        String(100)
    )

    document: Mapped[str] = mapped_column(
        String(20),
        unique=True
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        default=""
    )

    phone2: Mapped[str] = mapped_column(
        String(20),
        default=""
    )

    address: Mapped[str] = mapped_column(
        String(255),
        default=""
    )

    reference: Mapped[str] = mapped_column(
        String(255),
        default=""
    )

    reference_phone: Mapped[str] = mapped_column(
        String(20),
        default=""
    )

    email: Mapped[str] = mapped_column(
        String(120),
        default=""
    )

    notes: Mapped[str] = mapped_column(
        String(500),
        default=""
    )

    active: Mapped[int] = mapped_column(
        Integer,
        default=1
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now
    )