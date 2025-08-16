from datetime import datetime, timedelta, time
from typing import List, Dict, Any, Tuple, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class AvailabilityService:
    def __init__(self, credentials):
        self.service = build('calendar', 'v3', credentials=credentials)
        self.work_start = time(9, 0)  # 9 AM
        self.work_end = time(17, 0)   # 5 PM
    
    def get_weekly_availability(self) -> Dict[str, Any]:
        """
        Get availability for the current week (Monday to Friday, 9 AM to 5 PM)
        
        Returns:
            Dict containing availability slots for each weekday
        """
        try:
            # Get current Monday
            today = datetime.now().date()
            days_since_monday = today.weekday()
            monday = today - timedelta(days=days_since_monday)
            
            weekly_availability = {
                "week_start": monday.strftime('%Y-%m-%d'),
                "work_hours": "09:00-17:00",
                "timezone": "Local",
                "days": {}
            }
            
            # Process Monday to Friday
            for day_offset in range(5):  # 0=Monday, 4=Friday
                current_date = monday + timedelta(days=day_offset)
                day_name = current_date.strftime('%A')
                
                availability = self._get_day_availability(current_date)
                weekly_availability["days"][day_name.lower()] = {
                    "date": current_date.strftime('%Y-%m-%d'),
                    "day_name": day_name,
                    "available_slots": availability["available_slots"],
                    "busy_slots": availability["busy_slots"],
                    "total_available_hours": availability["total_available_hours"],
                    "total_busy_hours": availability["total_busy_hours"]
                }
            
            return weekly_availability
            
        except Exception as error:
            raise Exception(f"Error calculating weekly availability: {error}")
    
    def _get_day_availability(self, target_date: datetime.date) -> Dict[str, Any]:
        """Get availability for a specific day"""
        try:
            # Get all events for the day
            start_of_day = datetime.combine(target_date, time(0, 0))
            end_of_day = datetime.combine(target_date, time(23, 59, 59))
            
            start_iso = start_of_day.isoformat() + 'Z'
            end_iso = end_of_day.isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_iso,
                timeMax=end_iso,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Extract busy periods during work hours
            busy_periods = []
            for event in events:
                busy_period = self._extract_busy_period(event, target_date)
                if busy_period:
                    busy_periods.append(busy_period)
            
            # Sort busy periods by start time
            busy_periods.sort(key=lambda x: x['start_minutes'])
            
            # Calculate available slots
            available_slots = self._calculate_available_slots(busy_periods)
            
            # Calculate totals
            total_busy_minutes = sum(period['duration_minutes'] for period in busy_periods)
            total_work_minutes = 8 * 60  # 9 AM to 5 PM = 8 hours
            total_available_minutes = total_work_minutes - total_busy_minutes
            
            return {
                "available_slots": available_slots,
                "busy_slots": busy_periods,
                "total_available_hours": round(total_available_minutes / 60, 2),
                "total_busy_hours": round(total_busy_minutes / 60, 2)
            }
            
        except Exception as error:
            raise Exception(f"Error calculating day availability: {error}")
    
    def _extract_busy_period(self, event: Dict[str, Any], target_date: datetime.date) -> Optional[Dict[str, Any]]:
        """Extract busy period from calendar event if it's during work hours"""
        try:
            start = event.get('start', {})
            end = event.get('end', {})
            
            start_datetime = start.get('dateTime', start.get('date'))
            end_datetime = end.get('dateTime', end.get('date'))
            
            if not start_datetime:
                return None
            
            # Handle all-day events
            if 'T' not in start_datetime:
                return {
                    "title": event.get('summary', 'Busy'),
                    "start_time": "09:00",
                    "end_time": "17:00",
                    "start_minutes": 9 * 60,
                    "end_minutes": 17 * 60,
                    "duration_minutes": 8 * 60,
                    "is_all_day": True
                }
            
            # Parse datetime events
            start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
            
            # Convert to local timezone for date comparison
            start_local = start_dt.replace(tzinfo=None)
            end_local = end_dt.replace(tzinfo=None)
            
            # Check if event overlaps with target date
            if start_local.date() != target_date and end_local.date() != target_date:
                return None
            
            # Clip to work hours (9 AM to 5 PM)
            work_start_dt = datetime.combine(target_date, self.work_start)
            work_end_dt = datetime.combine(target_date, self.work_end)
            
            # If event is completely outside work hours, ignore it
            if end_local <= work_start_dt or start_local >= work_end_dt:
                return None
            
            # Clip event to work hours (use local times)
            clipped_start = max(start_local, work_start_dt)
            clipped_end = min(end_local, work_end_dt)
            
            start_minutes = clipped_start.hour * 60 + clipped_start.minute
            end_minutes = clipped_end.hour * 60 + clipped_end.minute
            duration_minutes = end_minutes - start_minutes
            
            if duration_minutes <= 0:
                return None
            
            return {
                "title": event.get('summary', 'Busy'),
                "start_time": clipped_start.strftime('%H:%M'),
                "end_time": clipped_end.strftime('%H:%M'),
                "start_minutes": start_minutes,
                "end_minutes": end_minutes,
                "duration_minutes": duration_minutes,
                "is_all_day": False,
                "location": event.get('location'),
                "attendees_count": len(event.get('attendees', []))
            }
            
        except Exception:
            return None
    
    def _calculate_available_slots(self, busy_periods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate available time slots between busy periods"""
        available_slots = []
        
        work_start_minutes = 9 * 60  # 9 AM
        work_end_minutes = 17 * 60   # 5 PM
        
        current_time = work_start_minutes
        
        for busy_period in busy_periods:
            # If there's a gap before this busy period
            if current_time < busy_period['start_minutes']:
                gap_start = self._minutes_to_time(current_time)
                gap_end = self._minutes_to_time(busy_period['start_minutes'])
                gap_duration = busy_period['start_minutes'] - current_time
                
                available_slots.append({
                    "start_time": gap_start,
                    "end_time": gap_end,
                    "duration_minutes": gap_duration,
                    "duration_hours": round(gap_duration / 60, 2)
                })
            
            # Move current time to end of busy period
            current_time = max(current_time, busy_period['end_minutes'])
        
        # Check if there's time available after the last meeting
        if current_time < work_end_minutes:
            gap_start = self._minutes_to_time(current_time)
            gap_end = self._minutes_to_time(work_end_minutes)
            gap_duration = work_end_minutes - current_time
            
            available_slots.append({
                "start_time": gap_start,
                "end_time": gap_end,
                "duration_minutes": gap_duration,
                "duration_hours": round(gap_duration / 60, 2)
            })
        
        return available_slots
    
    def _minutes_to_time(self, minutes: int) -> str:
        """Convert minutes since midnight to HH:MM format"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"