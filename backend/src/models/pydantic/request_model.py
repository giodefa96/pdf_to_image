from pydantic import BaseModel, Field
import uuid

class ChatRequest(BaseModel):
    prompt: str
    model: str

class TaskData(BaseModel):
    pdf_azure_storage_url: str
    hash_id: str
    output_format: str = "png"
    quality: int = 95

class AzureQueueRequest(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str
    data: TaskData
