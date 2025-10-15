import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'happenin.settings')

# Create the Celery app
app = Celery('happenin')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure Celery Beat schedule
app.conf.beat_schedule = {
    'scrape-scheduled-targets': {
        'task': 'apps.scraping.tasks.scrape_scheduled_targets',
        'schedule': 60.0,  # Run every minute
    },
    'cleanup-old-scraping-data': {
        'task': 'apps.scraping.tasks.cleanup_old_data',
        'schedule': 3600.0,  # Run every hour
    },
    'update-scraping-metrics': {
        'task': 'apps.scraping.tasks.update_daily_metrics',
        'schedule': 86400.0,  # Run daily
    },
}

# Celery configuration
app.conf.update(
    # Task serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Time settings
    timezone='UTC',
    enable_utc=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Result backend
    result_backend='redis://localhost:6379/1',
    
    # Task routing
    task_routes={
        'apps.scraping.tasks.*': {'queue': 'scraping'},
        'apps.notifications.tasks.*': {'queue': 'notifications'},
    },
    
    # Task execution
    task_always_eager=False,  # Set to True for testing
    task_eager_propagates=True,
    
    # Rate limiting
    task_annotations={
        'apps.scraping.tasks.scrape_website': {'rate_limit': '10/m'},
    },
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_acks_late=True,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

@app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery setup"""
    print(f'Request: {self.request!r}')
    return 'Celery is working!'
