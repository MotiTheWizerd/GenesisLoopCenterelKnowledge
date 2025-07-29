"""
Data models for web search and scraping operations
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class WebSearchRequest:
    """Request model for web search operations"""
    query: str
    max_results: int = 10
    safe_search: bool = True
    language: str = "en"
    region: str = "us"


@dataclass
class WebScrapeRequest:
    """Request model for web scraping operations"""
    url: str
    extract_text: bool = True
    extract_links: bool = False
    extract_images: bool = False
    max_content_length: int = 50000
    timeout: int = 30
    follow_redirects: bool = True


@dataclass
class SearchResult:
    """Individual search result"""
    title: str
    url: str
    snippet: str
    domain: str
    rank: int


@dataclass
class ScrapedContent:
    """Scraped content from a web page"""
    url: str
    title: str
    text_content: str
    links: List[Dict[str, str]]
    images: List[Dict[str, str]]
    metadata: Dict[str, Any]
    content_length: int
    scraped_at: datetime


@dataclass
class WebSearchResponse:
    """Response model for web search operations"""
    success: bool
    query: str
    results: List[SearchResult]
    total_results: int
    search_time: float
    timestamp: datetime
    error_message: Optional[str] = None


@dataclass
class WebScrapeResponse:
    """Response model for web scraping operations"""
    success: bool
    content: Optional[ScrapedContent]
    processing_time: float
    timestamp: datetime
    error_message: Optional[str] = None


@dataclass
class WebTaskRequest:
    """Main task request wrapper"""
    task: Dict[str, Any]
    assigned_by: str
    
    def get_task_type(self) -> str:
        """Get the type of web task"""
        return self.task.get('type', '')
    
    def to_search_request(self) -> WebSearchRequest:
        """Convert to WebSearchRequest"""
        task = self.task
        return WebSearchRequest(
            query=task['query'],
            max_results=task.get('max_results', 10),
            safe_search=task.get('safe_search', True),
            language=task.get('language', 'en'),
            region=task.get('region', 'us')
        )
    
    def to_scrape_request(self) -> WebScrapeRequest:
        """Convert to WebScrapeRequest"""
        task = self.task
        return WebScrapeRequest(
            url=task['url'],
            extract_text=task.get('extract_text', True),
            extract_links=task.get('extract_links', False),
            extract_images=task.get('extract_images', False),
            max_content_length=task.get('max_content_length', 50000),
            timeout=task.get('timeout', 30),
            follow_redirects=task.get('follow_redirects', True)
        )