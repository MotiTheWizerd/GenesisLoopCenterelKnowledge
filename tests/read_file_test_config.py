"""
Configuration for read_file tests.

This module contains test configuration, fixtures, and utilities
for comprehensive read_file testing.
"""

import os
import tempfile
import shutil
from pathlib import Path


class ReadFileTestConfig:
    """Configuration for read_file tests."""
    
    # Server configuration
    BASE_URL = "http://localhost:8000"
    TIMEOUT = 30  # seconds
    
    # Test file sizes
    SMALL_FILE_SIZE = 100  # bytes
    MEDIUM_FILE_SIZE = 10240  # 10KB
    LARGE_FILE_SIZE = 1048576  # 1MB
    
    # Test limits
    MAX_TEST_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    DEFAULT_LINE_COUNT = 100
    
    # Test encodings
    TEST_ENCODINGS = ["utf-8", "latin-1", "ascii"]
    
    # Test file types
    TEST_FILE_TYPES = {
        "text": [".txt", ".md", ".log"],
        "code": [".py", ".js", ".json", ".yaml", ".yml"],
        "config": [".conf", ".ini", ".cfg"],
        "data": [".csv", ".tsv", ".xml"]
    }


class TestFileGenerator:
    """Utility class for generating test files."""
    
    @staticmethod
    def create_text_file(path: str, lines: int = 10, line_prefix: str = "Line") -> str:
        """Create a text file with specified number of lines."""
        content = "\n".join([f"{line_prefix} {i}: Test content for line {i}" for i in range(1, lines + 1)])
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return content
    
    @staticmethod
    def create_json_file(path: str, data: dict = None) -> str:
        """Create a JSON file with test data."""
        import json
        
        if data is None:
            data = {
                "version": "1.0",
                "debug": True,
                "features": ["read", "write", "search"],
                "config": {
                    "max_size": 1024,
                    "encoding": "utf-8"
                }
            }
        
        content = json.dumps(data, indent=2)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return content
    
    @staticmethod
    def create_python_file(path: str) -> str:
        """Create a Python file with test code."""
        content = '''#!/usr/bin/env python3
"""
Test Python file for read_file functionality.
"""

import os
import sys


def hello_world():
    """Print hello world message."""
    print("Hello, World!")
    return True


def process_data(data):
    """Process some data."""
    if not data:
        return None
    
    result = []
    for item in data:
        if isinstance(item, str):
            result.append(item.upper())
        else:
            result.append(str(item))
    
    return result


class TestClass:
    """Test class for demonstration."""
    
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hello from {self.name}!"


if __name__ == "__main__":
    hello_world()
    
    test_data = ["hello", "world", 123, 456]
    processed = process_data(test_data)
    print(f"Processed data: {processed}")
    
    test_obj = TestClass("Ray")
    print(test_obj.greet())
'''
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return content
    
    @staticmethod
    def create_unicode_file(path: str) -> str:
        """Create a file with Unicode characters."""
        content = """Unicode Test File 🌟

This file contains various Unicode characters for testing:

Emojis: 😀 😃 😄 😁 😆 😅 😂 🤣 🧠 🌟 ⭐ 💫
Accented characters: àáâãäå èéêë ìíîï òóôõö ùúûü ñç
Mathematical symbols: ∑ ∏ ∫ ∂ ∆ ∇ ∞ ≈ ≠ ≤ ≥
Greek letters: α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω
Currency symbols: $ € £ ¥ ₹ ₽ ₩ ₪
Arrows: ← → ↑ ↓ ↔ ↕ ↖ ↗ ↘ ↙

Ray's consciousness test: 🧠 → 💭 → 🌟
"""
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return content
    
    @staticmethod
    def create_binary_file(path: str, size: int = 1024) -> bytes:
        """Create a binary file with random data."""
        import random
        
        data = bytes([random.randint(0, 255) for _ in range(size)])
        
        with open(path, 'wb') as f:
            f.write(data)
        
        return data
    
    @staticmethod
    def create_large_file(path: str, lines: int = 1000) -> str:
        """Create a large file for performance testing."""
        content_lines = []
        
        for i in range(1, lines + 1):
            line = f"Line {i:04d}: This is a large file for performance testing. " \
                   f"It contains {lines} lines total. Current timestamp: {i * 1000}. " \
                   f"Random data: {'x' * (i % 50)}"
            content_lines.append(line)
        
        content = "\n".join(content_lines)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return content
    
    @staticmethod
    def create_encoded_file(path: str, encoding: str = 'latin-1') -> str:
        """Create a file with specific encoding."""
        if encoding == 'latin-1':
            content = "Latin-1 encoded file\nSpecial characters: café, naïve, résumé, piñata\nMore: àáâãäå èéêë ìíîï òóôõö ùúûü"
        elif encoding == 'ascii':
            content = "ASCII encoded file\nOnly basic characters allowed\nNo special symbols or accents"
        else:
            content = "UTF-8 encoded file\nUnicode characters: 🌟 🧠 💭\nAccents: café naïve résumé"
        
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        
        return content


class TestFileManager:
    """Manager for creating and cleaning up test files."""
    
    def __init__(self):
        self.temp_dirs = []
        self.temp_files = []
    
    def create_temp_dir(self) -> str:
        """Create a temporary directory."""
        temp_dir = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        return temp_dir
    
    def create_comprehensive_test_structure(self) -> str:
        """Create a comprehensive test directory structure."""
        temp_dir = self.create_temp_dir()
        
        # Create various test files
        generator = TestFileGenerator()
        
        # Text files
        generator.create_text_file(os.path.join(temp_dir, "simple.txt"), 5)
        generator.create_text_file(os.path.join(temp_dir, "medium.txt"), 50)
        generator.create_large_file(os.path.join(temp_dir, "large.txt"), 200)
        
        # Empty file
        with open(os.path.join(temp_dir, "empty.txt"), 'w') as f:
            f.write("")
        
        # Single line file
        with open(os.path.join(temp_dir, "single_line.txt"), 'w') as f:
            f.write("Just one line without newline")
        
        # Code files
        generator.create_python_file(os.path.join(temp_dir, "script.py"))
        generator.create_json_file(os.path.join(temp_dir, "config.json"))
        
        # Unicode file
        generator.create_unicode_file(os.path.join(temp_dir, "unicode.txt"))
        
        # Different encodings
        generator.create_encoded_file(os.path.join(temp_dir, "latin1.txt"), "latin-1")
        generator.create_encoded_file(os.path.join(temp_dir, "ascii.txt"), "ascii")
        
        # Binary file
        generator.create_binary_file(os.path.join(temp_dir, "binary.dat"), 512)
        
        # Log files
        log_content = "\n".join([
            f"[2025-07-30 10:{i:02d}:00] INFO: Log entry {i} - System operational"
            for i in range(1, 101)
        ])
        with open(os.path.join(temp_dir, "application.log"), 'w') as f:
            f.write(log_content)
        
        # Create subdirectory
        subdir = os.path.join(temp_dir, "subdir")
        os.makedirs(subdir)
        generator.create_text_file(os.path.join(subdir, "nested.txt"), 3, "Nested line")
        
        # Create hidden file
        with open(os.path.join(temp_dir, ".hidden"), 'w') as f:
            f.write("Hidden file content")
        
        return temp_dir
    
    def cleanup(self):
        """Clean up all temporary files and directories."""
        # Clean up temporary files
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass
        
        # Clean up temporary directories
        for dir_path in self.temp_dirs:
            try:
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path)
            except Exception:
                pass
        
        self.temp_files.clear()
        self.temp_dirs.clear()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


# Test data constants
SAMPLE_JSON_DATA = {
    "app_name": "Ray's Consciousness System",
    "version": "2.0.0",
    "features": {
        "read_file": True,
        "directory_search": True,
        "task_processing": True
    },
    "limits": {
        "max_file_size": 10485760,
        "max_line_count": 10000,
        "timeout_seconds": 30
    },
    "encodings": ["utf-8", "latin-1", "ascii"]
}

SAMPLE_PYTHON_CODE = '''
def fibonacci(n):
    """Calculate Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
for i in range(10):
    print(f"fib({i}) = {fibonacci(i)}")
'''

SAMPLE_LOG_ENTRIES = [
    "[2025-07-30 10:00:00] INFO: System started",
    "[2025-07-30 10:00:01] DEBUG: Loading configuration",
    "[2025-07-30 10:00:02] INFO: Configuration loaded successfully",
    "[2025-07-30 10:00:03] INFO: Starting read_file service",
    "[2025-07-30 10:00:04] INFO: Service ready to accept requests",
    "[2025-07-30 10:00:05] DEBUG: First request received",
    "[2025-07-30 10:00:06] INFO: Request processed successfully",
    "[2025-07-30 10:00:07] DEBUG: Response sent to client",
    "[2025-07-30 10:00:08] INFO: System operational",
    "[2025-07-30 10:00:09] DEBUG: Monitoring system health"
]