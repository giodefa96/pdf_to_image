import json
import logging

from sqlalchemy import select
from src.models.db.pdf_document import PdfDocument
from src.models.pydantic.response_model import PdfBlobResponse
from src.models.pydantic.response_model import PdfResponse
from src.utils.blob_storage import AzureBlobManager
from src.db.database import Database

logger = logging.getLogger(__name__)

class PdfRepository:
    def __init__(self, blob_storage: AzureBlobManager, db: Database) -> None:
        self.blob_storage = blob_storage
        self.db = db

    async def save_pdf_document_hash(self, pdf_blob_response: PdfBlobResponse) -> PdfDocument | None:
        """
        Save the PDF document hash and metadata to the database.

        Args:
            pdf_blob_response (PdfBlobResponse): Response object containing blob metadata.

        Returns:
            Optional[PdfDocument]: The saved PDF document object.
        """
        logging.info("Saving PDF document hash to the database.")
        async with self.db.transaction() as session:
            pdf_document = PdfDocument(
                hash_id=pdf_blob_response.blob_name,
                blob_url=pdf_blob_response.blob_url,
                container_name=pdf_blob_response.container_name,
                host_name=pdf_blob_response.host_name,
            )
            session.add(pdf_document)
            return pdf_document

    async def get_pdf_blob_storage_url_by_hash(self, hash_id: str) -> PdfResponse:
        """
        Retrieve the PDF document from the database by its hash ID.

        Args:
            hash_id (str): The hash ID of the PDF document.

        Returns:
            PdfResponse: Response object containing the document data or error information.
        """
        logging.info("Retrieving PDF document from the database.")
        async with self.db.get_session() as session:
            result = await session.execute(select(PdfDocument).where(PdfDocument.hash_id == hash_id))
            pdf_document = result.scalars().first()
            if pdf_document:
                return PdfResponse.success(hash_id=pdf_document.hash_id, blob_url=pdf_document.blob_url)
            return PdfResponse.not_found(hash_id=hash_id)

    async def get_image_from_blob_storage_by_name(self, blob_url: str) -> list[dict[str, str]]:
        """
        Retrieve the image from blob storage by its URL.

        Args:
            blob_url (str): The URL of the blob storage.

        Returns:
            List[Dict[str, str]]: The parsed JSON data from the blob.
        """
        logging.info("Retrieving image from blob storage.")
        blob_response = await self.blob_storage.get_file(blob_url)
        return json.loads(blob_response)

    async def save_image_to_blob_storage(self, image_data: list[dict[str, str]], blob_name: str) -> PdfBlobResponse:
        """
        Save the image data to blob storage.

        Args:
            image_data (List[Dict[str, str]]): The image data to save as JSON.
            blob_name (str): The name of the blob.

        Returns:
            PdfBlobResponse: Response object containing information about the saved blob.
        """
        logging.info("Saving image data to blob storage.")
        json_dumped = json.dumps(image_data).encode("utf-8")
        return await self.blob_storage.upload_file(json_dumped, blob_name)
