#!/usr/bin/env python3
"""
Fix encoding issues in memory metadata file
"""

import json
import chardet
from pathlib import Path

def detect_and_fix_encoding(file_path):
    """Detect file encoding and convert to UTF-8"""
    
    print(f"🔍 Analyzing file: {file_path}")
    
    # Read raw bytes to detect encoding
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    
    # Detect encoding
    detected = chardet.detect(raw_data)
    print(f"📊 Detected encoding: {detected}")
    
    if detected['encoding'] is None:
        print("❌ Could not detect encoding")
        return False
    
    # Try multiple encoding strategies
    encodings_to_try = [
        detected['encoding'],
        'utf-8',
        'utf-8-sig',
        'latin1',
        'cp1252',
        'iso-8859-1'
    ]
    
    for encoding in encodings_to_try:
        if encoding is None:
            continue
            
        try:
            print(f"🔄 Trying encoding: {encoding}")
            
            # Try with error handling
            text_content = raw_data.decode(encoding, errors='replace')
            print(f"✅ Decoded with {encoding} (with character replacement)")
            
            # Try to parse as JSON
            json_data = json.loads(text_content)
            print(f"✅ Valid JSON with {len(json_data)} entries")
            
            # Create backup
            backup_path = file_path.with_suffix('.json.backup')
            print(f"💾 Creating backup: {backup_path}")
            
            with open(backup_path, 'wb') as f:
                f.write(raw_data)
            
            # Write UTF-8 version
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ File converted to UTF-8: {file_path}")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed with {encoding}: {e}")
            continue
        except Exception as e:
            print(f"❌ Error with {encoding}: {e}")
            continue
    
    print("❌ All encoding attempts failed")
    return False

def main():
    print("🔧 Memory Metadata Encoding Fixer")
    print("=" * 40)
    
    metadata_file = Path("extract/memory_metadata.json")
    
    if not metadata_file.exists():
        print(f"❌ File not found: {metadata_file}")
        return
    
    # Check current file size
    file_size = metadata_file.stat().st_size
    print(f"📏 File size: {file_size:,} bytes")
    
    if detect_and_fix_encoding(metadata_file):
        print("\n🎉 Encoding fix completed successfully!")
        print("✅ The metadata file should now work properly with the dashboard")
        
        # Test the fix
        print("\n🧪 Testing the fix...")
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Test successful: {len(data)} entries loaded")
        except Exception as e:
            print(f"❌ Test failed: {e}")
    else:
        print("\n❌ Encoding fix failed")
        print("💡 You may need to regenerate the metadata file")

if __name__ == "__main__":
    main()