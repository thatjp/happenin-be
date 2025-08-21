from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import URLValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
import json

User = get_user_model()


class ScrapingTarget(models.Model):
    """Model for defining websites to scrape"""
    
    class ScrapingStatus(models.TextChoices):
        ACTIVE = 'active', _('Active')
        PAUSED = 'paused', _('Paused')
        DISABLED = 'disabled', _('Disabled')
    
    class ScrapingFrequency(models.TextChoices):
        HOURLY = 'hourly', _('Hourly')
        DAILY = 'daily', _('Daily')
        WEEKLY = 'weekly', _('Weekly')
        MONTHLY = 'monthly', _('Monthly')
        CUSTOM = 'custom', _('Custom')
    
    name = models.CharField(max_length=200, help_text="Name/description of the scraping target")
    url = models.URLField(validators=[URLValidator()], help_text="URL to scrape")
    
    # Scraping configuration
    status = models.CharField(
        max_length=20,
        choices=ScrapingStatus.choices,
        default=ScrapingStatus.ACTIVE
    )
    frequency = models.CharField(
        max_length=20,
        choices=ScrapingFrequency.choices,
        default=ScrapingFrequency.DAILY
    )
    custom_interval_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10080)],  # Max 1 week
        help_text="Custom interval in minutes (only used when frequency is 'custom')"
    )
    
    # Rate limiting and politeness
    delay_between_requests = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(3600)],
        help_text="Delay between requests in seconds"
    )
    max_requests_per_hour = models.PositiveIntegerField(
        default=100,
        validators=[MinValueValidator(1), MaxValueValidator(10000)],
        help_text="Maximum requests per hour"
    )
    
    # Scraping behavior
    respect_robots_txt = models.BooleanField(default=True, help_text="Respect robots.txt file")
    user_agent = models.CharField(
        max_length=500,
        default="Happin Scraper Bot (+https://happin.com/bot)",
        help_text="User agent string to use for requests"
    )
    
    # Data extraction rules
    extraction_rules = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON configuration for data extraction"
    )
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='scraping_targets',
        help_text="User who created this scraping target"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_scraped = models.DateTimeField(null=True, blank=True)
    next_scrape_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = _('Scraping Target')
        verbose_name_plural = _('Scraping Targets')
    
    def __str__(self):
        return f"{self.name} ({self.url})"
    
    def get_interval_minutes(self):
        """Get the interval in minutes based on frequency"""
        if self.frequency == self.ScrapingFrequency.HOURLY:
            return 60
        elif self.frequency == self.ScrapingFrequency.DAILY:
            return 1440  # 24 * 60
        elif self.frequency == self.ScrapingFrequency.WEEKLY:
            return 10080  # 7 * 24 * 60
        elif self.frequency == self.ScrapingFrequency.MONTHLY:
            return 43200  # 30 * 24 * 60
        elif self.frequency == self.ScrapingFrequency.CUSTOM:
            return self.custom_interval_minutes or 1440
        return 1440
    
    def calculate_next_scrape(self):
        """Calculate when the next scrape should occur"""
        if not self.last_scraped:
            return timezone.now()
        
        interval_minutes = self.get_interval_minutes()
        return self.last_scraped + timezone.timedelta(minutes=interval_minutes)
    
    def save(self, *args, **kwargs):
        """Override save to calculate next scrape time"""
        if self.pk:  # Only for existing instances
            old_instance = ScrapingTarget.objects.get(pk=self.pk)
            if old_instance.last_scraped != self.last_scraped:
                self.next_scrape_at = self.calculate_next_scrape()
        else:
            # New instance
            self.next_scrape_at = timezone.now()
        
        super().save(*args, **kwargs)


class ScrapingJob(models.Model):
    """Model for tracking individual scraping jobs"""
    
    class JobStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        RUNNING = 'running', _('Running')
        COMPLETED = 'completed', _('Completed')
        FAILED = 'failed', _('Failed')
        CANCELLED = 'cancelled', _('Cancelled')
    
    class JobType(models.TextChoices):
        SCHEDULED = 'scheduled', _('Scheduled')
        MANUAL = 'manual', _('Manual')
        RETRY = 'retry', _('Retry')
    
    target = models.ForeignKey(
        ScrapingTarget,
        on_delete=models.CASCADE,
        related_name='scraping_jobs'
    )
    
    # Job details
    status = models.CharField(
        max_length=20,
        choices=JobStatus.choices,
        default=JobStatus.PENDING
    )
    job_type = models.CharField(
        max_length=20,
        choices=JobType.choices,
        default=JobType.SCHEDULED
    )
    
    # Timing
    scheduled_at = models.DateTimeField(help_text="When the job was scheduled to run")
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Results
    success = models.BooleanField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    items_scraped = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    response_size_bytes = models.PositiveIntegerField(null=True, blank=True)
    
    # Celery task info
    celery_task_id = models.CharField(max_length=255, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Scraping Job')
        verbose_name_plural = _('Scraping Jobs')
    
    def __str__(self):
        return f"{self.target.name} - {self.get_status_display()} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    @property
    def duration_seconds(self):
        """Calculate job duration in seconds"""
        if not self.started_at or not self.completed_at:
            return None
        return (self.completed_at - self.started_at).total_seconds()
    
    def mark_started(self):
        """Mark job as started"""
        self.status = self.JobStatus.RUNNING
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at', 'updated_at'])
    
    def mark_completed(self, success=True, items_scraped=0, error_message=""):
        """Mark job as completed"""
        self.status = self.JobStatus.COMPLETED
        self.completed_at = timezone.now()
        self.success = success
        self.items_scraped = items_scraped
        self.error_message = error_message
        self.save(update_fields=[
            'status', 'completed_at', 'success', 'items_scraped', 
            'error_message', 'updated_at'
        ])
    
    def mark_failed(self, error_message=""):
        """Mark job as failed"""
        self.status = self.JobStatus.FAILED
        self.completed_at = timezone.now()
        self.success = False
        self.error_message = error_message
        self.save(update_fields=[
            'status', 'completed_at', 'success', 'error_message', 'updated_at'
        ])


class ScrapedData(models.Model):
    """Model for storing scraped data"""
    
    class DataStatus(models.TextChoices):
        RAW = 'raw', _('Raw')
        PROCESSED = 'processed', _('Processed')
        ARCHIVED = 'archived', _('Archived')
    
    job = models.ForeignKey(
        ScrapingJob,
        on_delete=models.CASCADE,
        related_name='scraped_data'
    )
    
    # Data content
    url = models.URLField(help_text="URL that was scraped")
    title = models.CharField(max_length=500, blank=True)
    content = models.TextField(blank=True)
    raw_html = models.TextField(blank=True)
    
    # Extracted data
    extracted_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured data extracted from the page"
    )
    
    # Metadata
    status = models.CharField(
        max_length=20,
        choices=DataStatus.choices,
        default=DataStatus.RAW
    )
    http_status_code = models.PositiveIntegerField(null=True, blank=True)
    content_type = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    scraped_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-scraped_at']
        verbose_name = _('Scraped Data')
        verbose_name_plural = _('Scraped Data')
        indexes = [
            models.Index(fields=['status', 'scraped_at']),
            models.Index(fields=['url', 'scraped_at']),
        ]
    
    def __str__(self):
        return f"{self.title or self.url} - {self.scraped_at.strftime('%Y-%m-%d %H:%M')}"
    
    def mark_processed(self):
        """Mark data as processed"""
        self.status = self.DataStatus.PROCESSED
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_at'])


class ScrapingRule(models.Model):
    """Model for defining data extraction rules"""
    
    class RuleType(models.TextChoices):
        CSS_SELECTOR = 'css_selector', _('CSS Selector')
        XPATH = 'xpath', _('XPath')
        REGEX = 'regex', _('Regular Expression')
        JSON_PATH = 'json_path', _('JSON Path')
    
    target = models.ForeignKey(
        ScrapingTarget,
        on_delete=models.CASCADE,
        related_name='scraping_rules'
    )
    
    name = models.CharField(max_length=200, help_text="Name/description of the rule")
    rule_type = models.CharField(
        max_length=20,
        choices=RuleType.choices,
        default=RuleType.CSS_SELECTOR
    )
    
    # Rule configuration
    selector = models.CharField(max_length=500, help_text="CSS selector, XPath, or regex pattern")
    attribute = models.CharField(
        max_length=100,
        blank=True,
        help_text="HTML attribute to extract (e.g., 'href', 'src')"
    )
    
    # Data processing
    data_type = models.CharField(
        max_length=50,
        default='text',
        help_text="Type of data to extract (text, number, date, url, etc.)"
    )
    post_processing = models.JSONField(
        default=dict,
        blank=True,
        help_text="Post-processing rules (cleaning, validation, etc.)"
    )
    
    # Priority and ordering
    priority = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Priority for processing (lower numbers = higher priority)"
    )
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['priority', 'name']
        verbose_name = _('Scraping Rule')
        verbose_name_plural = _('Scraping Rules')
        unique_together = ['target', 'name']
    
    def __str__(self):
        return f"{self.target.name} - {self.name} ({self.get_rule_type_display()})"


class ScrapingLog(models.Model):
    """Model for detailed logging of scraping activities"""
    
    class LogLevel(models.TextChoices):
        DEBUG = 'debug', _('Debug')
        INFO = 'info', _('Info')
        WARNING = 'warning', _('Warning')
        ERROR = 'error', _('Error')
        CRITICAL = 'critical', _('Critical')
    
    job = models.ForeignKey(
        ScrapingJob,
        on_delete=models.CASCADE,
        related_name='logs',
        null=True,
        blank=True
    )
    target = models.ForeignKey(
        ScrapingTarget,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    
    # Log details
    level = models.CharField(
        max_length=20,
        choices=LogLevel.choices,
        default=LogLevel.INFO
    )
    message = models.TextField(help_text="Log message")
    
    # Additional context
    context = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional context data for the log entry"
    )
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Scraping Log')
        verbose_name_plural = _('Scraping Logs')
        indexes = [
            models.Index(fields=['level', 'created_at']),
            models.Index(fields=['target', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.target.name} - {self.get_level_display()}: {self.message[:50]}"


class ScrapingMetrics(models.Model):
    """Model for storing aggregated scraping metrics"""
    
    target = models.ForeignKey(
        ScrapingTarget,
        on_delete=models.CASCADE,
        related_name='metrics'
    )
    
    # Date for aggregation
    date = models.DateField(help_text="Date for these metrics")
    
    # Counts
    jobs_scheduled = models.PositiveIntegerField(default=0)
    jobs_completed = models.PositiveIntegerField(default=0)
    jobs_failed = models.PositiveIntegerField(default=0)
    
    # Data metrics
    items_scraped = models.PositiveIntegerField(default=0)
    data_processed = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    avg_response_time_ms = models.FloatField(null=True, blank=True)
    total_response_size_bytes = models.BigIntegerField(default=0)
    
    # Error metrics
    errors_count = models.PositiveIntegerField(default=0)
    warnings_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['target', 'date']
        ordering = ['-date']
        verbose_name = _('Scraping Metrics')
        verbose_name_plural = _('Scraping Metrics')
    
    def __str__(self):
        return f"{self.target.name} - {self.date} (Jobs: {self.jobs_completed}/{self.jobs_scheduled})"
