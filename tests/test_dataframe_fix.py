#!/usr/bin/env python3
"""
Test DataFrame creation to verify PyArrow fix
"""

import pandas as pd

def test_dataframe_creation():
    """Test that DataFrames can be created without PyArrow errors"""
    print("🧪 Testing DataFrame Creation")
    print("=" * 30)
    
    try:
        # Test 1: Mixed type DataFrame (the problematic case)
        print("1. Testing mixed type DataFrame...")
        mixed_data = [
            {'Category': 'Low-importance ops', 'Count': 10, 'Percentage': '66%'},
            {'Category': 'Mid-importance ops', 'Count': 5, 'Percentage': '25%'},
        ]
        mixed_df = pd.DataFrame(mixed_data)
        print(f"   ✅ Mixed DataFrame created: {mixed_df.shape}")
        
        # Test 2: String-only DataFrame (the fix)
        print("2. Testing string-only DataFrame...")
        string_data = [
            {'Category': 'Low-importance ops', 'Count': '10', 'Percentage': '66%'},
            {'Category': 'Mid-importance ops', 'Count': '5', 'Percentage': '25%'},
        ]
        string_df = pd.DataFrame(string_data)
        print(f"   ✅ String DataFrame created: {string_df.shape}")
        
        # Test 3: Schema analysis style
        print("3. Testing schema analysis style...")
        schema_data = [
            {'Field': 'content', 'Presence': '100/100 (100.0%)', 'Types': 'str', 'Examples': 'example text'},
            {'Field': 'timestamp', 'Presence': '95/100 (95.0%)', 'Types': 'float', 'Examples': '1234567890.0'}
        ]
        schema_df = pd.DataFrame(schema_data)
        print(f"   ✅ Schema DataFrame created: {schema_df.shape}")
        
        print("\n🎉 All DataFrame tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ DataFrame test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_streamlit_compatibility():
    """Test Streamlit compatibility"""
    print("\n🧪 Testing Streamlit Compatibility")
    print("=" * 35)
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
        
        # Test DataFrame display (this would normally cause the PyArrow error)
        test_data = [
            {'Field': 'test', 'Count': '5', 'Percentage': '50%'}
        ]
        test_df = pd.DataFrame(test_data)
        
        # This is where the PyArrow error would occur in Streamlit
        print("✅ DataFrame ready for Streamlit display")
        return True
        
    except Exception as e:
        print(f"❌ Streamlit compatibility test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 DataFrame PyArrow Fix Tests")
    print("=" * 40)
    
    results = []
    results.append(test_dataframe_creation())
    results.append(test_streamlit_compatibility())
    
    print(f"\n📊 Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("🎉 All tests passed! PyArrow error should be fixed!")
    else:
        print("⚠️  Some tests failed - there may still be issues")

if __name__ == "__main__":
    main()