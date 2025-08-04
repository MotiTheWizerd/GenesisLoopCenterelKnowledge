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
        
        try:
            # Try the HTML version first
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
            
            # Use more realistic headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = self.session.get(search_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors for DuckDuckGo results
            result_elements = soup.find_all('div', class_='result') or \
                            soup.find_all('div', class_='web-result') or \
                            soup.find_all('article') or \
                            soup.find_all('div', {'data-testid': 'result'})
            
            print(f"🔍 Found {len(result_elements)} result elements")
            
            for i, element in enumerate(result_elements[:request.max_results]):
                try:
                    # Try multiple selectors for title and URL
                    title_element = element.find('a', class_='result__a') or \
                                  element.find('h3') or \
                                  element.find('a', class_='result-title-a') or \
                                  element.find('a')
                    
                    if not title_element:
                        continue
                    
                    title = clean_text(title_element.get_text())
                    url = title_element.get('href', '')
                    
                    # Extract snippet with multiple selectors
                    snippet_element = element.find('a', class_='result__snippet') or \
                                    element.find('span', class_='result__snippet') or \
                                    element.find('div', class_='snippet') or \
                                    element.find('p')
                    
                    snippet = ""
                    if snippet_element:
                        snippet = clean_text(snippet_element.get_text())
                    
                    # Create search result
                    if title and url and url.startswith('http'):
                        result = SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet,
                            domain=extract_domain(url),
                            rank=i + 1
                        )
                        results.append(result)
                        print(f"   ✅ Result {i+1}: {title[:50]}...")
                        
                except Exception as e:
                    print(f"   ⚠️  Error parsing result {i+1}: {str(e)}")
                    continue
            
            # If no results, try fallback to Google
            if not results:
                print("🔄 No DuckDuckGo results, trying Google fallback...")
                results = self._search_google_fallback(request)
            
        except Exception as e:
            print(f"❌ DuckDuckGo search failed: {str(e)}")
            # Try Google fallback
            try:
                results = self._search_google_fallback(request)
            except Exception as fallback_error:
                print(f"❌ Google fallback also failed: {str(fallback_error)}")
        
        return results
    
    def _search_google_fallback(self, request: WebSearchRequest) -> List[SearchResult]:
        """Fallback Google search (basic scraping - use carefully)"""
        results = []
        
        try:
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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = self.session.get(search_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse Google results (try multiple selectors)
            result_elements = soup.find_all('div', class_='g') or \
                            soup.find_all('div', class_='tF2Cxc') or \
                            soup.find_all('div', {'data-ved': True})
            
            print(f"🔍 Google fallback found {len(result_elements)} result elements")
            
            for i, element in enumerate(result_elements[:request.max_results]):
                try:
                    # Extract title and URL with multiple selectors
                    title_element = element.find('h3') or element.find('h2')
                    link_element = element.find('a')
                    
                    if not title_element or not link_element:
                        continue
                    
                    title = clean_text(title_element.get_text())
                    url = link_element.get('href', '')
                    
                    # Clean up Google redirect URLs
                    if url.startswith('/url?q='):
                        url = url.split('/url?q=')[1].split('&')[0]
                    
                    # Extract snippet with multiple selectors
                    snippet_elements = element.find_all('span') + element.find_all('div')
                    snippet = ""
                    for elem in snippet_elements:
                        text = elem.get_text()
                        if len(text) > 50 and len(text) < 300:  # Likely a snippet
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
                        print(f"   ✅ Google result {i+1}: {title[:50]}...")
                        
                except Exception as e:
                    print(f"   ⚠️  Error parsing Google result {i+1}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"❌ Google fallback search failed: {str(e)}")
        
        return results