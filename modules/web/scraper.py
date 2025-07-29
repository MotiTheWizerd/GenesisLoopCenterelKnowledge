"""
Web scraping functionality for Ray
"""

import time
from datetime import datetime
from typing import List, Dict
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

from .models import WebScrapeRequest, WebScrapeResponse, ScrapedContent
from .utils import (
    create_session, clean_text, is_valid_url, normalize_url, 
    truncate_content, extract_metadata, rate_limit
)


class WebScraper:
    """Handles web scraping operations"""
    
    def __init__(self):
        self.session = create_session()
    
    def scrape(self, request: WebScrapeRequest) -> WebScrapeResponse:
        """Scrape content from a web page"""
        start_time = time.time()
        
        try:
            # Validate URL
            if not is_valid_url(request.url):
                raise ValueError(f"Invalid URL: {request.url}")
            
            # Add rate limiting
            rate_limit(0.5)
            
            # Fetch the page
            response = self._fetch_page(request)
            
            # Parse content
            content = self._parse_content(response, request)
            
            processing_time = time.time() - start_time
            
            return WebScrapeResponse(
                success=True,
                content=content,
                processing_time=processing_time,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return WebScrapeResponse(
                success=False,
                content=None,
                processing_time=processing_time,
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    def _fetch_page(self, request: WebScrapeRequest) -> requests.Response:
        """Fetch the web page"""
        response = self.session.get(
            request.url,
            timeout=request.timeout,
            allow_redirects=request.follow_redirects
        )
        response.raise_for_status()
        return response
    
    def _parse_content(self, response: requests.Response, request: WebScrapeRequest) -> ScrapedContent:
        """Parse content from the response"""
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Extract title
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = clean_text(title_tag.get_text())
        
        # Extract text content
        text_content = ""
        if request.extract_text:
            text_content = self._extract_text(soup, request.max_content_length)
        
        # Extract links
        links = []
        if request.extract_links:
            links = self._extract_links(soup, response.url)
        
        # Extract images
        images = []
        if request.extract_images:
            images = self._extract_images(soup, response.url)
        
        # Extract metadata
        metadata = extract_metadata(soup)
        metadata.update({
            'url': response.url,
            'status_code': response.status_code,
            'content_type': response.headers.get('content-type', ''),
            'content_encoding': response.encoding or 'utf-8'
        })
        
        return ScrapedContent(
            url=response.url,
            title=title,
            text_content=text_content,
            links=links,
            images=images,
            metadata=metadata,
            content_length=len(text_content),
            scraped_at=datetime.now()
        )
    
    def _extract_text(self, soup: BeautifulSoup, max_length: int) -> str:
        """Extract clean text content"""
        # Try to find main content areas first
        main_content = None
        
        # Look for common content containers
        for selector in ['main', 'article', '.content', '#content', '.post', '.entry']:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        # If no main content found, use body
        if not main_content:
            main_content = soup.find('body') or soup
        
        # Extract text
        text = main_content.get_text(separator=' ', strip=True)
        text = clean_text(text)
        
        # Truncate if necessary
        if len(text) > max_length:
            text = truncate_content(text, max_length)
        
        return text
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract links from the page"""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = clean_text(link.get_text())
            
            # Normalize URL
            full_url = normalize_url(href, base_url)
            
            if is_valid_url(full_url) and text:
                links.append({
                    'url': full_url,
                    'text': text,
                    'title': link.get('title', '')
                })
        
        return links[:100]  # Limit to first 100 links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract images from the page"""
        images = []
        
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            alt = img.get('alt', '')
            title = img.get('title', '')
            
            # Normalize URL
            full_url = normalize_url(src, base_url)
            
            if is_valid_url(full_url):
                images.append({
                    'url': full_url,
                    'alt': alt,
                    'title': title,
                    'width': img.get('width', ''),
                    'height': img.get('height', '')
                })
        
        return images[:50]  # Limit to first 50 images
    
    def scrape_multiple(self, urls: List[str], request_template: WebScrapeRequest) -> List[WebScrapeResponse]:
        """Scrape multiple URLs"""
        results = []
        
        for url in urls:
            # Create request for this URL
            request = WebScrapeRequest(
                url=url,
                extract_text=request_template.extract_text,
                extract_links=request_template.extract_links,
                extract_images=request_template.extract_images,
                max_content_length=request_template.max_content_length,
                timeout=request_template.timeout,
                follow_redirects=request_template.follow_redirects
            )
            
            # Scrape the URL
            result = self.scrape(request)
            results.append(result)
            
            # Add delay between requests
            rate_limit(1.0)
        
        return results