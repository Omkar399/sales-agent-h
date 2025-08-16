"""HubSpot CRM integration tool for the AI agent."""

import json
from typing import Dict, List, Any, Optional
import httpx
from ...config import settings


class HubSpotTool:
    """HubSpot CRM API integration tool."""
    
    def __init__(self):
        self.api_key = settings.HUBSPOT_API_KEY
        self.base_url = "https://api.hubapi.com"
    
    def get_function_schemas(self) -> List[Dict[str, Any]]:
        """Get function schemas for Gemini function calling."""
        return [
            {
                "name": "get_contact_info",
                "description": "Get detailed information about a contact from HubSpot CRM",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "Email address of the contact"
                        },
                        "contact_id": {
                            "type": "string",
                            "description": "HubSpot contact ID (alternative to email)"
                        }
                    }
                }
            },
            {
                "name": "search_contacts",
                "description": "Search for contacts in HubSpot CRM",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (name, company, email, etc.)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_company_info",
                "description": "Get information about a company from HubSpot CRM",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "company_name": {
                            "type": "string",
                            "description": "Name of the company"
                        },
                        "company_id": {
                            "type": "string",
                            "description": "HubSpot company ID (alternative to company name)"
                        }
                    }
                }
            },
            {
                "name": "get_recent_activities",
                "description": "Get recent activities for a contact or company",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "contact_email": {
                            "type": "string",
                            "description": "Email of the contact to get activities for"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of activities to return",
                            "default": 20
                        }
                    },
                    "required": ["contact_email"]
                }
            },
            {
                "name": "create_note",
                "description": "Create a note for a contact in HubSpot",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "contact_email": {
                            "type": "string",
                            "description": "Email of the contact"
                        },
                        "note_content": {
                            "type": "string",
                            "description": "Content of the note"
                        },
                        "note_title": {
                            "type": "string",
                            "description": "Title of the note",
                            "default": "AI Assistant Note"
                        }
                    },
                    "required": ["contact_email", "note_content"]
                }
            }
        ]
    
    async def get_contact_info(self, email: Optional[str] = None, contact_id: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed contact information from HubSpot."""
        try:
            if not self.api_key:
                return self._mock_contact_response(email)
            
            # In production, this would make actual HubSpot API calls
            # For now, return mock data
            return self._mock_contact_response(email)
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get contact info: {str(e)}"
            }
    
    async def search_contacts(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search for contacts in HubSpot."""
        try:
            if not self.api_key:
                return self._mock_search_response(query, limit)
            
            # Mock search results
            return self._mock_search_response(query, limit)
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to search contacts: {str(e)}"
            }
    
    async def get_company_info(self, company_name: Optional[str] = None, company_id: Optional[str] = None) -> Dict[str, Any]:
        """Get company information from HubSpot."""
        try:
            if not self.api_key:
                return self._mock_company_response(company_name)
            
            # Mock company data
            return self._mock_company_response(company_name)
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get company info: {str(e)}"
            }
    
    async def get_recent_activities(self, contact_email: str, limit: int = 20) -> Dict[str, Any]:
        """Get recent activities for a contact."""
        try:
            if not self.api_key:
                return self._mock_activities_response(contact_email, limit)
            
            # Mock activities data
            return self._mock_activities_response(contact_email, limit)
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get recent activities: {str(e)}"
            }
    
    async def create_note(self, contact_email: str, note_content: str, note_title: str = "AI Assistant Note") -> Dict[str, Any]:
        """Create a note for a contact in HubSpot."""
        try:
            if not self.api_key:
                return self._mock_note_creation_response(contact_email, note_content, note_title)
            
            # Mock note creation
            return self._mock_note_creation_response(contact_email, note_content, note_title)
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create note: {str(e)}"
            }
    
    def _mock_contact_response(self, email: Optional[str]) -> Dict[str, Any]:
        """Generate mock contact response."""
        return {
            "status": "success",
            "contact": {
                "id": "12345",
                "email": email or "john.doe@example.com",
                "firstname": "John",
                "lastname": "Doe",
                "company": "Example Corp",
                "jobtitle": "Marketing Director",
                "phone": "+1-555-123-4567",
                "lifecyclestage": "lead",
                "hubspot_owner_id": "67890",
                "createdate": "2024-01-01T10:00:00Z",
                "lastmodifieddate": "2024-01-15T15:30:00Z",
                "last_activity_date": "2024-01-14T09:15:00Z"
            },
            "message": f"Retrieved contact information for {email or 'contact'}"
        }
    
    def _mock_search_response(self, query: str, limit: int) -> Dict[str, Any]:
        """Generate mock search response."""
        return {
            "status": "success",
            "results": [
                {
                    "id": "12345",
                    "email": "john.doe@example.com",
                    "name": "John Doe",
                    "company": "Example Corp",
                    "jobtitle": "Marketing Director"
                },
                {
                    "id": "12346",
                    "email": "jane.smith@testco.com",
                    "name": "Jane Smith", 
                    "company": "Test Co",
                    "jobtitle": "Sales Manager"
                }
            ],
            "total": 2,
            "message": f"Found contacts matching '{query}'"
        }
    
    def _mock_company_response(self, company_name: Optional[str]) -> Dict[str, Any]:
        """Generate mock company response."""
        return {
            "status": "success",
            "company": {
                "id": "98765",
                "name": company_name or "Example Corp",
                "domain": "example.com",
                "industry": "Technology",
                "city": "San Francisco",
                "state": "California",
                "country": "United States",
                "numberofemployees": "50-200",
                "annualrevenue": "$5M-$10M",
                "createdate": "2024-01-01T10:00:00Z"
            },
            "message": f"Retrieved company information for {company_name or 'company'}"
        }
    
    def _mock_activities_response(self, contact_email: str, limit: int) -> Dict[str, Any]:
        """Generate mock activities response."""
        return {
            "status": "success",
            "activities": [
                {
                    "id": "activity_1",
                    "type": "EMAIL",
                    "timestamp": "2024-01-14T09:15:00Z",
                    "subject": "Follow-up on our conversation",
                    "body": "Hi John, Following up on our discussion..."
                },
                {
                    "id": "activity_2",
                    "type": "CALL",
                    "timestamp": "2024-01-12T14:30:00Z",
                    "subject": "Sales call",
                    "duration": 1800,
                    "outcome": "Connected"
                }
            ],
            "total": 2,
            "message": f"Retrieved recent activities for {contact_email}"
        }
    
    def _mock_note_creation_response(self, contact_email: str, note_content: str, note_title: str) -> Dict[str, Any]:
        """Generate mock note creation response."""
        return {
            "status": "success",
            "note": {
                "id": "note_123",
                "title": note_title,
                "content": note_content,
                "contact_email": contact_email,
                "created_at": "2024-01-15T16:00:00Z"
            },
            "message": f"Note created successfully for {contact_email}"
        }
