from pydantic import BaseModel, ConfigDict


class ClientCreate(BaseModel):
    name: str
    cuit: str | None = None


class ClientResponse(BaseModel):
    id: int
    name: str
    cuit: str | None

    model_config = ConfigDict(from_attributes=True)