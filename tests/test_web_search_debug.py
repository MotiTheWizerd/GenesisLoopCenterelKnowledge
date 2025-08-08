#!/usr/bin/env python3
"""
Debug script to test web search functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.web.search import WebSearcher
from modules.web.models import WebSearchRequest

def test_web_search():
    """Test the web search functionality"""
    print("🔍 Testing web search functionality...")
    
    searcher = WebSearcher()
    
    # Test with a simple query
    request = WebSearchRequest(
        query="how to add broadlink rm4 pro to home assistant using YAML",
        max_results=5,
        safe_search=True,
        language="en",
        region="us"
    )
    
    print(f"Query: {request.query}")
    print(f"Max results: {request.max_results}")
    
    try:
        response = searcher.search(request)
        
        print(f"\n📊 Search Results:")
        print(f"Success: {response.success}")
        print(f"Total results: {response.total_results}")
        print(f"Search time: {response.search_time:.2f}s")
        
        if response.error_message:
            print(f"❌ Error: {response.error_message}")
        
        if response.results:
            print(f"\n📋 Found {len(response.results)} results:")
            for i, result in enumerate(response.results, 1):
                print(f"\n{i}. {result.title}")
                print(f"   URL: {result.url}")
                print(f"   Domain: {result.domain}")
                print(f"   Snippet: {result.snippet[:100]}...")
        else:
            print("❌ No results found")
            
            # Let's try to debug the DuckDuckGo response
            print("\n🔧 Debugging DuckDuckGo response...")
            
            import requests
            from bs4 import BeautifulSoup
            
            search_url = "https://duckduckgo.com/html/"
            params = {
                'q': request.query,
                'kl': f'{request.region}-{request.language}',
                's': '0',
                'dc': str(request.max_results)
            }
            
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Ray-AI-Assistant/1.0 (Web Search and Scraping Module)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            })
            
            try:
                response_raw = session.get(search_url, params=params, timeout=30)
                print(f"HTTP Status: {response_raw.status_code}")
                print(f"Response length: {len(response_raw.content)} bytes")
                
                soup = BeautifulSoup(response_raw.content, 'html.parser')
                result_elements = soup.find_all('div', class_='result')
                print(f"Found {len(result_elements)} result elements")
                
                # Check for any error messages or captcha
                if "blocked" in response_raw.text.lower() or "captcha" in response_raw.text.lower():
                    print("⚠️  Possible blocking or captcha detected")
                
                # Save raw response for inspection
                with open('debug_duckduckgo_response.html', 'w', encoding='utf-8') as f:
                    f.write(response_raw.text)
                print("💾 Raw response saved to debug_duckduckgo_response.html")
                
            except Exception as e:
                print(f"❌ Raw request failed: {e}")
    
    except Exception as e:
        print(f"❌ Search failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_web_search()