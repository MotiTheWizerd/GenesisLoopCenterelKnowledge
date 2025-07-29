"""
Ray Web Scraping Examples
Demonstrates web scraping capabilities
"""

import requests
import json
from datetime import datetime


def basic_scraping_example():
    """Basic web scraping example"""
    print("🕷️ Basic Web Scraping Example")
    print("=" * 40)
    
    scrape_data = {
        "task": {
            "type": "scrape",
            "url": "https://httpbin.org/html",  # Test URL that returns HTML
            "extract_text": True,
            "extract_links": False,
            "max_content_length": 5000
        },
        "assigned_by": "ray"
    }
    
    try:
        response = requests.post("http://localhost:8000/web/scrape", json=scrape_data)
        result = response.json()
        
        if result['success']:
            content = result['content']
            print(f"URL: {content['url']}")
            print(f"Title: {content['title']}")
            print(f"Content Length: {content['content_length']} characters")
            print(f"Processing Time: {result['processing_time']:.2f}s")
            print(f"\nText Content Preview:")
            print(content['text_content'][:300] + "..." if len(content['text_content']) > 300 else content['text_content'])
            
            # Show metadata
            print(f"\nMetadata:")
            for key, value in content['metadata'].items():
                if key not in ['content_type', 'content_encoding']:
                    print(f"  {key}: {value}")
        else:
            print(f"Scraping failed: {result.get('error_message', 'Unknown error')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Ray server. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def advanced_scraping_example():
    """Advanced scraping with links and images"""
    print("\n🕷️ Advanced Web Scraping Example")
    print("=" * 40)
    
    scrape_data = {
        "task": {
            "type": "scrape",
            "url": "https://example.com",
            "extract_text": True,
            "extract_links": True,
            "extract_images": True,
            "max_content_length": 10000,
            "timeout": 30
        },
        "assigned_by": "ray"
    }
    
    try:
        response = requests.post("http://localhost:8000/web/scrape", json=scrape_data)
        result = response.json()
        
        if result['success']:
            content = result['content']
            print(f"Successfully scraped: {content['url']}")
            print(f"Title: {content['title']}")
            print(f"Content length: {content['content_length']} characters")
            
            # Show links
            if content['links']:
                print(f"\n🔗 Found {len(content['links'])} links:")
                for i, link in enumerate(content['links'][:5], 1):  # Show first 5
                    print(f"  {i}. {link['text'][:50]}... -> {link['url']}")
                if len(content['links']) > 5:
                    print(f"  ... and {len(content['links']) - 5} more links")
            
            # Show images
            if content['images']:
                print(f"\n🖼️ Found {len(content['images'])} images:")
                for i, img in enumerate(content['images'][:3], 1):  # Show first 3
                    print(f"  {i}. {img['alt'][:30]}... -> {img['url']}")
                if len(content['images']) > 3:
                    print(f"  ... and {len(content['images']) - 3} more images")
            
            # Show text preview
            print(f"\n📄 Text content preview:")
            print(content['text_content'][:400] + "..." if len(content['text_content']) > 400 else content['text_content'])
            
        else:
            print(f"Scraping failed: {result.get('error_message', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def scrape_multiple_urls():
    """Example of scraping multiple URLs"""
    print("\n🕷️ Multiple URL Scraping Example")
    print("=" * 40)
    
    urls = [
        "https://httpbin.org/html",
        "https://example.com",
        "https://httpbin.org/json"
    ]
    
    results = []
    
    for url in urls:
        print(f"\nScraping: {url}")
        
        scrape_data = {
            "task": {
                "type": "scrape",
                "url": url,
                "extract_text": True,
                "max_content_length": 2000
            },
            "assigned_by": "ray"
        }
        
        try:
            response = requests.post("http://localhost:8000/web/scrape", json=scrape_data)
            result = response.json()
            
            if result['success']:
                content = result['content']
                print(f"  ✅ Success - {content['content_length']} chars")
                results.append({
                    'url': url,
                    'title': content['title'],
                    'content_length': content['content_length'],
                    'success': True
                })
            else:
                print(f"  ❌ Failed: {result.get('error_message', 'Unknown error')}")
                results.append({
                    'url': url,
                    'error': result.get('error_message', 'Unknown error'),
                    'success': False
                })
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            results.append({
                'url': url,
                'error': str(e),
                'success': False
            })
    
    # Summary
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\n📊 Summary:")
    print(f"Successful: {len(successful)}/{len(results)}")
    print(f"Failed: {len(failed)}/{len(results)}")
    
    if successful:
        total_content = sum(r['content_length'] for r in successful)
        print(f"Total content scraped: {total_content} characters")


if __name__ == "__main__":
    print("🤖 Ray Web Scraping Examples")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run examples
    basic_scraping_example()
    advanced_scraping_example()
    scrape_multiple_urls()
    
    print("\n✨ Examples completed!")
    print("\nNext steps:")
    print("- Try scraping different websites")
    print("- Experiment with extraction settings")
    print("- Check out combined_examples.py for search + scrape workflows")