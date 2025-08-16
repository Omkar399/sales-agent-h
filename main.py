from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv

from google_calendar import CalendarService
from daily_meetings import DailyMeetingsService
from availability import AvailabilityService
from auth import get_authenticated_service

load_dotenv()

app = FastAPI(
    title="Google Calendar API Suite",
    description="API for calendar meetings, availability, and person-specific meeting checks",
    version="2.0.0"
)

class MeetingInfo(BaseModel):
    date: str
    time: str
    title: str
    location: Optional[str] = None

class MeetingResponse(BaseModel):
    email: str
    has_meetings: bool
    meetings_found: int
    meetings: List[MeetingInfo]

def get_daily_meetings_service(credentials=Depends(get_authenticated_service)) -> DailyMeetingsService:
    return DailyMeetingsService(credentials)

def get_availability_service(credentials=Depends(get_authenticated_service)) -> AvailabilityService:
    return AvailabilityService(credentials)

def get_calendar_service(credentials=Depends(get_authenticated_service)) -> CalendarService:
    return CalendarService(credentials)

@app.get("/")
async def root():
    return {
        "message": "Google Calendar API Suite",
        "endpoints": {
            "daily_meetings": "/meetings/today or /meetings/{date}",
            "weekly_availability": "/availability/week", 
            "person_meetings": "/check-meetings/{email}"
        }
    }

@app.get("/meetings/today")
async def get_today_meetings(
    daily_service: DailyMeetingsService = Depends(get_daily_meetings_service)
):
    try:
        return daily_service.get_daily_meetings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching today's meetings: {str(e)}")

@app.get("/meetings/{date}")
async def get_meetings_by_date(
    date: str,
    daily_service: DailyMeetingsService = Depends(get_daily_meetings_service)
):
    try:
        return daily_service.get_daily_meetings(date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format. Use YYYY-MM-DD: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching meetings for {date}: {str(e)}")

@app.get("/availability/week")
async def get_weekly_availability(
    availability_service: AvailabilityService = Depends(get_availability_service)
):
    try:
        return availability_service.get_weekly_availability()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating availability: {str(e)}")

@app.get("/check-meetings/{email}", response_model=MeetingResponse)
async def check_meetings(
    email: EmailStr,
    calendar_service: CalendarService = Depends(get_calendar_service)
):
    try:
        meetings = calendar_service.get_meetings_with_person(email)
        
        return MeetingResponse(
            email=email,
            has_meetings=len(meetings) > 0,
            meetings_found=len(meetings),
            meetings=meetings
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid email format: {str(e)}")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=f"Calendar access denied: {str(e)}")
    except Exception as e:
        if "quota" in str(e).lower():
            raise HTTPException(status_code=429, detail="Google API quota exceeded. Please try again later.")
        elif "authentication" in str(e).lower() or "credentials" in str(e).lower():
            raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")
        else:
            raise HTTPException(status_code=500, detail=f"Error checking meetings: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)