from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.client import Client
from app.models.instrument import Instrument
from app.models.operation import Operation, OperationType
from app.schemas.operation import BuyOperationCreate, OperationResponse
from sqlalchemy import select
from decimal import Decimal
from app.schemas.operation import HoldingResponse

from app.schemas.operation import SaleResultResponse

from sqlalchemy import func, select
from app.models.fifo_allocation import FifoAllocation
from app.schemas.operation import (
    BuyOperationCreate,
    SellOperationCreate,
    OperationResponse,
    FifoAllocationResponse,
)

router = APIRouter(
    prefix="/operations",
    tags=["Operations"],
)


@router.post("/buy", response_model=OperationResponse, status_code=201)
def create_buy_operation(
    operation_data: BuyOperationCreate,
    db: Session = Depends(get_db),
):
    client = db.get(Client, operation_data.client_id)

    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Client not found",
        )

    instrument = db.get(
        Instrument,
        operation_data.instrument_id,
    )

    if instrument is None:
        raise HTTPException(
            status_code=404,
            detail="Instrument not found",
        )

    if operation_data.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero",
        )

    if operation_data.unit_price < 0:
        raise HTTPException(
            status_code=400,
            detail="Unit price cannot be negative",
        )

    operation = Operation(
        client_id=operation_data.client_id,
        instrument_id=operation_data.instrument_id,
        operation_type=OperationType.BUY,
        operation_date=operation_data.operation_date,
        quantity=operation_data.quantity,
        unit_price=operation_data.unit_price,
        commission=operation_data.commission,
    )

    db.add(operation)
    db.commit()
    db.refresh(operation)

    return operation

@router.get("/", response_model=list[OperationResponse])
def get_operations(
    db: Session = Depends(get_db),
):
    statement = select(Operation).order_by(
        Operation.operation_date,
        Operation.id,
    )

    operations = db.scalars(statement).all()

    return operations

@router.post("/sell", response_model=OperationResponse, status_code=201)
def create_sell_operation(
    operation_data: SellOperationCreate,
    db: Session = Depends(get_db),
):
    client = db.get(Client, operation_data.client_id)

    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Client not found",
        )

    instrument = db.get(
        Instrument,
        operation_data.instrument_id,
    )

    if instrument is None:
        raise HTTPException(
            status_code=404,
            detail="Instrument not found",
        )

    if operation_data.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero",
        )

    if operation_data.unit_price < 0:
        raise HTTPException(
            status_code=400,
            detail="Unit price cannot be negative",
        )

    buys = db.scalars(
        select(Operation)
        .where(
            Operation.client_id == operation_data.client_id,
            Operation.instrument_id == operation_data.instrument_id,
            Operation.operation_type == OperationType.BUY,
            Operation.operation_date <= operation_data.operation_date,
        )
        .order_by(
            Operation.operation_date.asc(),
            Operation.id.asc(),
        )
    ).all()

    remaining_to_sell = operation_data.quantity

    allocations_to_create = []

    for buy in buys:
        already_used = db.scalar(
            select(func.coalesce(func.sum(FifoAllocation.quantity), 0))
            .where(
                FifoAllocation.buy_operation_id == buy.id
            )
        )

        available_quantity = buy.quantity - already_used

        if available_quantity <= 0:
            continue

        quantity_to_use = min(
            available_quantity,
            remaining_to_sell,
        )

        allocations_to_create.append(
            (
                buy,
                quantity_to_use,
            )
        )

        remaining_to_sell -= quantity_to_use

        if remaining_to_sell == 0:
            break

    if remaining_to_sell > 0:
        raise HTTPException(
            status_code=400,
            detail="Not enough available quantity to sell",
        )

    sell_operation = Operation(
        client_id=operation_data.client_id,
        instrument_id=operation_data.instrument_id,
        operation_type=OperationType.SELL,
        operation_date=operation_data.operation_date,
        quantity=operation_data.quantity,
        unit_price=operation_data.unit_price,
        commission=operation_data.commission,
    )

    db.add(sell_operation)

    try:
        db.flush()

        for buy, quantity_to_use in allocations_to_create:
            allocation = FifoAllocation(
                sell_operation_id=sell_operation.id,
                buy_operation_id=buy.id,
                quantity=quantity_to_use,
                unit_cost=buy.unit_price,
            )

            db.add(allocation)

        db.commit()

    except Exception:
        db.rollback()
        raise

    db.refresh(sell_operation)

    return sell_operation

@router.get(
    "/{sale_id}/fifo",
    response_model=list[FifoAllocationResponse],
)
def get_fifo_allocations(
    sale_id: int,
    db: Session = Depends(get_db),
):
    sale = db.get(Operation, sale_id)

    if sale is None:
        raise HTTPException(
            status_code=404,
            detail="Operation not found",
        )

    if sale.operation_type != OperationType.SELL:
        raise HTTPException(
            status_code=400,
            detail="Operation is not a sale",
        )

    statement = (
        select(FifoAllocation)
        .where(
            FifoAllocation.sell_operation_id == sale_id
        )
        .order_by(FifoAllocation.id)
    )

    allocations = db.scalars(statement).all()

    return allocations


@router.get(
    "/{sale_id}/result",
    response_model=SaleResultResponse,
)
def get_sale_result(
    sale_id: int,
    db: Session = Depends(get_db),
):
    sale = db.get(Operation, sale_id)

    if sale is None:
        raise HTTPException(
            status_code=404,
            detail="Operation not found",
        )

    if sale.operation_type != OperationType.SELL:
        raise HTTPException(
            status_code=400,
            detail="Operation is not a sale",
        )

    allocations = db.scalars(
        select(FifoAllocation).where(
            FifoAllocation.sell_operation_id == sale_id
        )
    ).all()

    fifo_cost = sum(
        allocation.quantity * allocation.unit_cost
        for allocation in allocations
    )

    gross_proceeds = sale.quantity * sale.unit_price

    realized_gain = (
        gross_proceeds
        - fifo_cost
        - sale.commission
    )

    return SaleResultResponse(
        sale_id=sale.id,
        quantity=sale.quantity,
        unit_price=sale.unit_price,
        gross_proceeds=gross_proceeds,
        fifo_cost=fifo_cost,
        commission=sale.commission,
        realized_gain=realized_gain,
    )

@router.get(
    "/holdings/{client_id}",
    response_model=list[HoldingResponse],
)
def get_client_holdings(
    client_id: int,
    db: Session = Depends(get_db),
):
    client = db.get(Client, client_id)

    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Client not found",
        )

    buys = db.scalars(
        select(Operation)
        .where(
            Operation.client_id == client_id,
            Operation.operation_type == OperationType.BUY,
        )
        .order_by(
            Operation.instrument_id,
            Operation.operation_date,
            Operation.id,
        )
    ).all()

    holdings: dict[int, Decimal] = {}

    for buy in buys:
        already_used = db.scalar(
            select(
                func.coalesce(
                    func.sum(FifoAllocation.quantity),
                    0,
                )
            )
            .where(
                FifoAllocation.buy_operation_id == buy.id
            )
        )

        available_quantity = buy.quantity - already_used

        if available_quantity <= 0:
            continue

        holdings[buy.instrument_id] = (
            holdings.get(
                buy.instrument_id,
                Decimal("0"),
            )
            + available_quantity
        )

    return [
        HoldingResponse(
            client_id=client_id,
            instrument_id=instrument_id,
            quantity=quantity,
        )
        for instrument_id, quantity in holdings.items()
    ]