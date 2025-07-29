# Web Module Examples

This directory contains examples of how to use Ray's web search and scraping capabilities.

## Available Examples

### 1. Web Search (`ray_web_search.py`)
- Basic web search functionality
- Search with custom parameters
- Processing search results

### 2. Web Scraping (`ray_web_scraping.py`)
- Scrape content from specific URLs
- Extract text, links, and images
- Handle different content types

### 3. Combined Operations (`combined_examples.py`)
- Search and scrape in one operation
- Process multiple URLs
- Advanced workflows

## Quick Start

### Web Search
```python
import requests

# Search for Python tutorials
search_data = {
    "task": {
        "type": "search",
        "query": "python programming tutorials",
        "max_results": 10,
        "safe_search": True
    },
    "assigned_by": "ray"
}

response = requests.post("http://localhost:8000/web/search", json=search_data)
results = response.json()

for result in results['results']:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Snippet: {result['snippet']}")
    print("-" * 50)
```

### Web Scraping
```python
import requests

# Scrape content from a webpage
scrape_data = {
    "task": {
        "type": "scrape",
        "url": "https://example.com",
        "extract_text": True,
        "extract_links": True,
        "max_content_length": 10000
    },
    "assigned_by": "ray"
}

response = requests.post("http://localhost:8000/web/scrape", json=scrape_data)
result = response.json()

if result['success']:
    content = result['content']
    print(f"Title: {content['title']}")
    print(f"Content Length: {content['content_length']}")
    print(f"Text: {content['text_content'][:500]}...")
```

## Running Examples

1. Make sure Ray's server is running:
   ```bash
   python main.py
   ```

2. Run any example:
   ```bash
   python examples/web/ray_web_search.py
   python examples/web/ray_web_scraping.py
   python examples/web/combined_examples.py
   ```

## API Endpoints

- `POST /web/search` - Perform web search
- `POST /web/scrape` - Scrape web content
- `POST /web/search-and-scrape` - Combined operation
- `GET /web/status` - Module status

## Safety Notes

- The module includes rate limiting to be respectful to websites
- Content length limits prevent excessive memory usage
- Safe search is enabled by default
- Timeouts prevent hanging requests

## Dependencies

Make sure you have these packages installed:
```bash
pip install requests beautifulsoup4 lxml
```