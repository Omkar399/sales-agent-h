"""Gemini AI client for intelligent conversation and function calling."""

import json
import asyncio
from typing import Dict, List, Any, Optional
from google import genai
from google.genai import types
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models.cards import Card, CardStatus
from .tools import AVAILABLE_TOOLS, TOOL_FUNCTIONS


class GeminiClient:
    """Gemini AI client with agentic capabilities."""
    
    def __init__(self):
        """Initialize Gemini client with API key and tools."""
        if not settings.GEMINI_API_KEY:
            self.client = None
            self.tools = None
            return
        
        try:
            # Initialize the client
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            # Convert tool functions to the new format
            function_declarations = []
            for tool in AVAILABLE_TOOLS.values():
                schemas = tool.get_function_schemas()
                for schema in schemas:
                    # Convert from old format to new types.FunctionDeclaration
                    func_decl = types.FunctionDeclaration(
                        name=schema["name"],
                        description=schema["description"],
                        parameters=schema["parameters"]
                    )
                    function_declarations.append(func_decl)
            
            # Create tools configuration
            self.tools = [types.Tool(function_declarations=function_declarations)] if function_declarations else []
            
        except Exception as e:
            print(f"Warning: Failed to initialize Gemini client: {e}")
            self.client = None
            self.tools = None
        
        # System prompt for the sales agent
        self.system_prompt = """You are an intelligent AI sales assistant for a CRM dashboard. Your role is to help sales teams manage customer relationships effectively.

You have access to the following tools:
1. Google Calendar - Schedule meetings with customers
2. HubSpot CRM - Fetch customer data and company information  
3. Email Service - Send personalized and bulk emails

Your capabilities include:
- Analyzing customer data and providing insights
- Scheduling meetings and follow-ups
- Drafting and sending personalized emails
- Updating customer statuses and notes
- Providing sales recommendations

Always be helpful, professional, and proactive. When users ask about customers, provide comprehensive information and suggest next steps. Use the available tools to perform actions automatically when appropriate.

Current context: You're helping manage a Kanban-style sales board with columns: To Reach | In Progress | Reached Out | Follow-up"""
    
    async def chat(self, message: str, conversation_history: List[Dict[str, str]] = None, db: Session = None) -> Dict[str, Any]:
        """Process a chat message with potential function calling."""
        if not self.client:
            return {
                "status": "error",
                "message": "AI service is not available. Please check GEMINI_API_KEY configuration.",
                "response": "I'm sorry, but the AI service is currently not available. Please check the configuration."
            }
        
        try:
            # Create the full prompt with conversation context
            full_prompt = self.system_prompt + "\n\n"
            if conversation_history:
                for msg in conversation_history[-10:]:
                    full_prompt += f"{msg['role']}: {msg['content']}\n"
            full_prompt += f"user: {message}"
            
            # Create generation config with tools
            config = types.GenerateContentConfig(tools=self.tools) if self.tools else None
            
            # Generate response
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-1.5-pro",
                contents=full_prompt,
                config=config
            )
            
            # Check if function calls were made
            function_calls = []
            if response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        function_calls.append(part.function_call)
            
            # Execute function calls if any
            function_results = []
            if function_calls:
                for function_call in function_calls:
                    result = await self._execute_function_call(function_call, db)
                    function_results.append(result)
            
            # Get the text response
            response_text = response.text if response.text else "I've executed the requested actions."
            
            return {
                "status": "success",
                "response": response_text,
                "function_calls": function_calls,
                "function_results": function_results,
                "conversation_id": None  # Could implement conversation persistence
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to process chat message: {str(e)}",
                "response": "I'm sorry, I encountered an error processing your request. Please try again."
            }
    
    async def _execute_function_call(self, function_call, db: Session = None) -> Dict[str, Any]:
        """Execute a function call from Gemini."""
        try:
            function_name = function_call.name
            function_args = dict(function_call.args)
            
            # Calendar tools
            if function_name == "schedule_meeting":
                return await AVAILABLE_TOOLS["calendar"].schedule_meeting(**function_args)
            elif function_name == "get_available_slots":
                return await AVAILABLE_TOOLS["calendar"].get_available_slots(**function_args)
            elif function_name == "get_upcoming_meetings":
                return await AVAILABLE_TOOLS["calendar"].get_upcoming_meetings(**function_args)
            
            # HubSpot tools
            elif function_name == "get_contact_info":
                return await AVAILABLE_TOOLS["hubspot"].get_contact_info(**function_args)
            elif function_name == "search_contacts":
                return await AVAILABLE_TOOLS["hubspot"].search_contacts(**function_args)
            elif function_name == "get_company_info":
                return await AVAILABLE_TOOLS["hubspot"].get_company_info(**function_args)
            elif function_name == "get_recent_activities":
                return await AVAILABLE_TOOLS["hubspot"].get_recent_activities(**function_args)
            elif function_name == "create_note":
                return await AVAILABLE_TOOLS["hubspot"].create_note(**function_args)
            
            # Email tools
            elif function_name == "send_personalized_email":
                return await AVAILABLE_TOOLS["email"].send_personalized_email(**function_args, db=db)
            elif function_name == "send_bulk_emails":
                return await AVAILABLE_TOOLS["email"].send_bulk_emails(**function_args, db=db)
            elif function_name == "create_email_template":
                return await AVAILABLE_TOOLS["email"].create_email_template(**function_args)
            elif function_name == "get_email_analytics":
                return await AVAILABLE_TOOLS["email"].get_email_analytics(**function_args)
            
            else:
                return {
                    "status": "error",
                    "message": f"Unknown function: {function_name}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error executing function {function_call.name}: {str(e)}"
            }
    
    async def get_customer_insights(self, customer_data: Dict[str, Any], db: Session = None) -> Dict[str, Any]:
        """Get AI insights about a specific customer."""
        try:
            prompt = f"""
            Analyze this customer data and provide insights:
            
            Customer: {customer_data.get('customer_name', 'Unknown')}
            Company: {customer_data.get('company', 'Unknown')}
            Email: {customer_data.get('email', 'Unknown')}
            Status: {customer_data.get('status', 'Unknown')}
            Priority: {customer_data.get('priority', 'Unknown')}
            Notes: {customer_data.get('notes', 'None')}
            Last Contact: {customer_data.get('last_contact_date', 'Never')}
            Next Follow-up: {customer_data.get('next_followup_date', 'Not scheduled')}
            
            Please provide:
            1. Customer analysis and insights
            2. Recommended next actions
            3. Suggested email templates or approaches
            4. Optimal follow-up timing
            """
            
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            
            return {
                "status": "success",
                "insights": response.text,
                "customer_id": customer_data.get('id'),
                "customer_name": customer_data.get('customer_name')
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to generate customer insights: {str(e)}"
            }
    
    async def suggest_email_content(self, customer_data: Dict[str, Any], email_type: str = "follow_up") -> Dict[str, Any]:
        """Generate personalized email content suggestions."""
        try:
            prompt = f"""
            Create a personalized {email_type} email for this customer:
            
            Customer: {customer_data.get('customer_name', 'Unknown')}
            Company: {customer_data.get('company', 'Unknown')}
            Current Status: {customer_data.get('status', 'Unknown')}
            Notes: {customer_data.get('notes', 'None')}
            
            Generate:
            1. Subject line (compelling and personalized)
            2. Email body (professional, personalized, and actionable)
            3. Call-to-action suggestions
            
            Keep it concise, professional, and focused on value.
            """
            
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            
            return {
                "status": "success",
                "email_content": response.text,
                "email_type": email_type,
                "customer_name": customer_data.get('customer_name')
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to generate email content: {str(e)}"
            }


# Global instance - always create, but may be non-functional without API key
try:
    gemini_client = GeminiClient()
except Exception as e:
    print(f"Warning: Failed to create Gemini client: {e}")
    gemini_client = None
