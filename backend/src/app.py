import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from src.db.database import Database
from src.dependencies import setup_logging
from src.routers import pdf_router
from src.utils.blob_storage import AzureBlobManager

setup_logging()
logger = logging.getLogger(__name__)
blob_storage = AzureBlobManager()
db = Database()


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    """
    Lifespan context manager for the FastAPI application.

    This function is used to manage the lifespan of the FastAPI application.
    It initializes and cleans up resources when the application starts and stops.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: This function does not yield any values.
    """
    await db.initialize()
    await db.create_tables()
    logger.info("Database initialized during application startup")
    success = await blob_storage.initialize()
    if success:
        logger.info("Azure Blob Storage initialized during application startup")
        app.state.blob_storage = blob_storage
        app.state.db = db
    else:
        logger.warning("Azure Blob Storage initialization failed")
    yield
    await db.close()
    logger.info("Database connection closed during application shutdown")


def create_app() -> FastAPI:
    """
    Factory Method to create a FastAPI instance

    set up logging, middleware, and include routers.
    Returns:
        FastAPI: Configured FastAPI application instance.
    """

    app = FastAPI(title="FastAPI Template", version="0.0.1", lifespan=lifespan)

    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

    app.include_router(pdf_router.router, prefix="/api")

    logger.info("FastAPI application created and configured.")

    return app


instance = create_app()
