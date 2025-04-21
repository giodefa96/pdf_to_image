import asyncio
import hashlib

from src.models.pydantic.response_model import PdfBlobResponse
from src.models.pydantic.response_model import PdfResponse
from src.models.pydantic.response_model import StatusResponse
from src.repositories.pdf_repository import PdfRepository
from src.utils.convert_pdf_to_image import convert_pdf_to_images


class PdfService:
    def __init__(self, repository: PdfRepository) -> None:
        self.pdf_repository = repository

    async def convert_pdf_to_image(self, file: bytes) -> list[dict[str, str]]:
        """
        Convert the PDF file to base64-encoded images.

        Args:
            file: The uploaded PDF file.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing base64-encoded images
                                and metadata for each page of the PDF.
        """
        return await asyncio.to_thread(convert_pdf_to_images, file)

    async def get_file_hash(self, file_content: bytes) -> str:
        """Generate SHA-256 hash from file content"""
        if not isinstance(file_content, bytes):
            raise TypeError(f"Expected bytes object, got {type(file_content)}")
        return hashlib.sha256(file_content).hexdigest()

    async def check_cache(self, file_content: bytes) -> PdfResponse:
        """
        Check if the file exists in cache by its hash

        Returns:
            Tuple containing the file hash and cache entry (if found)
        """
        file_hash = await self.get_file_hash(file_content)
        return await self.pdf_repository.get_pdf_blob_storage_url_by_hash(file_hash)

    async def already_exists(self, file_content: bytes) -> PdfResponse:
        """
        Check if the file already exists in the database by its hash.

        Args:
            file_content (bytes): The content of the PDF file.

        Returns:
            PdfResponse: The PDF response object containing metadata.
        """
        file_hash = await self.get_file_hash(file_content)
        return await self.pdf_repository.get_pdf_blob_storage_url_by_hash(file_hash)

    async def save_pdf_hash(self, pdf_blob_response: PdfBlobResponse) -> None:
        """
        Save the PDF document hash and metadata to the database.

        Args:
            pdf_response (PdfResponse): The PDF response object containing metadata.

        Returns:
            PdfBlobResponse: The saved PDF document object.
        """
        await self.pdf_repository.save_pdf_document_hash(pdf_blob_response)

    async def process_pdf_conversion(self, file: bytes) -> None:
        """
        Process the PDF conversion in the background.
        """
        pdf_content = file
        cache_entry = await self.check_cache(pdf_content)
        converted_images = await self.convert_pdf_to_image(pdf_content)
        pdf_blob_response = await self.pdf_repository.save_image_to_blob_storage(converted_images, cache_entry.hash_id)
        await self.save_pdf_hash(pdf_blob_response)

    async def get_task_status(self, task_id: str) -> StatusResponse:
        """
        Check the status of a task by its ID.

        Args:
            task_id (str): The ID of the task.

        Returns:
            StatusResponse: A dictionary containing the status of the task.
        """
        pdf_response = await self.pdf_repository.get_pdf_blob_storage_url_by_hash(task_id)
        if pdf_response.found:
            return StatusResponse(status="completed", hash_id=pdf_response.hash_id, blob_url=pdf_response.blob_url)
        return StatusResponse(status="not_found", hash_id=task_id, message="Task not found")
