"""
Main handler for web operations
"""

from typing import Dict, Any, Union
import logging

from .models import WebTaskRequest, WebSearchResponse, WebScrapeResponse
from .search import WebSearcher
from .scraper import WebScraper

logger = logging.getLogger(__name__)


class WebHandler:
    """Main handler for web search and scraping operations"""
    
    def __init__(self):
        self.searcher = WebSearcher()
        self.scraper = WebScraper()
    
    def handle_task(self, task_data: Dict[str, Any]) -> Union[WebSearchResponse, WebScrapeResponse]:
        """Handle a web task request"""
        try:
            # Parse the task request
            task_request = WebTaskRequest(**task_data)
            task_type = task_request.get_task_type()
            
            logger.info(f"Processing web task: {task_type}")
            
            if task_type == "search":
                return self._handle_search(task_request)
            elif task_type == "scrape":
                return self._handle_scrape(task_request)
            else:
                raise ValueError(f"Unknown web task type: {task_type}")
                
        except Exception as e:
            logger.error(f"Error handling web task: {str(e)}")
            # Return error response based on task type
            if 'search' in str(task_data).lower():
                return WebSearchResponse(
                    success=False,
                    query="",
                    results=[],
                    total_results=0,
                    search_time=0.0,
                    timestamp=None,
                    error_message=str(e)
                )
            else:
                return WebScrapeResponse(
                    success=False,
                    content=None,
                    processing_time=0.0,
                    timestamp=None,
                    error_message=str(e)
                )
    
    def _handle_search(self, task_request: WebTaskRequest) -> WebSearchResponse:
        """Handle web search request"""
        search_request = task_request.to_search_request()
        
        logger.info(f"Searching for: {search_request.query}")
        
        response = self.searcher.search(search_request)
        
        if response.success:
            logger.info(f"Search completed: {response.total_results} results found")
        else:
            logger.error(f"Search failed: {response.error_message}")
        
        return response
    
    def _handle_scrape(self, task_request: WebTaskRequest) -> WebScrapeResponse:
        """Handle web scraping request"""
        scrape_request = task_request.to_scrape_request()
        
        logger.info(f"Scraping URL: {scrape_request.url}")
        
        response = self.scraper.scrape(scrape_request)
        
        if response.success:
            content_length = response.content.content_length if response.content else 0
            logger.info(f"Scraping completed: {content_length} characters extracted")
        else:
            logger.error(f"Scraping failed: {response.error_message}")
        
        return response
    
    def search_and_scrape(self, query: str, max_results: int = 5, scrape_first: bool = True) -> Dict[str, Any]:
        """Combined search and scrape operation"""
        results = {
            "search_results": None,
            "scraped_content": [],
            "success": False,
            "error_message": None
        }
        
        try:
            # First, perform the search
            search_task = {
                "task": {
                    "type": "search",
                    "query": query,
                    "max_results": max_results
                },
                "assigned_by": "system"
            }
            
            search_response = self.handle_task(search_task)
            results["search_results"] = search_response
            
            if not search_response.success:
                results["error_message"] = f"Search failed: {search_response.error_message}"
                return results
            
            # Then scrape the first result (or all if requested)
            urls_to_scrape = []
            if scrape_first and search_response.results:
                urls_to_scrape = [search_response.results[0].url]
            elif not scrape_first:
                urls_to_scrape = [result.url for result in search_response.results[:3]]  # Scrape first 3
            
            scraped_responses = []
            for url in urls_to_scrape:
                scrape_task = {
                    "task": {
                        "type": "scrape",
                        "url": url,
                        "extract_text": True,
                        "extract_links": False,
                        "max_content_length": 10000
                    },
                    "assigned_by": "system"
                }
                
                scrape_response = self.handle_task(scrape_task)
                scraped_responses.append(scrape_response)
            
            results["scraped_content"] = scraped_responses
            results["success"] = True
            
        except Exception as e:
            results["error_message"] = str(e)
            logger.error(f"Combined search and scrape failed: {str(e)}")
        
        return results
    
    def search(self, query: str, max_results: int = 5) -> WebSearchResponse:
        """Simple search method for backward compatibility"""
        search_task = {
            "task": {
                "type": "search",
                "query": query,
                "max_results": max_results
            },
            "assigned_by": "system"
        }
        return self.handle_task(search_task)
    
    def scrape_url(self, url: str, extract_content: bool = True) -> WebScrapeResponse:
        """Simple scrape method for backward compatibility"""
        scrape_task = {
            "task": {
                "type": "scrape",
                "url": url,
                "extract_text": extract_content,
                "extract_links": False,
                "max_content_length": 10000
            },
            "assigned_by": "system"
        }
        return self.handle_task(scrape_task)


# Create global instance
web_manager = WebHandler()