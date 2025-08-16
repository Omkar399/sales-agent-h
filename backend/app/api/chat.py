"""API routes for AI chat functionality."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy.orm import Session
from collections import defaultdict, deque

from ..database import get_db
from ..ai.gemini_client import gemini_client
from ..models.cards import Card

router = APIRouter(prefix="/chat", tags=["chat"])

# Simple in-memory conversation storage (max 20 messages per conversation)
conversations: defaultdict = defaultdict(lambda: deque(maxlen=20))


class ChatMessage(BaseModel):
    """Chat message schema."""
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response schema."""
    response: str
    status: str
    function_calls: Optional[List] = None
    function_results: Optional[List] = None
    conversation_id: Optional[str] = None


class CustomerInsightRequest(BaseModel):
    """Customer insight request schema."""
    customer_id: int


class EmailSuggestionRequest(BaseModel):
    """Email suggestion request schema."""
    customer_id: int
    email_type: str = "follow_up"


# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.post("/message", response_model=ChatResponse)
async def send_message(chat_message: ChatMessage, db: Session = Depends(get_db)):
    """Send a message to the AI assistant."""
    if not gemini_client:
        raise HTTPException(
            status_code=503, 
            detail="AI service is not available. Please check GEMINI_API_KEY configuration."
        )
    
    try:
        # Get conversation ID (use "default" if not provided)
        conversation_id = chat_message.conversation_id or "default"
        
        # Get conversation history
        history = list(conversations[conversation_id])
        
        # Process the message with Gemini
        response = await gemini_client.chat(
            message=chat_message.message,
            conversation_history=history,
            db=db
        )
        
        # Store the conversation
        conversations[conversation_id].append({"role": "user", "content": chat_message.message})
        conversations[conversation_id].append({"role": "assistant", "content": response["response"]})
        
        return ChatResponse(
            response=response["response"],
            status=response["status"],
            function_calls=response.get("function_calls"),
            function_results=response.get("function_results"),
            conversation_id=conversation_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.post("/insights/{customer_id}")
async def get_customer_insights(customer_id: int, db: Session = Depends(get_db)):
    """Get AI-generated insights for a specific customer."""
    if not gemini_client:
        raise HTTPException(
            status_code=503,
            detail="AI service is not available. Please check GEMINI_API_KEY configuration."
        )
    
    # Get customer data
    customer = db.query(Card).filter(Card.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Convert to dict for AI processing
    customer_data = {
        "id": customer.id,
        "customer_name": customer.customer_name,
        "company": customer.company,
        "email": customer.email,
        "phone": customer.phone,
        "status": customer.status.value if customer.status else None,
        "priority": customer.priority.value if customer.priority else None,
        "notes": customer.notes,
        "assigned_to": customer.assigned_to,
        "last_contact_date": customer.last_contact_date.isoformat() if customer.last_contact_date else None,
        "next_followup_date": customer.next_followup_date.isoformat() if customer.next_followup_date else None,
        "created_at": customer.created_at.isoformat(),
        "updated_at": customer.updated_at.isoformat()
    }
    
    try:
        insights = await gemini_client.get_customer_insights(customer_data, db)
        return insights
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")


@router.post("/email-suggestion/{customer_id}")
async def get_email_suggestion(customer_id: int, email_type: str = "follow_up", db: Session = Depends(get_db)):
    """Get AI-generated email content suggestions for a customer."""
    if not gemini_client:
        raise HTTPException(
            status_code=503,
            detail="AI service is not available. Please check GEMINI_API_KEY configuration."
        )
    
    # Get customer data
    customer = db.query(Card).filter(Card.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Convert to dict for AI processing
    customer_data = {
        "id": customer.id,
        "customer_name": customer.customer_name,
        "company": customer.company,
        "email": customer.email,
        "status": customer.status.value if customer.status else None,
        "notes": customer.notes
    }
    
    try:
        suggestion = await gemini_client.suggest_email_content(customer_data, email_type)
        return suggestion
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate email suggestion: {str(e)}")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    """WebSocket endpoint for real-time chat."""
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            if not gemini_client:
                await manager.send_personal_message(
                    "AI service is not available. Please check configuration.",
                    websocket
                )
                continue
            
            try:
                # Process message with AI
                response = await gemini_client.chat(message=data, db=db)
                
                # Send response back to client
                await manager.send_personal_message(
                    response["response"],
                    websocket
                )
                
            except Exception as e:
                await manager.send_personal_message(
                    f"Error processing message: {str(e)}",
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
