import time
import logging
import requests
from urllib.parse import urljoin, urlparse
from typing import Dict, Any, Optional, List
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


def is_robots_txt_allowed(url: str, user_agent: str = None) -> bool:
    """
    Check if scraping is allowed by robots.txt
    
    Args:
        url: URL to check
        user_agent: User agent string (defaults to happenin bot)
    
    Returns:
        True if scraping is allowed, False otherwise
    """
    if not user_agent:
        user_agent = "happenin Scraper Bot"
    
    try:
        # Parse URL to get robots.txt location
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        
        # Check cache first
        cache_key = f"robots_txt:{parsed_url.netloc}"
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Fetch robots.txt
        response = requests.get(robots_url, timeout=10)
        if response.status_code != 200:
            # If robots.txt doesn't exist or is inaccessible, assume allowed
            cache.set(cache_key, True, 3600)  # Cache for 1 hour
            return True
        
        robots_content = response.text
        
        # Parse robots.txt content
        allowed = parse_robots_txt(robots_content, user_agent, url)
        
        # Cache result for 1 hour
        cache.set(cache_key, allowed, 3600)
        
        return allowed
        
    except Exception as e:
        logger.warning(f"Error checking robots.txt for {url}: {e}")
        # On error, assume allowed (fail open)
        return True


def parse_robots_txt(content: str, user_agent: str, url: str) -> bool:
    """
    Parse robots.txt content to determine if scraping is allowed
    
    Args:
        content: Content of robots.txt file
        user_agent: User agent string
        url: URL to check
    
    Returns:
        True if scraping is allowed, False otherwise
    """
    try:
        lines = content.split('\n')
        current_user_agent = None
        disallow_rules = []
        allow_rules = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if ':' in line:
                directive, value = line.split(':', 1)
                directive = directive.strip().lower()
                value = value.strip()
                
                if directive == 'user-agent':
                    current_user_agent = value
                elif directive == 'disallow' and current_user_agent in ['*', user_agent]:
                    disallow_rules.append(value)
                elif directive == 'allow' and current_user_agent in ['*', user_agent]:
                    allow_rules.append(value)
        
        # Check if URL matches any disallow rules
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        for rule in disallow_rules:
            if rule == '/':
                # Disallow all
                return False
            elif path.startswith(rule):
                # Check if there's a more specific allow rule
                if not any(path.startswith(allow_rule) for allow_rule in allow_rules):
                    return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error parsing robots.txt: {e}")
        return True  # Fail open


def get_rate_limit_key(target_id: int, user_id: int = None) -> str:
    """
    Generate a rate limit key for a scraping target
    
    Args:
        target_id: ID of the scraping target
        user_id: ID of the user (optional)
    
    Returns:
        Rate limit cache key
    """
    if user_id:
        return f"rate_limit:target:{target_id}:user:{user_id}"
    else:
        return f"rate_limit:target:{target_id}"


def check_rate_limit(target, user_id: int = None) -> bool:
    """
    Check if rate limit allows scraping for a target
    
    Args:
        target: ScrapingTarget instance
        user_id: ID of the user (optional)
    
    Returns:
        True if rate limit allows, False otherwise
    """
    try:
        rate_limit_key = get_rate_limit_key(target.id, user_id)
        
        # Get current request count for this hour
        current_hour = int(time.time() // 3600)
        hour_key = f"{rate_limit_key}:{current_hour}"
        
        current_count = cache.get(hour_key, 0)
        
        # Check if we're under the limit
        if current_count < target.max_requests_per_hour:
            return True
        else:
            logger.warning(f"Rate limit exceeded for target {target.name}: "
                         f"{current_count}/{target.max_requests_per_hour} requests per hour")
            return False
            
    except Exception as e:
        logger.error(f"Error checking rate limit: {e}")
        return True  # Fail open


def update_rate_limit(target, user_id: int = None):
    """
    Update rate limit counter for a target
    
    Args:
        target: ScrapingTarget instance
        user_id: ID of the user (optional)
    """
    try:
        rate_limit_key = get_rate_limit_key(target.id, user_id)
        
        # Get current hour
        current_hour = int(time.time() // 3600)
        hour_key = f"{rate_limit_key}:{current_hour}"
        
        # Increment counter
        current_count = cache.get(hour_key, 0)
        cache.set(hour_key, current_count + 1, 3600)  # Expire in 1 hour
        
    except Exception as e:
        logger.error(f"Error updating rate limit: {e}")


def clean_text_data(text: str) -> str:
    """
    Clean and normalize text data
    
    Args:
        text: Raw text to clean
    
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove common HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    
    return text.strip()


def extract_links_from_html(html: str, base_url: str) -> List[str]:
    """
    Extract all links from HTML content
    
    Args:
        html: HTML content
        base_url: Base URL for resolving relative links
    
    Returns:
        List of absolute URLs
    """
    try:
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Skip javascript, mailto, tel, etc.
            if href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                continue
            
            # Resolve relative URLs
            absolute_url = urljoin(base_url, href)
            
            # Only include HTTP/HTTPS URLs
            if absolute_url.startswith(('http://', 'https://')):
                links.append(absolute_url)
        
        return list(set(links))  # Remove duplicates
        
    except Exception as e:
        logger.error(f"Error extracting links: {e}")
        return []


def validate_url(url: str) -> bool:
    """
    Validate if a URL is properly formatted
    
    Args:
        url: URL to validate
    
    Returns:
        True if valid, False otherwise
    """
    try:
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc])
    except Exception:
        return False


def normalize_url(url: str) -> str:
    """
    Normalize a URL (remove fragments, normalize scheme, etc.)
    
    Args:
        url: URL to normalize
    
    Returns:
        Normalized URL
    """
    try:
        parsed = urlparse(url)
        
        # Normalize scheme
        if not parsed.scheme:
            parsed = parsed._replace(scheme='https')
        
        # Remove fragments
        parsed = parsed._replace(fragment='')
        
        # Ensure www prefix for common domains
        if parsed.netloc and not parsed.netloc.startswith('www.'):
            # Add www for common domains that typically use it
            common_domains = ['google.com', 'facebook.com', 'twitter.com', 'linkedin.com']
            if any(domain in parsed.netloc for domain in common_domains):
                parsed = parsed._replace(netloc=f'www.{parsed.netloc}')
        
        return parsed.geturl()
        
    except Exception as e:
        logger.error(f"Error normalizing URL {url}: {e}")
        return url


def extract_metadata_from_html(html: str) -> Dict[str, Any]:
    """
    Extract metadata from HTML content
    
    Args:
        html: HTML content
    
    Returns:
        Dictionary of metadata
    """
    try:
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        metadata = {}
        
        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            
            if name and content:
                metadata[name] = content
        
        # Extract Open Graph tags
        og_tags = {}
        for meta in soup.find_all('meta', property=lambda x: x and x.startswith('og:')):
            property_name = meta.get('property', '').replace('og:', '')
            content = meta.get('content')
            if property_name and content:
                og_tags[property_name] = content
        
        if og_tags:
            metadata['open_graph'] = og_tags
        
        # Extract Twitter Card tags
        twitter_tags = {}
        for meta in soup.find_all('meta', name=lambda x: x and x.startswith('twitter:')):
            name = meta.get('name', '').replace('twitter:', '')
            content = meta.get('content')
            if name and content:
                twitter_tags[name] = content
        
        if twitter_tags:
            metadata['twitter_card'] = twitter_tags
        
        # Extract structured data (JSON-LD)
        json_ld_data = []
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                json_ld_data.append(data)
            except (json.JSONDecodeError, AttributeError):
                continue
        
        if json_ld_data:
            metadata['structured_data'] = json_ld_data
        
        return metadata
        
    except Exception as e:
        logger.error(f"Error extracting metadata: {e}")
        return {}


def calculate_content_hash(content: str) -> str:
    """
    Calculate a hash of content for deduplication
    
    Args:
        content: Content to hash
    
    Returns:
        SHA-256 hash of the content
    """
    import hashlib
    
    if not content:
        return ""
    
    # Normalize content (remove whitespace differences)
    normalized = ' '.join(content.split())
    
    # Calculate hash
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def is_content_duplicate(content: str, target_id: int) -> bool:
    """
    Check if content is a duplicate for a specific target
    
    Args:
        content: Content to check
        target_id: ID of the scraping target
    
    Returns:
        True if duplicate, False otherwise
    """
    try:
        content_hash = calculate_content_hash(content)
        cache_key = f"content_hash:target:{target_id}:{content_hash}"
        
        # Check if we've seen this content before
        if cache.get(cache_key):
            return True
        
        # Store hash for future checks (expire in 24 hours)
        cache.set(cache_key, True, 86400)
        return False
        
    except Exception as e:
        logger.error(f"Error checking content duplicate: {e}")
        return False


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def get_domain_from_url(url: str) -> str:
    """
    Extract domain from URL
    
    Args:
        url: URL to extract domain from
    
    Returns:
        Domain string
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return ""


def is_same_domain(url1: str, url2: str) -> bool:
    """
    Check if two URLs are from the same domain
    
    Args:
        url1: First URL
        url2: Second URL
    
    Returns:
        True if same domain, False otherwise
    """
    domain1 = get_domain_from_url(url1)
    domain2 = get_domain_from_url(url2)
    
    return domain1 == domain2 and domain1 != ""


def create_scraping_summary(target, jobs: List, data: List) -> Dict[str, Any]:
    """
    Create a summary of scraping activities
    
    Args:
        target: ScrapingTarget instance
        jobs: List of ScrapingJob instances
        data: List of ScrapedData instances
    
    Returns:
        Summary dictionary
    """
    try:
        total_jobs = len(jobs)
        successful_jobs = len([j for j in jobs if j.success])
        failed_jobs = total_jobs - successful_jobs
        
        total_data = len(data)
        processed_data = len([d for d in data if d.status == 'processed'])
        
        # Calculate average response time
        response_times = [j.response_time_ms for j in jobs if j.response_time_ms]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Calculate total data size
        total_size = sum(d.raw_html.__sizeof__() for d in data if d.raw_html)
        
        return {
            'target_name': target.name,
            'target_url': target.url,
            'period': {
                'start': min(j.created_at for j in jobs) if jobs else None,
                'end': max(j.created_at for j in jobs) if jobs else None,
            },
            'jobs': {
                'total': total_jobs,
                'successful': successful_jobs,
                'failed': failed_jobs,
                'success_rate': (successful_jobs / total_jobs * 100) if total_jobs > 0 else 0,
            },
            'data': {
                'total_records': total_data,
                'processed': processed_data,
                'pending': total_data - processed_data,
            },
            'performance': {
                'avg_response_time_ms': round(avg_response_time, 2),
                'total_data_size': format_file_size(total_size),
            },
            'last_updated': timezone.now().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Error creating scraping summary: {e}")
        return {
            'error': str(e),
            'target_name': target.name if target else 'Unknown',
        }
