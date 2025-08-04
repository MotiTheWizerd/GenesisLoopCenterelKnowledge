#!/usr/bin/env python3
"""
Quick Memory Structure Peek
Fast overview of Ray's memory structure
"""

import json
from services.memory_service import MemoryService

def quick_peek():
    """Quick peek at memory structure"""
    print("🔍 QUICK MEMORY STRUCTURE PEEK")
    print("=" * 40)
    
    memory_service = MemoryService()
    
    if not memory_service.is_system_ready():
        print("❌ Memory system not ready")
        return
    
    # Load a small sample
    memories = memory_service._load_memories()[:10]  # Just first 10
    metadata = memory_service._load_metadata()
    
    print(f"📊 Sample Analysis (first 10 of {len(memory_service._load_memories())} total)")
    print()
    
    # Show structure of first few memories
    for i, memory in enumerate(memories[:3]):
        print(f"🧠 Memory {i} Structure:")
        for field, value in memory.items():
            value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
            print(f"   {field}: {type(value).__name__} = {value_preview}")
        print()
    
    # Show mem-6 specifically if it exists
    mem_6 = metadata.get("mem-6")
    if mem_6:
        print("🎯 Memory mem-6 (your example):")
        for field, value in mem_6.items():
            if field == 'content':
                print(f"   {field}: {len(str(value))} chars = {str(value)[:100]}...")
            elif field == 'timestamp':
                from datetime import datetime
                if isinstance(value, (int, float)):
                    dt = datetime.fromtimestamp(value)
                    print(f"   {field}: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    print(f"   {field}: {value}")
            else:
                print(f"   {field}: {value}")
        print()
    
    # Quick stats
    sources = {}
    for memory in memories:
        source = memory.get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1
    
    print("📈 Quick Stats (sample):")
    for source, count in sources.items():
        print(f"   {source}: {count}")

if __name__ == "__main__":
    quick_peek()