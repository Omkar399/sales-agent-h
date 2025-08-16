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
1. Google Calendar - Schedule meetings with customers, check upcoming meetings, get availability
2. HubSpot CRM - Fetch customer data and company information  
3. Gmail API - Send real emails directly from Gmail account

IMPORTANT CALENDAR BEHAVIOR:
- When users ask for "meetings today" or "today's meetings", use get_upcoming_meetings with days_ahead=0
- When users ask for "this week's meetings", use get_upcoming_meetings with days_ahead=7
- When users ask for availability or free slots, use get_available_slots with proper YYYY-MM-DD date format
- Always convert relative dates like "today" to proper YYYY-MM-DD format before calling functions

IMPORTANT EMAIL BEHAVIOR:
- When users ask to send an email to a PERSON (by name), ALWAYS use lookup_and_prepare_email first to find them in HubSpot and get confirmation
- When users provide a direct EMAIL ADDRESS, you can use send_personalized_email directly
- For HubSpot contact lookups, show the contact details and ask for confirmation before sending
- Compose professional email content based on the user's intent
- For meeting requests, create appropriate subject lines like "Meeting Request" and professional messages
- SEND REAL EMAILS using Gmail API, not mock responses

Your capabilities include:
- Analyzing customer data and providing insights
- Scheduling meetings and follow-ups
- Drafting and sending personalized emails via Gmail
- Updating customer statuses and notes
- Providing sales recommendations

Always be helpful, professional, and proactive. When users request email actions, prioritize sending actual emails over searching for contacts.

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
                    
                    # Include function call details for assistant messages
                    if msg['role'] == 'assistant' and msg.get('function_calls') and msg.get('function_results'):
                        full_prompt += f"[Previous function calls: {msg['function_calls']}]\n"
                        full_prompt += f"[Function results: {msg['function_results']}]\n"
            
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
            
            # Create a natural language response based on function results
            if function_calls and function_results:
                natural_response = self._create_natural_response(function_calls, function_results)
                response_text = natural_response
            else:
                response_text = response.text if response.text else "I'm here to help! What would you like me to do?"
            
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
            elif function_name == "check_meetings_with_person":
                return await AVAILABLE_TOOLS["calendar"].check_meetings_with_person(**function_args)
            
            # HubSpot tools
            elif function_name == "get_all_contacts":
                return await AVAILABLE_TOOLS["hubspot"].get_all_contacts(**function_args)
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
            elif function_name == "lookup_and_prepare_email":
                return await AVAILABLE_TOOLS["email"].lookup_and_prepare_email(**function_args)
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
    
    def _create_natural_response(self, function_calls: List, function_results: List) -> str:
        """Create a natural language response based on function calls and results."""
        if not function_calls or not function_results:
            return "I've completed the requested action."
        
        responses = []
        
        for i, (call, result) in enumerate(zip(function_calls, function_results)):
            function_name = call.name
            
            if function_name == "lookup_and_prepare_email":
                if result.get("status") == "ready_to_send":
                    responses.append(result.get("message", "Contact found and email prepared."))
                elif result.get("status") == "not_found":
                    responses.append(result.get("message", "Contact not found in HubSpot."))
                elif result.get("status") == "no_email":
                    responses.append(result.get("message", "Contact found but no email address available."))
                else:
                    error_msg = result.get("message", "Unknown error")
                    responses.append(f"❌ I wasn't able to lookup the contact. {error_msg}")
            
            elif function_name == "send_personalized_email":
                if result.get("status") == "success":
                    to_name = result.get("to_name", "the recipient")
                    to_email = result.get("to", "")
                    subject = result.get("subject", "")
                    responses.append(f"✅ I've successfully sent an email to {to_name} ({to_email}) with the subject '{subject}'. The email has been delivered via Gmail.")
                else:
                    error_msg = result.get("message", "Unknown error")
                    responses.append(f"❌ I wasn't able to send the email. {error_msg}")
            
            elif function_name == "send_bulk_emails":
                if result.get("status") == "success":
                    sent_count = result.get("emails_sent", 0)
                    total_count = result.get("recipients_count", 0)
                    campaign_name = result.get("campaign_name", "email campaign")
                    responses.append(f"✅ I've successfully sent the {campaign_name} to {sent_count} out of {total_count} recipients.")
                else:
                    error_msg = result.get("message", "Unknown error")
                    responses.append(f"❌ I wasn't able to send the bulk emails. {error_msg}")
            
            elif function_name == "schedule_meeting":
                if result.get("status") == "success":
                    title = result.get("title", "meeting")
                    date = result.get("date", "")
                    time = result.get("start_time", "")
                    customer = result.get("customer_email", "")
                    responses.append(f"✅ I've successfully scheduled '{title}' with {customer} on {date} at {time}. The meeting has been added to your Google Calendar.")
                else:
                    error_msg = result.get("message", "Unknown error")
                    responses.append(f"❌ I wasn't able to schedule the meeting. {error_msg}")
            
            elif function_name == "get_available_slots":
                if result.get("status") == "success":
                    date = result.get("date", "")
                    slots = result.get("available_slots", [])
                    responses.append(f"I found {len(slots)} available time slots on {date}: {', '.join(slots[:5])}{'...' if len(slots) > 5 else ''}")
                else:
                    error_msg = result.get("message", "Unknown error")
                    responses.append(f"I wasn't able to check availability. {error_msg}")
            
            elif function_name == "get_upcoming_meetings":
                # Calendar tool now returns natural language strings directly
                if isinstance(result, str):
                    responses.append(result)
                elif result.get("status") == "success":
                    count = result.get("meetings_found", 0)
                    days = result.get("days_ahead", 7)
                    responses.append(f"You have {count} upcoming meetings in the next {days} days.")
                else:
                    error_msg = result.get("message", "Unknown error")
                    responses.append(f"I wasn't able to retrieve your meetings. {error_msg}")
            
            elif function_name == "check_meetings_with_person":
                # Calendar tool now returns natural language strings directly
                if isinstance(result, str):
                    responses.append(result)
                elif result.get("status") == "success":
                    email = result.get("email", "")
                    count = result.get("meetings_found", 0)
                    if count > 0:
                        responses.append(f"You have {count} upcoming meetings with {email}.")
                    else:
                        responses.append(f"You don't have any upcoming meetings with {email}.")
                else:
                    error_msg = result.get("message", "Unknown error")
                    responses.append(f"I wasn't able to check meetings with that person. {error_msg}")
            
            elif function_name == "get_all_contacts":
                if result.get("status") == "success":
                    count = result.get("count", 0)
                    contacts = result.get("contacts", [])
                    if count > 0:
                        # Show first few contact names as examples
                        contact_names = [contact.get("name", "Unknown") for contact in contacts[:3]]
                        names_preview = ", ".join(contact_names)
                        if count > 3:
                            names_preview += f" and {count - 3} more"
                        responses.append(f"📋 I found {count} contacts in your HubSpot CRM. Here are some examples: {names_preview}. The contacts include their names, emails, companies, job titles, and other relevant information.")
                    else:
                        responses.append("I didn't find any contacts in your HubSpot CRM.")
                else:
                    error_msg = result.get("message", "Unknown error")
                    responses.append(f"❌ I wasn't able to retrieve your HubSpot contacts. {error_msg}")
            
            elif function_name in ["search_contacts", "get_contact_info"]:
                if result.get("status") == "success":
                    if function_name == "search_contacts":
                        total = result.get("total", 0)
                        responses.append(f"I found {total} contacts matching your search.")
                    else:
                        contact_name = result.get("contact", {}).get("firstname", "the contact")
                        responses.append(f"I've retrieved the information for {contact_name}.")
                else:
                    error_msg = result.get("message", "Unknown error")
                    responses.append(f"I wasn't able to find the contact information. {error_msg}")
            
            else:
                # Generic response for other functions
                if result.get("status") == "success":
                    responses.append("✅ I've completed the requested action successfully.")
                else:
                    error_msg = result.get("message", "Unknown error")
                    responses.append(f"❌ I wasn't able to complete the action. {error_msg}")
        
        return " ".join(responses)
    
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
