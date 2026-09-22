from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.clients import router as clients_router
from app.routers.instrument import router as instruments_router
from app.routers.operation import router as operations_router
from app.routers import auth


app = FastAPI(
    title="FIFolio API",
    version="0.1.0",
)


# =====================================================
# CORS
# =====================================================

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


# =====================================================
# ROUTERS
# =====================================================

app.include_router(clients_router)
app.include_router(instruments_router)
app.include_router(operations_router)
app.include_router(auth.router)


# =====================================================
# GENERAL ENDPOINTS
# =====================================================

@app.get("/")
def root():
    return {
        "message": "FIFolio API",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
    }