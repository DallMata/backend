from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.instrument import Instrument
from app.schemas.instrument import InstrumentCreate, InstrumentResponse
from app.dependencies import get_current_user


router = APIRouter(
    prefix="/instruments",
    tags=["instruments"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=InstrumentResponse, status_code=201)
def create_instrument(
    instrument_data: InstrumentCreate,
    db: Session = Depends(get_db),
):
    instrument = Instrument(
        ticker=instrument_data.ticker,
        name=instrument_data.name,
        currency=instrument_data.currency,
    )

    db.add(instrument)
    db.commit()
    db.refresh(instrument)

    return instrument


@router.get("/", response_model=list[InstrumentResponse])
def get_instruments(
    db: Session = Depends(get_db),
):
    statement = select(Instrument).order_by(Instrument.id)

    instruments = db.scalars(statement).all()

    return instruments
