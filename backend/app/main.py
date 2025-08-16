"""FastAPI main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from .config import settings
from .database import init_db
from .api.cards import router as cards_router
from .api.chat import router as chat_router

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cards_router, prefix="/api")
app.include_router(chat_router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API information."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sales Agent Dashboard API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .header { color: #2563eb; }
            .endpoint { background: #f3f4f6; padding: 10px; margin: 10px 0; border-radius: 5px; }
            .method { color: #059669; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1 class="header">🤖 Sales Agent Dashboard API</h1>
        <p>AI-powered sales dashboard with Kanban board and intelligent assistant</p>
        
        <h2>📋 Card Management</h2>
        <div class="endpoint">
            <span class="method">GET</span> /api/cards - Get all customer cards
        </div>
        <div class="endpoint">
            <span class="method">POST</span> /api/cards - Create a new customer card
        </div>
        <div class="endpoint">
            <span class="method">GET</span> /api/cards/{id} - Get specific customer card
        </div>
        <div class="endpoint">
            <span class="method">PUT</span> /api/cards/{id} - Update customer card
        </div>
        <div class="endpoint">
            <span class="method">PATCH</span> /api/cards/{id}/status - Update card status
        </div>
        <div class="endpoint">
            <span class="method">DELETE</span> /api/cards/{id} - Delete customer card
        </div>
        <div class="endpoint">
            <span class="method">GET</span> /api/cards/stats/summary - Get cards statistics
        </div>
        
        <h2>🤖 AI Assistant</h2>
        <div class="endpoint">
            <span class="method">POST</span> /api/chat/message - Send message to AI assistant
        </div>
        <div class="endpoint">
            <span class="method">POST</span> /api/chat/insights/{customer_id} - Get customer insights
        </div>
        <div class="endpoint">
            <span class="method">POST</span> /api/chat/email-suggestion/{customer_id} - Get email suggestions
        </div>
        <div class="endpoint">
            <span class="method">WebSocket</span> /api/chat/ws - Real-time chat connection
        </div>
        
        <h2>🔗 Documentation</h2>
        <p>
            <a href="/docs">📖 Interactive API Docs (Swagger)</a><br>
            <a href="/redoc">📚 ReDoc Documentation</a>
        </p>
        
        <h2>🛠 Tools Available to AI</h2>
        <ul>
            <li>📅 Google Calendar - Schedule meetings and check availability</li>
            <li>🏢 HubSpot CRM - Fetch customer and company data</li>
            <li>📧 Email Service - Send personalized and bulk emails</li>
        </ul>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "ai_enabled": bool(settings.GEMINI_API_KEY)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
