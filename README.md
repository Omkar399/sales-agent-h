# 🤖 Sales Agent Dashboard

An AI-powered sales dashboard with Kanban board interface and intelligent assistant capabilities. Built with FastAPI, React, and Google Gemini AI.

## ✨ Features

### 🎯 Core Features
- **Kanban Board**: Jira-like interface with 4 columns (To Reach | In Progress | Reached Out | Follow-up)
- **Drag & Drop**: Move customer cards between stages seamlessly
- **AI Assistant**: Gemini-powered chatbot with agentic capabilities
- **Real-time Updates**: WebSocket integration for live synchronization

### 🤖 AI Capabilities
- **Smart Conversations**: Context-aware responses about customers
- **Calendar Integration**: Schedule meetings directly from chat
- **CRM Sync**: Pull/push data to HubSpot
- **Email Automation**: Send personalized and bulk emails
- **Customer Insights**: AI-generated analysis and recommendations

### 🛠 Tools Integration
- **Google Calendar**: Meeting scheduling and availability checking
- **HubSpot CRM**: Customer and company data management
- **Gmail SMTP**: Send emails directly from your Gmail account
- **Email Automation**: Bulk and personalized email campaigns with template support
- **Customer Lookup**: Send emails by customer name with automatic database lookup

## 🏗 Architecture

```
sales-agent-h/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── api/            # API routes
│   │   ├── ai/             # Gemini AI integration
│   │   │   ├── gemini_client.py
│   │   │   └── tools/      # AI tool definitions
│   │   └── database.py     # Database configuration
│   └── pyproject.toml      # Python dependencies
└── frontend/         # React frontend
    ├── src/
    │   ├── components/     # React components
    │   ├── services/       # API services
    │   ├── types/          # TypeScript types
    │   └── lib/           # Utilities
    └── package.json       # Node.js dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- UV package manager
- Google Gemini API key

### 1. Clone and Setup Environment

```bash
git clone <repository-url>
cd sales-agent-h

# Copy environment file
cp backend/env.example backend/.env
```

### 2. Configure Environment Variables

Edit `backend/.env`:

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# For Gmail Email Functionality
GMAIL_EMAIL=your_gmail_address@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password_here

# Optional (for full functionality)
HUBSPOT_API_KEY=your_hubspot_api_key_here
GOOGLE_CALENDAR_CREDENTIALS_PATH=path/to/credentials.json
```

**📧 Gmail Setup**: For email functionality, see [GMAIL_SETUP.md](GMAIL_SETUP.md) for detailed Gmail configuration instructions.

### 3. Start Backend

```bash
cd backend

# Install dependencies with UV
uv sync

# Run the FastAPI server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: http://localhost:8000

### 4. Start Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at: http://localhost:3000

## 📋 API Documentation

Once the backend is running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Overview**: http://localhost:8000

### Key Endpoints

#### Cards Management
- `GET /api/cards` - Get all customer cards
- `POST /api/cards` - Create new customer card
- `PUT /api/cards/{id}` - Update customer card
- `PATCH /api/cards/{id}/status` - Update card status
- `DELETE /api/cards/{id}` - Delete customer card
- `GET /api/cards/stats/summary` - Get cards statistics

#### AI Assistant
- `POST /api/chat/message` - Send message to AI assistant
- `POST /api/chat/insights/{customer_id}` - Get customer insights
- `POST /api/chat/email-suggestion/{customer_id}` - Get email suggestions
- `WebSocket /api/chat/ws` - Real-time chat connection

## 🔧 Configuration

### Database
- **Type**: SQLite (default)
- **Location**: `backend/sales_agent.db`
- **Auto-created**: Yes, on first run

### AI Tools
The AI assistant has access to:

1. **Calendar Tool** (`calendar_tool.py`)
   - Schedule meetings
   - Check availability
   - Get upcoming meetings

2. **HubSpot Tool** (`hubspot_tool.py`)
   - Fetch contact information
   - Search contacts
   - Get company data
   - Create notes

3. **Email Tool** (`email_tool.py`)
   - Send personalized emails
   - Bulk email campaigns
   - Create templates
   - Get analytics

## 🎨 UI Components

### Kanban Board
- **Responsive Design**: Works on desktop and tablet
- **Drag & Drop**: React Beautiful DND
- **Real-time Updates**: WebSocket synchronization
- **Search & Filter**: Find customers quickly

### Chat Modal
- **Context-Aware**: Knows about selected customer
- **Function Calling**: AI can use tools automatically
- **Quick Actions**: Generate insights, schedule meetings
- **Message History**: Conversation persistence

### Customer Cards
- **Rich Information**: Name, company, contact details
- **Priority Badges**: Visual priority indicators
- **Action Buttons**: Edit, delete, chat
- **Status Tracking**: Last contact, follow-up dates

## 🔌 Integrations

### Google Calendar
1. Enable Google Calendar API
2. Download credentials.json
3. Set `GOOGLE_CALENDAR_CREDENTIALS_PATH` in .env

### HubSpot CRM
1. Get HubSpot API key
2. Set `HUBSPOT_API_KEY` in .env

### Email Service (SendGrid)
1. Create SendGrid account
2. Generate API key
3. Set `SENDGRID_API_KEY` and `FROM_EMAIL` in .env

## 🧪 Development

### Backend Development

```bash
cd backend

# Run with auto-reload
uv run uvicorn app.main:app --reload

# Run tests (when implemented)
uv run pytest

# Code formatting
uv run black app/
uv run isort app/
```

### Frontend Development

```bash
cd frontend

# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Linting
npm run lint
```

## 🚀 Deployment

### Backend Deployment
```bash
cd backend

# Build
uv build

# Run production server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Deployment
```bash
cd frontend

# Build for production
npm run build

# Serve static files (dist/ directory)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check API docs at `/docs`
- **Issues**: Create GitHub issues for bugs
- **Features**: Submit feature requests via issues

## 🎯 Roadmap

- [ ] User authentication and authorization
- [ ] Multi-tenant support
- [ ] Advanced analytics dashboard
- [ ] Mobile app support
- [ ] Slack/Teams integration
- [ ] Custom AI tool creation
- [ ] Email template builder
- [ ] Advanced filtering and search
- [ ] Data export/import
- [ ] Webhook support

---

Built with ❤️ using FastAPI, React, and Google Gemini AI
