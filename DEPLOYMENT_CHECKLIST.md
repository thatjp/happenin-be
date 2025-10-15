# Elastic Beanstalk Deployment Checklist

## ✅ Pre-Deployment Checklist

### Configuration Files
- [x] `Procfile` created with Gunicorn configuration
- [x] `runtime.txt` specifies Python 3.9
- [x] `.ebextensions/` directory with Django configurations
- [x] `.ebignore` file to exclude unnecessary files
- [x] `.gitignore` updated with EB-specific entries
- [x] `requirements.txt` includes all production dependencies

### Settings & Security
- [ ] Generate new SECRET_KEY for production (never use default!)
- [ ] Set `DEBUG=False` in environment variables
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set up `CSRF_TRUSTED_ORIGINS`
- [ ] Configure CORS settings for your frontend
- [ ] Enable HTTPS/SSL certificate via AWS Certificate Manager

### Database
- [ ] Create PostgreSQL RDS instance (or use EB-managed DB)
- [ ] Configure database security groups
- [ ] Set all DB_* environment variables
- [ ] Test database connection

### Third-Party Services
- [ ] Configure Twilio credentials for SMS
- [ ] Set up any other API keys/secrets

### Testing
- [ ] Test application locally with production-like settings
- [ ] Run migrations locally: `python manage.py migrate`
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Run tests: `python manage.py test`

## 🚀 Deployment Steps

1. **Install EB CLI**
   ```bash
   pip install awsebcli --upgrade
   ```

2. **Initialize EB Application**
   ```bash
   eb init
   ```

3. **Create Environment**
   ```bash
   eb create happin-production
   ```

4. **Set Environment Variables**
   ```bash
   # Use the command from env_variables.txt
   eb setenv SECRET_KEY="..." DEBUG=False ...
   ```

5. **Deploy Application**
   ```bash
   eb deploy
   ```

6. **Verify Deployment**
   ```bash
   eb status
   eb health
   eb logs
   ```

7. **Test Application**
   ```bash
   eb open  # Opens in browser
   # Test API endpoints
   # Test admin panel: /admin/
   ```

## 📋 Post-Deployment

- [ ] Verify all API endpoints work
- [ ] Test authentication flow
- [ ] Check admin panel access
- [ ] Monitor application logs
- [ ] Set up CloudWatch alarms
- [ ] Configure auto-scaling (if needed)
- [ ] Set up domain name (Route 53)
- [ ] Enable HTTPS
- [ ] Configure backups for RDS
- [ ] Document production URLs and credentials (securely!)

## 🔍 Common Issues & Solutions

### Static Files Not Loading
```bash
# SSH into instance and check
eb ssh
source /var/app/venv/*/bin/activate
cd /var/app/current
python manage.py collectstatic --noinput
```

### Database Connection Failed
- Check RDS security group allows EB security group
- Verify DB_* environment variables: `eb printenv`
- Check RDS is in same VPC as EB environment

### Application Won't Start
- Check logs: `eb logs --all`
- Verify Procfile syntax
- Ensure all dependencies in requirements.txt
- Check Python version matches runtime.txt

### 502 Bad Gateway
- Application failed to start
- Check eb logs for Python errors
- Verify WSGI configuration in Procfile
- Check if migrations failed

## 📊 Monitoring

```bash
# View logs
eb logs

# Stream logs in real-time
eb logs --stream

# Check application health
eb health

# View environment info
eb status

# List all environments
eb list
```

## 🔐 Security Reminders

- ✅ Never commit secrets to Git
- ✅ Use environment variables for all sensitive data
- ✅ Enable HTTPS (free with AWS Certificate Manager)
- ✅ Set DEBUG=False in production
- ✅ Regularly update dependencies for security patches
- ✅ Use strong database passwords
- ✅ Restrict CORS to specific origins
- ✅ Enable RDS encryption
- ✅ Set up CloudWatch monitoring
- ✅ Configure automated backups

## 💰 Cost Considerations

**Estimated Monthly Costs:**
- t2.micro: ~$10-15/month (development)
- t2.small: ~$20-30/month (small production)
- RDS db.t3.micro: ~$15-20/month
- Load Balancer: ~$16-25/month (if using)
- Data transfer: Variable

**Cost Optimization:**
- Use t2.micro for dev/staging
- Enable auto-scaling (scale down during off-hours)
- Use reserved instances for predictable workloads
- Monitor with AWS Cost Explorer

## 📚 Additional Resources

- [DEPLOYMENT.md](./DEPLOYMENT.md) - Detailed deployment guide
- [env_variables.txt](./env_variables.txt) - Environment variables template
- [AWS EB Documentation](https://docs.aws.amazon.com/elasticbeanstalk/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)

