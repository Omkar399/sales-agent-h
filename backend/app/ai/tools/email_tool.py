"""Email service integration tool for the AI agent using Gmail API v1."""

import json
import base64
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ...config import settings
from ...database import get_db
from ...models.cards import Card


class EmailTool:
    """Gmail API v1 integration tool for bulk and personalized emails."""
    
    # Gmail API scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    def __init__(self):
        self.client_id = settings.GMAIL_CLIENT_ID
        self.client_secret = settings.GMAIL_CLIENT_SECRET
        self.refresh_token = settings.GMAIL_REFRESH_TOKEN
        self.service = None
        self._initialize_gmail_service()
    
    def _initialize_gmail_service(self):
        """Initialize the Gmail API service with client credentials."""
        try:
            if not self.client_id or not self.client_secret or not self.refresh_token:
                print("Gmail credentials not configured. Please set GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, and GMAIL_REFRESH_TOKEN.")
                return
            
            # Create credentials from client ID, secret, and refresh token
            creds = Credentials(
                token=None,
                refresh_token=self.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=self.SCOPES
            )
            
            # Refresh the token if needed
            if not creds.valid:
                creds.refresh(Request())
            
            # Build the Gmail service
            self.service = build('gmail', 'v1', credentials=creds)
            print(f"Gmail API service initialized successfully!")
            
        except Exception as e:
            print(f"Failed to initialize Gmail service: {str(e)}")
            self.service = None
    
    def get_function_schemas(self) -> List[Dict[str, Any]]:
        """Get function schemas for Gemini function calling."""
        return [
            {
                "name": "send_personalized_email",
                "description": "Send a personalized email to a single recipient or specific customer",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to_email": {
                            "type": "string",
                            "description": "Recipient email address (optional if customer_name is provided)"
                        },
                        "to_name": {
                            "type": "string",
                            "description": "Recipient name (optional if customer_name is provided)"
                        },
                        "customer_name": {
                            "type": "string",
                            "description": "Name of customer from database to send email to"
                        },
                        "subject": {
                            "type": "string",
                            "description": "Email subject line"
                        },
                        "message": {
                            "type": "string",
                            "description": "Email message content"
                        },
                        "email_type": {
                            "type": "string",
                            "description": "Type of email (follow_up, introduction, meeting_request, etc.)",
                            "default": "follow_up"
                        }
                    },
                    "required": ["subject", "message"]
                }
            },
            {
                "name": "send_bulk_emails",
                "description": "Send personalized emails to all customers or multiple recipients",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "send_to_all_customers": {
                            "type": "boolean",
                            "description": "If true, send to all customers in database. If false, use recipients list.",
                            "default": False
                        },
                        "recipients": {
                            "type": "array",
                            "description": "List of specific recipients (ignored if send_to_all_customers is true)",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "email": {"type": "string"},
                                    "name": {"type": "string"},
                                    "company": {"type": "string"},
                                    "custom_data": {"type": "object"}
                                }
                            }
                        },
                        "subject_template": {
                            "type": "string",
                            "description": "Email subject template with placeholders like {{name}}, {{company}}"
                        },
                        "message_template": {
                            "type": "string",
                            "description": "Email message template with placeholders"
                        },
                        "campaign_name": {
                            "type": "string",
                            "description": "Name for this email campaign",
                            "default": "AI Generated Campaign"
                        }
                    },
                    "required": ["subject_template", "message_template"]
                }
            },
            {
                "name": "create_email_template",
                "description": "Create a reusable email template",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "template_name": {
                            "type": "string",
                            "description": "Name of the template"
                        },
                        "subject": {
                            "type": "string",
                            "description": "Subject line template"
                        },
                        "html_content": {
                            "type": "string",
                            "description": "HTML email content"
                        },
                        "text_content": {
                            "type": "string",
                            "description": "Plain text email content"
                        },
                        "template_type": {
                            "type": "string",
                            "description": "Type of template (follow_up, introduction, etc.)"
                        }
                    },
                    "required": ["template_name", "subject", "html_content"]
                }
            },
            {
                "name": "get_email_analytics",
                "description": "Get email campaign analytics and statistics",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "campaign_name": {
                            "type": "string",
                            "description": "Name of the campaign to analyze"
                        },
                        "days_back": {
                            "type": "integer",
                            "description": "Number of days back to analyze",
                            "default": 30
                        }
                    }
                }
            }
        ]
    
    async def send_personalized_email(
        self,
        subject: str,
        message: str,
        to_email: Optional[str] = None,
        to_name: Optional[str] = None,
        customer_name: Optional[str] = None,
        email_type: str = "follow_up",
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Send a personalized email to a single recipient or customer."""
        try:
            # Check if Gmail service is available
            if not self.service:
                return {
                    "status": "error",
                    "message": "Gmail API service not initialized. Please check credentials configuration."
                }
            
            # Get database session if not provided
            if db is None:
                db = next(get_db())
            
            # If customer_name is provided, look up customer in database
            if customer_name:
                customer = db.query(Card).filter(Card.customer_name.ilike(f"%{customer_name}%")).first()
                if customer:
                    to_email = customer.email
                    to_name = customer.customer_name
                    # Add company context to message if available
                    if customer.company:
                        message = message.replace("{{company}}", customer.company)
                        message = message.replace("{{name}}", customer.customer_name)
                else:
                    return {
                        "status": "error",
                        "message": f"Customer '{customer_name}' not found in database"
                    }
            
            if not to_email or not to_name:
                return {
                    "status": "error",
                    "message": "Recipient email and name are required"
                }
            
            # Send email via Gmail API
            result = self._send_gmail_api_email(to_email, to_name, subject, message)
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to send email: {str(e)}"
            }
    
    async def send_bulk_emails(
        self,
        subject_template: str,
        message_template: str,
        send_to_all_customers: bool = False,
        recipients: Optional[List[Dict[str, Any]]] = None,
        campaign_name: str = "AI Generated Campaign",
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Send personalized emails to all customers or multiple recipients."""
        try:
            # Get database session if not provided
            if db is None:
                db = next(get_db())
            
            # Check if Gmail service is available
            if not self.service:
                return {
                    "status": "error",
                    "message": "Gmail API service not initialized. Please check credentials configuration."
                }
            
            # Determine recipients
            if send_to_all_customers:
                # Get all customers from database
                customers = db.query(Card).filter(Card.email.isnot(None)).all()
                recipients = []
                for customer in customers:
                    recipients.append({
                        "email": customer.email,
                        "name": customer.customer_name,
                        "company": customer.company or "",
                        "custom_data": {
                            "status": customer.status.value if customer.status else "",
                            "priority": customer.priority.value if customer.priority else "",
                            "notes": customer.notes or ""
                        }
                    })
            
            if not recipients:
                return {
                    "status": "error",
                    "message": "No recipients found. Either provide recipients list or enable send_to_all_customers."
                }
            
            # Send emails to all recipients
            sent_count = 0
            failed_count = 0
            failed_emails = []
            
            for recipient in recipients:
                try:
                    # Personalize subject and message
                    personalized_subject = subject_template.replace("{{name}}", recipient["name"]).replace("{{company}}", recipient["company"])
                    personalized_message = message_template.replace("{{name}}", recipient["name"]).replace("{{company}}", recipient["company"])
                    
                    # Send individual email
                    result = self._send_gmail_api_email(
                        recipient["email"], 
                        recipient["name"], 
                        personalized_subject, 
                        personalized_message
                    )
                    
                    if result["status"] == "success":
                        sent_count += 1
                    else:
                        failed_count += 1
                        failed_emails.append(recipient["email"])
                        
                except Exception as e:
                    failed_count += 1
                    failed_emails.append(recipient["email"])
                    print(f"Failed to send email to {recipient['email']}: {str(e)}")
            
            return {
                "status": "success",
                "campaign_id": f"campaign_{datetime.now().timestamp()}",
                "campaign_name": campaign_name,
                "recipients_count": len(recipients),
                "emails_sent": sent_count,
                "emails_failed": failed_count,
                "failed_emails": failed_emails,
                "sent_at": datetime.now().isoformat(),
                "message": f"Bulk email campaign '{campaign_name}' completed. Sent: {sent_count}, Failed: {failed_count}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to send bulk emails: {str(e)}"
            }
    
    async def create_email_template(
        self,
        template_name: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        template_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a reusable email template."""
        try:
            if not self.api_key:
                return self._mock_template_creation_response(template_name, template_type)
            
            # Mock template creation
            return self._mock_template_creation_response(template_name, template_type)
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create template: {str(e)}"
            }
    
    async def get_email_analytics(self, campaign_name: Optional[str] = None, days_back: int = 30) -> Dict[str, Any]:
        """Get email campaign analytics and statistics."""
        try:
            if not self.api_key:
                return self._mock_analytics_response(campaign_name, days_back)
            
            # Mock analytics data
            return self._mock_analytics_response(campaign_name, days_back)
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get analytics: {str(e)}"
            }
    
    def _mock_email_response(self, to_email: str, subject: str, email_type: str) -> Dict[str, Any]:
        """Generate mock email response."""
        return {
            "status": "success",
            "message_id": f"mock_email_{datetime.now().timestamp()}",
            "to": to_email,
            "subject": subject,
            "type": email_type,
            "sent_at": datetime.now().isoformat(),
            "message": f"Email sent successfully to {to_email}"
        }
    
    def _mock_bulk_email_response(self, recipients: List[Dict[str, Any]], campaign_name: str) -> Dict[str, Any]:
        """Generate mock bulk email response."""
        return {
            "status": "success",
            "campaign_id": f"campaign_{datetime.now().timestamp()}",
            "campaign_name": campaign_name,
            "recipients_count": len(recipients),
            "emails_sent": len(recipients),
            "emails_failed": 0,
            "sent_at": datetime.now().isoformat(),
            "estimated_delivery": "Within 5-10 minutes",
            "message": f"Bulk email campaign '{campaign_name}' sent to {len(recipients)} recipients"
        }
    
    def _mock_template_creation_response(self, template_name: str, template_type: Optional[str]) -> Dict[str, Any]:
        """Generate mock template creation response."""
        return {
            "status": "success",
            "template_id": f"template_{datetime.now().timestamp()}",
            "template_name": template_name,
            "template_type": template_type,
            "created_at": datetime.now().isoformat(),
            "message": f"Email template '{template_name}' created successfully"
        }
    
    def _mock_analytics_response(self, campaign_name: Optional[str], days_back: int) -> Dict[str, Any]:
        """Generate mock analytics response."""
        return {
            "status": "success",
            "campaign_name": campaign_name or "All Campaigns",
            "period": f"Last {days_back} days",
            "analytics": {
                "emails_sent": 1250,
                "emails_delivered": 1198,
                "emails_opened": 487,
                "emails_clicked": 156,
                "emails_bounced": 52,
                "unsubscribes": 8,
                "delivery_rate": 95.8,
                "open_rate": 40.7,
                "click_rate": 32.0,
                "bounce_rate": 4.2,
                "unsubscribe_rate": 0.7
            },
            "top_performing_subjects": [
                {"subject": "Quick question about your marketing goals", "open_rate": 68.2},
                {"subject": "Following up on our conversation", "open_rate": 52.1},
                {"subject": "Exclusive offer for {{company}}", "open_rate": 45.8}
            ],
            "message": f"Analytics retrieved for {campaign_name or 'all campaigns'} over the last {days_back} days"
        }
    
    def _send_gmail_api_email(self, to_email: str, to_name: str, subject: str, message: str) -> Dict[str, Any]:
        """Send email via Gmail API v1."""
        try:
            if not self.service:
                return {
                    "status": "error",
                    "message": "Gmail API service not initialized. Please check credentials configuration."
                }
            
            # Create the email message
            msg = MIMEText(message)
            msg['to'] = to_email
            msg['subject'] = subject
            msg['from'] = 'me'  # 'me' represents the authenticated user
            
            # Encode the message
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
            
            # Send the email
            send_result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {
                "status": "success",
                "message_id": send_result.get('id'),
                "to": to_email,
                "to_name": to_name,
                "subject": subject,
                "sent_at": datetime.now().isoformat(),
                "message": f"✅ Email sent successfully to {to_name} ({to_email}) via Gmail API!",
                "gmail_message_id": send_result.get('id'),
                "thread_id": send_result.get('threadId')
            }
            
        except HttpError as error:
            return {
                "status": "error",
                "message": f"Gmail API error: {error}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to send email via Gmail API: {str(e)}"
            }
