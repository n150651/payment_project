from sqlalchemy import String, DECIMAL, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from database import Base
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

# --- SQLAlchemy Table (2.0 Style) ---

class TransactionDB(Base):
    __tablename__ = "transactions"
    
    # Using Mapped for better type hinting and 2.0 compatibility
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(nullable=False, index=True) # Added index for faster queries
    amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    status: Mapped[str] = mapped_column(String(20), default="PENDING")

# --- Pydantic Schemas (v2 Style) ---

class TransactionCreate(BaseModel):
    user_id: int = Field(..., gt=0, description="Must be a positive user ID")
    amount: float = Field(..., gt=0, description="Transaction amount must be greater than 0")
    currency: str = Field(..., min_length=3, max_length=3, pattern="^[A-Z]{3}$")

class TransactionResponse(TransactionCreate):
    id: int
    timestamp: datetime
    status: str

    # Updated for Pydantic v2
    model_config = ConfigDict(from_attributes=True)