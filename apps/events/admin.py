from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'event_type', 'city', 'price', 'is_free', 'start_date', 'end_date', 
        'open_time', 'close_time', 'is_open', 'is_active', 'created_by', 'created_at'
    ]
    list_filter = [
        'is_open', 'is_active', 'event_type', 'city', 'state', 'country', 
        'start_date', 'end_date', 'is_free'
    ]
    search_fields = ['title', 'description', 'address', 'city', 'state', 'event_type']
    readonly_fields = ['created_at', 'updated_at', 'is_currently_open']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'event_type', 'icon', 'created_by')
        }),
        ('Pricing', {
            'fields': ('price', 'is_free')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Time & Date', {
            'fields': ('start_date', 'end_date', 'open_time', 'close_time')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Status', {
            'fields': ('is_open', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'is_currently_open'),
            'classes': ('collapse',)
        }),
    )
    
    def is_currently_open(self, obj):
        """Display if event is currently open"""
        return obj.is_currently_open
    is_currently_open.boolean = True
    is_currently_open.short_description = 'Currently Open'
