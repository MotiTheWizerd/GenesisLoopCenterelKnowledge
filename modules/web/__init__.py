"""
Web module for Ray - Web search and scraping capabilities
"""

from .models import WebSearchRequest, WebScrapeRequest, WebSearchResponse, WebScrapeResponse
from .handler import WebHandler, web_manager
from .search import WebSearcher
from .scraper import WebScraper

__all__ = [
    'WebSearchRequest',
    'WebScrapeRequest', 
    'WebSearchResponse',
    'WebScrapeResponse',
    'WebHandler',
    'web_manager',
    'WebSearcher',
    'WebScraper'
]