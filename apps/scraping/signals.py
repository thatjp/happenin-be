from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.core.cache import cache

from .models import (
    ScrapingTarget, ScrapingJob, ScrapedData, ScrapingRule,
    ScrapingLog, ScrapingMetrics
)


@receiver(post_save, sender=ScrapingTarget)
def scraping_target_saved(sender, instance, created, **kwargs):
    """Handle scraping target save events"""
    if created:
        # New target created
        cache_key = f"scraping_target_created:{instance.id}"
        cache.set(cache_key, True, 300)  # Cache for 5 minutes
        
        # Log the creation
        ScrapingLog.objects.create(
            target=instance,
            level=ScrapingLog.LogLevel.INFO,
            message=f"New scraping target '{instance.name}' created",
            context={
                'target_id': instance.id,
                'url': instance.url,
                'frequency': instance.frequency
            }
        )
    else:
        # Target updated
        cache_key = f"scraping_target_updated:{instance.id}"
        cache.set(cache_key, True, 300)  # Cache for 5 minutes
        
        # Log significant changes
        if hasattr(instance, '_state') and hasattr(instance._state, 'fields_cache'):
            old_values = instance._state.fields_cache
            new_values = {
                'status': instance.status,
                'frequency': instance.frequency,
                'delay_between_requests': instance.delay_between_requests,
                'max_requests_per_hour': instance.max_requests_per_hour
            }
            
            changes = []
            for field, new_value in new_values.items():
                old_value = old_values.get(field)
                if old_value != new_value:
                    changes.append(f"{field}: {old_value} → {new_value}")
            
            if changes:
                ScrapingLog.objects.create(
                    target=instance,
                    level=ScrapingLog.LogLevel.INFO,
                    message=f"Scraping target '{instance.name}' updated",
                    context={
                        'target_id': instance.id,
                        'changes': changes
                    }
                )


@receiver(post_save, sender=ScrapingJob)
def scraping_job_saved(sender, instance, created, **kwargs):
    """Handle scraping job save events"""
    if created:
        # New job created
        cache_key = f"scraping_job_created:{instance.id}"
        cache.set(cache_key, True, 300)  # Cache for 5 minutes
        
        # Log job creation
        ScrapingLog.objects.create(
            target=instance.target,
            job=instance,
            level=ScrapingLog.LogLevel.INFO,
            message=f"New scraping job {instance.id} created for '{instance.target.name}'",
            context={
                'job_id': instance.id,
                'job_type': instance.job_type,
                'scheduled_at': instance.scheduled_at.isoformat() if instance.scheduled_at else None
            }
        )
    else:
        # Job updated - check for status changes
        if hasattr(instance, '_state') and hasattr(instance._state, 'fields_cache'):
            old_status = instance._state.fields_cache.get('status')
            new_status = instance.status
            
            if old_status and old_status != new_status:
                # Status changed
                ScrapingLog.objects.create(
                    target=instance.target,
                    job=instance,
                    level=ScrapingLog.LogLevel.INFO,
                    message=f"Job {instance.id} status changed from {old_status} to {new_status}",
                    context={
                        'job_id': instance.id,
                        'old_status': old_status,
                        'new_status': new_status,
                        'target_name': instance.target.name
                    }
                )


@receiver(post_save, sender=ScrapedData)
def scraped_data_saved(sender, instance, created, **kwargs):
    """Handle scraped data save events"""
    if created:
        # New data scraped
        cache_key = f"scraped_data_created:{instance.id}"
        cache.set(cache_key, True, 300)  # Cache for 5 minutes
        
        # Log data creation
        ScrapingLog.objects.create(
            target=instance.job.target,
            job=instance.job,
            level=ScrapingLog.LogLevel.INFO,
            message=f"New data scraped from {instance.url}",
            context={
                'data_id': instance.id,
                'url': instance.url,
                'title': instance.title,
                'items_extracted': len(instance.extracted_data) if instance.extracted_data else 0
            }
        )
    else:
        # Data updated - check for status changes
        if hasattr(instance, '_state') and hasattr(instance._state, 'fields_cache'):
            old_status = instance._state.fields_cache.get('status')
            new_status = instance.status
            
            if old_status and old_status != new_status:
                # Status changed
                ScrapingLog.objects.create(
                    target=instance.job.target,
                    job=instance.job,
                    level=ScrapingLog.LogLevel.INFO,
                    message=f"Data {instance.id} status changed from {old_status} to {new_status}",
                    context={
                        'data_id': instance.id,
                        'old_status': old_status,
                        'new_status': new_status,
                        'url': instance.url
                    }
                )


@receiver(post_save, sender=ScrapingRule)
def scraping_rule_saved(sender, instance, created, **kwargs):
    """Handle scraping rule save events"""
    if created:
        # New rule created
        ScrapingLog.objects.create(
            target=instance.target,
            level=ScrapingLog.LogLevel.INFO,
            message=f"New scraping rule '{instance.name}' created for '{instance.target.name}'",
            context={
                'rule_id': instance.id,
                'rule_name': instance.name,
                'rule_type': instance.rule_type,
                'selector': instance.selector
            }
        )
    else:
        # Rule updated
        ScrapingLog.objects.create(
            target=instance.target,
            level=ScrapingLog.LogLevel.INFO,
            message=f"Scraping rule '{instance.name}' updated for '{instance.target.name}'",
            context={
                'rule_id': instance.id,
                'rule_name': instance.name,
                'rule_type': instance.rule_type
            }
        )


@receiver(post_delete, sender=ScrapingTarget)
def scraping_target_deleted(sender, instance, **kwargs):
    """Handle scraping target deletion"""
    # Log deletion
    ScrapingLog.objects.create(
        level=ScrapingLog.LogLevel.WARNING,
        message=f"Scraping target '{instance.name}' deleted",
        context={
            'target_name': instance.name,
            'target_url': instance.url,
            'deleted_at': timezone.now().isoformat()
        }
    )
    
    # Clear related cache
    cache.delete(f"scraping_target_created:{instance.id}")
    cache.delete(f"scraping_target_updated:{instance.id}")


@receiver(post_delete, sender=ScrapingJob)
def scraping_job_deleted(sender, instance, **kwargs):
    """Handle scraping job deletion"""
    # Log deletion
    ScrapingLog.objects.create(
        target=instance.target,
        level=ScrapingLog.LogLevel.WARNING,
        message=f"Scraping job {instance.id} deleted for '{instance.target.name}'",
        context={
            'job_id': instance.id,
            'target_name': instance.target.name,
            'deleted_at': timezone.now().isoformat()
        }
    )
    
    # Clear related cache
    cache.delete(f"scraping_job_created:{instance.id}")


@receiver(post_delete, sender=ScrapedData)
def scraped_data_deleted(sender, instance, **kwargs):
    """Handle scraped data deletion"""
    # Log deletion
    ScrapingLog.objects.create(
        target=instance.job.target,
        job=instance.job,
        level=ScrapingLog.LogLevel.WARNING,
        message=f"Scraped data {instance.id} deleted from {instance.url}",
        context={
            'data_id': instance.id,
            'url': instance.url,
            'deleted_at': timezone.now().isoformat()
        }
    )
    
    # Clear related cache
    cache.delete(f"scraped_data_created:{instance.id}")


@receiver(post_delete, sender=ScrapingRule)
def scraping_rule_deleted(sender, instance, **kwargs):
    """Handle scraping rule deletion"""
    # Log deletion
    ScrapingLog.objects.create(
        target=instance.target,
        level=ScrapingLog.LogLevel.WARNING,
        message=f"Scraping rule '{instance.name}' deleted from '{instance.target.name}'",
        context={
            'rule_id': instance.id,
            'rule_name': instance.name,
            'target_name': instance.target.name,
            'deleted_at': timezone.now().isoformat()
        }
    )


# Signal to update metrics when jobs are completed
@receiver(post_save, sender=ScrapingJob)
def update_metrics_on_job_completion(sender, instance, **kwargs):
    """Update metrics when a job is completed"""
    if instance.status == ScrapingJob.JobStatus.COMPLETED:
        try:
            # Get or create metrics for today
            today = timezone.now().date()
            metrics, created = ScrapingMetrics.objects.get_or_create(
                target=instance.target,
                date=today,
                defaults={
                    'jobs_scheduled': 0,
                    'jobs_completed': 0,
                    'jobs_failed': 0,
                    'items_scraped': 0,
                    'data_processed': 0,
                    'total_response_size_bytes': 0,
                    'errors_count': 0,
                    'warnings_count': 0,
                }
            )
            
            # Update job counts
            if instance.success:
                metrics.jobs_completed += 1
            else:
                metrics.jobs_failed += 1
            
            # Update performance metrics
            if instance.response_time_ms:
                # Calculate new average
                existing_jobs = ScrapingJob.objects.filter(
                    target=instance.target,
                    status=ScrapingJob.JobStatus.COMPLETED,
                    response_time_ms__isnull=False,
                    created_at__date=today
                ).exclude(id=instance.id)
                
                total_time = instance.response_time_ms
                count = 1
                
                if existing_jobs.exists():
                    existing_avg = existing_jobs.aggregate(
                        avg=models.Avg('response_time_ms')
                    )['avg']
                    if existing_avg:
                        total_time += existing_avg * existing_jobs.count()
                        count += existing_jobs.count()
                
                metrics.avg_response_time_ms = total_time / count
            
            if instance.response_size_bytes:
                metrics.total_response_size_bytes += instance.response_size_bytes
            
            # Update data metrics
            if instance.items_scraped:
                metrics.items_scraped += instance.items_scraped
            
            metrics.save()
            
        except Exception as e:
            # Log error but don't fail the signal
            ScrapingLog.objects.create(
                target=instance.target,
                level=ScrapingLog.LogLevel.ERROR,
                message=f"Error updating metrics for job {instance.id}: {str(e)}",
                context={
                    'job_id': instance.id,
                    'error': str(e)
                }
            )


# Signal to update metrics when data is processed
@receiver(post_save, sender=ScrapedData)
def update_metrics_on_data_processing(sender, instance, **kwargs):
    """Update metrics when data is processed"""
    if instance.status == ScrapedData.DataStatus.PROCESSED:
        try:
            # Get or create metrics for today
            today = timezone.now().date()
            metrics, created = ScrapingMetrics.objects.get_or_create(
                target=instance.job.target,
                date=today,
                defaults={
                    'jobs_scheduled': 0,
                    'jobs_completed': 0,
                    'jobs_failed': 0,
                    'items_scraped': 0,
                    'data_processed': 0,
                    'total_response_size_bytes': 0,
                    'errors_count': 0,
                    'warnings_count': 0,
                }
            )
            
            # Update data processed count
            metrics.data_processed += 1
            metrics.save()
            
        except Exception as e:
            # Log error but don't fail the signal
            ScrapingLog.objects.create(
                target=instance.job.target,
                level=ScrapingLog.LogLevel.ERROR,
                message=f"Error updating metrics for data {instance.id}: {str(e)}",
                context={
                    'data_id': instance.id,
                    'error': str(e)
                }
            )


# Signal to update metrics when logs are created
@receiver(post_save, sender=ScrapingLog)
def update_metrics_on_log_creation(sender, instance, **kwargs):
    """Update metrics when logs are created"""
    if instance.level in [ScrapingLog.LogLevel.ERROR, ScrapingLog.LogLevel.WARNING]:
        try:
            # Get or create metrics for today
            today = timezone.now().date()
            metrics, created = ScrapingMetrics.objects.get_or_create(
                target=instance.target,
                date=today,
                defaults={
                    'jobs_scheduled': 0,
                    'jobs_completed': 0,
                    'jobs_failed': 0,
                    'items_scraped': 0,
                    'data_processed': 0,
                    'total_response_size_bytes': 0,
                    'errors_count': 0,
                    'warnings_count': 0,
                }
            )
            
            # Update error/warning counts
            if instance.level == ScrapingLog.LogLevel.ERROR:
                metrics.errors_count += 1
            elif instance.level == ScrapingLog.LogLevel.WARNING:
                metrics.warnings_count += 1
            
            metrics.save()
            
        except Exception as e:
            # Log error but don't fail the signal
            pass  # Avoid infinite recursion
