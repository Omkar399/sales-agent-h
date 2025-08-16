from datetime import datetime, timedelta
from typing import List, Dict, Any
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz

class CalendarService:
    def __init__(self, credentials):
        self.service = build('calendar', 'v3', credentials=credentials)
    
    def get_meetings_with_person(self, email: str) -> List[Dict[str, Any]]:
        try:
            now = datetime.utcnow()
            end_date = now + timedelta(days=30)
            
            now_iso = now.isoformat() + 'Z'
            end_iso = end_date.isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now_iso,
                timeMax=end_iso,
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
            
            return matching_meetings
            
        except HttpError as error:
            raise Exception(f"Google Calendar API error: {error}")
        except Exception as error:
            raise Exception(f"Error fetching calendar events: {error}")
    
    def _extract_meeting_info(self, event: Dict[str, Any]) -> Dict[str, Any]:
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
            
            return {
                "date": date_str,
                "time": time_str,
                "title": event.get('summary', 'No title'),
                "location": event.get('location')
            }
            
        except Exception:
            return None