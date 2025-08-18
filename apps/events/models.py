from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Event(models.Model):
    """Event model for managing events with location and time information"""
    
    # Basic event information
    title = models.CharField(max_length=200, help_text="Event title")
    description = models.TextField(blank=True, help_text="Event description")
    
    # Event categorization
    event_type = models.CharField(
        max_length=100, 
        default="General",
        help_text="Type/category of the event (e.g., Music, Sports, Food, Art, Business, Education)"
    )
    icon = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Icon identifier for the event (e.g., 'music-note', 'soccer-ball', 'utensils')"
    )
    
    # Pricing information
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="Event price (leave blank if free)"
    )
    is_free = models.BooleanField(
        default=True, 
        help_text="Whether the event is free to attend"
    )
    
    # Address information
    address = models.TextField(help_text="Full address of the event")
    city = models.CharField(max_length=100, help_text="City where event is located")
    state = models.CharField(max_length=100, blank=True, help_text="State/province")
    country = models.CharField(max_length=100, default="United States", help_text="Country")
    postal_code = models.CharField(max_length=20, blank=True, help_text="Postal/ZIP code")
    
    # Time information
    open_time = models.TimeField(help_text="Event opening time")
    close_time = models.TimeField(help_text="Event closing time")
    start_date = models.DateField(help_text="Event start date")
    end_date = models.DateField(help_text="Event end date")
    
    # Location coordinates
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text="Latitude coordinate"
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text="Longitude coordinate"
    )
    
    # Status flags
    is_open = models.BooleanField(default=True, help_text="Whether the event is currently open")
    is_active = models.BooleanField(default=True, help_text="Whether the event is active/published")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='created_events',
        help_text="User who created this event"
    )
    
    class Meta:
        ordering = ['-start_date', '-created_at']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
    
    def __str__(self):
        return f"{self.title} - {self.city}"
    
    @property
    def lat_lng(self):
        """Return latitude and longitude as a tuple"""
        return (float(self.latitude), float(self.longitude))
    
    @property
    def is_currently_open(self):
        """Check if event is currently open based on time and date"""
        now = timezone.now()
        current_time = now.time()
        current_date = now.date()
        
        # Check if current date is within event dates
        if not (self.start_date <= current_date <= self.end_date):
            return False
        
        # Check if current time is within open hours
        if self.open_time <= self.close_time:
            # Same day (e.g., 9 AM to 5 PM)
            return self.open_time <= current_time <= self.close_time
        else:
            # Overnight (e.g., 10 PM to 6 AM)
            return current_time >= self.open_time or current_time <= self.close_time
    
    @property
    def full_address(self):
        """Return formatted full address"""
        address_parts = [self.address, self.city]
        if self.state:
            address_parts.append(self.state)
        if self.postal_code:
            address_parts.append(self.postal_code)
        address_parts.append(self.country)
        return ", ".join(filter(None, address_parts))
    
    def save(self, *args, **kwargs):
        """Override save to automatically set is_free based on price"""
        if self.price is None or self.price == 0:
            self.is_free = True
        else:
            self.is_free = False
        super().save(*args, **kwargs)
