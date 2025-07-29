"""
Utility functions for web operations
"""

import re
import time
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def create_session(timeout: int = 30) -> requests.Session:
    """Create a configured requests session with retry logic"""
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Set headers
    session.headers.update({
        'User-Agent': 'Ray-AI-Assistant/1.0 (Web Search and Scraping Module)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    })
    
    return session


def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
    
    return text.strip()


def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except:
        return ""


def is_valid_url(url: str) -> bool:
    """Check if URL is valid"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def normalize_url(url: str, base_url: str = None) -> str:
    """Normalize and resolve relative URLs"""
    if not url:
        return ""
    
    # Handle relative URLs
    if base_url and not url.startswith(('http://', 'https://')):
        url = urljoin(base_url, url)
    
    return url


def truncate_content(content: str, max_length: int) -> str:
    """Truncate content to maximum length"""
    if len(content) <= max_length:
        return content
    
    # Try to truncate at word boundary
    truncated = content[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:  # If we can find a space in the last 20%
        truncated = truncated[:last_space]
    
    return truncated + "..."


def rate_limit(delay: float = 1.0):
    """Simple rate limiting"""
    time.sleep(delay)


def extract_metadata(soup) -> Dict[str, str]:
    """Extract metadata from HTML soup"""
    metadata = {}
    
    # Extract meta tags
    meta_tags = soup.find_all('meta')
    for tag in meta_tags:
        name = tag.get('name') or tag.get('property')
        content = tag.get('content')
        if name and content:
            metadata[name] = content
    
    # Extract title
    title_tag = soup.find('title')
    if title_tag:
        metadata['title'] = title_tag.get_text().strip()
    
    return metadata