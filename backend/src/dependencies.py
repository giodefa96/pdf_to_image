import logging
import sys
from functools import lru_cache

from fastapi import Depends
from fastapi import Request
from src.db.database import Database
from src.repositories.pdf_repository import PdfRepository
from src.services.pdf_service import PdfService
from src.utils.blob_storage import AzureBlobManager


def setup_logging(log_level: str = "INFO") -> None:
    """Set up logging configuration."""
    logging.getLogger("logging").setLevel(logging.INFO)

    logger = logging.getLogger()
    logger.propagate = False
    logger.setLevel(logging.INFO)

    logger.setLevel(log_level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(stdout_handler)


def get_blob_storage(request: Request) -> AzureBlobManager:
    """Retrieve the blob storage instance from app state."""
    return request.app.state.blob_storage


def get_db(request: Request) -> Database:
    """Retrieve the database instance from app state."""
    return request.app.state.db


@lru_cache
def get_pdf_repository(
    blob_storage: AzureBlobManager = Depends(get_blob_storage), db: Database = Depends(get_db)
) -> PdfRepository:
    """Create a singleton repository instance."""
    return PdfRepository(blob_storage=blob_storage, db=db)


@lru_cache
def get_pdf_service(repository: PdfRepository = Depends(get_pdf_repository)) -> PdfService:
    """Create a singleton service instance."""
    return PdfService(repository)
