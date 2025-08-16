import os
import pickle
import json
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from fastapi import HTTPException

from google_calendar import CalendarService

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
TOKEN_FILE = 'token.pickle'

def get_credentials_config():
    """Get credentials either from file or environment variables"""
    credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE')
    
    if credentials_file and os.path.exists(credentials_file):
        return credentials_file
    
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    project_id = os.getenv('GOOGLE_PROJECT_ID')
    
    if client_id and client_secret:
        credentials_dict = {
            "installed": {
                "client_id": client_id,
                "project_id": project_id or "default-project",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": client_secret,
                "redirect_uris": ["http://localhost"]
            }
        }
        
        temp_file = 'temp_credentials.json'
        with open(temp_file, 'w') as f:
            json.dump(credentials_dict, f)
        return temp_file
    
    raise Exception(
        "Google credentials not found. Either:\n"
        "1. Set GOOGLE_CREDENTIALS_FILE pointing to credentials.json, OR\n"
        "2. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables"
    )

def get_credentials():
    creds = None
    
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials_source = get_credentials_config()
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_source, SCOPES
            )
            creds = flow.run_local_server(port=0)
            
            if credentials_source == 'temp_credentials.json':
                os.remove(credentials_source)
        
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def get_authenticated_service():
    """Return raw credentials for use by different services"""
    try:
        credentials = get_credentials()
        return credentials
    except Exception as e:
        raise HTTPException(
            status_code=401, 
            detail=f"Authentication failed: {str(e)}"
        )