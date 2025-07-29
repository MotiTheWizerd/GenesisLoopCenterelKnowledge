"""
Web routes for Ray's web search and scraping functionality
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from modules.web.handler import WebHandler
from utils.timestamp_utils import add_ray_timestamp_to_response, get_ray_time_context

logger = logging.getLogger(__name__)

# Create router
web_router = APIRouter(prefix="/web", tags=["web"])

# Initialize handler
web_handler = WebHandler()


class WebTaskRequest(BaseModel):
    task: Dict[str, Any]
    assigned_by: str


class SearchAndScrapeRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5
    scrape_first: Optional[bool] = True
    assigned_by: Optional[str] = "unknown"


@web_router.post("/search")
async def web_search(request: WebTaskRequest):
    """Handle web search requests"""
    try:
        data = request.dict()
        
        # Validate required fields
        task = data['task']
        if 'query' not in task:
            raise HTTPException(status_code=400, detail="Missing query in task")
        
        # Set task type
        task['type'] = 'search'
        
        # Process the search
        response = web_handler.handle_task(data)
        
        # Convert response to dict for JSON serialization
        result = {
            'success': response.success,
            'query': response.query,
            'results': [
                {
                    'title': r.title,
                    'url': r.url,
                    'snippet': r.snippet,
                    'domain': r.domain,
                    'rank': r.rank
                } for r in response.results
            ],
            'total_results': response.total_results,
            'search_time': response.search_time,
            'timestamp': response.timestamp.isoformat() if response.timestamp else None,
            'assigned_by': data.get('assigned_by', 'unknown')
        }
        
        if not response.success:
            result['error_message'] = response.error_message
        
        logger.info(f"Web search completed: {response.total_results} results for '{response.query}'")
        
        # Add comprehensive timestamp information for Ray
        result = add_ray_timestamp_to_response(result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in web search endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@web_router.post("/scrape")
async def web_scrape(request: WebTaskRequest):
    """Handle web scraping requests"""
    try:
        data = request.dict()
        
        # Validate required fields
        task = data['task']
        if 'url' not in task:
            raise HTTPException(status_code=400, detail="Missing url in task")
        
        # Set task type
        task['type'] = 'scrape'
        
        # Process the scraping
        response = web_handler.handle_task(data)
        
        # Convert response to dict for JSON serialization
        result = {
            'success': response.success,
            'processing_time': response.processing_time,
            'timestamp': response.timestamp.isoformat() if response.timestamp else None,
            'assigned_by': data.get('assigned_by', 'unknown')
        }
        
        if response.success and response.content:
            content = response.content
            result['content'] = {
                'url': content.url,
                'title': content.title,
                'text_content': content.text_content,
                'links': content.links,
                'images': content.images,
                'metadata': content.metadata,
                'content_length': content.content_length,
                'scraped_at': content.scraped_at.isoformat()
            }
        else:
            result['error_message'] = response.error_message
        
        logger.info(f"Web scraping completed for: {task['url']}")
        
        # Add comprehensive timestamp information for Ray
        result = add_ray_timestamp_to_response(result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in web scrape endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@web_router.post("/search-and-scrape")
async def search_and_scrape(request: SearchAndScrapeRequest):
    """Combined search and scrape operation"""
    try:
        data = request.dict()
        
        query = data['query']
        max_results = data.get('max_results', 5)
        scrape_first = data.get('scrape_first', True)
        
        # Process combined operation
        result = web_handler.search_and_scrape(query, max_results, scrape_first)
        
        # Add metadata
        result['timestamp'] = datetime.now().isoformat()
        result['assigned_by'] = data.get('assigned_by', 'unknown')
        
        logger.info(f"Combined search and scrape completed for: {query}")
        
        # Add comprehensive timestamp information for Ray
        result = add_ray_timestamp_to_response(result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in search and scrape endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@web_router.get("/status")
async def web_status():
    """Get web module status"""
    return {
        'module': 'web',
        'status': 'active',
        'capabilities': [
            'web_search',
            'web_scraping',
            'combined_operations'
        ],
        'endpoints': [
            '/web/search',
            '/web/scrape',
            '/web/search-and-scrape',
            '/web/status'
        ],
        'timestamp': datetime.now().isoformat()
    }
    
    # Add comprehensive timestamp information for Ray
    status = add_ray_timestamp_to_response(status)
    
    return status