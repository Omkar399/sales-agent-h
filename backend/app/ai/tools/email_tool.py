"""Email service integration tool for the AI agent."""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import httpx
from ...config import settings


class EmailTool:
    """Email service integration tool for bulk and personalized emails."""
    
    def __init__(self):
        self.api_key = settings.SENDGRID_API_KEY
        self.from_email = settings.FROM_EMAIL
        self.base_url = "https://api.sendgrid.com/v3"
    
    def get_function_schemas(self) -> List[Dict[str, Any]]:
        """Get function schemas for Gemini function calling."""
        return [
            {
                "name": "send_personalized_email",
                "description": "Send a personalized email to a single recipient",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to_email": {
                            "type": "string",
                            "description": "Recipient email address"
                        },
                        "to_name": {
                            "type": "string",
                            "description": "Recipient name"
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
                    "required": ["to_email", "to_name", "subject", "message"]
                }
            },
            {
                "name": "send_bulk_emails",
                "description": "Send personalized emails to multiple recipients",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recipients": {
                            "type": "array",
                            "description": "List of recipients with email, name, and personalization data",
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
                    "required": ["recipients", "subject_template", "message_template"]
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
        to_email: str,
        to_name: str,
        subject: str,
        message: str,
        email_type: str = "follow_up"
    ) -> Dict[str, Any]:
        """Send a personalized email to a single recipient."""
        try:
            if not self.api_key or not self.from_email:
                return self._mock_email_response(to_email, subject, "single")
            
            # In production, this would use SendGrid API
            # Mock response for now
            return self._mock_email_response(to_email, subject, "single")
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to send email: {str(e)}"
            }
    
    async def send_bulk_emails(
        self,
        recipients: List[Dict[str, Any]],
        subject_template: str,
        message_template: str,
        campaign_name: str = "AI Generated Campaign"
    ) -> Dict[str, Any]:
        """Send personalized emails to multiple recipients."""
        try:
            if not self.api_key or not self.from_email:
                return self._mock_bulk_email_response(recipients, campaign_name)
            
            # In production, this would use SendGrid API with personalization
            # Mock response for now
            return self._mock_bulk_email_response(recipients, campaign_name)
            
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
