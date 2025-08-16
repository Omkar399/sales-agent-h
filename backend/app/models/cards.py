"""Database models for customer cards."""

from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from ..database import Base


class CardStatus(PyEnum):
    """Card status enumeration."""
    TO_REACH = "to_reach"
    IN_PROGRESS = "in_progress" 
    REACHED_OUT = "reached_out"
    FOLLOWUP = "followup"


class CardPriority(PyEnum):
    """Card priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Card(Base):
    """Customer card model."""
    
    __tablename__ = "cards"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    status = Column(Enum(CardStatus), default=CardStatus.TO_REACH, nullable=False, index=True)
    priority = Column(Enum(CardPriority), default=CardPriority.MEDIUM, nullable=False)
    notes = Column(Text, nullable=True)
    assigned_to = Column(String(255), nullable=True)
    last_contact_date = Column(DateTime(timezone=True), nullable=True)
    next_followup_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Card(id={self.id}, customer_name='{self.customer_name}', status='{self.status}')>"
