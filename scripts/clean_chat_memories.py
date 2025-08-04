#!/usr/bin/env python3
"""
Clean Chat Memories Script
Extracts actual conversation content from JSON chunks and removes duplicates
"""

import json
import re
from datetime import datetime

def extract_conversation_content(json_text):
    """Extract actual conversation content from JSON structure"""
    try:
        # Try to parse as JSON first
        if json_text.strip().startswith('{') or json_text.strip().startswith('['):
            data = json.loads(json_text)
            
            # Extract message content from various chat formats
            if isinstance(data, dict):
                # Look for common chat message fields
                content = (
                    data.get('message', '') or 
                    data.get('content', '') or 
                    data.get('text', '') or
                    data.get('body', '')
                )
                
                # Also extract author/sender info
                author = (
                    data.get('author', '') or
                    data.get('sender', '') or
                    data.get('from', '') or
                    data.get('user', '')
                )
                
                if content and author:
                    return f"{author}: {content}"
                elif content:
                    return content
                    
            elif isinstance(data, list):
                # Handle array of messages
                messages = []
                for item in data:
                    if isinstance(item, dict):
                        content = (
                            item.get('message', '') or 
                            item.get('content', '') or 
                            item.get('text', '')
                        )
                        author = (
                            item.get('author', '') or
                            item.get('sender', '') or
                            item.get('from', '')
                        )
                        
                        if content:
                            if author:
                                messages.append(f"{author}: {content}")
                            else:
                                messages.append(content)
                
                return '\n'.join(messages) if messages else json_text
        
        # If not JSON, return as-is but clean up
        return json_text.strip()
        
    except json.JSONDecodeError:
        # Not valid JSON, return cleaned text
        return json_text.strip()

def clean_chat_memories():
    """Clean up chat memories to extract actual conversation content"""
    print("🧹 Cleaning chat memories...")
    
    # Load current memories
    with open('extract/agent_memories.json', 'r', encoding='utf-8') as f:
        memories = json.load(f)
    
    print(f"📊 Found {len(memories)} memories")
    
    # Find chat-related memories
    chat_memories = [m for m in memories if 'chats.json' in str(m.get('original_file', ''))]
    print(f"💬 Found {len(chat_memories)} chat memories")
    
    # Clean and deduplicate
    cleaned_memories = []
    seen_content = set()
    
    for i, memory in enumerate(memories):
        if 'chats.json' in str(memory.get('original_file', '')):
            # Extract actual conversation content
            original_content = memory.get('content', '')
            cleaned_content = extract_conversation_content(original_content)
            
            # Skip if too short or duplicate
            if len(cleaned_content) < 10:
                continue
                
            content_hash = hash(cleaned_content)
            if content_hash in seen_content:
                continue
            
            seen_content.add(content_hash)
            
            # Update memory with cleaned content
            memory['content'] = cleaned_content
            memory['tags'] = memory.get('tags', []) + ['cleaned_chat']
            memory['importance'] = min(memory.get('importance', 0.5) + 0.2, 1.0)  # Boost importance
            
            cleaned_memories.append(memory)
            
            if i % 100 == 0:
                print(f"  Processed {i}/{len(memories)} memories...")
        else:
            # Keep non-chat memories as-is
            cleaned_memories.append(memory)
    
    print(f"✅ Cleaned memories: {len(cleaned_memories)} (removed {len(memories) - len(cleaned_memories)} duplicates/low-quality)")
    
    # Backup original
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"extract/agent_memories_before_cleaning_{timestamp}.json"
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(memories, f, indent=2, ensure_ascii=False)
    print(f"📦 Backup saved: {backup_file}")
    
    # Save cleaned memories
    with open('extract/agent_memories.json', 'w', encoding='utf-8') as f:
        json.dump(cleaned_memories, f, indent=2, ensure_ascii=False)
    
    # Update metadata
    metadata = {}
    for i, memory in enumerate(cleaned_memories):
        metadata[f"mem-{i}"] = memory
    
    with open('extract/memory_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print("✅ Memories cleaned and saved!")
    print("🔄 Next steps:")
    print("1. Restart your dashboard")
    print("2. Go to Memory Management tab")
    print("3. Click 'Rebuild Index' to update FAISS")
    print("4. Try searching for 'Motti' again")

if __name__ == "__main__":
    clean_chat_memories()