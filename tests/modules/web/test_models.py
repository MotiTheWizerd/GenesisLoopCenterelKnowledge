"""
Tests for web module models
"""

import pytest
from datetime import datetime
from modules.web.models import (
    WebSearchRequest, WebScrapeRequest, WebTaskRequest,
    SearchResult, ScrapedContent, WebSearchResponse, WebScrapeResponse
)


class TestWebSearchRequest:
    def test_default_values(self):
        request = WebSearchRequest(query="test query")
        assert request.query == "test query"
        assert request.max_results == 10
        assert request.safe_search == True
        assert request.language == "en"
        assert request.region == "us"
    
    def test_custom_values(self):
        request = WebSearchRequest(
            query="python programming",
            max_results=20,
            safe_search=False,
            language="es",
            region="mx"
        )
        assert request.query == "python programming"
        assert request.max_results == 20
        assert request.safe_search == False
        assert request.language == "es"
        assert request.region == "mx"


class TestWebScrapeRequest:
    def test_default_values(self):
        request = WebScrapeRequest(url="https://example.com")
        assert request.url == "https://example.com"
        assert request.extract_text == True
        assert request.extract_links == False
        assert request.extract_images == False
        assert request.max_content_length == 50000
        assert request.timeout == 30
        assert request.follow_redirects == True
    
    def test_custom_values(self):
        request = WebScrapeRequest(
            url="https://test.com",
            extract_text=False,
            extract_links=True,
            extract_images=True,
            max_content_length=10000,
            timeout=60,
            follow_redirects=False
        )
        assert request.url == "https://test.com"
        assert request.extract_text == False
        assert request.extract_links == True
        assert request.extract_images == True
        assert request.max_content_length == 10000
        assert request.timeout == 60
        assert request.follow_redirects == False


class TestWebTaskRequest:
    def test_get_task_type(self):
        task_request = WebTaskRequest(
            task={"type": "search", "query": "test"},
            assigned_by="ray"
        )
        assert task_request.get_task_type() == "search"
    
    def test_to_search_request(self):
        task_request = WebTaskRequest(
            task={
                "type": "search",
                "query": "python",
                "max_results": 15,
                "safe_search": False
            },
            assigned_by="ray"
        )
        
        search_request = task_request.to_search_request()
        assert isinstance(search_request, WebSearchRequest)
        assert search_request.query == "python"
        assert search_request.max_results == 15
        assert search_request.safe_search == False
    
    def test_to_scrape_request(self):
        task_request = WebTaskRequest(
            task={
                "type": "scrape",
                "url": "https://example.com",
                "extract_links": True,
                "timeout": 45
            },
            assigned_by="ray"
        )
        
        scrape_request = task_request.to_scrape_request()
        assert isinstance(scrape_request, WebScrapeRequest)
        assert scrape_request.url == "https://example.com"
        assert scrape_request.extract_links == True
        assert scrape_request.timeout == 45


class TestSearchResult:
    def test_creation(self):
        result = SearchResult(
            title="Test Title",
            url="https://example.com",
            snippet="Test snippet",
            domain="example.com",
            rank=1
        )
        assert result.title == "Test Title"
        assert result.url == "https://example.com"
        assert result.snippet == "Test snippet"
        assert result.domain == "example.com"
        assert result.rank == 1


class TestScrapedContent:
    def test_creation(self):
        now = datetime.now()
        content = ScrapedContent(
            url="https://example.com",
            title="Test Page",
            text_content="Test content",
            links=[{"url": "https://link.com", "text": "Link"}],
            images=[{"url": "https://img.com", "alt": "Image"}],
            metadata={"author": "Test Author"},
            content_length=100,
            scraped_at=now
        )
        
        assert content.url == "https://example.com"
        assert content.title == "Test Page"
        assert content.text_content == "Test content"
        assert len(content.links) == 1
        assert len(content.images) == 1
        assert content.metadata["author"] == "Test Author"
        assert content.content_length == 100
        assert content.scraped_at == now


class TestWebSearchResponse:
    def test_successful_response(self):
        results = [
            SearchResult("Title 1", "https://example1.com", "Snippet 1", "example1.com", 1),
            SearchResult("Title 2", "https://example2.com", "Snippet 2", "example2.com", 2)
        ]
        
        response = WebSearchResponse(
            success=True,
            query="test query",
            results=results,
            total_results=2,
            search_time=1.5,
            timestamp=datetime.now()
        )
        
        assert response.success == True
        assert response.query == "test query"
        assert len(response.results) == 2
        assert response.total_results == 2
        assert response.search_time == 1.5
        assert response.error_message is None
    
    def test_failed_response(self):
        response = WebSearchResponse(
            success=False,
            query="test query",
            results=[],
            total_results=0,
            search_time=0.5,
            timestamp=datetime.now(),
            error_message="Search failed"
        )
        
        assert response.success == False
        assert response.query == "test query"
        assert len(response.results) == 0
        assert response.total_results == 0
        assert response.error_message == "Search failed"


class TestWebScrapeResponse:
    def test_successful_response(self):
        content = ScrapedContent(
            url="https://example.com",
            title="Test",
            text_content="Content",
            links=[],
            images=[],
            metadata={},
            content_length=7,
            scraped_at=datetime.now()
        )
        
        response = WebScrapeResponse(
            success=True,
            content=content,
            processing_time=2.0,
            timestamp=datetime.now()
        )
        
        assert response.success == True
        assert response.content == content
        assert response.processing_time == 2.0
        assert response.error_message is None
    
    def test_failed_response(self):
        response = WebScrapeResponse(
            success=False,
            content=None,
            processing_time=1.0,
            timestamp=datetime.now(),
            error_message="Scraping failed"
        )
        
        assert response.success == False
        assert response.content is None
        assert response.processing_time == 1.0
        assert response.error_message == "Scraping failed"