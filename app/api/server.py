from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI

from app.api.routers import router
from app.bootstrap import init_ssl

from app.tasks.subscription_task import subscription_task
from app.api.routes.admin import router as admin_router

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
    admin_router,
    prefix="/api/v1",
)


app.include_router(router)