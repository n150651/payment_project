from sqlalchemy import Column, Integer, String, DECIMAL, DateTime
from sqlalchemy.sql import func
from database import Base
from pydantic import BaseModel
from datetime import datetime

# SQLAlchemy Table

class TransactionDB(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), default="PENDING")

# Pydantic Schemas
class TransactionCreate(BaseModel):
    user_id: int
    amount: float
    currency: str

class TransactionResponse(TransactionCreate):
    id: int
    timestamp: datetime
    status: str

    class Config:
        from_attributes = True