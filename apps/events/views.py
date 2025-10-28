from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from datetime import date
from .models import Event
from .serializers import (
    EventSerializer, EventCreateSerializer, EventUpdateSerializer, EventListSerializer
)
from .utils import success_response, error_response


class EventListView(generics.ListCreateAPIView):
    """List all events or create a new event"""
    queryset = Event.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'state', 'country', 'is_open', 'is_active', 'event_type', 'is_free']
    search_fields = ['title', 'description', 'address', 'city', 'event_type']
    ordering_fields = ['start_date', 'created_at', 'title', 'price']
    ordering = ['-start_date', '-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EventCreateSerializer
        return EventListSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        """Filter events based on query parameters"""
        queryset = Event.objects.filter(is_active=True)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = date.fromisoformat(start_date)
                queryset = queryset.filter(start_date__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = date.fromisoformat(end_date)
                queryset = queryset.filter(end_date__lte=end_date)
            except ValueError:
                pass
        
        # Filter by location (within radius)
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        radius = self.request.query_params.get('radius', 50)  # Default 50km
        
        if lat and lng:
            try:
                lat = float(lat)
                lng = float(lng)
                radius = float(radius)
                
                # Simple distance calculation (approximate)
                # In production, you might want to use PostGIS or similar
                queryset = queryset.filter(
                    latitude__range=(lat - radius/111, lat + radius/111),
                    longitude__range=(lng - radius/111, lng + radius/111)
                )
            except ValueError:
                pass
        
        # Filter by open/closed status
        is_open = self.request.query_params.get('is_open')
        if is_open is not None:
            is_open = is_open.lower() == 'true'
            if is_open:
                queryset = queryset.filter(is_open=True)
            else:
                queryset = queryset.filter(is_open=False)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            try:
                min_price = float(min_price)
                queryset = queryset.filter(price__gte=min_price)
            except ValueError:
                pass
        
        if max_price:
            try:
                max_price = float(max_price)
                queryset = queryset.filter(price__lte=max_price)
            except ValueError:
                pass
        
        # Filter by free events only
        free_only = self.request.query_params.get('free_only')
        if free_only is not None:
            free_only = free_only.lower() == 'true'
            if free_only:
                queryset = queryset.filter(is_free=True)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        # Handle pagination - DRF wraps paginated results in 'results' key
        if isinstance(response.data, dict) and 'results' in response.data:
            # For paginated responses, preserve pagination info
            paginated_data = {
                'results': response.data['results'],
                'count': response.data.get('count', len(response.data['results'])),
                'next': response.data.get('next'),
                'previous': response.data.get('previous')
            }
            return success_response(data=paginated_data)
        # For non-paginated list responses
        return success_response(data=response.data if isinstance(response.data, list) else [response.data])
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return success_response(
            data=serializer.data,
            message='Event created successfully',
            status_code=status.HTTP_201_CREATED
        )


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an event"""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        """Filter events based on active status for public access"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Restrict modifications to creator or admins
            user = self.request.user
            return Event.objects.filter(Q(created_by=user) | Q(admins=user)).distinct()
        else:
            # Only show active events for public access
            return Event.objects.filter(is_active=True)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(data=serializer.data, message='Event updated successfully')
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        # HTTP 204 No Content should not have a body, but for consistency we use 200
        return success_response(message='Event deleted successfully', status_code=status.HTTP_200_OK)


class UserEventsView(generics.ListAPIView):
    """List events created by the current user"""
    serializer_class = EventListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Event.objects.filter(Q(created_by=user) | Q(admins=user)).distinct()
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if isinstance(response.data, dict) and 'results' in response.data:
            data = {
                'results': response.data['results'],
                'count': response.data.get('count', len(response.data['results'])),
                'next': response.data.get('next'),
                'previous': response.data.get('previous')
            }
            return success_response(data=data)
        return success_response(data=response.data if isinstance(response.data, list) else [response.data])


class NearbyEventsView(generics.ListAPIView):
    """Find events near a specific location"""
    serializer_class = EventListSerializer
    permission_classes = [permissions.AllowAny]
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if isinstance(response.data, dict) and 'results' in response.data:
            data = {
                'results': response.data['results'],
                'count': response.data.get('count', len(response.data['results'])),
                'next': response.data.get('next'),
                'previous': response.data.get('previous')
            }
            return success_response(data=data)
        return success_response(data=response.data if isinstance(response.data, list) else [response.data])
    
    def get_queryset(self):
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        radius = self.request.query_params.get('radius', 10)  # Default 10km
        
        if not lat or not lng:
            return Event.objects.none()
        
        try:
            lat = float(lat)
            lng = float(lng)
            radius = float(radius)
            
            # Simple distance calculation (approximate)
            # In production, you might want to use PostGIS or similar
            return Event.objects.filter(
                is_active=True,
                latitude__range=(lat - radius/111, lat + radius/111),
                longitude__range=(lng - radius/111, lng + radius/111)
            )
        except ValueError:
            return Event.objects.none()


class OpenEventsView(generics.ListAPIView):
    """List currently open events"""
    serializer_class = EventListSerializer
    permission_classes = [permissions.AllowAny]
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if isinstance(response.data, dict) and 'results' in response.data:
            data = {
                'results': response.data['results'],
                'count': response.data.get('count', len(response.data['results'])),
                'next': response.data.get('next'),
                'previous': response.data.get('previous')
            }
            return success_response(data=data)
        return success_response(data=response.data if isinstance(response.data, list) else [response.data])
    
    def get_queryset(self):
        now = timezone.now()
        current_time = now.time()
        current_date = now.date()
        
        return Event.objects.filter(
            is_active=True,
            is_open=True,
            start_date__lte=current_date,
            end_date__gte=current_date
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_event_status(request, pk):
    """Toggle event open/closed status"""
    try:
        event = Event.objects.get(Q(pk=pk) & (Q(created_by=request.user) | Q(admins=request.user)))
        event.is_open = not event.is_open
        event.save()
        return success_response(
            data={'is_open': event.is_open},
            message=f'Event {"opened" if event.is_open else "closed"} successfully'
        )
    except Event.DoesNotExist:
        return error_response(
            'Event not found or you do not have permission to modify it',
            status_code=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_event_active(request, pk):
    """Toggle event active/inactive status"""
    try:
        event = Event.objects.get(Q(pk=pk) & (Q(created_by=request.user) | Q(admins=request.user)))
        event.is_active = not event.is_active
        event.save()
        return success_response(
            data={'is_active': event.is_active},
            message=f'Event {"activated" if event.is_active else "deactivated"} successfully'
        )
    except Event.DoesNotExist:
        return error_response(
            'Event not found or you do not have permission to modify it',
            status_code=status.HTTP_404_NOT_FOUND
        )
