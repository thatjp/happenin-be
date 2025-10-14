"""
SMS Service using Twilio API
"""
import logging
from typing import Optional, Dict, Any
from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

logger = logging.getLogger(__name__)


class SMSService:
    """SMS service using Twilio API"""
    
    def __init__(self):
        self.account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        self.auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        self.phone_number = getattr(settings, 'TWILIO_PHONE_NUMBER', None)
        
        if not all([self.account_sid, self.auth_token, self.phone_number]):
            logger.warning("Twilio credentials not configured. SMS service will not work.")
            self.client = None
        else:
            try:
                self.client = Client(self.account_sid, self.auth_token)
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self.client = None
    
    def send_sms(self, to: str, message: str, from_number: Optional[str] = None) -> Dict[str, Any]:
        """
        Send SMS message
        
        Args:
            to: Recipient phone number (E.164 format)
            message: SMS message content
            from_number: Sender phone number (optional, uses default if not provided)
            
        Returns:
            Dict with success status and message details
        """
        if not self.client:
            return {
                'success': False,
                'error': 'SMS service not configured',
                'message_id': None
            }
        
        try:
            # Use provided from_number or default
            from_phone = from_number or self.phone_number
            
            # Send SMS
            message_obj = self.client.messages.create(
                body=message,
                from_=from_phone,
                to=to
            )
            
            logger.info(f"SMS sent successfully to {to}. Message SID: {message_obj.sid}")
            
            return {
                'success': True,
                'message_id': message_obj.sid,
                'status': message_obj.status,
                'to': to,
                'from': from_phone,
                'body': message
            }
            
        except TwilioException as e:
            logger.error(f"Twilio error sending SMS to {to}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message_id': None
            }
        except Exception as e:
            logger.error(f"Unexpected error sending SMS to {to}: {e}")
            return {
                'success': False,
                'error': 'Unexpected error occurred',
                'message_id': None
            }
    
    def is_configured(self) -> bool:
        """
        Check if SMS service is properly configured
        
        Returns:
            True if configured, False otherwise
        """
        return self.client is not None


# Global SMS service instance
sms_service = SMSService()
