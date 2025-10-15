import time
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


@dataclass
class ScrapingResult:
    """Result of a web scraping operation"""
    url: str
    title: Optional[str] = None
    content: Optional[str] = None
    raw_html: Optional[str] = None
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class WebScraper:
    """Main web scraper class that handles different scraping methods"""
    
    def __init__(self, 
                 user_agent: str = None,
                 delay: int = 1,
                 timeout: int = 30,
                 max_retries: int = 3,
                 respect_robots: bool = True):
        """
        Initialize the web scraper
        
        Args:
            user_agent: User agent string to use
            delay: Delay between requests in seconds
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            respect_robots: Whether to respect robots.txt
        """
        self.user_agent = user_agent or "happenin Scraper Bot (+https://happenin.com/bot)"
        self.delay = delay
        self.timeout = timeout
        self.max_retries = max_retries
        self.respect_robots = respect_robots
        
        # Create session with retry strategy
        self.session = self._create_session()
        
        # Track request history for rate limiting
        self.request_history = []
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        
        # Create adapter with retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        return session
    
    def scrape(self, url: str, **kwargs) -> ScrapingResult:
        """
        Scrape a website and return the results
        
        Args:
            url: URL to scrape
            **kwargs: Additional options for scraping
        
        Returns:
            ScrapingResult object with scraped data
        """
        try:
            # Respect delay between requests
            if self.delay > 0 and self.request_history:
                time.sleep(self.delay)
            
            # Record request start time
            start_time = time.time()
            
            # Make the request
            response = self._make_request(url, **kwargs)
            
            # Record request completion
            request_time = time.time() - start_time
            self._record_request(url, request_time, response.status_code)
            
            # Parse the response
            result = self._parse_response(url, response)
            
            return result
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return ScrapingResult(
                url=url,
                error=str(e)
            )
    
    def _make_request(self, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling"""
        try:
            # Merge default options with provided options
            request_kwargs = {
                'timeout': self.timeout,
                'allow_redirects': True,
                'verify': True,  # SSL verification
            }
            request_kwargs.update(kwargs)
            
            # Make the request
            response = self.session.get(url, **request_kwargs)
            response.raise_for_status()
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            raise
    
    def _parse_response(self, url: str, response: requests.Response) -> ScrapingResult:
        """Parse HTTP response and extract data"""
        try:
            # Get content type
            content_type = response.headers.get('content-type', '').split(';')[0]
            
            # Parse HTML content
            if 'text/html' in content_type:
                return self._parse_html_response(url, response)
            elif 'application/json' in content_type:
                return self._parse_json_response(url, response)
            elif 'text/plain' in content_type:
                return self._parse_text_response(url, response)
            else:
                # Unknown content type, treat as text
                return self._parse_text_response(url, response)
                
        except Exception as e:
            logger.error(f"Error parsing response from {url}: {e}")
            # Return basic result with error
            return ScrapingResult(
                url=url,
                status_code=response.status_code,
                content_type=response.headers.get('content-type'),
                headers=dict(response.headers),
                error=f"Parse error: {str(e)}"
            )
    
    def _parse_html_response(self, url: str, response: requests.Response) -> ScrapingResult:
        """Parse HTML response and extract structured data"""
        try:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = None
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)
            
            # Extract main content (try to find the most relevant content)
            content = self._extract_main_content(soup)
            
            # Clean up HTML for storage
            raw_html = self._clean_html(response.text)
            
            return ScrapingResult(
                url=url,
                title=title,
                content=content,
                raw_html=raw_html,
                status_code=response.status_code,
                content_type=response.headers.get('content-type'),
                headers=dict(response.headers)
            )
            
        except Exception as e:
            logger.error(f"Error parsing HTML from {url}: {e}")
            raise
    
    def _parse_json_response(self, url: str, response: requests.Response) -> ScrapingResult:
        """Parse JSON response"""
        try:
            data = response.json()
            
            # For JSON responses, we might want to extract specific fields
            title = None
            content = None
            
            # Try to find common fields that might contain title/content
            if isinstance(data, dict):
                title = data.get('title') or data.get('name') or data.get('headline')
                content = data.get('content') or data.get('body') or data.get('description')
            
            return ScrapingResult(
                url=url,
                title=title,
                content=content,
                raw_html=response.text,  # Store JSON as "raw_html" for consistency
                status_code=response.status_code,
                content_type=response.headers.get('content-type'),
                headers=dict(response.headers),
                metadata={'is_json': True, 'data_keys': list(data.keys()) if isinstance(data, dict) else None}
            )
            
        except Exception as e:
            logger.error(f"Error parsing JSON from {url}: {e}")
            raise
    
    def _parse_text_response(self, url: str, response: requests.Response) -> ScrapingResult:
        """Parse plain text response"""
        text = response.text
        
        # Try to extract title from first line
        lines = text.split('\n')
        title = lines[0].strip() if lines else None
        
        # Use first few lines as content
        content = '\n'.join(lines[:5]).strip() if len(lines) > 1 else None
        
        return ScrapingResult(
            url=url,
            title=title,
            content=content,
            raw_html=text,  # Store text as "raw_html" for consistency
            status_code=response.status_code,
            content_type=response.headers.get('content-type'),
            headers=dict(response.headers)
        )
    
    def _extract_main_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract main content from HTML, trying to avoid navigation and ads"""
        # Common selectors for main content
        content_selectors = [
            'main',
            'article',
            '[role="main"]',
            '.content',
            '.main-content',
            '.post-content',
            '.entry-content',
            '#content',
            '#main',
            '.container .row .col',  # Bootstrap-style
        ]
        
        # Try to find main content using selectors
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remove unwanted elements
                self._remove_unwanted_elements(content_elem)
                text = content_elem.get_text(separator='\n', strip=True)
                if len(text) > 100:  # Ensure we have substantial content
                    return text
        
        # Fallback: try to find the largest text block
        text_blocks = []
        for elem in soup.find_all(['p', 'div', 'section']):
            text = elem.get_text(strip=True)
            if len(text) > 50:  # Minimum text length
                text_blocks.append((len(text), text))
        
        if text_blocks:
            # Return the largest text block
            text_blocks.sort(key=lambda x: x[0], reverse=True)
            return text_blocks[0][1]
        
        return None
    
    def _remove_unwanted_elements(self, element):
        """Remove unwanted elements from content (ads, navigation, etc.)"""
        unwanted_selectors = [
            'nav', 'header', 'footer', 'aside',
            '.advertisement', '.ad', '.ads',
            '.navigation', '.nav', '.menu',
            '.sidebar', '.widget',
            '.social', '.share',
            '.comments', '.comment',
            'script', 'style', 'noscript'
        ]
        
        for selector in unwanted_selectors:
            for unwanted in element.select(selector):
                unwanted.decompose()
    
    def _clean_html(self, html: str) -> str:
        """Clean HTML for storage"""
        # Remove script and style tags
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Remove comments
        from bs4 import Comment
        comments = soup.findAll(text=lambda text: isinstance(text, Comment))
        for comment in comments:
            comment.extract()
        
        # Limit size if too long
        cleaned_html = str(soup)
        if len(cleaned_html) > 50000:  # 50KB limit
            cleaned_html = cleaned_html[:50000] + "... [truncated]"
        
        return cleaned_html
    
    def _record_request(self, url: str, duration: float, status_code: int):
        """Record request for rate limiting and monitoring"""
        self.request_history.append({
            'url': url,
            'timestamp': time.time(),
            'duration': duration,
            'status_code': status_code
        })
        
        # Keep only last 100 requests
        if len(self.request_history) > 100:
            self.request_history = self.request_history[-100:]
    
    def get_request_stats(self) -> Dict[str, Any]:
        """Get statistics about recent requests"""
        if not self.request_history:
            return {}
        
        recent_requests = [r for r in self.request_history 
                          if time.time() - r['timestamp'] < 3600]  # Last hour
        
        if not recent_requests:
            return {}
        
        return {
            'total_requests': len(recent_requests),
            'avg_duration': sum(r['duration'] for r in recent_requests) / len(recent_requests),
            'success_rate': sum(1 for r in recent_requests if r['status_code'] < 400) / len(recent_requests),
            'last_request': max(r['timestamp'] for r in recent_requests)
        }
    
    def close(self):
        """Close the session and cleanup"""
        if self.session:
            self.session.close()


class AdvancedWebScraper(WebScraper):
    """Advanced web scraper with additional features"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.proxy_pool = []
        self.cookies = {}
        self.custom_headers = {}
    
    def add_proxy(self, proxy: str):
        """Add a proxy to the proxy pool"""
        self.proxy_pool.append(proxy)
    
    def set_cookies(self, cookies: Dict[str, str]):
        """Set cookies for requests"""
        self.cookies.update(cookies)
        self.session.cookies.update(cookies)
    
    def add_headers(self, headers: Dict[str, str]):
        """Add custom headers"""
        self.custom_headers.update(headers)
        self.session.headers.update(headers)
    
    def scrape_with_js_rendering(self, url: str, wait_time: int = 5) -> ScrapingResult:
        """
        Scrape with JavaScript rendering (requires selenium)
        This is a placeholder for selenium-based scraping
        """
        # This would require selenium to be installed
        # For now, fall back to regular scraping
        logger.warning("JavaScript rendering not available, falling back to regular scraping")
        return self.scrape(url)
    
    def scrape_multiple_pages(self, urls: List[str], **kwargs) -> List[ScrapingResult]:
        """Scrape multiple pages with rate limiting"""
        results = []
        
        for i, url in enumerate(urls):
            try:
                result = self.scrape(url, **kwargs)
                results.append(result)
                
                # Add delay between requests (except for the last one)
                if i < len(urls) - 1 and self.delay > 0:
                    time.sleep(self.delay)
                    
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                results.append(ScrapingResult(url=url, error=str(e)))
        
        return results


class APIScraper(WebScraper):
    """Specialized scraper for API endpoints"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.auth_headers = kwargs.get('auth_headers', {})
        
        if self.api_key:
            self.session.headers.update({'Authorization': f'Bearer {self.api_key}'})
        
        if self.auth_headers:
            self.session.headers.update(self.auth_headers)
    
    def scrape_api(self, url: str, params: Dict[str, Any] = None, 
                   method: str = 'GET', data: Dict[str, Any] = None) -> ScrapingResult:
        """Scrape an API endpoint"""
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            # Parse as JSON
            return self._parse_json_response(url, response)
            
        except Exception as e:
            logger.error(f"Error scraping API {url}: {e}")
            return ScrapingResult(url=url, error=str(e))
    
    def paginate_api(self, base_url: str, page_param: str = 'page', 
                    max_pages: int = 10, **kwargs) -> List[ScrapingResult]:
        """Scrape paginated API endpoints"""
        results = []
        page = 1
        
        while page <= max_pages:
            try:
                params = kwargs.get('params', {})
                params[page_param] = page
                
                result = self.scrape_api(base_url, params=params, **kwargs)
                results.append(result)
                
                # Check if we should continue paginating
                if result.error or not result.metadata or not result.metadata.get('data_keys'):
                    break
                
                page += 1
                
                # Respect rate limiting
                if self.delay > 0:
                    time.sleep(self.delay)
                    
            except Exception as e:
                logger.error(f"Error on page {page}: {e}")
                break
        
        return results
