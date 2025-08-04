#!/usr/bin/env python3
"""
Redundancy Detection Agent
Uses embeddings to detect memory collisions and suggest merges/deletions
"""

import json
import os
import sys
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from services.memory_service import MemoryService

class RedundancyDetector:
    """Detect and suggest fixes for redundant memories"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.memory_service = MemoryService()
    
    def detect_redundant_memories(self) -> List[Dict[str, Any]]:
        """Detect redundant memories using embedding similarity"""
        print(f"🔍 Detecting redundant memories (threshold: {self.similarity_threshold})")
        
        if not self.memory_service.is_system_ready():
            print("❌ Memory system not ready")
            return []
        
        # Load memories and embeddings
        memories = self.memory_service._load_memories()
        embedding_manager = self.memory_service._get_embedding_manager()
        
        print(f"📊 Analyzing {len(memories)} memories...")
        
        # Generate embeddings for all memories
        embeddings = []
        valid_indices = []
        
        for i, memory in enumerate(memories):
            content = memory.get('content', '')
            if content and len(content.strip()) > 10:  # Skip very short content
                try:
                    vector = embedding_manager.embed(content)
                    embeddings.append(vector)
                    valid_indices.append(i)
                    
                    if (i + 1) % 100 == 0:
                        print(f"   Processed {i + 1}/{len(memories)} embeddings...")
                        
                except Exception as e:
                    print(f"⚠️  Error embedding memory {i}: {e}")
                    continue
        
        if len(embeddings) < 2:
            print("❌ Not enough valid embeddings for comparison")
            return []
        
        # Calculate similarity matrix
        print("🧮 Calculating similarity matrix...")
        embeddings_array = np.array(embeddings)
        similarity_matrix = cosine_similarity(embeddings_array)
        
        # Find redundant pairs
        redundant_groups = []
        processed_indices = set()
        
        for i in range(len(similarity_matrix)):
            if i in processed_indices:
                continue
                
            similar_indices = []
            for j in range(i + 1, len(similarity_matrix)):
                if j in processed_indices:
                    continue
                    
                similarity = similarity_matrix[i][j]
                if similarity >= self.similarity_threshold:
                    if not similar_indices:
                        similar_indices.append(i)
                    similar_indices.append(j)
            
            if similar_indices:
                # Create redundancy group
                group_memories = []
                for idx in similar_indices:
                    memory_idx = valid_indices[idx]
                    memory = memories[memory_idx].copy()
                    memory['memory_id'] = f"mem-{memory_idx}"
                    memory['embedding_index'] = idx
                    group_memories.append(memory)
                    processed_indices.add(idx)
                
                # Calculate group statistics
                group = {
                    'group_id': len(redundant_groups),
                    'memories': group_memories,
                    'count': len(group_memories),
                    'max_similarity': max(similarity_matrix[i][j] for j in similar_indices[1:]) if len(similar_indices) > 1 else 0,
                    'avg_similarity': np.mean([similarity_matrix[i][j] for j in similar_indices[1:]]) if len(similar_indices) > 1 else 0,
                    'suggested_action': self._suggest_action(group_memories)
                }
                
                redundant_groups.append(group)
        
        print(f"✅ Found {len(redundant_groups)} redundant groups")
        return redundant_groups
    
    def _suggest_action(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Suggest action for a group of redundant memories"""
        if len(memories) < 2:
            return {'action': 'none', 'reason': 'Single memory'}
        
        # Analyze memories to suggest best action
        content_lengths = [len(mem.get('content', '')) for mem in memories]
        importance_scores = [mem.get('importance', 0) for mem in memories if isinstance(mem.get('importance'), (int, float))]
        sources = [mem.get('source', '') for mem in memories]
        
        # Find best memory (longest content, highest importance)
        best_idx = 0
        best_score = 0
        
        for i, memory in enumerate(memories):
            score = 0
            score += len(memory.get('content', '')) * 0.01  # Content length
            score += memory.get('importance', 0) * 100  # Importance
            if memory.get('source') == 'agent_response':
                score += 10  # Prefer agent responses
            
            if score > best_score:
                best_score = score
                best_idx = i
        
        # Determine action
        if len(set(content_lengths)) == 1:
            # Identical content lengths - suggest delete duplicates
            return {
                'action': 'delete_duplicates',
                'keep_memory': memories[best_idx]['memory_id'],
                'delete_memories': [mem['memory_id'] for i, mem in enumerate(memories) if i != best_idx],
                'reason': 'Identical or near-identical content'
            }
        elif max(content_lengths) > sum(content_lengths) * 0.7:
            # One memory is much longer - suggest keep longest
            longest_idx = content_lengths.index(max(content_lengths))
            return {
                'action': 'keep_longest',
                'keep_memory': memories[longest_idx]['memory_id'],
                'delete_memories': [mem['memory_id'] for i, mem in enumerate(memories) if i != longest_idx],
                'reason': 'One memory contains significantly more content'
            }
        else:
            # Similar lengths - suggest merge
            return {
                'action': 'merge',
                'base_memory': memories[best_idx]['memory_id'],
                'merge_memories': [mem['memory_id'] for i, mem in enumerate(memories) if i != best_idx],
                'reason': 'Similar content that could be consolidated'
            }
    
    def generate_report(self, redundant_groups: List[Dict[str, Any]]) -> str:
        """Generate a detailed redundancy report"""
        if not redundant_groups:
            return "✅ No redundant memories detected!"
        
        report = []
        report.append("🔍 REDUNDANCY DETECTION REPORT")
        report.append("=" * 50)
        report.append(f"Found {len(redundant_groups)} redundant groups")
        report.append(f"Similarity threshold: {self.similarity_threshold}")
        report.append("")
        
        total_redundant = sum(group['count'] for group in redundant_groups)
        potential_savings = total_redundant - len(redundant_groups)  # Keep one per group
        
        report.append("📊 SUMMARY")
        report.append(f"Total redundant memories: {total_redundant}")
        report.append(f"Potential memory savings: {potential_savings}")
        report.append(f"Space reduction: {(potential_savings/total_redundant)*100:.1f}%")
        report.append("")
        
        # Group details
        for group in redundant_groups:
            report.append(f"🔸 GROUP {group['group_id']} ({group['count']} memories)")
            report.append(f"   Max similarity: {group['max_similarity']:.3f}")
            report.append(f"   Avg similarity: {group['avg_similarity']:.3f}")
            report.append(f"   Suggested action: {group['suggested_action']['action']}")
            report.append(f"   Reason: {group['suggested_action']['reason']}")
            report.append("")
            
            # Show memory previews
            for memory in group['memories']:
                content_preview = memory['content'][:100] + "..." if len(memory['content']) > 100 else memory['content']
                report.append(f"     {memory['memory_id']}: {content_preview}")
            
            report.append("")
        
        return "\n".join(report)
    
    def save_report(self, redundant_groups: List[Dict[str, Any]], output_file: str = "redundancy_report.txt") -> None:
        """Save redundancy report to file"""
        report = self.generate_report(redundant_groups)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Report saved to {output_file}")
    
    def export_deletion_script(self, redundant_groups: List[Dict[str, Any]], output_file: str = "cleanup_script.py") -> None:
        """Export a Python script to perform suggested deletions"""
        script_lines = []
        script_lines.append("#!/usr/bin/env python3")
        script_lines.append('"""')
        script_lines.append("Auto-generated memory cleanup script")
        script_lines.append("Review carefully before running!")
        script_lines.append('"""')
        script_lines.append("")
        script_lines.append("import json")
        script_lines.append("import os")
        script_lines.append("from datetime import datetime")
        script_lines.append("")
        script_lines.append("def cleanup_redundant_memories():")
        script_lines.append('    """Execute redundancy cleanup"""')
        script_lines.append('    print("🧹 Starting redundancy cleanup...")')
        script_lines.append("")
        script_lines.append("    # Load current data")
        script_lines.append('    with open("extract/agent_memories.json", "r", encoding="utf-8") as f:')
        script_lines.append("        memories = json.load(f)")
        script_lines.append('    with open("extract/memory_metadata.json", "r", encoding="utf-8") as f:')
        script_lines.append("        metadata = json.load(f)")
        script_lines.append("")
        script_lines.append("    # Memories to delete")
        
        all_deletions = []
        for group in redundant_groups:
            action = group['suggested_action']
            if action['action'] in ['delete_duplicates', 'keep_longest']:
                all_deletions.extend(action['delete_memories'])
        
        script_lines.append(f"    memories_to_delete = {all_deletions}")
        script_lines.append("")
        script_lines.append("    # Create backup")
        script_lines.append('    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")')
        script_lines.append('    os.rename("extract/agent_memories.json", f"extract/agent_memories_backup_{timestamp}.json")')
        script_lines.append('    os.rename("extract/memory_metadata.json", f"extract/memory_metadata_backup_{timestamp}.json")')
        script_lines.append("")
        script_lines.append("    # Remove memories")
        script_lines.append("    deleted_count = 0")
        script_lines.append("    for memory_id in memories_to_delete:")
        script_lines.append("        idx = int(memory_id.replace('mem-', ''))")
        script_lines.append("        if idx < len(memories):")
        script_lines.append("            del memories[idx]")
        script_lines.append("            deleted_count += 1")
        script_lines.append("        if memory_id in metadata:")
        script_lines.append("            del metadata[memory_id]")
        script_lines.append("")
        script_lines.append("    # Save cleaned data")
        script_lines.append('    with open("extract/agent_memories.json", "w", encoding="utf-8") as f:')
        script_lines.append("        json.dump(memories, f, indent=2, ensure_ascii=False)")
        script_lines.append('    with open("extract/memory_metadata.json", "w", encoding="utf-8") as f:')
        script_lines.append("        json.dump(metadata, f, indent=2, ensure_ascii=False)")
        script_lines.append("")
        script_lines.append('    print(f"✅ Deleted {deleted_count} redundant memories")')
        script_lines.append('    print("🔄 Remember to rebuild the FAISS index!")')
        script_lines.append("")
        script_lines.append('if __name__ == "__main__":')
        script_lines.append("    cleanup_redundant_memories()")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(script_lines))
        
        print(f"🐍 Cleanup script saved to {output_file}")

def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Detect redundant memories")
    parser.add_argument("--threshold", type=float, default=0.85,
                       help="Similarity threshold (0.0-1.0, default: 0.85)")
    parser.add_argument("--report", default="redundancy_report.txt",
                       help="Output report file (default: redundancy_report.txt)")
    parser.add_argument("--script", default="cleanup_script.py",
                       help="Output cleanup script file (default: cleanup_script.py)")
    parser.add_argument("--no-script", action="store_true",
                       help="Don't generate cleanup script")
    
    args = parser.parse_args()
    
    # Create detector
    detector = RedundancyDetector(similarity_threshold=args.threshold)
    
    # Detect redundancies
    redundant_groups = detector.detect_redundant_memories()
    
    # Generate and save report
    detector.save_report(redundant_groups, args.report)
    
    # Generate cleanup script
    if not args.no_script and redundant_groups:
        detector.export_deletion_script(redundant_groups, args.script)
    
    # Print summary
    if redundant_groups:
        total_redundant = sum(group['count'] for group in redundant_groups)
        potential_savings = total_redundant - len(redundant_groups)
        print(f"\n📊 SUMMARY:")
        print(f"   Found {len(redundant_groups)} redundant groups")
        print(f"   Total redundant memories: {total_redundant}")
        print(f"   Potential savings: {potential_savings} memories")
        print(f"   Reports saved to: {args.report}")
        if not args.no_script:
            print(f"   Cleanup script: {args.script}")
    else:
        print("\n✅ No redundant memories found!")

if __name__ == "__main__":
    main()