from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine
from app.routers.clients import router as clients_router
from app.routers.instrument import router as instruments_router
from app.routers.operation import router as operations_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="FIFolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.config import settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clients_router)
app.include_router(instruments_router)
app.include_router(operations_router)

@app.get("/")
def root():
    return {"message": "FIFolio API"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/database-test")
def database_test():
    with engine.connect() as connection:
        version = connection.execute(
            text("SELECT version();")
        ).scalar()

    return {
        "status": "connected",
        "postgresql_version": version,
    }