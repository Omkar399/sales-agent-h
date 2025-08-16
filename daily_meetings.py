from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz
import logging

logging.basicConfig(level=logging.DEBUG)

class DailyMeetingsService:
    def __init__(self, credentials):
        self.service = build('calendar', 'v3', credentials=credentials)
    
    def get_daily_meetings(self, target_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all meetings for a specific day with complete details
        
        Args:
            target_date: Date in YYYY-MM-DD format. If None, uses today.
        
        Returns:
            Dict containing meeting details for the day
        """
        try:
            # Get local timezone
            local_tz = pytz.timezone('America/Los_Angeles')  # You might want to make this configurable
            
            if target_date:
                date_obj = datetime.strptime(target_date, '%Y-%m-%d')
                date_obj = local_tz.localize(date_obj)
            else:
                date_obj = datetime.now(local_tz)
            
            start_of_day = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Convert to UTC for Google Calendar API
            start_utc = start_of_day.astimezone(pytz.UTC)
            end_utc = end_of_day.astimezone(pytz.UTC)
            
            start_iso = start_utc.isoformat().replace('+00:00', 'Z')
            end_iso = end_utc.isoformat().replace('+00:00', 'Z')
            
            logging.debug(f"Fetching meetings between {start_iso} and {end_iso}")
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_iso,
                timeMax=end_iso,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            logging.debug(f"Found {len(events)} events from Google Calendar API")
            
            meetings = []
            for event in events:
                logging.debug(f"Processing event: {event.get('summary', 'No title')} at {event.get('start', {})}")
                # Add requested date to event for timezone comparison
                event['requested_date'] = date_obj.strftime('%Y-%m-%d')
                meeting_details = self._extract_complete_meeting_details(event)
                if meeting_details:
                    meetings.append(meeting_details)
                else:
                    logging.debug(f"Skipped event {event.get('summary', 'No title')} - could not extract details")
            
            return {
                "date": date_obj.strftime('%Y-%m-%d'),
                "day_of_week": date_obj.strftime('%A'),
                "total_meetings": len(meetings),
                "meetings": meetings
            }
            
        except HttpError as error:
            raise Exception(f"Google Calendar API error: {error}")
        except Exception as error:
            raise Exception(f"Error fetching daily meetings: {error}")
    
    def _extract_complete_meeting_details(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract complete meeting details from calendar event"""
        try:
            start = event.get('start', {})
            end = event.get('end', {})
            
            start_datetime = start.get('dateTime', start.get('date'))
            end_datetime = end.get('dateTime', end.get('date'))
            
            if not start_datetime:
                return None
            
            # Parse datetime
            if 'T' in start_datetime:
                # Parse UTC times from Google Calendar
                start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
                
                # Convert to local timezone
                local_tz = pytz.timezone('America/Los_Angeles')  # You might want to make this configurable
                start_dt_local = start_dt.astimezone(local_tz)
                end_dt_local = end_dt.astimezone(local_tz)
                
                is_all_day = False
                start_time = start_dt_local.strftime('%H:%M')
                end_time = end_dt_local.strftime('%H:%M')
                duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
                
                # Check if the event date in local time matches the requested date
                event_date = start_dt_local.date()
                requested_date = datetime.strptime(event.get('requested_date'), '%Y-%m-%d').date()
                
                if event_date != requested_date:
                    logging.debug(f"Skipping event {event.get('summary')} - date mismatch: {event_date} != {requested_date}")
                    return None
            else:
                is_all_day = True
                start_time = "All day"
                end_time = "All day"
                duration_minutes = 1440  # 24 hours
            
            # Extract attendees
            attendees = []
            for attendee in event.get('attendees', []):
                attendee_info = {
                    "email": attendee.get('email'),
                    "display_name": attendee.get('displayName'),
                    "response_status": attendee.get('responseStatus', 'needsAction'),
                    "is_organizer": attendee.get('organizer', False),
                    "is_self": attendee.get('self', False)
                }
                attendees.append(attendee_info)
            
            # Extract recurrence info
            recurrence_info = None
            if event.get('recurrence'):
                recurrence_info = {
                    "rules": event.get('recurrence'),
                    "is_recurring": True
                }
            
            return {
                "id": event.get('id'),
                "title": event.get('summary', 'No title'),
                "description": event.get('description', ''),
                "start_time": start_time,
                "end_time": end_time,
                "duration_minutes": duration_minutes,
                "is_all_day": is_all_day,
                "location": event.get('location'),
                "meeting_link": self._extract_meeting_link(event),
                "status": event.get('status', 'confirmed'),
                "attendees": attendees,
                "attendees_count": len(attendees),
                "organizer": {
                    "email": event.get('organizer', {}).get('email'),
                    "display_name": event.get('organizer', {}).get('displayName')
                },
                "created": event.get('created'),
                "updated": event.get('updated'),
                "recurrence": recurrence_info,
                "calendar_id": event.get('organizer', {}).get('email', 'primary'),
                "html_link": event.get('htmlLink'),
                "visibility": event.get('visibility', 'default'),
                "transparency": event.get('transparency', 'opaque')
            }
            
        except Exception as e:
            print(f"Error extracting meeting details: {e}")
            return None
    
    def _extract_meeting_link(self, event: Dict[str, Any]) -> Optional[str]:
        """Extract meeting link from various possible locations"""
        # Check hangout link
        if event.get('hangoutLink'):
            return event.get('hangoutLink')
        
        # Check conference data
        conference_data = event.get('conferenceData', {})
        entry_points = conference_data.get('entryPoints', [])
        for entry_point in entry_points:
            if entry_point.get('entryPointType') == 'video':
                return entry_point.get('uri')
        
        # Check description for common meeting links
        description = event.get('description', '')
        if description:
            # Look for common video meeting patterns
            import re
            patterns = [
                r'https://[a-zA-Z0-9.-]+\.zoom\.us/[a-zA-Z0-9/?=&-]+',
                r'https://meet\.google\.com/[a-zA-Z0-9-]+',
                r'https://teams\.microsoft\.com/[a-zA-Z0-9/?=&-]+',
                r'https://[a-zA-Z0-9.-]+\.webex\.com/[a-zA-Z0-9/?=&-]+'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, description)
                if match:
                    return match.group(0)
        
        return None