#!/usr/bin/env python3
"""
Test script for embedding search and learning features
"""

import sys
import json
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import sentence_transformers
        print("✅ sentence-transformers imported successfully")
    except ImportError as e:
        print(f"❌ sentence-transformers import failed: {e}")
        return False
    
    try:
        import faiss
        print("✅ faiss imported successfully")
    except ImportError as e:
        print(f"❌ faiss import failed: {e}")
        return False
    
    try:
        import plotly
        print("✅ plotly imported successfully")
    except ImportError as e:
        print(f"❌ plotly import failed: {e}")
        return False
    
    try:
        import pandas
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    return True

def test_memory_files():
    """Test if memory files exist"""
    print("\n📁 Testing memory files...")
    
    extract_dir = Path("extract")
    metadata_file = extract_dir / "memory_metadata.json"
    faiss_file = extract_dir / "faiss_index.bin"
    
    if metadata_file.exists():
        print("✅ memory_metadata.json found")
        try:
            with open(metadata_file, 'r', encoding='utf-8', errors='ignore') as f:
                metadata = json.load(f)
            print(f"📊 Found {len(metadata)} memory entries")
        except Exception as e:
            print(f"⚠️  Could not read metadata: {e}")
    else:
        print("❌ memory_metadata.json not found")
        print("💡 Run the memory extraction process first")
    
    if faiss_file.exists():
        print("✅ faiss_index.bin found")
    else:
        print("❌ faiss_index.bin not found")
        print("💡 Run the embedding process first")
    
    return metadata_file.exists()

def test_dashboard_pages():
    """Test if dashboard pages exist"""
    print("\n📄 Testing dashboard pages...")
    
    pages_dir = Path("ui/streamlit/pages")
    required_pages = [
        "embedding_search.py",
        "learning_planner.py"
    ]
    
    all_exist = True
    for page in required_pages:
        page_path = pages_dir / page
        if page_path.exists():
            print(f"✅ {page} exists")
        else:
            print(f"❌ {page} missing")
            all_exist = False
    
    return all_exist

def test_model_loading():
    """Test if AI models can be loaded"""
    print("\n🤖 Testing model loading...")
    
    try:
        from sentence_transformers import SentenceTransformer, CrossEncoder
        
        print("📥 Loading embedding model...")
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        print("✅ Embedding model loaded successfully")
        
        print("📥 Loading reranker model...")
        reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        print("✅ Reranker model loaded successfully")
        
        # Test encoding
        test_text = "This is a test sentence"
        embedding = embedding_model.encode([test_text])
        print(f"✅ Test encoding successful (shape: {embedding.shape})")
        
        return True
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False

def main():
    print("🧠 Ray's AI Features Test Suite")
    print("=" * 40)
    
    tests = [
        ("Package Imports", test_imports),
        ("Memory Files", test_memory_files),
        ("Dashboard Pages", test_dashboard_pages),
        ("Model Loading", test_model_loading)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results Summary:")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AI features are ready to use.")
        print("\n🚀 To launch the dashboard:")
        print("   python launch_streamlit.py")
    else:
        print("⚠️  Some tests failed. Please address the issues above.")
        
        if not results.get("Package Imports", False):
            print("\n💡 To install missing packages:")
            print("   python install_ai_deps.py")
        
        if not results.get("Memory Files", False):
            print("\n💡 To generate memory files:")
            print("   1. Ensure Ray's memory system is running")
            print("   2. Run the embedding extraction process")

if __name__ == "__main__":
    main()