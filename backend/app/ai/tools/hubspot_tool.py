"""HubSpot CRM integration tool for the AI agent."""

import os
from typing import Dict, List, Any, Optional
from hubspot import HubSpot
from ...config import settings


class HubSpotTool:
    """HubSpot CRM API integration tool."""
    
    def __init__(self):
        self.access_token = settings.HUBSPOT_ACCESS_TOKEN
        self.client = None
        self.connected = False
        
        if self.access_token:
            try:
                self.client = HubSpot(access_token=self.access_token)
                # Test connection
                test = self.client.crm.contacts.basic_api.get_page(limit=1)
                self.connected = True
                print("✅ HubSpot connected successfully")
            except Exception as e:
                print(f"❌ HubSpot connection failed: {e}")
                self.connected = False
    
    def get_function_schemas(self) -> List[Dict[str, Any]]:
        """Get function schemas for Gemini function calling."""
        return [
            {
                "name": "get_all_contacts",
                "description": "Get all real contacts from HubSpot CRM with their details",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of contacts to return",
                            "default": 50
                        }
                    }
                }
            },
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
    
    async def get_all_contacts(self, limit: int = 50) -> Dict[str, Any]:
        """Get all real contacts from HubSpot - no dummy data."""
        if not self.connected:
            return {
                "status": "error",
                "message": "HubSpot not connected. Check HUBSPOT_ACCESS_TOKEN in environment variables.",
                "contacts": []
            }
        
        try:
            response = self.client.crm.contacts.basic_api.get_page(
                limit=limit,
                properties=[
                    "firstname", 
                    "lastname", 
                    "email", 
                    "company", 
                    "phone",
                    "jobtitle",
                    "city",
                    "state",
                    "lifecyclestage",
                    "hubspot_owner_id",
                    "createdate",
                    "lastmodifieddate"
                ]
            )
            
            contacts = []
            for contact in response.results:
                props = contact.properties
                
                # Only add contacts with actual data (skip empty contacts)
                name = f"{props.get('firstname', '')} {props.get('lastname', '')}".strip()
                email = props.get('email', '')
                
                if name or email:  # Only include if has name or email
                    contacts.append({
                        'id': contact.id,
                        'name': name if name else 'No Name',
                        'email': email if email else '',
                        'company': props.get('company', ''),
                        'phone': props.get('phone', ''),
                        'job_title': props.get('jobtitle', ''),
                        'city': props.get('city', ''),
                        'state': props.get('state', ''),
                        'lifecycle_stage': props.get('lifecyclestage', ''),
                        'owner_id': props.get('hubspot_owner_id', ''),
                        'created_date': props.get('createdate', ''),
                        'last_modified_date': props.get('lastmodifieddate', '')
                    })
            
            print(f"📋 Retrieved {len(contacts)} real contacts from HubSpot")
            return {
                "status": "success",
                "connected": self.connected,
                "count": len(contacts),
                "contacts": contacts,
                "message": f"Retrieved {len(contacts)} real contacts from HubSpot"
            }
            
        except Exception as e:
            print(f"❌ Error retrieving contacts: {e}")
            return {
                "status": "error",
                "message": f"Failed to retrieve contacts: {str(e)}",
                "contacts": []
            }
    
    async def get_contact_info(self, email: Optional[str] = None, contact_id: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed contact information from HubSpot."""
        if not self.connected:
            return {
                "status": "error",
                "message": "HubSpot not connected. Check HUBSPOT_ACCESS_TOKEN in environment variables."
            }
        
        try:
            contact = None
            
            if contact_id:
                # Get contact by ID
                contact = self.client.crm.contacts.basic_api.get_by_id(
                    contact_id=contact_id,
                    properties=[
                        "firstname", "lastname", "email", "company", "phone",
                        "jobtitle", "city", "state", "lifecyclestage",
                        "hubspot_owner_id", "createdate", "lastmodifieddate"
                    ]
                )
            elif email:
                # Search for contact by email
                search_request = {
                    "filterGroups": [
                        {
                            "filters": [
                                {
                                    "propertyName": "email",
                                    "operator": "EQ",
                                    "value": email
                                }
                            ]
                        }
                    ],
                    "properties": [
                        "firstname", "lastname", "email", "company", "phone",
                        "jobtitle", "city", "state", "lifecyclestage",
                        "hubspot_owner_id", "createdate", "lastmodifieddate"
                    ],
                    "limit": 1
                }
                
                search_results = self.client.crm.contacts.search_api.do_search(
                    public_object_search_request=search_request
                )
                
                if search_results.results:
                    contact = search_results.results[0]
            
            if not contact:
                return {
                    "status": "error",
                    "message": f"Contact not found with {'email: ' + email if email else 'ID: ' + contact_id}"
                }
            
            props = contact.properties
            name = f"{props.get('firstname', '')} {props.get('lastname', '')}".strip()
            
            return {
                "status": "success",
                "contact": {
                    "id": contact.id,
                    "name": name if name else 'No Name',
                    "email": props.get('email', ''),
                    "company": props.get('company', ''),
                    "phone": props.get('phone', ''),
                    "job_title": props.get('jobtitle', ''),
                    "city": props.get('city', ''),
                    "state": props.get('state', ''),
                    "lifecycle_stage": props.get('lifecyclestage', ''),
                    "owner_id": props.get('hubspot_owner_id', ''),
                    "created_date": props.get('createdate', ''),
                    "last_modified_date": props.get('lastmodifieddate', '')
                },
                "message": f"Retrieved contact information for {email or contact_id}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get contact info: {str(e)}"
            }
    
    async def search_contacts(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search for contacts in HubSpot."""
        if not self.connected:
            return {
                "status": "error",
                "message": "HubSpot not connected. Check HUBSPOT_ACCESS_TOKEN in environment variables.",
                "results": []
            }
        
        try:
            # Search across multiple fields
            search_request = {
                "query": query,
                "properties": [
                    "firstname", "lastname", "email", "company", 
                    "phone", "jobtitle", "city", "state"
                ],
                "limit": limit
            }
            
            search_results = self.client.crm.contacts.search_api.do_search(
                public_object_search_request=search_request
            )
            
            contacts = []
            for contact in search_results.results:
                props = contact.properties
                name = f"{props.get('firstname', '')} {props.get('lastname', '')}".strip()
                
                contacts.append({
                    "id": contact.id,
                    "name": name if name else 'No Name',
                    "email": props.get('email', ''),
                    "company": props.get('company', ''),
                    "phone": props.get('phone', ''),
                    "job_title": props.get('jobtitle', ''),
                    "city": props.get('city', ''),
                    "state": props.get('state', '')
                })
            
            return {
                "status": "success",
                "results": contacts,
                "total": len(contacts),
                "message": f"Found {len(contacts)} contacts matching '{query}'"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to search contacts: {str(e)}",
                "results": []
            }
    
    async def get_company_info(self, company_name: Optional[str] = None, company_id: Optional[str] = None) -> Dict[str, Any]:
        """Get company information from HubSpot."""
        if not self.connected:
            return {
                "status": "error",
                "message": "HubSpot not connected. Check HUBSPOT_ACCESS_TOKEN in environment variables."
            }
        
        try:
            # TODO: Implement real company API calls
            return {
                "status": "info",
                "message": "Company info feature not yet implemented with real API calls"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get company info: {str(e)}"
            }
    
    async def get_recent_activities(self, contact_email: str, limit: int = 20) -> Dict[str, Any]:
        """Get recent activities for a contact."""
        if not self.connected:
            return {
                "status": "error",
                "message": "HubSpot not connected. Check HUBSPOT_ACCESS_TOKEN in environment variables."
            }
        
        try:
            # TODO: Implement real activities API calls
            return {
                "status": "info",
                "message": "Recent activities feature not yet implemented with real API calls"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get recent activities: {str(e)}"
            }
    
    async def create_note(self, contact_email: str, note_content: str, note_title: str = "AI Assistant Note") -> Dict[str, Any]:
        """Create a note for a contact in HubSpot."""
        if not self.connected:
            return {
                "status": "error",
                "message": "HubSpot not connected. Check HUBSPOT_ACCESS_TOKEN in environment variables."
            }
        
        try:
            # TODO: Implement real note creation API calls
            return {
                "status": "info",
                "message": "Note creation feature not yet implemented with real API calls"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create note: {str(e)}"
            }

