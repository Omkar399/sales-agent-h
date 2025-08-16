"""Google Calendar integration tool for the AI agent."""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import httpx
from ...config import settings


class CalendarTool:
    """Google Calendar API integration tool."""
    
    def __init__(self):
        self.credentials_path = settings.GOOGLE_CALENDAR_CREDENTIALS_PATH
        self.base_url = "https://www.googleapis.com/calendar/v3"
    
    def get_function_schemas(self) -> List[Dict[str, Any]]:
        """Get function schemas for Gemini function calling."""
        return [
            {
                "name": "schedule_meeting",
                "description": "Schedule a meeting with a customer in Google Calendar",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "customer_name": {
                            "type": "STRING",
                            "description": "Name of the customer"
                        },
                        "customer_email": {
                            "type": "STRING",
                            "description": "Email address of the customer"
                        },
                        "meeting_title": {
                            "type": "STRING",
                            "description": "Title of the meeting"
                        },
                        "meeting_description": {
                            "type": "STRING",
                            "description": "Description of the meeting"
                        },
                        "start_datetime": {
                            "type": "STRING",
                            "description": "Meeting start time in ISO format (e.g., 2024-01-15T14:00:00)"
                        },
                        "duration_minutes": {
                            "type": "INTEGER",
                            "description": "Meeting duration in minutes"
                        }
                    },
                    "required": ["customer_name", "customer_email", "meeting_title", "start_datetime"]
                }
            },
            {
                "name": "get_available_slots",
                "description": "Get available time slots for scheduling meetings",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "Date to check availability (YYYY-MM-DD format)"
                        },
                        "duration_minutes": {
                            "type": "integer",
                            "description": "Required meeting duration in minutes",
                            "default": 30
                        }
                    },
                    "required": ["date"]
                }
            },
            {
                "name": "get_upcoming_meetings",
                "description": "Get list of upcoming meetings for the next few days",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days_ahead": {
                            "type": "integer",
                            "description": "Number of days to look ahead",
                            "default": 7
                        }
                    }
                }
            }
        ]
    
    async def schedule_meeting(
        self,
        customer_name: str,
        customer_email: str,
        meeting_title: str,
        start_datetime: str,
        meeting_description: str = "",
        duration_minutes: int = 30
    ) -> Dict[str, Any]:
        """Schedule a meeting in Google Calendar."""
        try:
            # Parse start datetime
            start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
            end_dt = start_dt + timedelta(minutes=duration_minutes)
            
            # For now, return a mock response since we need proper OAuth setup
            # In production, this would use Google Calendar API
            meeting_data = {
                "status": "success",
                "meeting_id": f"mock_meeting_{datetime.now().timestamp()}",
                "meeting_url": f"https://meet.google.com/mock-meeting-{customer_name.lower().replace(' ', '-')}",
                "details": {
                    "title": meeting_title,
                    "customer": customer_name,
                    "customer_email": customer_email,
                    "start_time": start_dt.isoformat(),
                    "end_time": end_dt.isoformat(),
                    "duration_minutes": duration_minutes,
                    "description": meeting_description
                },
                "message": f"Meeting '{meeting_title}' scheduled with {customer_name} for {start_dt.strftime('%Y-%m-%d %H:%M')}"
            }
            
            return meeting_data
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to schedule meeting: {str(e)}"
            }
    
    async def get_available_slots(self, date: str, duration_minutes: int = 30) -> Dict[str, Any]:
        """Get available time slots for a given date."""
        try:
            # Mock available slots (in production, this would check actual calendar)
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
            
            # Generate mock available slots (9 AM to 5 PM, excluding lunch)
            slots = []
            base_datetime = datetime.combine(target_date, datetime.min.time().replace(hour=9))
            
            for hour in range(9, 17):  # 9 AM to 5 PM
                if hour == 12:  # Skip lunch hour
                    continue
                
                slot_time = base_datetime.replace(hour=hour)
                slots.append({
                    "start_time": slot_time.isoformat(),
                    "end_time": (slot_time + timedelta(minutes=duration_minutes)).isoformat(),
                    "available": True
                })
            
            return {
                "status": "success",
                "date": date,
                "available_slots": slots,
                "message": f"Found {len(slots)} available slots for {date}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get available slots: {str(e)}"
            }
    
    async def get_upcoming_meetings(self, days_ahead: int = 7) -> Dict[str, Any]:
        """Get upcoming meetings for the next few days."""
        try:
            # Mock upcoming meetings (in production, this would fetch from actual calendar)
            meetings = [
                {
                    "id": "mock_meeting_1",
                    "title": "Sales Call - ABC Corp",
                    "start_time": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
                    "attendees": ["john@abccorp.com"],
                    "status": "confirmed"
                },
                {
                    "id": "mock_meeting_2", 
                    "title": "Follow-up - XYZ Ltd",
                    "start_time": (datetime.now() + timedelta(days=2, hours=3)).isoformat(),
                    "attendees": ["sarah@xyzltd.com"],
                    "status": "confirmed"
                }
            ]
            
            return {
                "status": "success",
                "meetings": meetings,
                "count": len(meetings),
                "message": f"Found {len(meetings)} upcoming meetings in the next {days_ahead} days"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get upcoming meetings: {str(e)}"
            }
