from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from tortoise.contrib.fastapi import RegisterTortoise

from src.config.settings import ALLOWED_ORIGINS, APP_NAME
from src.database.config import TORTOISE_ORM
from src.routes.auth import router as auth_router
from src.routes.auctions import router as auctions_router
from src.routes.bids import router as bids_router
from src.socket.server import socket_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with RegisterTortoise(
        app, config=TORTOISE_ORM, generate_schemas=False, add_exception_handlers=True
    ):
        yield


app = FastAPI(title=APP_NAME, lifespan=lifespan)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# REST routes
app.include_router(auth_router, prefix="/api")
app.include_router(auctions_router, prefix="/api")
app.include_router(bids_router, prefix="/api")

# Socket.IO mount
app.mount("/ws", socket_app)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
