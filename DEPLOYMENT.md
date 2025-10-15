# AWS Elastic Beanstalk Deployment Guide

## Prerequisites

1. AWS Account with appropriate permissions
2. AWS CLI installed and configured
3. EB CLI installed: `pip install awsebcli`
4. PostgreSQL RDS instance (recommended for production)

## Initial Setup

### 1. Install EB CLI (if not already installed)

```bash
pip install awsebcli --upgrade
```

### 2. Initialize Elastic Beanstalk

```bash
eb init
```

Follow the prompts:
- Select your AWS region
- Select "Create new Application"
- Application name: `happin-backend`
- Platform: Python
- Platform branch: Python 3.9
- Set up SSH: Yes (recommended)

### 3. Create an Environment

```bash
eb create happin-production
```

Or specify more options:

```bash
eb create happin-production \
  --instance-type t2.small \
  --database \
  --database.engine postgres \
  --database.version 14 \
  --database.username dbadmin \
  --database.password YourSecurePassword123
```

## Environment Variables

Set required environment variables in EB:

```bash
# Django Settings
eb setenv SECRET_KEY="your-super-secret-key-change-this"
eb setenv DEBUG=False
eb setenv ALLOWED_HOSTS=".elasticbeanstalk.com,.amazonaws.com"

# Database (if using external RDS)
eb setenv DB_ENGINE="django.db.backends.postgresql"
eb setenv DB_NAME="happin_db"
eb setenv DB_USER="your_db_user"
eb setenv DB_PASSWORD="your_db_password"
eb setenv DB_HOST="your-rds-endpoint.rds.amazonaws.com"
eb setenv DB_PORT="5432"

# Security Settings
eb setenv CSRF_COOKIE_SECURE=True
eb setenv SESSION_COOKIE_SECURE=True
eb setenv CSRF_TRUSTED_ORIGINS="https://your-domain.elasticbeanstalk.com"

# CORS Settings (adjust for your frontend)
eb setenv CORS_ALLOW_ALL_ORIGINS=False
eb setenv CORS_ALLOWED_ORIGINS="https://your-frontend-domain.com,https://your-app.com"

# Twilio Configuration
eb setenv TWILIO_ACCOUNT_SID="your_twilio_sid"
eb setenv TWILIO_AUTH_TOKEN="your_twilio_token"
eb setenv TWILIO_PHONE_NUMBER="+1234567890"
```

## Deployment

### Deploy your application

```bash
eb deploy
```

### Check application status

```bash
eb status
```

### View logs

```bash
eb logs
```

### Open application in browser

```bash
eb open
```

## Database Setup

### Option 1: Use EB-managed RDS (Recommended for testing)

When creating your environment with `--database` flag, EB will automatically:
- Create an RDS instance
- Set environment variables (RDS_HOSTNAME, RDS_PORT, RDS_DB_NAME, RDS_USERNAME, RDS_PASSWORD)
- You'll need to update settings.py to use these variables

### Option 2: Use standalone RDS (Recommended for production)

1. Create RDS instance manually in AWS Console
2. Configure security groups to allow EB instances to connect
3. Set DB_* environment variables as shown above

## Post-Deployment

### 1. Run migrations (automatically handled by container_commands)

Migrations run automatically via `.ebextensions/01_django.config`

### 2. Create superuser (optional, basic one created automatically)

```bash
eb ssh
source /var/app/venv/*/bin/activate
cd /var/app/current
python manage.py createsuperuser
exit
```

### 3. Access Django Admin

Navigate to: `https://your-app.elasticbeanstalk.com/admin/`

## Updating Your Application

1. Make changes to your code
2. Commit changes: `git commit -am "Your changes"`
3. Deploy: `eb deploy`

## Environment Management

### List environments
```bash
eb list
```

### Switch environments
```bash
eb use environment-name
```

### Scale your application
```bash
eb scale 3  # Scale to 3 instances
```

### Configure environment
```bash
eb config
```

## Monitoring

### Health dashboard
```bash
eb health
```

### CloudWatch logs
```bash
eb logs --cloudwatch-logs enable
```

## Troubleshooting

### View recent logs
```bash
eb logs --all
```

### SSH into instance
```bash
eb ssh
```

### Check environment variables
```bash
eb printenv
```

### Common Issues

1. **Static files not loading**
   - Ensure `collectstatic` ran successfully
   - Check `.ebextensions/02_python.config` static file configuration

2. **Database connection errors**
   - Verify environment variables: `eb printenv`
   - Check RDS security group allows connections from EB instances
   - Ensure `psycopg2-binary` is in requirements.txt

3. **502 Bad Gateway**
   - Check application logs: `eb logs`
   - Verify Procfile is correct
   - Check if migrations ran successfully

4. **Module import errors**
   - Ensure all dependencies are in requirements.txt
   - Check Python version matches runtime.txt

## Cost Optimization

- Use t2.micro or t2.small for development
- Enable auto-scaling for production
- Use RDS with appropriate instance size
- Consider reserved instances for long-term use

## Security Best Practices

1. Never commit secrets to Git
2. Use environment variables for all sensitive data
3. Enable HTTPS (SSL certificate via AWS Certificate Manager)
4. Set `DEBUG=False` in production
5. Regularly update dependencies
6. Use security groups to restrict access
7. Enable RDS encryption at rest

## Cleanup

To terminate your environment:

```bash
eb terminate happin-production
```

## Additional Resources

- [AWS Elastic Beanstalk Documentation](https://docs.aws.amazon.com/elasticbeanstalk/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [EB CLI Reference](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html)

