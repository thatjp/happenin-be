# Environment Setup Guide

This guide will help you set up environment variables for the happenin backend project.

## Quick Setup

1. **Run the setup script:**
   ```bash
   python setup_env.py
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Edit your .env file:**
   ```bash
   # Open .env file and update with your actual values
   nano .env  # or use your preferred editor
   ```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `TWILIO_ACCOUNT_SID` | Your Twilio Account SID | `your_twilio_account_sid_here` |
| `TWILIO_AUTH_TOKEN` | Your Twilio Auth Token | `your_auth_token_here` |
| `TWILIO_PHONE_NUMBER` | Your Twilio phone number | `+1234567890` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1,0.0.0.0,*` |
| `CORS_ALLOW_ALL_ORIGINS` | Allow all CORS origins | `True` |
| `CORS_ALLOW_CREDENTIALS` | Allow CORS credentials | `True` |

## Getting Twilio Credentials

1. **Sign up for Twilio:**
   - Go to [https://www.twilio.com](https://www.twilio.com)
   - Create a free account

2. **Get your credentials:**
   - Go to your Twilio Console Dashboard
   - Find your Account SID and Auth Token
   - Get a phone number from the Phone Numbers section

3. **Update .env file:**
   ```bash
   TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_PHONE_NUMBER=+1234567890
   ```

## Security Best Practices

1. **Never commit .env files:**
   - The .env file is already in .gitignore
   - Only commit .env.example or env_template.txt

2. **Use different values for different environments:**
   - Development: Use test credentials
   - Production: Use production credentials

3. **Rotate credentials regularly:**
   - Change your Twilio auth token periodically
   - Use strong, unique secret keys

## Testing Your Setup

1. **Test Django server:**
   ```bash
   python manage.py runserver
   ```

2. **Test API endpoints:**
   ```bash
   curl -X POST http://localhost:8000/api/accounts/sms/send-verification/ \
     -H "Content-Type: application/json" \
     -d '{"phone_number": "+1234567890"}'
   ```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'twilio'**
   ```bash
   pip install twilio
   ```

2. **ModuleNotFoundError: No module named 'decouple'**
   ```bash
   pip install python-decouple
   ```

3. **SMS service not configured**
   - Check your .env file has correct Twilio credentials
   - Verify your Twilio account is active

4. **Permission denied errors**
   - Check file permissions on .env file
   - Ensure .env file is readable by Django

### Getting Help

- Check the logs in your terminal
- Verify all environment variables are set correctly
- Test with a simple SMS first
- Check Twilio console for delivery status

## Production Deployment

For production deployment:

1. **Set environment variables on your server:**
   ```bash
   export SECRET_KEY="your_production_secret_key"
   export DEBUG=False
   export ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"
   export TWILIO_ACCOUNT_SID="your_production_sid"
   export TWILIO_AUTH_TOKEN="your_production_token"
   export TWILIO_PHONE_NUMBER="+1234567890"
   ```

2. **Use a proper database:**
   - PostgreSQL or MySQL instead of SQLite
   - Set DATABASE_URL environment variable

3. **Enable security settings:**
   - Set DEBUG=False
   - Use HTTPS
   - Set secure cookie settings