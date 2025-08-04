"""
Quick test to verify web endpoints are working
"""

import requests
import json
import time


def test_web_status():
    """Test the web status endpoint"""
    print("🔍 Testing Web Status Endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/web/status")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Web status endpoint working!")
            print(f"   Module: {result['module']}")
            print(f"   Status: {result['status']}")
            print(f"   Capabilities: {', '.join(result['capabilities'])}")
            return True
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_web_search():
    """Test the web search endpoint"""
    print("\n🔍 Testing Web Search Endpoint...")
    
    search_data = {
        "task": {
            "type": "search",
            "query": "python programming",
            "max_results": 3
        },
        "assigned_by": "test"
    }
    
    try:
        response = requests.post("http://localhost:8000/web/search", json=search_data)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ Web search endpoint working!")
                print(f"   Query: {result['query']}")
                print(f"   Results: {result['total_results']}")
                print(f"   Search time: {result['search_time']:.2f}s")
                
                if result['results']:
                    print(f"   First result: {result['results'][0]['title'][:50]}...")
                return True
            else:
                print(f"❌ Search failed: {result.get('error_message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Search endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_web_scrape():
    """Test the web scraping endpoint"""
    print("\n🕷️ Testing Web Scraping Endpoint...")
    
    scrape_data = {
        "task": {
            "type": "scrape",
            "url": "https://httpbin.org/html",
            "extract_text": True,
            "max_content_length": 1000
        },
        "assigned_by": "test"
    }
    
    try:
        response = requests.post("http://localhost:8000/web/scrape", json=scrape_data)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                content = result['content']
                print("✅ Web scraping endpoint working!")
                print(f"   URL: {content['url']}")
                print(f"   Title: {content['title']}")
                print(f"   Content length: {content['content_length']} chars")
                print(f"   Processing time: {result['processing_time']:.2f}s")
                return True
            else:
                print(f"❌ Scraping failed: {result.get('error_message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Scraping endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    print("🤖 Ray Web Module Endpoint Tests")
    print("=" * 50)
    
    # Test all endpoints
    status_ok = test_web_status()
    search_ok = test_web_search()
    scrape_ok = test_web_scrape()
    
    print("\n📊 Test Summary:")
    print(f"Status endpoint: {'✅' if status_ok else '❌'}")
    print(f"Search endpoint: {'✅' if search_ok else '❌'}")
    print(f"Scraping endpoint: {'✅' if scrape_ok else '❌'}")
    
    if all([status_ok, search_ok, scrape_ok]):
        print("\n🎉 All web endpoints are working perfectly!")
        print("\nRay now has full web search and scraping capabilities!")
    else:
        print("\n⚠️ Some endpoints need attention.")
        print("Make sure the server is running: python main.py")


if __name__ == "__main__":
    main()