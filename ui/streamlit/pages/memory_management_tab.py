#!/usr/bin/env python3
"""
Memory Management - Tools for managing memory data.
"""

import streamlit as st
import json
import shutil
from pathlib import Path
import sys
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import dashboard config
sys.path.append(str(Path(__file__).parent))
from dashboard_config import config

st.set_page_config(
    page_title="Memory Management",
    page_icon="⚙️",
    layout="wide"
)

def get_memory_stats():
    """Get current memory statistics."""
    stats = {
        "metadata_exists": False,
        "metadata_size": 0,
        "memory_dirs_exist": False,
        "memory_files": 0,
        "memory_size": 0,
        "locations": []
    }
    
    # Check metadata
    metadata_path = config.extract_dir / "memory_metadata.json"
    if metadata_path.exists():
        stats["metadata_exists"] = True
        stats["metadata_size"] = metadata_path.stat().st_size
    
    # Check memory directories
    memory_dirs = [
        config.extract_dir,
        config.rays_memory_room,
        config.ray_workspace,
        config.logs_dir,
        config.memories_dir
    ]
    
    for memory_dir in memory_dirs:
        if memory_dir.exists():
            stats["memory_dirs_exist"] = True
            location_files = 0
            location_size = 0
            
            for file_path in memory_dir.rglob("*"):
                if file_path.is_file():
                    stats["memory_files"] += 1
                    location_files += 1
                    file_size = file_path.stat().st_size
                    stats["memory_size"] += file_size
                    location_size += file_size
            
            if location_files > 0:
                stats["locations"].append({
                    "path": str(memory_dir),
                    "files": location_files,
                    "size": location_size
                })
    
    return stats

def backup_memory():
    """Create a backup of memory data."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = config.backups_dir / f"memory_backup_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    backed_up = []
    
    # Backup key memory files
    memory_files = [
        config.extract_dir / "memory_metadata.json",
        config.extract_dir / "agent_memories.json", 
        config.extract_dir / "chats.json"
    ]
    
    for file_path in memory_files:
        if file_path.exists():
            backup_file = backup_dir / file_path.name
            shutil.copy2(file_path, backup_file)
            backed_up.append(file_path.name)
    
    # Backup memory directories
    memory_dirs = [
        (config.rays_memory_room, "RaysMemoryRoom"),
        (config.ray_workspace, "ray_workspace"),
        (config.memories_dir, "memories")  # Keep for backward compatibility
    ]
    
    for source_path, backup_name in memory_dirs:
        if source_path.exists():
            backup_path = backup_dir / backup_name
            shutil.copytree(source_path, backup_path, dirs_exist_ok=True)
            backed_up.append(f"{backup_name}/")
    
    return backup_dir, backed_up

def main():
    st.title("⚙️ Memory Management")
    
    # Get current stats
    stats = get_memory_stats()
    
    # Display current status
    st.subheader("📊 Current Memory Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = "✅" if stats["metadata_exists"] else "❌"
        st.metric("Metadata", status)
    
    with col2:
        st.metric("Metadata Size", f"{stats['metadata_size'] / 1024:.1f} KB")
    
    with col3:
        st.metric("Memory Files", stats["memory_files"])
    
    with col4:
        st.metric("Memory Size", f"{stats['memory_size'] / 1024:.1f} KB")
    
    # Show memory locations
    if stats["locations"]:
        st.subheader("📍 Memory Locations")
        for location in stats["locations"]:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"📁 {location['path']}")
            with col2:
                st.write(f"📄 {location['files']} files")
            with col3:
                st.write(f"💾 {location['size'] / 1024:.1f} KB")
    
    # Management Operations
    st.subheader("🛠️ Management Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔄 Backup Operations")
        
        if st.button("📦 Create Memory Backup", type="primary", key="create_backup_button"):
            try:
                backup_dir, backed_up = backup_memory()
                st.success(f"✅ Backup created: {backup_dir}")
                st.info(f"Backed up: {', '.join(backed_up)}")
            except Exception as e:
                st.error(f"❌ Backup failed: {str(e)}")
        
        # List existing backups
        backups_dir = Path("backups")
        if backups_dir.exists():
            backups = [d for d in backups_dir.iterdir() if d.is_dir() and d.name.startswith("memory_backup_")]
            if backups:
                st.write("📋 Existing Backups:")
                for backup in sorted(backups, reverse=True)[:5]:  # Show last 5
                    backup_time = backup.name.replace("memory_backup_", "").replace("_", " ")
                    st.write(f"- {backup_time}")
    
    with col2:
        st.subheader("🧹 Cleanup Operations")
        
        st.warning("⚠️ Cleanup operations are destructive!")
        
        if st.button("🗑️ Clear Memory Metadata", type="secondary", key="clear_metadata_button"):
            metadata_path = Path("extract/memory_metadata.json")
            if metadata_path.exists():
                if st.button("⚠️ Confirm Clear Metadata", type="secondary", key="confirm_clear_metadata_button"):
                    try:
                        metadata_path.unlink()
                        st.success("✅ Memory metadata cleared")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to clear metadata: {str(e)}")
            else:
                st.info("No metadata file to clear")
        
        if st.button("🗑️ Clear All Memory Files", type="secondary", key="clear_all_files_button"):
            memory_dir = Path("memories")
            if memory_dir.exists():
                if st.button("⚠️ Confirm Clear All Memory", type="secondary", key="confirm_clear_all_button"):
                    try:
                        shutil.rmtree(memory_dir)
                        st.success("✅ All memory files cleared")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to clear memory files: {str(e)}")
            else:
                st.info("No memory directory to clear")
    
    # Memory Health
    st.subheader("🏥 Memory Health")
    
    health_score = 0
    max_score = 4
    
    if stats["metadata_exists"]:
        health_score += 1
        st.success("✅ Memory metadata exists")
    else:
        st.error("❌ Memory metadata missing")
    
    if stats["memory_dirs_exist"]:
        health_score += 1
        st.success("✅ Memory directories exist")
    else:
        st.error("❌ Memory directories missing")
    
    if stats["memory_files"] > 0:
        health_score += 1
        st.success(f"✅ {stats['memory_files']} memory files found")
    else:
        st.warning("⚠️ No memory files found")
    
    if stats["memory_size"] < 50 * 1024 * 1024:  # Less than 50MB
        health_score += 1
        st.success("✅ Memory usage is reasonable")
    else:
        st.warning("⚠️ High memory usage detected")
    
    # Health score
    health_percentage = (health_score / max_score) * 100
    st.metric("Memory Health Score", f"{health_percentage:.0f}%")
    st.progress(health_percentage / 100)
    
    # Recommendations
    st.subheader("💡 Recommendations")
    
    if health_score == max_score:
        st.success("🎉 Memory system is healthy! No action needed.")
    else:
        if not stats["metadata_exists"]:
            st.info("📝 Consider initializing memory metadata")
        if stats["memory_files"] == 0:
            st.info("🧠 Memory system appears unused - this may be normal for new installations")
        if stats["memory_size"] > 50 * 1024 * 1024:
            st.info("🧹 Consider cleaning up old memory files to free space")

if __name__ == "__main__":
    main()