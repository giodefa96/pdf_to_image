from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.sql import expression
from src.db.database import Base


class PdfDocument(Base):
    """
    Model for storing information about PDF documents stored in Blob Storage
    """

    __tablename__ = "pdf_documents"

    hash_id = Column(String(64), primary_key=True, index=True)
    blob_url = Column(String(2000), nullable=False)
    container_name = Column(String(100), nullable=False)
    host_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, server_default=expression.true(), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<PdfDocument(hash_id='{self.hash_id}', blob_name='{self.blob_name}')>"
