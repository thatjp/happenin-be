from elasticsearch_dsl import Document, Text, Keyword, Date, Boolean, Double, Integer, connections
from django.conf import settings
from .models import Event


# Configure Elasticsearch connection (will be initialized when needed)
def get_elasticsearch_connection():
    """Get or create Elasticsearch connection"""
    es_config = settings.ELASTICSEARCH_DSL['default']
    
    # Normalize hosts - ensure they have proper scheme
    hosts = es_config['hosts']
    normalized_hosts = []
    use_ssl = es_config.get('use_ssl', False)
    
    for host in hosts:
        host = host.strip()
        # If host doesn't have a scheme, add one based on SSL config
        if not host.startswith(('http://', 'https://')):
            scheme = 'https' if use_ssl else 'http'
            host = f'{scheme}://{host}'
        normalized_hosts.append(host)
    
    # Check if connection already exists
    try:
        conn = connections.get_connection()
        # Test if connection is alive by checking if we can access the cluster
        if conn is not None:
            try:
                # Try a simple operation to verify connection
                conn.cluster.health(request_timeout=2)
                return conn
            except Exception:
                # Connection is dead, remove it and create new one
                connections.remove_connection()
    except Exception:
        # Connection doesn't exist, create new one
        pass
    
    # Create new connection
    # SSL is automatically determined by the URL scheme (https:// vs http://)
    # elasticsearch-dsl passes these params to Elasticsearch client
    # Valid params: hosts, http_auth, timeout, verify_certs, ca_certs, etc.
    
    # Build connection params - only include valid parameters
    connection_params = {
        'hosts': normalized_hosts,
    }
    
    # Optional authentication
    if es_config.get('http_auth'):
        connection_params['http_auth'] = es_config['http_auth']
    
    # Timeout
    connection_params['timeout'] = es_config.get('timeout', 30)
    
    # SSL verification settings (only for HTTPS URLs)
    # verify_certs is a valid parameter for the Elasticsearch client
    if any(host.startswith('https://') for host in normalized_hosts):
        connection_params['verify_certs'] = es_config.get('verify_certs', False)
        if es_config.get('ca_certs'):
            connection_params['ca_certs'] = es_config['ca_certs']
    
    return connections.create_connection(**connection_params)


class EventDocument(Document):
    """Elasticsearch document for Event model"""
    
    # Basic event information
    title = Text(
        fields={'keyword': Keyword()},
        analyzer='standard'
    )
    description = Text(analyzer='standard')
    
    # Event categorization
    event_type = Keyword()
    icon = Keyword()
    
    # Pricing information
    price = Double()
    is_free = Boolean()
    
    # Address information
    address = Text(analyzer='standard')
    city = Keyword()
    state = Keyword()
    country = Keyword()
    postal_code = Keyword()
    full_address = Text(analyzer='standard')
    
    # Time information
    open_time = Keyword()
    close_time = Keyword()
    start_date = Date()
    end_date = Date()
    
    # Location coordinates
    latitude = Double()
    longitude = Double()
    
    # Status flags
    is_open = Boolean()
    is_active = Boolean()
    is_currently_open = Boolean()
    
    # Metadata
    created_at = Date()
    updated_at = Date()
    created_by_id = Integer()
    created_by_username = Keyword()
    
    class Index:
        name = settings.ELASTICSEARCH_INDEX_NAME
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'analysis': {
                'analyzer': {
                    'standard': {
                        'type': 'standard',
                        'stopwords': '_english_'
                    }
                }
            }
        }
    
    class Django:
        model = Event
    
    def save(self, **kwargs):
        """Override save to ensure connection is initialized"""
        get_elasticsearch_connection()
        return super().save(**kwargs)
    
    def delete(self, **kwargs):
        """Override delete to ensure connection is initialized"""
        get_elasticsearch_connection()
        return super().delete(**kwargs)
    
    @classmethod
    def from_event(cls, event):
        """Create EventDocument from Event model instance"""
        get_elasticsearch_connection()
        doc = cls()
        doc.meta.id = event.id
        
        # Basic information
        doc.title = event.title
        doc.description = event.description or ''
        
        # Categorization
        doc.event_type = event.event_type
        doc.icon = event.icon or ''
        
        # Pricing
        doc.price = float(event.price) if event.price else None
        doc.is_free = event.is_free
        
        # Address
        doc.address = event.address
        doc.city = event.city
        doc.state = event.state or ''
        doc.country = event.country
        doc.postal_code = event.postal_code or ''
        doc.full_address = event.full_address
        
        # Time
        doc.open_time = str(event.open_time) if event.open_time else None
        doc.close_time = str(event.close_time) if event.close_time else None
        doc.start_date = event.start_date
        doc.end_date = event.end_date
        
        # Location
        doc.latitude = float(event.latitude) if event.latitude else None
        doc.longitude = float(event.longitude) if event.longitude else None
        
        # Status
        doc.is_open = event.is_open
        doc.is_active = event.is_active
        doc.is_currently_open = event.is_currently_open
        
        # Metadata
        doc.created_at = event.created_at
        doc.updated_at = event.updated_at
        doc.created_by_id = event.created_by.id if event.created_by else None
        doc.created_by_username = event.created_by.username if event.created_by else ''
        
        return doc

