#!/usr/bin/env python3
"""
Test the embedding adapter implementation
"""

import os
from utils.embedding_adapter import EmbeddingManager

def test_minilm():
    """Test MiniLM backend"""
    print("🧪 Testing MiniLM Backend")
    print("-" * 30)
    
    try:
        # Setup (MiniLM now, Gemini later)
        embedding_manager = EmbeddingManager(backend="minilm")
        print("✅ MiniLM backend initialized")
        
        # Usage
        vector = embedding_manager.embed("some test text")
        print(f"✅ Embedding generated: {len(vector)} dimensions")
        print(f"✅ First few values: {vector[:5]}")
        
        return True
    except Exception as e:
        print(f"❌ MiniLM test failed: {e}")
        return False

def test_gemini():
    """Test Gemini backend"""
    print("\n🧪 Testing Gemini Backend")
    print("-" * 30)
    
    # Check for API key
    api_key = "AIzaSyB9T0S4iI4lRYfSDiYXvwsfE_-VqVbvfEI"
    if not api_key:
        print("⚠️  GEMINI_API_KEY not set - skipping Gemini test")
        print("   Set environment variable: export GEMINI_API_KEY='AIzaSyB9T0S4iI4lRYfSDiYXvwsfE_-VqVbvfEI'")
        return False
    
    try:
        # Switch to Gemini
        embedding_manager = EmbeddingManager(backend="gemini", gemini_api_key=api_key)
        print("✅ Gemini backend initialized")
        
        # Usage
        vector = embedding_manager.embed("some test text")
        print(f"✅ Embedding generated: {len(vector)} dimensions")
        print(f"✅ First few values: {vector[:5]}")
        
        return True
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        return False

def main():
    """Run tests"""
    print("🚀 Embedding Adapter Tests")
    print("=" * 40)
    
    results = []
    results.append(test_minilm())
    results.append(test_gemini())
    
    print(f"\n📊 Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed or skipped")

if __name__ == "__main__":
    main()