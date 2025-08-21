# Web Scraping App

A comprehensive web scraping application built with Django, Celery, and Celery Beat for periodic, legal web scraping operations.

## Features

### 🎯 **Core Functionality**
- **Scheduled Scraping**: Automatically scrape websites based on configurable frequencies
- **Legal Compliance**: Respects robots.txt and implements rate limiting
- **Multiple Scraping Methods**: CSS selectors, XPath, regex, and JSON path extraction
- **Data Storage**: Comprehensive storage of scraped data, jobs, and logs
- **Performance Monitoring**: Track response times, success rates, and data volumes

### 🔧 **Technical Features**
- **Celery Integration**: Asynchronous task processing with Celery workers
- **Celery Beat**: Scheduled task execution for periodic scraping
- **Rate Limiting**: Configurable delays and request limits per hour
- **Error Handling**: Comprehensive error logging and retry mechanisms
- **Data Deduplication**: Prevent duplicate content storage
- **Admin Interface**: Full Django admin integration with custom views

### 📊 **Monitoring & Analytics**
- **Real-time Logging**: Detailed logging of all scraping activities
- **Performance Metrics**: Track response times, success rates, and data volumes
- **Dashboard Views**: Admin interface with statistics and monitoring
- **Alert System**: Log-based alerting for failures and issues

## Architecture

### Models

#### ScrapingTarget
- Defines websites to scrape with configuration options
- Supports multiple frequencies (hourly, daily, weekly, monthly, custom)
- Configurable rate limiting and politeness settings
- Robots.txt compliance options

#### ScrapingJob
- Tracks individual scraping operations
- Supports different job types (scheduled, manual, retry)
- Performance metrics and error tracking
- Celery task integration

#### ScrapedData
- Stores extracted data from websites
- Supports multiple content types (HTML, JSON, text)
- Metadata extraction and storage
- Content deduplication

#### ScrapingRule
- Defines data extraction rules
- Multiple rule types (CSS, XPath, regex, JSON path)
- Priority-based processing
- Post-processing configuration

#### ScrapingLog
- Comprehensive logging of all activities
- Multiple log levels (debug, info, warning, error, critical)
- Context data storage
- Performance tracking

#### ScrapingMetrics
- Daily aggregated metrics
- Performance analytics
- Error rate monitoring
- Data volume tracking

### Celery Tasks

#### Scheduled Tasks
- `scrape_scheduled_targets`: Runs every minute to check for targets due for scraping
- `cleanup_old_data`: Runs hourly to clean up old data and logs
- `update_daily_metrics`: Runs daily to update aggregated metrics

#### Scraping Tasks
- `scrape_website`: Main scraping task for individual jobs
- `scrape_target_manual`: Manual scraping for immediate execution
- `extract_data_from_page`: Data extraction using defined rules
- `retry_failed_jobs`: Retry mechanism for failed scraping jobs

### Scraping Engine

#### WebScraper
- Main scraping class with BeautifulSoup integration
- Configurable user agents and headers
- Retry logic with exponential backoff
- Response parsing for multiple content types

#### Advanced Features
- Proxy support
- Cookie management
- Custom header configuration
- JavaScript rendering support (placeholder for Selenium)

## Installation & Setup

### 1. Install Dependencies
```bash
pip install celery redis beautifulsoup4 requests lxml
```

### 2. Add to Django Settings
```python
INSTALLED_APPS = [
    # ... other apps
    'apps.scraping',
]

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
```

### 3. Run Migrations
```bash
python manage.py makemigrations scraping
python manage.py migrate scraping
```

### 4. Set Up Example Data
```bash
python manage.py setup_scraping --all
```

## Usage

### Creating Scraping Targets

#### Basic Target
```python
from apps.scraping.models import ScrapingTarget

target = ScrapingTarget.objects.create(
    name='Domino Park Events',
    url='https://www.dominopark.com/events',
    frequency=ScrapingTarget.ScrapingFrequency.DAILY,
    delay_between_requests=5,
    max_requests_per_hour=100,
    created_by=user
)
```

#### Advanced Target with Rules
```python
from apps.scraping.models import ScrapingTarget, ScrapingRule

# Create target
target = ScrapingTarget.objects.create(
    name='News Site',
    url='https://news.example.com',
    frequency=ScrapingTarget.ScrapingFrequency.HOURLY,
    created_by=user
)

# Create extraction rules
ScrapingRule.objects.create(
    target=target,
    name='headline',
    rule_type=ScrapingRule.RuleType.CSS_SELECTOR,
    selector='h1.headline',
    data_type='text',
    priority=1
)

ScrapingRule.objects.create(
    target=target,
    name='article_content',
    rule_type=ScrapingRule.RuleType.CSS_SELECTOR,
    selector='.article-body',
    data_type='text',
    priority=2
)
```

### Manual Scraping

#### Immediate Execution
```python
from apps.scraping.tasks import scrape_target_manual

# Start manual scraping
result = scrape_target_manual.delay(target_id=1, user_id=1)
print(f"Job started: {result.id}")
```

#### Using the Scraper Directly
```python
from apps.scraping.scrapers import WebScraper

scraper = WebScraper(
    user_agent='My Bot (+https://www.dominopark.com/events)',
    delay=2,
    timeout=30
)

result = scraper.scrape('https://example.com')
print(f"Title: {result.title}")
print(f"Content: {result.content[:200]}...")
```

### Monitoring & Analytics

#### View Recent Jobs
```python
from apps.scraping.models import ScrapingJob

# Get recent jobs
recent_jobs = ScrapingJob.objects.filter(
    target__name='My Website'
).order_by('-created_at')[:10]

for job in recent_jobs:
    print(f"Job {job.id}: {job.status} - {job.items_scraped} items")
```

#### Check Performance Metrics
```python
from apps.scraping.models import ScrapingMetrics

# Get today's metrics
today = timezone.now().date()
metrics = ScrapingMetrics.objects.filter(
    target__name='My Website',
    date=today
).first()

if metrics:
    print(f"Success rate: {metrics.jobs_completed}/{metrics.jobs_scheduled}")
    print(f"Average response time: {metrics.avg_response_time_ms}ms")
```

## Configuration

### Celery Beat Schedule
```python
# happin/celery.py
app.conf.beat_schedule = {
    'scrape-scheduled-targets': {
        'task': 'apps.scraping.tasks.scrape_scheduled_targets',
        'schedule': 60.0,  # Every minute
    },
    'cleanup-old-scraping-data': {
        'task': 'apps.scraping.tasks.cleanup_old_data',
        'schedule': 3600.0,  # Every hour
    },
    'update-scraping-metrics': {
        'task': 'apps.scraping.tasks.update_daily_metrics',
        'schedule': 86400.0,  # Daily
    },
}
```

### Rate Limiting
```python
# Per-target configuration
target.delay_between_requests = 5  # 5 seconds between requests
target.max_requests_per_hour = 100  # Max 100 requests per hour
```

### User Agents
```python
# Custom user agent
target.user_agent = 'My Company Bot (+https://mycompany.com/bot)'

# Default user agent
target.user_agent = 'Happin Scraper Bot (+https://happin.com/bot)'
```

## Legal & Ethical Considerations

### Robots.txt Compliance
- Automatically checks robots.txt before scraping
- Respects disallow directives
- Configurable per target

### Rate Limiting
- Configurable delays between requests
- Per-hour request limits
- Polite scraping practices

### User Agent Identification
- Clear identification of scraping bot
- Contact information in user agent
- Transparent about scraping activities

### Data Usage
- Store only necessary data
- Respect website terms of service
- Implement data retention policies

## Monitoring & Maintenance

### Health Checks
```bash
# Check Celery worker status
celery -A happin status

# Check scheduled tasks
celery -A happin inspect scheduled

# Monitor task execution
celery -A happin events
```

### Log Analysis
```python
from apps.scraping.models import ScrapingLog

# Check for errors
errors = ScrapingLog.objects.filter(
    level=ScrapingLog.LogLevel.ERROR
).order_by('-created_at')[:10]

# Monitor performance
slow_jobs = ScrapingJob.objects.filter(
    response_time_ms__gt=5000  # > 5 seconds
).order_by('-response_time_ms')[:10]
```

### Data Cleanup
```python
from apps.scraping.tasks import cleanup_old_data

# Clean up data older than 30 days
cleanup_old_data.delay(days_to_keep=30)
```

## Troubleshooting

### Common Issues

#### Celery Worker Not Running
```bash
# Start Celery worker
celery -A happin worker -l info -Q scraping

# Start Celery Beat
celery -A happin beat -l info
```

#### Redis Connection Issues
```bash
# Check Redis status
redis-cli ping

# Start Redis if needed
redis-server
```

#### Scraping Failures
- Check target status (active/paused/disabled)
- Verify URL accessibility
- Check rate limiting settings
- Review error logs for specific issues

### Debug Mode
```python
# Enable debug logging
import logging
logging.getLogger('apps.scraping').setLevel(logging.DEBUG)

# Test scraping manually
from apps.scraping.tasks import scrape_website
result = scrape_website.delay(job_id=1)
```

## API Integration

### REST API Endpoints
The scraping app can be extended with REST API endpoints for:
- Managing scraping targets
- Monitoring job status
- Retrieving scraped data
- Configuring extraction rules

### Webhook Support
- Job completion notifications
- Error alerts
- Performance metrics
- Data processing events

## Extensions & Customization

### Custom Scrapers
```python
from apps.scraping.scrapers import WebScraper

class CustomScraper(WebScraper):
    def custom_extraction(self, html):
        # Custom extraction logic
        pass
    
    def preprocess_content(self, content):
        # Custom preprocessing
        pass
```

### Custom Rules
```python
from apps.scraping.models import ScrapingRule

# Custom rule types
class CustomRule(ScrapingRule):
    def apply_rule(self, content):
        # Custom rule application
        pass
```

### Integration with Other Apps
- **Notifications**: Send alerts for job completion/failure
- **Analytics**: Process scraped data for insights
- **Data Processing**: Pipeline scraped data to other systems
- **Monitoring**: Integrate with external monitoring tools

## Performance Optimization

### Database Optimization
- Use database indexes for frequently queried fields
- Implement data archiving for old records
- Use select_related for related model queries

### Caching Strategy
- Cache frequently accessed data
- Implement Redis for session storage
- Use Django's cache framework for query results

### Task Optimization
- Configure worker concurrency based on system resources
- Use task routing for different types of scraping
- Implement task result expiration

## Security Considerations

### Access Control
- User-based target ownership
- Admin-only configuration access
- Audit logging for all operations

### Data Protection
- Encrypt sensitive configuration data
- Implement data retention policies
- Secure API endpoints with authentication

### Network Security
- Use HTTPS for all external requests
- Implement request signing for API calls
- Monitor for suspicious activity patterns

## Contributing

### Development Setup
1. Clone the repository
2. Install development dependencies
3. Set up local development environment
4. Run tests and linting

### Testing
```bash
# Run scraping app tests
python manage.py test apps.scraping

# Run with coverage
coverage run --source='apps.scraping' manage.py test apps.scraping
coverage report
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints for function parameters
- Document all public methods and classes
- Write comprehensive tests for new features

## License

This app is part of the Happin backend system and follows the same licensing terms.

## Support

For questions, issues, or contributions:
- Check the documentation
- Review existing issues
- Create new issues with detailed information
- Contact the development team

---

**Note**: This scraping app is designed for legal and ethical web scraping. Always respect website terms of service, robots.txt files, and implement appropriate rate limiting to avoid overwhelming target servers.
