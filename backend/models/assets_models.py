import uuid

from database import Base  # Import SQLAlchemy Base for database models
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


# SQLAlchemy model for the Asset table
class Asset(Base):
    __tablename__ = "assets"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    description = Column(String(1024), nullable=True)
    for_sale = Column(Boolean, default=False)
    price = Column(Float, nullable=True)
    additional_info = Column(String(1024), nullable=True)
    owner_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )  # Assuming users table exists
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="assets")  # Define the back reference

    def __repr__(self):
        return f"<Asset(id={self.id}, name={self.name}, for_sale={self.for_sale})>"


# Pydantic models for validation
class AssetCreate(BaseModel):
    name: str
    description: str = None


class AssetUpdate(BaseModel):
    name: str = None
    description: str = None
    price: float = None
    additional_info: str = None
