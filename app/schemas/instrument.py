from pydantic import BaseModel, ConfigDict


class InstrumentCreate(BaseModel):
    ticker: str
    name: str
    currency: str


class InstrumentResponse(BaseModel):
    id: int
    ticker: str
    name: str
    currency: str

    model_config = ConfigDict(from_attributes=True)