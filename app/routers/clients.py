from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientResponse
from app.dependencies import get_current_user


router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=ClientResponse, status_code=201)
def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
):
    client = Client(
        name=client_data.name,
        cuit=client_data.cuit,
    )

    db.add(client)
    db.commit()
    db.refresh(client)

    return client


@router.get("/", response_model=list[ClientResponse])
def get_clients(
    db: Session = Depends(get_db),
):
    statement = select(Client).order_by(Client.id)

    clients = db.scalars(statement).all()

    return clients