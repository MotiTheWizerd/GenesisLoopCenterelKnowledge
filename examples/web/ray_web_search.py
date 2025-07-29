"""
Ray Web Search Examples
Demonstrates web search capabilities
"""

import requests
import json
from datetime import datetime


def basic_search_example():
    """Basic web search example"""
    print("🔍 Basic Web Search Example")
    print("=" * 40)
    
    search_data = {
        "task": {
            "type": "search",
            "query": "python web scraping tutorial",
            "max_results": 5,
            "safe_search": True
        },
        "assigned_by": "ray"
    }
    
    try:
        response = requests.post("http://localhost:8000/web/search", json=search_data)
        result = response.json()
        
        if result['success']:
            print(f"Query: {result['query']}")
            print(f"Total Results: {result['total_results']}")
            print(f"Search Time: {result['search_time']:.2f}s")
            print("\nResults:")
            
            for i, search_result in enumerate(result['results'], 1):
                print(f"\n{i}. {search_result['title']}")
                print(f"   URL: {search_result['url']}")
                print(f"   Domain: {search_result['domain']}")
                print(f"   Snippet: {search_result['snippet'][:100]}...")
        else:
            print(f"Search failed: {result.get('error_message', 'Unknown error')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Ray server. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def advanced_search_example():
    """Advanced search with custom parameters"""
    print("\n🔍 Advanced Web Search Example")
    print("=" * 40)
    
    search_data = {
        "task": {
            "type": "search",
            "query": "machine learning algorithms",
            "max_results": 8,
            "safe_search": False,
            "language": "en",
            "region": "us"
        },
        "assigned_by": "ray"
    }
    
    try:
        response = requests.post("http://localhost:8000/web/search", json=search_data)
        result = response.json()
        
        if result['success']:
            print(f"Query: {result['query']}")
            print(f"Results found: {result['total_results']}")
            
            # Group results by domain
            domains = {}
            for search_result in result['results']:
                domain = search_result['domain']
                if domain not in domains:
                    domains[domain] = []
                domains[domain].append(search_result)
            
            print(f"\nResults grouped by domain:")
            for domain, results in domains.items():
                print(f"\n📍 {domain} ({len(results)} results)")
                for res in results:
                    print(f"   • {res['title']}")
        else:
            print(f"Search failed: {result.get('error_message', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def multiple_search_example():
    """Example of performing multiple searches"""
    print("\n🔍 Multiple Search Example")
    print("=" * 40)
    
    queries = [
        "artificial intelligence news",
        "python best practices",
        "web development trends 2024"
    ]
    
    all_results = []
    
    for query in queries:
        print(f"\nSearching for: {query}")
        
        search_data = {
            "task": {
                "type": "search",
                "query": query,
                "max_results": 3
            },
            "assigned_by": "ray"
        }
        
        try:
            response = requests.post("http://localhost:8000/web/search", json=search_data)
            result = response.json()
            
            if result['success']:
                print(f"  ✅ Found {result['total_results']} results")
                all_results.extend(result['results'])
            else:
                print(f"  ❌ Failed: {result.get('error_message', 'Unknown error')}")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"Total results collected: {len(all_results)}")
    
    # Top domains
    domain_counts = {}
    for result in all_results:
        domain = result['domain']
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    print("\nTop domains:")
    for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {domain}: {count} results")


if __name__ == "__main__":
    print("🤖 Ray Web Search Examples")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run examples
    basic_search_example()
    advanced_search_example()
    multiple_search_example()
    
    print("\n✨ Examples completed!")
    print("\nNext steps:")
    print("- Try modifying the queries")
    print("- Experiment with different parameters")
    print("- Check out ray_web_scraping.py for scraping examples")