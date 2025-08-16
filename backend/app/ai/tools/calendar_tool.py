"""Google Calendar integration tool for the AI agent."""

import json
import os
import pickle
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from ...config import settings


class CalendarTool:
    """Google Calendar integration tool for scheduling and availability."""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/gmail.send']
    TOKEN_FILE = 'calendar_token.pickle'
    
    def __init__(self):
        self.credentials_path = settings.GOOGLE_CALENDAR_CREDENTIALS_PATH
        # Use Gmail credentials for Google Calendar (same Google Cloud project)
        self.client_id = settings.GMAIL_CLIENT_ID
        self.client_secret = settings.GMAIL_CLIENT_SECRET
        self.service = None
        self.work_start = time(9, 0)  # 9 AM
        self.work_end = time(17, 0)   # 5 PM
        self._initialize_service()
    
    def _get_credentials_config(self):
        """Get credentials either from file or environment variables"""
        if self.credentials_path and os.path.exists(self.credentials_path):
            return self.credentials_path
        
        if self.client_id and self.client_secret:
            credentials_dict = {
                "installed": {
                    "client_id": self.client_id,
                    "project_id": "sales-agent-calendar",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": self.client_secret,
                    "redirect_uris": ["http://localhost"]
                }
            }
            
            temp_file = 'temp_calendar_credentials.json'
            with open(temp_file, 'w') as f:
                json.dump(credentials_dict, f)
            return temp_file
        
        return None
    
    def _get_credentials(self):
        """Get Google Calendar API credentials"""
        creds = None
        
        if os.path.exists(self.TOKEN_FILE):
            with open(self.TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                credentials_source = self._get_credentials_config()
                if not credentials_source:
                    print("Google Calendar credentials not configured.")
                    return None
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_source, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
                
                if credentials_source == 'temp_calendar_credentials.json':
                    os.remove(credentials_source)
            
            with open(self.TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
        
        return creds
    
    def _initialize_service(self):
        """Initialize Google Calendar service"""
        try:
            creds = self._get_credentials()
            if creds:
                self.service = build('calendar', 'v3', credentials=creds)
                print("Google Calendar service initialized successfully!")
            else:
                print("Google Calendar service not initialized - credentials not available")
        except Exception as e:
            print(f"Failed to initialize Google Calendar service: {str(e)}")
            self.service = None
    
    def get_function_schemas(self) -> List[Dict[str, Any]]:
        """Get function schemas for Gemini function calling."""
        return [
            {
                "name": "schedule_meeting",
                "description": "Schedule a meeting with a customer in Google Calendar",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_email": {
                            "type": "string",
                            "description": "Customer email address"
                        },
                        "meeting_title": {
                            "type": "string",
                            "description": "Title of the meeting"
                        },
                        "date": {
                            "type": "string",
                            "description": "Meeting date in YYYY-MM-DD format"
                        },
                        "start_time": {
                            "type": "string",
                            "description": "Meeting start time in HH:MM format (24-hour)"
                        },
                        "duration_minutes": {
                            "type": "integer",
                            "description": "Meeting duration in minutes",
                            "default": 60
                        },
                        "description": {
                            "type": "string",
                            "description": "Meeting description or agenda"
                        }
                    },
                    "required": ["customer_email", "meeting_title", "date", "start_time"]
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
                            "description": "Date to check availability in YYYY-MM-DD format"
                        },
                        "duration_minutes": {
                            "type": "integer",
                            "description": "Required meeting duration in minutes",
                            "default": 60
                        }
                    },
                    "required": ["date"]
                }
            },
            {
                "name": "get_upcoming_meetings",
                "description": "Get upcoming meetings from Google Calendar",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days_ahead": {
                            "type": "integer",
                            "description": "Number of days ahead to look for meetings",
                            "default": 7
                        },
                        "customer_email": {
                            "type": "string",
                            "description": "Filter meetings with specific customer email (optional)"
                        }
                    }
                }
            },
            {
                "name": "check_meetings_with_person",
                "description": "Check for meetings with a specific person in the next 30 days",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "Email address of the person to check meetings with"
                        }
                    },
                    "required": ["email"]
                }
            }
        ]
    
    async def schedule_meeting(
        self,
        customer_email: str,
        meeting_title: str,
        date: str,
        start_time: str,
        duration_minutes: int = 60,
        description: str = ""
    ) -> Dict[str, Any]:
        """Schedule a meeting with a customer in Google Calendar."""
        try:
            if not self.service:
                return "Sorry, I can't access your Google Calendar right now. Please check your calendar credentials."
            
            # Parse date and time
            meeting_date = datetime.strptime(date, "%Y-%m-%d").date()
            meeting_time = datetime.strptime(start_time, "%H:%M").time()
            start_datetime = datetime.combine(meeting_date, meeting_time)
            end_datetime = start_datetime + timedelta(minutes=duration_minutes)
            
            # Create event
            event = {
                'summary': meeting_title,
                'description': description,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'America/New_York',  # You can make this configurable
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'America/New_York',
                },
                'attendees': [
                    {'email': customer_email},
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }
            
            created_event = self.service.events().insert(calendarId='primary', body=event).execute()
            
            return {
                "status": "success",
                "meeting_id": created_event['id'],
                "customer_email": customer_email,
                "title": meeting_title,
                "date": date,
                "start_time": start_time,
                "duration_minutes": duration_minutes,
                "description": description,
                "calendar_link": created_event.get('htmlLink', ''),
                "message": f"Meeting '{meeting_title}' scheduled with {customer_email} on {date} at {start_time}"
            }
            
        except HttpError as error:
            return {
                "status": "error",
                "message": f"Google Calendar API error: {error}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to schedule meeting: {str(e)}"
            }
    
    async def get_available_slots(self, date: str, duration_minutes: int = 60) -> Dict[str, Any]:
        """Get available time slots for scheduling meetings."""
        try:
            if not self.service:
                return "Sorry, I can't access your Google Calendar right now. Please check your calendar credentials."
            
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
            
            # Get busy times for the day
            start_of_day = datetime.combine(target_date, self.work_start)
            end_of_day = datetime.combine(target_date, self.work_end)
            
            freebusy_query = {
                'timeMin': start_of_day.isoformat() + 'Z',
                'timeMax': end_of_day.isoformat() + 'Z',
                'items': [{'id': 'primary'}]
            }
            
            freebusy_result = self.service.freebusy().query(body=freebusy_query).execute()
            busy_times = freebusy_result['calendars']['primary']['busy']
            
            # Calculate available slots
            available_slots = self._calculate_available_slots(
                start_of_day, end_of_day, busy_times, duration_minutes
            )
            
            return {
                "status": "success",
                "date": date,
                "duration_minutes": duration_minutes,
                "available_slots": available_slots,
                "work_hours": f"{self.work_start.strftime('%H:%M')}-{self.work_end.strftime('%H:%M')}",
                "timezone": "Local",
                "message": f"Found {len(available_slots)} available slots on {date}"
            }
            
        except HttpError as error:
            return {
                "status": "error",
                "message": f"Google Calendar API error: {error}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get availability: {str(e)}"
            }
    
    async def get_upcoming_meetings(self, days_ahead: int = 7, customer_email: str = None) -> Dict[str, Any]:
        """Get upcoming meetings from Google Calendar."""
        try:
            if not self.service:
                return "Sorry, I can't access your Google Calendar right now. Please check your calendar credentials."
            
            now = datetime.utcnow()
            if days_ahead == 0:
                # For today only, go to end of day instead of current time
                end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            else:
                end_date = now + timedelta(days=days_ahead)
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            meetings = []
            
            for event in events:
                meeting_info = self._extract_meeting_info(event)
                if meeting_info:
                    # Filter by customer email if provided
                    if customer_email:
                        attendees = event.get('attendees', [])
                        attendee_emails = [a.get('email', '').lower() for a in attendees]
                        if customer_email.lower() not in attendee_emails:
                            continue
                    
                    meetings.append(meeting_info)
            
            # Return natural language response
            if len(meetings) == 0:
                if days_ahead == 0:
                    return "You have no meetings scheduled for today."
                else:
                    return f"You have no meetings scheduled for the next {days_ahead} days."
            
            # Format meetings in natural language
            if days_ahead == 0:
                response = f"You have {len(meetings)} meeting{'s' if len(meetings) != 1 else ''} today:\n\n"
            else:
                response = f"You have {len(meetings)} upcoming meeting{'s' if len(meetings) != 1 else ''} in the next {days_ahead} days:\n\n"
            
            for i, meeting in enumerate(meetings, 1):
                attendees_str = ""
                if meeting['attendees']:
                    other_attendees = [email for email in meeting['attendees'] if 'omkarpodey@gmail.com' not in email.lower()]
                    if other_attendees:
                        attendees_str = f" with {', '.join(other_attendees)}"
                
                response += f"{i}. **{meeting['title']}**\n"
                response += f"   📅 {meeting['date']} at {meeting['time']}{attendees_str}\n"
                if meeting['description']:
                    response += f"   📝 {meeting['description']}\n"
                response += "\n"
            
            return response.strip()
            
        except HttpError as error:
            return f"Sorry, I encountered an error accessing your Google Calendar: {error}"
        except Exception as e:
            return f"Sorry, I couldn't retrieve your meetings: {str(e)}"
    
    async def check_meetings_with_person(self, email: str) -> Dict[str, Any]:
        """Check for meetings with a specific person in the next 30 days."""
        try:
            if not self.service:
                return "Sorry, I can't access your Google Calendar right now. Please check your calendar credentials."
            
            now = datetime.utcnow()
            end_date = now + timedelta(days=30)
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            matching_meetings = []
            
            for event in events:
                attendees = event.get('attendees', [])
                attendee_emails = [attendee.get('email', '').lower() for attendee in attendees]
                
                if email.lower() in attendee_emails:
                    meeting_info = self._extract_meeting_info(event)
                    if meeting_info:
                        matching_meetings.append(meeting_info)
            
            # Return natural language response
            if len(matching_meetings) == 0:
                return f"You don't have any upcoming meetings with {email}."
            
            response = f"You have {len(matching_meetings)} upcoming meeting{'s' if len(matching_meetings) != 1 else ''} with {email}:\n\n"
            
            for i, meeting in enumerate(matching_meetings, 1):
                response += f"{i}. **{meeting['title']}**\n"
                response += f"   📅 {meeting['date']} at {meeting['time']}\n"
                if meeting['description']:
                    response += f"   📝 {meeting['description']}\n"
                response += "\n"
            
            return response.strip()
            
        except HttpError as error:
            return f"Sorry, I encountered an error accessing your Google Calendar: {error}"
        except Exception as e:
            return f"Sorry, I couldn't check meetings with that person: {str(e)}"
    
    def _calculate_available_slots(self, start_time, end_time, busy_times, duration_minutes):
        """Calculate available time slots given busy periods."""
        available_slots = []
        current_time = start_time
        
        # Convert busy times to datetime objects
        busy_periods = []
        for busy in busy_times:
            busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
            busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
            busy_periods.append((busy_start, busy_end))
        
        # Sort busy periods by start time
        busy_periods.sort(key=lambda x: x[0])
        
        while current_time + timedelta(minutes=duration_minutes) <= end_time:
            slot_end = current_time + timedelta(minutes=duration_minutes)
            
            # Check if this slot conflicts with any busy period
            is_available = True
            for busy_start, busy_end in busy_periods:
                if (current_time < busy_end and slot_end > busy_start):
                    is_available = False
                    current_time = busy_end
                    break
            
            if is_available:
                available_slots.append(current_time.strftime('%H:%M'))
                current_time += timedelta(minutes=30)  # 30-minute increments
        
        return available_slots
    
    def _extract_meeting_info(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract meeting information from calendar event."""
        start = event.get('start', {})
        end = event.get('end', {})
        
        start_datetime = start.get('dateTime', start.get('date'))
        end_datetime = end.get('dateTime', end.get('date'))
        
        if not start_datetime:
            return None
        
        try:
            if 'T' in start_datetime:
                start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
                
                date_str = start_dt.strftime('%Y-%m-%d')
                time_str = f"{start_dt.strftime('%H:%M')}-{end_dt.strftime('%H:%M')}"
            else:
                date_str = start_datetime
                time_str = "All day"
            
            attendees = event.get('attendees', [])
            attendee_emails = [a.get('email', '') for a in attendees]
            
            return {
                "id": event.get('id'),
                "date": date_str,
                "time": time_str,
                "title": event.get('summary', 'No title'),
                "location": event.get('location'),
                "attendees": attendee_emails,
                "description": event.get('description', '')
            }
            
        except Exception:
            return None