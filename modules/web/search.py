"""
Web search functionality for Ray
"""

import time
from datetime import datetime
from typing import List
import requests
from bs4 import BeautifulSoup

from .models import WebSearchRequest, WebSearchResponse, SearchResult
from .utils import create_session, extract_domain, clean_text, rate_limit


class WebSearcher:
    """Handles web search operations"""
    
    def __init__(self):
        self.session = create_session()
    
    def search(self, request: WebSearchRequest) -> WebSearchResponse:
        """Perform web search"""
        start_time = time.time()
        
        try:
            # Use DuckDuckGo for search (no API key required)
            results = self._search_duckduckgo(request)
            
            search_time = time.time() - start_time
            
            return WebSearchResponse(
                success=True,
                query=request.query,
                results=results,
                total_results=len(results),
                search_time=search_time,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            search_time = time.time() - start_time
            return WebSearchResponse(
                success=False,
                query=request.query,
                results=[],
                total_results=0,
                search_time=search_time,
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    def _search_duckduckgo(self, request: WebSearchRequest) -> List[SearchResult]:
        """Search using DuckDuckGo"""
        results = []
        
        # DuckDuckGo search URL
        search_url = "https://duckduckgo.com/html/"
        
        params = {
            'q': request.query,
            'kl': f'{request.region}-{request.language}',
            's': '0',  # Start from first result
            'dc': str(request.max_results)
        }
        
        if request.safe_search:
            params['safe'] = 'moderate'
        
        # Add rate limiting
        rate_limit(1.0)
        
        response = self.session.get(search_url, params=params, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Parse search results
        result_elements = soup.find_all('div', class_='result')
        
        for i, element in enumerate(result_elements[:request.max_results]):
            try:
                # Extract title and URL
                title_element = element.find('a', class_='result__a')
                if not title_element:
                    continue
                
                title = clean_text(title_element.get_text())
                url = title_element.get('href', '')
                
                # Extract snippet
                snippet_element = element.find('a', class_='result__snippet')
                snippet = ""
                if snippet_element:
                    snippet = clean_text(snippet_element.get_text())
                
                # Create search result
                if title and url:
                    result = SearchResult(
                        title=title,
                        url=url,
                        snippet=snippet,
                        domain=extract_domain(url),
                        rank=i + 1
                    )
                    results.append(result)
                    
            except Exception as e:
                # Skip problematic results
                continue
        
        return results
    
    def _search_google_fallback(self, request: WebSearchRequest) -> List[SearchResult]:
        """Fallback Google search (basic scraping - use carefully)"""
        results = []
        
        # This is a basic implementation - in production, use Google Custom Search API
        search_url = "https://www.google.com/search"
        
        params = {
            'q': request.query,
            'num': min(request.max_results, 10),
            'hl': request.language,
            'gl': request.region
        }
        
        if request.safe_search:
            params['safe'] = 'active'
        
        # Add longer delay for Google
        rate_limit(2.0)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = self.session.get(search_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse Google results (structure may change)
            result_elements = soup.find_all('div', class_='g')
            
            for i, element in enumerate(result_elements[:request.max_results]):
                try:
                    # Extract title and URL
                    title_element = element.find('h3')
                    link_element = element.find('a')
                    
                    if not title_element or not link_element:
                        continue
                    
                    title = clean_text(title_element.get_text())
                    url = link_element.get('href', '')
                    
                    # Extract snippet
                    snippet_elements = element.find_all('span')
                    snippet = ""
                    for span in snippet_elements:
                        text = span.get_text()
                        if len(text) > 50:  # Likely a snippet
                            snippet = clean_text(text)
                            break
                    
                    if title and url and url.startswith('http'):
                        result = SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet,
                            domain=extract_domain(url),
                            rank=i + 1
                        )
                        results.append(result)
                        
                except Exception:
                    continue
                    
        except Exception as e:
            # Return empty results on error
            pass
        
        return results