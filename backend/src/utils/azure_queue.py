import logging
import json
from typing import Dict, Any, Optional

from azure.storage.queue import QueueServiceClient, QueueClient, QueueMessage, BinaryBase64DecodePolicy, BinaryBase64EncodePolicy
from azure.core.exceptions import ResourceExistsError, ServiceRequestError
from src.models.pydantic.request_model import AzureQueueRequest, TaskData
from src.models.pydantic.response_model import PdfBlobResponse
from src.config import Settings

logger = logging.getLogger(__name__)

class AzureQueueManager:
    def __init__(self) -> None:
        self.connection_string = Settings.AZURE_STORAGE_QUEUE_CONNECTION_STRING
        self.queue_name = Settings.AZURE_STORAGE_QUEUE_NAME
        self.queue_service_client = None
    
    def initialize(self) -> bool:
        """
        Initialize the Azure Queue Service client.

        Returns:
            bool: True if initialization is successful, False otherwise
        """
        try:
            self.queue_service_client = QueueServiceClient.from_connection_string(self.connection_string,
                                                                                  message_encode_policy = BinaryBase64EncodePolicy(),
                                                                                  message_decode_policy = BinaryBase64DecodePolicy())
            logger.info("Azure Queue Service client initialized successfully.")
            self.queue_service_client.create_queue(self.queue_name)
            logger.info("Queue '%s' is ready for use.", self.queue_name)
            return True
        except ResourceExistsError:
            logger.info("Queue '%s' already exists, ready for use.", self.queue_name)
            return True
        except Exception as e:
            logger.error("Failed to initialize Azure Queue Service client: %s", str(e))
            return False
    
    def send_message(self, message: str) -> bool:
        """
        Send a message to the Azure Queue.

        Args:
            message (str): The message to send

        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        if not self.queue_service_client:
            logger.error("Queue service client is not initialized.")
            return False
        
        if not message:
            logger.error("Message cannot be empty.")
            return False
        
        try:
            queue_client = self.queue_service_client.get_queue_client(self.queue_name)
            queue_client.send_message(message)
            logger.info("Message sent to queue '%s': %s", self.queue_name, message)
            return True
        except ServiceRequestError as e:
            logger.error("Service request error when sending message to queue '%s': %s", self.queue_name, str(e))
            return False
        except Exception as e:
            logger.error("Failed to send message to queue '%s': %s", self.queue_name, str(e))
            return False
    
    def send_task(self, task_data: AzureQueueRequest) -> bool:
        """
        Send a task to the Azure Queue with proper JSON serialization.

        Args:
            task_data (PdfBlobResponse): The task data to send

        Returns:
            bool: True if task was sent successfully, False otherwise
        """
        if not task_data:
            logger.error("Task data cannot be empty.")
            return False
        
        try:
            message = json.dumps(task_data)
            return self.send_message(message)
        except (TypeError, ValueError) as e:
            logger.error("Failed to serialize task data: %s", str(e))
            return False
    
    def is_connected(self) -> bool:
        """
        Check if the queue service client is initialized and connected.

        Returns:
            bool: True if connected, False otherwise
        """
        if not self.queue_service_client:
            return False
        
        try:
            # Try to get queue properties to test connection
            queue_client = self.queue_service_client.get_queue_client(self.queue_name)
            queue_client.get_queue_properties()
            return True
        except Exception:
            return False


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    queue_manager = AzureQueueManager()
    if queue_manager.initialize():
        task_data = AzureQueueRequest(
            task_type="pdf_conversion",
            data=TaskData(
                pdf_azure_storage_url="https://example.blob.core.windows.net/container/file.pdf",
                hash_id="abc123",
                output_format="png",
                quality=95
            )
        )
        if queue_manager.send_task(task_data.model_dump()):
            logger.info("Task sent successfully.")
        else:
            logger.error("Failed to send task.")
    else:
        logger.error("Failed to initialize Azure Queue Manager.")