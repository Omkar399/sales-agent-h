"""Pydantic schemas for card operations."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from ..models.cards import CardStatus, CardPriority


class CardBase(BaseModel):
    """Base card schema."""
    customer_name: str = Field(..., min_length=1, max_length=255, description="Customer name")
    company: Optional[str] = Field(None, max_length=255, description="Company name")
    email: Optional[EmailStr] = Field(None, description="Customer email")
    phone: Optional[str] = Field(None, max_length=50, description="Customer phone number")
    status: CardStatus = Field(CardStatus.TO_REACH, description="Card status")
    priority: CardPriority = Field(CardPriority.MEDIUM, description="Card priority")
    notes: Optional[str] = Field(None, description="Additional notes")
    assigned_to: Optional[str] = Field(None, max_length=255, description="Assigned team member")
    next_followup_date: Optional[datetime] = Field(None, description="Next follow-up date")


class CardCreate(CardBase):
    """Schema for creating a card."""
    pass


class CardUpdate(BaseModel):
    """Schema for updating a card."""
    customer_name: Optional[str] = Field(None, min_length=1, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    status: Optional[CardStatus] = None
    priority: Optional[CardPriority] = None
    notes: Optional[str] = None
    assigned_to: Optional[str] = Field(None, max_length=255)
    next_followup_date: Optional[datetime] = None


class CardResponse(CardBase):
    """Schema for card responses."""
    id: int
    last_contact_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CardStatusUpdate(BaseModel):
    """Schema for updating card status."""
    status: CardStatus


class CardListResponse(BaseModel):
    """Schema for card list responses."""
    cards: list[CardResponse]
    total: int
    page: int
    per_page: int
