# Ray Web Search & Scraping System

## Overview

Ray's web module provides comprehensive web search and scraping capabilities, enabling Ray to search the internet and extract content from web pages. The module is designed with safety, efficiency, and respect for web resources in mind.

## Core Components

### 1. Web Search (`WebSearcher`)
- **Purpose**: Search the web using DuckDuckGo (no API key required)
- **Features**: 
  - Configurable result limits
  - Safe search options
  - Language and region settings
  - Rate limiting for respectful usage
  - Fallback search engines

### 2. Web Scraping (`WebScraper`)
- **Purpose**: Extract content from web pages
- **Features**:
  - Text content extraction
  - Link extraction with metadata
  - Image extraction with attributes
  - Content length limits
  - Timeout handling
  - Metadata extraction

### 3. Combined Operations (`WebHandler`)
- **Purpose**: Orchestrate search and scraping workflows
- **Features**:
  - Search then scrape workflows
  - Batch processing
  - Error handling and recovery
  - Performance optimization

## API Endpoints

### Search Endpoint
```
POST /web/search
```

**Request Format:**
```json
{
    "task": [
        {
            "type": "search",
            "query": "python web scraping",
            "max_results": 10,
            "safe_search": true,
            "language": "en",
            "region": "us"
        }
    ],
    "assigned_by": "ray"
}
```

**Response Format:**
```json
{
    "success": true,
    "query": "python web scraping",
    "results": [
        {
            "title": "Web Scraping with Python",
            "url": "https://example.com/scraping",
            "snippet": "Learn how to scrape websites...",
            "domain": "example.com",
            "rank": 1
        }
    ],
    "total_results": 10,
    "search_time": 1.23,
    "timestamp": "2025-01-28T10:30:00Z",
    "assigned_by": "ray"
}
```

### Scraping Endpoint
```
POST /web/scrape
```

**Request Format:**
```json
{
    "task": [
        {
            "type": "scrape",
            "url": "https://example.com",
            "extract_text": true,
            "extract_links": true,
            "extract_images": false,
            "max_content_length": 50000,
            "timeout": 30,
            "follow_redirects": true
        }
    ],
    "assigned_by": "ray"
}
```

**Response Format:**
```json
{
    "success": true,
    "content": {
        "url": "https://example.com",
        "title": "Example Page",
        "text_content": "This is the main content...",
        "links": [
            {
                "url": "https://example.com/page2",
                "text": "Link Text",
                "title": "Link Title"
            }
        ],
        "images": [],
        "metadata": {
            "title": "Example Page",
            "description": "Page description",
            "author": "Author Name"
        },
        "content_length": 1234,
        "scraped_at": "2025-01-28T10:30:00Z"
    },
    "processing_time": 2.45,
    "timestamp": "2025-01-28T10:30:00Z",
    "assigned_by": "ray"
}
```

### Combined Endpoint
```
POST /web/search-and-scrape
```

**Request Format:**
```json
{
    "query": "machine learning tutorials",
    "max_results": 5,
    "scrape_first": true,
    "assigned_by": "ray"
}
```

## Configuration Options

### Search Parameters
- **query** (required): Search query string
- **max_results**: Maximum number of results (default: 10)
- **safe_search**: Enable safe search filtering (default: true)
- **language**: Language code (default: "en")
- **region**: Region code (default: "us")

### Scraping Parameters
- **url** (required): URL to scrape
- **extract_text**: Extract text content (default: true)
- **extract_links**: Extract links (default: false)
- **extract_images**: Extract images (default: false)
- **max_content_length**: Maximum content length (default: 50000)
- **timeout**: Request timeout in seconds (default: 30)
- **follow_redirects**: Follow HTTP redirects (default: true)

## Safety Features

### Rate Limiting
- Built-in delays between requests
- Configurable rate limits
- Respectful of server resources

### Content Filtering
- Content length limits to prevent memory issues
- Safe search enabled by default
- Timeout protection against hanging requests

### Error Handling
- Graceful failure handling
- Detailed error messages
- Retry logic for transient failures

### Ethical Considerations
- Respects robots.txt (planned feature)
- User-agent identification
- Rate limiting to avoid overwhelming servers
- Content length limits

## Performance Optimization

### Caching
- Session reuse for multiple requests
- Connection pooling
- Retry strategies for failed requests

### Content Processing
- Efficient HTML parsing with BeautifulSoup
- Text cleaning and normalization
- Smart content truncation at word boundaries

### Memory Management
- Content length limits
- Streaming for large responses
- Garbage collection friendly design

## Usage Examples

### Basic Search
```python
import requests

search_data = {
    "task": [
        {
            "type": "search",
            "query": "python tutorials",
            "max_results": 5
        }
    ],
    "assigned_by": "ray"
}

response = requests.post("http://localhost:8000/web/search", json=search_data)
results = response.json()
```

### Basic Scraping
```python
import requests

scrape_data = {
    "task": [
        {
            "type": "scrape",
            "url": "https://example.com",
            "extract_text": True
        }
    ],
    "assigned_by": "ray"
}

response = requests.post("http://localhost:8000/web/scrape", json=scrape_data)
content = response.json()
```

### Combined Operation
```python
import requests

combined_data = {
    "query": "web scraping best practices",
    "max_results": 3,
    "scrape_first": True,
    "assigned_by": "ray"
}

response = requests.post("http://localhost:8000/web/search-and-scrape", json=combined_data)
result = response.json()
```

## Error Handling

### Common Error Types
- **Invalid URL**: Malformed or unreachable URLs
- **Timeout**: Requests that exceed timeout limits
- **Network Error**: Connection failures
- **Content Error**: Parsing or processing failures
- **Rate Limit**: Too many requests too quickly

### Error Response Format
```json
{
    "success": false,
    "error_message": "Detailed error description",
    "timestamp": "2025-01-28T10:30:00Z"
}
```

## Dependencies

### Required Packages
```bash
pip install requests beautifulsoup4 lxml urllib3
```

### Optional Enhancements
- `googlesearch-python` for Google search fallback
- `selenium` for JavaScript-heavy sites (future feature)
- `aiohttp` for async operations (future feature)

## Future Enhancements

### Planned Features
- JavaScript rendering support
- Advanced content extraction (tables, forms)
- Bulk operations with better performance
- Custom search engine integration
- Content caching system
- Advanced filtering and processing

### Integration Possibilities
- Integration with Ray's memory system
- Content summarization capabilities
- Automatic fact-checking
- Research workflow automation

## Monitoring and Logging

### Performance Metrics
- Search response times
- Scraping success rates
- Content extraction statistics
- Error rates and types

### Logging
- Request/response logging
- Error tracking
- Performance monitoring
- Usage analytics

This web system provides Ray with powerful capabilities to search and extract information from the internet while maintaining ethical and efficient practices.