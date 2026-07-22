"""
Application entrypoint.

Responsible only for:
  - creating the FastAPI app
  - wiring up middleware
  - wiring up routers ("app router" pattern)
  - managing the MongoDB connection lifecycle

All actual logic lives in routers/services/core - this file stays thin on
purpose so the overall structure is easy to navigate.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import close_mongo_connection, connect_to_mongo
from app.middleware.logging import RequestLoggingMiddleware
from app.routers import redirect, url

logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: open the MongoDB connection once for the whole app lifetime.
    await connect_to_mongo()
    yield
    # Shutdown: cleanly close the connection.
    await close_mongo_connection()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="A simple URL shortener API built with FastAPI + MongoDB.",
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    # ---- Middleware -----------------------------------------------------
    # Order matters: middleware added last runs first (outermost) on requests.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    # ---- Health check -----------------------------------------------------
    @app.get("/health", tags=["Health"], summary="Health check")
    async def health_check() -> dict:
        return {"status": "ok", "app": settings.app_name, "env": settings.app_env}

    # ---- Routers (app router pattern) --------------------------------
    # API routes (specific, prefixed paths) must be registered before the
    # catch-all "/{short_code}" redirect route, so they are matched first.
    app.include_router(url.router)
    app.include_router(redirect.router)

    return app


app = create_app()
