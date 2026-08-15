from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import router
from app.bootstrap import init_ssl

from app.tasks.subscription_task import subscription_task

from app.api.routes.public_subscription import (
    router as public_subscription_router,
)

init_ssl()


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):

    task = asyncio.create_task(
        subscription_task()
    )

    yield

    task.cancel()

    try:
        await task

    except asyncio.CancelledError:
        pass



app = FastAPI(
    title="JustVPN Backend",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(
    public_subscription_router
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://students-decades-bicycle-society.trycloudflare.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    router
)
app.include_router(
    public_subscription_router
)
