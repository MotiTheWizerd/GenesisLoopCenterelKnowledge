#!/usr/bin/env python3
"""
Memory Migration System - Comprehensive migration to new memory structure
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import uuid

@dataclass
class MigrationConfig:
    """Configuration for memory migration"""
    backup_dir: str = "backups/memory_migration"
    current_memory_file: str = "extract/agent_memories.json"
    current_metadata_file: str = "extract/memory_metadata.json"
    new_memory_file: str = "extract/ray_memories_v2.json"
    new_metadata_file: str = "extract/ray_metadata_v2.json"
    batch_size: int = 1000
    
class MemoryMigrator:
    """Handles migration from old to new memory structure"""
    
    def __init__(self, config: MigrationConfig = None):
        self.config = config or MigrationConfig()
        self.migration_stats = {
            "total_processed": 0,
            "successful_migrations": 0,
            "failed_migrations": 0,
            "skipped_entries": 0,
            "new_fields_added": 0
        }
    
    def analyze_current_structure(self) -> Dict[str, Any]:
        """Analyze current memory structure before migration"""
        print("🔍 Analyzing current memory structure...")
        
        if not os.path.exists(self.config.current_memory_file):
            return {"error": "Current memory file not found"}
        
        try:
            with open(self.config.current_memory_file, 'r', encoding='utf-8') as f:
                memories = json.load(f)
            
            # Analyze structure
            field_stats = {}
            sample_entries = memories[:10] if len(memories) > 10 else memories
            
            for memory in memories:
                for field in memory.keys():
                    if field not in field_stats:
                        field_stats[field] = {"count": 0, "types": set(), "examples": []}
                    
                    field_stats[field]["count"] += 1
                    field_stats[field]["types"].add(type(memory[field]).__name__)
                    
                    if len(field_stats[field]["examples"]) < 3:
                        field_stats[field]["examples"].append(memory[field])
            
            # Convert sets to lists for JSON serialization
            for field in field_stats:
                field_stats[field]["types"] = list(field_stats[field]["types"])
            
            analysis = {
                "total_memories": len(memories),
                "field_statistics": field_stats,
                "sample_entries": sample_entries,
                "file_size_mb": os.path.getsize(self.config.current_memory_file) / (1024 * 1024)
            }
            
            print(f"✅ Analysis complete: {len(memories)} memories, {len(field_stats)} unique fields")
            return analysis
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def create_backup(self) -> bool:
        """Create backup of current memory system"""
        print("📦 Creating backup of current memory system...")
        
        try:
            # Create backup directory
            backup_path = Path(self.config.backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Backup files
            files_to_backup = [
                self.config.current_memory_file,
                self.config.current_metadata_file,
                "extract/faiss_index.bin"
            ]
            
            backed_up = []
            for file_path in files_to_backup:
                if os.path.exists(file_path):
                    filename = Path(file_path).name
                    backup_file = backup_path / f"{timestamp}_{filename}"
                    shutil.copy2(file_path, backup_file)
                    backed_up.append(str(backup_file))
            
            print(f"✅ Backup created: {len(backed_up)} files backed up to {backup_path}")
            return True
            
        except Exception as e:
            print(f"❌ Backup failed: {str(e)}")
            return False
    
    def migrate_memory_entry(self, old_memory: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Migrate a single memory entry to new structure"""
        
        # Generate new ID
        new_id = f"mem-{index + 1}"
        
        # Determine author based on source
        author = self._determine_author(old_memory.get("source", "unknown"))
        
        # Extract text content
        text = old_memory.get("content", "")
        
        # Preserve timestamp
        timestamp = old_memory.get("timestamp", datetime.now().timestamp())
        
        # Determine parent/child relationships (initially null, can be enhanced later)
        parent_id = None
        child_ids = []
        
        # Analyze intent from content and source
        intent = self._analyze_intent(text, old_memory.get("source", ""))
        
        # Analyze tone from content
        tone = self._analyze_tone(text)
        
        # Migrate and enhance tags
        old_tags = old_memory.get("tags", [])
        new_tags = self._enhance_tags(old_tags, old_memory)
        
        # Create context from old metadata
        context = self._create_context(old_memory)
        
        # Map source to new format
        source = self._map_source(old_memory.get("source", "unknown"))
        
        # Create new memory structure
        new_memory = {
            "id": new_id,
            "author": author,
            "text": text,
            "timestamp": timestamp,
            "parent_id": parent_id,
            "child_ids": child_ids,
            "intent": intent,
            "tone": tone,
            "tags": new_tags,
            "context": context,
            "source": source,
            "embedding": None  # Will be regenerated
        }
        
        # Add migration metadata
        new_memory["_migration"] = {
            "migrated_at": datetime.now().isoformat(),
            "original_structure": {
                "had_importance": "importance" in old_memory,
                "had_type": "type" in old_memory,
                "original_source": old_memory.get("source"),
                "original_tags_count": len(old_tags)
            }
        }
        
        return new_memory
    
    def _determine_author(self, source: str) -> str:
        """Determine author based on source"""
        if "agent_response" in source:
            return "ray"
        elif "user_input" in source:
            return "user"
        elif "json_file" in source:
            return "system"
        else:
            return "unknown"
    
    def _analyze_intent(self, text: str, source: str) -> List[str]:
        """Analyze intent from text content"""
        intents = []
        text_lower = text.lower()
        
        # Question patterns
        if "?" in text or any(word in text_lower for word in ["what", "how", "why", "when", "where", "who"]):
            intents.append("question")
        
        # Request patterns
        if any(word in text_lower for word in ["please", "can you", "could you", "would you"]):
            intents.append("request")
        
        # Information sharing
        if any(word in text_lower for word in ["here is", "this is", "i found", "according to"]):
            intents.append("information_sharing")
        
        # System/technical content
        if any(word in text_lower for word in ["function", "class", "method", "error", "debug"]):
            intents.append("technical_content")
        
        # Reflection/analysis
        if any(word in text_lower for word in ["reflect", "analyze", "consider", "think"]):
            intents.append("reflection")
        
        # Loop/time related (Ray-specific)
        if any(word in text_lower for word in ["loop", "time", "reflection_depth", "processing"]):
            intents.append("loop_management")
        
        return intents if intents else ["general"]
    
    def _analyze_tone(self, text: str) -> List[str]:
        """Analyze tone from text content"""
        tones = []
        text_lower = text.lower()
        
        # Emotional indicators
        if any(word in text_lower for word in ["please", "thank", "appreciate"]):
            tones.append("polite")
        
        if any(word in text_lower for word in ["!", "amazing", "great", "excellent"]):
            tones.append("enthusiastic")
        
        if any(word in text_lower for word in ["urgent", "quickly", "asap", "immediately"]):
            tones.append("urgent")
        
        if any(word in text_lower for word in ["sorry", "apologize", "mistake"]):
            tones.append("apologetic")
        
        if any(word in text_lower for word in ["curious", "wondering", "interested"]):
            tones.append("curious")
        
        # Technical tone
        if any(word in text_lower for word in ["implement", "configure", "optimize"]):
            tones.append("technical")
        
        # Ray-specific tones
        if any(word in text_lower for word in ["loop", "reflection", "consciousness"]):
            tones.append("introspective")
        
        return tones if tones else ["neutral"]
    
    def _enhance_tags(self, old_tags: List[str], old_memory: Dict[str, Any]) -> List[str]:
        """Enhance tags based on content analysis"""
        enhanced_tags = list(old_tags)  # Start with existing tags
        
        text = old_memory.get("content", "").lower()
        source = old_memory.get("source", "")
        
        # Add source-based tags
        if "agent_response" in source:
            enhanced_tags.append("ray_response")
        elif "user_input" in source:
            enhanced_tags.append("user_input")
        elif "json_file" in source:
            enhanced_tags.append("data_import")
        
        # Add content-based tags
        if any(word in text for word in ["error", "exception", "failed"]):
            enhanced_tags.append("error_related")
        
        if any(word in text for word in ["success", "completed", "finished"]):
            enhanced_tags.append("success")
        
        if any(word in text for word in ["memory", "remember", "recall"]):
            enhanced_tags.append("memory_related")
        
        if any(word in text for word in ["loop", "reflection", "depth"]):
            enhanced_tags.append("consciousness")
        
        # Remove duplicates and return
        return list(set(enhanced_tags))
    
    def _create_context(self, old_memory: Dict[str, Any]) -> Dict[str, Any]:
        """Create context object from old memory metadata"""
        context = {}
        
        # Preserve important old fields as context
        if "importance" in old_memory:
            context["importance_score"] = old_memory["importance"]
        
        if "type" in old_memory:
            context["original_type"] = old_memory["type"]
        
        if "original_file" in old_memory:
            context["source_file"] = old_memory["original_file"]
        
        if "file_type" in old_memory:
            context["file_type"] = old_memory["file_type"]
        
        if "array_index" in old_memory:
            context["array_index"] = old_memory["array_index"]
        
        if "chunk_index" in old_memory:
            context["chunk_index"] = old_memory["chunk_index"]
        
        # Add processing metadata
        context["content_length"] = len(old_memory.get("content", ""))
        context["word_count"] = len(old_memory.get("content", "").split())
        
        return context
    
    def _map_source(self, old_source: str) -> str:
        """Map old source to new source format"""
        if "agent_response" in old_source:
            return "conversation"
        elif "user_input" in old_source:
            return "conversation"
        elif "json_file" in old_source:
            return "data_import"
        else:
            return "system"
    
    def perform_migration(self, dry_run: bool = False) -> Dict[str, Any]:
        """Perform the complete migration"""
        print(f"🚀 Starting memory migration (dry_run={dry_run})...")
        
        # Step 1: Analyze current structure
        analysis = self.analyze_current_structure()
        if "error" in analysis:
            return {"success": False, "error": analysis["error"]}
        
        # Step 2: Create backup
        if not dry_run:
            if not self.create_backup():
                return {"success": False, "error": "Backup creation failed"}
        
        # Step 3: Load current memories
        try:
            with open(self.config.current_memory_file, 'r', encoding='utf-8') as f:
                old_memories = json.load(f)
        except Exception as e:
            return {"success": False, "error": f"Failed to load memories: {str(e)}"}
        
        # Step 4: Migrate memories in batches
        migrated_memories = []
        
        for i, old_memory in enumerate(old_memories):
            try:
                new_memory = self.migrate_memory_entry(old_memory, i)
                migrated_memories.append(new_memory)
                self.migration_stats["successful_migrations"] += 1
                
                if (i + 1) % self.config.batch_size == 0:
                    print(f"  Processed {i + 1}/{len(old_memories)} memories...")
                
            except Exception as e:
                print(f"  ⚠️ Failed to migrate memory {i}: {str(e)}")
                self.migration_stats["failed_migrations"] += 1
            
            self.migration_stats["total_processed"] += 1
        
        # Step 5: Save migrated memories
        if not dry_run:
            try:
                # Save new memory structure
                with open(self.config.new_memory_file, 'w', encoding='utf-8') as f:
                    json.dump(migrated_memories, f, indent=2, ensure_ascii=False)
                
                # Create new metadata structure
                new_metadata = {}
                for memory in migrated_memories:
                    new_metadata[memory["id"]] = memory
                
                with open(self.config.new_metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(new_metadata, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Migration complete: {len(migrated_memories)} memories migrated")
                
            except Exception as e:
                return {"success": False, "error": f"Failed to save migrated data: {str(e)}"}
        
        # Step 6: Generate migration report
        migration_report = {
            "success": True,
            "migration_stats": self.migration_stats,
            "analysis": analysis,
            "sample_migrated": migrated_memories[:3] if migrated_memories else [],
            "dry_run": dry_run,
            "timestamp": datetime.now().isoformat()
        }
        
        return migration_report
    
    def generate_migration_script(self) -> str:
        """Generate a script to update all system components"""
        script_content = '''#!/usr/bin/env python3
"""
Auto-generated migration script to update all system components
Run this after successful memory migration
"""

import os
import shutil
from pathlib import Path

def update_system_files():
    """Update system files to use new memory structure"""
    
    print("🔄 Updating system files for new memory structure...")
    
    # 1. Update memory service
    print("  Updating memory service...")
    # TODO: Update services/memory_service.py to use new structure
    
    # 2. Update dashboard components
    print("  Updating dashboard components...")
    # TODO: Update UI components to display new fields
    
    # 3. Update scripts
    print("  Updating scripts...")
    # TODO: Update scripts to create new memory format
    
    # 4. Replace old files with new ones (after backup)
    if input("Replace old memory files with migrated versions? (y/N): ").lower() == 'y':
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Backup and replace
        shutil.move("extract/agent_memories.json", f"extract/agent_memories_old_{timestamp}.json")
        shutil.move("extract/memory_metadata.json", f"extract/memory_metadata_old_{timestamp}.json")
        
        shutil.move("extract/ray_memories_v2.json", "extract/agent_memories.json")
        shutil.move("extract/ray_metadata_v2.json", "extract/memory_metadata.json")
        
        print("✅ Files replaced successfully")
    
    print("🎉 System update complete!")

if __name__ == "__main__":
    update_system_files()
'''
        return script_content

def main():
    """Main migration interface"""
    print("🧠 Ray's Memory Migration System")
    print("=" * 50)
    
    migrator = MemoryMigrator()
    
    # Show options
    print("Options:")
    print("1. Analyze current structure")
    print("2. Perform dry run migration")
    print("3. Perform actual migration")
    print("4. Generate migration script")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        analysis = migrator.analyze_current_structure()
        print("\n📊 Analysis Results:")
        print(json.dumps(analysis, indent=2))
    
    elif choice == "2":
        print("\n🧪 Performing dry run migration...")
        result = migrator.perform_migration(dry_run=True)
        print("\n📋 Dry Run Results:")
        print(json.dumps(result, indent=2))
    
    elif choice == "3":
        confirm = input("\n⚠️ This will modify your memory system. Continue? (y/N): ")
        if confirm.lower() == 'y':
            result = migrator.perform_migration(dry_run=False)
            print("\n🎉 Migration Results:")
            print(json.dumps(result, indent=2))
        else:
            print("Migration cancelled.")
    
    elif choice == "4":
        script = migrator.generate_migration_script()
        with open("migration_update_script.py", 'w') as f:
            f.write(script)
        print("✅ Migration script generated: migration_update_script.py")
    
    else:
        print("Invalid option selected.")

if __name__ == "__main__":
    main()