#!/usr/bin/env python3
"""
Memory Structure Analysis Tool
Deep dive into Ray's memory patterns and structure
"""

import json
import os
from datetime import datetime
from collections import Counter, defaultdict
from services.memory_service import MemoryService

class MemoryStructureAnalyzer:
    """Analyze the structure and patterns in Ray's memory system"""
    
    def __init__(self):
        self.memory_service = MemoryService()
        self.memories = None
        self.metadata = None
    
    def load_data(self):
        """Load memory data for analysis"""
        if not self.memory_service.is_system_ready():
            print("❌ Memory system not ready. Missing files:")
            print("   - extract/faiss_index.bin")
            print("   - extract/memory_metadata.json") 
            print("   - extract/agent_memories.json")
            return False
        
        print("📊 Loading memory data...")
        self.memories = self.memory_service._load_memories()
        self.metadata = self.memory_service._load_metadata()
        print(f"✅ Loaded {len(self.memories)} memories")
        return True
    
    def analyze_memory_schema(self):
        """Analyze the schema and structure of memory entries"""
        print("\n🔍 MEMORY SCHEMA ANALYSIS")
        print("=" * 50)
        
        if not self.memories:
            print("❌ No memories loaded")
            return
        
        # Analyze field presence across all memories
        field_stats = defaultdict(int)
        field_types = defaultdict(set)
        field_examples = defaultdict(list)
        
        for i, memory in enumerate(self.memories[:1000]):  # Sample first 1000
            for field, value in memory.items():
                field_stats[field] += 1
                field_types[field].add(type(value).__name__)
                
                # Collect examples (first 3 unique values)
                if len(field_examples[field]) < 3:
                    if value not in [ex['value'] for ex in field_examples[field]]:
                        field_examples[field].append({
                            'value': value,
                            'memory_id': f"mem-{i}" if 'mem-' not in str(value) else value
                        })
        
        # Display schema analysis
        print(f"📋 Schema Analysis (sample of {min(1000, len(self.memories))} memories):")
        print()
        
        for field in sorted(field_stats.keys()):
            presence_pct = (field_stats[field] / min(1000, len(self.memories))) * 100
            types = ', '.join(field_types[field])
            
            print(f"🔸 {field}")
            print(f"   Presence: {field_stats[field]}/{min(1000, len(self.memories))} ({presence_pct:.1f}%)")
            print(f"   Types: {types}")
            
            # Show examples
            if field_examples[field]:
                print("   Examples:")
                for ex in field_examples[field]:
                    value_str = str(ex['value'])
                    if len(value_str) > 100:
                        value_str = value_str[:100] + "..."
                    print(f"     • {value_str}")
            print()
    
    def analyze_specific_memory(self, memory_id="mem-6"):
        """Deep analysis of a specific memory entry"""
        print(f"\n🧠 SPECIFIC MEMORY ANALYSIS: {memory_id}")
        print("=" * 50)
        
        # Get from metadata (indexed format)
        memory = self.metadata.get(memory_id) if self.metadata else None
        
        if not memory:
            print(f"❌ Memory {memory_id} not found in metadata")
            # Try to find in raw memories
            try:
                idx = int(memory_id.replace('mem-', ''))
                if idx < len(self.memories):
                    memory = self.memories[idx]
                    print(f"✅ Found in raw memories at index {idx}")
            except:
                print(f"❌ Could not locate memory {memory_id}")
                return
        
        if not memory:
            print(f"❌ Memory {memory_id} not found")
            return
        
        print(f"📌 Memory Entry: {memory_id}")
        print("-" * 30)
        
        # Analyze each field
        for field, value in memory.items():
            print(f"🔸 {field}:")
            print(f"   Type: {type(value).__name__}")
            
            if field == 'content':
                print(f"   Length: {len(str(value))} characters")
                print(f"   Word count: {len(str(value).split())}")
                print(f"   Preview: {str(value)[:200]}{'...' if len(str(value)) > 200 else ''}")
            
            elif field == 'timestamp':
                if isinstance(value, (int, float)):
                    dt = datetime.fromtimestamp(value)
                    print(f"   Value: {value}")
                    print(f"   Human: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"   Age: {datetime.now() - dt}")
                else:
                    print(f"   Value: {value}")
            
            elif field == 'tags':
                if isinstance(value, list):
                    print(f"   Count: {len(value)}")
                    print(f"   Values: {', '.join(map(str, value))}")
                else:
                    print(f"   Value: {value}")
            
            elif field == 'importance':
                print(f"   Value: {value}")
                if isinstance(value, (int, float)):
                    if value >= 0.8:
                        print("   Level: HIGH 🔥")
                    elif value >= 0.5:
                        print("   Level: MEDIUM 📊")
                    else:
                        print("   Level: LOW 📝")
            
            else:
                value_str = str(value)
                if len(value_str) > 100:
                    value_str = value_str[:100] + "..."
                print(f"   Value: {value_str}")
            
            print()
    
    def analyze_memory_patterns(self):
        """Analyze patterns across all memories"""
        print("\n📈 MEMORY PATTERNS ANALYSIS")
        print("=" * 50)
        
        if not self.memories:
            print("❌ No memories loaded")
            return
        
        # Source distribution
        sources = Counter()
        importance_dist = Counter()
        content_lengths = []
        timestamps = []
        tag_counts = Counter()
        
        for memory in self.memories:
            # Source analysis
            source = memory.get('source', 'unknown')
            sources[source] += 1
            
            # Importance analysis
            importance = memory.get('importance', 0)
            if isinstance(importance, (int, float)):
                importance_range = f"{importance:.1f}-{importance + 0.1:.1f}"
                importance_dist[importance_range] += 1
            
            # Content length analysis
            content = memory.get('content', '')
            content_lengths.append(len(str(content)))
            
            # Timestamp analysis
            timestamp = memory.get('timestamp')
            if timestamp:
                timestamps.append(timestamp)
            
            # Tag analysis
            tags = memory.get('tags', [])
            if isinstance(tags, list):
                for tag in tags:
                    tag_counts[tag] += 1
        
        # Display patterns
        print("🔸 Source Distribution:")
        for source, count in sources.most_common():
            pct = (count / len(self.memories)) * 100
            print(f"   {source}: {count} ({pct:.1f}%)")
        
        print(f"\n🔸 Content Length Statistics:")
        if content_lengths:
            print(f"   Min: {min(content_lengths)} chars")
            print(f"   Max: {max(content_lengths)} chars")
            print(f"   Average: {sum(content_lengths)/len(content_lengths):.1f} chars")
            print(f"   Median: {sorted(content_lengths)[len(content_lengths)//2]} chars")
        
        print(f"\n🔸 Top Tags:")
        for tag, count in tag_counts.most_common(10):
            pct = (count / len(self.memories)) * 100
            print(f"   {tag}: {count} ({pct:.1f}%)")
        
        print(f"\n🔸 Importance Distribution:")
        for imp_range, count in sorted(importance_dist.items()):
            pct = (count / len(self.memories)) * 100
            print(f"   {imp_range}: {count} ({pct:.1f}%)")
        
        # Timeline analysis
        if timestamps:
            timestamps.sort()
            earliest = datetime.fromtimestamp(timestamps[0])
            latest = datetime.fromtimestamp(timestamps[-1])
            span = latest - earliest
            
            print(f"\n🔸 Timeline Analysis:")
            print(f"   Earliest: {earliest.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Latest: {latest.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Span: {span}")
            print(f"   Total entries: {len(timestamps)}")
    
    def analyze_memory_quality(self):
        """Analyze the quality and completeness of memory data"""
        print("\n🏥 MEMORY QUALITY ANALYSIS")
        print("=" * 50)
        
        if not self.memories:
            print("❌ No memories loaded")
            return
        
        # Quality metrics
        complete_memories = 0
        missing_fields = defaultdict(int)
        empty_fields = defaultdict(int)
        
        required_fields = ['content', 'source', 'timestamp']
        optional_fields = ['tags', 'importance', 'type']
        
        for memory in self.memories:
            is_complete = True
            
            # Check required fields
            for field in required_fields:
                if field not in memory:
                    missing_fields[field] += 1
                    is_complete = False
                elif not memory[field]:
                    empty_fields[field] += 1
                    is_complete = False
            
            # Check optional fields
            for field in optional_fields:
                if field not in memory:
                    missing_fields[field] += 1
                elif not memory[field]:
                    empty_fields[field] += 1
            
            if is_complete:
                complete_memories += 1
        
        # Display quality metrics
        completeness_pct = (complete_memories / len(self.memories)) * 100
        
        print(f"🔸 Overall Quality:")
        print(f"   Complete memories: {complete_memories}/{len(self.memories)} ({completeness_pct:.1f}%)")
        
        if missing_fields:
            print(f"\n🔸 Missing Fields:")
            for field, count in missing_fields.most_common():
                pct = (count / len(self.memories)) * 100
                print(f"   {field}: {count} ({pct:.1f}%)")
        
        if empty_fields:
            print(f"\n🔸 Empty Fields:")
            for field, count in empty_fields.most_common():
                pct = (count / len(self.memories)) * 100
                print(f"   {field}: {count} ({pct:.1f}%)")
        
        # Quality score
        if completeness_pct >= 95:
            print(f"\n✅ Quality Score: EXCELLENT ({completeness_pct:.1f}%)")
        elif completeness_pct >= 80:
            print(f"\n⚠️  Quality Score: GOOD ({completeness_pct:.1f}%)")
        else:
            print(f"\n❌ Quality Score: NEEDS IMPROVEMENT ({completeness_pct:.1f}%)")

def main():
    """Run comprehensive memory structure analysis"""
    print("🧠 RAY'S MEMORY STRUCTURE ANALYSIS")
    print("=" * 60)
    
    analyzer = MemoryStructureAnalyzer()
    
    # Load data
    if not analyzer.load_data():
        return
    
    # Run all analyses
    analyzer.analyze_memory_schema()
    analyzer.analyze_specific_memory("mem-6")  # The memory you mentioned
    analyzer.analyze_memory_patterns()
    analyzer.analyze_memory_quality()
    
    print("\n🎯 ANALYSIS COMPLETE")
    print("=" * 30)
    print("This analysis reveals Ray's memory structure, patterns, and quality.")
    print("Use this insight to understand how Ray's consciousness is organized!")

if __name__ == "__main__":
    main()