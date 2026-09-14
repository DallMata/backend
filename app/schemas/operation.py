from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class BuyOperationCreate(BaseModel):
    client_id: int
    instrument_id: int
    operation_date: date
    quantity: Decimal
    unit_price: Decimal
    commission: Decimal = Decimal("0")


class OperationResponse(BaseModel):
    id: int
    client_id: int
    instrument_id: int
    operation_type: str
    operation_date: date
    quantity: Decimal
    unit_price: Decimal
    commission: Decimal

    model_config = ConfigDict(from_attributes=True)

class SellOperationCreate(BaseModel):
    client_id: int
    instrument_id: int
    operation_date: date
    quantity: Decimal
    unit_price: Decimal
    commission: Decimal = Decimal("0")

class FifoAllocationResponse(BaseModel):
    id: int
    sell_operation_id: int
    buy_operation_id: int
    quantity: Decimal
    unit_cost: Decimal

    model_config = ConfigDict(from_attributes=True)

class SaleResultResponse(BaseModel):
    sale_id: int
    quantity: Decimal
    unit_price: Decimal
    gross_proceeds: Decimal
    fifo_cost: Decimal
    commission: Decimal
    realized_gain: Decimal

class HoldingResponse(BaseModel):
    client_id: int
    instrument_id: int
    quantity: Decimal