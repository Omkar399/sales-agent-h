"""API routes for card operations."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models.cards import Card, CardStatus
from ..schemas.cards import CardCreate, CardUpdate, CardResponse, CardStatusUpdate, CardListResponse

router = APIRouter(prefix="/cards", tags=["cards"])


@router.post("/", response_model=CardResponse)
def create_card(card: CardCreate, db: Session = Depends(get_db)):
    """Create a new customer card."""
    db_card = Card(**card.dict())
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card


@router.get("/", response_model=CardListResponse)
def get_cards(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    status: Optional[CardStatus] = Query(None, description="Filter by status"),
    assigned_to: Optional[str] = Query(None, description="Filter by assigned person"),
    search: Optional[str] = Query(None, description="Search in customer name or company"),
    db: Session = Depends(get_db)
):
    """Get all cards with pagination and filtering."""
    query = db.query(Card)
    
    # Apply filters
    if status:
        query = query.filter(Card.status == status)
    if assigned_to:
        query = query.filter(Card.assigned_to == assigned_to)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Card.customer_name.ilike(search_term)) |
            (Card.company.ilike(search_term))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    cards = query.order_by(Card.created_at.desc()).offset(offset).limit(per_page).all()
    
    return CardListResponse(
        cards=cards,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{card_id}", response_model=CardResponse)
def get_card(card_id: int, db: Session = Depends(get_db)):
    """Get a specific card by ID."""
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card


@router.put("/{card_id}", response_model=CardResponse)
def update_card(card_id: int, card_update: CardUpdate, db: Session = Depends(get_db)):
    """Update a specific card."""
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    # Update only provided fields
    update_data = card_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(card, field, value)
    
    card.updated_at = func.now()
    db.commit()
    db.refresh(card)
    return card


@router.patch("/{card_id}/status", response_model=CardResponse)
def update_card_status(card_id: int, status_update: CardStatusUpdate, db: Session = Depends(get_db)):
    """Update card status."""
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    card.status = status_update.status
    card.updated_at = func.now()
    
    # Update last_contact_date when status changes to reached_out
    if status_update.status == CardStatus.REACHED_OUT:
        card.last_contact_date = func.now()
    
    db.commit()
    db.refresh(card)
    return card


@router.delete("/{card_id}")
def delete_card(card_id: int, db: Session = Depends(get_db)):
    """Delete a specific card."""
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    db.delete(card)
    db.commit()
    return {"message": "Card deleted successfully"}


@router.get("/stats/summary")
def get_cards_summary(db: Session = Depends(get_db)):
    """Get summary statistics of cards."""
    stats = {}
    
    # Count by status
    for status in CardStatus:
        count = db.query(Card).filter(Card.status == status).count()
        stats[status.value] = count
    
    # Total cards
    stats["total"] = db.query(Card).count()
    
    # Cards due for follow-up
    stats["due_followup"] = db.query(Card).filter(
        Card.next_followup_date <= datetime.now(),
        Card.status != CardStatus.REACHED_OUT
    ).count()
    
    return stats
