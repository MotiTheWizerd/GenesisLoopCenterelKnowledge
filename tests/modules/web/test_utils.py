"""
Tests for web module utilities
"""

import pytest
import requests
from modules.web.utils import (
    create_session, clean_text, extract_domain, is_valid_url,
    normalize_url, truncate_content
)


class TestCreateSession:
    def test_session_creation(self):
        session = create_session()
        assert isinstance(session, requests.Session)
        assert 'User-Agent' in session.headers
        assert 'Ray-AI-Assistant' in session.headers['User-Agent']


class TestCleanText:
    def test_clean_basic_text(self):
        text = "  Hello   world  "
        result = clean_text(text)
        assert result == "Hello world"
    
    def test_clean_empty_text(self):
        assert clean_text("") == ""
        assert clean_text(None) == ""
    
    def test_clean_special_characters(self):
        text = "Hello @#$% world!"
        result = clean_text(text)
        assert result == "Hello  world!"
    
    def test_clean_multiple_spaces(self):
        text = "Hello\n\n\tworld\r\n"
        result = clean_text(text)
        assert result == "Hello world"


class TestExtractDomain:
    def test_extract_valid_domain(self):
        url = "https://www.example.com/path/to/page"
        result = extract_domain(url)
        assert result == "www.example.com"
    
    def test_extract_domain_no_www(self):
        url = "https://example.com"
        result = extract_domain(url)
        assert result == "example.com"
    
    def test_extract_domain_with_port(self):
        url = "http://localhost:8080/path"
        result = extract_domain(url)
        assert result == "localhost:8080"
    
    def test_extract_invalid_url(self):
        url = "not-a-url"
        result = extract_domain(url)
        assert result == ""


class TestIsValidUrl:
    def test_valid_http_url(self):
        assert is_valid_url("http://example.com") == True
    
    def test_valid_https_url(self):
        assert is_valid_url("https://example.com") == True
    
    def test_valid_url_with_path(self):
        assert is_valid_url("https://example.com/path/to/page") == True
    
    def test_invalid_url_no_scheme(self):
        assert is_valid_url("example.com") == False
    
    def test_invalid_url_no_domain(self):
        assert is_valid_url("https://") == False
    
    def test_invalid_url_malformed(self):
        assert is_valid_url("not-a-url") == False


class TestNormalizeUrl:
    def test_absolute_url(self):
        url = "https://example.com/page"
        result = normalize_url(url)
        assert result == "https://example.com/page"
    
    def test_relative_url_with_base(self):
        url = "/page"
        base_url = "https://example.com"
        result = normalize_url(url, base_url)
        assert result == "https://example.com/page"
    
    def test_relative_url_no_base(self):
        url = "/page"
        result = normalize_url(url)
        assert result == "/page"
    
    def test_empty_url(self):
        result = normalize_url("")
        assert result == ""


class TestTruncateContent:
    def test_short_content(self):
        content = "Short content"
        result = truncate_content(content, 100)
        assert result == "Short content"
    
    def test_long_content_word_boundary(self):
        content = "This is a very long piece of content that needs to be truncated"
        result = truncate_content(content, 30)
        assert len(result) <= 33  # 30 + "..."
        assert result.endswith("...")
        assert not result[:-3].endswith(" ")  # Should not end with space before ...
    
    def test_long_content_no_spaces(self):
        content = "a" * 100
        result = truncate_content(content, 50)
        assert len(result) == 53  # 50 + "..."
        assert result.endswith("...")
    
    def test_exact_length(self):
        content = "a" * 50
        result = truncate_content(content, 50)
        assert result == content  # Should not be truncated