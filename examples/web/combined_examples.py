"""
Ray Combined Web Operations Examples
Demonstrates search + scrape workflows
"""

import requests
import json
from datetime import datetime


def search_and_scrape_example():
    """Example of combined search and scrape operation"""
    print("🔍🕷️ Search and Scrape Example")
    print("=" * 40)
    
    # Use the combined endpoint
    combined_data = {
        "query": "python web scraping best practices",
        "max_results": 3,
        "scrape_first": True,
        "assigned_by": "ray"
    }
    
    try:
        response = requests.post("http://localhost:8000/web/search-and-scrape", json=combined_data)
        result = response.json()
        
        if result['success']:
            # Show search results
            search_results = result['search_results']
            print(f"Search Query: {search_results['query']}")
            print(f"Found {search_results['total_results']} results")
            
            print("\nSearch Results:")
            for i, search_result in enumerate(search_results['results'], 1):
                print(f"{i}. {search_result['title']}")
                print(f"   {search_result['url']}")
                print(f"   {search_result['snippet'][:80]}...")
            
            # Show scraped content
            scraped_content = result['scraped_content']
            if scraped_content:
                print(f"\n📄 Scraped Content from First Result:")
                for scrape_result in scraped_content:
                    if scrape_result['success']:
                        content = scrape_result['content']
                        print(f"Title: {content['title']}")
                        print(f"Content Length: {content['content_length']} characters")
                        print(f"Preview: {content['text_content'][:200]}...")
                    else:
                        print(f"Scraping failed: {scrape_result.get('error_message', 'Unknown error')}")
        else:
            print(f"Operation failed: {result.get('error_message', 'Unknown error')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Ray server. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def manual_search_then_scrape():
    """Example of manual search followed by scraping multiple results"""
    print("\n🔍➡️🕷️ Manual Search Then Scrape Example")
    print("=" * 50)
    
    # Step 1: Search
    search_data = {
        "task": {
            "type": "search",
            "query": "artificial intelligence tutorials",
            "max_results": 5
        },
        "assigned_by": "ray"
    }
    
    try:
        print("Step 1: Searching...")
        response = requests.post("http://localhost:8000/web/search", json=search_data)
        search_result = response.json()
        
        if not search_result['success']:
            print(f"Search failed: {search_result.get('error_message', 'Unknown error')}")
            return
        
        print(f"Found {search_result['total_results']} results")
        
        # Step 2: Scrape top 3 results
        print("\nStep 2: Scraping top 3 results...")
        scraped_data = []
        
        for i, result in enumerate(search_result['results'][:3], 1):
            print(f"\nScraping {i}/3: {result['title'][:50]}...")
            
            scrape_data = {
                "task": {
                    "type": "scrape",
                    "url": result['url'],
                    "extract_text": True,
                    "extract_links": False,
                    "max_content_length": 3000
                },
                "assigned_by": "ray"
            }
            
            try:
                scrape_response = requests.post("http://localhost:8000/web/scrape", json=scrape_data)
                scrape_result = scrape_response.json()
                
                if scrape_result['success']:
                    content = scrape_result['content']
                    scraped_data.append({
                        'title': content['title'],
                        'url': content['url'],
                        'content_length': content['content_length'],
                        'text_preview': content['text_content'][:150] + "...",
                        'success': True
                    })
                    print(f"  ✅ Success - {content['content_length']} chars")
                else:
                    scraped_data.append({
                        'url': result['url'],
                        'error': scrape_result.get('error_message', 'Unknown error'),
                        'success': False
                    })
                    print(f"  ❌ Failed: {scrape_result.get('error_message', 'Unknown error')}")
                    
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                scraped_data.append({
                    'url': result['url'],
                    'error': str(e),
                    'success': False
                })
        
        # Step 3: Summary
        print(f"\n📊 Summary:")
        successful_scrapes = [d for d in scraped_data if d['success']]
        print(f"Successfully scraped: {len(successful_scrapes)}/3")
        
        if successful_scrapes:
            total_content = sum(d['content_length'] for d in successful_scrapes)
            print(f"Total content: {total_content} characters")
            
            print(f"\nContent previews:")
            for data in successful_scrapes:
                print(f"• {data['title'][:40]}... ({data['content_length']} chars)")
                print(f"  {data['text_preview']}")
                print()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def research_workflow_example():
    """Example of a research workflow using search and scrape"""
    print("\n📚 Research Workflow Example")
    print("=" * 40)
    
    research_topics = [
        "machine learning fundamentals",
        "neural network architectures",
        "deep learning applications"
    ]
    
    research_data = {}
    
    for topic in research_topics:
        print(f"\n🔍 Researching: {topic}")
        
        # Search for the topic
        search_data = {
            "task": {
                "type": "search",
                "query": topic,
                "max_results": 2
            },
            "assigned_by": "ray"
        }
        
        try:
            response = requests.post("http://localhost:8000/web/search", json=search_data)
            search_result = response.json()
            
            if search_result['success'] and search_result['results']:
                # Scrape the first result
                first_result = search_result['results'][0]
                print(f"  📄 Scraping: {first_result['title'][:50]}...")
                
                scrape_data = {
                    "task": {
                        "type": "scrape",
                        "url": first_result['url'],
                        "extract_text": True,
                        "max_content_length": 2000
                    },
                    "assigned_by": "ray"
                }
                
                scrape_response = requests.post("http://localhost:8000/web/scrape", json=scrape_data)
                scrape_result = scrape_response.json()
                
                if scrape_result['success']:
                    content = scrape_result['content']
                    research_data[topic] = {
                        'source_title': content['title'],
                        'source_url': content['url'],
                        'content_length': content['content_length'],
                        'key_content': content['text_content'][:500] + "...",
                        'success': True
                    }
                    print(f"    ✅ Collected {content['content_length']} chars")
                else:
                    research_data[topic] = {
                        'error': scrape_result.get('error_message', 'Scraping failed'),
                        'success': False
                    }
                    print(f"    ❌ Scraping failed")
            else:
                research_data[topic] = {
                    'error': 'No search results found',
                    'success': False
                }
                print(f"    ❌ No search results")
                
        except Exception as e:
            research_data[topic] = {
                'error': str(e),
                'success': False
            }
            print(f"    ❌ Error: {str(e)}")
    
    # Research summary
    print(f"\n📋 Research Summary:")
    successful_topics = [topic for topic, data in research_data.items() if data['success']]
    print(f"Successfully researched: {len(successful_topics)}/{len(research_topics)} topics")
    
    for topic, data in research_data.items():
        if data['success']:
            print(f"\n📖 {topic.title()}:")
            print(f"   Source: {data['source_title']}")
            print(f"   Content: {data['content_length']} characters")
            print(f"   Preview: {data['key_content'][:100]}...")


if __name__ == "__main__":
    print("🤖 Ray Combined Web Operations Examples")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run examples
    search_and_scrape_example()
    manual_search_then_scrape()
    research_workflow_example()
    
    print("\n✨ Examples completed!")
    print("\nNext steps:")
    print("- Try different research topics")
    print("- Experiment with scraping multiple results")
    print("- Build your own research workflows")