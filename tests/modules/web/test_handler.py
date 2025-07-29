"""
Tests for web handler
"""

import pytest
from unittest.mock import Mock, patch
from modules.web.handler import WebHandler
from modules.web.models import WebSearchResponse, WebScrapeResponse, SearchResult


class TestWebHandler:
    def setup_method(self):
        self.handler = WebHandler()
    
    def test_init(self):
        assert self.handler.searcher is not None
        assert self.handler.scraper is not None
    
    @patch('modules.web.handler.WebSearcher')
    def test_handle_search_task(self, mock_searcher_class):
        # Setup mock
        mock_searcher = Mock()
        mock_searcher_class.return_value = mock_searcher
        
        mock_response = WebSearchResponse(
            success=True,
            query="test query",
            results=[],
            total_results=0,
            search_time=1.0,
            timestamp=None
        )
        mock_searcher.search.return_value = mock_response
        
        # Create handler with mock
        handler = WebHandler()
        
        # Test data
        task_data = {
            "task": {
                "type": "search",
                "query": "test query",
                "max_results": 10
            },
            "assigned_by": "ray"
        }
        
        # Execute
        result = handler.handle_task(task_data)
        
        # Verify
        assert isinstance(result, WebSearchResponse)
        assert result.success == True
        assert result.query == "test query"
    
    @patch('modules.web.handler.WebScraper')
    def test_handle_scrape_task(self, mock_scraper_class):
        # Setup mock
        mock_scraper = Mock()
        mock_scraper_class.return_value = mock_scraper
        
        mock_response = WebScrapeResponse(
            success=True,
            content=None,
            processing_time=2.0,
            timestamp=None
        )
        mock_scraper.scrape.return_value = mock_response
        
        # Create handler with mock
        handler = WebHandler()
        
        # Test data
        task_data = {
            "task": {
                "type": "scrape",
                "url": "https://example.com",
                "extract_text": True
            },
            "assigned_by": "ray"
        }
        
        # Execute
        result = handler.handle_task(task_data)
        
        # Verify
        assert isinstance(result, WebScrapeResponse)
        assert result.success == True
    
    def test_handle_invalid_task_type(self):
        task_data = {
            "task": {
                "type": "invalid",
                "query": "test"
            },
            "assigned_by": "ray"
        }
        
        result = self.handler.handle_task(task_data)
        
        # Should return error response
        assert hasattr(result, 'success')
        assert result.success == False
        assert "Unknown web task type" in str(result.error_message)
    
    def test_handle_malformed_task(self):
        task_data = {
            "invalid": "data"
        }
        
        result = self.handler.handle_task(task_data)
        
        # Should return error response
        assert hasattr(result, 'success')
        assert result.success == False
    
    @patch('modules.web.handler.WebSearcher')
    @patch('modules.web.handler.WebScraper')
    def test_search_and_scrape(self, mock_scraper_class, mock_searcher_class):
        # Setup mocks
        mock_searcher = Mock()
        mock_scraper = Mock()
        mock_searcher_class.return_value = mock_searcher
        mock_scraper_class.return_value = mock_scraper
        
        # Mock search response
        search_results = [
            SearchResult("Title", "https://example.com", "Snippet", "example.com", 1)
        ]
        mock_search_response = WebSearchResponse(
            success=True,
            query="test",
            results=search_results,
            total_results=1,
            search_time=1.0,
            timestamp=None
        )
        mock_searcher.search.return_value = mock_search_response
        
        # Mock scrape response
        mock_scrape_response = WebScrapeResponse(
            success=True,
            content=None,
            processing_time=2.0,
            timestamp=None
        )
        mock_scraper.scrape.return_value = mock_scrape_response
        
        # Create handler with mocks
        handler = WebHandler()
        
        # Execute
        result = handler.search_and_scrape("test query", max_results=5, scrape_first=True)
        
        # Verify
        assert result["success"] == True
        assert result["search_results"] is not None
        assert len(result["scraped_content"]) == 1
        assert result["error_message"] is None
    
    @patch('modules.web.handler.WebSearcher')
    def test_search_and_scrape_search_fails(self, mock_searcher_class):
        # Setup mock to fail
        mock_searcher = Mock()
        mock_searcher_class.return_value = mock_searcher
        
        mock_search_response = WebSearchResponse(
            success=False,
            query="test",
            results=[],
            total_results=0,
            search_time=0.0,
            timestamp=None,
            error_message="Search failed"
        )
        mock_searcher.search.return_value = mock_search_response
        
        # Create handler with mock
        handler = WebHandler()
        
        # Execute
        result = handler.search_and_scrape("test query")
        
        # Verify
        assert result["success"] == False
        assert "Search failed" in result["error_message"]
        assert len(result["scraped_content"]) == 0