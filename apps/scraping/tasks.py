import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
from celery import shared_task
from django.utils import timezone
from django.db import transaction
from django.conf import settings

import requests
from bs4 import BeautifulSoup
import lxml.etree as etree
import re
import json

from .models import (
    ScrapingTarget, ScrapingJob, ScrapedData, ScrapingRule,
    ScrapingLog, ScrapingMetrics
)
from .scrapers import WebScraper, ScrapingResult
from .utils import (
    is_robots_txt_allowed, get_rate_limit_key, 
    check_rate_limit, update_rate_limit
)

logger = logging.getLogger(__name__)


@shared_task(bind=True, name='apps.scraping.tasks.scrape_scheduled_targets')
def scrape_scheduled_targets(self):
    """
    Celery Beat task to check for targets that need scraping
    Runs every minute to check for scheduled scraping jobs
    """
    try:
        now = timezone.now()
        
        # Find targets that are due for scraping
        targets_to_scrape = ScrapingTarget.objects.filter(
            status=ScrapingTarget.ScrapingStatus.ACTIVE,
            next_scrape_at__lte=now
        ).select_related('created_by')
        
        logger.info(f"Found {targets_to_scrape.count()} targets due for scraping")
        
        for target in targets_to_scrape:
            # Check rate limiting
            if not check_rate_limit(target):
                logger.warning(f"Rate limit exceeded for {target.name}")
                continue
            
            # Create scraping job
            job = ScrapingJob.objects.create(
                target=target,
                job_type=ScrapingJob.JobType.SCHEDULED,
                scheduled_at=now,
                celery_task_id=self.request.id
            )
            
            # Start scraping asynchronously
            scrape_website.delay(job.id)
            
            # Update target's next scrape time
            target.last_scraped = now
            target.save()
            
            logger.info(f"Scheduled scraping job {job.id} for target {target.name}")
        
        return f"Processed {targets_to_scrape.count()} scraping targets"
        
    except Exception as e:
        logger.error(f"Error in scrape_scheduled_targets: {e}")
        raise


@shared_task(bind=True, name='apps.scraping.tasks.scrape_website')
def scrape_website(self, job_id: int) -> Dict[str, Any]:
    """
    Main scraping task that processes a single scraping job
    
    Args:
        job_id: ID of the ScrapingJob to process
    
    Returns:
        Dictionary with scraping results
    """
    job = None
    target = None
    
    try:
        # Get the job and target
        job = ScrapingJob.objects.select_related('target').get(id=job_id)
        target = job.target
        
        # Mark job as started
        job.mark_started()
        
        # Log start
        ScrapingLog.objects.create(
            job=job,
            target=target,
            level=ScrapingLog.LogLevel.INFO,
            message=f"Starting scraping job for {target.url}",
            context={'job_id': job_id, 'target_id': target.id}
        )
        
        # Check if scraping is allowed
        if target.respect_robots_txt:
            if not is_robots_txt_allowed(target.url):
                raise Exception("Scraping not allowed by robots.txt")
        
        # Initialize scraper
        scraper = WebScraper(
            user_agent=target.user_agent,
            delay=target.delay_between_requests
        )
        
        # Perform scraping
        start_time = time.time()
        result = scraper.scrape(target.url)
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Update job with performance metrics
        job.response_time_ms = response_time_ms
        job.response_size_bytes = len(result.raw_html) if result.raw_html else 0
        
        # Extract data using rules
        extracted_data = extract_data_from_page(target, result)
        
        # Store scraped data
        scraped_data = ScrapedData.objects.create(
            job=job,
            url=target.url,
            title=result.title,
            content=result.content,
            raw_html=result.raw_html,
            extracted_data=extracted_data,
            http_status_code=result.status_code,
            content_type=result.content_type
        )
        
        # Mark job as completed
        job.mark_completed(
            success=True,
            items_scraped=len(extracted_data) if extracted_data else 0
        )
        
        # Log success
        ScrapingLog.objects.create(
            job=job,
            target=target,
            level=ScrapingLog.LogLevel.INFO,
            message=f"Successfully scraped {target.url}",
            context={
                'job_id': job_id,
                'data_id': scraped_data.id,
                'items_extracted': len(extracted_data) if extracted_data else 0,
                'response_time_ms': response_time_ms
            }
        )
        
        # Update rate limiting
        update_rate_limit(target)
        
        return {
            'success': True,
            'job_id': job_id,
            'target_name': target.name,
            'items_scraped': len(extracted_data) if extracted_data else 0,
            'response_time_ms': response_time_ms
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error scraping website (job {job_id}): {error_msg}")
        
        if job:
            job.mark_failed(error_message=error_msg)
            
            # Log error
            if target:
                ScrapingLog.objects.create(
                    job=job,
                    target=target,
                    level=ScrapingLog.LogLevel.ERROR,
                    message=f"Scraping failed: {error_msg}",
                    context={'job_id': job_id, 'error': error_msg}
                )
        
        return {
            'success': False,
            'job_id': job_id,
            'error': error_msg
        }


@shared_task(name='apps.scraping.tasks.scrape_target_manual')
def scrape_target_manual(target_id: int, user_id: int) -> Dict[str, Any]:
    """
    Manual scraping task for immediate execution
    
    Args:
        target_id: ID of the ScrapingTarget to scrape
        user_id: ID of the user requesting the scrape
    
    Returns:
        Dictionary with scraping results
    """
    try:
        target = ScrapingTarget.objects.get(id=target_id)
        
        # Create manual job
        job = ScrapingJob.objects.create(
            target=target,
            job_type=ScrapingJob.JobType.MANUAL,
            scheduled_at=timezone.now()
        )
        
        # Start scraping
        result = scrape_website.delay(job.id)
        
        return {
            'success': True,
            'job_id': job.id,
            'task_id': result.id,
            'message': f"Manual scraping job {job.id} created for {target.name}"
        }
        
    except ScrapingTarget.DoesNotExist:
        return {
            'success': False,
            'error': f"Scraping target {target_id} not found"
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@shared_task(name='apps.scraping.tasks.extract_data_from_page')
def extract_data_from_page(target: ScrapingTarget, result: ScrapingResult) -> Dict[str, Any]:
    """
    Extract data from scraped page using defined rules
    
    Args:
        target: ScrapingTarget with extraction rules
        result: ScrapingResult containing page data
    
    Returns:
        Dictionary with extracted data
    """
    extracted_data = {}
    
    try:
        # Get active scraping rules for this target
        rules = ScrapingRule.objects.filter(
            target=target,
            is_active=True
        ).order_by('priority')
        
        if not rules.exists():
            # Use default extraction if no rules defined
            extracted_data = extract_default_data(result)
        else:
            # Apply custom rules
            for rule in rules:
                try:
                    value = apply_scraping_rule(rule, result)
                    if value is not None:
                        extracted_data[rule.name] = value
                except Exception as e:
                    logger.warning(f"Error applying rule {rule.name}: {e}")
                    continue
        
        return extracted_data
        
    except Exception as e:
        logger.error(f"Error extracting data: {e}")
        return {}


def extract_default_data(result: ScrapingResult) -> Dict[str, Any]:
    """Extract default data when no custom rules are defined"""
    data = {}
    
    if result.title:
        data['title'] = result.title
    
    if result.content:
        # Extract first paragraph
        soup = BeautifulSoup(result.content, 'html.parser')
        first_p = soup.find('p')
        if first_p:
            data['first_paragraph'] = first_p.get_text(strip=True)
    
    # Extract all links
    if result.raw_html:
        soup = BeautifulSoup(result.raw_html, 'html.parser')
        links = soup.find_all('a', href=True)
        data['links'] = [link['href'] for link in links[:10]]  # Limit to 10 links
    
    return data


def apply_scraping_rule(rule: ScrapingRule, result: ScrapingResult) -> Any:
    """
    Apply a single scraping rule to extract data
    
    Args:
        rule: ScrapingRule to apply
        result: ScrapingResult containing page data
    
    Returns:
        Extracted value or None if extraction failed
    """
    try:
        if rule.rule_type == ScrapingRule.RuleType.CSS_SELECTOR:
            return extract_with_css_selector(rule, result.raw_html)
        elif rule.rule_type == ScrapingRule.RuleType.XPATH:
            return extract_with_xpath(rule, result.raw_html)
        elif rule.rule_type == ScrapingRule.RuleType.REGEX:
            return extract_with_regex(rule, result.raw_html)
        elif rule.rule_type == ScrapingRule.RuleType.JSON_PATH:
            return extract_with_json_path(rule, result.raw_html)
        else:
            logger.warning(f"Unknown rule type: {rule.rule_type}")
            return None
            
    except Exception as e:
        logger.error(f"Error applying rule {rule.name}: {e}")
        return None


def extract_with_css_selector(rule: ScrapingRule, html: str) -> Any:
    """Extract data using CSS selector"""
    soup = BeautifulSoup(html, 'html.parser')
    elements = soup.select(rule.selector)
    
    if not elements:
        return None
    
    if rule.attribute:
        # Extract specific attribute
        values = [elem.get(rule.attribute) for elem in elements if elem.get(rule.attribute)]
    else:
        # Extract text content
        values = [elem.get_text(strip=True) for elem in elements]
    
    # Return single value or list based on number of matches
    if len(values) == 1:
        return values[0]
    elif len(values) > 1:
        return values
    else:
        return None


def extract_with_xpath(rule: ScrapingRule, html: str) -> Any:
    """Extract data using XPath"""
    try:
        tree = etree.HTML(html)
        elements = tree.xpath(rule.selector)
        
        if not elements:
            return None
        
        if rule.attribute:
            # Extract specific attribute
            values = [elem.get(rule.attribute) for elem in elements if hasattr(elem, 'get')]
        else:
            # Extract text content
            values = [elem.text if hasattr(elem, 'text') else str(elem) for elem in elements]
        
        # Return single value or list based on number of matches
        if len(values) == 1:
            return values[0]
        elif len(values) > 1:
            return values
        else:
            return None
            
    except Exception as e:
        logger.error(f"XPath extraction error: {e}")
        return None


def extract_with_regex(rule: ScrapingRule, html: str) -> Any:
    """Extract data using regular expression"""
    try:
        matches = re.findall(rule.selector, html, re.IGNORECASE | re.MULTILINE)
        
        if not matches:
            return None
        
        # Return single value or list based on number of matches
        if len(matches) == 1:
            return matches[0]
        else:
            return matches
            
    except Exception as e:
        logger.error(f"Regex extraction error: {e}")
        return None


def extract_with_json_path(rule: ScrapingRule, html: str) -> Any:
    """Extract data using JSON path (for JSON responses)"""
    try:
        # Try to parse as JSON
        data = json.loads(html)
        
        # Simple JSON path implementation
        path_parts = rule.selector.split('.')
        current = data
        
        for part in path_parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            elif isinstance(current, list) and part.isdigit():
                index = int(part)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    return None
            else:
                return None
        
        return current
        
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"JSON path extraction error: {e}")
        return None


@shared_task(name='apps.scraping.tasks.cleanup_old_data')
def cleanup_old_data(days_to_keep: int = 30) -> Dict[str, Any]:
    """
    Clean up old scraping data to prevent database bloat
    
    Args:
        days_to_keep: Number of days of data to keep
    
    Returns:
        Dictionary with cleanup results
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        
        # Clean up old scraped data
        old_data_count = ScrapedData.objects.filter(
            scraped_at__lt=cutoff_date,
            status=ScrapedData.DataStatus.ARCHIVED
        ).count()
        
        ScrapedData.objects.filter(
            scraped_at__lt=cutoff_date,
            status=ScrapedData.DataStatus.ARCHIVED
        ).delete()
        
        # Clean up old logs
        old_logs_count = ScrapingLog.objects.filter(
            created_at__lt=cutoff_date
        ).count()
        
        ScrapingLog.objects.filter(
            created_at__lt=cutoff_date
        ).delete()
        
        # Clean up old metrics (keep only last 90 days)
        metrics_cutoff = timezone.now() - timedelta(days=90)
        old_metrics_count = ScrapingMetrics.objects.filter(
            date__lt=metrics_cutoff.date()
        ).count()
        
        ScrapingMetrics.objects.filter(
            date__lt=metrics_cutoff.date()
        ).delete()
        
        logger.info(f"Cleanup completed: {old_data_count} data records, "
                   f"{old_logs_count} logs, {old_metrics_count} metrics removed")
        
        return {
            'success': True,
            'data_removed': old_data_count,
            'logs_removed': old_logs_count,
            'metrics_removed': old_metrics_count
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup_old_data: {e}")
        return {
            'success': False,
            'error': str(e)
        }


@shared_task(name='apps.scraping.tasks.update_daily_metrics')
def update_daily_metrics() -> Dict[str, Any]:
    """
    Update daily scraping metrics for all targets
    """
    try:
        today = timezone.now().date()
        targets_updated = 0
        
        for target in ScrapingTarget.objects.all():
            try:
                # Get today's jobs
                today_jobs = ScrapingJob.objects.filter(
                    target=target,
                    created_at__date=today
                )
                
                # Calculate metrics
                jobs_scheduled = today_jobs.count()
                jobs_completed = today_jobs.filter(status=ScrapingJob.JobStatus.COMPLETED).count()
                jobs_failed = today_jobs.filter(status=ScrapingJob.JobStatus.FAILED).count()
                
                # Get data metrics
                today_data = ScrapedData.objects.filter(
                    job__target=target,
                    scraped_at__date=today
                )
                
                items_scraped = sum(data.items_scraped for data in today_data if hasattr(data, 'items_scraped'))
                data_processed = today_data.filter(status=ScrapedData.DataStatus.PROCESSED).count()
                
                # Calculate performance metrics
                completed_jobs = today_jobs.filter(
                    status=ScrapingJob.JobStatus.COMPLETED,
                    response_time_ms__isnull=False
                )
                
                if completed_jobs.exists():
                    avg_response_time = completed_jobs.aggregate(
                        avg=models.Avg('response_time_ms')
                    )['avg']
                    total_response_size = completed_jobs.aggregate(
                        sum=models.Sum('response_size_bytes')
                    )['sum'] or 0
                else:
                    avg_response_time = None
                    total_response_size = 0
                
                # Get error counts
                today_logs = ScrapingLog.objects.filter(
                    target=target,
                    created_at__date=today
                )
                
                errors_count = today_logs.filter(level=ScrapingLog.LogLevel.ERROR).count()
                warnings_count = today_logs.filter(level=ScrapingLog.LogLevel.WARNING).count()
                
                # Update or create metrics
                metrics, created = ScrapingMetrics.objects.update_or_create(
                    target=target,
                    date=today,
                    defaults={
                        'jobs_scheduled': jobs_scheduled,
                        'jobs_completed': jobs_completed,
                        'jobs_failed': jobs_failed,
                        'items_scraped': items_scraped,
                        'data_processed': data_processed,
                        'avg_response_time_ms': avg_response_time,
                        'total_response_size_bytes': total_response_size,
                        'errors_count': errors_count,
                        'warnings_count': warnings_count,
                    }
                )
                
                targets_updated += 1
                
            except Exception as e:
                logger.error(f"Error updating metrics for target {target.name}: {e}")
                continue
        
        logger.info(f"Daily metrics updated for {targets_updated} targets")
        
        return {
            'success': True,
            'targets_updated': targets_updated
        }
        
    except Exception as e:
        logger.error(f"Error in update_daily_metrics: {e}")
        return {
            'success': False,
            'error': str(e)
        }


@shared_task(name='apps.scraping.tasks.retry_failed_jobs')
def retry_failed_jobs(max_retries: int = 3) -> Dict[str, Any]:
    """
    Retry failed scraping jobs
    
    Args:
        max_retries: Maximum number of retries per job
    
    Returns:
        Dictionary with retry results
    """
    try:
        # Find failed jobs that can be retried
        failed_jobs = ScrapingJob.objects.filter(
            status=ScrapingJob.JobStatus.FAILED,
            target__status=ScrapingTarget.ScrapingStatus.ACTIVE
        ).select_related('target')
        
        retried_count = 0
        
        for job in failed_jobs:
            try:
                # Create retry job
                retry_job = ScrapingJob.objects.create(
                    target=job.target,
                    job_type=ScrapingJob.JobType.RETRY,
                    scheduled_at=timezone.now()
                )
                
                # Start retry
                scrape_website.delay(retry_job.id)
                retried_count += 1
                
                logger.info(f"Retry job {retry_job.id} created for failed job {job.id}")
                
            except Exception as e:
                logger.error(f"Error creating retry job for {job.id}: {e}")
                continue
        
        return {
            'success': True,
            'jobs_retried': retried_count
        }
        
    except Exception as e:
        logger.error(f"Error in retry_failed_jobs: {e}")
        return {
            'success': False,
            'error': str(e)
        }
