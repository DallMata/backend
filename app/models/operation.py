from datetime import date
from decimal import Decimal
from enum import Enum

from sqlalchemy import Date, Enum as SqlEnum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class OperationType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class Operation(Base):
    __tablename__ = "operations"

    id: Mapped[int] = mapped_column(primary_key=True)

    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id"),
        nullable=False,
    )

    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.id"),
        nullable=False,
    )

    operation_type: Mapped[OperationType] = mapped_column(
        SqlEnum(OperationType),
        nullable=False,
    )

    operation_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 6),
        nullable=False,
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(18, 6),
        nullable=False,
    )

    commission: Mapped[Decimal] = mapped_column(
        Numeric(18, 6),
        nullable=False,
        default=0,
    )