"""
Management command to test SMS service
"""
from django.core.management.base import BaseCommand
from apps.accounts.sms_service import sms_service


class Command(BaseCommand):
    help = 'Test SMS service functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--phone',
            type=str,
            help='Phone number to send test SMS to (E.164 format)',
            required=False
        )
        parser.add_argument(
            '--message',
            type=str,
            help='Test message to send',
            default='Hello from happenin! This is a test SMS message. 🎉'
        )
        parser.add_argument(
            '--config-only',
            action='store_true',
            help='Only test configuration, do not send SMS'
        )

    def handle(self, *args, **options):
        self.stdout.write("🧪 Twilio SMS Service Test")
        self.stdout.write("=" * 50)
        
        # Test configuration
        self.stdout.write("🔧 Testing Configuration...")
        self.stdout.write(f"Account SID: {sms_service.account_sid}")
        self.stdout.write(f"Auth Token: {'*' * 10 if sms_service.auth_token else 'Not set'}")
        self.stdout.write(f"Phone Number: {sms_service.phone_number}")
        self.stdout.write(f"Client initialized: {sms_service.client is not None}")
        self.stdout.write(f"Service configured: {sms_service.is_configured()}")
        
        if not sms_service.is_configured():
            self.stdout.write(
                self.style.ERROR('❌ SMS service is not configured!')
            )
            self.stdout.write("Please check your .env file and ensure you have:")
            self.stdout.write("- TWILIO_ACCOUNT_SID")
            self.stdout.write("- TWILIO_AUTH_TOKEN") 
            self.stdout.write("- TWILIO_PHONE_NUMBER")
            return
        
        self.stdout.write(
            self.style.SUCCESS('✅ SMS service is properly configured!')
        )
        
        # Test sending SMS if phone number provided
        if options['config_only']:
            self.stdout.write("\n📝 Next steps:")
            self.stdout.write("1. Get a real Twilio phone number from your Twilio console")
            self.stdout.write("2. Update TWILIO_PHONE_NUMBER in your .env file")
            self.stdout.write("3. Run: python manage.py test_sms --phone=+1234567890")
            return
        
        phone_number = options['phone']
        if not phone_number:
            self.stdout.write("\n📝 To test SMS sending, run:")
            self.stdout.write("python manage.py test_sms --phone=+1234567890")
            return
        
        message = options['message']
        
        self.stdout.write(f"\n📱 Testing SMS Sending...")
        self.stdout.write(f"Phone: {phone_number}")
        self.stdout.write(f"Message: {message}")
        
        # Send test SMS
        result = sms_service.send_sms(phone_number, message)

        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ SMS sent successfully!')
            )
            self.stdout.write(f"Message ID: {result['message_id']}")
            self.stdout.write(f"Status: {result['status']}")
            self.stdout.write(f"To: {result['to']}")
            self.stdout.write(f"From: {result['from']}")
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to send SMS: {result["error"]}')
            )
            if "not a Twilio phone number" in result['error']:
                self.stdout.write("\n💡 This error means you need to:")
                self.stdout.write("1. Get a real Twilio phone number from your Twilio console")
                self.stdout.write("2. Update TWILIO_PHONE_NUMBER in your .env file")
