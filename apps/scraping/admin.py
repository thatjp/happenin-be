from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import (
    ScrapingTarget, ScrapingJob, ScrapedData, ScrapingRule,
    ScrapingLog, ScrapingMetrics
)


@admin.register(ScrapingTarget)
class ScrapingTargetAdmin(admin.ModelAdmin):
    """Admin interface for scraping targets"""
    list_display = [
        'name', 'url', 'status', 'frequency', 'next_scrape_at', 
        'last_scraped', 'created_by', 'created_at'
    ]
    list_filter = [
        'status', 'frequency', 'created_at', 'last_scraped'
    ]
    search_fields = ['name', 'url', 'created_by__username']
    readonly_fields = [
        'created_at', 'updated_at', 'last_scraped', 'next_scrape_at'
    ]
    ordering = ['name']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'url', 'created_by')
        }),
        ('Scraping Configuration', {
            'fields': ('status', 'frequency', 'custom_interval_minutes')
        }),
        ('Rate Limiting & Politeness', {
            'fields': ('delay_between_requests', 'max_requests_per_hour')
        }),
        ('Scraping Behavior', {
            'fields': ('respect_robots_txt', 'user_agent')
        }),
        ('Data Extraction', {
            'fields': ('extraction_rules',),
            'classes': ('collapse',)
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at', 'last_scraped', 'next_scrape_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('created_by')
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly for existing objects"""
        if obj:  # Editing existing object
            return self.readonly_fields + ('created_by',)
        return self.readonly_fields


@admin.register(ScrapingJob)
class ScrapingJobAdmin(admin.ModelAdmin):
    """Admin interface for scraping jobs"""
    list_display = [
        'id', 'target', 'job_type', 'status', 'success', 'items_scraped',
        'scheduled_at', 'started_at', 'duration_display', 'created_at'
    ]
    list_filter = [
        'status', 'job_type', 'success', 'created_at', 'scheduled_at'
    ]
    search_fields = [
        'target__name', 'target__url', 'error_message'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'duration_display'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Job Information', {
            'fields': ('target', 'job_type', 'status', 'success')
        }),
        ('Timing', {
            'fields': ('scheduled_at', 'started_at', 'completed_at', 'duration_display')
        }),
        ('Results', {
            'fields': ('items_scraped', 'error_message')
        }),
        ('Performance', {
            'fields': ('response_time_ms', 'response_size_bytes')
        }),
        ('System', {
            'fields': ('celery_task_id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('target')
    
    def duration_display(self, obj):
        """Display job duration in human-readable format"""
        if obj.duration_seconds:
            if obj.duration_seconds < 60:
                return f"{obj.duration_seconds:.1f}s"
            elif obj.duration_seconds < 3600:
                minutes = obj.duration_seconds / 60
                return f"{minutes:.1f}m"
            else:
                hours = obj.duration_seconds / 3600
                return f"{hours:.1f}h"
        return "-"
    duration_display.short_description = "Duration"


@admin.register(ScrapedData)
class ScrapedDataAdmin(admin.ModelAdmin):
    """Admin interface for scraped data"""
    list_display = [
        'id', 'job', 'url', 'title', 'status', 'http_status_code',
        'scraped_at', 'processed_at'
    ]
    list_filter = [
        'status', 'http_status_code', 'scraped_at', 'processed_at'
    ]
    search_fields = [
        'url', 'title', 'content', 'job__target__name'
    ]
    readonly_fields = [
        'scraped_at', 'processed_at', 'content_preview', 'extracted_data_display'
    ]
    ordering = ['-scraped_at']
    date_hierarchy = 'scraped_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('job', 'url', 'title', 'status')
        }),
        ('Content', {
            'fields': ('content', 'content_preview', 'raw_html')
        }),
        ('Extracted Data', {
            'fields': ('extracted_data_display',)
        }),
        ('Metadata', {
            'fields': ('http_status_code', 'content_type')
        }),
        ('Timestamps', {
            'fields': ('scraped_at', 'processed_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('job__target')
    
    def content_preview(self, obj):
        """Show preview of content"""
        if obj.content:
            preview = obj.content[:200] + "..." if len(obj.content) > 200 else obj.content
            return format_html('<div style="max-height: 100px; overflow-y: auto;">{}</div>', preview)
        return "-"
    content_preview.short_description = "Content Preview"
    
    def extracted_data_display(self, obj):
        """Display extracted data in a readable format"""
        if obj.extracted_data:
            import json
            formatted = json.dumps(obj.extracted_data, indent=2)
            return format_html('<pre style="max-height: 200px; overflow-y: auto;">{}</pre>', formatted)
        return "-"
    extracted_data_display.short_description = "Extracted Data"


@admin.register(ScrapingRule)
class ScrapingRuleAdmin(admin.ModelAdmin):
    """Admin interface for scraping rules"""
    list_display = [
        'name', 'target', 'rule_type', 'selector', 'data_type',
        'priority', 'is_active', 'created_at'
    ]
    list_filter = [
        'rule_type', 'data_type', 'is_active', 'created_at'
    ]
    search_fields = [
        'name', 'target__name', 'selector'
    ]
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['target__name', 'priority', 'name']
    
    fieldsets = (
        ('Rule Information', {
            'fields': ('name', 'target', 'rule_type', 'is_active')
        }),
        ('Extraction Configuration', {
            'fields': ('selector', 'attribute', 'data_type')
        }),
        ('Processing', {
            'fields': ('post_processing', 'priority')
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('target')


@admin.register(ScrapingLog)
class ScrapingLogAdmin(admin.ModelAdmin):
    """Admin interface for scraping logs"""
    list_display = [
        'id', 'target', 'job', 'level', 'message_preview', 'created_at'
    ]
    list_filter = [
        'level', 'created_at', 'target__name'
    ]
    search_fields = [
        'message', 'target__name', 'job__id'
    ]
    readonly_fields = ['created_at', 'context_display']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Log Information', {
            'fields': ('target', 'job', 'level', 'message')
        }),
        ('Context', {
            'fields': ('context_display',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        })
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('target', 'job')
    
    def message_preview(self, obj):
        """Show preview of log message"""
        if obj.message:
            preview = obj.message[:100] + "..." if len(obj.message) > 100 else obj.message
            return preview
        return "-"
    message_preview.short_description = "Message"
    
    def context_display(self, obj):
        """Display context data in a readable format"""
        if obj.context:
            import json
            formatted = json.dumps(obj.context, indent=2)
            return format_html('<pre style="max-height: 200px; overflow-y: auto;">{}</pre>', formatted)
        return "-"
    context_display.short_description = "Context"


@admin.register(ScrapingMetrics)
class ScrapingMetricsAdmin(admin.ModelAdmin):
    """Admin interface for scraping metrics"""
    list_display = [
        'target', 'date', 'jobs_scheduled', 'jobs_completed', 'jobs_failed',
        'items_scraped', 'data_processed', 'success_rate', 'avg_response_time'
    ]
    list_filter = ['date', 'target__name']
    search_fields = ['target__name']
    readonly_fields = ['created_at', 'updated_at', 'success_rate', 'avg_response_time']
    ordering = ['-date', 'target__name']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Target Information', {
            'fields': ('target', 'date')
        }),
        ('Job Metrics', {
            'fields': ('jobs_scheduled', 'jobs_completed', 'jobs_failed', 'success_rate')
        }),
        ('Data Metrics', {
            'fields': ('items_scraped', 'data_processed')
        }),
        ('Performance Metrics', {
            'fields': ('avg_response_time_ms', 'total_response_size_bytes')
        }),
        ('Error Metrics', {
            'fields': ('errors_count', 'warnings_count')
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('target')
    
    def success_rate(self, obj):
        """Calculate and display success rate"""
        if obj.jobs_scheduled > 0:
            rate = (obj.jobs_completed / obj.jobs_scheduled) * 100
            return f"{rate:.1f}%"
        return "0%"
    success_rate.short_description = "Success Rate"
    
    def avg_response_time(self, obj):
        """Display average response time"""
        if obj.avg_response_time_ms:
            return f"{obj.avg_response_time_ms:.1f}ms"
        return "-"
    avg_response_time.short_description = "Avg Response Time"


# Custom admin actions
@admin.action(description="Mark selected targets as active")
def make_active(modeladmin, request, queryset):
    queryset.update(status=ScrapingTarget.ScrapingStatus.ACTIVE)
make_active.short_description = "Mark selected targets as active"

@admin.action(description="Mark selected targets as paused")
def make_paused(modeladmin, request, queryset):
    queryset.update(status=ScrapingTarget.ScrapingStatus.PAUSED)
make_paused.short_description = "Mark selected targets as paused"

@admin.action(description="Mark selected targets as disabled")
def make_disabled(modeladmin, request, queryset):
    queryset.update(status=ScrapingTarget.ScrapingStatus.DISABLED)
make_disabled.short_description = "Mark selected targets as disabled"

# Add actions to ScrapingTargetAdmin
ScrapingTargetAdmin.actions = [make_active, make_paused, make_disabled]


# Custom admin views for statistics
class ScrapingStatisticsAdmin(admin.ModelAdmin):
    """Custom admin view for scraping statistics"""
    change_list_template = 'admin/scraping/scrapingtarget/change_list.html'
    
    def changelist_view(self, request, extra_context=None):
        """Add statistics to the change list view"""
        extra_context = extra_context or {}
        
        # Get basic statistics
        total_targets = ScrapingTarget.objects.count()
        active_targets = ScrapingTarget.objects.filter(
            status=ScrapingTarget.ScrapingStatus.ACTIVE
        ).count()
        
        # Get job statistics for last 7 days
        week_ago = timezone.now() - timedelta(days=7)
        recent_jobs = ScrapingJob.objects.filter(created_at__gte=week_ago)
        
        total_jobs = recent_jobs.count()
        successful_jobs = recent_jobs.filter(success=True).count()
        failed_jobs = recent_jobs.filter(success=False).count()
        
        # Get data statistics
        total_data = ScrapedData.objects.filter(scraped_at__gte=week_ago).count()
        
        extra_context.update({
            'total_targets': total_targets,
            'active_targets': active_targets,
            'total_jobs': total_jobs,
            'successful_jobs': successful_jobs,
            'failed_jobs': failed_jobs,
            'total_data': total_data,
            'success_rate': (successful_jobs / total_jobs * 100) if total_jobs > 0 else 0,
        })
        
        return super().changelist_view(request, extra_context)


# Replace the default ScrapingTargetAdmin with the statistics version
admin.site.unregister(ScrapingTarget)
admin.site.register(ScrapingTarget, ScrapingStatisticsAdmin)
