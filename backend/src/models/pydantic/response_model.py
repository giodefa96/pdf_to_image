from typing import Literal

from pydantic import BaseModel


class PdfResponse(BaseModel):
    hash_id: str | None = None
    blob_url: str | None = None
    found: bool = False

    @classmethod
    def success(cls, hash_id: str, blob_url: str) -> "PdfResponse":
        return cls(hash_id=hash_id, blob_url=blob_url, found=True)

    @classmethod
    def not_found(cls, hash_id: str) -> "PdfResponse":
        return cls(hash_id=hash_id, found=False)


class PdfBlobResponse(BaseModel):
    blob_url: str
    host_name: str
    container_name: str
    account_name: str
    blob_name: str
    found: bool = False

    @classmethod
    def success(
        cls, blob_url: str, host_name: str, container_name: str, account_name: str, blob_name: str
    ) -> "PdfBlobResponse":
        return cls(
            blob_url=blob_url,
            host_name=host_name,
            container_name=container_name,
            account_name=account_name,
            blob_name=blob_name,
            found=True,
        )


class StatusResponse(BaseModel):
    status: Literal["completed", "not_found", "pending", "failed"]
    hash_id: str
    blob_url: str | None = None
    message: str | None = None
