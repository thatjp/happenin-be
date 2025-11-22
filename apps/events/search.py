"""
Elasticsearch search functionality for events
"""
from elasticsearch_dsl import Search, Q
from django.conf import settings
from .documents import EventDocument, get_elasticsearch_connection


def search_events(query=None, filters=None, sort=None, page=1, page_size=20):
    """
    Search events using Elasticsearch
    
    Args:
        query: Search query string
        filters: Dict of filters (e.g., {'city': 'New York', 'is_free': True})
        sort: Sort field and direction (e.g., ['start_date:asc', '-created_at'])
        page: Page number (1-indexed)
        page_size: Number of results per page
    
    Returns:
        Dict with results, total count, and pagination info
    """
    # Ensure connection is initialized
    get_elasticsearch_connection()
    
    # Build search query
    search = Search(index=settings.ELASTICSEARCH_INDEX_NAME)
    
    # Build the main text query
    text_query = None
    if query:
        # Multi-match query across multiple fields
        # Removed fuzziness to prevent fuzzy matching - only exact word matches
        # Fields with ^ are boosted (title^3 means title matches are worth 3x more)
        # Using 'phrase' type for better precision - requires words to be closer together
        text_query = Q(
            'multi_match',
            query=query,
            fields=['title^3', 'description^2', 'event_type^2', 'city', 'full_address'],
            type='best_fields',
            # No fuzziness parameter - this prevents fuzzy matching
            # This will match words exactly (after tokenization/analysis)
        )
    
    # Build filter queries
    filter_queries = []
    
    if filters:
        # City filter
        if 'city' in filters and filters['city']:
            filter_queries.append(Q('term', city=filters['city']))
        
        # State filter
        if 'state' in filters and filters['state']:
            filter_queries.append(Q('term', state=filters['state']))
        
        # Country filter
        if 'country' in filters and filters['country']:
            filter_queries.append(Q('term', country=filters['country']))
        
        # Event type filter
        if 'event_type' in filters and filters['event_type']:
            filter_queries.append(Q('term', event_type=filters['event_type']))
        
        # Boolean filters
        if 'is_free' in filters and filters['is_free'] is not None:
            filter_queries.append(Q('term', is_free=filters['is_free']))
        
        if 'is_open' in filters and filters['is_open'] is not None:
            filter_queries.append(Q('term', is_open=filters['is_open']))
        
        if 'is_active' in filters and filters['is_active'] is not None:
            filter_queries.append(Q('term', is_active=filters['is_active']))
        
        # Date range filters
        if 'start_date_from' in filters and filters['start_date_from']:
            filter_queries.append(Q('range', start_date={'gte': filters['start_date_from']}))
        
        if 'start_date_to' in filters and filters['start_date_to']:
            filter_queries.append(Q('range', start_date={'lte': filters['start_date_to']}))
        
        # Location filters (simple bounding box)
        if 'lat' in filters and 'lng' in filters and 'radius' in filters:
            lat = float(filters['lat'])
            lng = float(filters['lng'])
            radius = float(filters['radius'])
            
            # Approximate bounding box (rough calculation)
            lat_range = radius / 111  # ~111 km per degree latitude
            lng_range = radius / (111 * abs(lat) * 0.017453)  # Adjust for longitude
            
            filter_queries.append(Q('range', latitude={
                'gte': lat - lat_range,
                'lte': lat + lat_range
            }))
            filter_queries.append(Q('range', longitude={
                'gte': lng - lng_range,
                'lte': lng + lng_range
            }))
        
        # Price range filters
        if 'min_price' in filters and filters['min_price'] is not None:
            filter_queries.append(Q('range', price={'gte': float(filters['min_price'])}))
        
        if 'max_price' in filters and filters['max_price'] is not None:
            filter_queries.append(Q('range', price={'lte': float(filters['max_price'])}))
    
    # Combine text query with filters using bool query
    must_clauses = []
    
    # Add text query if it exists
    if text_query:
        must_clauses.append(text_query)
    
    # Add all filters
    must_clauses.extend(filter_queries)
    
    # Only return active events by default (add as filter, not in must)
    if not filters or 'is_active' not in filters:
        must_clauses.append(Q('term', is_active=True))
    
    # Build the final query
    if must_clauses:
        if len(must_clauses) == 1:
            # Single clause, use it directly
            search = search.query(must_clauses[0])
        else:
            # Multiple clauses, combine with bool
            search = search.query('bool', must=must_clauses)
    else:
        # No query or filters, match all
        search = search.query('match_all')
    
    # Apply sorting
    if sort:
        if isinstance(sort, str):
            sort_fields = [sort]
        else:
            sort_fields = sort
        
        sort_list = []
        for field in sort_fields:
            if field.startswith('-'):
                sort_list.append({field[1:]: {'order': 'desc'}})
            elif ':' in field:
                field_name, direction = field.split(':')
                sort_list.append({field_name: {'order': direction}})
            else:
                sort_list.append({field: {'order': 'asc'}})
        
        search = search.sort(*sort_list)
    else:
        # Default sorting
        search = search.sort('-start_date', '-created_at')
    
    # Apply pagination
    from_index = (page - 1) * page_size
    search = search[from_index:from_index + page_size]
    
    # Execute search
    try:
        response = search.execute()
        
        # Format results
        results = []
        for hit in response:
            event_data = {
                'id': hit.meta.id,
                'title': hit.title,
                'description': hit.description,
                'event_type': hit.event_type,
                'icon': hit.icon,
                'price': hit.price,
                'is_free': hit.is_free,
                'address': hit.address,
                'city': hit.city,
                'state': hit.state,
                'country': hit.country,
                'postal_code': hit.postal_code,
                'full_address': hit.full_address,
                'open_time': hit.open_time,
                'close_time': hit.close_time,
                'start_date': hit.start_date,
                'end_date': hit.end_date,
                'latitude': hit.latitude,
                'longitude': hit.longitude,
                'is_open': hit.is_open,
                'is_active': hit.is_active,
                'is_currently_open': hit.is_currently_open,
                'created_at': hit.created_at,
                'updated_at': hit.updated_at,
                'created_by_id': hit.created_by_id,
                'created_by_username': hit.created_by_username,
                'score': hit.meta.score,  # Relevance score
            }
            results.append(event_data)
        
        # Calculate pagination info
        total = response.hits.total.value if hasattr(response.hits.total, 'value') else response.hits.total
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        
        return {
            'results': results,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_previous': page > 1,
        }
    
    except Exception as e:
        # If Elasticsearch is not available, return empty results
        # In production, you might want to log this and fall back to database search
        return {
            'results': [],
            'total': 0,
            'page': page,
            'page_size': page_size,
            'total_pages': 0,
            'has_next': False,
            'has_previous': False,
            'error': str(e)
        }

