import json
import os

from azure.storage.blob import BlobServiceClient

blob_connetion_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
if blob_connetion_string is None:
    raise ValueError("AZURE_STORAGE_CONNECTION_STRING environment variable is not set")

blob_service_client = BlobServiceClient.from_connection_string(blob_connetion_string)


def get_content_from_blob(blob_name: str) -> list[dict[str, str]]:
    """
    Retrieve the content of a blob from Azure Blob Storage.

    Args:
        blob_name (str): The name of the blob to retrieve.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing base64-encoded images
                              and metadata for each page of the PDF.
    """
    container_client = blob_service_client.get_container_client("pdfs")
    blob_client = container_client.get_blob_client(blob_name)

    blob_data = blob_client.download_blob()
    content = blob_data.readall()

    return json.loads(content)
