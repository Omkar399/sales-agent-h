# Google Calendar Meeting Checker API

A FastAPI-based web service that checks for upcoming meetings with specific people in your Google Calendar.

## Features

- Check meetings with a specific person for the next 30 days
- RESTful API endpoint with JSON responses
- Secure Google OAuth2 authentication
- Comprehensive error handling

## Prerequisites

- Python 3.8+
- Google Cloud Console account
- Google Calendar access

## Setup Instructions

### 1. Google Cloud Console Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

4. Create OAuth2 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Desktop application"
   - Download the JSON file and save it as `credentials.json` in this project directory

### 2. Project Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure credentials (choose ONE method):

   **Method A: Using credentials.json file**
   ```bash
   cp .env.example .env
   # Set GOOGLE_CREDENTIALS_FILE=credentials.json in .env
   # Place your downloaded credentials.json in the project directory
   ```

   **Method B: Using environment variables (recommended for deployment)**
   ```bash
   cp .env.example .env
   # Set these values in .env from your Google Cloud Console:
   # GOOGLE_CLIENT_ID=your-client-id.googleusercontent.com
   # GOOGLE_CLIENT_SECRET=your-client-secret
   # GOOGLE_PROJECT_ID=your-project-id
   ```

4. Run the application:
   ```bash
   python main.py
   ```
   
   Or with uvicorn:
   ```bash
   uvicorn main:app --reload
   ```

### 3. First Time Authentication

When you first run the API and make a request, it will:
1. Open a browser window for Google OAuth2 authentication
2. Ask you to grant calendar read permissions
3. Save the authentication token locally for future use

## API Usage

### Check Meetings Endpoint

**GET** `/check-meetings/{email}`

**Parameters:**
- `email`: Email address of the person to check meetings with

**Example Request:**
```bash
curl http://localhost:8000/check-meetings/colleague@example.com
```

**Example Response:**
```json
{
  "email": "colleague@example.com",
  "has_meetings": true,
  "meetings_found": 2,
  "meetings": [
    {
      "date": "2025-08-20",
      "time": "14:00-15:00",
      "title": "Project Review",
      "location": "Conference Room A"
    },
    {
      "date": "2025-08-25",
      "time": "10:00-11:30",
      "title": "Weekly Sync",
      "location": null
    }
  ]
}
```

### API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## Error Handling

The API provides specific error responses:
- `400`: Invalid email format
- `401`: Authentication failed
- `403`: Calendar access denied
- `429`: Google API quota exceeded
- `500`: General server error

## Security Notes

- Keep your `credentials.json` file secure and never commit it to version control
- The `token.pickle` file contains your access tokens - keep it secure
- Only grant necessary calendar permissions

## Troubleshooting

### Common Issues

1. **Authentication Error**: Ensure either:
   - `credentials.json` is in the project directory with `GOOGLE_CREDENTIALS_FILE` set, OR
   - Environment variables `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set correctly

2. **Permission Denied**: Make sure you've granted calendar read permissions during the OAuth flow

3. **API Quota Exceeded**: Google Calendar API has usage limits. Wait and try again later.

## Files Structure

- `main.py` - FastAPI application and endpoints
- `google_calendar.py` - Google Calendar API service
- `auth.py` - OAuth2 authentication handling
- `requirements.txt` - Python dependencies
- `.env.example` - Environment configuration template