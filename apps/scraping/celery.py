from celery import Celery
from django.conf import settings
import os

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'happin.settings')

# Create celery app
app = Celery('happin_scraping')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule Configuration
app.conf.beat_schedule = {
    # Scrape all active targets every hour
    'scrape-active-targets-hourly': {
        'task': 'apps.scraping.tasks.scrape_all_active_targets',
        'schedule': 3600.0,  # Every hour
        'options': {'queue': 'scraping'}
    },
    
    # Retry failed jobs every 30 minutes
    'retry-failed-jobs': {
        'task': 'apps.scraping.tasks.retry_failed_jobs',
        'schedule': 1800.0,  # Every 30 minutes
        'options': {'queue': 'scraping'}
    },
    
    # Cleanup old data daily at 2 AM
    'cleanup-old-data': {
        'task': 'apps.scraping.tasks.cleanup_old_data',
        'schedule': 86400.0,  # Daily
        'options': {'queue': 'maintenance'}
    },
    
    # Health check every 5 minutes
    'scraping-health-check': {
        'task': 'apps.scraping.tasks.health_check',
        'schedule': 300.0,  # Every 5 minutes
        'options': {'queue': 'monitoring'}
    },
}

# Task routing
app.conf.task_routes = {
    'apps.scraping.tasks.scrape_target': {'queue': 'scraping'},
    'apps.scraping.tasks.scrape_all_active_targets': {'queue': 'scraping'},
    'apps.scraping.tasks.retry_failed_jobs': {'queue': 'scraping'},
    'apps.scraping.tasks.test_scraping_target': {'queue': 'scraping'},
    'apps.scraping.tasks.cleanup_old_data': {'queue': 'maintenance'},
    'apps.scraping.tasks.health_check': {'queue': 'monitoring'},
}

# Task serialization
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']

# Task execution settings
app.conf.task_always_eager = False
app.conf.task_eager_propagates = True

# Result backend settings
app.conf.result_backend = 'django-db'
app.conf.result_expires = 3600  # 1 hour

# Worker settings
app.conf.worker_prefetch_multiplier = 1
app.conf.worker_max_tasks_per_child = 1000
app.conf.worker_disable_rate_limits = False

# Task time limits
app.conf.task_soft_time_limit = 300  # 5 minutes
app.conf.task_time_limit = 600  # 10 minutes

# Rate limiting
app.conf.task_annotations = {
    'apps.scraping.tasks.scrape_target': {
        'rate_limit': '10/m',  # 10 tasks per minute
        'time_limit': 300,     # 5 minutes
        'soft_time_limit': 240, # 4 minutes
    },
    'apps.scraping.tasks.scrape_all_active_targets': {
        'rate_limit': '1/m',   # 1 task per minute
        'time_limit': 60,      # 1 minute
    },
}

# Error handling
app.conf.task_reject_on_worker_lost = True
app.conf.task_acks_late = True

# Monitoring
app.conf.worker_send_task_events = True
app.conf.task_send_sent_event = True

# Logging
app.conf.worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
app.conf.worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'

# Security
app.conf.worker_hijack_root_logger = False
app.conf.worker_redirect_stdouts = False

# Task result settings
app.conf.task_ignore_result = False
app.conf.task_store_errors_even_if_ignored = True

# Queue settings
app.conf.task_default_queue = 'default'
app.conf.task_default_exchange = 'default'
app.conf.task_default_routing_key = 'default'

# Broker settings (these should be configured in Django settings)
# app.conf.broker_url = 'redis://localhost:6379/0'
# app.conf.broker_connection_retry_on_startup = True

# Result backend settings
# app.conf.result_backend = 'redis://localhost:6379/0'

# Task routing for different types of scraping
app.conf.task_routes.update({
    'apps.scraping.tasks.scrape_target': {
        'queue': 'scraping',
        'routing_key': 'scraping.target'
    },
    'apps.scraping.tasks.scrape_all_active_targets': {
        'queue': 'scraping',
        'routing_key': 'scraping.scheduler'
    },
    'apps.scraping.tasks.retry_failed_jobs': {
        'queue': 'scraping',
        'routing_key': 'scraping.retry'
    },
    'apps.scraping.tasks.test_scraping_target': {
        'queue': 'scraping',
        'routing_key': 'scraping.test'
    },
    'apps.scraping.tasks.cleanup_old_data': {
        'queue': 'maintenance',
        'routing_key': 'maintenance.cleanup'
    },
    'apps.scraping.tasks.health_check': {
        'queue': 'monitoring',
        'routing_key': 'monitoring.health'
    },
})

# Custom task routing based on target properties
def route_task(name, args, kwargs, options, task=None, **kw):
    """Custom task routing based on target properties"""
    if name == 'apps.scraping.tasks.scrape_target' and args:
        target_id = args[0]
        try:
            from apps.scraping.models import ScrapingTarget
            target = ScrapingTarget.objects.get(id=target_id)
            
            # Route based on scraping method
            if target.scraping_method == 'selenium':
                return {'queue': 'scraping_selenium', 'routing_key': 'scraping.selenium'}
            elif target.scraping_method == 'api':
                return {'queue': 'scraping_api', 'routing_key': 'scraping.api'}
            else:
                return {'queue': 'scraping', 'routing_key': 'scraping.requests'}
                
        except Exception:
            # Fallback to default routing
            pass
    
    # Default routing
    return {'queue': 'default', 'routing_key': 'default'}

app.conf.task_routes = (route_task,)

# Task execution hooks
@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    print(f'Request: {self.request!r}')

# Health check task
@app.task(bind=True)
def health_check(self):
    """Health check task for monitoring scraping system"""
    try:
        from apps.scraping.models import ScrapingTarget, ScrapingJob
        from django.utils import timezone
        from datetime import timedelta
        
        # Check active targets
        active_targets = ScrapingTarget.objects.filter(
            is_active=True,
            status='active'
        ).count()
        
        # Check recent jobs
        recent_jobs = ScrapingJob.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=1)
        ).count()
        
        # Check failed jobs in last hour
        failed_jobs = ScrapingJob.objects.filter(
            status='failed',
            created_at__gte=timezone.now() - timedelta(hours=1)
        ).count()
        
        health_status = {
            'status': 'healthy',
            'active_targets': active_targets,
            'recent_jobs': recent_jobs,
            'failed_jobs': failed_jobs,
            'timestamp': timezone.now().isoformat(),
            'worker_id': self.request.id if hasattr(self.request, 'id') else 'unknown'
        }
        
        # Mark as unhealthy if too many failures
        if failed_jobs > 10:
            health_status['status'] = 'warning'
        if failed_jobs > 50:
            health_status['status'] = 'unhealthy'
        
        return health_status
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }

# Task error handling
@app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def error_handling_task(self, task_func, *args, **kwargs):
    """Wrapper task for error handling"""
    try:
        return task_func(*args, **kwargs)
    except Exception as exc:
        # Log the error
        self.update_state(
            state='FAILURE',
            meta={'exc_type': type(exc).__name__, 'exc_message': str(exc)}
        )
        raise

# Task monitoring
@app.task(bind=True)
def monitor_task_execution(self, task_name, *args, **kwargs):
    """Monitor task execution and performance"""
    start_time = timezone.now()
    
    try:
        # Execute the actual task
        result = self.app.tasks[task_name].apply(args=args, kwargs=kwargs)
        
        # Calculate execution time
        execution_time = (timezone.now() - start_time).total_seconds()
        
        # Log performance metrics
        from apps.scraping.utils import log_scraping_activity
        log_scraping_activity(
            level='info',
            message=f'Task {task_name} completed in {execution_time:.2f}s',
            source='task_monitor',
            details={
                'task_name': task_name,
                'execution_time': execution_time,
                'args': args,
                'kwargs': kwargs
            }
        )
        
        return result
        
    except Exception as exc:
        execution_time = (timezone.now() - start_time).total_seconds()
        
        # Log error
        from apps.scraping.utils import log_scraping_activity
        log_scraping_activity(
            level='error',
            message=f'Task {task_name} failed after {execution_time:.2f}s: {str(exc)}',
            source='task_monitor',
            details={
                'task_name': task_name,
                'execution_time': execution_time,
                'error': str(exc),
                'args': args,
                'kwargs': kwargs
            }
        )
        
        raise

# Queue management
@app.task(bind=True)
def manage_queues(self):
    """Manage queue sizes and priorities"""
    try:
        from celery import current_app
        
        # Get queue information
        inspect = current_app.control.inspect()
        active_queues = inspect.active_queues()
        
        if active_queues:
            for worker, queues in active_queues.items():
                for queue in queues:
                    queue_name = queue['name']
                    queue_size = queue.get('messages', 0)
                    
                    # Log queue status
                    from apps.scraping.utils import log_scraping_activity
                    log_scraping_activity(
                        level='info',
                        message=f'Queue {queue_name} on {worker} has {queue_size} messages',
                        source='queue_manager'
                    )
                    
                    # Alert if queue is getting too large
                    if queue_size > 100:
                        log_scraping_activity(
                            level='warning',
                            message=f'Queue {queue_name} is getting large: {queue_size} messages',
                            source='queue_manager'
                        )
        
        return {'status': 'success', 'queues_checked': len(active_queues) if active_queues else 0}
        
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

# Add queue management to beat schedule
app.conf.beat_schedule.update({
    'manage-queues': {
        'task': 'apps.scraping.celery.manage_queues',
        'schedule': 300.0,  # Every 5 minutes
        'options': {'queue': 'monitoring'}
    },
})
