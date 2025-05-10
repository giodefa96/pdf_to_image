import logging
import os

logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv

    load_dotenv()
    logger.info("INFO: .env file loaded by dotenv (likely development environment).")
except ImportError:
    logger.error("INFO: python-dotenv not found. Skipping .env file loading (expected in production).")
except Exception as e:
    logger.error("INFO: Error loading .env file with dotenv: %s (expected in production if .env is not present).", e)


class Settings:
    AZURE_STORAGE_CONNECTION_STRING: str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    AZURE_STORAGE_CONTAINER_NAME: str = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")

    PDF_BATCH_SIZE: int = int(os.getenv("PDF_BATCH_SIZE", 10))

    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY")
