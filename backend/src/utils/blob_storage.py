import logging
import os

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob.aio import BlobServiceClient

from src.models.pydantic.response_model import PdfBlobResponse
from src.config import Settings

logger = logging.getLogger(__name__)


class AzureBlobManager:
    def __init__(self) -> None:
        self.connection_string = Settings.AZURE_STORAGE_CONNECTION_STRING
        self.container_name = Settings.AZURE_STORAGE_CONTAINER_NAME
        self.blob_service_client = None

    async def initialize(self) -> bool:
        """Initialize the blob service client and create default container"""
        if not self.connection_string:
            logger.warning("Azure Storage connection string not provided")
            return False

        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            await self.create_container(self.container_name)
            logger.info("Blob Storage initialized with container '%s'", self.container_name)
            return True
        except Exception as e:
            logger.error("Failed to initialize Blob Storage: %s", str(e))
            return False

    async def create_container(self, container_name: str) -> BlobServiceClient:
        """
        Create a new container.

        Args:
            container_name (str): Name of the container to create

        Returns:
            ContainerClient: Container client object if created successfully
        """
        try:
            container_client = self.blob_service_client.get_container_client(container_name)
            await container_client.create_container()
            logger.info("Container '%s' created successfully.", container_name)
            return container_client
        except ResourceExistsError:
            logger.info("Container '%s' already exists.", container_name)
            return self.blob_service_client.get_container_client(container_name)

    async def get_file(self, blob_name: str) -> bytes:
        """
        get a file from a blob.

        Args:
            blob_name (str): Name of the blob to download

        Returns:
            bytes: Content of the downloaded file
        """
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)

        blob_data = await blob_client.download_blob()
        content = await blob_data.readall()

        logger.info("Blob '%s' downloaded successfully.", blob_name)
        return content

    async def upload_file(self, file: bytes, file_name: str) -> PdfBlobResponse:
        """
        Upload a file to a blob.

        Args:
            file (file-like object): File to upload
            file_name (str): Name of the blob to create

        Returns:
            str: URL of the uploaded blob
        """
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=file_name)
        await blob_client.upload_blob(file, overwrite=True)
        logger.info("Blob '%s' uploaded successfully.", file_name)
        return PdfBlobResponse.success(
            blob_client.primary_endpoint,
            blob_client.primary_hostname,
            blob_client.container_name,
            blob_client.account_name,
            blob_client.blob_name,
        )
