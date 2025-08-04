# Web Scraper Frontend Guide

A complete guide for using Ray's web scraping capabilities from the frontend.

## Quick Start

Ray's web scraper provides three main operations:
- **Search**: Find web pages using search queries
- **Scrape**: Extract content from specific URLs
- **Search & Scrape**: Combined operation that searches then scrapes results

## API Endpoints

### Base URL
```
http://localhost:8000
```

### Available Routes
- `POST /web/search` - Web search functionality
- `POST /web/scrape` - URL content scraping
- `POST /web/search-and-scrape` - Combined operation
- `GET /web/status` - Check web module status

## 1. Web Search

### Endpoint
```
POST /web/search
```

### Request Format
```json
{
  "task": {
    "query": "your search terms",
    "max_results": 5
  },
  "assigned_by": "frontend_user"
}
```

### JavaScript Example
```javascript
async function searchWeb(query, maxResults = 5) {
  const response = await fetch('http://localhost:8000/web/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      task: {
        query: query,
        max_results: maxResults
      },
      assigned_by: 'frontend_user'
    })
  });
  
  const data = await response.json();
  return data;
}

// Usage
searchWeb('Python web scraping tutorial', 10)
  .then(results => {
    console.log('Search Results:', results);
    results.results.forEach(result => {
      console.log(`${result.title}: ${result.url}`);
    });
  });
```

### Response Format
```json
{
  "success": true,
  "query": "Python web scraping tutorial",
  "results": [
    {
      "title": "Web Scraping with Python Tutorial",
      "url": "https://example.com/tutorial",
      "snippet": "Learn how to scrape websites...",
      "domain": "example.com",
      "rank": 1
    }
  ],
  "total_results": 5,
  "search_time": 1.23,
  "timestamp": "2025-01-27T10:30:00Z",
  "assigned_by": "frontend_user"
}
```

## 2. Web Scraping

### Endpoint
```
POST /web/scrape
```

### Request Format
```json
{
  "task": {
    "url": "https://example.com",
    "extract_text": true,
    "extract_links": false,
    "max_content_length": 10000
  },
  "assigned_by": "frontend_user"
}
```

### JavaScript Example
```javascript
async function scrapeUrl(url, options = {}) {
  const defaultOptions = {
    extract_text: true,
    extract_links: false,
    max_content_length: 10000
  };
  
  const scrapeOptions = { ...defaultOptions, ...options };
  
  const response = await fetch('http://localhost:8000/web/scrape', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      task: {
        url: url,
        ...scrapeOptions
      },
      assigned_by: 'frontend_user'
    })
  });
  
  const data = await response.json();
  return data;
}

// Usage
scrapeUrl('https://example.com/article', {
  extract_text: true,
  extract_links: true,
  max_content_length: 15000
})
.then(result => {
  if (result.success) {
    console.log('Title:', result.content.title);
    console.log('Content:', result.content.text_content);
    console.log('Links found:', result.content.links.length);
  } else {
    console.error('Scraping failed:', result.error_message);
  }
});
```

### Response Format
```json
{
  "success": true,
  "processing_time": 2.45,
  "timestamp": "2025-01-27T10:30:00Z",
  "assigned_by": "frontend_user",
  "content": {
    "url": "https://example.com/article",
    "title": "Article Title",
    "text_content": "Full article text content...",
    "links": ["https://link1.com", "https://link2.com"],
    "images": ["https://image1.jpg"],
    "metadata": {
      "description": "Article description",
      "keywords": "keyword1, keyword2"
    },
    "content_length": 5432,
    "scraped_at": "2025-01-27T10:30:00Z"
  }
}
```

## 3. Combined Search & Scrape

### Endpoint
```
POST /web/search-and-scrape
```

### Request Format
```json
{
  "query": "search terms",
  "max_results": 5,
  "scrape_first": true,
  "assigned_by": "frontend_user"
}
```

### JavaScript Example
```javascript
async function searchAndScrape(query, options = {}) {
  const defaultOptions = {
    max_results: 5,
    scrape_first: true
  };
  
  const searchOptions = { ...defaultOptions, ...options };
  
  const response = await fetch('http://localhost:8000/web/search-and-scrape', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      ...searchOptions,
      assigned_by: 'frontend_user'
    })
  });
  
  const data = await response.json();
  return data;
}

// Usage
searchAndScrape('latest AI news', {
  max_results: 3,
  scrape_first: false  // Scrape first 3 results instead of just first
})
.then(result => {
  if (result.success) {
    console.log('Search Results:', result.search_results);
    console.log('Scraped Content:', result.scraped_content);
  } else {
    console.error('Operation failed:', result.error_message);
  }
});
```

## 4. Complete Frontend Integration Example

### HTML Structure
```html
<!DOCTYPE html>
<html>
<head>
    <title>Ray Web Scraper</title>
    <style>
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .result { border: 1px solid #ddd; margin: 10px 0; padding: 15px; }
        .loading { color: #666; font-style: italic; }
        .error { color: red; }
        .success { color: green; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Ray Web Scraper</h1>
        
        <!-- Search Form -->
        <div>
            <h2>Web Search</h2>
            <input type="text" id="searchQuery" placeholder="Enter search query" style="width: 300px;">
            <input type="number" id="maxResults" value="5" min="1" max="20" style="width: 60px;">
            <button onclick="performSearch()">Search</button>
        </div>
        
        <!-- Scrape Form -->
        <div>
            <h2>Scrape URL</h2>
            <input type="url" id="scrapeUrl" placeholder="Enter URL to scrape" style="width: 400px;">
            <button onclick="performScrape()">Scrape</button>
        </div>
        
        <!-- Results -->
        <div id="results"></div>
    </div>

    <script src="scraper.js"></script>
</body>
</html>
```

### JavaScript Implementation (scraper.js)
```javascript
class RayWebScraper {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async search(query, maxResults = 5) {
    try {
      const response = await fetch(`${this.baseUrl}/web/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          task: { query, max_results: maxResults },
          assigned_by: 'frontend_user'
        })
      });
      return await response.json();
    } catch (error) {
      return { success: false, error_message: error.message };
    }
  }

  async scrape(url, options = {}) {
    try {
      const response = await fetch(`${this.baseUrl}/web/scrape`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          task: { url, extract_text: true, ...options },
          assigned_by: 'frontend_user'
        })
      });
      return await response.json();
    } catch (error) {
      return { success: false, error_message: error.message };
    }
  }

  async searchAndScrape(query, options = {}) {
    try {
      const response = await fetch(`${this.baseUrl}/web/search-and-scrape`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          max_results: 5,
          scrape_first: true,
          ...options,
          assigned_by: 'frontend_user'
        })
      });
      return await response.json();
    } catch (error) {
      return { success: false, error_message: error.message };
    }
  }
}

// Initialize scraper
const scraper = new RayWebScraper();

// UI Functions
function showLoading(message = 'Processing...') {
  document.getElementById('results').innerHTML = `<div class="loading">${message}</div>`;
}

function showError(message) {
  document.getElementById('results').innerHTML = `<div class="error">Error: ${message}</div>`;
}

function showSearchResults(data) {
  if (!data.success) {
    showError(data.error_message || 'Search failed');
    return;
  }

  let html = `<div class="success">Found ${data.total_results} results in ${data.search_time.toFixed(2)}s</div>`;
  
  data.results.forEach(result => {
    html += `
      <div class="result">
        <h3><a href="${result.url}" target="_blank">${result.title}</a></h3>
        <p><strong>Domain:</strong> ${result.domain}</p>
        <p>${result.snippet}</p>
        <button onclick="scrapeFromResult('${result.url}')">Scrape This Page</button>
      </div>
    `;
  });

  document.getElementById('results').innerHTML = html;
}

function showScrapeResults(data) {
  if (!data.success) {
    showError(data.error_message || 'Scraping failed');
    return;
  }

  const content = data.content;
  const html = `
    <div class="success">Scraping completed in ${data.processing_time.toFixed(2)}s</div>
    <div class="result">
      <h3>${content.title}</h3>
      <p><strong>URL:</strong> <a href="${content.url}" target="_blank">${content.url}</a></p>
      <p><strong>Content Length:</strong> ${content.content_length} characters</p>
      <p><strong>Links Found:</strong> ${content.links.length}</p>
      <p><strong>Images Found:</strong> ${content.images.length}</p>
      <div>
        <h4>Content Preview:</h4>
        <div style="max-height: 300px; overflow-y: auto; border: 1px solid #ccc; padding: 10px;">
          ${content.text_content.substring(0, 2000)}${content.text_content.length > 2000 ? '...' : ''}
        </div>
      </div>
    </div>
  `;

  document.getElementById('results').innerHTML = html;
}

async function performSearch() {
  const query = document.getElementById('searchQuery').value.trim();
  const maxResults = parseInt(document.getElementById('maxResults').value) || 5;

  if (!query) {
    showError('Please enter a search query');
    return;
  }

  showLoading('Searching...');
  const results = await scraper.search(query, maxResults);
  showSearchResults(results);
}

async function performScrape() {
  const url = document.getElementById('scrapeUrl').value.trim();

  if (!url) {
    showError('Please enter a URL to scrape');
    return;
  }

  showLoading('Scraping...');
  const results = await scraper.scrape(url);
  showScrapeResults(results);
}

async function scrapeFromResult(url) {
  showLoading('Scraping selected result...');
  const results = await scraper.scrape(url);
  showScrapeResults(results);
}
```

## Error Handling

### Common Error Responses
```json
{
  "success": false,
  "error_message": "Failed to connect to URL",
  "timestamp": "2025-01-27T10:30:00Z"
}
```

### Error Handling Best Practices
```javascript
async function handleWebOperation(operation) {
  try {
    const result = await operation();
    
    if (!result.success) {
      console.error('Operation failed:', result.error_message);
      // Show user-friendly error message
      showUserError(result.error_message);
      return null;
    }
    
    return result;
  } catch (error) {
    console.error('Network error:', error);
    showUserError('Network connection failed. Please try again.');
    return null;
  }
}
```

## Rate Limiting & Best Practices

### Recommendations
- **Search**: Wait 1-2 seconds between searches
- **Scraping**: Wait 2-3 seconds between scrape requests
- **Batch Operations**: Use search-and-scrape for efficiency
- **Error Handling**: Always check `success` field in responses
- **Content Length**: Limit `max_content_length` for better performance

### Example with Rate Limiting
```javascript
class RateLimitedScraper extends RayWebScraper {
  constructor(baseUrl) {
    super(baseUrl);
    this.lastRequest = 0;
    this.minInterval = 2000; // 2 seconds
  }

  async makeRequest(url, options) {
    const now = Date.now();
    const timeSinceLastRequest = now - this.lastRequest;
    
    if (timeSinceLastRequest < this.minInterval) {
      const waitTime = this.minInterval - timeSinceLastRequest;
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }
    
    this.lastRequest = Date.now();
    return super.makeRequest(url, options);
  }
}
```

## Status Check

### Check Web Module Status
```javascript
async function checkWebStatus() {
  try {
    const response = await fetch('http://localhost:8000/web/status');
    const status = await response.json();
    console.log('Web module status:', status);
    return status.status === 'active';
  } catch (error) {
    console.error('Failed to check web status:', error);
    return false;
  }
}
```

This guide provides everything you need to integrate Ray's web scraping capabilities into your frontend application. The scraper uses DuckDuckGo for search with Google fallback, includes proper rate limiting, and provides comprehensive error handling.