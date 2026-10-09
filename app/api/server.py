from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import router
from app.bootstrap import init_ssl
from app.database.schema import create_tables

from app.services.vpn_service import vpn_service

from app.api.routes.public_subscription import (
    router as public_subscription_router,
)

init_ssl()


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):

    create_tables()

    try:
        yield

    finally:
        await vpn_service.close()


app = FastAPI(
    title="JustVPN Backend",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["Health"])
async def root_health():
    return {
        "status": "ok",
        "service": "justvpn-backend",
    }

app.include_router(
    public_subscription_router
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://app.just-cdn.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    router
)
