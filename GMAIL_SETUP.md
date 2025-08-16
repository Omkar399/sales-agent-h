# Gmail API v1 Setup Guide (2025)

This guide follows the official Google documentation for [Gmail API server-side authorization](https://developers.google.com/workspace/gmail/api/auth/web-server).

## Prerequisites

1. A Gmail account
2. Access to Google Cloud Console

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: "Sales Agent Gmail"
4. Click "Create"

## Step 2: Enable Gmail API

1. In the Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click on "Gmail API" and click "Enable"

## Step 3: Create OAuth 2.0 Client ID

Following the [official setup tool](https://developers.google.com/workspace/gmail/api/auth/web-server#create_a_client_id_and_client_secret):

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: External (for personal Gmail) or Internal (for G Suite)
   - App name: "Sales Agent"
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: Add `https://www.googleapis.com/auth/gmail.send`
4. For Application type, select "Web application"
5. Name: "Sales Agent Web Client"
6. Add authorized redirect URIs: `http://localhost:8080` (for testing)
7. Click "Create"
8. **Copy the Client ID and Client Secret** - you'll need these

## Step 4: Get Refresh Token

To get a refresh token for server-side access, you need to complete the OAuth flow once:

1. Create an authorization URL with these parameters:
   ```
   https://accounts.google.com/o/oauth2/auth?
   client_id=YOUR_CLIENT_ID&
   redirect_uri=http://localhost:8080&
   scope=https://www.googleapis.com/auth/gmail.send&
   response_type=code&
   access_type=offline&
   approval_prompt=force
   ```

2. Visit this URL in your browser and authorize the application
3. You'll be redirected to `http://localhost:8080/?code=AUTHORIZATION_CODE`
4. Use this authorization code to get a refresh token:

```bash
curl -X POST https://oauth2.googleapis.com/token \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "code=AUTHORIZATION_CODE" \
  -d "grant_type=authorization_code" \
  -d "redirect_uri=http://localhost:8080"
```

5. The response will include a `refresh_token` - save this!

## Step 5: Configure Environment Variables

1. Copy the `backend/env.example` file to `backend/.env`
2. Update the Gmail configuration:

```bash
# Gmail API Configuration (for sending emails)
GMAIL_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your_client_secret_here
GMAIL_REFRESH_TOKEN=your_refresh_token_here
```

## Step 6: Test Email Functionality

Once configured, you can test the email functionality in the chat:

```
"Send an email to omkarpodey@gmail.com with name Omkar, subject 'Hello' and message 'Hey this is your friend'"
```

## Security Best Practices

1. **Never commit credentials to version control**
2. **Store refresh tokens securely** - they provide long-term access
3. **Use HTTPS in production** for redirect URIs
4. **Regularly rotate client secrets** for enhanced security

## Troubleshooting

### "Invalid client" error
- Verify your client ID and client secret are correct
- Ensure the Gmail API is enabled in your Google Cloud project

### "Invalid grant" error  
- Your refresh token may have expired or been revoked
- Re-run the OAuth flow to get a new refresh token

### "Insufficient permissions" error
- Ensure you have the `https://www.googleapis.com/auth/gmail.send` scope
- Check that the user granted permission during OAuth flow

## Features

The Gmail API integration supports:

- **Single Email**: Send personalized emails to specific customers
- **Bulk Emails**: Send personalized emails to all customers or a list of recipients  
- **Template Variables**: Use `{{name}}` and `{{company}}` placeholders
- **Customer Lookup**: Send emails by customer name without specifying email address
- **OAuth 2.0 Security**: Modern authentication following Google's best practices

## Chat Commands Examples

```
# Send to specific customer by name
"Send an email to John Smith with subject 'Follow up' and message 'Hi John, just following up on our conversation.'"

# Send to all customers  
"Send a bulk email to all customers with subject 'Monthly Update' and message 'Hello {{name}}, here's our monthly update for {{company}}.'"

# Send to specific email address
"Send an email to john@example.com with name John Doe, subject 'Welcome' and message 'Welcome to our service!'"
```

The AI will automatically:
- Look up customer information from the database
- Personalize messages with customer names and company information
- Handle errors gracefully
- Provide detailed feedback on email delivery status