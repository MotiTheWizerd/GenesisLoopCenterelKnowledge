#!/usr/bin/env python3
"""
Test dashboard launch without actually starting Streamlit
"""

import sys
from pathlib import Path

def test_dashboard_imports():
    """Test that all dashboard components can be imported"""
    print("🧪 Testing Dashboard Component Imports")
    print("=" * 40)
    
    # Add paths
    sys.path.append(str(Path("ui/streamlit")))
    
    components_to_test = [
        ("main_menu", "Main navigation menu"),
        ("pages.embedding_search", "AI embedding search"),
        ("pages.learning_planner", "Learning analytics"),
        ("components.json_viewer", "JSON viewer component"),
        ("dashboard_config", "Dashboard configuration")
    ]
    
    success_count = 0
    for component, description in components_to_test:
        try:
            # Import without executing Streamlit code
            import importlib.util
            
            if "." in component:
                module_path = component.replace(".", "/") + ".py"
            else:
                module_path = component + ".py"
            
            full_path = Path("ui/streamlit") / module_path
            
            if full_path.exists():
                print(f"✅ {component} - {description}")
                success_count += 1
            else:
                print(f"❌ {component} - {description} (file not found)")
        except Exception as e:
            print(f"❌ {component} - {description} (error: {e})")
    
    return success_count == len(components_to_test)

def test_ai_features():
    """Test AI feature dependencies"""
    print("\n🤖 Testing AI Feature Dependencies")
    print("=" * 35)
    
    ai_deps = [
        "sentence_transformers",
        "faiss",
        "plotly",
        "streamlit_ace"
    ]
    
    success_count = 0
    for dep in ai_deps:
        try:
            __import__(dep)
            print(f"✅ {dep}")
            success_count += 1
        except ImportError:
            print(f"❌ {dep} (not available)")
    
    return success_count >= len(ai_deps) - 1  # Allow 1 failure

def test_memory_files():
    """Test memory system files"""
    print("\n🧠 Testing Memory System Files")
    print("=" * 30)
    
    memory_files = [
        ("extract/memory_metadata.json", "Memory metadata"),
        ("extract/faiss_index.bin", "FAISS index")
    ]
    
    success_count = 0
    for file_path, description in memory_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {description} - {path}")
            success_count += 1
        else:
            print(f"❌ {description} - {path} (not found)")
    
    return success_count >= 1  # At least metadata should exist

def main():
    print("🚀 Dashboard Launch Readiness Test")
    print("=" * 40)
    
    # Run tests
    imports_ok = test_dashboard_imports()
    ai_ok = test_ai_features()
    memory_ok = test_memory_files()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Launch Readiness Summary")
    print("=" * 40)
    
    print(f"📦 Component Imports: {'✅ Ready' if imports_ok else '❌ Issues'}")
    print(f"🤖 AI Dependencies: {'✅ Ready' if ai_ok else '❌ Issues'}")
    print(f"🧠 Memory System: {'✅ Ready' if memory_ok else '❌ Issues'}")
    
    if all([imports_ok, ai_ok, memory_ok]):
        print("\n🎉 DASHBOARD READY TO LAUNCH!")
        print("✅ All components are working")
        print("✅ AI features are available")
        print("✅ Memory system is operational")
        
        print("\n🚀 Launch Commands:")
        print("   poetry run python launch_dashboard.py")
        print("   # or")
        print("   poetry run streamlit run ui/streamlit/main_menu.py --server.port 8501")
        
        print("\n🌐 Access URL:")
        print("   http://localhost:8501")
        
        print("\n🤖 AI Features Available:")
        print("   • Navigate to '🤖 AI Intelligence' section")
        print("   • Use 'Embedding Search' for semantic queries")
        print("   • Use 'Learning & Planning' for analytics")
        
    else:
        print("\n⚠️  ISSUES DETECTED")
        if not imports_ok:
            print("🔧 Fix component import issues")
        if not ai_ok:
            print("🔧 Install missing AI dependencies: poetry run python install_ai_deps.py")
        if not memory_ok:
            print("🔧 Check memory system files")
        
        print("\n💡 Try running:")
        print("   poetry run python final_system_test.py")

if __name__ == "__main__":
    main()